# Quick Start: Sunset Quality Prediction

## Current Status

✅ **Downloaded:** Yesterday's timelapse video from Lawrence Hall of Science
- File: `data/lhs_timelapses/yesterdayview.1080p.mp4`
- Source: https://lawrencehallofscience.org/play/view/

## Next Steps

### 1. Install ffmpeg (Required)

```bash
brew install ffmpeg
```

### 2. Extract Sunset from Yesterday's Video

Once ffmpeg is installed:

```bash
python3 extract_lhs_sunsets.py --video-file data/lhs_timelapses/yesterdayview.1080p.mp4
```

This will extract the sunset frame and save it to `data/sunset_images_for_grading/`

### 3. Get More Timelapse Videos

**Option A: Download from Archive Page**
1. Visit: https://lawrencehallofscience.org/play/view/
2. Check "Time-lapse Archive" section
3. Download videos manually
4. Place in `data/lhs_timelapses/`

**Option B: Try Automated Download**
```bash
python3 get_lhs_archive.py --try-daily --num-days 300
```

This attempts to download videos using URL patterns (may or may not work depending on their naming).

### 4. Extract All Sunset Frames

```bash
python3 extract_lhs_sunsets.py --process-all
```

Extracts sunset frames from all videos in `data/lhs_timelapses/`

### 5. Organize for Grading

```bash
python3 setup_grading.py
```

Creates organized folder with numbered images ready for grading.

### 6. Grade Sunsets

**Interactive Grading:**
```bash
python3 grade_sunsets.py
```

Shows images one by one:
- Press 1-10 to score
- Use slider to adjust
- Auto-saves scores

**Manual Grading:**
1. Open `data/grading/images_to_grade/`
2. Review each sunset
3. Fill scores in `data/grading/grading_sheet.csv`

### 7. After Grading ~300 Sunsets

We'll then:
1. Collect midday images (3 hours before each sunset)
2. Train a classifier to predict sunset quality from midday images
3. Test the model

## File Structure

```
data/
├── lhs_timelapses/              # Downloaded timelapse videos
│   └── yesterdayview.1080p.mp4
├── sunset_images_for_grading/   # Extracted sunset images
│   ├── sunset_20260103.jpg
│   └── sunset_metadata.json     # With quality scores after grading
└── grading/
    ├── images_to_grade/         # Organized for grading
    └── grading_sheet.csv         # Score spreadsheet
```

## Grading Scale

Rate each sunset **1-10**:
- **1-3:** Poor (cloudy, dull, no color)
- **4-6:** Average (some color, decent)
- **7-8:** Good (nice colors, clear sky)
- **9-10:** Spectacular (vibrant, dramatic, beautiful)

## Current Progress

- ✅ Scripts created for collection and grading
- ✅ Downloaded 1 timelapse video (yesterday)
- ⏳ Need ffmpeg to extract frames
- ⏳ Need more timelapse videos (300 total)
- ⏳ Need to grade sunsets
- ⏳ Then train quality predictor

## Getting More Videos

The LHS page shows a "Time-lapse Archive" section. You can:
1. Visit the archive page
2. Download videos manually
3. Or check if there's an API/pattern for automated download

Once you have ~300 timelapse videos, we can extract all the sunset frames and you can grade them!

