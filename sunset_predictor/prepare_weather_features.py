"""
Prepare weather features for training.
Loads weather data and combines with existing dataset.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

def load_weather_data(weather_file="data/weather/weather_data.csv"):
    """Load weather data from CSV."""
    weather_path = Path(weather_file)
    
    if not weather_path.exists():
        print(f"⚠ Weather data file not found: {weather_path}")
        print("  Options:")
        print("    1. Fill in data/weather/weather_template.csv")
        print("    2. Or download via API (requires API keys)")
        return None
    
    df = pd.read_csv(weather_path)
    
    # Check for missing values (excluding date column)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    missing = df[numeric_cols].isnull().sum()
    if missing.sum() > 0:
        print(f"⚠ Missing weather data:")
        print(missing[missing > 0])
        print("\n  Filling missing values with median...")
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    # Convert date to string for matching
    df['date'] = df['date'].astype(str)
    
    print(f"✓ Loaded weather data for {len(df)} dates")
    return df

def extract_weather_features(weather_df):
    """Extract and normalize weather features."""
    feature_cols = [
        'temperature_max', 'temperature_min', 'temperature_mean',
        'humidity', 'cloud_cover', 'precipitation',
        'wind_speed', 'pressure', 'visibility'
    ]
    
    # Check which columns exist and have data
    available_cols = []
    for col in feature_cols:
        if col in weather_df.columns:
            # Only include if not all NaN
            if weather_df[col].notna().sum() > 0:
                available_cols.append(col)
            else:
                print(f"  ⚠ Excluding {col} (all NaN)")
    
    if len(available_cols) == 0:
        print("⚠ No weather features found in data")
        return None, None
    
    # Extract features and fill any remaining NaN with 0
    features = weather_df[available_cols].fillna(0).values
    
    # Normalize
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    
    print(f"✓ Extracted {len(available_cols)} weather features")
    print(f"  Features: {available_cols}")
    
    return features_normalized, scaler

def combine_with_dataset(train_file="data/training/train_dataset.json",
                        test_file="data/training/test_dataset.json",
                        weather_file="data/weather/weather_data.csv"):
    """Combine weather features with existing dataset."""
    
    # Load datasets
    with open(train_file, "r") as f:
        train_data = json.load(f)
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    # Load weather data
    weather_df = load_weather_data(weather_file)
    if weather_df is None:
        return None, None
    
    # Extract features
    weather_features, scaler = extract_weather_features(weather_df)
    if weather_features is None:
        return None, None
    
    # Create date to feature mapping
    weather_dict = {}
    for idx, row in weather_df.iterrows():
        weather_dict[str(row['date'])] = weather_features[idx]
    
    # Combine with datasets
    train_with_weather = []
    test_with_weather = []
    
    missing_dates = []
    
    for sample in train_data:
        date = sample['date']
        if date in weather_dict:
            sample['weather_features'] = weather_dict[date].tolist()
            train_with_weather.append(sample)
        else:
            missing_dates.append(date)
    
    for sample in test_data:
        date = sample['date']
        if date in weather_dict:
            sample['weather_features'] = weather_dict[date].tolist()
            test_with_weather.append(sample)
        else:
            missing_dates.append(date)
    
    if missing_dates:
        print(f"\n⚠ Missing weather data for {len(missing_dates)} dates:")
        print(f"  {missing_dates[:5]}...")
        print(f"  These samples will be excluded")
    
    print(f"\n✓ Combined datasets:")
    print(f"  Train: {len(train_with_weather)} samples (was {len(train_data)})")
    print(f"  Test: {len(test_with_weather)} samples (was {len(test_data)})")
    
    # Save combined datasets
    output_dir = Path("data/training")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "train_dataset_weather.json", "w") as f:
        json.dump(train_with_weather, f, indent=2)
    
    with open(output_dir / "test_dataset_weather.json", "w") as f:
        json.dump(test_with_weather, f, indent=2)
    
    # Save scaler for later use
    import pickle
    with open(output_dir / "weather_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    print(f"\n✓ Saved combined datasets:")
    print(f"  {output_dir / 'train_dataset_weather.json'}")
    print(f"  {output_dir / 'test_dataset_weather.json'}")
    print(f"  {output_dir / 'weather_scaler.pkl'}")
    
    return train_with_weather, test_with_weather

if __name__ == "__main__":
    print("=" * 70)
    print("PREPARING WEATHER FEATURES")
    print("=" * 70)
    
    train_data, test_data = combine_with_dataset()
    
    if train_data is None:
        print("\n⚠ Could not combine weather data. Check weather_data.csv exists.")
    else:
        print("\n" + "=" * 70)
        print("✓ WEATHER FEATURES PREPARED")
        print("=" * 70)
        print("\nNext: Train weather-based models with:")
        print("  python3 train_weather_predictor.py")

