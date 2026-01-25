# Quick test - just check if we can send you a message
import os
import requests

telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TOKEN_HERE')
chat_id = 1438794965

url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
data = {
    'chat_id': chat_id,
    'text': '🌅 Test message from sunset bot! If you see this, the bot is working!'
}

response = requests.post(url, data=data)
print(response.json())
