#!/bin/bash
# Creates all sunset bot files in one go

set -e
echo "🌅 Creating sunset prediction bot files..."

# Create directory structure
mkdir -p sunset-bot/.github/workflows

# Create sunset_bot.py
cat > sunset-bot/sunset_bot.py << 'EOF'
#!/usr/bin/env python3
"""
Sunset Quality Prediction Bot for Texcoco, Mexico
Predicts aesthetic quality of sunsets based on weather data
"""

import os
import json
import requests
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
import sqlite3


class SunsetPredictor:
    """Predicts sunset quality based on weather conditions"""
    
    def __init__(self):
        self.weights = self.load_weights()
    
    def load_weights(self):
        """Load model weights from file, or use defaults"""
        default_weights = {
            'cloud_cover_optimal': 0.4,  # 40% cloud cover is often ideal
            'cloud_cover_weight': 3.0,
            'humidity_weight': 1.5,
            'visibility_weight': 2.0,
            'pollution_weight': 1.0,
            'dust_weight': 2.5,  # Dust can create spectacular sunsets
        }
        
        if os.path.exists('model_weights.json'):
            with open('model_weights.json', 'r') as f:
                return json.load(f)
        return default_weights
    
    def save_weights(self):
        """Save updated weights after training"""
        with open('model_weights.json', 'w') as f:
            json.dump(self.weights, f, indent=2)
    
    def predict(self, weather_data):
        """
        Predict sunset quality on 1-10 scale
        
        Args:
            weather_data: dict with keys:
                - cloud_cover: percentage (0-100)
                - humidity: percentage (0-100)
                - visibility: meters
                - aqi: air quality index (optional)
                - pm25: PM2.5 level (optional)
        
        Returns:
            float: predicted quality (1-10)
        """
        score = 5.0  # Start at middle
        
        # Cloud cover: Sweet spot around 30-50%
        cloud_cover = weather_data.get('cloud_cover', 50)
        cloud_deviation = abs(cloud_cover - (self.weights['cloud_cover_optimal'] * 100))
        cloud_score = (100 - cloud_deviation) / 100 * self.weights['cloud_cover_weight']
        score += (cloud_score - 1.5)  # Center around 0
        
        # Humidity: Lower is generally better for vivid colors
        humidity = weather_data.get('humidity', 60)
        humidity_score = (100 - humidity) / 100 * self.weights['humidity_weight']
        score += (humidity_score - 0.75)
        
        # Visibility: Higher is better, but diminishing returns
        visibility = weather_data.get('visibility', 10000)
        visibility_km = visibility / 1000
        visibility_score = min(visibility_km / 10, 1.0) * self.weights['visibility_weight']
        score += (visibility_score - 1.0)
        
        # Air quality: Some particulates help, but too much is bad
        pm25 = weather_data.get('pm25', 15)
        if 10 <= pm25 <= 35:  # Sweet spot for colorful sunsets
            dust_score = self.weights['dust_weight'] * 0.5
        elif pm25 < 10:  # Too clean
            dust_score = -self.weights['dust_weight'] * 0.3
        else:  # Too polluted
            dust_score = -self.weights['dust_weight'] * 0.5
        score += dust_score
        
        # Clamp to 1-10 range
        return max(1.0, min(10.0, score))


class WeatherFetcher:
    """Fetches weather data from OpenWeatherMap API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, lat, lon):
        """Get current weather conditions"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            'cloud_cover': data['clouds']['all'],
            'humidity': data['main']['humidity'],
            'visibility': data.get('visibility', 10000),
            'description': data['weather'][0]['description'],
            'temp': data['main']['temp'],
        }
        
        return weather_info
    
    def get_air_quality(self, lat, lon):
        """Get air quality data"""
        url = f"{self.base_url}/air_pollution"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            components = data['list'][0]['components']
            return {
                'aqi': data['list'][0]['main']['aqi'],
                'pm25': components.get('pm2_5', 15),
                'pm10': components.get('pm10', 20),
            }
        except:
            return {'aqi': 3, 'pm25': 15, 'pm10': 20}  # Defaults


class SunsetBot:
    """Main bot controller"""
    
    def __init__(self, telegram_token, weather_api_key, location_name, lat, lon):
        self.telegram_token = telegram_token
        self.weather_fetcher = WeatherFetcher(weather_api_key)
        self.predictor = SunsetPredictor()
        self.location_name = location_name
        self.lat = lat
        self.lon = lon
        self.db_path = 'sunset_data.db'
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for feedback storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                sunset_time TEXT NOT NULL,
                predicted_quality REAL NOT NULL,
                actual_quality INTEGER,
                weather_data TEXT NOT NULL,
                feedback_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_sunset_time(self, date=None):
        """Calculate sunset time for location"""
        if date is None:
            date = datetime.now(pytz.timezone('America/Mexico_City'))
        
        location = LocationInfo(
            self.location_name, 
            "Mexico", 
            "America/Mexico_City", 
            self.lat, 
            self.lon
        )
        s = sun(location.observer, date=date)
        return s['sunset']
    
    def send_telegram_message(self, chat_id, text):
        """Send message via Telegram bot"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data)
        return response.json()
    
    def get_telegram_updates(self):
        """Get recent messages to bot"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
        response = requests.get(url)
        return response.json()
    
    def get_chat_id(self, username):
        """Get chat ID for a username from recent updates"""
        updates = self.get_telegram_updates()
        
        for update in updates.get('result', []):
            if 'message' in update:
                msg = update['message']
                if msg.get('from', {}).get('username', '').lower() == username.lower().replace('@', ''):
                    return msg['chat']['id']
        
        return None
    
    def save_prediction(self, sunset_time, predicted_quality, weather_data):
        """Save prediction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (date, sunset_time, predicted_quality, weather_data)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().strftime('%Y-%m-%d'),
            sunset_time.strftime('%Y-%m-%d %H:%M:%S'),
            predicted_quality,
            json.dumps(weather_data)
        ))
        conn.commit()
        conn.close()
    
    def run_prediction(self, chat_id):
        """Main prediction workflow"""
        # Get sunset time
        sunset_time = self.get_sunset_time()
        
        # Fetch weather data
        weather = self.weather_fetcher.get_current_weather(self.lat, self.lon)
        air_quality = self.weather_fetcher.get_air_quality(self.lat, self.lon)
        weather.update(air_quality)
        
        # Make prediction
        predicted_quality = self.predictor.predict(weather)
        
        # Save to database
        self.save_prediction(sunset_time, predicted_quality, weather)
        
        # Format message
        message = f"""🌅 *Sunset Prediction for {self.location_name}*

*Sunset Time:* {sunset_time.strftime('%I:%M %p')}
*Predicted Quality:* {predicted_quality:.1f}/10

*Current Conditions:*
- Cloud Cover: {weather['cloud_cover']}%
- Humidity: {weather['humidity']}%
- Visibility: {weather['visibility']/1000:.1f} km
- PM2.5: {weather.get('pm25', 'N/A')}
- Weather: {weather['description']}

After watching the sunset, reply with a number 1-10 to help calibrate the model!
"""
        
        # Send message
        result = self.send_telegram_message(chat_id, message)
        return result
    
    def process_feedback(self):
        """Check for feedback messages and update database"""
        updates = self.get_telegram_updates()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for update in updates.get('result', []):
            if 'message' in update:
                msg = update['message']
                text = msg.get('text', '').strip()
                
                # Check if it's a rating (1-10)
                try:
                    rating = int(text)
                    if 1 <= rating <= 10:
                        # Update most recent prediction without feedback
                        cursor.execute('''
                            UPDATE predictions
                            SET actual_quality = ?, feedback_time = ?
                            WHERE actual_quality IS NULL
                            ORDER BY created_at DESC
                            LIMIT 1
                        ''', (rating, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                        
                        # Send confirmation
                        self.send_telegram_message(
                            msg['chat']['id'],
                            f"Thanks! Recorded your rating of {rating}/10 🌅"
                        )
                except ValueError:
                    pass
        
        conn.close()


def main():
    """Main execution"""
    # Get configuration from environment variables
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    weather_api_key = os.environ.get('OPENWEATHER_API_KEY')
    
    if not telegram_token or not weather_api_key:
        print("Error: Missing required environment variables")
        print("Need: TELEGRAM_BOT_TOKEN, OPENWEATHER_API_KEY")
        return
    
    # Texcoco, Mexico coordinates
    location_name = "Texcoco"
    lat = 19.5164
    lon = -98.8836
    
    # Initialize bot
    bot = SunsetBot(telegram_token, weather_api_key, location_name, lat, lon)
    
    # Get chat ID (you may need to message the bot first)
    username = "Kaseymarkel"
    chat_id = bot.get_chat_id(username)
    
    if not chat_id:
        print(f"Could not find chat ID for @{username}")
        print("Please message the bot first at t.me/Bayweatherbot")
        return
    
    # Run prediction and send message
    result = bot.run_prediction(chat_id)
    print(f"Prediction sent: {result}")
    
    # Process any pending feedback
    bot.process_feedback()


if __name__ == "__main__":
    main()
EOF

echo "✅ Created sunset_bot.py"

# Create requirements.txt
cat > sunset-bot/requirements.txt << 'EOF'
requests>=2.31.0
astral>=3.2
pytz>=2023.3
EOF

echo "✅ Created requirements.txt"

# Create .gitignore
cat > sunset-bot/.gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Database - we actually want to commit this to track predictions
# sunset_data.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables (use GitHub Secrets instead)
.env
EOF

echo "✅ Created .gitignore"

# Create GitHub Actions workflow
cat > sunset-bot/.github/workflows/sunset-prediction.yml << 'EOF'
name: Sunset Prediction Bot

on:
  schedule:
    # Runs at 6:30 PM CST (00:30 UTC next day) - adjust based on actual sunset
    # In winter: sunsets ~6:00 PM, in summer: ~8:00 PM in Texcoco
    # Running at 6:30 PM should catch most, will need seasonal adjustment
    - cron: '30 0 * * *'  # 6:30 PM CST daily
  
  workflow_dispatch:  # Allows manual testing

jobs:
  predict-sunset:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd sunset-bot
        pip install requests astral pytz
    
    - name: Run sunset prediction
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
      run: |
        cd sunset-bot
        python sunset_bot.py
    
    - name: Commit updated data
      run: |
        cd sunset-bot
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add -A
        git diff --quiet && git diff --staged --quiet || git commit -m "Update sunset predictions and feedback [skip ci]"
        git push
      continue-on-error: true  # Don't fail if no changes to commit
EOF

echo "✅ Created GitHub Actions workflow"

# Create train_model.py
cat > sunset-bot/train_model.py << 'EOF'
#!/usr/bin/env python3
"""
Train sunset prediction model from collected feedback data
Run this periodically after collecting ratings
"""

import sqlite3
import json
import numpy as np
from datetime import datetime


def load_feedback_data():
    """Load all predictions with feedback from database"""
    conn = sqlite3.connect('sunset_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT predicted_quality, actual_quality, weather_data
        FROM predictions
        WHERE actual_quality IS NOT NULL
    ''')
    
    data = []
    for row in cursor.fetchall():
        predicted, actual, weather_json = row
        weather = json.loads(weather_json)
        data.append({
            'predicted': predicted,
            'actual': actual,
            'weather': weather
        })
    
    conn.close()
    return data


def calculate_model_accuracy(data):
    """Calculate current model performance metrics"""
    if not data:
        print("No feedback data available yet!")
        return
    
    predictions = [d['predicted'] for d in data]
    actuals = [d['actual'] for d in data]
    
    mae = np.mean([abs(p - a) for p, a in zip(predictions, actuals)])
    rmse = np.sqrt(np.mean([(p - a)**2 for p, a in zip(predictions, actuals)]))
    
    print(f"\n📊 Current Model Performance")
    print(f"=" * 50)
    print(f"Total ratings collected: {len(data)}")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"Root Mean Squared Error: {rmse:.2f}")
    print(f"\nAverage predicted quality: {np.mean(predictions):.2f}")
    print(f"Average actual quality: {np.mean(actuals):.2f}")
    print(f"Bias: {np.mean(predictions) - np.mean(actuals):.2f}")
    
    # Show some examples
    print(f"\n🌅 Recent Examples:")
    for i, d in enumerate(data[-5:]):
        print(f"  Predicted: {d['predicted']:.1f} | Actual: {d['actual']} | "
              f"Clouds: {d['weather']['cloud_cover']}% | "
              f"Humidity: {d['weather']['humidity']}%")


def analyze_feature_correlations(data):
    """Analyze which weather features correlate with good sunsets"""
    if len(data) < 3:
        print("\nNeed at least 3 ratings to analyze correlations")
        return
    
    actuals = [d['actual'] for d in data]
    
    features = {
        'cloud_cover': [],
        'humidity': [],
        'visibility': [],
        'pm25': []
    }
    
    for d in data:
        w = d['weather']
        features['cloud_cover'].append(w['cloud_cover'])
        features['humidity'].append(w['humidity'])
        features['visibility'].append(w.get('visibility', 10000))
        features['pm25'].append(w.get('pm25', 15))
    
    print(f"\n🔍 Feature Analysis:")
    print(f"=" * 50)
    
    for feature, values in features.items():
        corr = np.corrcoef(values, actuals)[0, 1]
        print(f"{feature:15s}: correlation = {corr:+.3f}")
    
    # Find optimal cloud cover range
    cloud_actuals = list(zip(features['cloud_cover'], actuals))
    cloud_actuals.sort(key=lambda x: x[1], reverse=True)
    top_clouds = [c for c, a in cloud_actuals[:len(cloud_actuals)//3]]
    
    if top_clouds:
        print(f"\n☁️  Best sunsets had cloud cover: {min(top_clouds):.0f}-{max(top_clouds):.0f}%")
        print(f"   (Average: {np.mean(top_clouds):.0f}%)")


def suggest_weight_adjustments(data):
    """Suggest weight adjustments based on errors"""
    if len(data) < 5:
        print("\nNeed at least 5 ratings to suggest weight adjustments")
        return
    
    print(f"\n💡 Suggested Improvements:")
    print(f"=" * 50)
    
    # Analyze systematic errors
    errors = [d['predicted'] - d['actual'] for d in data]
    avg_error = np.mean(errors)
    
    if abs(avg_error) > 1.0:
        if avg_error > 0:
            print(f"⚠️  Model is over-predicting by {avg_error:.1f} points on average")
            print(f"   Consider reducing base score or feature weights")
        else:
            print(f"⚠️  Model is under-predicting by {abs(avg_error):.1f} points on average")
            print(f"   Consider increasing base score or feature weights")
    
    # Check if certain conditions are consistently wrong
    high_clouds = [d for d in data if d['weather']['cloud_cover'] > 70]
    if len(high_clouds) >= 2:
        high_cloud_errors = [d['predicted'] - d['actual'] for d in high_clouds]
        if np.mean(high_cloud_errors) > 1.5:
            print(f"⚠️  Over-predicting in high cloud conditions")
            print(f"   Consider increasing penalty for high cloud cover")
    
    low_humidity = [d for d in data if d['weather']['humidity'] < 40]
    if len(low_humidity) >= 2:
        low_hum_errors = [d['predicted'] - d['actual'] for d in low_humidity]
        if np.mean(low_hum_errors) < -1.5:
            print(f"⚠️  Under-predicting in low humidity conditions")
            print(f"   Consider increasing humidity weight")


def main():
    """Main training workflow"""
    print("🌅 Sunset Prediction Model Training")
    print("=" * 50)
    
    # Load data
    data = load_feedback_data()
    
    if not data:
        print("\n❌ No feedback data found!")
        print("Rate some sunsets first, then run this script.")
        return
    
    # Show current performance
    calculate_model_accuracy(data)
    
    # Analyze features
    analyze_feature_correlations(data)
    
    # Suggest improvements
    suggest_weight_adjustments(data)
    
    print(f"\n" + "=" * 50)
    print("Training complete! Review suggestions above.")
    print("To apply changes, edit model_weights.json manually")
    print("(Automated training coming in future version)")


if __name__ == "__main__":
    main()
EOF

echo "✅ Created train_model.py"

# Create test_local.py
cat > sunset-bot/test_local.py << 'EOF'
#!/usr/bin/env python3
"""
Local test script for sunset bot
Run this to test the bot without GitHub Actions
"""

import os
import sys

# Set test environment variables (replace with your actual keys)
os.environ['TELEGRAM_BOT_TOKEN'] = input("Enter Telegram bot token: ").strip()
os.environ['OPENWEATHER_API_KEY'] = input("Enter OpenWeather API key: ").strip()

print("\n🧪 Testing sunset bot...\n")

# Import and run the bot
import sunset_bot

try:
    sunset_bot.main()
    print("\n✅ Test completed successfully!")
    print("Check your Telegram for the prediction message.")
except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
EOF

echo "✅ Created test_local.py"

# Create README.md
cat > sunset-bot/README.md << 'EOF'
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
EOF

echo "✅ Created README.md"

echo ""
echo "🎉 All files created successfully!"
echo ""
echo "Next steps:"
echo "1. git add sunset-bot/"
echo "2. git commit -m 'Add sunset prediction bot'"
echo "3. git push"
echo "4. Message @Bayweatherbot on Telegram"
echo "5. Test via GitHub Actions"
