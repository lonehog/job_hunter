#!/bin/bash

# Glassdoor Job Scraper Runner
# This script activates the virtual environment and runs the scraper

echo "========================================="
echo "Glassdoor Job Scraper"
echo "========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    echo "Then: source .venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run scraper
cd "$SCRIPT_DIR"
source .venv/bin/activate

echo "Running scraper..."
python glassdoor_scraper.py

echo ""
echo "========================================="
echo "Analysis of scraped data:"
echo "========================================="
python view_jobs.py --analyze

echo ""
echo "Done! Check glassdoor_jobs.csv for results."
