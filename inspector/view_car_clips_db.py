#!/usr/bin/env python3
"""
View car clips using database results
"""

import os
import sys
import json
import subprocess
import platform
from database import CarDetectionDB
import config


def get_video_player():
    """Get the appropriate video player command for the current platform"""
    system = platform.system().lower()

    if system == "darwin":  # macOS
        return "open"
    elif system == "linux":
        # Try common Linux video players
        for player in ["vlc", "mpv", "mplayer", "totem"]:
            try:
                subprocess.run([player, "--version"], capture_output=True, check=True)
                return player
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        return None
    elif system == "windows":
        return "start"
    else:
        return None


def play_video(video_path):
    """Play a video file using the system's default video player"""
    player = get_video_player()

    if not player:
        print(f"Could not find video player. Please open manually: {video_path}")
        return False

    try:
        if player == "open":  # macOS
            subprocess.run([player, video_path], check=True)
        elif player == "start":  # Windows
            subprocess.run([player, video_path], check=True)
        else:  # Linux
            subprocess.run([player, video_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error playing video: {e}")
        return False


def view_clips_in_list(clips, title):
    """View clips from a list of database results"""
    if not clips:
        print(f"No clips found for: {title}")
        return

    print(f"\n{title}")
    print("=" * 50)

    for i, clip in enumerate(clips, 1):
        filename = clip['filename'] or 'Unknown'
        file_path = clip['file_path'] or 'Unknown'
        car_ratio = clip.get('car_ratio', 0) or 0
        frames_analyzed = clip.get('frames_analyzed', 0) or 0
        frames_with_cars = clip.get('frames_with_cars', 0) or 0
        is_distracted = clip.get('is_distracted')

        # Format distraction status
        distraction_status = "Unknown"
        if is_distracted is True:
            distraction_status = "DISTRACTED"
        elif is_distracted is False:
            distraction_status = "Not Distracted"

        print(f"{i:3d}. {filename}")
        print(f"     Path: {file_path}")
        print(f"     Car ratio: {car_ratio:.2f} ({frames_with_cars}/{frames_analyzed} frames)")
        print(f"     Distraction: {distraction_status}")
        print()

    while True:
        try:
            choice = input(f"Enter clip number to play (1-{len(clips)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                break

            clip_num = int(choice)
            if 1 <= clip_num <= len(clips):
                selected_clip = clips[clip_num - 1]
                file_path = selected_clip['file_path']

                if os.path.exists(file_path):
                    print(f"Playing: {selected_clip['filename']}")
                    play_video(file_path)
                else:
                    print(f"File not found: {file_path}")
                    print("The file may have been moved or deleted.")
            else:
                print(f"Please enter a number between 1 and {len(clips)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


def main():
    """Main function"""
    # Initialize database
    db = CarDetectionDB(config.DATABASE_PATH)

    # Get statistics
    stats = db.get_statistics()

    if stats['total_clips'] == 0:
        print("No clips found in database!")
        print("Please run car detection first using: pipenv run python run_car_detection.py")
        sys.exit(1)

    print("Car Clip Viewer (Database)")
    print("==========================")
    print(f"Total clips in database: {stats['total_clips']}")
    print(f"Clips with cars: {stats['with_cars']}")
    print(f"Clips without cars: {stats['without_cars']}")
    print(f"Distracted drivers: {stats['distracted']}")
    print(f"Not distracted drivers: {stats['not_distracted']}")
    print(f"Unanalyzed for distraction: {stats['unanalyzed_distraction']}")
    print(f"Errors: {stats['errors']}")
    print()
    print("1. View clips WITH cars (for driver analysis)")
    print("2. View clips WITHOUT cars (for verification)")
    print("3. View DISTRACTED driver clips")
    print("4. View NOT DISTRACTED driver clips")
    print("5. View clips needing distraction analysis")
    print("6. View all clips")
    print("7. View database statistics")
    print("8. Exit")

    while True:
        choice = input("\nEnter your choice (1-8): ").strip()

        if choice == '1':
            car_clips = db.get_car_clips()
            view_clips_in_list(car_clips, "Clips WITH Cars")
        elif choice == '2':
            no_car_clips = db.get_no_car_clips()
            view_clips_in_list(no_car_clips, "Clips WITHOUT Cars")
        elif choice == '3':
            distracted_clips = db.get_distracted_clips()
            view_clips_in_list(distracted_clips, "Clips with DISTRACTED Drivers")
        elif choice == '4':
            not_distracted_clips = db.get_not_distracted_clips()
            view_clips_in_list(not_distracted_clips, "Clips with NOT DISTRACTED Drivers")
        elif choice == '5':
            unanalyzed_clips = db.get_unanalyzed_distraction_clips()
            view_clips_in_list(unanalyzed_clips, "Clips Needing Distraction Analysis")
        elif choice == '6':
            all_clips = db.get_all_analyses()
            view_clips_in_list(all_clips, "All Clips")
        elif choice == '7':
            print("\nDatabase Statistics:")
            print("====================")
            print(f"Total clips: {stats['total_clips']}")
            print(f"With cars: {stats['with_cars']}")
            print(f"Without cars: {stats['without_cars']}")
            print(f"Distracted drivers: {stats['distracted']}")
            print(f"Not distracted drivers: {stats['not_distracted']}")
            print(f"Unanalyzed for distraction: {stats['unanalyzed_distraction']}")
            print(f"Errors: {stats['errors']}")
            print(f"Success rate: {stats['success_rate']:.1f}%")
            print(f"Distraction analysis rate: {stats['distraction_analysis_rate']:.1f}%")
            print(f"Average car ratio: {stats['avg_car_ratio']:.2f}")
        elif choice == '8':
            print("Goodbye!")
            break
        else:
            print("Please enter a valid choice (1-8)")


if __name__ == "__main__":
    main()