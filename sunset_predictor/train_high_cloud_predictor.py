"""
Train a simple model using high-level cloud cover as the main predictor.
Uses the sweet spot hypothesis: 5-80% high cloud cover predicts better sunsets.
"""

import json
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from scipy.stats import pearsonr

class HighCloudDataset(Dataset):
    """Dataset using high-level cloud cover."""
    def __init__(self, high_cloud, quality_scores, peak_times, durations_above_5):
        self.high_cloud = high_cloud
        self.quality_scores = quality_scores
        self.peak_times = peak_times
        self.durations_above_5 = durations_above_5
    
    def __len__(self):
        return len(self.high_cloud)
    
    def __getitem__(self, idx):
        # Use high cloud as single feature, normalized
        cloud_feature = torch.tensor([self.high_cloud[idx] / 100.0], dtype=torch.float32)
        quality = torch.tensor(self.quality_scores[idx], dtype=torch.float32)
        peak_time = torch.tensor(self.peak_times[idx], dtype=torch.float32)
        duration = torch.tensor(self.durations_above_5[idx], dtype=torch.float32)
        
        return cloud_feature, quality, peak_time, duration

class HighCloudPredictor(nn.Module):
    """Simple model using high-level cloud cover."""
    def __init__(self):
        super().__init__()
        
        # Simple model: cloud cover -> predictions
        self.quality_head = nn.Sequential(
            nn.Linear(1, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        self.peak_time_head = nn.Sequential(
            nn.Linear(1, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        self.duration_head = nn.Sequential(
            nn.Linear(1, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.ReLU()
        )
    
    def forward(self, cloud):
        quality = self.quality_head(cloud) * 10.0
        peak_time = self.peak_time_head(cloud)
        duration = self.duration_head(cloud)
        
        return quality.squeeze(), peak_time.squeeze(), duration.squeeze()

def train_high_cloud_model():
    """Train model using high-level cloud cover."""
    print("=" * 70)
    print("TRAINING HIGH-LEVEL CLOUD PREDICTOR")
    print("=" * 70)
    
    # Load datasets
    train_file = Path("data/training/train_dataset_weather.json")
    test_file = Path("data/training/test_dataset_weather.json")
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Load high cloud data
    cloud_df = pd.read_csv("data/weather/high_cloud_data.csv")
    cloud_df['date'] = cloud_df['date'].astype(str)
    cloud_dict = {str(row['date']): row['cloud_cover_high'] for _, row in cloud_df.iterrows()}
    
    # Match dates
    train_samples = []
    test_samples = []
    
    for sample in train_data:
        if sample['date'] in cloud_dict and pd.notna(cloud_dict[sample['date']]):
            train_samples.append({
                'date': sample['date'],
                'high_cloud': cloud_dict[sample['date']],
                'quality': sample['quality_score'],
                'peak_time': sample['peak_time_minutes'],
                'duration': sample.get('duration_above_5_minutes', 0)
            })
    
    for sample in test_data:
        if sample['date'] in cloud_dict and pd.notna(cloud_dict[sample['date']]):
            test_samples.append({
                'date': sample['date'],
                'high_cloud': cloud_dict[sample['date']],
                'quality': sample['quality_score'],
                'peak_time': sample['peak_time_minutes'],
                'duration': sample.get('duration_above_5_minutes', 0)
            })
    
    print(f"\nMatched cloud data:")
    print(f"  Train: {len(train_samples)} samples")
    print(f"  Test: {len(test_samples)} samples")
    
    if len(train_samples) == 0 or len(test_samples) == 0:
        print("⚠ Not enough data to train")
        return None
    
    # Extract features
    train_cloud = np.array([s['high_cloud'] for s in train_samples])
    train_quality = np.array([s['quality'] for s in train_samples])
    train_peak = np.array([s['peak_time'] for s in train_samples])
    train_duration = np.array([s['duration'] for s in train_samples])
    
    test_cloud = np.array([s['high_cloud'] for s in test_samples])
    test_quality = np.array([s['quality'] for s in test_samples])
    test_peak = np.array([s['peak_time'] for s in test_samples])
    test_duration = np.array([s['duration'] for s in test_samples])
    
    # Create datasets
    train_dataset = HighCloudDataset(train_cloud, train_quality, train_peak, train_duration)
    test_dataset = HighCloudDataset(test_cloud, test_quality, test_peak, test_duration)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    
    # Model
    model = HighCloudPredictor()
    
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
    
    for epoch in range(num_epochs):
        model.train()
        train_losses = {'quality': 0, 'peak': 0, 'duration': 0}
        
        for cloud, quality, peak_time, duration in train_loader:
            cloud = cloud.to(device)
            quality = quality.to(device)
            peak_time = peak_time.to(device)
            duration = duration.to(device)
            
            pred_quality, pred_peak, pred_duration = model(cloud)
            
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
        
        if (epoch + 1) % 10 == 0:
            model.eval()
            val_losses = {'quality': 0, 'peak': 0, 'duration': 0}
            
            with torch.no_grad():
                for cloud, quality, peak_time, duration in test_loader:
                    cloud = cloud.to(device)
                    quality = quality.to(device)
                    peak_time = peak_time.to(device)
                    duration = duration.to(device)
                    
                    pred_quality, pred_peak, pred_duration = model(cloud)
                    
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
    model_path = Path("models/high_cloud_predictor.pth")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    print(f"\n✓ High-cloud model saved: {model_path}")
    
    # Evaluate
    model.eval()
    predictions_quality = []
    predictions_peak = []
    predictions_duration = []
    
    with torch.no_grad():
        for cloud, quality, peak_time, duration in test_loader:
            cloud = cloud.to(device)
            pred_quality, pred_peak, pred_duration = model(cloud)
            
            predictions_quality.extend(pred_quality.cpu().numpy())
            predictions_peak.extend(pred_peak.cpu().numpy())
            predictions_duration.extend(pred_duration.cpu().numpy())
    
    # Calculate metrics
    quality_mae = np.mean(np.abs(predictions_quality - test_quality))
    quality_rmse = np.sqrt(np.mean((predictions_quality - test_quality)**2))
    quality_corr, quality_p = pearsonr(test_quality, predictions_quality)
    
    peak_mae = np.mean(np.abs(predictions_peak - test_peak))
    peak_rmse = np.sqrt(np.mean((predictions_peak - test_peak)**2))
    peak_corr, peak_p = pearsonr(test_peak, predictions_peak)
    
    duration_mae = np.mean(np.abs(predictions_duration - test_duration))
    duration_rmse = np.sqrt(np.mean((predictions_duration - test_duration)**2))
    duration_corr, duration_p = pearsonr(test_duration, predictions_duration)
    
    results = {
        "model": "high_cloud_only",
        "quality": {
            "mae": float(quality_mae),
            "rmse": float(quality_rmse),
            "correlation": float(quality_corr),
            "p_value": float(quality_p)
        },
        "peak_time": {
            "mae": float(peak_mae),
            "rmse": float(peak_rmse),
            "correlation": float(peak_corr),
            "p_value": float(peak_p)
        },
        "duration": {
            "mae": float(duration_mae),
            "rmse": float(duration_rmse),
            "correlation": float(duration_corr),
            "p_value": float(duration_p)
        },
        "predictions": [
            {
                "date": test_samples[i]["date"],
                "high_cloud_cover": float(test_cloud[i]),
                "true_quality": float(test_quality[i]),
                "pred_quality": float(predictions_quality[i]),
                "true_peak_time": float(test_peak[i]),
                "pred_peak_time": float(predictions_peak[i]),
                "true_duration_above_5": float(test_duration[i]),
                "pred_duration_above_5": float(predictions_duration[i])
            }
            for i in range(len(test_samples))
        ]
    }
    
    # Save results
    output_file = Path("data/training/high_cloud_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved: {output_file}")
    print(f"\nHigh-cloud model performance:")
    print(f"  Quality: MAE={quality_mae:.2f}, r={quality_corr:.3f} (p={quality_p:.3f})")
    print(f"  Peak Time: MAE={peak_mae:.2f} min, r={peak_corr:.3f} (p={peak_p:.3f})")
    print(f"  Duration: MAE={duration_mae:.2f} min, r={duration_corr:.3f} (p={duration_p:.3f})")
    
    return model, results

if __name__ == "__main__":
    train_high_cloud_model()

