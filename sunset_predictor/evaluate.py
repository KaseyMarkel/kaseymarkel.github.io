"""
Evaluation script for sunset prediction model.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import argparse

from model import create_model
from dataset_builder import get_data_loaders


def evaluate_model(model, test_loader, device, checkpoint_path=None):
    """
    Evaluate model on test set.
    
    Args:
        model: Model to evaluate
        test_loader: Test data loader
        device: Device to use
        checkpoint_path: Path to checkpoint (optional)
    
    Returns:
        Dictionary with evaluation metrics
    """
    if checkpoint_path:
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        print(f"Loaded checkpoint from {checkpoint_path}")
    
    model = model.to(device)
    model.eval()
    
    predictions = []
    targets = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            
            predictions.extend(outputs.cpu().numpy())
            targets.extend(labels.cpu().numpy())
    
    predictions = np.array(predictions)
    targets = np.array(targets)
    
    # Calculate metrics
    mae = np.mean(np.abs(predictions - targets))
    rmse = np.sqrt(np.mean((predictions - targets)**2))
    mape = np.mean(np.abs((predictions - targets) / (targets + 1e-8))) * 100
    
    # Calculate R²
    ss_res = np.sum((targets - predictions)**2)
    ss_tot = np.sum((targets - np.mean(targets))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    metrics = {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "R²": r2,
        "Mean Prediction": np.mean(predictions),
        "Mean Target": np.mean(targets),
        "Std Prediction": np.std(predictions),
        "Std Target": np.std(targets)
    }
    
    return metrics, predictions, targets


def plot_predictions(predictions, targets, save_path=None):
    """Plot predictions vs targets."""
    plt.figure(figsize=(10, 8))
    
    # Scatter plot
    plt.subplot(2, 2, 1)
    plt.scatter(targets, predictions, alpha=0.5)
    plt.plot([targets.min(), targets.max()], 
             [targets.min(), targets.max()], 'r--', lw=2)
    plt.xlabel("True Hours Until Sunset")
    plt.ylabel("Predicted Hours Until Sunset")
    plt.title("Predictions vs Targets")
    plt.grid(True, alpha=0.3)
    
    # Residuals
    plt.subplot(2, 2, 2)
    residuals = predictions - targets
    plt.scatter(targets, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel("True Hours Until Sunset")
    plt.ylabel("Residuals")
    plt.title("Residual Plot")
    plt.grid(True, alpha=0.3)
    
    # Distribution of errors
    plt.subplot(2, 2, 3)
    plt.hist(residuals, bins=30, edgecolor='black')
    plt.xlabel("Prediction Error (hours)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Prediction Errors")
    plt.grid(True, alpha=0.3)
    
    # Time series (if sorted by time)
    plt.subplot(2, 2, 4)
    indices = np.arange(len(predictions))
    plt.plot(indices, targets, label="True", alpha=0.7)
    plt.plot(indices, predictions, label="Predicted", alpha=0.7)
    plt.xlabel("Sample Index")
    plt.ylabel("Hours Until Sunset")
    plt.title("Predictions Over Samples")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Plot saved to {save_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Evaluate sunset prediction model")
    parser.add_argument("--test-metadata", type=str, required=True,
                       help="Path to test metadata JSON")
    parser.add_argument("--image-dir", type=str, required=True,
                       help="Directory containing images")
    parser.add_argument("--checkpoint", type=str, required=True,
                       help="Path to model checkpoint")
    parser.add_argument("--model-type", type=str, default="resnet18",
                       choices=["resnet18", "resnet34", "resnet50", "simple"],
                       help="Model architecture")
    parser.add_argument("--batch-size", type=int, default=32,
                       help="Batch size")
    parser.add_argument("--device", type=str, default="cuda",
                       help="Device to use (cuda/cpu)")
    parser.add_argument("--output-dir", type=str, default="evaluation",
                       help="Directory to save evaluation results")
    
    args = parser.parse_args()
    
    # Set device
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    if args.device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        device = torch.device("cpu")
    
    # Create data loader (we only need test loader)
    print("Loading test data...")
    from dataset_builder import SunsetDataset
    from torch.utils.data import DataLoader
    from torchvision import transforms
    import json
    
    with open(args.test_metadata, "r") as f:
        test_meta = json.load(f)
    
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    test_dataset = SunsetDataset(test_meta, args.image_dir, transform=test_transform)
    test_loader = DataLoader(
        test_dataset, batch_size=args.batch_size, shuffle=False,
        num_workers=4, pin_memory=True
    )
    
    # Create model
    print(f"Creating {args.model_type} model...")
    model = create_model(args.model_type, pretrained=False)
    
    # Evaluate
    print("Evaluating model...")
    metrics, predictions, targets = evaluate_model(
        model, test_loader, device, args.checkpoint
    )
    
    # Print metrics
    print("\nEvaluation Metrics:")
    print("-" * 50)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    # Save metrics
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "metrics.json", "w") as f:
        json.dump({k: float(v) if isinstance(v, np.number) else v 
                  for k, v in metrics.items()}, f, indent=2)
    
    # Plot results
    plot_path = output_path / "evaluation_plots.png"
    plot_predictions(predictions, targets, plot_path)
    
    print(f"\nEvaluation complete! Results saved to {output_path}")


if __name__ == "__main__":
    main()

