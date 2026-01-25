"""
Evaluate weather-based models and compare with image-only model.
"""

import json
import torch
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr
from train_weather_predictor import WeatherOnlyPredictor, WeatherOnlyDataset
from torch.utils.data import DataLoader

def evaluate_weather_only_model(model_path="models/weather_only_predictor.pth",
                                test_file="data/training/test_dataset_weather.json"):
    """Evaluate weather-only model."""
    
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    test_weather = np.array([d['weather_features'] for d in test_data])
    test_quality = np.array([d['quality_score'] for d in test_data])
    test_peak = np.array([d['peak_time_minutes'] for d in test_data])
    test_duration = np.array([d.get('duration_above_5_minutes', 0) for d in test_data])
    
    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_features = test_weather.shape[1]
    model = WeatherOnlyPredictor(num_weather_features=num_features)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
    model.to(device)
    model.eval()
    
    # Evaluate
    predictions_quality = []
    predictions_peak = []
    predictions_duration = []
    
    with torch.no_grad():
        for weather, quality, peak_time, duration in zip(test_weather, test_quality, test_peak, test_duration):
            weather_tensor = torch.tensor(weather, dtype=torch.float32).unsqueeze(0).to(device)
            pred_quality, pred_peak, pred_duration = model(weather_tensor)
            
            predictions_quality.append(pred_quality.item())
            predictions_peak.append(pred_peak.item())
            predictions_duration.append(pred_duration.item())
    
    # Calculate metrics
    quality_mae = np.mean(np.abs(np.array(predictions_quality) - test_quality))
    quality_rmse = np.sqrt(np.mean((np.array(predictions_quality) - test_quality)**2))
    quality_corr, quality_p = pearsonr(test_quality, predictions_quality)
    
    peak_mae = np.mean(np.abs(np.array(predictions_peak) - test_peak))
    peak_rmse = np.sqrt(np.mean((np.array(predictions_peak) - test_peak)**2))
    peak_corr, peak_p = pearsonr(test_peak, predictions_peak)
    
    duration_mae = np.mean(np.abs(np.array(predictions_duration) - test_duration))
    duration_rmse = np.sqrt(np.mean((np.array(predictions_duration) - test_duration)**2))
    duration_corr, duration_p = pearsonr(test_duration, predictions_duration)
    
    results = {
        "model": "weather_only",
        "quality": {
            "mae": float(quality_mae),
            "rmse": float(quality_rmse),
            "correlation": float(quality_corr),
            "p_value": float(quality_p)
        },
        "peak_time": {
            "mae": float(peak_mae),
            "rmse": float(peak_rmse),
            "correlation": float(peak_corr),
            "p_value": float(peak_p)
        },
        "duration": {
            "mae": float(duration_mae),
            "rmse": float(duration_rmse),
            "correlation": float(duration_corr),
            "p_value": float(duration_p)
        },
        "predictions": [
            {
                "date": test_data[i]["date"],
                "true_quality": float(test_quality[i]),
                "pred_quality": float(predictions_quality[i]),
                "true_peak_time": float(test_peak[i]),
                "pred_peak_time": float(predictions_peak[i]),
                "true_duration_above_5": float(test_duration[i]),
                "pred_duration_above_5": float(predictions_duration[i])
            }
            for i in range(len(test_data))
        ]
    }
    
    return results

def compare_models():
    """Compare image-only, weather-only, and combined models."""
    
    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    
    # Load image-only results
    img_results_file = Path("data/training/evaluation_results.json")
    if img_results_file.exists():
        with open(img_results_file, "r") as f:
            img_results = json.load(f)
        print("\n✓ Image-only model results loaded")
    else:
        print("\n⚠ Image-only results not found")
        img_results = None
    
    # Evaluate weather-only model
    weather_model_path = Path("models/weather_only_predictor.pth")
    if weather_model_path.exists():
        weather_results = evaluate_weather_only_model()
        print("\n✓ Weather-only model evaluated")
    else:
        print("\n⚠ Weather-only model not found")
        weather_results = None
    
    # Save comparison
    comparison = {
        "image_only": img_results,
        "weather_only": weather_results
    }
    
    output_file = Path("data/training/model_comparison.json")
    with open(output_file, "w") as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n✓ Comparison saved: {output_file}")
    
    # Print summary
    if weather_results:
        print("\n" + "=" * 70)
        print("WEATHER-ONLY MODEL PERFORMANCE")
        print("=" * 70)
        print(f"\nQuality Prediction:")
        print(f"  MAE: {weather_results['quality']['mae']:.2f}")
        print(f"  RMSE: {weather_results['quality']['rmse']:.2f}")
        print(f"  Correlation: r={weather_results['quality']['correlation']:.3f} (p={weather_results['quality']['p_value']:.3f})")
        
        print(f"\nPeak Time Prediction:")
        print(f"  MAE: {weather_results['peak_time']['mae']:.2f} minutes")
        print(f"  RMSE: {weather_results['peak_time']['rmse']:.2f} minutes")
        print(f"  Correlation: r={weather_results['peak_time']['correlation']:.3f} (p={weather_results['peak_time']['p_value']:.3f})")
        
        print(f"\nDuration Above 5 Prediction:")
        print(f"  MAE: {weather_results['duration']['mae']:.2f} minutes")
        print(f"  RMSE: {weather_results['duration']['rmse']:.2f} minutes")
        print(f"  Correlation: r={weather_results['duration']['correlation']:.3f} (p={weather_results['duration']['p_value']:.3f})")
    
    return comparison

if __name__ == "__main__":
    compare_models()

