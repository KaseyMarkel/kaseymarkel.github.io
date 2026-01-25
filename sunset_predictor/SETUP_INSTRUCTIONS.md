# Setup Instructions: Sunset Quality Prediction

## Current Status

✅ **Downloaded:** Yesterday's timelapse video  
✅ **Scripts Created:** All collection and grading scripts ready  
⏳ **Need:** ffmpeg installed, more timelapse videos, grading

## Step 1: Install ffmpeg

```bash
brew install ffmpeg
```

This is required to extract frames from videos.

## Step 2: Extract Sunset from Yesterday's Video

Once ffmpeg is installed:

```bash
python3 extract_from_yesterday.py
```

This will extract the sunset frame and save it to `data/sunset_images_for_grading/sunset_YYYYMMDD.jpg`

## Step 3: Get More Timelapse Videos (300 total)

The LHS archive page shows historical timelapses. You have a few options:

### Option A: Manual Download (Recommended)

1. Visit: https://lawrencehallofscience.org/play/view/
2. Scroll to "Time-lapse Archive" section
3. Download videos for dates you want
4. Save them to: `data/lhs_timelapses/`
5. Name them: `lhs_YYYYMMDD.mp4` (or any name, script will detect)

Then extract sunsets:
```bash
python3 extract_lhs_sunsets.py --process-all
```

### Option B: Check Archive URL Pattern

The videos might be accessible at:
- `https://www.ocf.berkeley.edu/~thelawrence/timelapse/YYYYMMDDview.1080p.mp4`
- Or similar patterns

You can try:
```bash
python3 download_300_sunsets.py --num-sunsets 300
```

This will attempt to download videos, but may not work for all dates.

### Option C: Contact LHS

They may have an archive API or bulk download option. Check their website or contact them.

## Step 4: Extract All Sunset Frames

Once you have videos in `data/lhs_timelapses/`:

```bash
python3 extract_lhs_sunsets.py --process-all
```

This will:
- Extract sunset frame from each video
- Save to `data/sunset_images_for_grading/`
- Create metadata with dates and sunset times

## Step 5: Organize for Grading

```bash
python3 setup_grading.py
```

Creates:
- `data/grading/images_to_grade/` - Numbered images (0001_sunset.jpg, etc.)
- `data/grading/grading_sheet.csv` - Spreadsheet for scores

## Step 6: Grade Sunsets

**Interactive Grading (Easiest):**
```bash
python3 grade_sunsets.py
```

Shows images one by one:
- Press **1-10** keys to score
- Use **slider** to adjust
- **Enter** to save and next
- **Left/Right** arrows to navigate
- Auto-saves scores

**Manual Grading:**
1. Open `data/grading/images_to_grade/` in Finder
2. Review each sunset image
3. Record scores in `data/grading/grading_sheet.csv`
4. Import scores: `python3 import_grades.py` (to be created)

## Step 7: After Grading

Once you've graded ~300 sunsets, we'll:
1. Collect midday images (3 hours before each sunset)
2. Train a classifier to predict sunset quality from midday images
3. Test and deploy the model

## File Structure

```
data/
├── lhs_timelapses/              # Timelapse videos
│   ├── yesterdayview.1080p.mp4
│   └── lhs_YYYYMMDD.mp4         # More videos here
├── sunset_images_for_grading/   # Extracted sunset images
│   ├── sunset_20260103.jpg
│   ├── sunset_20260102.jpg
│   └── sunset_metadata.json     # With quality scores
└── grading/
    ├── images_to_grade/         # Organized for grading
    └── grading_sheet.csv        # Score spreadsheet
```

## Quick Commands

```bash
# Extract from yesterday's video (once ffmpeg installed)
python3 extract_from_yesterday.py

# Process all videos in directory
python3 extract_lhs_sunsets.py --process-all

# Setup grading
python3 setup_grading.py

# Start grading
python3 grade_sunsets.py
```

## Getting 300 Videos

The main challenge is getting 300 timelapse videos. Options:

1. **Check LHS Archive Page** - They may have a download page or API
2. **Contact LHS** - Ask about archive access
3. **Daily Collection** - Download "yesterday" video daily for 300 days
4. **Manual Download** - Download from archive page manually

Once you have the videos, the extraction and grading process is automated!

