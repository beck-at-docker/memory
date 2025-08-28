#!/bin/bash

# Source the wrapper for virtual environment management
source "$(dirname "$0")/therapy_wrapper.sh"

start_therapy() {
    # Use the wrapper function for proper venv management
    memory_start
}

stop_therapy() {
    # Use the wrapper function for proper venv management
    memory_stop
}

restart_therapy() {
    # Use the wrapper function for proper venv management
    memory_restart
}

status_therapy() {
    # Use the wrapper function for proper venv management
    memory_status
}

# Main script logic
if [ "$1" = "start" ]; then
    start_therapy
elif [ "$1" = "stop" ]; then
    stop_therapy
elif [ "$1" = "restart" ]; then
    restart_therapy
elif [ "$1" = "status" ]; then
    status_therapy
else
    echo "Usage: $0 {start|stop|restart|status}"
    echo "  start   - Start the memory system and Claude Code"
    echo "  stop    - Stop all memory system processes"
    echo "  restart - Restart the memory system"
    echo "  status  - Check status of memory system components"
    exit 1
fi