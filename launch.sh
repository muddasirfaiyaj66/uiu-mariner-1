#!/bin/bash
# UIU MARINER ROV Control Launcher
# Linux/macOS shell script

echo "========================================"
echo "  UIU MARINER - ROV Control System"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Launching ROV Control Application..."
echo ""

# Launch application
python src/ui/rovControlApp.py

echo ""
echo "Application closed."
