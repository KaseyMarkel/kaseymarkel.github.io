"""
Dataset builder for sunset prediction.
Creates train/test splits and prepares data for model training.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import pickle


class SunsetDataset(Dataset):
    """
    PyTorch Dataset for sunset prediction from images.
    """
    
    def __init__(self, metadata, image_dir, transform=None, target_type="hours_until_sunset"):
        """
        Args:
            metadata: List of metadata dictionaries
            image_dir: Base directory for images
            transform: Image transforms
            target_type: What to predict - "hours_until_sunset" or "sunset_time"
        """
        self.metadata = metadata
        self.image_dir = Path(image_dir)
        self.transform = transform
        self.target_type = target_type
        
        if self.transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
    
    def __len__(self):
        return len(self.metadata)
    
    def __getitem__(self, idx):
        item = self.metadata[idx]
        
        # Load image
        img_path = Path(item["image_path"])
        if not img_path.is_absolute():
            img_path = self.image_dir / img_path
        
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            # Return a black image as fallback
            image = Image.new("RGB", (224, 224), color="black")
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get target
        if self.target_type == "hours_until_sunset":
            # Predict hours until sunset
            capture_time = datetime.fromisoformat(item["capture_time"])
            sunset_time = datetime.fromisoformat(item["sunset_time"])
            hours_until = (sunset_time - capture_time).total_seconds() / 3600.0
            target = torch.tensor(hours_until, dtype=torch.float32)
        else:
            # Predict sunset time as hours from midnight
            sunset_time = datetime.fromisoformat(item["sunset_time"])
            hours_from_midnight = sunset_time.hour + sunset_time.minute / 60.0
            target = torch.tensor(hours_from_midnight, dtype=torch.float32)
        
        return image, target


def create_train_test_split(metadata, test_size=0.2, random_state=42, 
                           stratify_by_date=True):
    """
    Create train/test split from metadata.
    
    Args:
        metadata: List of metadata dictionaries
        test_size: Proportion of data for test set
        random_state: Random seed
        stratify_by_date: If True, ensure both sets have similar date distributions
    
    Returns:
        train_metadata, test_metadata
    """
    if stratify_by_date:
        # Extract dates for stratification
        dates = [item["date"] for item in metadata]
        train_meta, test_meta = train_test_split(
            metadata, test_size=test_size, random_state=random_state,
            stratify=dates if len(set(dates)) > 1 else None
        )
    else:
        train_meta, test_meta = train_test_split(
            metadata, test_size=test_size, random_state=random_state
        )
    
    return train_meta, test_meta


def build_dataset(metadata_file, image_dir, output_dir="data/processed",
                  test_size=0.2, random_state=42):
    """
    Build train/test datasets from metadata.
    
    Args:
        metadata_file: Path to metadata JSON file
        image_dir: Directory containing images
        output_dir: Directory to save processed datasets
        test_size: Proportion for test set
        random_state: Random seed
    
    Returns:
        train_metadata, test_metadata
    """
    # Load metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    print(f"Loaded {len(metadata)} images")
    
    # Create train/test split
    train_meta, test_meta = create_train_test_split(
        metadata, test_size=test_size, random_state=random_state
    )
    
    print(f"Train set: {len(train_meta)} images")
    print(f"Test set: {len(test_meta)} images")
    
    # Save splits
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / "train_metadata.json", "w") as f:
        json.dump(train_meta, f, indent=2)
    
    with open(output_path / "test_metadata.json", "w") as f:
        json.dump(test_meta, f, indent=2)
    
    print(f"Saved train/test splits to {output_path}")
    
    # Print statistics
    print("\nDataset Statistics:")
    print("-" * 50)
    
    train_hours = [item.get("hours_before_sunset", 0) for item in train_meta]
    test_hours = [item.get("hours_before_sunset", 0) for item in test_meta]
    
    print(f"Train - Hours before sunset: mean={np.mean(train_hours):.2f}, "
          f"std={np.std(train_hours):.2f}")
    print(f"Test - Hours before sunset: mean={np.mean(test_hours):.2f}, "
          f"std={np.std(test_hours):.2f}")
    
    return train_meta, test_meta


def get_data_loaders(train_metadata_file, test_metadata_file, image_dir,
                    batch_size=32, num_workers=4, image_size=224):
    """
    Create PyTorch DataLoaders for training and testing.
    
    Args:
        train_metadata_file: Path to train metadata JSON
        test_metadata_file: Path to test metadata JSON
        image_dir: Directory containing images
        batch_size: Batch size
        num_workers: Number of worker processes
        image_size: Target image size
    
    Returns:
        train_loader, test_loader
    """
    # Load metadata
    with open(train_metadata_file, "r") as f:
        train_meta = json.load(f)
    
    with open(test_metadata_file, "r") as f:
        test_meta = json.load(f)
    
    # Define transforms
    train_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    test_transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Create datasets
    train_dataset = SunsetDataset(train_meta, image_dir, transform=train_transform)
    test_dataset = SunsetDataset(test_meta, image_dir, transform=test_transform)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True
    )
    
    return train_loader, test_loader


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build sunset prediction dataset")
    parser.add_argument("--metadata", type=str, required=True,
                       help="Path to metadata JSON file")
    parser.add_argument("--image-dir", type=str, required=True,
                       help="Directory containing images")
    parser.add_argument("--output-dir", type=str, default="data/processed",
                       help="Output directory for processed datasets")
    parser.add_argument("--test-size", type=float, default=0.2,
                       help="Proportion of data for test set")
    
    args = parser.parse_args()
    
    build_dataset(
        args.metadata,
        args.image_dir,
        args.output_dir,
        test_size=args.test_size
    )

