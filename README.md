# Distracted Driving Detector (DDD)

A proof-of-concept system that uses a camera pointed at a road to detect when someone driving by is distracted.

## Project Overview

This project implements a multi-phase approach to distracted driving detection:

1. **Motion Detection & Recording** ✅ - Automatically records video clips when motion is detected (Raspberry Pi)
2. **Car Detection** ✅ - Filters clips to identify those containing cars (Server-side ML)
3. **Driver Detection** 🔄 - Identifies clips with visible drivers
4. **Distraction Detection** 🔄 - Analyzes driver behavior for signs of distraction

## Architecture

### Raspberry Pi (Recording Side)
- **Hardware**: Raspberry Pi 4 + Global Shutter Camera
- **Role**: Motion detection, video recording, storage
- **Dependencies**: Lightweight (OpenCV, Picamera2)
- **Files**: `main.py`, `motion_detector.py`, `video_recorder.py`

### Ubuntu Server (Analysis Side)
- **Hardware**: Standard Ubuntu server with more CPU/memory
- **Role**: ML processing, car detection, analysis
- **Dependencies**: Heavy ML libraries (YOLOv8, PyTorch)
- **Files**: `yolo_car_detector.py`, `yolo_car_table.py`

## Hardware Requirements

- **Raspberry Pi**: Pi 4 Model B/4GB + Global Shutter Camera
- **Server**: Ubuntu 20.04+ with Python 3.9+
- **Storage**: Home NAS for shared storage
- **Network**: Both devices on same network

## Quick Start

### 1. Raspberry Pi Setup (Recording)

```bash
# Install system dependencies
sudo apt install python3-picamera2 python3-opencv python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start motion recording
python main.py
```

### 2. Server Setup (Analysis)

```bash
# Install pipenv
pip3 install --user pipenv

# Install ML dependencies
pipenv install

# Test installation
pipenv run test-yolo

# Transfer clips from RPi and analyze
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ ./
pipenv run analyze-clips
```

## Detailed Setup

### Raspberry Pi Configuration

Edit `config.py` to adjust recording settings:

```python
# Recording times
RECORDING_START_TIME = "08:00"  # 8 AM
RECORDING_END_TIME = "18:00"    # 6 PM

# Motion detection
MOTION_THRESHOLD = 80
MIN_MOTION_AREA = 1500

# Storage
STORAGE_DIR = "recorded_clips"
CLIP_RETENTION_DAYS = 7
```

### Server Configuration

See `server_setup.md` for detailed server setup instructions.

## Usage

### Phase 1: Motion Recording (Raspberry Pi)
```bash
# Start recording system
python main.py
```

### Phase 2: Car Detection (Server)
```bash
# Transfer clips from RPi
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ ./

# Analyze with YOLOv8
pipenv run analyze-clips
```

### Phase 3: Manual Review
Review clips in organized directories:
- `recorded_clips_organized/with_cars/` - Clips containing cars
- `recorded_clips_organized/no_cars/` - Clips without cars

## File Transfer Options

### Option 1: Manual SCP
```bash
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ ./
```

### Option 2: Network Share
```bash
# Copy to NAS from RPi
cp recorded_clips/*.mp4 /mnt/nas/ddd_clips/

# Copy from NAS to server
cp /mnt/nas/ddd_clips/*.mp4 ./recorded_clips/
```

### Option 3: Automated Script
Create `transfer_clips.sh` for automatic transfer:
```bash
rsync -avz --remove-source-files \
  user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ \
  ./recorded_clips/
```

## Performance Notes

### Raspberry Pi Optimization
- Lightweight dependencies only
- Efficient motion detection
- Automatic clip cleanup
- Minimal resource usage

### Server Optimization
- YOLOv8n model for speed
- Configurable confidence thresholds
- Frame sampling for efficiency
- Batch processing capabilities

## Development

### Testing Components

**Raspberry Pi:**
```bash
# Test motion detection
python test_motion_detection.py

# Test camera
python test_picamera2.py
```

**Server:**
```bash
# Test YOLOv8
pipenv run test-yolo

# Test car detection
pipenv run analyze-clips
```

### Adding Features
1. Keep RPi side lightweight
2. Add ML features to server side
3. Use file-based messaging between components
4. Test on actual hardware

## Troubleshooting

### Raspberry Pi Issues
- **Camera not detected**: Check connections and permissions
- **Motion detection issues**: Adjust thresholds in `config.py`
- **Storage full**: Enable cleanup in `config.py`

### Server Issues
- **YOLOv8 installation**: See `server_setup.md`
- **Memory issues**: Use smaller model or increase sampling
- **Transfer issues**: Check network connectivity

## Project Structure

```
ddd/
├── main.py                 # Motion recording (RPi)
├── motion_detector.py      # Motion detection (RPi)
├── video_recorder.py       # Video recording (RPi)
├── config.py              # Configuration (shared)
├── requirements.txt       # RPi dependencies
├── Pipfile               # Server dependencies
├── yolo_car_detector.py   # YOLOv8 detection (server)
├── yolo_car_table.py      # Analysis script (server)
├── server_setup.md        # Server setup guide
├── recorded_clips/        # Video storage (shared)
└── README.md             # This file
```

## License

This project is for research and educational purposes.

## Contributing

1. Follow the lightweight RPi / heavy server architecture
2. Test on actual hardware
3. Update documentation
4. Use file-based messaging between components

