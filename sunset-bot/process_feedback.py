#!/usr/bin/env python3
"""
Process feedback from Telegram users
Runs independently from prediction workflow
"""

import os
import sqlite3
import requests
from datetime import datetime


def get_telegram_updates(token):
    """Get recent messages to bot"""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    return response.json()


def send_telegram_message(token, chat_id, text):
    """Send message via Telegram bot"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=data)
    return response.json()


def process_feedback(token):
    """Check for new feedback and process it"""
    updates = get_telegram_updates(token)
    
    conn = sqlite3.connect('sunset_data.db')
    cursor = conn.cursor()
    
    # Get the most recent prediction
    cursor.execute('''
        SELECT id FROM predictions 
        ORDER BY created_at DESC 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    
    if not result:
        print("No predictions found")
        conn.close()
        return
    
    latest_prediction_id = result[0]
    feedback_count = 0
    
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
                        feedback_count += 1
                        
                        # Send confirmation
                        send_telegram_message(
                            token,
                            chat_id,
                            f"Thanks! Recorded your rating of {rating}/10 🌅"
                        )
                        print(f"Processed rating {rating} from chat_id {chat_id}")
            except ValueError:
                pass
    
    conn.close()
    
    if feedback_count > 0:
        print(f"Processed {feedback_count} new rating(s)")
    else:
        print("No new feedback to process")


def main():
    """Main execution"""
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not telegram_token:
        print("Error: Missing TELEGRAM_BOT_TOKEN")
        return
    
    process_feedback(telegram_token)


if __name__ == "__main__":
    main()
