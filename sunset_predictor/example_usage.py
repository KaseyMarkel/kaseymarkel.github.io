"""
Example usage of the sunset predictor system.
Demonstrates the complete workflow from data collection to prediction.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json

# Example 1: Generate synthetic data (when historical archive unavailable)
print("Example 1: Generating synthetic training data")
print("-" * 50)

from generate_synthetic_data import generate_synthetic_dataset

metadata = generate_synthetic_dataset(
    num_samples=100,
    output_dir="data/example_images"
)
print(f"Generated {len(metadata)} images\n")

# Example 2: Build train/test dataset
print("Example 2: Building train/test datasets")
print("-" * 50)

from dataset_builder import build_dataset

train_meta, test_meta = build_dataset(
    metadata_file="data/example_images/metadata.json",
    image_dir="data/example_images",
    output_dir="data/example_processed",
    test_size=0.2
)
print(f"Train: {len(train_meta)} images, Test: {len(test_meta)} images\n")

# Example 3: Create data loaders
print("Example 3: Creating data loaders")
print("-" * 50)

from dataset_builder import get_data_loaders

train_loader, test_loader = get_data_loaders(
    train_metadata_file="data/example_processed/train_metadata.json",
    test_metadata_file="data/example_processed/test_metadata.json",
    image_dir="data/example_images",
    batch_size=8
)
print(f"Train batches: {len(train_loader)}, Test batches: {len(test_loader)}\n")

# Example 4: Create and test model
print("Example 4: Creating model")
print("-" * 50)

from model import create_model
import torch

model = create_model("resnet18", pretrained=True)
print(f"Model created: {model}")

# Test forward pass
dummy_batch = next(iter(train_loader))
images, labels = dummy_batch
print(f"Input shape: {images.shape}")
print(f"Labels shape: {labels.shape}")

with torch.no_grad():
    predictions = model(images)
    print(f"Predictions shape: {predictions.shape}")
    print(f"Sample predictions: {predictions[:3].tolist()}")
    print(f"Sample labels: {labels[:3].tolist()}\n")

# Example 5: Get sunset time for a date
print("Example 5: Getting sunset times")
print("-" * 50)

from data_collector import get_sunset_time

test_date = datetime(2024, 6, 15)  # June 15, 2024
sunset = get_sunset_time(test_date)
print(f"Sunset time for {test_date.date()}: {sunset.strftime('%H:%M:%S %Z')}")

# Calculate 3 hours before sunset
three_hours_before = sunset - timedelta(hours=3)
print(f"3 hours before sunset: {three_hours_before.strftime('%H:%M:%S %Z')}")
print(f"Hours until sunset: {(sunset - three_hours_before).total_seconds() / 3600:.2f}\n")

print("=" * 50)
print("Example usage complete!")
print("\nTo train a model, run:")
print("  python train.py --train-metadata data/example_processed/train_metadata.json \\")
print("                   --test-metadata data/example_processed/test_metadata.json \\")
print("                   --image-dir data/example_images")
print("\nTo evaluate a trained model, run:")
print("  python evaluate.py --test-metadata data/example_processed/test_metadata.json \\")
print("                      --image-dir data/example_images \\")
print("                      --checkpoint checkpoints/best.pth")

