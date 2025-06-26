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
rsync -avz --progress --remove-source-files \
  "$WATCHER_HOST:$SOURCE_PATH/" \
  "$DEST_PATH/"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Transfer completed successfully!"
    echo "📁 Clips are now available in: $DEST_PATH"
    echo ""
    echo "🔍 Next steps:"
    echo "   pipenv run analyze-clips"
else
    echo ""
    echo "❌ Transfer failed!"
    echo "   Check your network connection and file permissions."
    exit 1
fi