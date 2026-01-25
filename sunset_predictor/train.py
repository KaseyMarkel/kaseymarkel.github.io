"""
Training script for sunset prediction model.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import argparse
from pathlib import Path
import json
from tqdm import tqdm
import numpy as np
from datetime import datetime

from model import create_model
from dataset_builder import get_data_loaders


def train_epoch(model, train_loader, criterion, optimizer, device):
    """Train for one epoch."""
    model.train()
    running_loss = 0.0
    predictions = []
    targets = []
    
    for images, labels in tqdm(train_loader, desc="Training"):
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Statistics
        running_loss += loss.item()
        predictions.extend(outputs.detach().cpu().numpy())
        targets.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / len(train_loader)
    mae = np.mean(np.abs(np.array(predictions) - np.array(targets)))
    rmse = np.sqrt(np.mean((np.array(predictions) - np.array(targets))**2))
    
    return epoch_loss, mae, rmse


def validate(model, test_loader, criterion, device):
    """Validate the model."""
    model.eval()
    running_loss = 0.0
    predictions = []
    targets = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Validating"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            predictions.extend(outputs.cpu().numpy())
            targets.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / len(test_loader)
    mae = np.mean(np.abs(np.array(predictions) - np.array(targets)))
    rmse = np.sqrt(np.mean((np.array(predictions) - np.array(targets))**2))
    
    return epoch_loss, mae, rmse


def train(model, train_loader, test_loader, num_epochs=50, learning_rate=1e-4,
         device="cuda", save_dir="checkpoints", log_dir="logs"):
    """
    Main training loop.
    
    Args:
        model: Model to train
        train_loader: Training data loader
        test_loader: Test data loader
        num_epochs: Number of epochs
        learning_rate: Learning rate
        device: Device to use
        save_dir: Directory to save checkpoints
        log_dir: Directory for tensorboard logs
    """
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )
    
    # Tensorboard writer
    writer = SummaryWriter(log_dir)
    
    # Create save directory
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    best_test_loss = float("inf")
    
    print(f"Training on {device}")
    print(f"Model: {model}")
    print(f"Train batches: {len(train_loader)}, Test batches: {len(test_loader)}")
    print("-" * 50)
    
    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch+1}/{num_epochs}")
        
        # Train
        train_loss, train_mae, train_rmse = train_epoch(
            model, train_loader, criterion, optimizer, device
        )
        
        # Validate
        test_loss, test_mae, test_rmse = validate(
            model, test_loader, criterion, device
        )
        
        # Learning rate scheduling
        scheduler.step(test_loss)
        
        # Logging
        writer.add_scalar("Loss/Train", train_loss, epoch)
        writer.add_scalar("Loss/Test", test_loss, epoch)
        writer.add_scalar("MAE/Train", train_mae, epoch)
        writer.add_scalar("MAE/Test", test_mae, epoch)
        writer.add_scalar("RMSE/Train", train_rmse, epoch)
        writer.add_scalar("RMSE/Test", test_rmse, epoch)
        
        print(f"Train Loss: {train_loss:.4f}, MAE: {train_mae:.4f}, RMSE: {train_rmse:.4f}")
        print(f"Test Loss: {test_loss:.4f}, MAE: {test_mae:.4f}, RMSE: {test_rmse:.4f}")
        
        # Save checkpoint
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "train_loss": train_loss,
            "test_loss": test_loss,
            "train_mae": train_mae,
            "test_mae": test_mae,
        }
        
        torch.save(checkpoint, save_path / "latest.pth")
        
        # Save best model
        if test_loss < best_test_loss:
            best_test_loss = test_loss
            torch.save(checkpoint, save_path / "best.pth")
            print(f"Saved best model (test loss: {test_loss:.4f})")
    
    writer.close()
    print("\nTraining complete!")
    print(f"Best test loss: {best_test_loss:.4f}")
    print(f"Checkpoints saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train sunset prediction model")
    parser.add_argument("--train-metadata", type=str, required=True,
                       help="Path to train metadata JSON")
    parser.add_argument("--test-metadata", type=str, required=True,
                       help="Path to test metadata JSON")
    parser.add_argument("--image-dir", type=str, required=True,
                       help="Directory containing images")
    parser.add_argument("--model-type", type=str, default="resnet18",
                       choices=["resnet18", "resnet34", "resnet50", "simple"],
                       help="Model architecture")
    parser.add_argument("--batch-size", type=int, default=32,
                       help="Batch size")
    parser.add_argument("--num-epochs", type=int, default=50,
                       help="Number of epochs")
    parser.add_argument("--learning-rate", type=float, default=1e-4,
                       help="Learning rate")
    parser.add_argument("--save-dir", type=str, default="checkpoints",
                       help="Directory to save checkpoints")
    parser.add_argument("--log-dir", type=str, default="logs",
                       help="Directory for tensorboard logs")
    parser.add_argument("--device", type=str, default="cuda",
                       help="Device to use (cuda/cpu)")
    
    args = parser.parse_args()
    
    # Set device
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    if args.device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        device = torch.device("cpu")
    
    # Create data loaders
    print("Loading data...")
    train_loader, test_loader = get_data_loaders(
        args.train_metadata,
        args.test_metadata,
        args.image_dir,
        batch_size=args.batch_size
    )
    
    # Create model
    print(f"Creating {args.model_type} model...")
    model = create_model(args.model_type, pretrained=True)
    
    # Train
    train(
        model,
        train_loader,
        test_loader,
        num_epochs=args.num_epochs,
        learning_rate=args.learning_rate,
        device=device,
        save_dir=args.save_dir,
        log_dir=args.log_dir
    )


if __name__ == "__main__":
    main()

