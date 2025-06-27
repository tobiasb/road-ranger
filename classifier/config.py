"""
Configuration settings for the Classifier (manual classification side)
"""

# Flask settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True

# Database settings
DATABASE_PATH = "../inspector/car_detection.db"  # Path to the inspector's database

# Video settings
VIDEO_DIR = "../inspector/downloaded_clips"  # Directory containing video clips
MAX_VIDEOS_PER_PAGE = 20

# Classification options
CLASSIFICATION_OPTIONS = {
    'yes': True,      # Driver is distracted
    'no': False,      # Driver is not distracted
    'unknown': None   # Don't know/unsure
}

# UI settings
AUTO_PLAY_VIDEOS = False  # Whether to auto-play videos when loaded
SHOW_CLASSIFICATION_HISTORY = True  # Show previously classified clips