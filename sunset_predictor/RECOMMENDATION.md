# Recommendation: Getting Enough Data

## Current Situation
- **14 sunset images** extracted successfully
- **~87 videos** failed to download (yt-dlp issues)
- **Need:** 50-100 samples for decent weather-based predictor

## Options (Ranked)

### Option 1: Fix Downloads & Get All Videos ⭐ BEST
**Action:** Fix yt-dlp installation or use alternative download method
- Install yt-dlp properly: `brew install yt-dlp` or `pip install yt-dlp`
- Or manually download videos from YouTube playlist
- Extract sunsets from all 101 videos
- **Result:** ~80-100 working sunset images

**Pros:**
- Gets us to comfortable dataset size
- All from same source (consistent)
- Covers 2000-2020 time period

**Cons:**
- Requires fixing download issues
- Takes time to download 101 videos

### Option 2: Data Augmentation ⭐ GOOD ALTERNATIVE
**Action:** Extract multiple frames per video (sunset ±30min, ±10min)
- Extract 4 frames per video: -30min, -10min, +10min, +30min
- **Result:** 14 videos × 4 frames = 56 samples

**Pros:**
- Quick (no downloads needed)
- Increases dataset 4x
- Still uses same videos (consistent)

**Cons:**
- Less diversity (same videos, different times)
- May have some correlation between frames
- Still on the small side (56 samples)

### Option 3: Manual Download + Extract ⭐ RELIABLE
**Action:** You manually download videos, we extract frames
- You download videos from YouTube playlist
- Place in `data/lhs_timelapses/`
- Run: `python3 extract_lhs_sunsets.py --process-all`
- **Result:** All 101 videos → ~80-100 sunsets

**Pros:**
- Most reliable
- You control the process
- Can verify downloads

**Cons:**
- Manual work for you
- Takes time

### Option 4: Work with 14 + Strong Regularization ⚠️ RISKY
**Action:** Use 14 samples with very strong regularization
- Use Ridge/Lasso regression with high alpha
- Cross-validation to prevent overfitting
- **Result:** Basic predictor, but high variance

**Pros:**
- Can start immediately
- Tests the approach

**Cons:**
- Very small dataset (high overfitting risk)
- Unreliable predictions
- Not recommended for production

## My Recommendation

**Do Option 2 (Data Augmentation) FIRST** - Quick win, gets us to 56 samples
**Then Option 1 or 3** - Get to 80-100 samples for better model

**Combined approach:**
1. Extract 4 frames per existing 14 videos = 56 samples
2. Fix downloads or manually get more videos
3. Extract sunsets from additional videos
4. **Final:** 80-100+ samples for training

## Next Steps

1. **Immediate:** Extract multiple frames from existing videos (4x dataset)
2. **Short-term:** Fix yt-dlp or manually download remaining videos
3. **Then:** Extract all sunsets and grade them
4. **Finally:** Train weather-based predictor with 80-100 samples

This gets us to a workable dataset size!


