#!/bin/bash
# Quick setup for daily sunset email automation

echo "Daily Sunset Email Setup"
echo "========================"
echo ""

# Check model
if [ -f "models/dual_predictor.pth" ]; then
    echo "✓ Model found"
else
    echo "✗ Model not found - need to train first!"
    exit 1
fi

# Get email password
echo ""
echo "Step 1: Gmail App Password"
echo "---------------------------"
echo "1. Go to: https://myaccount.google.com/apppasswords"
echo "2. Generate an app password for 'Mail'"
echo "3. Copy the 16-character password"
echo ""
read -p "Enter your Gmail app password: " -s EMAIL_PASS
echo ""

# Add to shell config
SHELL_RC="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if ! grep -q "EMAIL_PASSWORD" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Sunset predictor email password" >> "$SHELL_RC"
    echo "export EMAIL_PASSWORD='$EMAIL_PASS'" >> "$SHELL_RC"
    echo "✓ Added EMAIL_PASSWORD to $SHELL_RC"
else
    echo "⚠ EMAIL_PASSWORD already in $SHELL_RC"
fi

# Export for current session
export EMAIL_PASSWORD="$EMAIL_PASS"

# Find livestream URL
echo ""
echo "Step 2: Livestream Image URL"
echo "-----------------------------"
echo "We need to find the actual image URL from LHS webcam."
echo "Try visiting: https://lawrencehallofscience.org/play/view/"
echo "and look for the webcam image URL (right-click image -> Copy Image Address)"
echo ""
read -p "Enter the livestream image URL (or press Enter to skip): " LIVESTREAM_URL

if [ ! -z "$LIVESTREAM_URL" ]; then
    # Update download script
    sed -i.bak "s|LHS_LIVESTREAM_URL = \".*\"|LHS_LIVESTREAM_URL = \"$LIVESTREAM_URL\"|" download_daily_midday.py
    sed -i.bak "s|urls_to_try = \[|urls_to_try = [\"$LIVESTREAM_URL\",|" download_daily_midday.py
    echo "✓ Updated livestream URL"
fi

# Install cron jobs
echo ""
echo "Step 3: Install Cron Jobs"
echo "--------------------------"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

CRON_3PM="0 15 * * * cd $SCRIPT_DIR && $PYTHON_PATH daily_sunset_automation.py >> logs/cron.log 2>&1"
CRON_EMAIL="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH send_sunset_email.py >> logs/cron.log 2>&1"

mkdir -p "$SCRIPT_DIR/logs"

read -p "Install cron jobs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "$CRON_3PM"; echo "$CRON_EMAIL") | crontab -
    echo "✓ Cron jobs installed!"
    echo ""
    echo "Cron jobs:"
    crontab -l | grep "daily_sunset\|send_sunset"
else
    echo "Skipped cron installation"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To test manually:"
echo "  python3 daily_sunset_automation.py"
echo ""
echo "To view logs:"
echo "  tail -f logs/cron.log"

