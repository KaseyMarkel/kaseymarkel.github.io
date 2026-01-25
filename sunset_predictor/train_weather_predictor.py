"""
Train models using weather data:
1. Weather-only model (no images)
2. Combined model (weather + images)
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from train_dual_predictor import DualPredictor

class WeatherOnlyDataset(Dataset):
    """Dataset using only weather features."""
    def __init__(self, weather_features, quality_scores, peak_times, durations_above_5):
        self.weather_features = weather_features
        self.quality_scores = quality_scores
        self.peak_times = peak_times
        self.durations_above_5 = durations_above_5
    
    def __len__(self):
        return len(self.weather_features)
    
    def __getitem__(self, idx):
        weather = torch.tensor(self.weather_features[idx], dtype=torch.float32)
        quality = torch.tensor(self.quality_scores[idx], dtype=torch.float32)
        peak_time = torch.tensor(self.peak_times[idx], dtype=torch.float32)
        duration = torch.tensor(self.durations_above_5[idx], dtype=torch.float32)
        
        return weather, quality, peak_time, duration

class WeatherOnlyPredictor(nn.Module):
    """Model that predicts from weather features only."""
    def __init__(self, num_weather_features):
        super().__init__()
        
        # Weather feature encoder
        self.weather_encoder = nn.Sequential(
            nn.Linear(num_weather_features, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32)
        )
        
        # Quality predictor
        self.quality_head = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Peak time predictor
        self.peak_time_head = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 1)
        )
        
        # Duration predictor
        self.duration_head = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, 1),
            nn.ReLU()
        )
    
    def forward(self, weather):
        features = self.weather_encoder(weather)
        
        quality = self.quality_head(features) * 10.0
        peak_time = self.peak_time_head(features)
        duration = self.duration_head(features)
        
        return quality.squeeze(), peak_time.squeeze(), duration.squeeze()

def train_weather_only_model(train_data, test_data):
    """Train weather-only model."""
    print("\n" + "=" * 70)
    print("TRAINING WEATHER-ONLY MODEL")
    print("=" * 70)
    
    # Extract data
    train_weather = np.array([d['weather_features'] for d in train_data])
    train_quality = np.array([d['quality_score'] for d in train_data])
    train_peak = np.array([d['peak_time_minutes'] for d in train_data])
    train_duration = np.array([d.get('duration_above_5_minutes', 0) for d in train_data])
    
    test_weather = np.array([d['weather_features'] for d in test_data])
    test_quality = np.array([d['quality_score'] for d in test_data])
    test_peak = np.array([d['peak_time_minutes'] for d in test_data])
    test_duration = np.array([d.get('duration_above_5_minutes', 0) for d in test_data])
    
    num_features = train_weather.shape[1]
    
    # Create datasets
    train_dataset = WeatherOnlyDataset(train_weather, train_quality, train_peak, train_duration)
    test_dataset = WeatherOnlyDataset(test_weather, test_quality, test_peak, test_duration)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    
    # Model
    model = WeatherOnlyPredictor(num_weather_features=num_features)
    
    # Loss and optimizer
    quality_loss_fn = nn.MSELoss()
    peak_loss_fn = nn.MSELoss()
    duration_loss_fn = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training
    num_epochs = 50
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    print(f"\nTraining on {device}...")
    print(f"Weather features: {num_features}")
    
    for epoch in range(num_epochs):
        model.train()
        train_losses = {'quality': 0, 'peak': 0, 'duration': 0}
        
        for weather, quality, peak_time, duration in train_loader:
            weather = weather.to(device)
            quality = quality.to(device)
            peak_time = peak_time.to(device)
            duration = duration.to(device)
            
            pred_quality, pred_peak, pred_duration = model(weather)
            
            q_loss = quality_loss_fn(pred_quality, quality)
            p_loss = peak_loss_fn(pred_peak, peak_time)
            d_loss = duration_loss_fn(pred_duration, duration)
            total_loss = q_loss + p_loss + d_loss
            
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()
            
            train_losses['quality'] += q_loss.item()
            train_losses['peak'] += p_loss.item()
            train_losses['duration'] += d_loss.item()
        
        # Validation
        if (epoch + 1) % 10 == 0:
            model.eval()
            val_losses = {'quality': 0, 'peak': 0, 'duration': 0}
            
            with torch.no_grad():
                for weather, quality, peak_time, duration in test_loader:
                    weather = weather.to(device)
                    quality = quality.to(device)
                    peak_time = peak_time.to(device)
                    duration = duration.to(device)
                    
                    pred_quality, pred_peak, pred_duration = model(weather)
                    
                    val_losses['quality'] += quality_loss_fn(pred_quality, quality).item()
                    val_losses['peak'] += peak_loss_fn(pred_peak, peak_time).item()
                    val_losses['duration'] += duration_loss_fn(pred_duration, duration).item()
            
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train - Q: {train_losses['quality']/len(train_loader):.4f}, "
                  f"P: {train_losses['peak']/len(train_loader):.4f}, "
                  f"D: {train_losses['duration']/len(train_loader):.4f}")
            print(f"  Val   - Q: {val_losses['quality']/len(test_loader):.4f}, "
                  f"P: {val_losses['peak']/len(test_loader):.4f}, "
                  f"D: {val_losses['duration']/len(test_loader):.4f}")
    
    # Save model
    model_path = Path("models/weather_only_predictor.pth")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"\n✓ Weather-only model saved: {model_path}")
    
    return model

def train_combined_model(train_data, test_data):
    """Train combined model (weather + images)."""
    print("\n" + "=" * 70)
    print("TRAINING COMBINED MODEL (WEATHER + IMAGES)")
    print("=" * 70)
    
    # This will use the existing DualPredictor but with weather features
    # Implementation similar to train_dual_predictor.py but with weather
    # For now, return placeholder
    print("⚠ Combined model training not yet implemented")
    print("  Will use DualPredictor with weather features enabled")
    
    return None

if __name__ == "__main__":
    # Load datasets with weather
    train_file = Path("data/training/train_dataset_weather.json")
    test_file = Path("data/training/test_dataset_weather.json")
    
    if not train_file.exists() or not test_file.exists():
        print("⚠ Weather datasets not found. Run prepare_weather_features.py first.")
        exit(1)
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    print(f"Loaded datasets:")
    print(f"  Train: {len(train_data)} samples")
    print(f"  Test: {len(test_data)} samples")
    
    # Train weather-only model
    weather_model = train_weather_only_model(train_data, test_data)
    
    # Train combined model
    # combined_model = train_combined_model(train_data, test_data)
    
    print("\n" + "=" * 70)
    print("✓ TRAINING COMPLETE")
    print("=" * 70)
    print("\nNext: Evaluate models with:")
    print("  python3 evaluate_weather_models.py")

