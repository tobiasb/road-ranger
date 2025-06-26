#!/bin/bash

# Server script to run transfer_clips.sh and analyze-clips with error handling
# Designed to be run via cron job, ensuring only one instance runs at a time

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK_FILE="$SCRIPT_DIR/server.lock"
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Cleanup function
cleanup() {
    log "INFO" "🧹 Cleaning up..."
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
        log "INFO" "Lock file removed"
    fi
    if [[ -f "$PID_FILE" ]]; then
        rm -f "$PID_FILE"
        log "INFO" "PID file removed"
    fi
    log "INFO" "Cleanup completed"
}

# Signal handlers
trap cleanup EXIT
trap 'log "WARN" "Received SIGINT, shutting down..."; exit 1' INT
trap 'log "WARN" "Received SIGTERM, shutting down..."; exit 1' TERM

# Check if another instance is running
check_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "WARN" "Another instance (PID: $pid) is already running"
            return 1
        else
            log "WARN" "Stale lock file found, removing..."
            rm -f "$LOCK_FILE"
        fi
    fi
    return 0
}

# Acquire lock
acquire_lock() {
    if ! check_lock; then
        return 1
    fi

    echo $$ > "$LOCK_FILE"
    echo $$ > "$PID_FILE"
    log "INFO" "🔒 Lock acquired (PID: $$)"
    return 0
}

# Run command with error handling
run_command() {
    local description="$1"
    local command="$2"
    local cwd="${3:-$SCRIPT_DIR}"

    log "INFO" "🔄 Starting: $description"
    log "INFO" "Command: $command"
    log "INFO" "Working directory: $cwd"

    local start_time=$(date +%s)

    if (cd "$cwd" && eval "$command"); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "INFO" "✅ $description completed successfully (${duration}s)"
        return 0
    else
        local exit_code=$?
        log "ERROR" "❌ $description failed with exit code $exit_code"
        return $exit_code
    fi
}

# Main server process
main() {
    local start_time=$(date +%s)
    log "INFO" "🚀 Server started at $(date)"

    # Try to acquire lock
    if ! acquire_lock; then
        log "INFO" "Another instance is running, exiting..."
        exit 0
    fi

    # Step 1: Transfer clips
    if ! run_command "Transfer clips from Watcher" "./transfer_clips.sh"; then
        log "ERROR" "❌ Transfer failed - stopping process"
        exit 1
    fi

    # Step 2: Analyze clips
    if ! run_command "Analyze clips with car detection" "pipenv run analyze-clips"; then
        log "ERROR" "❌ Analysis failed"
        exit 1
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log "INFO" "✅ Server completed successfully in ${duration}s"
}

# Run main function
main "$@"