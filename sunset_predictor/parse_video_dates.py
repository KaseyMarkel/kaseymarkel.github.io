"""
Parse dates from video filenames/titles and update metadata.
YouTube videos have dates in their titles like "Aug. 16, 2020" or "Nov. 6, 2016"
"""

import re
from pathlib import Path
from datetime import datetime
import json
import csv

def parse_date_from_title(title):
    """Parse date from video title."""
    # Patterns: "Aug. 16, 2020", "Nov. 6, 2016", "April 12, 2012", etc.
    patterns = [
        r'([A-Za-z]+)\.?\s+(\d+),?\s+(\d{4})',  # "Aug. 16, 2020"
        r'([A-Za-z]+)\s+(\d+),?\s+(\d{4})',     # "August 16, 2020"
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # "08/16/2020"
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # "2020/08/16"
    ]
    
    month_names = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
    }
    
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            groups = match.groups()
            
            if len(groups) == 3:
                # Try month name format
                if groups[0].isalpha():
                    month_str = groups[0].lower()
                    month = month_names.get(month_str)
                    if month:
                        day = int(groups[1])
                        year = int(groups[2])
                        try:
                            return datetime(year, month, day).date()
                        except:
                            continue
                # Try numeric format
                elif groups[0].isdigit():
                    if len(groups[2]) == 4:  # MM/DD/YYYY
                        month = int(groups[0])
                        day = int(groups[1])
                        year = int(groups[2])
                    else:  # YYYY/MM/DD
                        year = int(groups[0])
                        month = int(groups[1])
                        day = int(groups[2])
                    try:
                        return datetime(year, month, day).date()
                    except:
                        continue
    
    return None

def update_video_dates():
    """Parse dates from video filenames and update metadata."""
    # Load playlist CSV
    csv_file = Path("lhs_playlist_videos.csv")
    if not csv_file.exists():
        print("Playlist CSV not found. Run download_playlist.py first.")
        return
    
    video_dates = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_id = row['Video ID']
            title = row['Title']
            date = parse_date_from_title(title)
            if date:
                video_dates[video_id] = date
                print(f"{video_id}: {date} - {title[:50]}")
    
    print(f"\nParsed {len(video_dates)} dates from video titles")
    
    # Update video filenames with dates
    videos_dir = Path("data/lhs_timelapses")
    updated = 0
    
    for video_file in videos_dir.glob("*.mp4"):
        # Extract video ID from filename (format: lhs_XXX_VIDEOID.mp4)
        match = re.search(r'_([A-Za-z0-9_-]{11})\.mp4$', video_file.name)
        if match:
            video_id = match.group(1)
            if video_id in video_dates:
                date = video_dates[video_id]
                new_name = f"lhs_{date.strftime('%Y%m%d')}_{video_id}.mp4"
                new_path = videos_dir / new_name
                if not new_path.exists():
                    video_file.rename(new_path)
                    print(f"Renamed: {video_file.name} -> {new_name}")
                    updated += 1
    
    print(f"\n✓ Updated {updated} video filenames with dates")
    return video_dates

if __name__ == "__main__":
    update_video_dates()


