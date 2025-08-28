#!/bin/bash

start_therapy() {
    echo "Starting complete memory system..."

    # Setup environment if needed
    cd /Users/beck/Documents/private/memory
    if [ ! -d "memory_env" ]; then
        echo "Setting up Python environment..."
        python3 setup_env.py
    fi

    # Start memory system in background
    ./start_interactive_memory.sh &

    # Wait for memory system to start
    echo "Waiting for memory system to initialize..."
    sleep 5

    # Check if memory system is running
    if curl -s http://localhost:5001/status > /dev/null; then
        echo "Memory system is running"
    else
        echo "Memory system failed to start"
        exit 1
    fi


    echo "Everything is ready! Memory system is running and you just need to run 'claude code'."
    echo "Test with: 'Can you check my memory system status?'"
}

stop_therapy() {
    echo "Stopping memory system..."

    # Stop memory API server
    pkill -f "python3.*memory_api.py" && echo "Stopped memory API server" || echo "Memory API server was not running"

    # Stop MCP server
    pkill -f "python3.*memory_mcp_server_simple.py" && echo "Stopped MCP server" || echo "MCP server was not running"

    # Stop any other memory-related processes
    pkill -f "start_interactive_memory.sh" && echo "Stopped interactive memory script" || echo "Interactive memory script was not running"

    echo "Memory system stopped successfully!"
}

status_therapy() {
    echo "Memory system status..."
    echo

    # Check memory API server
    if pgrep -f "python3.*memory_api.py" > /dev/null; then
        echo "[RUNNING] Memory API server is running"
        if curl -s http://localhost:5001/status > /dev/null; then
            echo "          API endpoint responding on port 5001"
        else
            echo "          WARNING: Process running but API not responding"
        fi
    else
        echo "[STOPPED] Memory API server is not running"
    fi

    # Check MCP server
    if pgrep -f "python3.*memory_mcp_server_simple.py" > /dev/null; then
        echo "[RUNNING] MCP server is running"
    else
        echo "[STOPPED] MCP server is not running"
    fi

    # Check interactive memory script
    if pgrep -f "start_interactive_memory.sh" > /dev/null; then
        echo "[RUNNING] Interactive memory script is running"
    else
        echo "[STOPPED] Interactive memory script is not running"
    fi

    echo
    echo "Quick links:"
    echo "   Memory API: http://localhost:5001/status"
    echo "   Test command: curl http://localhost:5001/status"
}

# Main script logic
if [ "$1" = "start" ]; then
    start_therapy
elif [ "$1" = "stop" ]; then
    stop_therapy
elif [ "$1" = "status" ]; then
    status_therapy
else
    echo "Usage: $0 {start|stop|status}"
    echo "  start  - Start the memory system and Claude Code"
    echo "  stop   - Stop all memory system processes"
    echo "  status - Check status of memory system components"
    exit 1
fi
