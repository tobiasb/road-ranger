#!/bin/bash

# Transfer clips from Watcher to Inspector
# Usage: ./transfer_clips.sh [destination_folder]

# Default values
DEFAULT_DEST="downloaded_clips"
WATCHER_HOST="tobi@raspberrypi-ddd.local"
SOURCE_PATH="/home/tobi/ddd/watcher/recorded_clips"

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
    echo "  destination_folder  - Local directory to transfer clips to (default: $DEFAULT_DEST)"
    echo ""
    echo "This will transfer from: $WATCHER_HOST:$SOURCE_PATH"
    echo "Files will be removed from the Raspberry Pi after successful transfer."
    echo ""
    echo "Examples:"
    echo "  $0                     # Transfer to default folder"
    echo "  $0 my_clips            # Transfer to custom folder"
    exit 0
}

# Check for help flag
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
fi

# Parse arguments
DEST_PATH="${1:-$DEFAULT_DEST}"

echo -e "${YELLOW}🔄 Transferring clips from Watcher to Inspector...${NC}"
echo -e "${YELLOW}   From: $WATCHER_HOST:$SOURCE_PATH${NC}"
echo -e "${YELLOW}   To: $DEST_PATH${NC}"
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
    echo -e "${GREEN}✅ Transfer completed successfully!${NC}"
    echo -e "${GREEN}📁 Clips are now available in: $DEST_PATH${NC}"
    echo ""
    echo "🔍 Next steps:"
    echo "   pipenv run analyze-clips"
else
    echo ""
    echo -e "${RED}❌ Transfer failed!${NC}"
    echo "   Check your network connection and file permissions."
    exit 1
fi