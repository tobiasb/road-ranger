#!/bin/bash

# Script to run inspector server.sh in a loop with 5-second delay
# Usage: ./run_server_loop.sh

echo "Starting inspector server loop with 5-second delay between runs..."
echo "Press Ctrl+C to stop the loop"

# Function to handle graceful shutdown
cleanup() {
    echo -e "\nReceived interrupt signal. Stopping server loop..."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Counter for tracking runs
run_count=0

while true; do
    run_count=$((run_count + 1))
    echo -e "\n=== Run #$run_count ==="
    echo "Starting server.sh at $(date)"

    # Run the server script
    ./server.sh

    # Check if server.sh exited with an error
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "Warning: server.sh exited with code $exit_code"
    fi

    echo "Server stopped. Waiting 5 seconds before next run..."
    sleep 5
done