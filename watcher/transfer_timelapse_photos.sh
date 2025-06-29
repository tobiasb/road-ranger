#!/bin/bash

# Transfer timelapse photos from Raspberry Pi
# Usage: ./transfer_timelapse_photos.sh [destination_folder]

# Default values
DEFAULT_DEST="timelapse_photos"
REMOTE_HOST="tobi@raspberrypi-ddd.local"
REMOTE_PATH="/home/tobi/ddd/watcher/timelapse_photos/"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [destination_folder]"
    echo ""
    echo "Arguments:"
    echo "  destination_folder  - Local directory to sync photos to (default: $DEFAULT_DEST)"
    echo ""
    echo "This will sync from: $REMOTE_HOST:$REMOTE_PATH"
    echo "Files will be removed from the Raspberry Pi after successful transfer."
    echo ""
    echo "Examples:"
    echo "  $0                          # Sync to default folder"
    echo "  $0 my_timelapse_photos      # Sync to custom folder"
    exit 0
}

# Check for help flag
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
fi

# Parse arguments
DEST_FOLDER="${1:-$DEFAULT_DEST}"

echo -e "${YELLOW}🔄 Transferring timelapse photos from Raspberry Pi...${NC}"
echo -e "${YELLOW}   From: $REMOTE_HOST:$REMOTE_PATH${NC}"
echo -e "${YELLOW}   To: $DEST_FOLDER${NC}"
echo ""

# Create local directory if it doesn't exist
mkdir -p "$DEST_FOLDER"

# Count files before transfer
echo "Checking remote files..."
REMOTE_COUNT=$(ssh "$REMOTE_HOST" "find $REMOTE_PATH -maxdepth 1 -name '*.jpg' -o -name '*.JPG' | wc -l" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to connect to Raspberry Pi${NC}"
    echo "Please check your connection and SSH access."
    exit 1
fi

if [ "$REMOTE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}No photos found on Raspberry Pi${NC}"
    exit 0
fi

echo -e "${GREEN}Found $REMOTE_COUNT photos to transfer${NC}"
echo ""

# Transfer files with rsync
rsync -avz --progress --remove-source-files \
    "$REMOTE_HOST:$REMOTE_PATH" \
    "$DEST_FOLDER/"

if [ $? -eq 0 ]; then
    # Count local files after transfer
    LOCAL_COUNT=$(find "$DEST_FOLDER" -maxdepth 1 -name "*.jpg" -o -name "*.JPG" | wc -l)

    echo ""
    echo -e "${GREEN}✅ Transfer completed successfully!${NC}"
    echo -e "${GREEN}   Photos transferred: $REMOTE_COUNT${NC}"
    echo -e "${GREEN}   Total photos in $DEST_FOLDER: $LOCAL_COUNT${NC}"
    echo ""
    echo -e "${YELLOW}Note: Original files have been removed from Raspberry Pi${NC}"
    echo ""
    echo "Next steps:"
    echo "  - Create timelapse: ./create_timelapse_video.sh $DEST_FOLDER"
    echo "  - View photos: ls -la $DEST_FOLDER"
else
    echo ""
    echo -e "${RED}✗ Transfer failed!${NC}"
    echo "Please check your network connection and file permissions."
    exit 1
fi