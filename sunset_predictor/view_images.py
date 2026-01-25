"""
Simple image viewer to check if images are actually visible.
"""

import json
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import random

def view_images(metadata_file, image_dir, num_samples=5):
    """View images directly."""
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    
    samples = random.sample(metadata, min(num_samples, len(metadata)))
    
    fig, axes = plt.subplots(1, num_samples, figsize=(20, 4))
    if num_samples == 1:
        axes = [axes]
    
    for idx, sample in enumerate(samples):
        img_path_str = sample["image_path"]
        img_path = Path(img_path_str)
        
        print(f"\nSample {idx+1}:")
        print(f"  Path in metadata: {img_path_str}")
        print(f"  Resolved path: {img_path}")
        print(f"  Exists: {img_path.exists()}")
        
        if img_path.exists():
            img = Image.open(img_path)
            print(f"  Image size: {img.size}")
            print(f"  Image mode: {img.mode}")
            
            # Convert to array to check values
            import numpy as np
            arr = np.array(img)
            print(f"  Pixel range: {arr.min()}-{arr.max()}")
            print(f"  Mean brightness: {arr.mean():.1f}")
            
            axes[idx].imshow(img)
            axes[idx].set_title(f"Sample {idx+1}\n{Path(img_path_str).name}", fontsize=10)
        else:
            # Try alternative path
            alt_path = Path(image_dir) / Path(img_path_str).name
            print(f"  Trying alternative: {alt_path}")
            print(f"  Alternative exists: {alt_path.exists()}")
            
            if alt_path.exists():
                img = Image.open(alt_path)
                axes[idx].imshow(img)
                axes[idx].set_title(f"Sample {idx+1}\n(alt path)", fontsize=10)
            else:
                axes[idx].text(0.5, 0.5, "NOT FOUND", ha='center', va='center', 
                              fontsize=20, color='red')
                print(f"  ERROR: Image not found!")
        
        axes[idx].axis('off')
    
    plt.tight_layout()
    output_path = Path("evaluation") / "direct_image_view.png"
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved to {output_path}")
    print("Check this file - images should be visible!")
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", default="data/processed/train_metadata.json")
    parser.add_argument("--image-dir", default="data/synthetic_images")
    parser.add_argument("--num-samples", type=int, default=5)
    args = parser.parse_args()
    
    view_images(args.metadata, args.image_dir, args.num_samples)

