#!/bin/bash

# Transfer clips from Watcher to Inspector
# Usage: ./transfer_clips.sh [watcher_host] [source_path] [dest_path]

# Default values
WATCHER_HOST=${1:-"tobi@raspberrypi-ddd.local"}
SOURCE_PATH=${2:-"/home/tobi/ddd/watcher/recorded_clips"}
DEST_PATH=${3:-"./downloaded_clips"}

echo "🔄 Transferring clips from Watcher to Inspector..."
echo "   From: $WATCHER_HOST:$SOURCE_PATH"
echo "   To: $DEST_PATH"
echo ""

# Create destination directory if it doesn't exist
mkdir -p "$DEST_PATH"

# Use rsync for efficient transfer with progress
# Note: Files are now written atomically on the watcher side, so no delay is needed
rsync -avz --progress --remove-source-files \
  "$WATCHER_HOST:$SOURCE_PATH/" \
  "$DEST_PATH/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Transfer completed successfully!"
    echo "📁 Clips are now available in: $DEST_PATH"

    # # Verify file integrity for MP4 files
    # echo "🔍 Verifying file integrity..."
    # corrupted_files=0
    # for file in "$DEST_PATH"/*.mp4; do
    #     if [ -f "$file" ]; then
    #         # Check if file has proper MP4 headers using ffprobe
    #         if ! ffprobe -v quiet -print_format json -show_format "$file" >/dev/null 2>&1; then
    #             echo "⚠️  Corrupted file detected: $(basename "$file")"
    #             corrupted_files=$((corrupted_files + 1))
    #             # Move corrupted file to a separate directory
    #             mkdir -p "$DEST_PATH/corrupted"
    #             mv "$file" "$DEST_PATH/corrupted/"
    #         fi
    #     fi
    # done

    # if [ $corrupted_files -eq 0 ]; then
    #     echo "✅ All files verified successfully!"
    # else
    #     echo "⚠️  Found $corrupted_files corrupted files (moved to corrupted/ subdirectory)"
    # fi

    echo ""
    echo "🔍 Next steps:"
    echo "   pipenv run analyze-clips"
else
    echo ""
    echo "❌ Transfer failed!"
    echo "   Check your network connection and file permissions."
    exit 1
fi