"""
Configuration settings for the Watcher (recording side)
"""

# Time-based recording settings
RECORDING_START_TIME = "08:00"  # 8 AM
RECORDING_END_TIME = "18:00"    # 6 PM

# Camera settings
CAMERA_INDEX = 0  # Default camera (usually webcam)
FRAME_WIDTH = 1920  # Increased from 640 for higher quality
FRAME_HEIGHT = 1080  # Increased from 480 for higher quality
FPS = 60

# Motion detection settings
MOTION_THRESHOLD = 80  # Sensitivity threshold for motion detection (higher = less sensitive)
MIN_MOTION_AREA = 1500  # Minimum area (in pixels) to consider as motion (higher = less sensitive)
MOTION_DETECTION_INTERVAL = 0.1  # Check for motion every 100ms
MOTION_PERSISTENCE_FRAMES = 1  # Number of frames motion must persist to trigger recording
MOTION_COOLDOWN_FRAMES = 2  # Number of frames to wait after motion stops before allowing new detection

# Recording settings
CLIP_DURATION = 10  # Duration of each recorded clip in seconds
PRE_MOTION_BUFFER = 2  # Seconds to record before motion is detected
POST_MOTION_BUFFER = 3  # Seconds to record after motion stops
MAX_CLIP_DURATION = 30  # Maximum duration of a single clip in seconds
FORCE_STOP_AFTER_MOTION = 5  # Force stop recording after this many seconds of no motion persistence

# Storage settings
STORAGE_DIR = "recorded_clips"
TEMP_STORAGE_DIR = "temp_clips"  # Temporary directory for writing files before moving to final location
CLIP_FORMAT = "mp4"
CODEC = "avc1"
MAX_STORAGE_GB = 10  # Maximum storage usage in GB
CLEANUP_OLD_CLIPS = True  # Whether to automatically delete old clips
CLIP_RETENTION_DAYS = 7  # How many days to keep clips

# File naming
CLIP_NAME_FORMAT = "motion_{timestamp}_{duration}s"

# Logging settings
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "motion_detector.log"