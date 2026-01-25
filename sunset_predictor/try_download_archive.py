"""
Try to download multiple timelapse videos from LHS.
Tests various URL patterns to find accessible videos.
"""

import requests
from datetime import datetime, timedelta
from pathlib import Path
import time

LHS_BASE = "https://www.ocf.berkeley.edu/~thelawrence/timelapse/"

def test_url_pattern(date_str):
    """Test if a URL pattern works for a given date."""
    patterns = [
        f"{LHS_BASE}{date_str}view.1080p.mp4",
        f"{LHS_BASE}view{date_str}.1080p.mp4",
        f"{LHS_BASE}{date_str}.1080p.mp4",
        f"{LHS_BASE}{date_str}view.mp4",
        f"{LHS_BASE}yesterdayview.1080p.mp4",  # This one we know works
    ]
    
    for url in patterns:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return url
        except:
            continue
    return None

def download_if_exists(url, output_dir, date_str):
    """Download video if URL exists."""
    try:
        response = requests.get(url, timeout=60, stream=True)
        if response.status_code == 200:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            filename = f"lhs_{date_str}.mp4"
            filepath = output_path / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if filepath.exists() and filepath.stat().st_size > 1000:
                return filepath
    except:
        pass
    return None

# Try to find working pattern
print("Testing URL patterns...")
test_date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
working_url = test_url_pattern(test_date)

if working_url:
    print(f"Found working pattern: {working_url}")
else:
    print("No working pattern found for historical dates.")
    print("\nThe LHS archive may require:")
    print("1. Manual download from their archive page")
    print("2. Different URL structure")
    print("3. Authentication/API access")
    print("\nFor now, we can:")
    print("- Extract from yesterday's video (already done)")
    print("- Download 'yesterday' daily for 300 days")
    print("- Or manually download from archive page")

