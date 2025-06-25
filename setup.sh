#!/bin/bash

# Setup script for Distracted Driving Detector
# This script handles the installation of dependencies and virtual environment setup

set -e  # Exit on any error

echo "🚀 Setting up Distracted Driving Detector..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi. Some dependencies may not work on other systems."
fi

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3-picamera2 python3-opencv python3-pip python3-venv

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create storage directory
echo "📁 Creating storage directory..."
mkdir -p recorded_clips

# Set permissions
echo "🔐 Setting permissions..."
chmod +x *.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the system:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Test motion detection: python test_motion_detection.py"
echo "3. Run the full system: python main.py"
echo ""
echo "📖 See README.md for more information"