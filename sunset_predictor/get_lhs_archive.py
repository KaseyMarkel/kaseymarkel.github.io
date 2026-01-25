"""
Download multiple timelapse videos from Lawrence Hall of Science archive.
The archive page shows historical timelapses - we'll try to access them.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
import re

LHS_BASE_URL = "https://lawrencehallofscience.org/play/view/"


def find_archive_videos():
    """Find links to timelapse archive videos."""
    print("Accessing LHS webcam page to find archive...")
    
    try:
        response = requests.get(LHS_BASE_URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for archive section
        archive_section = soup.find(string=re.compile(r'archive|Archive', re.I))
        
        # Find all video links
        video_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if 'timelapse' in href.lower() or 'video' in href.lower():
                if not href.startswith('http'):
                    href = LHS_BASE_URL.rstrip('/') + '/' + href.lstrip('/')
                video_links.append(href)
        
        # Also check for direct video URLs in page
        video_tags = soup.find_all('video')
        for video in video_tags:
            source = video.find('source')
            if source:
                src = source.get('src', '')
                if src:
                    if not src.startswith('http'):
                        src = "https://www.ocf.berkeley.edu" + src
                    video_links.append(src)
        
        print(f"Found {len(video_links)} potential video URL(s)")
        
        # Print unique URLs
        unique_urls = list(set(video_links))
        for url in unique_urls:
            print(f"  {url}")
        
        return unique_urls
        
    except Exception as e:
        print(f"Error: {e}")
        return []


def download_video(url, output_dir="data/lhs_timelapses"):
    """Download a video file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Determine filename
        filename = url.split('/')[-1]
        if '?' in filename:
            filename = filename.split('?')[0]
        
        if not filename.endswith(('.mp4', '.webm', '.mov')):
            filename = f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        filepath = output_path / filename
        
        # Download
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✓ Saved: {filepath.name} ({filepath.stat().st_size / 1024 / 1024:.1f} MB)")
        return filepath
        
    except Exception as e:
        print(f"\n✗ Error downloading {url}: {e}")
        return None


def generate_daily_urls(start_date, num_days=300):
    """
    Generate potential URLs for daily timelapse videos.
    LHS may have a pattern like: timelapse/YYYYMMDD.mp4
    """
    urls = []
    base_patterns = [
        "https://www.ocf.berkeley.edu/~thelawrence/timelapse/{date}.mp4",
        "https://www.ocf.berkeley.edu/~thelawrence/timelapse/view{date}.mp4",
        "https://www.ocf.berkeley.edu/~thelawrence/timelapse/{date}view.mp4",
    ]
    
    current_date = start_date
    for _ in range(num_days):
        date_str = current_date.strftime("%Y%m%d")
        
        for pattern in base_patterns:
            url = pattern.format(date=date_str)
            urls.append((url, current_date))
        
        current_date -= timedelta(days=1)
    
    return urls


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download LHS timelapse archive")
    parser.add_argument("--find-urls", action="store_true",
                       help="Find video URLs from archive page")
    parser.add_argument("--download-url", type=str, default=None,
                       help="Download specific URL")
    parser.add_argument("--try-daily", action="store_true",
                       help="Try to download daily videos using URL patterns")
    parser.add_argument("--start-date", type=str, default=None,
                       help="Start date for daily downloads (YYYY-MM-DD)")
    parser.add_argument("--num-days", type=int, default=300,
                       help="Number of days to try")
    
    args = parser.parse_args()
    
    if args.find_urls:
        urls = find_archive_videos()
        print(f"\nFound {len(urls)} URL(s)")
        
    elif args.download_url:
        download_video(args.download_url)
        
    elif args.try_daily:
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        else:
            start_date = datetime.now().date() - timedelta(days=1)
        
        print(f"Trying to download {args.num_days} days of timelapses...")
        print(f"Starting from: {start_date}")
        print("This may take a while...\n")
        
        urls_with_dates = generate_daily_urls(start_date, args.num_days)
        
        downloaded = 0
        for url, date in urls_with_dates[:10]:  # Try first 10 as test
            result = download_video(url)
            if result:
                downloaded += 1
                # Rename with date
                date_str = date.strftime("%Y%m%d")
                new_name = result.parent / f"lhs_{date_str}.mp4"
                if result.exists():
                    result.rename(new_name)
        
        print(f"\n✓ Downloaded {downloaded} videos")
        print("If successful, run with --num-days 300 to get more")
        
    else:
        print("LHS Archive Downloader")
        print("=" * 60)
        print("\nOptions:")
        print("  --find-urls          Find video URLs from archive page")
        print("  --download-url URL   Download specific video URL")
        print("  --try-daily          Try downloading daily videos")
        print("\nExample:")
        print("  python3 get_lhs_archive.py --find-urls")
        print("  python3 get_lhs_archive.py --try-daily --num-days 300")

