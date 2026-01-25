# Daily Sunset Automation Setup

This system automatically:
1. Downloads midday image from LHS livestream at 3pm daily
2. Runs prediction on the image
3. Sends email 1 hour before sunset with predicted quality and peak time

## Setup Steps

### 1. Find the Livestream Image URL

The script needs the actual image URL from the LHS livestream. You may need to:
- Check the LHS website for the webcam image URL
- Look for URLs like `https://lawrencehallofscience.org/webcam/latest.jpg`
- Update `download_daily_midday.py` with the correct URL

### 2. Set Up Gmail App Password

For email sending, you need a Gmail app password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "Mail"
3. Set it as an environment variable:
   ```bash
   export EMAIL_PASSWORD='your-app-password-here'
   ```
4. Add to your `~/.zshrc` or `~/.bashrc` to make it permanent

### 3. Install Cron Jobs

Run the setup script:
```bash
cd /Users/kasey/personal_website/sunset_predictor
chmod +x setup_cron_jobs.sh
./setup_cron_jobs.sh --install
```

Or manually add to crontab:
```bash
crontab -e
```

Add these lines:
```
0 15 * * * cd /Users/kasey/personal_website/sunset_predictor && python3 daily_sunset_automation.py >> logs/cron.log 2>&1
0 * * * * cd /Users/kasey/personal_website/sunset_predictor && python3 send_sunset_email.py >> logs/cron.log 2>&1
```

### 4. Test Manually

Test the system:
```bash
# Download midday image
python3 download_daily_midday.py

# Run prediction
python3 predict_daily_sunset.py

# Send email (if within 1 hour of sunset)
python3 send_sunset_email.py

# Or run everything at once
python3 daily_sunset_automation.py
```

### 5. Check Logs

Monitor the automation:
```bash
tail -f logs/cron.log
```

## Files Created

- `data/daily_midday/YYYY-MM-DD.jpg` - Daily midday images
- `data/daily_predictions/YYYY-MM-DD.json` - Daily predictions
- `logs/cron.log` - Automation logs

## Troubleshooting

- **No image downloaded**: Check the livestream URL in `download_daily_midday.py`
- **Email not sending**: Verify `EMAIL_PASSWORD` environment variable is set
- **Prediction fails**: Make sure model exists at `models/dual_predictor.pth`

