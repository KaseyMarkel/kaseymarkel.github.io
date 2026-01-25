"""
Download high-level cloud cover data for Berkeley.
Open-Meteo provides cloud cover at different levels.
"""

import json
import urllib.request
import urllib.parse
import pandas as pd
from pathlib import Path
import time

# Berkeley coordinates
BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def download_high_cloud_for_date(date_str):
    """Download high-level cloud cover data for a single date."""
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude': BERKELEY_LAT,
        'longitude': BERKELEY_LON,
        'start_date': date_str,
        'end_date': date_str,
        'daily': 'cloud_cover_high,cloud_cover_mid,cloud_cover_low,cloud_cover_mean',
        'timezone': 'America/Los_Angeles'
    }
    
    try:
        url_with_params = url + '?' + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(url_with_params, timeout=15) as response:
            data = json.loads(response.read().decode())
            daily = data.get('daily', {})
            
            if daily and len(daily.get('time', [])) > 0:
                return {
                    'date': date_str,
                    'cloud_cover_high': daily.get('cloud_cover_high', [None])[0],
                    'cloud_cover_mid': daily.get('cloud_cover_mid', [None])[0],
                    'cloud_cover_low': daily.get('cloud_cover_low', [None])[0],
                    'cloud_cover_mean': daily.get('cloud_cover_mean', [None])[0]
                }
    except Exception as e:
        print(f"  Error for {date_str}: {e}")
    
    return None

def download_all_high_cloud_data():
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
    print(f"Dates: {len(all_dates)} dates")
    print()
    
    cloud_records = []
    failed = []
    
    for i, date_str in enumerate(all_dates, 1):
        print(f"[{i:3d}/{len(all_dates)}] {date_str}...", end=" ", flush=True)
        
        cloud_data = download_high_cloud_for_date(date_str)
        
        if cloud_data:
            cloud_records.append(cloud_data)
            print("✓")
        else:
            failed.append(date_str)
            print("✗")
        
        time.sleep(0.3)
    
    # Save results
    output_path = Path("data/weather/high_cloud_data.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if cloud_records:
        df = pd.DataFrame(cloud_records)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved {len(cloud_records)} cloud records to {output_path}")
        
        print(f"\nHigh-level cloud cover summary:")
        print(f"  Range: {df['cloud_cover_high'].min():.0f}% to {df['cloud_cover_high'].max():.0f}%")
        print(f"  Mean: {df['cloud_cover_high'].mean():.1f}%")
        print(f"  Sweet spot (5-80%): {(df['cloud_cover_high'].between(5, 80)).sum()} days")
        
        if failed:
            print(f"\n⚠ Failed to download {len(failed)} dates")
    else:
        print("\n✗ No cloud data downloaded")

if __name__ == "__main__":
    download_all_high_cloud_data()

