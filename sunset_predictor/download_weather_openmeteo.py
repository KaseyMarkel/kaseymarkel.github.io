"""
Download historical weather data using Open-Meteo API (free, no API key needed).
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

def download_weather_for_date(date_str):
    """Download weather data for a single date using Open-Meteo."""
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude': BERKELEY_LAT,
        'longitude': BERKELEY_LON,
        'start_date': date_str,
        'end_date': date_str,
        'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,relative_humidity_2m_mean,cloud_cover_mean,pressure_msl_mean',
        'timezone': 'America/Los_Angeles'
    }
    
    try:
        # Build URL with parameters
        url_with_params = url + '?' + urllib.parse.urlencode(params)
        
        # Make request
        with urllib.request.urlopen(url_with_params, timeout=15) as response:
            data = json.loads(response.read().decode())
            daily = data.get('daily', {})
            
            if daily and len(daily.get('time', [])) > 0:
                return {
                    'date': date_str,
                    'temperature_max': daily.get('temperature_2m_max', [None])[0],
                    'temperature_min': daily.get('temperature_2m_min', [None])[0],
                    'temperature_mean': daily.get('temperature_2m_mean', [None])[0],
                    'precipitation': daily.get('precipitation_sum', [None])[0],
                    'wind_speed': daily.get('wind_speed_10m_max', [None])[0],
                    'wind_direction': daily.get('wind_direction_10m_dominant', [None])[0],
                    'humidity': daily.get('relative_humidity_2m_mean', [None])[0],
                    'cloud_cover': daily.get('cloud_cover_mean', [None])[0],
                    'pressure': daily.get('pressure_msl_mean', [None])[0],
                    'visibility': None  # Not available in Open-Meteo
                }
    except Exception as e:
        print(f"  Error for {date_str}: {e}")
    
    return None

def download_all_weather():
    """Download weather data for all dates in the dataset."""
    # Load dates
    train_file = Path("data/training/train_dataset.json")
    test_file = Path("data/training/test_dataset.json")
    
    if not train_file.exists() or not test_file.exists():
        print("⚠ Training data not found. Run prepare_training_data.py first.")
        return
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    all_dates = sorted(set([d['date'] for d in train_data + test_data]))
    
    print("=" * 70)
    print("DOWNLOADING WEATHER DATA")
    print("=" * 70)
    print(f"Source: Open-Meteo Historical Weather API (free)")
    print(f"Location: Berkeley, CA ({BERKELEY_LAT}, {BERKELEY_LON})")
    print(f"Dates: {len(all_dates)} dates from {min(all_dates)} to {max(all_dates)}")
    print()
    
    weather_records = []
    failed = []
    
    for i, date_str in enumerate(all_dates, 1):
        print(f"[{i:3d}/{len(all_dates)}] {date_str}...", end=" ", flush=True)
        
        weather = download_weather_for_date(date_str)
        
        if weather:
            weather_records.append(weather)
            print("✓")
        else:
            failed.append(date_str)
            print("✗")
        
        # Rate limiting - be nice to the API
        time.sleep(0.3)
    
    # Save results
    output_path = Path("data/weather/weather_data.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if weather_records:
        df = pd.DataFrame(weather_records)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved {len(weather_records)} weather records to {output_path}")
        
        # Show summary
        print(f"\nWeather data summary:")
        print(f"  Temperature: {df['temperature_mean'].min():.1f}°C to {df['temperature_mean'].max():.1f}°C")
        print(f"  Humidity: {df['humidity'].min():.0f}% to {df['humidity'].max():.0f}%")
        print(f"  Cloud cover: {df['cloud_cover'].min():.0f}% to {df['cloud_cover'].max():.0f}%")
        print(f"  Precipitation: {df['precipitation'].sum():.1f} mm total")
        
        if failed:
            print(f"\n⚠ Failed to download {len(failed)} dates:")
            print(f"  {failed[:10]}")
            print(f"\n  You may need to fill these manually or try a different source")
    else:
        print("\n✗ No weather data downloaded")
        print("  Check your internet connection and try again")

if __name__ == "__main__":
    download_all_weather()

