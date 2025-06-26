#!/usr/bin/env python3
"""
Script to analyze all clips in recorded_clips/ and print a table of car detection results to the console.
"""

import os
import argparse
from yolo_car_detector import YOLOCarDetector
import config


def main():
    parser = argparse.ArgumentParser(description='Analyze video clips with YOLOv8 car detection')
    parser.add_argument('--model-size', choices=['n', 's', 'm', 'l', 'x'], default=config.MODEL_SIZE,
                       help=f'YOLO model size (default: {config.MODEL_SIZE})')
    args = parser.parse_args()

    input_dir = config.STORAGE_DIR
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    detector = YOLOCarDetector(model_size=args.model_size)
    results = []

    print(f"Analyzing {len(video_files)} video clips in '{input_dir}' using YOLOv8{args.model_size}...\n")
    print(f"{'Clip Name':40} | {'Has Car':7} | {'Car Ratio':8} | {'Frames':6} | {'Method':12}")
    print("-" * 85)

    for filename in sorted(video_files):
        path = os.path.join(input_dir, filename)
        analysis = detector.analyze_video_clip(path, sample_frames=config.SAMPLE_FRAMES)
        has_car = analysis.get('has_cars', False)
        car_ratio = analysis.get('car_ratio', 0)
        frames = analysis.get('frames_analyzed', 0)
        method = analysis.get('detection_method', 'n/a')
        results.append((filename, has_car, car_ratio, frames, method))
        print(f"{filename:40} | {str(has_car):7} | {car_ratio:8.2f} | {frames:6} | {method:12}")

    print("\nDone.")

if __name__ == "__main__":
    main()