#!/bin/bash

# Setup script for Watcher (recording side of Distracted Driving Detector)
# This script handles the complete installation of dependencies and environment setup

set -e  # Exit on any error

echo "🕵️ Setting up Watcher (Distracted Driving Detector - Recording Side)..."
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi."
    echo "   Some dependencies (like picamera2) may not work on other systems."
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "❌ Do not run this script as root (sudo)."
    echo "   The script will use sudo for specific commands that need it."
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
echo "   - python3-picamera2 (camera interface)"
echo "   - python3-opencv (computer vision)"
echo "   - python3-numpy (numerical computing)"
echo "   - python3-pip (package manager)"
echo "   - python3-venv (virtual environment)"
echo "   - python3-dateutil (date/time utilities)"
echo "   - python3-pil (image processing)"
sudo apt install -y python3-picamera2 python3-opencv python3-numpy python3-pip python3-venv python3-dateutil python3-pil

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Create storage directory
echo "📁 Creating storage directory..."
mkdir -p recorded_clips

# Set permissions for Python scripts
echo "🔐 Setting script permissions..."
chmod +x *.py

# Test installation
echo "🧪 Testing installation..."
if python -c "import cv2; print('✓ OpenCV installed')" 2>/dev/null; then
    echo "✓ OpenCV test passed"
else
    echo "❌ OpenCV test failed"
    exit 1
fi

if python -c "import picamera2; print('✓ Picamera2 installed')" 2>/dev/null; then
    echo "✓ Picamera2 test passed"
else
    echo "❌ Picamera2 test failed"
    exit 1
fi

if python -c "import numpy; print('✓ NumPy installed')" 2>/dev/null; then
    echo "✓ NumPy test passed"
else
    echo "❌ NumPy test failed"
    exit 1
fi

if python -c "import dateutil; print('✓ DateUtil installed')" 2>/dev/null; then
    echo "✓ DateUtil test passed"
else
    echo "❌ DateUtil test failed"
    exit 1
fi

if python -c "import PIL; print('✓ PIL/Pillow installed')" 2>/dev/null; then
    echo "✓ PIL/Pillow test passed"
else
    echo "❌ PIL/Pillow test failed"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Test motion detection: python test_motion_detection.py"
echo "3. Test camera: python test_picamera2.py"
echo "4. Run the full system: python main.py"
echo ""
echo "📖 See README.md for configuration and usage information"
echo "🔧 Edit config.py to customize recording settings"