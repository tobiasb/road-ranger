#!/usr/bin/env python3
"""
Script to analyze all clips in recorded_clips/ and print a table of car detection results to the console.
"""

import os
from car_detector import CarDetector
import config


def main():
    input_dir = config.STORAGE_DIR
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    video_files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]

    if not video_files:
        print(f"No video files found in {input_dir}")
        return

    detector = CarDetector()
    results = []

    print(f"Analyzing {len(video_files)} video clips in '{input_dir}'...\n")
    print(f"{'Clip Name':40} | {'Has Car':7} | {'Car Ratio':8} | {'Frames':6} | {'Method':8}")
    print("-" * 80)

    for filename in sorted(video_files):
        path = os.path.join(input_dir, filename)
        analysis = detector.analyze_video_clip(path, sample_frames=config.SAMPLE_FRAMES)
        has_car = analysis.get('has_cars', False)
        car_ratio = analysis.get('car_ratio', 0)
        frames = analysis.get('frames_analyzed', 0)
        method = analysis.get('detection_method', 'n/a')
        results.append((filename, has_car, car_ratio, frames, method))
        print(f"{filename:40} | {str(has_car):7} | {car_ratio:8.2f} | {frames:6} | {method:8}")

    print("\nDone.")

if __name__ == "__main__":
    main()