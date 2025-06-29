#!/bin/bash

# Create timelapse video from JPG files
# Usage: ./create_timelapse_video.sh <input_folder> [fps] [output_file]

# Default values
DEFAULT_FPS=30
DEFAULT_OUTPUT="timelapse_video.mp4"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <input_folder> [fps] [output_file]"
    echo ""
    echo "Arguments:"
    echo "  input_folder  - Directory containing JPG files (required)"
    echo "  fps          - Frames per second (default: $DEFAULT_FPS)"
    echo "  output_file  - Output video filename (default: $DEFAULT_OUTPUT)"
    echo ""
    echo "Examples:"
    echo "  $0 timelapse_photos/"
    echo "  $0 timelapse_photos/ 24"
    echo "  $0 timelapse_photos/ 60 sunset_timelapse.mp4"
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Parse arguments
INPUT_FOLDER="$1"
FPS="${2:-$DEFAULT_FPS}"
OUTPUT_FILE="${3:-$DEFAULT_OUTPUT}"

# Check if input folder exists
if [ ! -d "$INPUT_FOLDER" ]; then
    echo -e "${RED}Error: Input folder '$INPUT_FOLDER' does not exist${NC}"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: ffmpeg is not installed${NC}"
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    exit 1
fi

# Count JPG files
JPG_COUNT=$(find "$INPUT_FOLDER" -maxdepth 1 -name "*.jpg" -o -name "*.JPG" | wc -l)

if [ "$JPG_COUNT" -eq 0 ]; then
    echo -e "${RED}Error: No JPG files found in '$INPUT_FOLDER'${NC}"
    exit 1
fi

echo -e "${GREEN}Found $JPG_COUNT JPG files in '$INPUT_FOLDER'${NC}"

# Calculate video duration
DURATION=$(echo "scale=2; $JPG_COUNT / $FPS" | bc)
echo -e "${YELLOW}Video duration will be approximately $DURATION seconds at $FPS fps${NC}"

# Create temporary directory for processing
TEMP_DIR=$(mktemp -d)
echo "Creating temporary directory: $TEMP_DIR"

# Copy and rename files with sequential numbering
echo "Preparing files for ffmpeg..."
COUNTER=1
find "$INPUT_FOLDER" -maxdepth 1 \( -name "*.jpg" -o -name "*.JPG" \) -print0 | sort -z | while IFS= read -r -d '' file; do
    # Create symlinks with sequential numbering that ffmpeg expects
    ln -s "$(realpath "$file")" "$TEMP_DIR/$(printf "%06d" $COUNTER).jpg"
    ((COUNTER++))
done

# Get dimensions of first image for video size
FIRST_IMAGE=$(find "$INPUT_FOLDER" -maxdepth 1 \( -name "*.jpg" -o -name "*.JPG" \) | sort | head -n1)
if [ -n "$FIRST_IMAGE" ]; then
    DIMENSIONS=$(identify -format "%wx%h" "$FIRST_IMAGE" 2>/dev/null || echo "")
    if [ -n "$DIMENSIONS" ]; then
        echo -e "${GREEN}Image dimensions: $DIMENSIONS${NC}"
    fi
fi

# Create video with ffmpeg
echo -e "${YELLOW}Creating timelapse video...${NC}"

# FFmpeg command with high quality settings
ffmpeg -framerate "$FPS" \
    -i "$TEMP_DIR/%06d.jpg" \
    -c:v libx264 \
    -preset slow \
    -crf 18 \
    -pix_fmt yuv420p \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
    -y \
    "$OUTPUT_FILE" 2>&1 | while read line; do
    # Show progress
    if [[ "$line" == *"time="* ]]; then
        echo -ne "\r$line"
    fi
done

# Check if video was created successfully
if [ -f "$OUTPUT_FILE" ]; then
    VIDEO_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo -e "\n${GREEN}✓ Timelapse video created successfully!${NC}"
    echo -e "${GREEN}  Output: $OUTPUT_FILE${NC}"
    echo -e "${GREEN}  Size: $VIDEO_SIZE${NC}"
    echo -e "${GREEN}  Duration: ~$DURATION seconds${NC}"
    echo -e "${GREEN}  Framerate: $FPS fps${NC}"

    # Optional: Show video info
    if command -v ffprobe &> /dev/null; then
        echo -e "\n${YELLOW}Video information:${NC}"
        ffprobe -v quiet -print_format json -show_streams "$OUTPUT_FILE" | \
            grep -E '"(width|height|r_frame_rate|duration|codec_name)"' | \
            sed 's/,$//' | sed 's/^ */  /'
    fi
else
    echo -e "\n${RED}✗ Failed to create timelapse video${NC}"
    exit 1
fi

# Cleanup
echo -e "\n${YELLOW}Cleaning up temporary files...${NC}"
rm -rf "$TEMP_DIR"

echo -e "${GREEN}Done!${NC}"

# Suggest next steps
echo -e "\n${YELLOW}Next steps:${NC}"
echo "  - Play the video: ffplay $OUTPUT_FILE"
echo "  - Or open with your default video player: open $OUTPUT_FILE (macOS) / xdg-open $OUTPUT_FILE (Linux)"