"""
Video recording module for the Distracted Driving Detector
"""

import cv2
import os
import time
import logging
from datetime import datetime
import config
import numpy as np
import threading
from typing import Optional, List
from collections import deque
from utils.time_utils import get_timestamp_string


class VideoRecorder:
    """
    Records video clips when motion is detected
    """

    def __init__(self):
        self.is_recording = False
        self.frame_buffer = deque(maxlen=int(config.FPS * config.PRE_MOTION_BUFFER))
        self.recording_thread = None
        self.current_writer = None
        self.current_filename = None

        # Ensure storage directory exists
        os.makedirs(config.STORAGE_DIR, exist_ok=True)

    def start_recording(self, motion_detector):
        """
        Start recording a clip when motion is detected

        Args:
            motion_detector: MotionDetector instance to get frames from
        """
        if self.is_recording:
            return

        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._recording_loop,
            args=(motion_detector,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)

    def _recording_loop(self, motion_detector):
        """Main recording loop"""
        motion_start_time = None
        motion_stop_time = None
        recording_started = False

        while self.is_recording:
            frame = motion_detector.get_current_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # Add frame to buffer
            self.frame_buffer.append(frame.copy())

            # Check if we should start/stop recording based on motion
            # This is a simplified approach - in practice you'd want more sophisticated
            # motion state tracking from the motion detector

            time.sleep(1.0 / config.FPS)  # Maintain frame rate

    def _create_video_writer(self, filename: str):
        """Create a new video writer"""
        fourcc = cv2.VideoWriter_fourcc(*config.CODEC)
        writer = cv2.VideoWriter(
            filename,
            fourcc,
            config.FPS,
            (config.FRAME_WIDTH, config.FRAME_HEIGHT)
        )
        return writer

    def _generate_filename(self) -> str:
        """Generate filename for new clip"""
        timestamp = get_timestamp_string()
        filename = f"{config.CLIP_NAME_FORMAT.format(timestamp=timestamp, duration=config.CLIP_DURATION)}.{config.CLIP_FORMAT}"
        return os.path.join(config.STORAGE_DIR, filename)

    def record_clip(self, frames: List[np.ndarray]) -> str:
        """
        Record a clip from a list of frames

        Args:
            frames: List of frames to record

        Returns:
            Path to the recorded file
        """
        if not frames:
            return None

        # Calculate actual duration from number of frames
        actual_duration = len(frames) / config.FPS

        # Generate filename with actual duration
        timestamp = get_timestamp_string()
        filename = f"{config.CLIP_NAME_FORMAT.format(timestamp=timestamp, duration=int(actual_duration))}.{config.CLIP_FORMAT}"
        filepath = os.path.join(config.STORAGE_DIR, filename)

        writer = self._create_video_writer(filepath)

        try:
            for frame in frames:
                writer.write(frame)
        finally:
            writer.release()

        print(f"Recorded clip: {filepath}")
        return filepath