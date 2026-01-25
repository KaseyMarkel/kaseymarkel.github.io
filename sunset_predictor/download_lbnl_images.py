"""
Download real images from LBNL webcam.
"""

import requests
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
from io import BytesIO
import json
import time
from data_collector import get_sunset_time, BERKELEY_LAT, BERKELEY_LON

# Common LBNL webcam URLs to try
LBNL_WEBCAM_URLS = [
    "http://www.lbl.gov/webcam/current.jpg",
    "https://www.lbl.gov/webcam/current.jpg",
    "http://webcam.lbl.gov/current.jpg",
    "https://webcam.lbl.gov/current.jpg",
]


def find_working_webcam_url():
    """Try to find a working LBNL webcam URL."""
    print("Searching for working LBNL webcam URL...")
    for url in LBNL_WEBCAM_URLS:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                print(f"✓ Found working webcam: {url}")
                print(f"  Image size: {img.size}")
                return url
        except Exception as e:
            print(f"✗ {url}: {e}")
            continue
    return None


def download_current_image(webcam_url, output_path):
    """Download current image from webcam."""
    try:
        response = requests.get(webcam_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.save(output_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False


def collect_images_over_time(days=30, hours_before_sunset=3, 
                             webcam_url=None, output_dir="data/lbnl_images",
                             check_interval_hours=1):
    """
    Collect images over time by checking the webcam periodically.
    Focus on times ~3 hours before sunset.
    
    Args:
        days: Number of days to collect
        hours_before_sunset: Target hours before sunset
        webcam_url: Webcam URL (if None, will try to find one)
        output_dir: Output directory
        check_interval_hours: How often to check (in hours)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find webcam URL
    if webcam_url is None:
        webcam_url = find_working_webcam_url()
        if webcam_url is None:
            print("\n❌ Could not find working LBNL webcam URL.")
            print("\nPlease provide the webcam URL manually:")
            print("  python3 download_lbnl_images.py --webcam-url <URL>")
            return []
    
    print(f"\nCollecting images from {webcam_url}")
    print(f"Target: Images {hours_before_sunset} hours before sunset")
    print(f"Will check every {check_interval_hours} hours for {days} days\n")
    
    metadata = []
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days)
    
    # Calculate check times
    current_time = start_date
    check_times = []
    
    while current_time < end_date:
        # Get sunset for this date
        sunset_time = get_sunset_time(current_time)
        target_time = sunset_time - timedelta(hours=hours_before_sunset)
        
        # Add check times around target
        check_times.append(target_time)
        check_times.append(target_time - timedelta(hours=0.5))
        check_times.append(target_time + timedelta(hours=0.5))
        
        current_time += timedelta(days=1)
    
    # Sort and remove duplicates
    check_times = sorted(set(check_times))
    check_times = [t for t in check_times if t > datetime.now()]
    
    print(f"Will attempt to collect {len(check_times)} images")
    print("(Note: This requires running over multiple days)")
    print("\nFor immediate collection, you can:")
    print("1. Download current image: python3 download_lbnl_images.py --current")
    print("2. Provide existing images in a directory")
    print("3. Manually download images and use load_existing_images()\n")
    
    return metadata


def download_current():
    """Download the current webcam image for testing."""
    webcam_url = find_working_webcam_url()
    if webcam_url is None:
        print("Could not find working webcam URL")
        return
    
    output_path = Path("data/lbnl_images")
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lbnl_{timestamp}.jpg"
    filepath = output_path / filename
    
    print(f"Downloading current image to {filepath}...")
    if download_current_image(webcam_url, filepath):
        print(f"✓ Saved: {filename}")
        
        # Show image info
        img = Image.open(filepath)
        print(f"  Size: {img.size}")
        print(f"  Mode: {img.mode}")
        
        # Try to display (if possible)
        try:
            img.show()
        except:
            print("  (Could not display image)")
    else:
        print("✗ Failed to download")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LBNL webcam images")
    parser.add_argument("--current", action="store_true",
                       help="Download current image for testing")
    parser.add_argument("--webcam-url", type=str, default=None,
                       help="Webcam URL (if not provided, will search)")
    parser.add_argument("--days", type=int, default=30,
                       help="Days to collect")
    parser.add_argument("--output-dir", type=str, default="data/lbnl_images",
                       help="Output directory")
    
    args = parser.parse_args()
    
    if args.current:
        download_current()
    else:
        collect_images_over_time(
            days=args.days,
            webcam_url=args.webcam_url,
            output_dir=args.output_dir
        )

