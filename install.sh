#!/bin/bash

# Installation Script for Job Hunter
# This script will set up the entire application

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Job Hunter - Installation Script                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Check Python version
echo "📋 Step 1: Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi
echo "✅ Python 3 is installed"
echo ""

# Step 2: Create virtual environment
echo "📋 Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment
echo "📋 Step 3: Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 4: Upgrade pip
echo "📋 Step 4: Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Step 5: Install dependencies
echo "📋 Step 5: Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Step 6: Create necessary directories
echo "📋 Step 6: Creating directories..."
mkdir -p app
mkdir -p templates
mkdir -p static
echo "✅ Directories created"
echo ""

# Step 7: Run installation checker
echo "📋 Step 7: Verifying installation..."
python3 check_installation.py
if [ $? -eq 0 ]; then
    echo "✅ Installation verified successfully"
else
    echo "⚠️  Installation verification had some warnings"
fi
echo ""

# Step 8: Make scripts executable
echo "📋 Step 8: Setting up scripts..."
chmod +x start.sh
chmod +x check_installation.py
echo "✅ Scripts configured"
echo ""

# Done
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Installation Complete! 🎉                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the application:"
echo "   ./start.sh"
echo ""
echo "2. Open your browser:"
echo "   http://localhost:5000"
echo ""
echo "3. Wait for the first scraper runs (they run hourly)"
echo ""
echo "For more information, see:"
echo "  - README.md          (Full documentation)"
echo "  - QUICKSTART.md      (Quick start guide)"
echo "  - ARCHITECTURE.md    (Technical details)"
echo "  - PROJECT_SUMMARY.md (Project overview)"
echo ""
echo "Happy Job Hunting! 🎯"
echo ""
