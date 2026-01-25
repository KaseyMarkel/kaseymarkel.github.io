"""
Download actual high-level cloud cover data from Open-Meteo archive API.
Uses hourly data and extracts midday values (3 hours before sunset).
"""

import json
import urllib.request
import urllib.parse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
import time

# Berkeley coordinates
BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730
BERKELEY_TZ = pytz.timezone('America/Los_Angeles')
berkeley = LocationInfo("Berkeley", "USA", "America/Los_Angeles", BERKELEY_LAT, BERKELEY_LON)

def get_sunset_time(date_str):
    """Get sunset time for a date."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    s = sun(berkeley.observer, date=date_obj, tzinfo=BERKELEY_TZ)
    return s['sunset']

def get_midday_time(date_str):
    """Get midday time (3 hours before sunset)."""
    sunset = get_sunset_time(date_str)
    midday = sunset - timedelta(hours=3)
    return midday

def download_high_level_clouds_for_date(date_str):
    """Download high-level cloud cover data for a single date."""
    # Get midday time (3 hours before sunset)
    midday = get_midday_time(date_str)
    
    # Download hourly data for the day
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude': BERKELEY_LAT,
        'longitude': BERKELEY_LON,
        'start_date': date_str,
        'end_date': date_str,
        'hourly': 'cloud_cover_high,cloud_cover_mid,cloud_cover_low',
        'timezone': 'America/Los_Angeles'
    }
    
    try:
        url_with_params = url + '?' + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url_with_params, timeout=15) as response:
            data = json.loads(response.read().decode())
            hourly = data.get('hourly', {})
            
            if hourly and len(hourly.get('time', [])) > 0:
                times = hourly.get('time', [])
                high_clouds = hourly.get('cloud_cover_high', [])
                mid_clouds = hourly.get('cloud_cover_mid', [])
                low_clouds = hourly.get('cloud_cover_low', [])
                
                # Find closest hour to midday
                midday_hour = midday.hour
                closest_idx = None
                min_diff = float('inf')
                
                for i, time_str in enumerate(times):
                    time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    hour_diff = abs(time_obj.hour - midday_hour)
                    if hour_diff < min_diff:
                        min_diff = hour_diff
                        closest_idx = i
                
                # Get value at midday, or average around midday
                if closest_idx is not None:
                    # Average over 3 hours around midday (±1 hour)
                    start_idx = max(0, closest_idx - 1)
                    end_idx = min(len(high_clouds), closest_idx + 2)
                    
                    high_vals = [h for h in high_clouds[start_idx:end_idx] if h is not None]
                    mid_vals = [m for m in mid_clouds[start_idx:end_idx] if m is not None]
                    low_vals = [l for l in low_clouds[start_idx:end_idx] if l is not None]
                    
                    return {
                        'date': date_str,
                        'cloud_cover_high': sum(high_vals) / len(high_vals) if high_vals else None,
                        'cloud_cover_mid': sum(mid_vals) / len(mid_vals) if mid_vals else None,
                        'cloud_cover_low': sum(low_vals) / len(low_vals) if low_vals else None,
                        'midday_hour': midday_hour
                    }
    except Exception as e:
        print(f"  Error for {date_str}: {e}")
    
    return None

def download_all_high_level_clouds():
    """Download high-level cloud data for all dates."""
    # Load dates
    train_file = Path("data/training/train_dataset.json")
    test_file = Path("data/training/test_dataset.json")
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    all_dates = sorted(set([d['date'] for d in train_data + test_data]))
    
    print("=" * 70)
    print("DOWNLOADING HIGH-LEVEL CLOUD DATA")
    print("=" * 70)
    print(f"Source: Open-Meteo Archive API (hourly cloud levels)")
    print(f"Location: Berkeley, CA ({BERKELEY_LAT}, {BERKELEY_LON})")
    print(f"Dates: {len(all_dates)} dates")
    print(f"Extracting: Midday values (3 hours before sunset)")
    print()
    
    cloud_records = []
    failed = []
    
    for i, date_str in enumerate(all_dates, 1):
        print(f"[{i:3d}/{len(all_dates)}] {date_str}...", end=" ", flush=True)
        
        cloud_data = download_high_level_clouds_for_date(date_str)
        
        if cloud_data and cloud_data['cloud_cover_high'] is not None:
            cloud_records.append(cloud_data)
            print(f"✓ ({cloud_data['cloud_cover_high']:.0f}%)")
        else:
            failed.append(date_str)
            print("✗")
        
        time.sleep(0.3)  # Rate limiting
    
    # Save results
    output_path = Path("data/weather/high_level_cloud_data.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if cloud_records:
        df = pd.DataFrame(cloud_records)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved {len(cloud_records)} high-level cloud records to {output_path}")
        
        print(f"\nHigh-level cloud cover summary:")
        print(f"  Range: {df['cloud_cover_high'].min():.0f}% to {df['cloud_cover_high'].max():.0f}%")
        print(f"  Mean: {df['cloud_cover_high'].mean():.1f}%")
        print(f"  Median: {df['cloud_cover_high'].median():.1f}%")
        print(f"  Sweet spot (5-80%): {(df['cloud_cover_high'].between(5, 80)).sum()} days ({100*(df['cloud_cover_high'].between(5, 80)).sum()/len(df):.1f}%)")
        
        if failed:
            print(f"\n⚠ Failed to download {len(failed)} dates:")
            print(f"  {failed[:10]}")
    else:
        print("\n✗ No cloud data downloaded")

if __name__ == "__main__":
    download_all_high_level_clouds()

