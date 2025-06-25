# Road Ranger

Distracted driving detection (DDD)

A proof-of-concept system for detecting distracted driving using a Raspberry Pi camera pointed at a road.

## Current Status: Motion Recording System

The system currently implements the first objective: **"Between certain times of the day, a camera records and stores clips of movement"**.

### Features

- **Time-based recording**: Only records during configured hours (default: 8 AM - 6 PM)
- **Motion detection**: Uses OpenCV background subtraction to detect movement
- **Raspberry Pi camera support**: Uses Picamera2 for the Raspberry Pi Global Shutter Camera
- **Automatic clip management**: Records clips when motion is detected and stops when motion ends
- **Smart clip duration**: Clips are automatically stopped when motion ends (typically 3-10 seconds)
- **Storage management**: Automatic cleanup of old clips based on retention policy
- **Configurable settings**: Adjustable motion sensitivity, clip duration, and storage settings
- **Clean logging**: Reduced verbose output with focused motion detection events

### Hardware Requirements

- Raspberry Pi 4 Model B (4GB recommended)
- Raspberry Pi Global Shutter Camera (6mm or 16mm lens)
- SD card with sufficient storage (or NAS for storage)

### Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup.sh
```

This will install all dependencies and set up the virtual environment automatically.

### Manual Setup

If you prefer to set up manually:

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-picamera2 python3-opencv python3-pip python3-venv python3-dateutil

# Create and activate virtual environment (required for externally managed environment)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

**Important Note**: For Picamera2 compatibility, the system now runs with system Python (`python3`) instead of the virtual environment. The virtual environment is still used for other dependencies.

### Configuration

Edit `config.py` to customize the system:

```python
# Recording hours (24-hour format)
RECORDING_START_TIME = "08:00"  # 8 AM
RECORDING_END_TIME = "18:00"    # 6 PM

# Motion detection sensitivity (tuned for stability)
MOTION_THRESHOLD = 80          # Higher = less sensitive (was 25)
MIN_MOTION_AREA = 1500         # Minimum area to trigger recording (was 500)
MOTION_PERSISTENCE_FRAMES = 1  # Frames motion must persist to trigger recording
MOTION_COOLDOWN_FRAMES = 2     # Frames to wait after motion stops

# Clip settings
CLIP_DURATION = 10             # Maximum seconds per clip
FORCE_STOP_AFTER_MOTION = 5    # Force stop after 5s of no motion
MAX_CLIP_DURATION = 30         # Maximum clip length

# Storage settings
STORAGE_DIR = "recorded_clips" # Where clips are saved
CLIP_RETENTION_DAYS = 7        # How long to keep clips
```

### Usage

#### 1. Test Motion Detection

First, test that motion detection works with your camera:

```bash
python3 test_motion_detection.py
```

This will show motion detection events without recording clips. Press Ctrl+C to stop.

For detailed motion detection debugging:

```bash
python3 debug_motion.py
```

#### 2. Run the Full System

Start the motion recording system:

```bash
python3 main.py
```

The system will:
- Only record during configured hours
- Detect motion using background subtraction
- Record clips when motion is detected
- Stop recording when motion stops (typically 3-10 seconds)
- Save clips with accurate duration in filename
- Clean logging output (no verbose Picamera2 debug messages)

#### 3. View Recorded Clips

List all recorded clips (sorted by filename):

```bash
python3 view_clips.py list
```

Play a specific clip:

```bash
python3 view_clips.py play motion_20250625_140352_6s.mp4
```

Delete a clip:

```bash
python3 view_clips.py delete motion_20250625_140352_6s.mp4
```

Clean up old clips:

```bash
python3 view_clips.py cleanup
```

#### 4. Camera Streaming (Optional)

For remote monitoring, you can stream the camera feed:

```bash
python3 camera_streamer.py
```

Then open `http://raspberrypi-ddd.local:8080` in your web browser.

### File Structure

```
ddd/
├── main.py                 # Main motion recording system
├── motion_detector.py      # Motion detection using OpenCV/Picamera2
├── video_recorder.py       # Video clip recording with accurate durations
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── setup.sh              # Automated setup script
├── test_motion_detection.py # Test motion detection
├── debug_motion.py        # Detailed motion detection debugging
├── view_clips.py          # View and manage recorded clips
├── camera_streamer.py     # HTTP camera stream
├── utils/
│   └── time_utils.py      # Time utility functions
├── venv/                  # Virtual environment (created during setup)
└── recorded_clips/        # Where motion clips are stored
```

### Recent Improvements

- **Stable motion detection**: Tuned parameters to reduce false positives while maintaining sensitivity
- **Accurate clip durations**: Filenames now show actual clip length (e.g., `6s.mp4` instead of `10s.mp4`)
- **Clean logging**: Reduced verbose Picamera2 debug output
- **Smart clip management**: Clips automatically stop when motion ends (typically 3-10 seconds)
- **Improved cooldown**: Better handling of motion start/stop events
- **Sorted clip listing**: Clips are now listed in chronological order by filename

### Troubleshooting

1. **"externally-managed-environment" error**: Use `python3` instead of `python` for main scripts
2. **"No module named 'dateutil'" error**: Install with `sudo apt install python3-dateutil`
3. **Camera not detected**: Make sure Picamera2 is installed and the camera is properly connected
4. **Too many false positives**: Increase `MOTION_THRESHOLD` or `MIN_MOTION_AREA` in config
5. **No motion detected**: Decrease `MOTION_THRESHOLD` or `MIN_MOTION_AREA`
6. **Storage full**: Enable `CLEANUP_OLD_CLIPS` or increase `CLIP_RETENTION_DAYS`
7. **Verbose logging**: Picamera2 debug messages are now filtered to INFO level

### Next Steps

This system provides the foundation for the distracted driving detection pipeline. The next objectives are:

1. **Car detection**: Identify clips that contain cars
2. **Driver detection**: Identify clips with cars that also show drivers
3. **Distraction detection**: Identify when drivers are distracted (looking at phone, etc.)

The recorded clips can be manually reviewed or processed with computer vision models for automated detection.

## Cursor Configuration

This project includes Cursor rules (`.cursor/rules`) to guide AI assistance with:
- project-specific coding patterns
- Architectural decisions
- Code organization
- Testing strategies

