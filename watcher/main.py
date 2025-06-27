"""
Main application for the Distracted Driving Detector
"""

import time
import signal
import sys
import os
import logging
from datetime import datetime, timedelta
from motion_detector import MotionDetector
from video_recorder import VideoRecorder
from utils.time_utils import is_within_recording_time
import config
import threading


class MotionRecordingSystem:
    """
    Main system that coordinates motion detection and video recording
    """

    def __init__(self):
        self.motion_detector = MotionDetector(config.CAMERA_INDEX)
        self.video_recorder = VideoRecorder()
        self.is_running = False
        self.motion_detected = False
        self.recording_frames = []

        # Motion persistence tracking
        self.motion_persistence_count = 0
        self.motion_cooldown_count = 0
        self.is_recording_clip = False
        self.last_motion_time = 0  # Track when motion was last detected

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Set picamera2 logging to INFO level to reduce verbose debug output
        logging.getLogger('picamera2.picamera2').setLevel(logging.INFO)

    def start(self):
        """Start the motion recording system"""
        self.logger.info("Starting Motion Recording System...")
        self.logger.info(f"Recording window: {config.RECORDING_START_TIME} - {config.RECORDING_END_TIME}")
        self.logger.info(f"Storage directory: {config.STORAGE_DIR}")
        self.logger.info(f"Temporary directory: {config.TEMP_STORAGE_DIR}")

        # Ensure storage directories exist
        os.makedirs(config.STORAGE_DIR, exist_ok=True)
        os.makedirs(config.TEMP_STORAGE_DIR, exist_ok=True)

        self.is_running = True

        # Start motion detection
        self.motion_detector.start(self._on_motion_state_change)

        # Main loop
        try:
            while self.is_running:
                # Check if we're within recording time
                if is_within_recording_time(config.RECORDING_START_TIME, config.RECORDING_END_TIME):
                    # System is active during recording hours
                    time.sleep(1)

                    # Periodic cleanup of old clips
                    if config.CLEANUP_OLD_CLIPS:
                        self._cleanup_old_clips()
                else:
                    # Outside recording hours - sleep longer
                    self.logger.info("Outside recording hours, sleeping...")
                    time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        finally:
            self.stop()

    def stop(self):
        """Stop the system"""
        self.is_running = False
        self.motion_detector.stop()
        self.video_recorder.stop_recording()
        self.logger.info("System stopped.")

    def _on_motion_state_change(self, motion_detected: bool):
        """
        Callback when motion state changes

        Args:
            motion_detected: True if motion is detected, False otherwise
        """
        if motion_detected:
            # Motion detected - increment persistence counter
            self.motion_persistence_count += 1
            self.motion_cooldown_count = 0
            self.last_motion_time = time.time()

            # Start recording if motion persists for required frames
            if (self.motion_persistence_count >= config.MOTION_PERSISTENCE_FRAMES and
                not self.is_recording_clip):
                self.logger.info(f"Motion detected! Starting recording... (persistence: {self.motion_persistence_count})")
                self._start_recording_clip()
        else:
            # Motion stopped - increment cooldown counter
            self.motion_cooldown_count += 1
            self.motion_persistence_count = 0

            # Stop recording if motion has been absent for cooldown frames
            if (self.motion_cooldown_count >= config.MOTION_COOLDOWN_FRAMES and
                self.is_recording_clip):
                self.logger.info(f"Motion stopped. Finishing recording... (cooldown: {self.motion_cooldown_count})")
                self._finish_recording_clip()
            elif self.is_recording_clip:
                self.logger.debug(f"Motion stopped, waiting for cooldown... (cooldown: {self.motion_cooldown_count}/{config.MOTION_COOLDOWN_FRAMES})")

    def _start_recording_clip(self):
        """Start recording a new clip"""
        if self.is_recording_clip:
            return

        self.is_recording_clip = True
        self.recording_frames = []
        # Start collecting frames in a background thread
        self._collect_thread = threading.Thread(target=self._collect_frames)
        self._collect_thread.daemon = True
        self._collect_thread.start()

    def _finish_recording_clip(self):
        """Finish recording the current clip"""
        if not self.is_recording_clip:
            return

        self.is_recording_clip = False
        # Don't join the thread here - let it finish naturally

        if self.recording_frames:
            # Record the clip
            filename = self.video_recorder.record_clip(self.recording_frames)
            if filename:
                self.logger.info(f"Saved clip: {filename}")
            self.recording_frames = []

    def _collect_frames(self):
        """Collect frames while motion is detected"""
        start_time = time.time()
        frame_count = 0

        while (self.is_recording_clip and self.is_running and
               (time.time() - start_time) < config.MAX_CLIP_DURATION):

            frame = self.motion_detector.get_current_frame()
            if frame is not None:
                self.recording_frames.append(frame.copy())
                frame_count += 1

            # Check if we should stop recording (motion stopped, max duration reached, or force stop)
            current_time = time.time()
            duration = current_time - start_time

            # Force stop if no motion persistence for too long
            if (current_time - self.last_motion_time) > config.FORCE_STOP_AFTER_MOTION:
                self.logger.debug(f"Force stopping recording: no motion persistence for {config.FORCE_STOP_AFTER_MOTION}s")
                break

            if not self.is_recording_clip or duration >= config.CLIP_DURATION:
                self.logger.debug(f"Stopping frame collection: is_recording_clip={self.is_recording_clip}, duration={duration:.1f}s")
                break

            time.sleep(1.0 / config.FPS)

        # If we're still recording, finish the clip
        if self.is_recording_clip:
            # Don't call _finish_recording_clip from within the thread
            # Just set the flag and let the main thread handle it
            self.is_recording_clip = False
            if self.recording_frames:
                # Record the clip directly here
                filename = self.video_recorder.record_clip(self.recording_frames)
                if filename:
                    self.logger.info(f"Saved clip: {filename}")
                self.recording_frames = []

    def _cleanup_old_clips(self):
        """Clean up old clips based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=config.CLIP_RETENTION_DAYS)
            deleted_count = 0

            # Clean up main storage directory
            for filename in os.listdir(config.STORAGE_DIR):
                if filename.endswith(f".{config.CLIP_FORMAT}"):
                    filepath = os.path.join(config.STORAGE_DIR, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))

                    if file_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        self.logger.debug(f"Deleted old clip: {filename}")

            # Clean up temporary directory (remove any orphaned temp files older than 1 hour)
            temp_cutoff = datetime.now() - timedelta(hours=1)
            temp_deleted_count = 0

            if os.path.exists(config.TEMP_STORAGE_DIR):
                for filename in os.listdir(config.TEMP_STORAGE_DIR):
                    if filename.endswith(f".{config.CLIP_FORMAT}"):
                        filepath = os.path.join(config.TEMP_STORAGE_DIR, filename)
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))

                        if file_time < temp_cutoff:
                            os.remove(filepath)
                            temp_deleted_count += 1
                            self.logger.debug(f"Deleted orphaned temp file: {filename}")

            if deleted_count > 0 or temp_deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old clips and {temp_deleted_count} orphaned temp files")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nReceived interrupt signal, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the system
    system = MotionRecordingSystem()
    system.start()


if __name__ == "__main__":
    main()