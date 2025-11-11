#!/bin/bash

# Job Hunter Startup Script

echo "=================================="
echo "Job Hunter Application"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
mkdir -p app
mkdir -p templates
mkdir -p static

echo ""
echo "=================================="
echo "Starting Job Hunter..."
echo "=================================="
echo ""
echo "🌐 Web interface will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application
python run.py
