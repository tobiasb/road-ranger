# Inspector - ML Analysis & Car Detection

The **Inspector** is the intelligent analysis side of the Distracted Driving Detector system. It runs on a more powerful server and processes video clips to detect cars, analyze driver behavior, and identify potential distractions.

## Overview

The Inspector system:
- **Processes** video clips from the Watcher
- **Detects** cars using YOLOv8 object detection
- **Analyzes** driver behavior and patterns
- **Organizes** clips by detection results
- **Provides** tools for manual review and analysis

## Quick Start

### Hardware Requirements
- Ubuntu 20.04+ server with Python 3.9+
- 8GB+ RAM recommended for YOLOv8 processing
- GPU acceleration (optional but recommended)
- Adequate storage for video processing

### Installation

```bash
# Install pipenv
pip3 install --user pipenv

# Install ML dependencies
pipenv install

# Test YOLOv8 installation
pipenv run test-yolo

# Process clips from Watcher
pipenv run analyze-clips
```

## Core Components

### `yolo_car_detector.py`
Main YOLOv8-based car detection engine with configurable confidence thresholds.

### `yolo_car_table.py`
Analysis script that processes all clips and organizes them by detection results.

### `car_detector.py`
Alternative car detection implementation with different algorithms.

### `car_clip_table.py`
Utilities for organizing and managing car detection results.

### `view_car_clips.py`
Interactive viewer for clips containing detected cars.

### `run_car_detection.py`
Batch processing script for large clip collections.

## Usage

### Basic Car Detection

```bash
# Process all clips in recorded_clips directory
pipenv run analyze-clips

# Process specific directory
python yolo_car_table.py /path/to/clips

# Use specific YOLO model size
python yolo_car_detector.py --model-size s  # small model
```

### Advanced Analysis

```bash
# Run with custom confidence threshold
python yolo_car_detector.py --confidence 0.7

# Process with frame sampling
python yolo_car_detector.py --sample-frames 20

# Generate detailed reports
python yolo_car_table.py --detailed-report
```

### Viewing Results

```bash
# View clips with detected cars
python view_car_clips.py

# View clips in organized directories
python view_car_clips.py organized_clips/with_cars/

# Interactive clip browser
python view_car_clips.py --interactive
```

## Configuration

The Inspector uses the same `config.py` as the Watcher for shared settings, plus ML-specific configurations:

```python
# YOLO model settings
MODEL_SIZE = 'n'  # n=nano, s=small, m=medium, l=large
CONFIDENCE_THRESHOLD = 0.5
MIN_CAR_FRAMES = 2

# Processing settings
SAMPLE_FRAMES = 10
INPUT_SIZE = (640, 640)
```

## File Organization

After processing, clips are organized into:

```
organized_clips/
├── with_cars/          # Clips containing detected cars
│   ├── high_confidence/  # High confidence detections
│   └── low_confidence/   # Lower confidence detections
├── no_cars/            # Clips without cars
└── analysis_report.json # Detailed analysis results
```

## Performance Optimization

### Model Selection
- **YOLOv8n**: Fastest, good for real-time processing
- **YOLOv8s**: Balanced speed and accuracy
- **YOLOv8m**: Higher accuracy, slower processing
- **YOLOv8l**: Highest accuracy, slowest processing

### Processing Strategies
- **Frame Sampling**: Process every Nth frame for speed
- **Batch Processing**: Process multiple clips simultaneously
- **GPU Acceleration**: Use CUDA for faster inference
- **Memory Management**: Clear GPU memory between batches

## Development

### Testing

```bash
# Test YOLOv8 installation
pipenv run test-yolo

# Test car detection
pipenv run python test_car_detection.py

# Test with sample clips
python test_car_detection.py --sample-clips
```

### Adding New Features

1. **New Detection Models**: Add to `yolo_car_detector.py`
2. **Analysis Algorithms**: Extend `car_detector.py`
3. **Visualization Tools**: Create new viewer scripts
4. **Reporting**: Enhance `yolo_car_table.py`

## Troubleshooting

### YOLOv8 Issues
- Check CUDA installation for GPU acceleration
- Verify model download and caching
- Monitor memory usage during processing

### Performance Issues
- Reduce model size or frame sampling
- Use batch processing for large datasets
- Consider GPU acceleration

### File Transfer Issues
- Verify network connectivity to Watcher
- Check file permissions and paths
- Use rsync for reliable transfers

## Architecture

The Inspector follows a modular ML pipeline:
1. **Input Processing** - Load and validate video clips
2. **Detection Engine** - YOLOv8-based object detection
3. **Analysis Pipeline** - Process detection results
4. **Organization System** - Sort and categorize clips
5. **Reporting Engine** - Generate analysis reports

This design allows for easy extension with new detection models and analysis algorithms while maintaining good performance and reliability.

## Integration with Watcher

The Inspector is designed to work seamlessly with the Watcher:

1. **File Transfer**: Automatic or manual transfer of clips
2. **Shared Configuration**: Common settings in `config.py`
3. **Organized Output**: Results ready for manual review
4. **Feedback Loop**: Analysis results can inform Watcher settings

This separation allows each component to be optimized for its specific role while maintaining a cohesive system.