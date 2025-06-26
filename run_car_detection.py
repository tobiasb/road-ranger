#!/usr/bin/env python3
"""
Script to run car detection on all recorded video clips
"""

import logging
import sys
import os
from car_detector import CarDetector
import config


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


def main():
    """Main function to run car detection on all clips"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting car detection analysis...")

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

    # Initialize car detector
    detector = CarDetector()

    # Process all clips
    try:
        results = detector.process_all_clips()

        # Print summary
        summary = detector.create_summary_report(results)
        print(summary)

        # Save summary to file
        output_dir = f"{config.STORAGE_DIR}_organized"
        summary_file = os.path.join(output_dir, "summary_report.txt")
        with open(summary_file, 'w') as f:
            f.write(summary)

        logger.info(f"Summary report saved to {summary_file}")
        logger.info("Car detection analysis complete!")

    except Exception as e:
        logger.error(f"Error during car detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()