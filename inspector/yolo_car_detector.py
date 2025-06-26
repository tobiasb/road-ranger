"""
Car detection module using YOLOv8 for accurate object detection
"""

import cv2
import numpy as np
import os
import json
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import config
from ultralytics import YOLO


class YOLOCarDetector:
    """
    Detects cars in video clips using YOLOv8
    """

    def __init__(self, model_size: str = None):
        """
        Initialize YOLO car detector

        Args:
            model_size: Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large)
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

        self.logger.info(f"YOLO car detector initialized with model: yolov8{self.model_size}")

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
            return {"error": "File not found"}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.logger.error(f"Could not open video: {video_path}")
            return {"error": "Could not open video"}

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
        Process all video clips in the input directory and organize them by car detection results

        Args:
            input_dir: Directory containing video clips (defaults to config.STORAGE_DIR)
            output_dir: Directory to organize results (defaults to input_dir + "_organized")

        Returns:
            Dictionary with processing results
        """
        if input_dir is None:
            input_dir = config.STORAGE_DIR

        if output_dir is None:
            output_dir = f"{input_dir}_organized"

        # Create output directories
        cars_dir = os.path.join(output_dir, "with_cars")
        no_cars_dir = os.path.join(output_dir, "no_cars")
        os.makedirs(cars_dir, exist_ok=True)
        os.makedirs(no_cars_dir, exist_ok=True)

        # Find all video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        video_files = []

        for file in os.listdir(input_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(input_dir, file))

        self.logger.info(f"Found {len(video_files)} video files to process")

        results = {
            "total_clips": len(video_files),
            "with_cars": 0,
            "no_cars": 0,
            "errors": 0,
            "processed_clips": [],
            "detection_method": f"yolov8{self.model_size}",
            "confidence_threshold": self.confidence_threshold
        }

        # Process each video file
        for i, video_path in enumerate(video_files):
            self.logger.info(f"Processing {i+1}/{len(video_files)}: {os.path.basename(video_path)}")

            try:
                analysis = self.analyze_video_clip(video_path)

                if "error" in analysis:
                    results["errors"] += 1
                    self.logger.error(f"Error processing {video_path}: {analysis['error']}")
                    continue

                # Copy file to appropriate directory
                filename = os.path.basename(video_path)
                if analysis["has_cars"]:
                    dest_path = os.path.join(cars_dir, filename)
                    results["with_cars"] += 1
                else:
                    dest_path = os.path.join(no_cars_dir, filename)
                    results["no_cars"] += 1

                # Copy the file
                import shutil
                shutil.copy2(video_path, dest_path)

                # Store analysis results
                results["processed_clips"].append(analysis)

            except Exception as e:
                results["errors"] += 1
                self.logger.error(f"Exception processing {video_path}: {e}")

        # Save detailed results to JSON file
        results_file = os.path.join(output_dir, "analysis_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"Processing complete. Results saved to {results_file}")
        self.logger.info(f"Summary: {results['with_cars']} clips with cars, {results['no_cars']} clips without cars")

        return results

    def create_summary_report(self, results: Dict) -> str:
        """
        Create a human-readable summary report

        Args:
            results: Results from process_all_clips

        Returns:
            Formatted summary string
        """
        summary = f"""
YOLOv8 Car Detection Analysis Summary
====================================

Detection Method: {results.get('detection_method', 'Unknown')}
Confidence Threshold: {results.get('confidence_threshold', 'Unknown')}

Total clips processed: {results['total_clips']}
Clips with cars: {results['with_cars']}
Clips without cars: {results['no_cars']}
Errors: {results['errors']}

Success rate: {((results['with_cars'] + results['no_cars']) / results['total_clips'] * 100):.1f}%

Manual Review Required:
- Review {results['with_cars']} clips in the 'with_cars' directory
- These clips likely contain cars and need driver/distraction analysis

Clips can be safely ignored:
- {results['no_cars']} clips in the 'no_cars' directory
- These clips don't contain cars and can be deleted or ignored

Performance Notes:
- Using YOLOv8{self.model_size} model for detection
- Confidence threshold: {self.confidence_threshold}
- Minimum frames with cars: {self.min_car_frames}
"""
        return summary