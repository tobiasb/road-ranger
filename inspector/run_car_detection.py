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
    parser.add_argument('--force-reprocess', action='store_true',
                       help='Force reprocessing of all files (default: skip already processed files)')
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Starting YOLOv8 car detection analysis using model size: {args.model_size}")
    if args.force_reprocess:
        logger.info("Force reprocess mode enabled - will reprocess all files")
    logger.info("Press Ctrl-C to stop processing gracefully (progress will be saved)")

    # Check if input directory exists
    if not os.path.exists(config.STORAGE_DIR):
        logger.error(f"Input directory {config.STORAGE_DIR} does not exist!")
        sys.exit(1)

    # Check if there are any video files
    video_files = [f for f in os.listdir(config.STORAGE_DIR)
                   if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    if not video_files:
        logger.warning(f"No video files found in {config.STORAGE_DIR}")
        sys.exit(0)

    logger.info(f"Found {len(video_files)} video files to analyze")

    # Initialize YOLO car detector
    detector = YOLOCarDetector(model_size=args.model_size)

    # Process all clips
    try:
        if args.force_reprocess:
            # For force reprocess, we need to clear the organized directory first
            output_dir = f"{config.STORAGE_DIR}_organized"
            if os.path.exists(output_dir):
                logger.info(f"Clearing existing organized directory: {output_dir}")
                import shutil
                shutil.rmtree(output_dir)

        results = detector.process_all_clips()

        # Print summary to console
        summary = detector.create_summary_report(results)
        print(summary)

        # Save results to JSON file (analysis report)
        output_dir = f"{config.STORAGE_DIR}_organized"
        results_file = os.path.join(output_dir, "analysis_results.json")
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