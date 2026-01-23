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
