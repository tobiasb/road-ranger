#!/usr/bin/env python3
"""
Test script for YOLOv8 car detection functionality
"""

import os
import sys
import cv2
import numpy as np
import time
import argparse
from pathlib import Path
import config
from yolo_car_detector import YOLOCarDetector


def test_yolo_detection_on_sample():
    """Test YOLO car detection on a sample video clip"""
    print("Testing YOLOv8 car detection...")

    # Initialize detector
    detector = YOLOCarDetector(model_size=config.MODEL_SIZE)

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
    result = detector.analyze_video_clip(test_file, sample_frames=config.SAMPLE_FRAMES)

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
    print(f"  Detection method: {result['detection_method']}")
    print(f"  Confidence threshold: {result['confidence_threshold']}")

    return True


def test_frame_detection():
    """Test YOLO car detection on a single frame"""
    print("\nTesting frame-level YOLO car detection...")

    # Create a simple test frame (you could also load an actual image)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Add a simple rectangle to simulate a car (this won't be detected as a real car)
    cv2.rectangle(test_frame, (200, 200), (400, 300), (255, 255, 255), -1)

    detector = YOLOCarDetector(model_size=config.MODEL_SIZE)
    detections = detector.detect_cars_in_frame(test_frame)

    print(f"Detections in test frame: {len(detections)}")
    for i, detection in enumerate(detections):
        bbox = detection['bbox']
        confidence = detection['confidence']
        print(f"  Detection {i+1}: {bbox} confidence={confidence:.2f}")

    return True


def test_yolo_model_loading():
    """Test if the YOLO model loads correctly"""
    print("\nTesting YOLO model loading...")

    try:
        # Test the YOLO detector initialization
        detector = YOLOCarDetector(model_size=config.MODEL_SIZE)
        print(f"✓ YOLOv8{config.MODEL_SIZE} model loaded successfully")
        print(f"✓ Confidence threshold: {detector.confidence_threshold}")
        print(f"✓ Car class ID: {detector.car_class_id}")
        return True
    except Exception as e:
        print(f"✗ Failed to load YOLO model: {e}")
        return False


def test_performance():
    """Test YOLO detection performance"""
    print("\nTesting YOLO detection performance...")

    detector = YOLOCarDetector(model_size=config.MODEL_SIZE)

    # Create a test frame
    test_frame = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # Time the detection
    start_time = time.time()
    detections = detector.detect_cars_in_frame(test_frame)
    end_time = time.time()

    processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
    print(f"✓ Frame processing time: {processing_time:.1f}ms")
    print(f"✓ Detections found: {len(detections)}")

    return True


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test YOLOv8 car detection')
    parser.add_argument('--model-size', choices=['n', 's', 'm', 'l', 'x'], default=config.MODEL_SIZE,
                       help=f'YOLO model size to test (default: {config.MODEL_SIZE})')
    args = parser.parse_args()

    print("YOLOv8 Car Detection Test Suite")
    print("===============================")
    print(f"Testing with model: yolov8{args.model_size}")

    # Test 1: Model loading
    if test_yolo_model_loading():
        print("✓ Model loading test passed")
    else:
        print("✗ Model loading test failed")
        return

    # Test 2: Frame-level detection
    if test_frame_detection():
        print("✓ Frame detection test passed")
    else:
        print("✗ Frame detection test failed")

    # Test 3: Performance
    if test_performance():
        print("✓ Performance test passed")
    else:
        print("✗ Performance test failed")

    # Test 4: Video clip analysis
    if test_yolo_detection_on_sample():
        print("✓ Video analysis test passed")
    else:
        print("✗ Video analysis test failed")

    print("\nTest suite complete!")


if __name__ == "__main__":
    main()