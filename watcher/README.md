# Watcher - Recording & Motion Detection

The **Watcher** is the vigilant recording side of the Distracted Driving Detector system. It runs on a Raspberry Pi and continuously monitors for motion, automatically recording video clips when activity is detected.

## Overview

The Watcher system:
- **Monitors** the road continuously during specified hours
- **Detects** motion using computer vision
- **Records** video clips when motion is detected
- **Manages** storage and cleanup automatically
- **Provides** tools for viewing and debugging recordings

## Quick Start

### Hardware Setup
- Raspberry Pi 4 Model B (4GB+ recommended)
- Global Shutter Camera or compatible camera module
- Adequate storage (SD card or external drive)

### Installation

```bash
# Run the automated setup script
./setup.sh

# Start the watcher
python3 main.py
```

The setup script will:
- Install system dependencies (picamera2, opencv, numpy, etc.)
- Test the installation
- Set up storage directories

## Configuration

Edit `config.py` to customize the system:

```python
# Recording schedule
RECORDING_START_TIME = "08:00"  # 8 AM
RECORDING_END_TIME = "18:00"    # 6 PM

# Motion detection sensitivity
MOTION_THRESHOLD = 80           # Higher = less sensitive
MIN_MOTION_AREA = 1500          # Minimum area to trigger

# Storage settings
STORAGE_DIR = "recorded_clips"
CLIP_RETENTION_DAYS = 7
```

## Core Components

### `main.py`
The main application that coordinates motion detection and recording.

### `motion_detector.py`
Handles motion detection using frame differencing and contour analysis.

### `video_recorder.py`
Manages video recording, encoding, and file management.

### `camera_streamer.py`
Provides camera interface and frame capture functionality.

### `config.py`
Central configuration for all recording parameters.

### `setup.sh`
Automated installation script that handles all dependencies.

## Testing

```bash
# Test motion detection
python3 test_motion_detection.py

# Test camera functionality
python3 test_picamera2.py

# Debug motion detection
python3 debug_motion.py
```

## Camera Streaming

For remote viewing and camera setup:

```bash
# Start camera stream (accessible via web browser)
python3 camera_streamer.py

# Access stream at: http://raspberrypi.local:8080
# Or: http://[your-pi-ip]:8080
```

The camera streamer provides:
- Real-time camera feed in web browser
- High resolution for camera calibration
- Auto-refresh functionality
- Useful for positioning and testing camera setup

## Viewing Recordings

```bash
# View all recorded clips
python3 view_clips.py

# View clips in a specific directory
python3 view_clips.py /path/to/clips
```

## File Transfer

To transfer recordings to the Inspector (analysis side):

```bash
# Manual transfer
scp -r user@raspberrypi.local:/home/user/ddd/watcher/recorded_clips/ ./inspector/

# Or use rsync for automated transfer
rsync -avz --remove-source-files \
  user@raspberrypi.local:/home/user/ddd/watcher/recorded_clips/ \
  ./inspector/
```

### Atomic File Operations

The watcher uses atomic file operations to prevent partial file transfers:

1. **Temporary Writing**: Files are first written to a `temp_clips/` directory
2. **Atomic Move**: Once writing is complete, files are atomically moved to `recorded_clips/`
3. **Clean Transfer**: Only complete files appear in the final storage location

This ensures that:
- No partial files are transferred to the inspector
- File transfers can happen immediately without delays
- Orphaned temporary files are automatically cleaned up

### Testing Atomic Operations

```bash
# Test the atomic file writing system
python3 test_atomic_writing.py
```

## Troubleshooting

### Installation Issues
- **Setup script fails**: Make sure you're not running as root, the script will use sudo when needed
- **Picamera2 not found**: Run `./setup.sh` to install system dependencies
- **Python packages not found**: Run `./setup.sh` to install all required system packages

### Camera Issues
- Check camera connections and permissions
- Verify `picamera2` installation with `python3 test_picamera2.py`
- Ensure camera is enabled in `raspi-config`

### Motion Detection Issues
- Adjust `MOTION_THRESHOLD` and `MIN_MOTION_AREA` in `config.py`
- Use `debug_motion.py` to visualize detection
- Check lighting conditions

### Storage Issues
- Monitor available space
- Adjust `CLIP_RETENTION_DAYS` for cleanup
- Consider external storage for large deployments

## Performance Notes

- Designed for lightweight operation on Raspberry Pi
- Efficient motion detection with minimal CPU usage
- Automatic cleanup prevents storage overflow
- Configurable recording windows reduce unnecessary processing

## Architecture

The Watcher follows a simple, reliable architecture:
1. **Motion Detection Loop** - Continuously monitors for activity
2. **Recording Manager** - Handles clip creation and storage
3. **Storage Manager** - Manages cleanup and organization
4. **Configuration System** - Centralized settings management

This design ensures the system can run continuously without manual intervention while maintaining good performance on limited hardware.

## Dependencies

### System Packages (installed via apt)
- `python3-picamera2` - Camera interface
- `python3-opencv` - Computer vision
- `python3-numpy` - Numerical computing
- `python3-dateutil` - Date/time utilities
- `python3-pil` - Image processing (Pillow)

**Note**: All dependencies are installed automatically by the setup script via the system package manager (apt). This is required due to externally managed environment restrictions on Raspberry Pi.