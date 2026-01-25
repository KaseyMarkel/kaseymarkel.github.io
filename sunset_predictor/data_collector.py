"""
Data collection script for LBNL webcam images.
Downloads historical webcam images and pairs them with sunset times.
"""

import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
from PIL import Image
from io import BytesIO
import json

# Berkeley coordinates
BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

# Common LBNL webcam URLs (user may need to update this)
# Typical pattern: http://www.lbl.gov/webcam/current.jpg or similar
LBNL_WEBCAM_URL = "http://www.lbl.gov/webcam/current.jpg"
# Alternative: If there's an archive URL pattern, update here
ARCHIVE_URL_PATTERN = None  # e.g., "http://www.lbl.gov/webcam/archive/{date}/{time}.jpg"


def get_sunset_time(date, lat=BERKELEY_LAT, lon=BERKELEY_LON):
    """
    Get sunset time for a given date in Berkeley using sunrise-sunset API.
    
    Args:
        date: datetime object for the date
        lat: latitude (default: Berkeley)
        lon: longitude (default: Berkeley)
    
    Returns:
        datetime object with sunset time
    """
    from astral import LocationInfo
    from astral.sun import sun
    
    # Create location for Berkeley
    location = LocationInfo("Berkeley", "California", "US/Pacific", lat, lon)
    
    # Get sun information for the date
    s = sun(location.observer, date=date.date(), tzinfo=location.timezone)
    
    return s["sunset"]


def download_image(url, timeout=10):
    """
    Download an image from a URL.
    
    Args:
        url: URL of the image
        timeout: Request timeout in seconds
    
    Returns:
        PIL Image object or None if download fails
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


def collect_historical_data(start_date, end_date, output_dir="data/raw_images", 
                           hours_before_sunset=3, webcam_url=LBNL_WEBCAM_URL):
    """
    Collect webcam images from historical dates, focusing on images taken
    approximately 3 hours before sunset.
    
    Args:
        start_date: datetime object for start date
        end_date: datetime object for end date
        output_dir: Directory to save images
        hours_before_sunset: Hours before sunset to capture (default: 3)
        webcam_url: URL pattern for webcam images
    
    Returns:
        List of metadata dictionaries with image paths and sunset times
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    current_date = start_date
    
    print(f"Collecting data from {start_date.date()} to {end_date.date()}")
    print(f"Target: Images {hours_before_sunset} hours before sunset")
    
    while current_date <= end_date:
        try:
            # Get sunset time for this date
            sunset_time = get_sunset_time(current_date)
            
            # Calculate target capture time (3 hours before sunset)
            target_time = sunset_time - timedelta(hours=hours_before_sunset)
            
            # If target time is in the past relative to current_date, skip
            if target_time < current_date:
                current_date += timedelta(days=1)
                continue
            
            # For historical data, we'll try to construct archive URLs
            # If archive URL pattern is available, use it
            if ARCHIVE_URL_PATTERN:
                img_url = ARCHIVE_URL_PATTERN.format(
                    date=target_time.strftime("%Y%m%d"),
                    time=target_time.strftime("%H%M")
                )
            else:
                # If no archive pattern, we can only get current image
                # This is a limitation - user may need to provide historical archive
                print(f"Warning: No archive URL pattern. Can only get current image.")
                print(f"To collect historical data, you need to:")
                print(f"1. Find the LBNL webcam archive URL pattern")
                print(f"2. Update ARCHIVE_URL_PATTERN in this script")
                print(f"3. Or provide a directory of historical images")
                break
            
            # Download image
            print(f"Downloading image for {target_time.strftime('%Y-%m-%d %H:%M')}...")
            img = download_image(img_url)
            
            if img:
                # Save image
                filename = f"img_{target_time.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = output_path / filename
                img.save(filepath, "JPEG")
                
                # Store metadata
                metadata.append({
                    "image_path": str(filepath),
                    "capture_time": target_time.isoformat(),
                    "sunset_time": sunset_time.isoformat(),
                    "hours_before_sunset": hours_before_sunset,
                    "date": current_date.date().isoformat()
                })
                
                print(f"Saved: {filename}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing date {current_date.date()}: {e}")
        
        current_date += timedelta(days=1)
    
    # Save metadata
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nCollected {len(metadata)} images")
    print(f"Metadata saved to {metadata_path}")
    
    return metadata


def load_existing_images(image_dir, metadata_file=None):
    """
    Load existing images from a directory and create metadata.
    Assumes images are named with timestamps or dates.
    
    Args:
        image_dir: Directory containing images
        metadata_file: Optional JSON file with metadata
    
    Returns:
        List of metadata dictionaries
    """
    image_path = Path(image_dir)
    
    if metadata_file and Path(metadata_file).exists():
        with open(metadata_file, "r") as f:
            return json.load(f)
    
    # If no metadata file, try to infer from filenames
    metadata = []
    for img_file in image_path.glob("*.jpg"):
        # Try to extract date/time from filename
        # Common patterns: img_YYYYMMDD_HHMMSS.jpg, YYYYMMDD_HHMMSS.jpg, etc.
        filename = img_file.stem
        try:
            # Try to parse timestamp from filename
            if "img_" in filename:
                timestamp_str = filename.replace("img_", "")
                capture_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            else:
                # Try other patterns
                capture_time = datetime.strptime(filename, "%Y%m%d_%H%M%S")
            
            # Get sunset time for that date
            sunset_time = get_sunset_time(capture_time)
            
            # Calculate hours before sunset
            hours_before = (sunset_time - capture_time).total_seconds() / 3600
            
            metadata.append({
                "image_path": str(img_file),
                "capture_time": capture_time.isoformat(),
                "sunset_time": sunset_time.isoformat(),
                "hours_before_sunset": hours_before,
                "date": capture_time.date().isoformat()
            })
        except Exception as e:
            print(f"Could not parse timestamp from {img_file}: {e}")
            continue
    
    return metadata


if __name__ == "__main__":
    # Example usage
    from datetime import datetime
    
    # Collect data for the last 30 days (if archive is available)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print("LBNL Webcam Data Collector")
    print("=" * 50)
    print("\nNote: This script requires access to LBNL webcam historical archive.")
    print("If you have existing images, use load_existing_images() instead.")
    print("\nTo use:")
    print("1. Find the LBNL webcam archive URL pattern")
    print("2. Update ARCHIVE_URL_PATTERN in this script")
    print("3. Run: python data_collector.py")
    print("\nOr provide a directory of images and use load_existing_images()")
    
    # Uncomment to run collection (requires archive URL):
    # metadata = collect_historical_data(start_date, end_date)

