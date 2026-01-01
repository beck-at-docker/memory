#!/bin/bash
# Main entry point for memory system management
# This is a simple wrapper around therapy_wrapper.sh

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the wrapper functions
# shellcheck source=therapy_wrapper.sh
source "$SCRIPT_DIR/therapy_wrapper.sh"

# Handle commands
case "${1:-}" in
    start)
        memory_start
        ;;
    stop)
        memory_stop
        ;;
    restart)
        memory_restart
        ;;
    status)
        memory_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the memory system"
        echo "  stop    - Stop all memory system processes"
        echo "  restart - Restart the memory system"
        echo "  status  - Check status of memory system components"
        echo ""
        echo "Examples:"
        echo "  $0 start    # Start memory system"
        echo "  $0 status   # Check if running"
        echo "  $0 stop     # Stop memory system"
        exit 1
        ;;
esac
