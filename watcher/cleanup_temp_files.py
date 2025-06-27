#!/usr/bin/env python3
"""
Utility script to clean up orphaned temporary files
"""

import os
import config
from datetime import datetime, timedelta


def cleanup_temp_files():
    """Clean up orphaned temporary files"""
    print("🧹 Cleaning up orphaned temporary files...")

    if not os.path.exists(config.TEMP_STORAGE_DIR):
        print(f"✅ Temp directory {config.TEMP_STORAGE_DIR} does not exist")
        return

    # Remove files older than 1 hour
    cutoff_time = datetime.now() - timedelta(hours=1)
    deleted_count = 0

    for filename in os.listdir(config.TEMP_STORAGE_DIR):
        if filename.endswith(f'.{config.CLIP_FORMAT}'):
            filepath = os.path.join(config.TEMP_STORAGE_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))

            if file_time < cutoff_time:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️  Deleted: {filename}")
                except Exception as e:
                    print(f"❌ Error deleting {filename}: {e}")

    if deleted_count == 0:
        print("✅ No orphaned temporary files found")
    else:
        print(f"✅ Cleaned up {deleted_count} orphaned temporary files")


if __name__ == "__main__":
    cleanup_temp_files()