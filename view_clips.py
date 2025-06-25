#!/usr/bin/env python3
"""
Script to view and manage recorded motion clips
"""

import os
import sys
import subprocess
from datetime import datetime
import config

def list_clips():
    """List all recorded clips with details"""
    if not os.path.exists(config.STORAGE_DIR):
        print(f"Storage directory '{config.STORAGE_DIR}' does not exist.")
        return

    clips = []
    for filename in os.listdir(config.STORAGE_DIR):
        if filename.endswith(f".{config.CLIP_FORMAT}"):
            filepath = os.path.join(config.STORAGE_DIR, filename)
            stat = os.stat(filepath)
            size_mb = stat.st_size / (1024 * 1024)
            created_time = datetime.fromtimestamp(stat.st_ctime)

            clips.append({
                'filename': filename,
                'filepath': filepath,
                'size_mb': size_mb,
                'created': created_time
            })

    if not clips:
        print("No clips found.")
        return

    # Sort by filename (ascending order)
    clips.sort(key=lambda x: x['filename'])

    print(f"Found {len(clips)} clips in '{config.STORAGE_DIR}':")
    print("-" * 80)
    print(f"{'Filename':<30} {'Size (MB)':<10} {'Created':<20}")
    print("-" * 80)

    total_size = 0
    for clip in clips:
        print(f"{clip['filename']:<30} {clip['size_mb']:<10.1f} {clip['created'].strftime('%Y-%m-%d %H:%M:%S'):<20}")
        total_size += clip['size_mb']

    print("-" * 80)
    print(f"Total: {len(clips)} clips, {total_size:.1f} MB")

def play_clip(filename):
    """Play a specific clip"""
    filepath = os.path.join(config.STORAGE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"Clip '{filename}' not found.")
        return

    print(f"Playing clip: {filename}")

    # Try to play with different video players
    players = ['vlc', 'mpv', 'mplayer', 'ffplay']

    for player in players:
        try:
            subprocess.run([player, filepath], check=True)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    print("No suitable video player found. Install one of: vlc, mpv, mplayer, or ffplay")

def delete_clip(filename):
    """Delete a specific clip"""
    filepath = os.path.join(config.STORAGE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"Clip '{filename}' not found.")
        return

    try:
        os.remove(filepath)
        print(f"Deleted clip: {filename}")
    except Exception as e:
        print(f"Error deleting clip: {e}")

def cleanup_old_clips():
    """Clean up old clips based on retention policy"""
    if not config.CLEANUP_OLD_CLIPS:
        print("Automatic cleanup is disabled in config.")
        return

    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=config.CLIP_RETENTION_DAYS)
    deleted_count = 0

    for filename in os.listdir(config.STORAGE_DIR):
        if filename.endswith(f".{config.CLIP_FORMAT}"):
            filepath = os.path.join(config.STORAGE_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))

            if file_time < cutoff_date:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"Deleted old clip: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")

    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old clips")
    else:
        print("No old clips to clean up")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python view_clips.py list                    - List all clips")
        print("  python view_clips.py play <filename>         - Play a specific clip")
        print("  python view_clips.py delete <filename>       - Delete a specific clip")
        print("  python view_clips.py cleanup                 - Clean up old clips")
        return

    command = sys.argv[1].lower()

    if command == "list":
        list_clips()
    elif command == "play" and len(sys.argv) > 2:
        play_clip(sys.argv[2])
    elif command == "delete" and len(sys.argv) > 2:
        delete_clip(sys.argv[2])
    elif command == "cleanup":
        cleanup_old_clips()
    else:
        print("Invalid command. Use 'list', 'play <filename>', 'delete <filename>', or 'cleanup'")

if __name__ == "__main__":
    main()