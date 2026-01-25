"""
Download historical weather data for Berkeley, CA for all dates in the dataset.
Uses NOAA API or OpenWeatherMap historical data.
"""

import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import os

# Berkeley, CA coordinates
BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def get_noaa_token():
    """Get NOAA API token from environment or prompt user."""
    token = os.getenv('NOAA_TOKEN')
    if not token:
        print("⚠ NOAA API token not found in environment.")
        print("Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token")
        print("Then set: export NOAA_TOKEN='your_token_here'")
        return None
    return token

def download_noaa_weather(date_str, station_id=None):
    """
    Download weather data from NOAA for a specific date.
    Falls back to OpenWeatherMap if NOAA fails.
    """
    # Try NOAA first (free, but requires token)
    token = get_noaa_token()
    if token:
        try:
            # NOAA CDO API endpoint
            url = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
            headers = {"token": token}
            
            # Use Berkeley station (if we can find it)
            # For now, use daily summaries
            params = {
                "datasetid": "GHCND",  # Daily summaries
                "locationid": "FIPS:06001",  # Alameda County
                "startdate": date_str,
                "enddate": date_str,
                "limit": 1000
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return parse_noaa_data(data['results'], date_str)
        except Exception as e:
            print(f"  NOAA API error for {date_str}: {e}")
    
    # Fallback: Use OpenWeatherMap historical (requires API key)
    return download_openweather_historical(date_str)

def download_openweather_historical(date_str):
    """Download historical weather from OpenWeatherMap (requires API key)."""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print(f"  ⚠ No weather API keys available for {date_str}")
        return None
    
    try:
        # OpenWeatherMap One Call API 3.0 (historical)
        # Note: Free tier has limited historical data
        url = "https://api.openweathermap.org/data/3.0/onecall/day_summary"
        params = {
            "lat": BERKELEY_LAT,
            "lon": BERKELEY_LON,
            "date": date_str,
            "appid": api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return parse_openweather_data(response.json(), date_str)
    except Exception as e:
        print(f"  OpenWeatherMap error for {date_str}: {e}")
    
    return None

def parse_noaa_data(results, date_str):
    """Parse NOAA API response into standardized format."""
    weather = {
        "date": date_str,
        "temperature_max": None,
        "temperature_min": None,
        "temperature_mean": None,
        "humidity": None,
        "cloud_cover": None,
        "precipitation": None,
        "wind_speed": None,
        "pressure": None,
        "visibility": None
    }
    
    for record in results:
        datatype = record.get('datatype')
        value = record.get('value')
        
        if value is None:
            continue
            
        if datatype == 'TMAX':
            weather['temperature_max'] = value / 10.0  # Convert from tenths of C
        elif datatype == 'TMIN':
            weather['temperature_min'] = value / 10.0
        elif datatype == 'TAVG':
            weather['temperature_mean'] = value / 10.0
        elif datatype == 'PRCP':
            weather['precipitation'] = value / 10.0  # mm
        elif datatype == 'AWND':  # Average wind speed
            weather['wind_speed'] = value / 10.0  # m/s
        elif datatype == 'SLP':  # Sea level pressure
            weather['pressure'] = value / 10.0  # hPa
    
    return weather

def parse_openweather_data(data, date_str):
    """Parse OpenWeatherMap response into standardized format."""
    return {
        "date": date_str,
        "temperature_max": data.get('temperature', {}).get('max'),
        "temperature_min": data.get('temperature', {}).get('min'),
        "temperature_mean": data.get('temperature', {}).get('mean'),
        "humidity": data.get('humidity', {}).get('afternoon'),
        "cloud_cover": data.get('cloud_cover', {}).get('afternoon'),
        "precipitation": data.get('precipitation', {}).get('total'),
        "wind_speed": data.get('wind', {}).get('max', {}).get('speed'),
        "pressure": data.get('pressure', {}).get('afternoon'),
        "visibility": data.get('visibility', {}).get('afternoon')
    }

def create_weather_template(dates, output_file="data/weather/weather_template.csv"):
    """Create a CSV template for manual weather data entry."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    template_data = []
    for date in dates:
        template_data.append({
            "date": date,
            "temperature_max": "",
            "temperature_min": "",
            "temperature_mean": "",
            "humidity": "",
            "cloud_cover": "",
            "precipitation": "",
            "wind_speed": "",
            "pressure": "",
            "visibility": ""
        })
    
    df = pd.DataFrame(template_data)
    df.to_csv(output_path, index=False)
    print(f"✓ Created weather template: {output_path}")
    print(f"  Fill in weather data for {len(dates)} dates")
    print(f"  Sources: https://www.wunderground.com/history or https://www.ncei.noaa.gov/")

def download_all_weather_data(dates, output_file="data/weather/weather_data.csv"):
    """Download weather data for all dates."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    weather_data = []
    failed_dates = []
    
    print(f"Downloading weather data for {len(dates)} dates...")
    
    for i, date in enumerate(dates, 1):
        print(f"[{i}/{len(dates)}] {date}...", end=" ")
        weather = download_noaa_weather(date)
        
        if weather:
            weather_data.append(weather)
            print("✓")
        else:
            failed_dates.append(date)
            print("✗")
        
        # Rate limiting
        time.sleep(0.5)
    
    if weather_data:
        df = pd.DataFrame(weather_data)
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved {len(weather_data)} weather records to {output_path}")
    
    if failed_dates:
        print(f"\n⚠ Failed to download {len(failed_dates)} dates:")
        print(f"  {failed_dates[:5]}...")
        print(f"\nCreating template for manual entry...")
        create_weather_template(failed_dates, "data/weather/weather_manual.csv")
    
    return weather_data

if __name__ == "__main__":
    # Load dates from training data
    train_file = Path("data/training/train_dataset.json")
    test_file = Path("data/training/test_dataset.json")
    
    if not train_file.exists() or not test_file.exists():
        print("⚠ Training data not found. Run prepare_training_data.py first.")
        exit(1)
    
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    all_dates = sorted(set([d["date"] for d in train_data + test_data]))
    print(f"Found {len(all_dates)} unique dates")
    print(f"Date range: {min(all_dates)} to {max(all_dates)}")
    
    # Check if weather data already exists
    weather_file = Path("data/weather/weather_data.csv")
    if weather_file.exists():
        existing = pd.read_csv(weather_file)
        existing_dates = set(existing['date'].astype(str))
        missing_dates = [d for d in all_dates if d not in existing_dates]
        
        if missing_dates:
            print(f"\nFound existing weather data for {len(existing_dates)} dates")
            print(f"Need to download {len(missing_dates)} more dates")
            download_all_weather_data(missing_dates)
        else:
            print(f"\n✓ Weather data already exists for all {len(all_dates)} dates")
    else:
        download_all_weather_data(all_dates)
