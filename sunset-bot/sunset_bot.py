#!/usr/bin/env python3
"""
Sunset Quality Prediction Bot - Multi-user version
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
            'cloud_cover_optimal': 0.4,
            'cloud_cover_weight': 3.0,
            'humidity_weight': 1.5,
            'visibility_weight': 2.0,
            'pollution_weight': 1.0,
            'dust_weight': 2.5,
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
        """Predict sunset quality on 1-10 scale"""
        score = 5.0
        
        # Cloud cover: Sweet spot around 30-50%
        cloud_cover = weather_data.get('cloud_cover', 50)
        cloud_deviation = abs(cloud_cover - (self.weights['cloud_cover_optimal'] * 100))
        cloud_score = (100 - cloud_deviation) / 100 * self.weights['cloud_cover_weight']
        score += (cloud_score - 1.5)
        
        # Humidity: Lower is better
        humidity = weather_data.get('humidity', 60)
        humidity_score = (100 - humidity) / 100 * self.weights['humidity_weight']
        score += (humidity_score - 0.75)
        
        # Visibility: Higher is better
        visibility = weather_data.get('visibility', 10000)
        visibility_km = visibility / 1000
        visibility_score = min(visibility_km / 10, 1.0) * self.weights['visibility_weight']
        score += (visibility_score - 1.0)
        
        # Air quality: Sweet spot for colorful sunsets
        pm25 = weather_data.get('pm25', 15)
        if 10 <= pm25 <= 35:
            dust_score = self.weights['dust_weight'] * 0.5
        elif pm25 < 10:
            dust_score = -self.weights['dust_weight'] * 0.3
        else:
            dust_score = -self.weights['dust_weight'] * 0.5
        score += dust_score
        
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
            return {'aqi': 3, 'pm25': 15, 'pm10': 20}


class SunsetBot:
    """Main bot controller with multi-user support"""
    
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
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                sunset_time TEXT NOT NULL,
                predicted_quality REAL NOT NULL,
                weather_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback table (links users to predictions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id),
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_sunset_time(self, date=None):
        """Calculate sunset time for location"""
        if date is None:
            date = datetime.now(pytz.timezone('America/Los_Angeles'))
        
        location = LocationInfo(
            self.location_name, 
            "Mexico", 
            "America/Los_Angeles", 
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
    
    def register_users_from_updates(self):
        """Check for new users and register them"""
        updates = self.get_telegram_updates()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_users = 0
        for update in updates.get('result', []):
            if 'message' in update:
                msg = update['message']
                chat_id = msg['chat']['id']
                username = msg.get('from', {}).get('username', '')
                first_name = msg.get('from', {}).get('first_name', '')
                
                # Check if user exists
                cursor.execute('SELECT chat_id FROM users WHERE chat_id = ?', (chat_id,))
                if not cursor.fetchone():
                    # New user - register them
                    cursor.execute('''
                        INSERT INTO users (chat_id, username, first_name)
                        VALUES (?, ?, ?)
                    ''', (chat_id, username, first_name))
                    new_users += 1
                    
                    # Send welcome message
                    welcome = f"""🌅 Welcome to Sunset Predictions, {first_name}!

You're now registered to receive daily sunset quality predictions 30 minutes before sunset in {self.location_name}.

After each sunset, reply with a number 1-10 to rate the actual quality and help improve the predictions!

Rating guide:
• 1-3: Disappointing
• 4-6: Average
• 7-8: Beautiful
• 9-10: Spectacular
"""
                    self.send_telegram_message(chat_id, welcome)
        
        conn.commit()
        conn.close()
        
        if new_users > 0:
            print(f"Registered {new_users} new user(s)")
        
        return new_users
    
    def get_active_users(self):
        """Get all active registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id, username, first_name FROM users WHERE active = 1')
        users = cursor.fetchall()
        conn.close()
        return users
    
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
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return prediction_id
    
    def run_prediction(self):
        """Main prediction workflow - send to all users"""
        # First, register any new users
        self.register_users_from_updates()
        
        # Get all active users
        users = self.get_active_users()
        
        if not users:
            print("No registered users yet!")
            return
        
        # Get sunset time
        sunset_time = self.get_sunset_time()
        
        # Fetch weather data
        weather = self.weather_fetcher.get_current_weather(self.lat, self.lon)
        air_quality = self.weather_fetcher.get_air_quality(self.lat, self.lon)
        weather.update(air_quality)
        
        # Make prediction
        predicted_quality = self.predictor.predict(weather)
        
        # Save to database
        prediction_id = self.save_prediction(sunset_time, predicted_quality, weather)
        
        # Format message
        message = f"""🌅 *Sunset Prediction for {self.location_name}*

*Sunset Time:* {sunset_time.strftime('%I:%M %p')}
*Predicted Quality:* {predicted_quality:.1f}/10

*Current Conditions:*
• Cloud Cover: {weather['cloud_cover']}%
• Humidity: {weather['humidity']}%
• Visibility: {weather['visibility']/1000:.1f} km
• PM2.5: {weather.get('pm25', 'N/A')}
• Weather: {weather['description']}

After watching the sunset, reply with a number 1-10 to help calibrate the model!
"""
        
        # Send to all users
        sent_count = 0
        for chat_id, username, first_name in users:
            try:
                result = self.send_telegram_message(chat_id, message)
                if result.get('ok'):
                    sent_count += 1
                    print(f"Sent prediction to @{username} (chat_id: {chat_id})")
                else:
                    print(f"Failed to send to @{username}: {result}")
            except Exception as e:
                print(f"Error sending to @{username}: {e}")
        
        print(f"Sent predictions to {sent_count}/{len(users)} users")
        
        # Process any pending feedback
        self.process_feedback(prediction_id)
    
    def process_feedback(self, latest_prediction_id):
        """Check for feedback messages and update database"""
        updates = self.get_telegram_updates()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for update in updates.get('result', []):
            if 'message' in update:
                msg = update['message']
                chat_id = msg['chat']['id']
                text = msg.get('text', '').strip()
                
                # Check if it's a rating (1-10)
                try:
                    rating = int(text)
                    if 1 <= rating <= 10:
                        # Check if this user already rated this prediction
                        cursor.execute('''
                            SELECT id FROM feedback 
                            WHERE prediction_id = ? AND chat_id = ?
                        ''', (latest_prediction_id, chat_id))
                        
                        if not cursor.fetchone():
                            # Save feedback
                            cursor.execute('''
                                INSERT INTO feedback (prediction_id, chat_id, rating)
                                VALUES (?, ?, ?)
                            ''', (latest_prediction_id, chat_id, rating))
                            conn.commit()
                            
                            # Send confirmation
                            self.send_telegram_message(
                                chat_id,
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
    
    # Richmond, CA coordinates
    location_name = "Richmond, CA"
    lat = 37.9358
    lon = -122.3478
    
    # Initialize bot
    bot = SunsetBot(telegram_token, weather_api_key, location_name, lat, lon)
    
    # Run prediction and send to all registered users
    bot.run_prediction()


if __name__ == "__main__":
    main()
