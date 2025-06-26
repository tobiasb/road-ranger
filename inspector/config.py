"""
Configuration settings for the Inspector (analysis side)
"""

# Input/Output settings
STORAGE_DIR = "recorded_clips"  # Directory containing video clips to analyze

# YOLO model settings
MODEL_SIZE = 'n'  # Model size ('n'=nano, 's'=small, 'm'=medium, 'l'=large)
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for car detection
SAMPLE_FRAMES = 10  # Number of frames to sample for analysis

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
