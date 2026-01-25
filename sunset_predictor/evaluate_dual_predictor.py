"""
Evaluate the dual predictor model on test set.
Shows predictions for quality and peak time.
"""

import json
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from torchvision import transforms
from train_dual_predictor import DualPredictor, SunsetDataset

def evaluate_model(model_path="models/dual_predictor.pth",
                   test_file="data/training/test_dataset.json"):
    """Evaluate model on test set."""
    
    # Load test data
    with open(test_file, "r") as f:
        test_data = json.load(f)
    
    test_images = [Path(d["midday_image"]) for d in test_data]
    test_quality = [d["quality_score"] for d in test_data]
    test_peak = [d["peak_time_minutes"] for d in test_data]
    test_duration = [d.get("duration_above_5_minutes", 0.0) for d in test_data]
    
    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DualPredictor(num_weather_features=0)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
    model.to(device)
    model.eval()
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Evaluate
    predictions_quality = []
    predictions_peak = []
    predictions_duration = []
    
    with torch.no_grad():
        for img_path, true_quality, true_peak, true_duration in zip(test_images, test_quality, test_peak, test_duration):
            img = Image.open(img_path).convert('RGB')
            img_tensor = transform(img).unsqueeze(0).to(device)
            
            pred_quality, pred_peak, pred_duration = model(img_tensor)
            
            predictions_quality.append(pred_quality.item())
            predictions_peak.append(pred_peak.item())
            predictions_duration.append(pred_duration.item())
    
    # Calculate metrics
    quality_mae = np.mean(np.abs(np.array(predictions_quality) - np.array(test_quality)))
    quality_rmse = np.sqrt(np.mean((np.array(predictions_quality) - np.array(test_quality))**2))
    
    peak_mae = np.mean(np.abs(np.array(predictions_peak) - np.array(test_peak)))
    peak_rmse = np.sqrt(np.mean((np.array(predictions_peak) - np.array(test_peak))**2))
    
    duration_mae = np.mean(np.abs(np.array(predictions_duration) - np.array(test_duration)))
    duration_rmse = np.sqrt(np.mean((np.array(predictions_duration) - np.array(test_duration))**2))
    
    print("=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)
    print(f"\nTest set: {len(test_data)} samples")
    print(f"\nQuality Prediction:")
    print(f"  MAE: {quality_mae:.2f}")
    print(f"  RMSE: {quality_rmse:.2f}")
    print(f"  True range: {min(test_quality):.1f} - {max(test_quality):.1f}")
    print(f"  Pred range: {min(predictions_quality):.1f} - {max(predictions_quality):.1f}")
    
    print(f"\nPeak Time Prediction:")
    print(f"  MAE: {peak_mae:.2f} minutes")
    print(f"  RMSE: {peak_rmse:.2f} minutes")
    print(f"  True range: {min(test_peak):.1f} - {max(test_peak):.1f} minutes")
    print(f"  Pred range: {min(predictions_peak):.1f} - {max(predictions_peak):.1f} minutes")
    
    print(f"\nDuration Above Quality 5 Prediction:")
    print(f"  MAE: {duration_mae:.2f} minutes")
    print(f"  RMSE: {duration_rmse:.2f} minutes")
    print(f"  True range: {min(test_duration):.1f} - {max(test_duration):.1f} minutes")
    print(f"  Pred range: {min(predictions_duration):.1f} - {max(predictions_duration):.1f} minutes")
    
    # Save predictions
    results = []
    for i, (img_path, true_q, true_p, true_d, pred_q, pred_p, pred_d) in enumerate(zip(
        test_images, test_quality, test_peak, test_duration, 
        predictions_quality, predictions_peak, predictions_duration
    )):
        results.append({
            "date": test_data[i]["date"],
            "true_quality": float(true_q),
            "pred_quality": float(pred_q),
            "true_peak_time": float(true_p),
            "pred_peak_time": float(pred_p),
            "true_duration_above_5": float(true_d),
            "pred_duration_above_5": float(pred_d),
            "quality_error": float(abs(pred_q - true_q)),
            "peak_error": float(abs(pred_p - true_p)),
            "duration_error": float(abs(pred_d - true_d))
        })
    
    results_file = Path("data/training/evaluation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved: {results_file}")
    
    return results

if __name__ == "__main__":
    evaluate_model()


