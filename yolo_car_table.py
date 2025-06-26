#!/usr/bin/env python3
"""
Script to analyze all clips in recorded_clips/ using YOLOv8 and print a table of car detection results to the console.
"""

import os
import logging
from yolo_car_detector import YOLOCarDetector
import config


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('yolo_car_detection.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main function to run YOLO car detection on all clips"""
    setup_logging()
    logger = logging.getLogger(__name__)

    input_dir = config.STORAGE_DIR
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    print(f"Initializing YOLOv8 car detector...")
    print("Note: First run will download the YOLOv8n model (~6MB)")

    # Initialize YOLO detector with nano model for speed
    detector = YOLOCarDetector(model_size='n')

    results = []

    print(f"\nAnalyzing {len(video_files)} video clips in '{input_dir}' using YOLOv8n...")
    print(f"{'Clip Name':40} | {'Has Car':7} | {'Car Ratio':8} | {'Frames':6} | {'Method':8}")
    print("-" * 80)

    for i, filename in enumerate(sorted(video_files)):
        path = os.path.join(input_dir, filename)
        print(f"Processing {i+1}/{len(video_files)}: {filename}")

        analysis = detector.analyze_video_clip(path, sample_frames=5)

        if "error" in analysis:
            has_car = False
            car_ratio = 0.0
            frames = 0
            method = "error"
        else:
            has_car = analysis.get('has_cars', False)
            car_ratio = analysis.get('car_ratio', 0)
            frames = analysis.get('frames_analyzed', 0)
            method = analysis.get('detection_method', 'n/a')

        results.append((filename, has_car, car_ratio, frames, method))
        print(f"{filename:40} | {str(has_car):7} | {car_ratio:8.2f} | {frames:6} | {method:8}")

    # Print summary
    with_cars = sum(1 for _, has_car, _, _, _ in results if has_car)
    without_cars = len(results) - with_cars

    print("\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"Total clips: {len(results)}")
    print(f"Clips with cars: {with_cars}")
    print(f"Clips without cars: {without_cars}")
    print(f"Detection method: YOLOv8n")
    print(f"Manual review required: {with_cars} clips")
    print("=" * 80)


if __name__ == "__main__":
    main()