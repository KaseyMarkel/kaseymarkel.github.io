"""
Train model to predict both:
1. Sunset aesthetic quality (1-10 scale)
2. Peak time (minutes relative to sun-under-horizon)

Uses midday images + weather features as input.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class SunsetDataset(Dataset):
    """Dataset for sunset prediction."""
    def __init__(self, midday_images, quality_scores, peak_times, durations_above_5=None, weather_features=None):
        self.midday_images = midday_images
        self.quality_scores = quality_scores
        self.peak_times = peak_times
        self.durations_above_5 = durations_above_5 if durations_above_5 is not None else [0.0] * len(midday_images)
        self.weather_features = weather_features
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def __len__(self):
        return len(self.midday_images)
    
    def __getitem__(self, idx):
        # Load image
        img = Image.open(self.midday_images[idx]).convert('RGB')
        img_tensor = self.transform(img)
        
        # Quality score
        quality = torch.tensor(self.quality_scores[idx], dtype=torch.float32)
        
        # Peak time
        peak_time = torch.tensor(self.peak_times[idx], dtype=torch.float32)
        
        # Duration above quality 5
        duration = torch.tensor(self.durations_above_5[idx], dtype=torch.float32)
        
        # Weather features (if available)
        if self.weather_features is not None:
            weather = torch.tensor(self.weather_features[idx], dtype=torch.float32)
            return img_tensor, weather, quality, peak_time, duration
        else:
            return img_tensor, quality, peak_time, duration

class DualPredictor(nn.Module):
    """Model that predicts both quality and peak time."""
    def __init__(self, num_weather_features=0):
        super().__init__()
        
        # Image encoder (ResNet backbone)
        from torchvision.models import resnet18
        self.image_encoder = resnet18(pretrained=True)
        self.image_encoder.fc = nn.Identity()  # Remove final layer
        
        # Weather features
        self.has_weather = num_weather_features > 0
        if self.has_weather:
            self.weather_fc = nn.Linear(num_weather_features, 64)
        
        # Combined features
        combined_dim = 512 + (64 if self.has_weather else 0)
        
        # Quality predictor
        self.quality_head = nn.Sequential(
            nn.Linear(combined_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Scale to 0-1, then multiply by 10
        )
        
        # Peak time predictor
        self.peak_time_head = nn.Sequential(
            nn.Linear(combined_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)  # Regression output
        )
        
        # Duration above quality 5 predictor
        self.duration_head = nn.Sequential(
            nn.Linear(combined_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.ReLU()  # Duration must be non-negative
        )
    
    def forward(self, image, weather=None):
        # Image features
        img_features = self.image_encoder(image)
        
        # Weather features
        if self.has_weather and weather is not None:
            weather_features = self.weather_fc(weather)
            combined = torch.cat([img_features, weather_features], dim=1)
        else:
            combined = img_features
        
        # Predictions
        quality = self.quality_head(combined) * 10  # Scale to 1-10
        peak_time = self.peak_time_head(combined)
        duration = self.duration_head(combined)  # Duration in minutes
        
        return quality.squeeze(), peak_time.squeeze(), duration.squeeze()

def load_training_data(train_file="data/training/train_dataset.json",
                      test_file="data/training/test_dataset.json"):
    """Load training data from prepared datasets."""
    # Load train set
    with open(train_file, "r") as f:
        train_data = json.load(f)
    
    # Load test set
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Extract data
    train_images = [Path(d["midday_image"]) for d in train_data]
    train_quality = [d["quality_score"] for d in train_data]
    train_peak = [d["peak_time_minutes"] for d in train_data]
    train_duration = [d.get("duration_above_5_minutes", 0.0) for d in train_data]
    
    test_images = [Path(d["midday_image"]) for d in test_data]
    test_quality = [d["quality_score"] for d in test_data]
    test_peak = [d["peak_time_minutes"] for d in test_data]
    test_duration = [d.get("duration_above_5_minutes", 0.0) for d in test_data]
    
    print(f"Loaded training data:")
    print(f"  Train: {len(train_images)} samples")
    print(f"  Test: {len(test_images)} samples")
    print(f"  Quality scores: {np.mean(train_quality):.2f} ± {np.std(train_quality):.2f}")
    print(f"  Peak times: {np.mean(train_peak):.2f} ± {np.std(train_peak):.2f} minutes")
    print(f"  Duration above 5: {np.mean(train_duration):.2f} ± {np.std(train_duration):.2f} minutes")
    
    return (train_images, train_quality, train_peak, train_duration), (test_images, test_quality, test_peak, test_duration)

def train_model(train_data, test_data, weather_features=None):
    """Train the triple predictor model (quality, peak time, duration above 5)."""
    train_images, train_quality, train_peak, train_duration = train_data
    test_images, test_quality, test_peak, test_duration = test_data
    
    # Create datasets
    train_dataset = SunsetDataset(train_images, train_quality, train_peak, train_duration, weather_features)
    val_dataset = SunsetDataset(test_images, test_quality, test_peak, test_duration, weather_features)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    
    # Model
    num_weather = len(weather_features[0]) if weather_features else 0
    model = DualPredictor(num_weather_features=num_weather)
    
    # Loss and optimizer
    quality_loss_fn = nn.MSELoss()
    peak_time_loss_fn = nn.MSELoss()
    duration_loss_fn = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    num_epochs = 50
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    print(f"\nTraining on {device}...")
    
    for epoch in range(num_epochs):
        model.train()
        train_quality_loss = 0
        train_peak_loss = 0
        train_duration_loss = 0
        
        for batch in train_loader:
            if weather_features:
                images, weather, quality, peak_time, duration = batch
                images, weather, quality, peak_time, duration = images.to(device), weather.to(device), quality.to(device), peak_time.to(device), duration.to(device)
                pred_quality, pred_peak, pred_duration = model(images, weather)
            else:
                images, quality, peak_time, duration = batch
                images, quality, peak_time, duration = images.to(device), quality.to(device), peak_time.to(device), duration.to(device)
                pred_quality, pred_peak, pred_duration = model(images)
            
            quality_loss = quality_loss_fn(pred_quality, quality)
            peak_loss = peak_time_loss_fn(pred_peak, peak_time)
            duration_loss = duration_loss_fn(pred_duration, duration)
            total_loss = quality_loss + peak_loss + duration_loss
            
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
            
            train_quality_loss += quality_loss.item()
            train_peak_loss += peak_loss.item()
            train_duration_loss += duration_loss.item()
        
        # Validation
        model.eval()
        val_quality_loss = 0
        val_peak_loss = 0
        val_duration_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                if weather_features:
                    images, weather, quality, peak_time, duration = batch
                    images, weather, quality, peak_time, duration = images.to(device), weather.to(device), quality.to(device), peak_time.to(device), duration.to(device)
                    pred_quality, pred_peak, pred_duration = model(images, weather)
                else:
                    images, quality, peak_time, duration = batch
                    images, quality, peak_time, duration = images.to(device), quality.to(device), peak_time.to(device), duration.to(device)
                    pred_quality, pred_peak, pred_duration = model(images)
                
                val_quality_loss += quality_loss_fn(pred_quality, quality).item()
                val_peak_loss += peak_time_loss_fn(pred_peak, peak_time).item()
                val_duration_loss += duration_loss_fn(pred_duration, duration).item()
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train - Quality: {train_quality_loss/len(train_loader):.4f}, Peak: {train_peak_loss/len(train_loader):.4f}, Duration: {train_duration_loss/len(train_loader):.4f}")
            print(f"  Val   - Quality: {val_quality_loss/len(val_loader):.4f}, Peak: {val_peak_loss/len(val_loader):.4f}, Duration: {val_duration_loss/len(val_loader):.4f}")
    
    # Save model
    model_path = Path("models/dual_predictor.pth")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"\n✓ Model saved: {model_path}")
    
    return model

if __name__ == "__main__":
    print("=" * 70)
    print("TRAINING DUAL PREDICTOR MODEL")
    print("=" * 70)
    
    print("\n[1/3] Loading training data...")
    train_data, test_data = load_training_data()
    
    train_images, train_quality, train_peak, train_duration = train_data
    
    if len(train_images) < 10:
        print(f"\n⚠ Warning: Only {len(train_images)} training samples.")
        print("This is quite small - model may overfit.")
        print("Consider grading more images or using strong regularization.")
    
    print("\n[2/3] Training model...")
    model = train_model(train_data, test_data)
    
    print("\n[3/3] Training complete!")
    print("\nModel saved to: models/dual_predictor.pth")
    print("\nNext: Evaluate model with:")
    print("  python3 evaluate_dual_predictor.py")

