#!/usr/bin/env python3
"""
Test script to verify YOLOv8 installation and basic functionality
"""

import sys
import os

def test_yolo_import():
    """Test if YOLOv8 can be imported"""
    print("Testing YOLOv8 import...")
    try:
        from ultralytics import YOLO
        print("✓ YOLOv8 import successful")
        return True
    except ImportError as e:
        print(f"✗ YOLOv8 import failed: {e}")
        return False

def test_yolo_model_loading():
    """Test if YOLOv8 model can be loaded"""
    print("\nTesting YOLOv8 model loading...")
    try:
        from ultralytics import YOLO

        print("Loading YOLOv8n model (this may take a moment on first run)...")
        model = YOLO('yolov8n.pt')
        print("✓ YOLOv8n model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ YOLOv8n model loading failed: {e}")
        return False

def test_basic_detection():
    """Test basic object detection"""
    print("\nTesting basic object detection...")
    try:
        from ultralytics import YOLO
        import numpy as np

        # Create a simple test image (black image)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)

        # Load model and run detection
        model = YOLO('yolov8n.pt')
        results = model(test_image, verbose=False)

        print("✓ Basic detection test passed")
        return True
    except Exception as e:
        print(f"✗ Basic detection test failed: {e}")
        return False

def main():
    """Main test function"""
    print("YOLOv8 Installation Test Suite")
    print("==============================")

    # Test 1: Import
    if not test_yolo_import():
        print("\nInstallation failed. Please install YOLOv8:")
        print("pip install ultralytics")
        sys.exit(1)

    # Test 2: Model loading
    if not test_yolo_model_loading():
        print("\nModel loading failed. Check internet connection and disk space.")
        sys.exit(1)

    # Test 3: Basic detection
    if not test_basic_detection():
        print("\nBasic detection failed. Check YOLOv8 installation.")
        sys.exit(1)

    print("\n✓ All tests passed! YOLOv8 is ready to use.")
    print("\nYou can now run car detection with:")
    print("pipenv run python yolo_car_table.py")

if __name__ == "__main__":
    main()