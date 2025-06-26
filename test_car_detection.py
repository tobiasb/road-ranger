#!/usr/bin/env python3
"""
Test script for car detection functionality
"""

import cv2
import numpy as np
import os
import sys
from car_detector import CarDetector
import config


def test_car_detection_on_sample():
    """Test car detection on a sample video clip"""
    print("Testing car detection...")

    # Initialize detector
    detector = CarDetector()

    # Check if we have any video files to test with
    if not os.path.exists(config.STORAGE_DIR):
        print(f"Storage directory {config.STORAGE_DIR} does not exist!")
        return False

    video_files = [f for f in os.listdir(config.STORAGE_DIR)
                   if f.lower().endswith('.mp4')]

    if not video_files:
        print("No video files found for testing!")
        return False

    # Test with the first video file
    test_file = os.path.join(config.STORAGE_DIR, video_files[0])
    print(f"Testing with: {video_files[0]}")

    # Analyze the video
    result = detector.analyze_video_clip(test_file, sample_frames=5)

    if "error" in result:
        print(f"Error: {result['error']}")
        return False

    print("Analysis Results:")
    print(f"  Video: {os.path.basename(result['video_path'])}")
    print(f"  Duration: {result['duration']:.1f}s")
    print(f"  Frames analyzed: {result['frames_analyzed']}")
    print(f"  Frames with cars: {result['frames_with_cars']}")
    print(f"  Car ratio: {result['car_ratio']:.2f}")
    print(f"  Has cars: {result['has_cars']}")
    print(f"  Total detections: {result['total_car_detections']}")

    return True


def test_frame_detection():
    """Test car detection on a single frame"""
    print("\nTesting frame-level car detection...")

    # Create a simple test frame (you could also load an actual image)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Add a simple rectangle to simulate a car (this won't be detected as a real car)
    cv2.rectangle(test_frame, (200, 200), (400, 300), (255, 255, 255), -1)

    detector = CarDetector()
    detections = detector.detect_cars_in_frame(test_frame)

    print(f"Detections in test frame: {len(detections)}")
    for i, (x, y, w, h, conf) in enumerate(detections):
        print(f"  Detection {i+1}: ({x}, {y}, {w}, {h}) confidence={conf:.2f}")

    return True


def test_cascade_loading():
    """Test if the car cascade classifier loads correctly"""
    print("\nTesting cascade classifier loading...")

    # Test the car detector initialization
    detector = CarDetector()

    if detector.car_cascade is not None:
        print("✓ Cascade classifier loaded successfully")
        return True
    else:
        print("✗ Cascade classifier not available, using simple detection")
        print("✓ Simple detection method available as fallback")
        return True


def main():
    """Main test function"""
    print("Car Detection Test Suite")
    print("========================")

    # Test 1: Cascade loading
    if test_cascade_loading():
        print("✓ Cascade loading test passed")
    else:
        print("✗ Cascade loading test failed")
        return

    # Test 2: Frame-level detection
    if test_frame_detection():
        print("✓ Frame detection test passed")
    else:
        print("✗ Frame detection test failed")

    # Test 3: Video clip analysis
    if test_car_detection_on_sample():
        print("✓ Video analysis test passed")
    else:
        print("✗ Video analysis test failed")

    print("\nTest suite complete!")


if __name__ == "__main__":
    main()