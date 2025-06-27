# Atomic File Operations for Reliable File Transfer

## Problem

The original system had a race condition where files could be transferred from the watcher to the inspector while they were still being written. This resulted in:

- **Partial files**: Incomplete video clips that couldn't be processed
- **Corrupted files**: Files with invalid MP4 headers
- **Transfer delays**: Need for artificial delays to ensure file completion
- **Processing errors**: Inspector failing to analyze incomplete files

## Solution: Two-Stage Atomic File Writing

### Overview

The solution implements atomic file operations on the watcher side:

1. **Temporary Writing**: Files are written to a `temp_clips/` directory
2. **Atomic Move**: Once writing is complete, files are moved to `recorded_clips/`
3. **Clean Transfer**: Only complete files appear in the final storage location

### Implementation Details

#### Configuration Changes

```python
# Added to watcher/config.py
TEMP_STORAGE_DIR = "temp_clips"  # Temporary directory for writing files
```

#### Video Recorder Changes

The `VideoRecorder.record_clip()` method now:

1. **Writes to temp directory**: Creates files in `temp_clips/` first
2. **Verifies completion**: Checks file size and existence
3. **Atomic move**: Uses `shutil.move()` for atomic file operation
4. **Error handling**: Cleans up temp files if move fails

#### Cleanup Improvements

- **Automatic cleanup**: Orphaned temp files older than 1 hour are removed
- **Periodic cleanup**: Integrated into the main cleanup routine
- **Manual cleanup**: Utility script for immediate cleanup

### Benefits

1. **No Partial Transfers**: Files only appear in final location when complete
2. **No Transfer Delays**: Removed 2-second delay from transfer script
3. **Reliable Processing**: Inspector receives only complete, valid files
4. **Automatic Recovery**: Orphaned temp files are automatically cleaned up
5. **Thread Safety**: Works correctly with concurrent recording operations

### File Flow

```
Motion Detection → Frame Collection → Temp File Writing → Atomic Move → Final Storage → Transfer Ready
```

### Testing

#### Basic Test (No OpenCV Required)
```bash
python3 test_atomic_logic.py
```

#### Full Test (Requires OpenCV on Raspberry Pi)
```bash
python3 test_atomic_writing.py
```

#### Cleanup Utility
```bash
python3 cleanup_temp_files.py
```

### Configuration

The system automatically creates both directories:
- `recorded_clips/` - Final storage location (transfer source)
- `temp_clips/` - Temporary writing location (not transferred)

### Transfer Script Changes

The `inspector/transfer_clips.sh` script no longer needs delays:

```bash
# Removed: sleep 2
# Added: Note about atomic operations
rsync -avz --progress --remove-source-files \
  "$WATCHER_HOST:$SOURCE_PATH/" \
  "$DEST_PATH/"
```

### Error Handling

- **Write failures**: Temp files are cleaned up automatically
- **Move failures**: Temp files are cleaned up, error logged
- **Orphaned files**: Automatically removed after 1 hour
- **Directory issues**: Both directories are created automatically

### Performance Impact

- **Minimal overhead**: Only one additional file operation per clip
- **No delays**: Transfer can happen immediately
- **Efficient cleanup**: Only old files are processed during cleanup
- **Atomic operations**: No risk of file corruption during move

## Migration

### For Existing Installations

1. **Update code**: Deploy the new watcher code
2. **Create directories**: Directories are created automatically on startup
3. **Clean up**: Run cleanup script to remove any existing issues
4. **Test**: Verify atomic operations work correctly

### Verification

After deployment, verify:

1. **Directories exist**: Both `recorded_clips/` and `temp_clips/` are created
2. **Temp directory is clean**: No files remain in temp directory after recording
3. **Transfer works**: Files transfer without delays or corruption
4. **Processing succeeds**: Inspector can process all transferred files

## Troubleshooting

### Common Issues

1. **Temp files not cleaned up**: Run `python3 cleanup_temp_files.py`
2. **Permission errors**: Ensure write permissions on both directories
3. **Disk space**: Monitor both temp and final directories
4. **Transfer failures**: Check that only complete files are in final directory

### Log Messages

Look for these log messages to verify operation:

```
✅ Successfully recorded: recorded_clips/motion_20231201_120000_10.0s.mp4
✅ Temp directory is clean
✅ All files properly moved to final location
```

## Conclusion

This solution provides a robust, efficient way to prevent partial file transfers while maintaining system performance and reliability. The atomic file operations ensure that only complete, valid files are available for transfer, eliminating the need for delays or complex file integrity checks.