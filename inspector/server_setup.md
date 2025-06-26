# Server-Side Analysis Setup

This guide sets up the ML analysis environment on your Ubuntu server for car detection and other computer vision tasks.

## Prerequisites

- Ubuntu 20.04+ server
- Python 3.9+
- pip and pipenv installed
- Sufficient disk space (~2GB for models and dependencies)

## Installation

### 1. Install System Dependencies

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and development tools
sudo apt install python3 python3-pip python3-venv git curl

# Install pipenv
pip3 install --user pipenv
```

### 2. Clone or Transfer Project Files

```bash
# If cloning from git
git clone <your-repo-url>
cd ddd

# Or transfer files via SCP/SFTP
# scp -r /path/to/ddd user@server:/home/user/
```

### 3. Install Python Dependencies

```bash
# Install dependencies using pipenv
pipenv install

# Activate the virtual environment
pipenv shell
```

### 4. Test Installation

```bash
# Test YOLOv8 installation
pipenv run test-yolo

# Or manually
python test_yolo_installation.py
```

## Usage

### Basic Car Detection

```bash
# Analyze clips and display results in table
pipenv run analyze-clips

# Process all clips and organize them
pipenv run process-all
```

### Manual Commands

```bash
# Activate environment
pipenv shell

# Run car detection
python yolo_car_table.py

# Run full processing
python run_car_detection.py
```

## File Transfer from Raspberry Pi

### Option 1: SCP Transfer

```bash
# From your local machine, transfer clips from RPi to server
scp -r user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ /path/to/server/ddd/

# Or transfer specific files
scp user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/*.mp4 /path/to/server/ddd/recorded_clips/
```

### Option 2: Network Share

If you have a network share (NAS) accessible from both devices:

```bash
# On RPi: Copy clips to NAS
cp /home/tobi/ddd/recorded_clips/*.mp4 /mnt/nas/ddd_clips/

# On server: Copy from NAS
cp /mnt/nas/ddd_clips/*.mp4 /path/to/server/ddd/recorded_clips/
```

### Option 3: Automated Transfer Script

Create a script to automatically transfer new clips:

```bash
#!/bin/bash
# transfer_clips.sh
rsync -avz --remove-source-files \
  user@raspberrypi-ddd.local:/home/tobi/ddd/recorded_clips/ \
  /path/to/server/ddd/recorded_clips/
```

## Configuration

### Model Selection

Edit `yolo_car_detector.py` to change model size:

```python
# For speed (nano model)
detector = YOLOCarDetector(model_size='n')

# For better accuracy (small model)
detector = YOLOCarDetector(model_size='s')

# For best accuracy (medium model)
detector = YOLOCarDetector(model_size='m')
```

### Performance Tuning

```python
# In yolo_car_detector.py
self.confidence_threshold = 0.5  # Adjust for speed vs accuracy
self.min_car_frames = 2          # Minimum frames with cars
self.sample_rate = 3             # Process every Nth frame
```

## Troubleshooting

### Common Issues

**Out of memory:**
- Reduce model size (use 'n' instead of 's' or 'm')
- Increase sample_rate in detector
- Process clips in smaller batches

**Slow processing:**
- Use YOLOv8n model
- Increase sample_rate
- Reduce input image size

**Model download fails:**
```bash
# Manual download
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
mkdir -p ~/.cache/ultralytics/
mv yolov8n.pt ~/.cache/ultralytics/
```

### Performance Monitoring

```bash
# Monitor system resources
htop
nvidia-smi  # If using GPU

# Monitor disk space
df -h
du -sh recorded_clips/
```

## Next Steps

After car detection is working:

1. **Driver Detection**: Implement driver detection within car clips
2. **Distraction Detection**: Add distraction analysis
3. **Automation**: Set up automated processing pipeline
4. **Results Storage**: Implement database for results
5. **Web Interface**: Create web dashboard for results