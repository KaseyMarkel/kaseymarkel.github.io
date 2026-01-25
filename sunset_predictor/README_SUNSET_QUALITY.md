# Sunset Quality Prediction Project

## Goal
Predict the **aesthetic quality** of sunsets from midday sky images (3 hours before sunset).

## Workflow

### Step 1: Collect Sunset Images
Get ~300 actual sunset images for manual grading.

**Option A: From YouTube Timelapse**
```bash
python3 extract_sunset_frames.py \
    --url <YOUTUBE_URL> \
    --start-date 2024-01-01 \
    --speed 1.0 \
    --num-sunsets 300
```

**Option B: From Existing Images**
```bash
python3 collect_sunset_images.py --existing-dir /path/to/sunset/images
```

**Option C: Manual Collection**
1. Download sunset images from LBNL webcam archive
2. Place in `data/sunset_images_for_grading/`
3. Name them: `sunset_YYYYMMDD.jpg`

### Step 2: Organize for Grading
```bash
python3 setup_grading.py
```

This creates:
- `data/grading/images_to_grade/` - Numbered images ready for review
- `data/grading/grading_sheet.csv` - Spreadsheet for scores

### Step 3: Grade Sunsets
**Option A: Interactive Grading (Recommended)**
```bash
python3 grade_sunsets.py
```

Shows images one by one with:
- Score slider (1-10)
- Keyboard shortcuts (1-10 keys to score)
- Auto-saves scores

**Option B: Manual Grading**
1. Open images in `data/grading/images_to_grade/`
2. Review each sunset
3. Record scores in `grading_sheet.csv`
4. Run: `python3 import_grades.py` to import scores

### Step 4: Collect Midday Images
For each sunset, get the corresponding midday image (3 hours before):

```bash
python3 collect_midday_images.py \
    --sunset-metadata data/sunset_images_for_grading/sunset_metadata.json \
    --output-dir data/midday_images
```

### Step 5: Train Quality Predictor
Train model to predict sunset quality from midday images:

```bash
python3 train_quality_predictor.py \
    --midday-images data/midday_images \
    --sunset-scores data/sunset_images_for_grading/sunset_metadata.json \
    --output-dir models/quality_predictor
```

## File Structure

```
data/
├── sunset_images_for_grading/     # Actual sunset images
│   ├── sunset_20240101.jpg
│   ├── sunset_20240102.jpg
│   └── sunset_metadata.json       # With quality scores
├── midday_images/                  # Images 3h before sunset
│   ├── midday_20240101.jpg
│   └── ...
└── grading/
    ├── images_to_grade/            # Organized for grading
    └── grading_sheet.csv           # Score spreadsheet
```

## Grading Scale

Suggested scale: **1-10**
- 1-3: Poor (cloudy, dull, no color)
- 4-6: Average (some color, decent)
- 7-8: Good (nice colors, clear)
- 9-10: Spectacular (vibrant, dramatic, beautiful)

## Next Steps After Grading

Once you've graded ~300 sunsets:

1. **Pair with midday images** - Get images 3 hours before each sunset
2. **Train classifier** - Predict quality score from midday image
3. **Evaluate** - Test on held-out sunsets
4. **Deploy** - Use midday images to predict sunset quality!

## Quick Start

If you have a YouTube timelapse URL:

```bash
# 1. Extract sunset frames
python3 extract_sunset_frames.py --url <URL> --start-date 2024-01-01

# 2. Setup grading
python3 setup_grading.py

# 3. Grade sunsets
python3 grade_sunsets.py
```

Then we'll train the quality predictor!

