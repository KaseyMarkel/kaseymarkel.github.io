#!/bin/bash

echo "🌱 BC Breeding Dashboard - Local Preview"
echo "========================================"
echo ""
echo "Starting local web server..."
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
    echo "🌐 Opening dashboard at http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Try to open browser automatically
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sleep 1 && open http://localhost:8000 &
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sleep 1 && xdg-open http://localhost:8000 &
    fi
    
    python3 -m http.server 8000
else
    echo "❌ Python 3 not found"
    echo ""
    echo "Please install Python 3 or simply open index.html in your browser"
fi
