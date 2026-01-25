"""
Download midday image from LHS livestream every day at 3pm.
Saves to data/daily_midday/YYYY-MM-DD.jpg
"""

import requests
from pathlib import Path
from datetime import datetime
import time

# LHS livestream URL (update if needed)
LHS_LIVESTREAM_URL = "https://lawrencehallofscience.org/play/view/"
# Alternative: might need to find the actual image URL
# Common pattern: https://lawrencehallofscience.org/webcam/latest.jpg or similar

def download_midday_image(output_dir="data/daily_midday"):
    """Download current image from livestream."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().date()
    filename = f"{today.isoformat()}.jpg"
    filepath = output_path / filename
    
    # Try multiple possible URLs
    urls_to_try = [
        "https://lawrencehallofscience.org/webcam/latest.jpg",
        "https://lawrencehallofscience.org/webcam/current.jpg",
        "https://lawrencehallofscience.org/webcam/image.jpg",
        # Add more if we find the actual URL
    ]
    
    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:  # Valid image
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"✓ Downloaded midday image: {filename}")
                return str(filepath)
        except Exception as e:
            print(f"  Failed {url}: {e}")
            continue
    
    print(f"✗ Could not download image from livestream")
    print(f"  Please check the livestream URL and update download_daily_midday.py")
    return None

if __name__ == "__main__":
    download_midday_image()

