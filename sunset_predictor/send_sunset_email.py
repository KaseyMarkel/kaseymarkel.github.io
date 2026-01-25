"""
Send daily sunset prediction email.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import json

# Email configuration
EMAIL_FROM = "kaseymarkel@gmail.com"  # Update if using different sender
EMAIL_TO = "kaseymarkel@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# You'll need to set up an app password for Gmail:
# https://support.google.com/accounts/answer/185833
# Store it securely (environment variable or config file)
EMAIL_PASSWORD = None  # Set via environment variable EMAIL_PASSWORD

def get_prediction_for_today():
    """Get today's prediction result."""
    today = datetime.now().date()
    prediction_file = Path(f"data/daily_predictions/{today.isoformat()}.json")
    
    if not prediction_file.exists():
        return None
    
    with open(prediction_file, 'r') as f:
        return json.load(f)

def send_sunset_email(prediction_result):
    """Send email with sunset prediction."""
    import os
    password = os.getenv('EMAIL_PASSWORD')
    if not password:
        print("✗ EMAIL_PASSWORD environment variable not set")
        print("  Set up Gmail app password and export EMAIL_PASSWORD='your-app-password'")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"Sunset Prediction for {prediction_result['date']}"
    
    body = f"""
Sunset Prediction for {prediction_result['date']}

Predicted Quality: {prediction_result['predicted_quality']}/10
Sunset Time: {prediction_result['sunset_time']}
Peak Viewing Time: {prediction_result['peak_time']} ({prediction_result['predicted_peak_minutes']:+.1f} minutes from sunset)

Enjoy the sunset!
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, password)
        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent to {EMAIL_TO}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False

def daily_sunset_email():
    """Main function to send daily sunset email."""
    from datetime import datetime, timedelta
    from astral import LocationInfo
    from astral.sun import sun
    from pytz import timezone
    
    BERKELEY_LAT = 37.8715
    BERKELEY_LON = -122.2730
    
    # Check if it's 1 hour before sunset
    today = datetime.now().date()
    location = LocationInfo("Berkeley", "California", "US/Pacific", BERKELEY_LAT, BERKELEY_LON)
    s = sun(location.observer, date=today, tzinfo=location.timezone)
    sunset_time = s["sunset"]
    email_time = sunset_time - timedelta(hours=1)
    
    now = datetime.now(timezone('US/Pacific'))
    
    # Only send if we're within 30 minutes of the email time
    time_diff = abs((now - email_time).total_seconds())
    if time_diff > 30 * 60:  # More than 30 minutes away
        # Not time yet
        return
    
    prediction = get_prediction_for_today()
    
    if not prediction:
        print("✗ No prediction found for today")
        return
    
    send_sunset_email(prediction)

if __name__ == "__main__":
    daily_sunset_email()

