#!/bin/bash
# Setup cron jobs for daily sunset automation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

# Create cron job entries
CRON_3PM="0 15 * * * cd $SCRIPT_DIR && $PYTHON_PATH daily_sunset_automation.py >> logs/cron.log 2>&1"
CRON_EMAIL="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH send_sunset_email.py >> logs/cron.log 2>&1"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo "Setting up cron jobs for sunset automation..."
echo ""
echo "Cron jobs to add:"
echo "1. Download midday image and predict (3pm daily):"
echo "   $CRON_3PM"
echo ""
echo "2. Send email if it's 1 hour before sunset (check every hour):"
echo "   $CRON_EMAIL"
echo ""
echo "To add these cron jobs, run:"
echo "  crontab -e"
echo ""
echo "Then paste these lines:"
echo ""
echo "$CRON_3PM"
echo "$CRON_EMAIL"
echo ""
echo "Or run this script with --install flag to auto-install (requires confirmation):"

if [ "$1" == "--install" ]; then
    read -p "Install cron jobs? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        (crontab -l 2>/dev/null; echo "$CRON_3PM"; echo "$CRON_EMAIL") | crontab -
        echo "✓ Cron jobs installed!"
        echo "View with: crontab -l"
    else
        echo "Cancelled."
    fi
fi

