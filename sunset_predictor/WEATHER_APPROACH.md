# Weather-Based Sunset Quality Prediction

## Great Idea! 🎯

Instead of extracting 300 sunset images, we can:
1. **Use historical weather data** as predictors
2. **You grade ~100 sunsets** from the videos we have
3. **Train model:** Weather features → Sunset quality

This is much more practical!

## Approach

### Features (Predictors)
- Temperature (max/min)
- Humidity
- Cloud cover
- Precipitation
- Wind speed
- Visibility
- Pressure
- Sky conditions (clear/cloudy/overcast)

### Target
- Sunset quality score (1-10) from your manual grading

### Data Needed
- **~100 graded sunsets** (from the 101 videos we have)
- **Weather data** for those same dates

## Steps

### 1. Grade ~100 Sunsets
```bash
python3 grade_sunsets.py
```
Grade sunsets from the videos we successfully extracted.

### 2. Get Weather Data

**Option A: Manual Download (Free)**
- NOAA: https://www.ncei.noaa.gov/cdo-web/
- Weather Underground: https://www.wunderground.com/history
- Download CSV for dates with sunset scores

**Option B: Use Template**
```bash
python3 download_weather_data.py --create-template
```
Fill in weather data manually.

### 3. Train Model
```bash
python3 train_weather_predictor.py \
    --sunset-scores data/sunset_images_for_grading/sunset_metadata.json \
    --weather-data data/weather/weather_data.csv
```

### 4. Predict Future Sunsets
Use midday weather forecasts to predict sunset quality!

## Advantages

✅ **Much faster** - Only need ~100 graded sunsets
✅ **More reliable** - Weather data is standardized
✅ **Predictive** - Can use weather forecasts
✅ **Scalable** - Works for any location with weather data

## Next Steps

1. Fix extraction to get all working sunsets from videos
2. Grade ~100 of them
3. Download weather data for those dates
4. Train the weather-based predictor!


