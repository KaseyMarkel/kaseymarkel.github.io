# Day-by-Day Grading System

## New Grading Approach

Instead of grading timepoint by timepoint, you now grade **day by day**:
- All 8 sunset images for one day open in Preview
- Score them all in sequence
- Faster and easier!

## Usage

```bash
cd /Users/kasey/personal_website/sunset_predictor
python3 grade_by_day.py
```

## How It Works

1. **Opens all 8 images** for the current day in Preview
2. **Prompts for scores** one by one:
   ```
   -10 min: [type score 1-10]
   -5 min: [type score 1-10]
   0 min: [type score 1-10]
   ...
   ```
3. **Just type the number** and press Enter - no need to click in terminal!
4. **Auto-saves** all scores when done with the day
5. **Moves to next day** automatically

## Commands

- **1-10**: Score the image
- **s**: Skip this timepoint
- **q**: Quit current day (saves progress)
- **Ctrl+C**: Quit entirely (saves progress)

## Tips

- Keep Terminal window focused (don't click away)
- Type numbers quickly - no need to click
- All images for the day stay open in Preview
- You can reference earlier images while scoring later ones

## Progress

The script shows:
- Which day you're on (e.g., "Day 3/86")
- How many timepoints already graded
- Progress through all days

## After Grading

Once you've graded all days:
```bash
python3 prepare_training_data.py  # Update dataset
python3 train_dual_predictor.py    # Retrain model
```

