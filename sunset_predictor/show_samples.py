"""
Display random samples from the dataset with predictions.
"""

import json
import random
import torch
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

from model import create_model
from dataset_builder import SunsetDataset
from torchvision import transforms


def load_model(checkpoint_path, model_type="resnet18", device="cpu"):
    """Load trained model."""
    model = create_model(model_type, pretrained=False)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()
    return model


def show_samples(metadata_file, image_dir, checkpoint_path, num_samples=5, 
                 model_type="resnet18", device="cpu"):
    """Show random samples with predictions."""
    
    # Load metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    # Filter for afternoon images (capture time after 12:00)
    afternoon_samples = []
    for item in metadata:
        capture_time = datetime.fromisoformat(item["capture_time"])
        if capture_time.hour >= 12:
            afternoon_samples.append(item)
    
    if len(afternoon_samples) < num_samples:
        print(f"Only {len(afternoon_samples)} afternoon samples available, using all of them")
        samples = afternoon_samples
    else:
        samples = random.sample(afternoon_samples, num_samples)
    
    # Load model
    print(f"Loading model from {checkpoint_path}...")
    model = load_model(checkpoint_path, model_type, device)
    
    # Image transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Create figure
    fig, axes = plt.subplots(1, num_samples, figsize=(20, 4))
    if num_samples == 1:
        axes = [axes]
    
    for idx, sample in enumerate(samples):
        # Load image
        img_path = Path(sample["image_path"])
        if not img_path.is_absolute():
            img_path = Path(image_dir) / img_path
        
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Create a black image as fallback
            image = Image.new("RGB", (640, 480), color="black")
        
        # Get actual sunset time
        capture_time = datetime.fromisoformat(sample["capture_time"])
        sunset_time = datetime.fromisoformat(sample["sunset_time"])
        hours_until_sunset = (sunset_time - capture_time).total_seconds() / 3600.0
        
        # Get prediction
        img_tensor = transform(image).unsqueeze(0).to(device)
        with torch.no_grad():
            prediction = model(img_tensor).item()
        
        # Calculate error
        error = abs(prediction - hours_until_sunset)
        
        # Display image
        axes[idx].imshow(image)
        axes[idx].axis('off')
        
        # Add text overlay
        info_text = (
            f"Capture: {capture_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"Sunset: {sunset_time.strftime('%H:%M')}\n"
            f"True: {hours_until_sunset:.2f} hrs\n"
            f"Predicted: {prediction:.2f} hrs\n"
            f"Error: {error:.2f} hrs ({error*60:.1f} min)"
        )
        
        axes[idx].text(0.02, 0.98, info_text, 
                      transform=axes[idx].transAxes,
                      fontsize=9, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    output_path = Path("evaluation") / "sample_predictions.png"
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved visualization to {output_path}")
    plt.show()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Show sample predictions")
    parser.add_argument("--metadata", type=str, 
                       default="data/processed/test_metadata.json",
                       help="Metadata file")
    parser.add_argument("--image-dir", type=str, default="data/synthetic_images",
                       help="Image directory")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/best.pth",
                       help="Model checkpoint")
    parser.add_argument("--num-samples", type=int, default=5,
                       help="Number of samples to show")
    parser.add_argument("--model-type", type=str, default="resnet18",
                       help="Model type")
    parser.add_argument("--device", type=str, default="cpu",
                       help="Device")
    
    args = parser.parse_args()
    
    show_samples(
        args.metadata,
        args.image_dir,
        args.checkpoint,
        args.num_samples,
        args.model_type,
        args.device
    )

