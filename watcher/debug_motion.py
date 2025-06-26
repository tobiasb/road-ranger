#!/usr/bin/env python3
"""
Debug script for motion detection - shows detailed motion detection events
"""

import time
import signal
import sys
from motion_detector import MotionDetector, PICAMERA2_AVAILABLE
import config

class MotionDebugger:
    """Debug motion detection with detailed output"""

    def __init__(self):
        self.motion_detector = MotionDetector(config.CAMERA_INDEX)
        self.is_running = False
        self.motion_count = 0
        self.last_motion_time = None

        # Motion persistence tracking (same as main system)
        self.motion_persistence_count = 0
        self.motion_cooldown_count = 0

    def start(self):
        """Start the motion detection debug"""
        print("Starting Motion Detection Debug...")
        print(f"Picamera2 available: {PICAMERA2_AVAILABLE}")
        print(f"Motion persistence frames: {config.MOTION_PERSISTENCE_FRAMES}")
        print(f"Motion cooldown frames: {config.MOTION_COOLDOWN_FRAMES}")
        print(f"Motion threshold: {config.MOTION_THRESHOLD}")
        print(f"Min motion area: {config.MIN_MOTION_AREA}")
        print("Press Ctrl+C to stop")
        print("-" * 50)

        self.is_running = True
        self.motion_detector.start(self._on_motion_state_change)

        # Determine camera type after initialization
        if hasattr(self.motion_detector, 'picam') and self.motion_detector.picam:
            camera_type = "Picamera2"
        elif hasattr(self.motion_detector, 'cap') and self.motion_detector.cap:
            camera_type = "OpenCV VideoCapture"
        else:
            camera_type = "Unknown"

        print(f"Camera initialized: {camera_type}")

        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping debug...")
        finally:
            self.stop()

    def stop(self):
        """Stop the debug"""
        self.is_running = False
        self.motion_detector.stop()
        print(f"\nDebug completed. Total motion events: {self.motion_count}")

    def _on_motion_state_change(self, motion_detected: bool):
        """Handle motion state changes with detailed logging"""
        current_time = time.time()

        if motion_detected:
            # Motion detected - increment persistence counter
            self.motion_persistence_count += 1
            self.motion_cooldown_count = 0

            print(f"[{time.strftime('%H:%M:%S')}] MOTION DETECTED! (persistence: {self.motion_persistence_count}/{config.MOTION_PERSISTENCE_FRAMES})")

            # Check if motion persists for required frames
            if self.motion_persistence_count >= config.MOTION_PERSISTENCE_FRAMES:
                self.motion_count += 1
                self.last_motion_time = current_time
                print(f"[{time.strftime('%H:%M:%S')}] *** MOTION PERSISTED! Starting recording... (#{self.motion_count}) ***")
        else:
            # Motion stopped - increment cooldown counter
            self.motion_cooldown_count += 1
            old_persistence = self.motion_persistence_count
            self.motion_persistence_count = 0

            print(f"[{time.strftime('%H:%M:%S')}] Motion stopped (cooldown: {self.motion_cooldown_count}/{config.MOTION_COOLDOWN_FRAMES})")

            if old_persistence > 0:
                print(f"[{time.strftime('%H:%M:%S')}] *** Motion persistence reset ***")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nReceived interrupt signal, stopping debug...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the debug
    debugger = MotionDebugger()
    debugger.start()


if __name__ == "__main__":
    main()