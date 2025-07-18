#!/bin/bash

echo "🚀 Starting Meta Ad Library Scraper..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 setup.py"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
python -c "import flask, selenium, requests, beautifulsoup4" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed. Please run setup first:"
    echo "   python3 setup.py"
    exit 1
fi

# Check if Chrome/Chromium is available
if command -v chromium-browser >/dev/null 2>&1; then
    echo "✅ Chromium browser found"
elif command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome browser found"
else
    echo "⚠️  Warning: No browser found. Install Chrome or Chromium for full functionality."
    echo "   sudo apt install chromium-browser"
fi

echo ""
echo "🌐 Starting Flask application..."
echo "📍 Application will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the Flask application
python app.py