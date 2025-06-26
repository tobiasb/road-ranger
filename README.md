# Distracted Driving Detector (DDD)

A proof-of-concept system that uses a camera pointed at a road to detect when someone driving by is distracted.

## Project Overview

This project implements a multi-phase approach to distracted driving detection:

1. **Motion Detection & Recording** ✅ - Automatically records video clips when motion is detected (Watcher)
2. **Car Detection** ✅ - Filters clips to identify those containing cars (Inspector)
3. **Driver Detection** 🔄 - Identifies clips with visible drivers
4. **Distraction Detection** 🔄 - Analyzes driver behavior for signs of distraction

## Architecture

The system is split into two specialized components:

### 🕵️ Watcher (Recording Side)
- **Hardware**: Raspberry Pi 4 + Global Shutter Camera
- **Role**: Motion detection, video recording, storage
- **Dependencies**: Lightweight (OpenCV, Picamera2)
- **Location**: `watcher/` directory
- **Config**: `watcher/config.py` - Recording and motion detection settings

### 🔍 Inspector (Analysis Side)
- **Hardware**: Standard Ubuntu server with more CPU/memory
- **Role**: ML processing, car detection, analysis
- **Dependencies**: Heavy ML libraries (YOLOv8, PyTorch)
- **Location**: `inspector/` directory
- **Config**: `inspector/config.py` - ML and analysis settings

## Quick Start

### 1. Watcher Setup (Raspberry Pi)

```bash
cd watcher/

# Install system dependencies
sudo apt install python3-picamera2 python3-opencv python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure recording settings
nano config.py

# Start motion recording
python main.py
```

### 2. Inspector Setup (Server)

```bash
cd inspector/

# Install pipenv
pip3 install --user pipenv

# Install ML dependencies
pipenv install

# Configure analysis settings
nano config.py

# Test installation
pipenv run test-yolo

# Transfer clips from Watcher and analyze
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/watcher/recorded_clips/ ./
pipenv run analyze-clips
```

## Configuration

### Watcher Configuration (`watcher/config.py`)
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

### Inspector Configuration (`inspector/config.py`)
```python
# YOLO model settings
MODEL_SIZE = 'n'                # n=nano, s=small, m=medium, l=large
CONFIDENCE_THRESHOLD = 0.5      # Minimum confidence for detection

# Processing settings
SAMPLE_FRAMES = 10              # Frames to sample per video
INPUT_SIZE = (640, 640)         # YOLO input size
```

## File Transfer Options

### Option 1: Manual SCP
```bash
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/watcher/recorded_clips/ ./inspector/
```

### Option 2: Network Share
```bash
# Copy to NAS from Watcher
cp watcher/recorded_clips/*.mp4 /mnt/nas/ddd_clips/

# Copy from NAS to Inspector
cp /mnt/nas/ddd_clips/*.mp4 ./inspector/
```

### Option 3: Automated Script
```bash
# Use the provided transfer script
./transfer_clips.sh
```

## Usage

### Phase 1: Motion Recording (Watcher)
```bash
cd watcher/
python main.py
```

### Phase 2: Car Detection (Inspector)
```bash
cd inspector/
pipenv run analyze-clips
```

### Phase 3: Manual Review
Review clips in organized directories:
- `inspector/organized_clips/with_cars/` - Clips containing cars
- `inspector/organized_clips/no_cars/` - Clips without cars

## Performance Notes

### Watcher Optimization
- Lightweight dependencies only
- Efficient motion detection
- Automatic clip cleanup
- Minimal resource usage

### Inspector Optimization
- YOLOv8n model for speed
- Configurable confidence thresholds
- Frame sampling for efficiency
- Batch processing capabilities

## Development

### Testing Components

**Watcher:**
```bash
cd watcher/
python test_motion_detection.py
python test_picamera2.py
```

**Inspector:**
```bash
cd inspector/
pipenv run test-yolo
pipenv run python test_car_detection.py
```

### Adding Features
1. Keep Watcher side lightweight
2. Add ML features to Inspector side
3. Use file-based messaging between components
4. Test on actual hardware

## Troubleshooting

### Watcher Issues
- **Camera not detected**: Check connections and permissions
- **Motion detection issues**: Adjust thresholds in `watcher/config.py`
- **Storage full**: Enable cleanup in `watcher/config.py`

### Inspector Issues
- **YOLOv8 installation**: See `inspector/server_setup.md`
- **Memory issues**: Use smaller model or increase sampling
- **Transfer issues**: Check network connectivity

## Project Structure

```
ddd/
├── watcher/                    # Recording & Motion Detection
│   ├── main.py                # Motion recording (RPi)
│   ├── motion_detector.py     # Motion detection (RPi)
│   ├── video_recorder.py      # Video recording (RPi)
│   ├── config.py              # Watcher configuration
│   ├── requirements.txt       # RPi dependencies
│   ├── recorded_clips/        # Video storage
│   └── README.md              # Watcher documentation
├── inspector/                  # ML Analysis & Car Detection
│   ├── yolo_car_detector.py   # YOLOv8 detection (server)
│   ├── yolo_car_table.py      # Analysis script (server)
│   ├── config.py              # Inspector configuration
│   ├── Pipfile               # Server dependencies
│   ├── server_setup.md        # Server setup guide
│   └── README.md              # Inspector documentation
├── transfer_clips.sh          # File transfer utility
└── README.md                  # This file
```

## License

This project is for research and educational purposes.

## Contributing

1. Follow the lightweight Watcher / heavy Inspector architecture
2. Test on actual hardware
3. Update documentation in appropriate directories
4. Use file-based messaging between components

# Watcher (Raspberry Pi)
cd watcher/
python main.py

# Inspector (Server)
cd inspector/
pipenv run analyze-clips

# Transfer clips
./transfer_clips.sh

