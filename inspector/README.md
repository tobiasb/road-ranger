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

### Convenient Shortcuts

The Pipfile includes convenient scripts for common operations:

```bash
# Quick commands (no need to type 'python')
pipenv run test-yolo          # Test YOLO installation
pipenv run analyze-clips      # Run car detection (default model)
pipenv run view-clips         # View organized clips
pipenv run test-detection     # Run detection tests
pipenv run car-table          # Show analysis table
pipenv run force-reprocess    # Force reprocess all files
```

## Core Components

### `yolo_car_detector.py`
Main YOLOv8-based car detection engine with configurable confidence thresholds and model sizes.

### `yolo_car_table.py`
Analysis script that processes all clips and organizes them by detection results.

### `car_clip_table.py`
Utilities for organizing and managing car detection results with YOLOv8.

### `view_car_clips.py`
Interactive viewer for clips containing detected cars.

### `run_car_detection.py`
Batch processing script for large clip collections using YOLOv8.

## Usage

### Basic Car Detection

```bash
# Quick commands (recommended)
pipenv run analyze-clips                    # Process all clips (idempotent)
pipenv run car-table                        # Show analysis results table
pipenv run view-clips                       # View organized clips

# Full commands with options
pipenv run python run_car_detection.py --model-size m  # medium model (default)
pipenv run python yolo_car_table.py /path/to/clips    # specific directory
```

### Advanced Analysis

```bash
# Run with different model sizes
pipenv run python run_car_detection.py --model-size n  # nano (fastest)
pipenv run python run_car_detection.py --model-size s  # small
pipenv run python run_car_detection.py --model-size m  # medium (default)
pipenv run python run_car_detection.py --model-size l  # large
pipenv run python run_car_detection.py --model-size x  # xlarge (most accurate)

# Force reprocessing
pipenv run force-reprocess                  # Quick command
pipenv run python run_car_detection.py --force-reprocess  # Full command

# Testing
pipenv run test-detection                   # Run all tests
pipenv run python test_car_detection.py --model-size m   # Test specific model
```

### Idempotent Processing

The car detection system is **idempotent** - you can run it multiple times safely:

- **First run**: Processes all video files and moves them into `with_cars/` and `no_cars/` directories
- **Subsequent runs**: Only processes files remaining in the input directory (new files)
- **Force reprocess**: Use `--force-reprocess` to clear existing results and reprocess everything
- **Graceful shutdown**: Press Ctrl-C to stop processing - progress is automatically saved

This makes it safe to:
- Run the script multiple times as new clips arrive
- Interrupt and restart processing without losing progress
- Add new files to the input directory and reprocess only those
- Keep the input directory clean (processed files are moved out)
- Stop processing at any time with Ctrl-C and resume later

### Graceful Shutdown & Progress Saving

The system supports graceful shutdown with automatic progress saving:

- **Ctrl-C Support**: Press Ctrl-C at any time to stop processing gracefully
- **Progress Saving**: Results are saved every 10 files and when interrupted
- **Resume Capability**: Restart the script to continue from where you left off
- **No Data Loss**: Files already processed are preserved and won't be reprocessed

**Example workflow:**
```bash
# Start processing
pipenv run python run_car_detection.py --model-size m

# Processing starts...
# Press Ctrl-C to stop (progress is saved)

# Later, resume processing
pipenv run python run_car_detection.py --model-size m
# Only processes remaining files
```

### Viewing Results

```bash
# View clips with detected cars
pipenv run python view_car_clips.py

# View clips in organized directories
pipenv run python view_car_clips.py organized_clips/with_cars/

# Interactive clip browser
pipenv run python view_car_clips.py --interactive
```

## Configuration

The Inspector uses `config.py` for ML-specific configurations:

```python
# YOLO model settings - optimized for beefier machines
MODEL_SIZE = 'm'  # n=nano, s=small, m=medium, l=large, x=xlarge
CONFIDENCE_THRESHOLD = 0.5
MIN_CAR_FRAMES = 2

# Processing settings
SAMPLE_FRAMES = 15  # Increased for better coverage
INPUT_SIZE = (640, 640)
```

## File Organization

After processing, clips are organized into:

```
organized_clips/
├── with_cars/          # Clips containing detected cars
├── no_cars/            # Clips without cars
├── analysis_results.json # Detailed analysis results
└── summary_report.txt   # Human-readable summary
```

### Idempotent File Management

The system uses the organized directories as a signal for processed files:

- **Input directory** (`downloaded_clips/`): Contains original video files to be processed
- **Organized directories** (`with_cars/`, `no_cars/`): Contain processed files (moved from input)
- **Processing logic**: Files are moved from input directory to appropriate organized directory
- **Idempotent behavior**: Only files remaining in input directory are processed on subsequent runs

This approach ensures:
- **No duplicate processing**: Files moved to organized directories are considered processed
- **Clean input directory**: Processed files are moved out, leaving only new files
- **Easy verification**: You can see exactly which files have been processed
- **Safe re-runs**: Multiple executions produce the same results
- **Storage efficiency**: No duplicate files (moved, not copied)

## Performance Optimization

### Model Selection
- **YOLOv8n**: Fastest, good for real-time processing
- **YOLOv8s**: Balanced speed and accuracy
- **YOLOv8m**: Higher accuracy, good for analysis (default)
- **YOLOv8l**: Higher accuracy, slower processing
- **YOLOv8x**: Highest accuracy, slowest processing

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

# Test with specific model size
pipenv run python test_car_detection.py --model-size m
```

### Adding New Features

1. **New Detection Models**: Extend `yolo_car_detector.py`
2. **Analysis Algorithms**: Add new analysis methods
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