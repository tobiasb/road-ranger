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
echo "   - python3-dateutil (date/time utilities)"
echo "   - python3-pil (image processing)"
sudo apt install -y python3-picamera2 python3-opencv python3-numpy python3-dateutil python3-pil

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
echo "1. Test motion detection: python3 test_motion_detection.py"
echo "2. Test camera: python3 test_picamera2.py"
echo "3. Start camera stream (for remote viewing): python3 camera_streamer.py"
echo "4. Run the full system: python3 main.py"
echo ""
echo "📖 See README.md for configuration and usage information"
echo "🔧 Edit config.py to customize recording settings"