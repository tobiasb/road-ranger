#!/usr/bin/env python3
"""
Script to display car detection results from database in a table format
"""

import os
import argparse
from database import CarDetectionDB
import config


def main():
    parser = argparse.ArgumentParser(description='Display car detection results from database')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of results to display')
    parser.add_argument('--filter', choices=['all', 'cars', 'no_cars', 'distracted', 'not_distracted', 'unanalyzed_distraction'], default='all',
                       help='Filter results (default: all)')
    args = parser.parse_args()

    # Initialize database
    db = CarDetectionDB(config.DATABASE_PATH)

    # Get statistics
    stats = db.get_statistics()

    if stats['total_clips'] == 0:
        print("No clips found in database!")
        print("Please run car detection first using: pipenv run python run_car_detection.py")
        return

    # Get clips based on filter
    if args.filter == 'cars':
        clips = db.get_car_clips(limit=args.limit)
        title = "Clips WITH Cars"
    elif args.filter == 'no_cars':
        clips = db.get_no_car_clips(limit=args.limit)
        title = "Clips WITHOUT Cars"
    elif args.filter == 'distracted':
        clips = db.get_distracted_clips(limit=args.limit)
        title = "Clips with DISTRACTED Drivers"
    elif args.filter == 'not_distracted':
        clips = db.get_not_distracted_clips(limit=args.limit)
        title = "Clips with NOT DISTRACTED Drivers"
    elif args.filter == 'unanalyzed_distraction':
        clips = db.get_unanalyzed_distraction_clips(limit=args.limit)
        title = "Clips Needing Distraction Analysis"
    else:
        clips = db.get_all_analyses(limit=args.limit)
        title = "All Clips"

    if not clips:
        print(f"No clips found for filter: {args.filter}")
        return

    print(f"Car Detection Results - {title}")
    print("=" * 100)
    print(f"Database: {config.DATABASE_PATH}")
    print(f"Total clips in database: {stats['total_clips']}")
    print(f"With cars: {stats['with_cars']}, Without cars: {stats['without_cars']}, Errors: {stats['errors']}")
    print(f"Distracted: {stats['distracted']}, Not distracted: {stats['not_distracted']}, Unanalyzed: {stats['unanalyzed_distraction']}")
    print()
    print(f"{'Filename':<35} | {'Has Car':<7} | {'Distracted':<10} | {'Car Ratio':<8} | {'Frames':<6} | {'Method':<10} | {'Processed':<20}")
    print("-" * 120)

    for clip in clips:
        filename = clip['filename'][:34] if clip['filename'] else 'Unknown'  # Truncate if too long
        is_car = "Yes" if clip['is_car'] else "No"
        is_distracted = clip.get('is_distracted')
        distraction_status = "Unknown"
        if is_distracted is True:
            distraction_status = "Yes"
        elif is_distracted is False:
            distraction_status = "No"
        car_ratio = clip.get('car_ratio', 0) or 0  # Handle None
        frames_analyzed = clip.get('frames_analyzed', 0) or 0  # Handle None
        detection_method = clip.get('detection_method', 'n/a') or 'n/a'  # Handle None
        processed_at = clip.get('processed_at', 'n/a') or 'n/a'  # Handle None

        # Format processed_at if it's a string
        if processed_at and isinstance(processed_at, str) and processed_at != 'n/a':
            processed_at = processed_at[:19]  # Show only date and time, not microseconds

        print(f"{filename:<35} | {is_car:<7} | {distraction_status:<10} | {car_ratio:<8.2f} | {frames_analyzed:<6} | {detection_method:<10} | {processed_at:<20}")

    print("\nDone.")


if __name__ == "__main__":
    main()