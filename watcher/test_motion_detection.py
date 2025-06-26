#!/usr/bin/env python3
"""
Test script for motion detection with Raspberry Pi camera
This script tests the motion detection system without recording clips
"""

import time
import signal
import sys
from motion_detector import MotionDetector, PICAMERA2_AVAILABLE
import config

class MotionDetectionTester:
    """Test motion detection without recording"""

    def __init__(self):
        self.motion_detector = MotionDetector(config.CAMERA_INDEX)
        self.is_running = False
        self.motion_count = 0
        self.last_motion_time = None
        self.camera_type = "Unknown"

    def start(self):
        """Start the motion detection test"""
        print("Starting Motion Detection Test...")
        print(f"Picamera2 available: {PICAMERA2_AVAILABLE}")
        print(f"Resolution: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
        print(f"FPS: {config.FPS}")
        print(f"Motion threshold: {config.MOTION_THRESHOLD}")
        print(f"Min motion area: {config.MIN_MOTION_AREA}")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        self.is_running = True
        self.motion_detector.start(self._on_motion_state_change)

        # Determine camera type after initialization
        if hasattr(self.motion_detector, 'picam') and self.motion_detector.picam:
            self.camera_type = "Picamera2"
        elif hasattr(self.motion_detector, 'cap') and self.motion_detector.cap:
            self.camera_type = "OpenCV VideoCapture"
        else:
            self.camera_type = "Unknown"

        print(f"Camera initialized: {self.camera_type}")

        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping test...")
        finally:
            self.stop()

    def stop(self):
        """Stop the test"""
        self.is_running = False
        self.motion_detector.stop()
        print(f"\nTest completed. Total motion events: {self.motion_count}")

    def _on_motion_state_change(self, motion_detected: bool):
        """Handle motion state changes"""
        current_time = time.time()

        if motion_detected:
            self.motion_count += 1
            self.last_motion_time = current_time
            print(f"[{time.strftime('%H:%M:%S')}] MOTION DETECTED! (#{self.motion_count})")
        else:
            if self.last_motion_time:
                duration = current_time - self.last_motion_time
                print(f"[{time.strftime('%H:%M:%S')}] Motion stopped (duration: {duration:.1f}s)")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nReceived interrupt signal, stopping test...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the test
    tester = MotionDetectionTester()
    tester.start()


if __name__ == "__main__":
    main()