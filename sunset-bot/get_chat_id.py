import requests
import sys

token = input("Enter your Telegram bot token: ").strip()

url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url)
data = response.json()

print("\nRecent messages to your bot:")
print("=" * 50)

if data.get('result'):
    for update in data['result']:
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            username = msg.get('from', {}).get('username', 'N/A')
            text = msg.get('text', 'N/A')
            print(f"\nChat ID: {chat_id}")
            print(f"Username: @{username}")
            print(f"Message: {text}")
else:
    print("No messages found!")
    print("Make sure you've messaged the bot first.")

