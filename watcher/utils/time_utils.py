"""
Time utility functions for the motion detection system
"""

from datetime import datetime, time
from dateutil import parser


def is_within_recording_time(start_time_str: str, end_time_str: str) -> bool:
    """
    Check if current time is within the specified recording time window.

    Args:
        start_time_str: Start time in "HH:MM" format
        end_time_str: End time in "HH:MM" format

    Returns:
        True if current time is within the recording window, False otherwise
    """
    current_time = datetime.now().time()
    start_time = parser.parse(start_time_str).time()
    end_time = parser.parse(end_time_str).time()

    # Handle cases where recording period crosses midnight
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        # Recording period crosses midnight (e.g., 22:00 to 06:00)
        return current_time >= start_time or current_time <= end_time


def get_timestamp_string() -> str:
    """
    Get current timestamp as a string suitable for filenames.

    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")