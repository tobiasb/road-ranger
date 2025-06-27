"""
Car detection module using YOLOv8 for accurate object detection
"""

import cv2
import numpy as np
import os
import logging
import signal
import sys
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import config
from ultralytics import YOLO
from database import CarDetectionDB
import subprocess


class YOLOCarDetector:
    """
    Detects cars in video clips using YOLOv8
    """

    def __init__(self, model_size: str = None, force: bool = False):
        """
        Initialize YOLO car detector

        Args:
            model_size: Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge)
            force: If True, reprocess files even if they have already been analyzed
        """
        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize YOLO model
        self.model_size = model_size or config.MODEL_SIZE
        self.model = self._load_yolo_model()

        # Detection settings
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        self.car_class_id = 2  # COCO dataset car class ID
        self.min_car_frames = 2  # Minimum frames with cars to consider video as containing cars

        # Performance settings for Raspberry Pi
        self.input_size = (640, 640)  # YOLO default input size
        self.sample_rate = 3  # Process every 3rd frame for speed

        # Processing control
        self.force = force

        # Initialize database
        self.db = CarDetectionDB(config.DATABASE_PATH)

        self.logger.info(f"YOLO car detector initialized with model: yolov8{self.model_size}")
        if self.force:
            self.logger.info("Force mode enabled - will reprocess files even if already analyzed")

    def _load_yolo_model(self) -> YOLO:
        """Load YOLO model"""
        try:
            model_name = f"yolov8{self.model_size}.pt"
            self.logger.info(f"Loading YOLO model: {model_name}")

            # This will automatically download the model if not present
            model = YOLO(model_name)

            self.logger.info(f"YOLO model loaded successfully")
            return model

        except Exception as e:
            self.logger.error(f"Failed to load YOLO model: {e}")
            raise

    def detect_cars_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect cars in a single frame using YOLOv8

        Args:
            frame: Input frame (BGR format)

        Returns:
            List of detection dictionaries with keys: bbox, confidence, class_id
        """
        try:
            # Run YOLO detection
            results = self.model(frame, verbose=False)

            car_detections = []

            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection info
                        bbox = box.xyxy[0].cpu().numpy()  # x1, y1, x2, y2
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])

                        # Filter for cars with sufficient confidence
                        if class_id == self.car_class_id and confidence >= self.confidence_threshold:
                            x1, y1, x2, y2 = bbox
                            detection = {
                                'bbox': (int(x1), int(y1), int(x2-x1), int(y2-y1)),  # x, y, w, h
                                'confidence': confidence,
                                'class_id': class_id
                            }
                            car_detections.append(detection)

            return car_detections

        except Exception as e:
            self.logger.error(f"Error in car detection: {e}")
            return []

    def analyze_video_clip(self, video_path: str, sample_frames: int = None) -> Dict:
        """
        Analyze a video clip to determine if it contains cars

        Args:
            video_path: Path to the video file
            sample_frames: Number of frames to sample for analysis

        Returns:
            Dictionary with analysis results
        """
        if sample_frames is None:
            sample_frames = config.SAMPLE_FRAMES

        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            return {"video_path": video_path, "error": "File not found"}

        # Check file size - if it's too small, it's likely corrupted
        file_size = os.path.getsize(video_path)
        if file_size < 1024:  # Less than 1KB
            self.logger.error(f"Video file too small (likely corrupted): {video_path} ({file_size} bytes)")
            return {"video_path": video_path, "error": "File too small (corrupted)"}

        # Check if file has proper MP4 headers using ffprobe
        try:
            result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', video_path],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                self.logger.error(f"Video file corrupted (ffprobe failed): {video_path}")
                return {"video_path": video_path, "error": "File corrupted (invalid MP4 headers)"}
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            # If ffprobe is not available or times out, continue with OpenCV
            self.logger.warning(f"ffprobe not available or timed out for {video_path}, continuing with OpenCV")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"Could not open video: {video_path}")
            return {"video_path": video_path, "error": "Could not open video"}

        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0

            # Calculate frame sampling strategy
            if total_frames <= sample_frames:
                frame_indices = list(range(total_frames))
            else:
                # Sample frames evenly throughout the video
                step = max(1, total_frames // sample_frames)
                frame_indices = list(range(0, total_frames, step))[:sample_frames]

            car_detections = []
            frames_with_cars = 0
            processed_frames = 0

            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    continue

                processed_frames += 1

                # Detect cars in this frame
                detections = self.detect_cars_in_frame(frame)

                if detections:
                    frames_with_cars += 1
                    car_detections.extend(detections)

            # Determine if video contains cars
            car_ratio = frames_with_cars / processed_frames if processed_frames > 0 else 0
            has_cars = frames_with_cars >= self.min_car_frames

            result = {
                "video_path": video_path,
                "total_frames": total_frames,
                "duration": duration,
                "frames_analyzed": processed_frames,
                "frames_with_cars": frames_with_cars,
                "car_ratio": car_ratio,
                "has_cars": has_cars,
                "total_car_detections": len(car_detections),
                "average_cars_per_frame": len(car_detections) / processed_frames if processed_frames > 0 else 0,
                "detection_method": f"yolov8{self.model_size}",
                "confidence_threshold": self.confidence_threshold,
                "min_car_frames": self.min_car_frames
            }

            self.logger.info(f"Analysis complete for {video_path}: has_cars={has_cars}, car_ratio={car_ratio:.2f}")
            return result

        finally:
            cap.release()

    def process_all_clips(self, input_dir: str = None, output_dir: str = None) -> Dict:
        """
        Process all video clips in the input directory and organize them by car detection results.
        This method is idempotent - files already processed will be skipped.
        Supports graceful shutdown with Ctrl-C.

        Args:
            input_dir: Directory containing video clips (defaults to config.STORAGE_DIR)
            output_dir: Directory to organize results (defaults to input_dir + "_organized")

        Returns:
            Dictionary with processing results
        """
        # Setup graceful shutdown
        self.shutdown_requested = False

        def signal_handler(signum, frame):
            self.logger.info("Shutdown signal received. Saving progress and shutting down gracefully...")
            self.shutdown_requested = True

        # Register signal handlers
        original_sigint = signal.signal(signal.SIGINT, signal_handler)
        original_sigterm = signal.signal(signal.SIGTERM, signal_handler)

        try:
            return self._process_all_clips_internal(input_dir, output_dir)
        finally:
            # Restore original signal handlers
            signal.signal(signal.SIGINT, original_sigint)
            signal.signal(signal.SIGTERM, original_sigterm)

    def _process_all_clips_internal(self, input_dir: str = None, output_dir: str = None) -> Dict:
        """
        Internal implementation of process_all_clips with database storage
        """
        if input_dir is None:
            input_dir = config.STORAGE_DIR

        # Find all video files in input directory
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        input_video_files = []

        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                input_video_files.append(os.path.join(input_dir, file))

        if not input_video_files:
            self.logger.info("No video files found in input directory")
            stats = self.db.get_statistics()
            return {
                "total_clips": stats['total_clips'],
                "with_cars": stats['with_cars'],
                "no_cars": stats['without_cars'],
                "errors": stats['errors'],
                "detection_method": f"yolov8{self.model_size}",
                "confidence_threshold": self.confidence_threshold,
                "status": "no_files_found"
            }

        # Get unprocessed files
        if self.force:
            files_to_process = input_video_files
            self.logger.info("Force mode enabled - will process all files")
        else:
            files_to_process = self.db.get_unprocessed_files(input_video_files)
            self.logger.info(f"Found {len(input_video_files)} video files in input directory")
            self.logger.info(f"Already processed: {len(input_video_files) - len(files_to_process)} files")
            self.logger.info(f"Files to process: {len(files_to_process)} files")

        if not files_to_process and not self.force:
            self.logger.info("No new files to process!")
            stats = self.db.get_statistics()
            return {
                "total_clips": stats['total_clips'],
                "with_cars": stats['with_cars'],
                "no_cars": stats['without_cars'],
                "errors": stats['errors'],
                "detection_method": f"yolov8{self.model_size}",
                "confidence_threshold": self.confidence_threshold,
                "status": "no_new_files_to_process"
            }

        # Process each video file
        newly_processed = 0
        errors = 0
        interrupted = False

        for i, video_path in enumerate(files_to_process):
            # Check for shutdown request
            if self.shutdown_requested:
                self.logger.info(f"Processing interrupted at file {i+1}/{len(files_to_process)}: {os.path.basename(video_path)}")
                interrupted = True
                break

            self.logger.info(f"Processing {i+1}/{len(files_to_process)}: {os.path.basename(video_path)}")

            try:
                analysis = self.analyze_video_clip(video_path)

                if "error" in analysis:
                    errors += 1
                    self.logger.error(f"Error processing {video_path}: {analysis['error']}")
                    # Save error result to database
                    self.db.save_analysis_result(analysis)
                    continue

                # Save analysis result to database
                if self.db.save_analysis_result(analysis):
                    newly_processed += 1
                    self.logger.info(f"Analysis complete for {os.path.basename(video_path)}: has_cars={analysis['has_cars']}")
                else:
                    errors += 1
                    self.logger.error(f"Failed to save analysis result for {video_path}")

            except Exception as e:
                errors += 1
                self.logger.error(f"Exception processing {video_path}: {e}")

        # Get final statistics
        stats = self.db.get_statistics()

        results = {
            "total_clips": stats['total_clips'],
            "with_cars": stats['with_cars'],
            "no_cars": stats['without_cars'],
            "errors": stats['errors'],
            "detection_method": f"yolov8{self.model_size}",
            "confidence_threshold": self.confidence_threshold,
            "newly_processed": newly_processed,
            "interrupted": interrupted
        }

        if interrupted:
            self.logger.info(f"Processing interrupted. Processed {newly_processed} new files.")
        else:
            self.logger.info(f"Processing complete. Processed {newly_processed} new files.")

        self.logger.info(f"Summary: {stats['with_cars']} clips with cars, {stats['without_cars']} clips without cars")
        if newly_processed > 0:
            self.logger.info(f"Newly processed: {newly_processed} clips")

        return results

    def create_summary_report(self, results: Dict) -> str:
        """
        Create a human-readable summary report

        Args:
            results: Results from process_all_clips

        Returns:
            Formatted summary string
        """
        # Check if this was an idempotent run or interrupted
        status_info = ""
        if results.get("status") == "no_new_files_to_process":
            status_info = "\nStatus: No new files to process (idempotent run)"
        elif results.get("interrupted", False):
            status_info = f"\nStatus: Processing was interrupted (Ctrl-C). Progress saved to database."
        elif results.get("newly_processed", 0) > 0:
            status_info = f"\nNewly processed: {results['newly_processed']} clips"

        summary = f"""
YOLOv8 Car Detection Analysis Summary
====================================

Detection Method: {results.get('detection_method', 'Unknown')}
Confidence Threshold: {results.get('confidence_threshold', 'Unknown')}

Total clips in database: {results['total_clips']}
Clips with cars: {results['with_cars']}
Clips without cars: {results['no_cars']}
Errors: {results['errors']}{status_info}

Success rate: {((results['with_cars'] + results['no_cars']) / results['total_clips'] * 100):.1f}%

Manual Review Required:
- Review {results['with_cars']} clips (files remain in original location)
- These clips likely contain cars and need driver/distraction analysis

Clips can be safely ignored:
- {results['no_cars']} clips (files remain in original location)
- These clips don't contain cars and can be deleted or ignored

Database Information:
- Results stored in: {config.DATABASE_PATH}
- System is idempotent - re-running will only process new files
- Supports graceful shutdown with Ctrl-C - progress is saved automatically
- Files are not moved - analysis results are stored in database

Performance Notes:
- Using YOLOv8{self.model_size} model for detection
- Confidence threshold: {self.confidence_threshold}
- Minimum frames with cars: {self.min_car_frames}
"""
        return summary