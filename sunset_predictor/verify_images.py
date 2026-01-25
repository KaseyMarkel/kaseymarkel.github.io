"""
Verify images before training - check that they're actual sky photos.
"""

import json
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime


def verify_images(metadata_file, image_dir, num_samples=10):
    """
    Verify images are real sky photos, not synthetic.
    Display sample images for manual inspection.
    """
    # Load metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    print(f"Found {len(metadata)} images in metadata")
    print(f"Showing {min(num_samples, len(metadata))} samples for verification\n")
    
    # Get sample images
    import random
    samples = random.sample(metadata, min(num_samples, len(metadata)))
    
    # Create figure
    cols = 5
    rows = (len(samples) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(20, 4*rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    for idx, sample in enumerate(samples):
        row = idx // cols
        col = idx % cols
        ax = axes[row, col]
        
        # Load image - handle different path formats
        img_path_str = sample["image_path"]
        img_path = Path(img_path_str)
        
        # If absolute path, use as-is
        if img_path.is_absolute():
            pass
        # If path already includes image_dir, use it directly (it's relative to current dir)
        elif str(img_path).startswith("data/"):
            # Path is like "data/synthetic_images/file.jpg" - use as-is from project root
            pass
        # Otherwise, join with image_dir
        else:
            img_path = Path(image_dir) / img_path
        
        try:
            # Ensure we're using the correct path
            if not img_path.exists() and Path(image_dir).exists():
                # Try with just filename
                img_path = Path(image_dir) / Path(sample["image_path"]).name
            
            if not img_path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")
            
            image = Image.open(img_path)
            ax.imshow(image)
            
            # Check if it's synthetic (very uniform colors = synthetic)
            import numpy as np
            img_array = np.array(image)
            color_std = img_array.std(axis=(0, 1)).mean()
            
            capture_time = datetime.fromisoformat(sample["capture_time"])
            sunset_time = datetime.fromisoformat(sample["sunset_time"])
            hours_until = (sunset_time - capture_time).total_seconds() / 3600.0
            
            title = f"{capture_time.strftime('%m/%d %H:%M')}\n{hours_until:.1f}h until sunset"
            
            # Mark synthetic images
            if color_std < 20:  # Very uniform = likely synthetic
                title += "\n⚠ SYNTHETIC?"
                ax.set_facecolor('yellow')
            else:
                title += "\n✓ Real sky?"
            
            ax.set_title(title, fontsize=8)
            ax.axis('off')
            
        except Exception as e:
            ax.text(0.5, 0.5, f"Error:\n{str(e)[:30]}", 
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')
    
    # Hide extra subplots
    for idx in range(len(samples), rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row, col].axis('off')
    
    plt.tight_layout()
    output_path = Path("evaluation") / "image_verification.png"
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved verification to {output_path}")
    plt.show()
    
    # Summary
    print("\n" + "="*50)
    print("VERIFICATION SUMMARY")
    print("="*50)
    print("\nPlease review the images above.")
    print("If images look synthetic (uniform colors, simple gradients):")
    print("  → These are NOT real sky photos")
    print("  → Need to collect real LBNL webcam images")
    print("\nIf images look like real sky photos:")
    print("  → Ready to train!")
    print("\nTo collect real images:")
    print("  1. Find LBNL webcam URL")
    print("  2. Download images manually or use download script")
    print("  3. Update metadata.json with real image paths")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify images before training")
    parser.add_argument("--metadata", type=str, 
                       default="data/processed/train_metadata.json",
                       help="Metadata file")
    parser.add_argument("--image-dir", type=str, default="data/synthetic_images",
                       help="Image directory")
    parser.add_argument("--num-samples", type=int, default=10,
                       help="Number of samples to show")
    
    args = parser.parse_args()
    
    verify_images(args.metadata, args.image_dir, args.num_samples)

