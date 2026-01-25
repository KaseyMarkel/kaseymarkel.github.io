"""
Collect actual sunset images (at sunset time) for aesthetic grading.
Goal: Get ~300 sunset images for manual quality scoring.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from data_collector import get_sunset_time, BERKELEY_LAT, BERKELEY_LON
import requests
from PIL import Image
from io import BytesIO
import time

def collect_sunset_images(num_sunsets=300, output_dir="data/sunset_images_for_grading",
                         webcam_url=None, start_date=None):
    """
    Collect sunset images at actual sunset times.
    
    Args:
        num_sunsets: Number of sunset images to collect (default: 300)
        output_dir: Directory to save images
        webcam_url: Webcam URL (if None, will try to find)
        start_date: Start date (default: 300 days ago)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_sunsets)
    
    print(f"Collecting {num_sunsets} sunset images...")
    print(f"Date range: {start_date.date()} to {datetime.now().date()}")
    print(f"Output directory: {output_path}")
    print("\nNote: This requires access to LBNL webcam archive or YouTube timelapse.")
    print("If you have a webcam URL, provide it with --webcam-url")
    print("\nFor YouTube timelapse, use process_timelapse.py instead.\n")
    
    metadata = []
    current_date = start_date
    collected = 0
    
    # Try to find webcam URL if not provided
    if webcam_url is None:
        from download_lbnl_images import find_working_webcam_url
        webcam_url = find_working_webcam_url()
    
    if webcam_url:
        print(f"Using webcam: {webcam_url}")
        print("Note: For historical images, you'll need archive access.")
        print("Current webcam only shows current image.\n")
    
    # Generate list of sunset times
    sunset_times = []
    for day in range(num_sunsets):
        date = start_date + timedelta(days=day)
        sunset = get_sunset_time(date)
        sunset_times.append({
            "date": date.date(),
            "sunset_time": sunset,
            "target_time": sunset  # At actual sunset
        })
    
    print(f"Generated {len(sunset_times)} sunset time targets")
    print("\nTo collect images:")
    print("1. Use YouTube timelapse: python3 process_timelapse.py")
    print("2. Download manually from webcam archive")
    print("3. Use existing images in a directory")
    print("\nCreating metadata template...")
    
    # Create metadata template
    metadata = []
    for item in sunset_times:
        metadata.append({
            "date": item["date"].isoformat(),
            "sunset_time": item["sunset_time"].isoformat(),
            "image_path": None,  # To be filled when images are added
            "quality_score": None,  # To be filled during grading
            "graded": False
        })
    
    # Save metadata
    metadata_file = output_path / "sunset_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Created metadata template: {metadata_file}")
    print(f"\nNext steps:")
    print(f"1. Add sunset images to: {output_path}")
    print(f"2. Name them: sunset_YYYYMMDD.jpg (matching dates)")
    print(f"3. Run: python3 setup_grading.py")
    print(f"4. Grade images using the grading interface")
    
    return metadata


def load_existing_sunset_images(image_dir):
    """Load existing sunset images and create metadata."""
    image_path = Path(image_dir)
    
    if not image_path.exists():
        print(f"Directory not found: {image_dir}")
        return []
    
    metadata = []
    
    # Find all images
    image_files = list(image_path.glob("*.jpg")) + list(image_path.glob("*.png"))
    
    print(f"Found {len(image_files)} images in {image_dir}")
    
    for img_file in sorted(image_files):
        # Try to extract date from filename
        # Patterns: sunset_YYYYMMDD.jpg, YYYYMMDD.jpg, etc.
        filename = img_file.stem
        
        try:
            # Try different date patterns
            date_str = None
            if "sunset_" in filename:
                date_str = filename.replace("sunset_", "").split("_")[0]
            elif len(filename) >= 8 and filename[:8].isdigit():
                date_str = filename[:8]
            
            if date_str and len(date_str) == 8:
                date = datetime.strptime(date_str, "%Y%m%d").date()
                sunset_time = get_sunset_time(datetime.combine(date, datetime.min.time()))
                
                metadata.append({
                    "date": date.isoformat(),
                    "sunset_time": sunset_time.isoformat(),
                    "image_path": str(img_file),
                    "quality_score": None,
                    "graded": False
                })
            else:
                # Use modification time as fallback
                mtime = datetime.fromtimestamp(img_file.stat().st_mtime)
                sunset_time = get_sunset_time(mtime)
                metadata.append({
                    "date": mtime.date().isoformat(),
                    "sunset_time": sunset_time.isoformat(),
                    "image_path": str(img_file),
                    "quality_score": None,
                    "graded": False
                })
        except Exception as e:
            print(f"Warning: Could not parse date from {img_file.name}: {e}")
            continue
    
    # Save metadata
    metadata_file = image_path / "sunset_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Created metadata for {len(metadata)} images")
    print(f"✓ Saved to: {metadata_file}")
    
    return metadata


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect sunset images for grading")
    parser.add_argument("--num-sunsets", type=int, default=300,
                       help="Number of sunset images to collect")
    parser.add_argument("--output-dir", type=str, 
                       default="data/sunset_images_for_grading",
                       help="Output directory")
    parser.add_argument("--existing-dir", type=str, default=None,
                       help="Load existing images from directory")
    parser.add_argument("--webcam-url", type=str, default=None,
                       help="Webcam URL")
    
    args = parser.parse_args()
    
    if args.existing_dir:
        load_existing_sunset_images(args.existing_dir)
    else:
        collect_sunset_images(args.num_sunsets, args.output_dir, args.webcam_url)

