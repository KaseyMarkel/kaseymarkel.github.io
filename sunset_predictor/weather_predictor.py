"""
Use historical weather data to predict sunset quality.
This is a great alternative - we can use weather features as predictors
and only need ~100 manually graded sunsets for training.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import requests
import json

# NOAA weather stations near Berkeley
# Berkeley has station ID: USW00023234 (Berkeley, CA)
# Or we can use Oakland: USW00023230

def download_noaa_weather(start_date, end_date, station_id="USW00023234"):
    """
    Download historical weather data from NOAA.
    
    Station IDs:
    - USW00023234: Berkeley (if available)
    - USW00023230: Oakland Airport (reliable)
    - USW00023237: San Francisco Airport
    """
    print(f"Downloading weather data from {start_date} to {end_date}")
    print(f"Station: {station_id}")
    
    # NOAA API endpoint
    # Note: Free tier requires manual download from their website
    # Alternative: Use wunderground historical data or other sources
    
    # For now, return structure for manual data entry
    return {
        "start_date": start_date,
        "end_date": end_date,
        "station_id": station_id,
        "features": [
            "temperature_max",
            "temperature_min", 
            "humidity",
            "cloud_cover",
            "precipitation",
            "wind_speed",
            "visibility",
            "pressure"
        ]
    }

def get_weather_features_for_date(date, weather_data):
    """Extract weather features for a specific date."""
    # This would parse weather data for the date
    # For now, return placeholder structure
    return {
        "date": date,
        "temp_max": None,
        "temp_min": None,
        "humidity": None,
        "cloud_cover": None,
        "precipitation": None,
        "wind_speed": None,
        "visibility": None,
        "pressure": None
    }

def create_weather_dataset(sunset_scores_file, weather_data_file=None):
    """
    Create dataset with weather features and sunset quality scores.
    
    Args:
        sunset_scores_file: JSON with dates and quality scores
        weather_data_file: CSV/JSON with weather data (optional, can download)
    """
    # Load sunset scores
    with open(sunset_scores_file, "r") as f:
        sunset_data = json.load(f)
    
    # Filter to graded sunsets
    graded = [item for item in sunset_data if item.get("graded") and item.get("quality_score")]
    
    print(f"Found {len(graded)} graded sunsets")
    
    # Create feature matrix
    features = []
    scores = []
    dates = []
    
    for item in graded:
        date = datetime.fromisoformat(item["date"]).date()
        score = item["quality_score"]
        
        # Get weather features for this date
        # TODO: Load from weather data file or API
        weather_features = get_weather_features_for_date(date, None)
        
        features.append([
            weather_features.get("temp_max", 0),
            weather_features.get("temp_min", 0),
            weather_features.get("humidity", 0),
            weather_features.get("cloud_cover", 0),
            weather_features.get("precipitation", 0),
            weather_features.get("wind_speed", 0),
            weather_features.get("visibility", 0),
            weather_features.get("pressure", 0),
        ])
        scores.append(score)
        dates.append(date)
    
    return pd.DataFrame({
        "date": dates,
        "quality_score": scores,
        **{f"feature_{i}": [f[i] for f in features] for i in range(len(features[0]))}
    })

if __name__ == "__main__":
    print("Weather-Based Sunset Quality Predictor")
    print("=" * 60)
    print("\nThis approach uses historical weather data as features")
    print("to predict sunset quality, requiring only ~100 graded sunsets.")
    print("\nNext steps:")
    print("1. Download historical weather data for Berkeley area")
    print("2. Grade ~100 sunsets from the videos we have")
    print("3. Train model: weather features -> sunset quality")
    print("4. Use midday weather forecasts to predict sunset quality")


