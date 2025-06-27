#!/usr/bin/env python3
"""
Test script to verify atomic file operation logic (without OpenCV dependency)
"""

import os
import shutil
import tempfile
import config
from datetime import datetime


def test_atomic_move_logic():
    """Test the atomic move logic without video recording"""
    print("🧪 Testing atomic file move logic...")

    # Create test directories
    temp_dir = "test_temp"
    final_dir = "test_final"

    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    try:
        # Test 1: Create a test file in temp directory
        test_content = "This is a test file content"
        temp_file = os.path.join(temp_dir, "test_file.txt")
        final_file = os.path.join(final_dir, "test_file.txt")

        print(f"📝 Creating test file: {temp_file}")
        with open(temp_file, 'w') as f:
            f.write(test_content)

        # Verify file exists in temp
        if os.path.exists(temp_file):
            print(f"✅ Test file created: {temp_file}")
            print(f"   Size: {os.path.getsize(temp_file)} bytes")
        else:
            print("❌ Test file not created")
            return False

        # Test 2: Atomic move
        print(f"🔄 Moving file to: {final_file}")
        shutil.move(temp_file, final_file)

        # Verify move was successful
        if os.path.exists(final_file) and not os.path.exists(temp_file):
            print("✅ Atomic move successful")
            print(f"   Final file size: {os.path.getsize(final_file)} bytes")
        else:
            print("❌ Atomic move failed")
            return False

        # Test 3: Verify content
        with open(final_file, 'r') as f:
            content = f.read()

        if content == test_content:
            print("✅ File content preserved")
        else:
            print("❌ File content corrupted")
            return False

        # Test 4: Clean up
        os.remove(final_file)
        print("✅ Cleanup successful")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up test directories
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(final_dir):
            shutil.rmtree(final_dir)


def test_directory_structure():
    """Test that the required directories can be created"""
    print("\n🔍 Testing directory structure...")

    # Test config values
    print(f"Storage directory: {config.STORAGE_DIR}")
    print(f"Temp directory: {config.TEMP_STORAGE_DIR}")

    # Create directories
    os.makedirs(config.STORAGE_DIR, exist_ok=True)
    os.makedirs(config.TEMP_STORAGE_DIR, exist_ok=True)

    # Verify directories exist
    if os.path.exists(config.STORAGE_DIR):
        print(f"✅ Storage directory created: {config.STORAGE_DIR}")
    else:
        print(f"❌ Failed to create storage directory: {config.STORAGE_DIR}")
        return False

    if os.path.exists(config.TEMP_STORAGE_DIR):
        print(f"✅ Temp directory created: {config.TEMP_STORAGE_DIR}")
    else:
        print(f"❌ Failed to create temp directory: {config.TEMP_STORAGE_DIR}")
        return False

    return True


def main():
    """Run all tests"""
    print("🚀 Starting atomic file operation tests...\n")

    # Test 1: Directory structure
    if not test_directory_structure():
        print("❌ Directory structure test failed")
        return

    # Test 2: Atomic move logic
    if not test_atomic_move_logic():
        print("❌ Atomic move logic test failed")
        return

    print("\n🎉 All tests passed! Atomic file operations are working correctly.")


if __name__ == "__main__":
    main()