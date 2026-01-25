# Grading Instructions

## Quick Start

Open Terminal and run these commands:

```bash
cd /Users/kasey/personal_website/sunset_predictor
```

## Grade Each Timepoint

Grade images for each timepoint one at a time:

```bash
# Grade -10 minutes before sunset
python3 grade_timepoint.py --timepoint -10

# Grade -5 minutes before sunset  
python3 grade_timepoint.py --timepoint -5

# Grade exactly at sunset (sun under horizon)
python3 grade_timepoint.py --timepoint 0

# Grade +5 minutes after sunset
python3 grade_timepoint.py --timepoint 5

# Grade +10 minutes after sunset
python3 grade_timepoint.py --timepoint 10

# Grade +15 minutes after sunset
python3 grade_timepoint.py --timepoint 15

# Grade +20 minutes after sunset
python3 grade_timepoint.py --timepoint 20

# Grade +25 minutes after sunset
python3 grade_timepoint.py --timepoint 25
```

## How the Grading Interface Works

When you run a command, it will:
1. Open a window showing images one by one
2. Display the timepoint and image number
3. Let you score 1-10:
   - Press **1-10** keys to score
   - Use the **slider** to adjust
   - Press **Enter** to save and move to next
   - **Left/Right arrows** to navigate
4. Auto-saves scores as you go

## After Grading All Timepoints

Once you've graded all 8 timepoints:

```bash
# Calculate peak times from your scores
python3 calculate_peak_time.py

# Train the dual predictor model
python3 train_dual_predictor.py
```

## Manual Grading Alternative

If you prefer to grade manually:
1. Open folders: `data/grading_by_timepoint/timepoint_Xmin/images_to_grade/`
2. Review images
3. Record scores in: `data/grading_by_timepoint/timepoint_Xmin/grading_sheet.csv`

Then import scores (script to be created if needed).

## Summary

**Total images to grade:** ~86 images × 8 timepoints = ~688 images

**Recommended order:**
1. Start with timepoint 0 (sunset)
2. Then grade surrounding timepoints (-10, -5, +5, +10, +15, +20, +25)
3. This helps you see the progression and score consistently

**Time per timepoint:** ~10-15 minutes (depending on how fast you grade)

**Total time:** ~1.5-2 hours to grade all timepoints


