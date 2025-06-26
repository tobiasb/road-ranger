"""
Motion detection module using OpenCV and Picamera2
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable
import config

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False


class MotionDetector:
    """
    Detects motion in video stream using background subtraction
    Supports both Picamera2 (Raspberry Pi) and OpenCV VideoCapture
    """

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.picam = None
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=100, varThreshold=config.MOTION_THRESHOLD, detectShadows=False
        )
        self.is_running = False
        self.motion_callback = None
        self.detection_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()

    def start(self, motion_callback: Callable[[bool], None]):
        """
        Start motion detection in a separate thread

        Args:
            motion_callback: Function to call when motion state changes
        """
        if self.is_running:
            return

        self.motion_callback = motion_callback

        # Try to use Picamera2 first (Raspberry Pi camera)
        if PICAMERA2_AVAILABLE and self.camera_index == 0:
            try:
                self._init_picamera2()
                print("Using Picamera2 for motion detection")
            except Exception as e:
                print(f"Failed to initialize Picamera2: {e}")
                print("Falling back to OpenCV VideoCapture")
                self._init_opencv_camera()
        else:
            if not PICAMERA2_AVAILABLE:
                print("Picamera2 not available, using OpenCV VideoCapture")
            self._init_opencv_camera()

        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def _init_picamera2(self):
        """Initialize Picamera2"""
        self.picam = Picamera2()
        config_dict = self.picam.create_preview_configuration(
            main={
                "size": (config.FRAME_WIDTH, config.FRAME_HEIGHT),
                "format": "RGB888"
            },
            buffer_count=2
        )
        self.picam.configure(config_dict)
        self.picam.start()
        time.sleep(2)  # Allow camera to warm up
        self.picam.set_controls({"AwbMode": 6})

    def _init_opencv_camera(self):
        """Initialize OpenCV VideoCapture"""
        self.cap = cv2.VideoCapture(self.camera_index)

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.FPS)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera at index {self.camera_index}")

    def stop(self):
        """Stop motion detection"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        if self.picam:
            self.picam.close()

    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        motion_detected = False

        while self.is_running:
            frame = self._get_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            # Store current frame for recording
            with self.frame_lock:
                self.current_frame = frame.copy()

            # Apply background subtraction
            fg_mask = self.background_subtractor.apply(frame)

            # Find contours of moving objects
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Check if any contour is large enough to be considered motion
            current_motion = False
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > config.MIN_MOTION_AREA:
                    current_motion = True
                    break

            # Notify callback if motion state changed
            if current_motion != motion_detected:
                motion_detected = current_motion
                if self.motion_callback:
                    self.motion_callback(motion_detected)

            time.sleep(config.MOTION_DETECTION_INTERVAL)

    def _get_frame(self) -> Optional[np.ndarray]:
        """Get frame from camera (Picamera2 or OpenCV)"""
        if self.picam:
            try:
                frame = self.picam.capture_array()
                # Convert RGB to BGR for OpenCV compatibility
                return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Failed to capture frame from Picamera2: {e}")
                return None
        elif self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current frame from camera (for recording)"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None