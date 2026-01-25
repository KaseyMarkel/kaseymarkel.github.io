# How to Start Grading Sunsets

## Option 1: Run in Your Terminal (Recommended)

Open Terminal and run:

```bash
cd /Users/kasey/personal_website/sunset_predictor
python3 grade_sunsets.py
```

This will open an interactive window showing sunset images one by one.

## Option 2: I Can Run It For You

Just ask me to run it, and I'll start the grading interface. However, you'll need to interact with it yourself to see the images and score them.

## How the Grading Interface Works

When you run `python3 grade_sunsets.py`:

1. **Image Display**: Shows one sunset image at a time
2. **Scoring**: 
   - Press **1-10** keys to score (1 = poor, 10 = spectacular)
   - Or use the **slider** to adjust score
   - Press **Enter** to save and move to next
   - **Left/Right arrows** to navigate between images
3. **Auto-save**: Scores are saved automatically to `sunset_metadata.json`

## Current Status

- **7 sunset images** ready for grading
- Located in: `data/grading/images_to_grade/`
- Metadata: `data/sunset_images_for_grading/sunset_metadata.json`

## Quick Start

Just copy-paste this into your terminal:

```bash
cd /Users/kasey/personal_website/sunset_predictor && python3 grade_sunsets.py
```

The grading window will open and you can start scoring!


