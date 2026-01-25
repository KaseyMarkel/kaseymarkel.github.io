# Current Status: Sunset Quality Prediction

## ✅ What's Done

1. **Installed ffmpeg** - Video processing ready
2. **Downloaded 1 timelapse video** - Yesterday's video from LHS
3. **Extracted 1 sunset image** - Ready for grading
4. **Created grading system** - Interactive grading interface ready
5. **All scripts created** - Collection, extraction, grading scripts ready

## 📊 Current Counts

- **Timelapse videos:** 1 (yesterday)
- **Sunset images extracted:** 1
- **Ready for grading:** 1
- **Target:** 300 sunsets

## 🎯 Next Steps

### To Get 300 Sunsets:

**Option 1: Daily Collection (Easiest)**
- Download "yesterday" video daily for 300 days
- Or set up automated daily download script

**Option 2: Manual Archive Download**
- Visit: https://lawrencehallofscience.org/play/view/
- Check "Time-lapse Archive" section
- Download videos manually
- Place in `data/lhs_timelapses/`
- Run: `python3 process_new_videos.py`

**Option 3: Check Archive API**
- The archive page may have an API or listing
- Could scrape available video URLs

### Once You Have Videos:

```bash
# Process any new videos you download
python3 process_new_videos.py

# Update grading folder
python3 setup_grading.py

# Start grading
python3 grade_sunsets.py
```

## 🎨 Start Grading Now

You can start grading the 1 sunset we have:

```bash
python3 grade_sunsets.py
```

This will show the sunset image and let you score it 1-10.

## 📁 File Locations

- **Videos:** `data/lhs_timelapses/`
- **Sunset images:** `data/sunset_images_for_grading/`
- **Grading folder:** `data/grading/images_to_grade/`
- **Metadata:** `data/sunset_images_for_grading/sunset_metadata.json`

## 🔄 Automated Processing

The script `process_new_videos.py` will:
- Check for new videos in `data/lhs_timelapses/`
- Extract sunset frames automatically
- Update metadata
- Skip already processed videos

Just download videos and run: `python3 process_new_videos.py`

