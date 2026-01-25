"""
Run prediction on daily midday image and prepare email.
"""

import torch
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image
from torchvision import transforms
from train_dual_predictor import DualPredictor
from astral import LocationInfo
from astral.sun import sun
from pytz import timezone

BERKELEY_LAT = 37.8715
BERKELEY_LON = -122.2730

def get_sunset_time(date=None):
    """Get sunset time for today or specified date."""
    if date is None:
        date = datetime.now().date()
    
    location = LocationInfo("Berkeley", "California", "US/Pacific", BERKELEY_LAT, BERKELEY_LON)
    s = sun(location.observer, date=date, tzinfo=location.timezone)
    return s["sunset"]

def predict_sunset(midday_image_path, model_path="models/dual_predictor.pth"):
    """Predict sunset quality and peak time from midday image."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DualPredictor(num_weather_features=0)
    
    if not Path(model_path).exists():
        print(f"✗ Model not found: {model_path}")
        return None, None
    
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=False))
    model.to(device)
    model.eval()
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Load and predict
    try:
        img = Image.open(midday_image_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            pred_quality, pred_peak = model(img_tensor)
        
        return pred_quality.item(), pred_peak.item()
    except Exception as e:
        print(f"✗ Error predicting: {e}")
        return None, None

def predict_today():
    """Predict sunset for today's midday image."""
    today = datetime.now().date()
    midday_file = Path(f"data/daily_midday/{today.isoformat()}.jpg")
    
    if not midday_file.exists():
        print(f"✗ No midday image found for today: {midday_file}")
        return None
    
    print(f"Running prediction on: {midday_file.name}")
    pred_quality, pred_peak = predict_sunset(midday_file)
    
    if pred_quality is None:
        return None
    
    # Get sunset time
    sunset_time = get_sunset_time(today)
    peak_time = sunset_time + timedelta(minutes=pred_peak)
    
    result = {
        "date": today.isoformat(),
        "predicted_quality": round(pred_quality, 1),
        "predicted_peak_minutes": round(pred_peak, 1),
        "sunset_time": sunset_time.strftime("%I:%M %p"),
        "peak_time": peak_time.strftime("%I:%M %p"),
        "midday_image": str(midday_file)
    }
    
    print(f"✓ Prediction complete:")
    print(f"  Quality: {result['predicted_quality']}/10")
    print(f"  Peak time: {result['peak_time']} ({result['predicted_peak_minutes']:+.1f} min from sunset)")
    
    return result

if __name__ == "__main__":
    predict_today()

