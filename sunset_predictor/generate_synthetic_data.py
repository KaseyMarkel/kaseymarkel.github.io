"""
Script to generate synthetic training data if historical archive is unavailable.
Creates images with sky-like patterns that vary based on time until sunset.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import json
from pathlib import Path
from datetime import datetime, timedelta
from data_collector import get_sunset_time, BERKELEY_LAT, BERKELEY_LON


def generate_sky_image(hours_until_sunset, width=640, height=480, seed=None):
    """
    Generate a synthetic sky image that simulates appearance based on hours until sunset.
    
    Args:
        hours_until_sunset: Hours until sunset (affects colors)
        width: Image width
        height: Image height
        seed: Random seed for reproducibility
    
    Returns:
        PIL Image
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Create base image
    img = Image.new("RGB", (width, height))
    pixels = np.array(img)
    
    # Color varies based on hours until sunset
    # 3+ hours: bright blue/white (daytime)
    # 1-3 hours: orange/yellow (approaching sunset)
    # <1 hour: deep red/orange (near sunset)
    
    if hours_until_sunset >= 3:
        # Daytime sky - bright blue gradient
        base_color = np.array([135, 206, 250])  # Sky blue
        variation = 30
    elif hours_until_sunset >= 1.5:
        # Late afternoon - orange/yellow tones
        base_color = np.array([255, 165, 0])  # Orange
        variation = 40
    else:
        # Near sunset - red/orange
        base_color = np.array([255, 69, 0])  # Red-orange
        variation = 50
    
    # Create gradient from top (lighter) to bottom (darker)
    for y in range(height):
        # Vertical gradient
        factor = 1.0 - (y / height) * 0.3
        color = (base_color * factor).astype(int)
        
        # Add some horizontal variation
        for x in range(width):
            noise = np.random.randint(-variation, variation, 3)
            pixel_color = np.clip(color + noise, 0, 255)
            pixels[y, x] = pixel_color
    
    # Add some cloud-like patterns
    overlay = Image.fromarray(pixels.astype(np.uint8))
    draw = ImageDraw.Draw(overlay)
    
    # Draw cloud-like shapes
    num_clouds = np.random.randint(3, 8)
    for _ in range(num_clouds):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height // 2)  # Clouds in upper half
        size = np.random.randint(50, 150)
        
        # Cloud color varies with time
        if hours_until_sunset >= 3:
            cloud_color = (255, 255, 255)  # White clouds
        else:
            # Warmer cloud colors near sunset
            cloud_color = (255, 200, 150)
        
        # Draw cloud as overlapping circles
        for offset_x in [-size//3, 0, size//3]:
            for offset_y in [-size//4, 0, size//4]:
                draw.ellipse(
                    [x + offset_x - size//2, y + offset_y - size//2,
                     x + offset_x + size//2, y + offset_y + size//2],
                    fill=cloud_color, outline=None
                )
    
    # Apply slight blur for realism
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=1))
    
    return overlay


def generate_synthetic_dataset(num_samples=200, output_dir="data/synthetic_images",
                               start_date=None, end_date=None):
    """
    Generate a synthetic dataset of sky images.
    
    Args:
        num_samples: Number of images to generate
        output_dir: Directory to save images
        start_date: Start date (default: 30 days ago)
        end_date: End date (default: today)
    
    Returns:
        List of metadata dictionaries
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    if end_date is None:
        end_date = datetime.now()
    
    metadata = []
    
    print(f"Generating {num_samples} synthetic sky images...")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Generate dates evenly distributed
    date_range = (end_date - start_date).days
    dates = [start_date + timedelta(days=i * date_range / num_samples) 
             for i in range(num_samples)]
    
    for i, date in enumerate(dates):
        # Get sunset time for this date
        sunset_time = get_sunset_time(date)
        
        # Generate capture time: 3 hours before sunset ± some variation
        hours_before = 3.0 + np.random.uniform(-0.5, 0.5)  # 2.5 to 3.5 hours
        capture_time = sunset_time - timedelta(hours=hours_before)
        
        # Ensure capture time is reasonable (during daylight)
        if capture_time.hour < 8 or capture_time.hour > 20:
            # Adjust to reasonable time
            capture_time = sunset_time - timedelta(hours=3)
        
        # Generate image
        hours_until = (sunset_time - capture_time).total_seconds() / 3600.0
        img = generate_sky_image(hours_until, seed=i)
        
        # Save image
        filename = f"img_{capture_time.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = output_path / filename
        img.save(filepath, "JPEG")
        
        # Store metadata
        metadata.append({
            "image_path": str(filepath),
            "capture_time": capture_time.isoformat(),
            "sunset_time": sunset_time.isoformat(),
            "hours_before_sunset": hours_until,
            "date": date.date().isoformat(),
            "synthetic": True
        })
        
        if (i + 1) % 50 == 0:
            print(f"Generated {i + 1}/{num_samples} images...")
    
    # Save metadata
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nGenerated {len(metadata)} synthetic images")
    print(f"Metadata saved to {metadata_path}")
    
    return metadata


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic sky images")
    parser.add_argument("--num-samples", type=int, default=200,
                       help="Number of images to generate")
    parser.add_argument("--output-dir", type=str, default="data/synthetic_images",
                       help="Output directory")
    
    args = parser.parse_args()
    
    print("Synthetic Sky Image Generator")
    print("=" * 50)
    print("\nThis script generates synthetic sky images for testing/training")
    print("when historical webcam data is not available.")
    print("\nNote: These are simplified synthetic images.")
    print("For best results, use real webcam images when possible.\n")
    
    generate_synthetic_dataset(
        num_samples=args.num_samples,
        output_dir=args.output_dir
    )

