"""
Complete daily automation: download midday, predict, save, and email.
Run this script to do everything.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import subprocess
import sys

def run_daily_automation():
    """Run the complete daily automation pipeline."""
    today = datetime.now().date()
    print(f"\n{'='*70}")
    print(f"DAILY SUNSET AUTOMATION - {today}")
    print(f"{'='*70}\n")
    
    # Step 1: Download midday image
    print("Step 1: Downloading midday image...")
    from download_daily_midday import download_midday_image
    midday_path = download_midday_image()
    
    if not midday_path:
        print("✗ Failed to download midday image. Exiting.")
        return False
    
    # Step 2: Run prediction
    print("\nStep 2: Running prediction...")
    from predict_daily_sunset import predict_today
    prediction = predict_today()
    
    if not prediction:
        print("✗ Failed to generate prediction. Exiting.")
        return False
    
    # Step 3: Save prediction
    print("\nStep 3: Saving prediction...")
    predictions_dir = Path("data/daily_predictions")
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    prediction_file = predictions_dir / f"{today.isoformat()}.json"
    with open(prediction_file, 'w') as f:
        json.dump(prediction, f, indent=2)
    print(f"✓ Saved: {prediction_file}")
    
    # Step 4: Send email (if running at right time)
    print("\nStep 4: Checking if email should be sent...")
    from astral import LocationInfo
    from astral.sun import sun
    from pytz import timezone
    
    BERKELEY_LAT = 37.8715
    BERKELEY_LON = -122.2730
    
    location = LocationInfo("Berkeley", "California", "US/Pacific", BERKELEY_LAT, BERKELEY_LON)
    s = sun(location.observer, date=today, tzinfo=location.timezone)
    sunset_time = s["sunset"]
    email_time = sunset_time - timedelta(hours=1)
    
    now = datetime.now(timezone('US/Pacific'))
    
    # Only send email if we're within 30 minutes of the email time
    time_diff = abs((now - email_time).total_seconds())
    if time_diff < 30 * 60:  # 30 minutes
        print(f"  Sending email (within 30 min of {email_time.strftime('%I:%M %p')})...")
        from send_sunset_email import send_sunset_email
        send_sunset_email(prediction)
    else:
        print(f"  Email will be sent at {email_time.strftime('%I:%M %p')} (1h before sunset)")
        print(f"  Current time: {now.strftime('%I:%M %p')}")
    
    print(f"\n{'='*70}")
    print(f"✓ Daily automation complete!")
    print(f"{'='*70}\n")
    
    return True

if __name__ == "__main__":
    success = run_daily_automation()
    sys.exit(0 if success else 1)

