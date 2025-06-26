#!/usr/bin/env python3
"""
Main script to run YOLOv8 car detection on video clips
"""

import os
import sys
import logging
import signal
import argparse
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


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutdown signal received. Exiting gracefully...")
    sys.exit(0)


def main():
    """Main function to run car detection on all clips"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description='Run YOLOv8 car detection on video clips')
    parser.add_argument('--model-size', choices=['n', 's', 'm', 'l', 'x'], default=config.MODEL_SIZE,
                       help=f'YOLO model size (default: {config.MODEL_SIZE})')
    parser.add_argument('--source-dir', type=str, default=config.STORAGE_DIR,
                       help=f'Source directory containing video clips (default: {config.STORAGE_DIR})')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of files even if they have already been analyzed')
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting YOLOv8 car detection analysis using model size: {args.model_size}")
    logger.info(f"Source directory: {args.source_dir}")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info("Press Ctrl-C to stop processing gracefully (progress will be saved to database)")

    # Check if input directory exists
    if not os.path.exists(args.source_dir):
        logger.error(f"Source directory {args.source_dir} does not exist!")
        sys.exit(1)

    # Check if there are any video files
    video_files = [f for f in os.listdir(args.source_dir)
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        logger.warning(f"No video files found in {args.source_dir}")
        sys.exit(0)

    # Check for duplicate filenames in the source directory
    filename_counts = {}
    for video_file in video_files:
        filename_counts[video_file] = filename_counts.get(video_file, 0) + 1

    duplicates = [filename for filename, count in filename_counts.items() if count > 1]
    if duplicates:
        logger.warning(f"Found {len(duplicates)} duplicate filenames in source directory:")
        for duplicate in duplicates:
            logger.warning(f"  - {duplicate} (appears {filename_counts[duplicate]} times)")
        logger.warning("This could cause issues during processing. Consider removing duplicates.")

    logger.info(f"Found {len(video_files)} video files to analyze")

    # Initialize YOLO car detector
    detector = YOLOCarDetector(model_size=args.model_size, force=args.force)

    # Process all clips
    try:
        results = detector.process_all_clips(input_dir=args.source_dir)

        # Print summary to console
        summary = detector.create_summary_report(results)
        print(summary)

        logger.info(f"Analysis results saved to database: {config.DATABASE_PATH}")

        if results.get("interrupted", False):
            logger.info("Processing was interrupted but progress was saved to database. You can resume by running the script again.")
        else:
            logger.info("Car detection analysis complete!")

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user (Ctrl-C). Progress should have been saved to database.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during car detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()