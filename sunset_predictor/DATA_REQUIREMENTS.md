# Data Requirements for Sunset Quality Predictor

## Current Status
- **Videos available:** 101 in playlist
- **Videos downloaded:** ~100 (checking...)
- **Sunset images extracted:** ~14-100 (depends on extraction success)

## Minimum Data Requirements

### For Weather-Based Predictor

**With good weather features (cloud cover, humidity, etc.):**
- **Minimum:** 50-80 samples
- **Good:** 100-150 samples  
- **Excellent:** 200+ samples

**Why weather features help:**
- Weather data is standardized and reliable
- Features like cloud cover are directly related to sunset quality
- Less noise than image-based features
- Can use regularization to prevent overfitting

### For Image-Based Predictor

**Much more data needed:**
- **Minimum:** 200-300 samples
- **Good:** 500-1000 samples
- **Excellent:** 1000+ samples

**Why images need more:**
- High-dimensional feature space
- More variation in lighting, composition
- Need more examples to learn patterns

## Our Strategy

### Option 1: Weather-Based (Recommended)
1. Extract all sunsets from 101 videos (~80-100 working)
2. Grade ~80-100 sunsets
3. Get weather data for those dates
4. Train weather → quality predictor

**Advantages:**
- Can work with 50-100 samples
- More interpretable
- Can use forecasts for prediction

### Option 2: Hybrid Approach
1. Use weather features as primary predictors
2. Add image features (color, brightness) as secondary
3. Ensemble model

**Advantages:**
- Best of both worlds
- Can work with 100-150 samples
- More robust predictions

### Option 3: Data Augmentation
1. Extract multiple frames per video (sunset ±30 min)
2. Use data augmentation (rotation, brightness)
3. Increases effective dataset size

**Advantages:**
- Can multiply dataset size 2-3x
- Still need ~50-100 base samples

## Next Steps

1. **Extract all sunsets** from downloaded videos
2. **Count working extractions** - see how many we have
3. **If < 50:** Consider data augmentation or hybrid approach
4. **If 50-100:** Proceed with weather-based predictor
5. **If > 100:** Great! Can do more sophisticated models

## Realistic Expectations

With **~80-100 graded sunsets** and **weather features**, we can expect:
- **Baseline accuracy:** 60-70% (better than random)
- **Good model:** 70-80% accuracy
- **Excellent:** 80%+ (with good features and regularization)

This is reasonable for a sunset quality predictor!


