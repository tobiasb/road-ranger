#!/usr/bin/env python3
"""
Interactive viewer for clips containing detected cars
"""

import cv2
import os
import sys
import argparse
from pathlib import Path
import json
import config


def view_clips_in_directory(directory: str, title: str):
    """
    View all video clips in a directory

    Args:
        directory: Directory containing video clips
        title: Title to display
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist!")
        return

    video_files = [f for f in os.listdir(directory)
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        print(f"No video files found in {directory}")
        return

    print(f"\n{title}")
    print("=" * len(title))
    print(f"Found {len(video_files)} video files")

    for i, filename in enumerate(sorted(video_files)):
        filepath = os.path.join(directory, filename)

        print(f"\n{i+1}/{len(video_files)}: {filename}")
        print("Press 'q' to quit, 'n' for next, 'p' for previous, 'r' to replay")

        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            print(f"Could not open {filename}")
            continue

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        print(f"Duration: {duration:.1f}s, FPS: {fps:.1f}, Frames: {frame_count}")

        # Play video
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Display frame
            cv2.imshow(f"{title} - {filename}", frame)

            # Handle key presses
            key = cv2.waitKey(int(1000/fps)) & 0xFF
            if key == ord('q'):  # Quit
                cap.release()
                cv2.destroyAllWindows()
                return
            elif key == ord('n'):  # Next video
                break
            elif key == ord('p'):  # Previous video
                cap.release()
                cv2.destroyAllWindows()
                if i > 0:
                    # Restart with previous video
                    prev_filename = sorted(video_files)[i-1]
                    prev_filepath = os.path.join(directory, prev_filename)
                    cap = cv2.VideoCapture(prev_filepath)
                    if cap.isOpened():
                        print(f"Playing previous: {prev_filename}")
                        while True:
                            ret, frame = cap.read()
                            if not ret:
                                break
                            cv2.imshow(f"{title} - {prev_filename}", frame)
                            key = cv2.waitKey(int(1000/fps)) & 0xFF
                            if key in [ord('q'), ord('n'), ord('p')]:
                                break
                break
            elif key == ord('r'):  # Replay current video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

        cap.release()
        cv2.destroyAllWindows()

    print(f"\nFinished viewing all clips in {directory}")


def main():
    """Main function"""
    organized_dir = f"{config.STORAGE_DIR}_organized"

    if not os.path.exists(organized_dir):
        print(f"Organized directory {organized_dir} does not exist!")
        print("Please run car detection first using: pipenv run python run_car_detection.py")
        sys.exit(1)

    cars_dir = os.path.join(organized_dir, "with_cars")
    no_cars_dir = os.path.join(organized_dir, "no_cars")

    print("Car Clip Viewer")
    print("===============")
    print("1. View clips WITH cars (for driver analysis)")
    print("2. View clips WITHOUT cars (for verification)")
    print("3. View analysis results")
    print("4. Exit")

    while True:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            view_clips_in_directory(cars_dir, "Clips WITH Cars")
        elif choice == '2':
            view_clips_in_directory(no_cars_dir, "Clips WITHOUT Cars")
        elif choice == '3':
            results_file = os.path.join(organized_dir, "analysis_results.json")
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    results = json.load(f)

                print("\nAnalysis Results:")
                print(f"Total clips: {results['total_clips']}")
                print(f"With cars: {results['with_cars']}")
                print(f"Without cars: {results['no_cars']}")
                print(f"Errors: {results['errors']}")

                if results['processed_clips']:
                    print("\nDetailed results for first 5 clips:")
                    for i, clip in enumerate(results['processed_clips'][:5]):
                        filename = os.path.basename(clip['video_path'])
                        print(f"  {filename}: has_cars={clip['has_cars']}, car_ratio={clip['car_ratio']:.2f}")
            else:
                print("Analysis results file not found!")
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()