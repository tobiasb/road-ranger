#!/usr/bin/env python3
"""
Test script to demonstrate graceful shutdown functionality
"""

import time
import signal
import sys
import logging
from yolo_car_detector import YOLOCarDetector
import config


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Test graceful shutdown functionality"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Graceful Shutdown Test")
    logger.info("======================")
    logger.info("This test will simulate processing and demonstrate Ctrl-C handling.")
    logger.info("Press Ctrl-C after a few seconds to test graceful shutdown.")
    logger.info("")

    # Initialize detector
    detector = YOLOCarDetector(model_size='n')  # Use nano for speed

    # Simulate processing with delays
    logger.info("Starting simulated processing...")

    try:
        # This will trigger the graceful shutdown when Ctrl-C is pressed
        results = detector.process_all_clips()

        logger.info("Processing completed successfully!")
        logger.info(f"Results: {results}")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt caught in main - this should not happen if graceful shutdown works")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()