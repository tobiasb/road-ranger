#!/usr/bin/env python3
"""
Test script to verify atomic file writing operations
"""

import os
import time
import threading
import config
from video_recorder import VideoRecorder
import numpy as np


def create_test_frames(num_frames=30):
    """Create test frames for recording"""
    frames = []
    for i in range(num_frames):
        # Create a simple test frame (640x480 RGB)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some visual content
        frame[:, :, 0] = (i * 8) % 256  # Varying blue channel
        frame[:, :, 1] = 128  # Fixed green channel
        frame[:, :, 2] = 255 - ((i * 8) % 256)  # Varying red channel
        frames.append(frame)
    return frames


def test_atomic_writing():
    """Test atomic file writing operations"""
    print("🧪 Testing atomic file writing operations...")

    # Ensure directories exist
    os.makedirs(config.STORAGE_DIR, exist_ok=True)
    os.makedirs(config.TEMP_STORAGE_DIR, exist_ok=True)

    # Create video recorder
    recorder = VideoRecorder()

    # Create test frames
    test_frames = create_test_frames(60)  # 1 second at 60fps

    print(f"📁 Storage directory: {config.STORAGE_DIR}")
    print(f"📁 Temp directory: {config.TEMP_STORAGE_DIR}")

    # Test 1: Basic recording
    print("\n🔍 Test 1: Basic atomic recording")
    result = recorder.record_clip(test_frames)
    if result:
        print(f"✅ Successfully recorded: {result}")
        if os.path.exists(result):
            size = os.path.getsize(result)
            print(f"   File size: {size} bytes")
        else:
            print("❌ File not found in final location")
    else:
        print("❌ Recording failed")

    # Test 2: Check temp directory is clean
    print("\n🔍 Test 2: Verify temp directory is clean")
    temp_files = [f for f in os.listdir(config.TEMP_STORAGE_DIR) if f.endswith(f'.{config.CLIP_FORMAT}')]
    if temp_files:
        print(f"⚠️  Found {len(temp_files)} files in temp directory (should be empty):")
        for f in temp_files:
            print(f"   - {f}")
    else:
        print("✅ Temp directory is clean")

    # Test 3: Concurrent recording simulation
    print("\n🔍 Test 3: Concurrent recording simulation")

    def record_clip_async(frames, clip_id):
        """Record a clip in a separate thread"""
        result = recorder.record_clip(frames)
        print(f"   Thread {clip_id}: {'✅' if result else '❌'} {os.path.basename(result) if result else 'Failed'}")

    # Start multiple recording threads
    threads = []
    for i in range(3):
        frames = create_test_frames(30 + i * 10)  # Different lengths
        thread = threading.Thread(target=record_clip_async, args=(frames, i+1))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check final state
    print("\n🔍 Final state check:")
    final_files = [f for f in os.listdir(config.STORAGE_DIR) if f.endswith(f'.{config.CLIP_FORMAT}')]
    temp_files = [f for f in os.listdir(config.TEMP_STORAGE_DIR) if f.endswith(f'.{config.CLIP_FORMAT}')]

    print(f"   Final storage: {len(final_files)} files")
    print(f"   Temp storage: {len(temp_files)} files")

    if temp_files:
        print("⚠️  Warning: Files remain in temp directory")
    else:
        print("✅ All files properly moved to final location")

    print("\n🎉 Atomic writing test completed!")


if __name__ == "__main__":
    test_atomic_writing()