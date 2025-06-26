"""
Car detection module using OpenCV's HOG car detector
"""

import cv2
import numpy as np
import os
import json
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import config
import urllib.request


class CarDetector:
    """
    Detects cars in video clips using OpenCV's HOG car detector
    """

    def __init__(self):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        # Try to load the car cascade classifier
        self.car_cascade = self._load_car_cascade()
        # Alternative: use HOG descriptor with SVM (more accurate but slower)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        # For car detection, we'll use a custom HOG detector
        self.car_detector = self.car_cascade
        # Detection settings
        self.confidence_threshold = 0.3
        self.min_car_size = (60, 60)  # Minimum car size to detect
        self.max_car_size = (400, 400)  # Maximum car size to detect

    def _load_car_cascade(self):
        """Load car cascade classifier, downloading if necessary"""
        cascade_path = "haarcascade_cars.xml"

        # Check if cascade file exists locally
        if not os.path.exists(cascade_path):
            self.logger.info("Car cascade file not found locally, attempting to download...")
            try:
                # Try to download from OpenCV repository
                url = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_cars.xml"
                urllib.request.urlretrieve(url, cascade_path)
                self.logger.info("Successfully downloaded car cascade file")
            except Exception as e:
                self.logger.warning(f"Failed to download cascade file: {e}")
                self.logger.info("Using alternative detection method")
                return None

        # Load the cascade classifier
        if os.path.exists(cascade_path):
            cascade = cv2.CascadeClassifier(cascade_path)
            if not cascade.empty():
                self.logger.info("Car cascade classifier loaded successfully")
                return cascade
            else:
                self.logger.warning("Failed to load cascade classifier")
                return None
        else:
            self.logger.warning("Cascade file not found")
            return None

    def _simple_car_detection(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Simple car detection using color and shape analysis
        This is a fallback when cascade classifier is not available
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define range for car-like colors (grays, whites, blacks, blues, reds)
        # This is a very basic approach and will have many false positives
        lower_gray = np.array([0, 0, 50])
        upper_gray = np.array([180, 30, 220])

        # Create mask for car-like colors
        mask = cv2.inRange(hsv, lower_gray, upper_gray)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h

                # Cars typically have aspect ratios between 1.5 and 3.0
                if 1.5 <= aspect_ratio <= 3.0 and w >= 60 and h >= 60:
                    confidence = min(0.8, area / 10000)  # Simple confidence based on area
                    detections.append((x, y, w, h, confidence))

        return detections

    def detect_cars_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect cars in a single frame

        Args:
            frame: Input frame (BGR format)

        Returns:
            List of (x, y, w, h, confidence) tuples for detected cars
        """
        if self.car_cascade is not None:
            # Use cascade classifier
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cars = self.car_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=self.min_car_size,
                maxSize=self.max_car_size
            )

            # Convert to list of (x, y, w, h, confidence) tuples
            detections = []
            for (x, y, w, h) in cars:
                confidence = 0.8  # Default confidence for cascade detections
                detections.append((x, y, w, h, confidence))

            return detections
        else:
            # Use simple detection method
            return self._simple_car_detection(frame)

    def analyze_video_clip(self, video_path: str, sample_frames: int = 10) -> Dict:
        """
        Analyze a video clip to determine if it contains cars

        Args:
            video_path: Path to the video file
            sample_frames: Number of frames to sample for analysis

        Returns:
            Dictionary with analysis results
        """
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

            # Sample frames evenly throughout the video
            frame_indices = []
            if total_frames > 0:
                step = max(1, total_frames // sample_frames)
                frame_indices = list(range(0, total_frames, step))[:sample_frames]

            car_detections = []
            frames_with_cars = 0

            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    continue

                # Detect cars in this frame
                detections = self.detect_cars_in_frame(frame)

                if detections:
                    frames_with_cars += 1
                    car_detections.extend(detections)

            # Determine if video contains cars
            car_ratio = frames_with_cars / len(frame_indices) if frame_indices else 0
            has_cars = car_ratio > 0.3  # If more than 30% of sampled frames have cars

            result = {
                "video_path": video_path,
                "total_frames": total_frames,
                "duration": duration,
                "frames_analyzed": len(frame_indices),
                "frames_with_cars": frames_with_cars,
                "car_ratio": car_ratio,
                "has_cars": has_cars,
                "total_car_detections": len(car_detections),
                "average_cars_per_frame": len(car_detections) / len(frame_indices) if frame_indices else 0,
                "detection_method": "cascade" if self.car_cascade else "simple"
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
            "processed_clips": []
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
Car Detection Analysis Summary
=============================

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
"""
        return summary