#!/usr/bin/env python3
"""
Script to run car detection on all video clips using YOLOv8
"""

import logging
import sys
import os
import argparse
import signal
import config
from yolo_car_detector import YOLOCarDetector


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('car_detection.log'),
            logging.StreamHandler()
        ]
    )


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = logging.getLogger(__name__)
    logger.info("Shutdown signal received in main script. Exiting gracefully...")
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
    parser.add_argument('--dest-dir', type=str, default=None,
                       help='Destination directory for organized results (default: source_dir + "_organized")')
    parser.add_argument('--no-move', action='store_true',
                       help='Do not move files to organized directories (useful for evaluation)')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing of files even if they have already been analyzed')
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    # Set destination directory if not provided
    if args.dest_dir is None:
        args.dest_dir = f"{args.source_dir}_organized"

    logger.info(f"Starting YOLOv8 car detection analysis using model size: {args.model_size}")
    logger.info(f"Source directory: {args.source_dir}")
    logger.info(f"Destination directory: {args.dest_dir}")
    logger.info("Press Ctrl-C to stop processing gracefully (progress will be saved)")

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
    detector = YOLOCarDetector(model_size=args.model_size, no_move=args.no_move, force=args.force)

    # Track files processed in this run to prevent duplicates
    processed_in_this_run = set()

    # Process all clips
    try:
        results = detector.process_all_clips(input_dir=args.source_dir, output_dir=args.dest_dir)

        # Print summary to console
        summary = detector.create_summary_report(results)
        print(summary)

        # Save results to JSON file (analysis report)
        results_file = os.path.join(args.dest_dir, "analysis_results.json")
        logger.info(f"Analysis results saved to {results_file}")

        if results.get("interrupted", False):
            logger.info("Processing was interrupted but progress was saved. You can resume by running the script again.")
        else:
            logger.info("Car detection analysis complete!")

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user (Ctrl-C). Progress should have been saved.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during car detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()