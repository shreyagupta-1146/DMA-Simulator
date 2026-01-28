#!/bin/bash

# DMA Controller Simulator - Setup Script for Linux/Mac

echo "============================================================"
echo "DMA CONTROLLER SIMULATOR - AUTOMATED SETUP"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "   Please install pip3"
    exit 1
fi

echo "✓ pip3 found"

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit 1

echo "✓ Changed to backend directory"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "To start the server, run one of these commands:"
echo ""
echo "  Option 1: python3 run.py (from project root)"
echo "  Option 2: cd backend && python3 app.py"
echo ""
echo "Then open http://localhost:5000 in your browser"
echo ""
echo "============================================================"