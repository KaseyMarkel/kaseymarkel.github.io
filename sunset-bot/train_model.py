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
