"""
Configuration settings for the Inspector (analysis side)
"""

# Input/Output settings
STORAGE_DIR = "downloaded_clips"  # Directory containing video clips to analyze

# YOLO model settings - using larger model for better accuracy on beefier machine
MODEL_SIZE = 'm'  # Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge)
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for car detection
SAMPLE_FRAMES = 15  # Number of frames to sample for analysis (increased for better coverage)

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
