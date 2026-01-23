# 🌅 Sunset Quality Prediction Bot

A Telegram bot that predicts the aesthetic quality of sunsets based on weather conditions and learns from your feedback.

## Features

- **Daily Predictions**: Automatically sends sunset quality predictions 30 minutes before sunset
- **Weather-Based ML**: Uses cloud cover, humidity, visibility, and air quality to predict sunset beauty
- **Feedback Learning**: Collects your 1-10 ratings to calibrate and improve predictions over time
- **Location Support**: Currently configured for Texcoco, Mexico (easily adaptable to SF Bay Area)

## Setup

### Prerequisites

1. **Telegram Bot Token**: @Bayweatherbot (already configured)
2. **OpenWeatherMap API Key**: Already added to GitHub Secrets ✓
3. **GitHub Repository**: Actions enabled

### Quick Start

1. **Message the bot**: [@Bayweatherbot](https://t.me/Bayweatherbot) - send "hi"
2. **Test manually**: Go to Actions → "Sunset Prediction Bot" → "Run workflow"
3. **Check Telegram**: You should receive a prediction!

### Providing Feedback

After each sunset:
1. Watch the actual sunset
2. Reply to the bot's message with a number 1-10
3. Bot confirms and stores your rating

**Rating Guide:**
- 1-3: Disappointing, dull colors
- 4-6: Average, some nice colors
- 7-8: Beautiful, vibrant colors
- 9-10: Spectacular, stunning sunset

## Files

- `sunset_bot.py`: Main bot logic and prediction model
- `sunset_data.db`: SQLite database (auto-created)
- `model_weights.json`: Model parameters (auto-created)
- `requirements.txt`: Python dependencies
- `.github/workflows/sunset-prediction.yml`: Automation

## Customization

### Change Location (for SF Bay Area)

Edit in `sunset_bot.py`:
```python
location_name = "San Francisco"
lat = 37.7749
lon = -122.4194
```

### Adjust Timing

Edit cron in `.github/workflows/sunset-prediction.yml`:
```yaml
- cron: '30 1 * * *'  # Example: 5:30 PM PST
```

## Model Training

After collecting 5+ ratings:
```bash
cd sunset-bot
python train_model.py
```

This shows which weather factors correlate with YOUR sunset preferences!

---

Built with ❤️ for beautiful sunsets 🌅
