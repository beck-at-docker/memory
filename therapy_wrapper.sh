#!/bin/bash

# Memory System Wrapper with Virtual Environment Management
# Usage: source therapy_wrapper.sh [start|stop|restart|status]

memory_start() {
    echo "Starting complete memory system..."
    
    # Setup environment if needed
    cd /Users/beck/Documents/private/memory
    if [ ! -d "memory_env" ]; then
        echo "Setting up Python environment..."
        python3 setup_env.py
    fi
    
    # Activate virtual environment in current shell
    echo "Activating virtual environment..."
    source memory_env/bin/activate
    
    # Start memory system in background
    ./start_interactive_memory.sh &
    
    # Wait for memory system to start
    echo "Waiting for memory system to initialize..."
    sleep 5
    
    # Check if memory system is running
    if curl -s http://localhost:8001/status > /dev/null; then
        echo "Memory system is running"
    else
        echo "Memory system failed to start"
        return 1
    fi
    
    echo "✅ Memory system started with virtual environment active"
    echo "Use 'memory_stop' to stop and deactivate"
}

memory_stop() {
    echo "Stopping memory system..."
    
    cd /Users/beck/Documents/private/memory
    
    # Stop memory API server
    pkill -f "python3.*memory_api.py" && echo "Stopped memory API server" || echo "Memory API server was not running"

    # Stop MCP server
    pkill -f "python3.*memory_mcp_server_simple.py" && echo "Stopped MCP server" || echo "MCP server was not running"

    # Stop any other memory-related processes
    pkill -f "start_interactive_memory.sh" && echo "Stopped interactive memory script" || echo "Interactive memory script was not running"
    
    # Deactivate virtual environment if it was activated by us
    if [[ "$VIRTUAL_ENV" == *"memory_env"* ]]; then
        echo "Deactivating virtual environment..."
        deactivate
    fi
    
    echo "✅ Memory system stopped and virtual environment deactivated"
}

memory_restart() {
    echo "Restarting memory system..."
    memory_stop
    sleep 2
    memory_start
}

memory_status() {
    cd /Users/beck/Documents/private/memory
    echo "Memory System Status"
    echo "===================="
    
    # Check if the system is running (main thing you care about)
    if curl -s http://localhost:8001/status > /dev/null; then
        echo "✅ Memory system is running and ready"
        echo "   API: http://localhost:8001/status"
        
        # Show virtual environment status only if relevant
        if [[ "$VIRTUAL_ENV" == *"memory_env"* ]]; then
            echo "   Virtual environment: Active in this shell"
        fi
    else
        echo "❌ Memory system is not running"
        echo "   Run 'therapy start' to start it"
        
        # Only show environment issues if system isn't running
        if [ ! -d "memory_env" ]; then
            echo "   Setup needed: Virtual environment missing"
        elif ! (source memory_env/bin/activate 2>/dev/null && python3 -c "import flask_limiter" 2>/dev/null); then
            echo "   Setup needed: Dependencies missing or broken"
        fi
    fi
}

# Only handle command line arguments if called directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ "$1" = "start" ]; then
        memory_start
    elif [ "$1" = "stop" ]; then
        memory_stop
    elif [ "$1" = "restart" ]; then
        memory_restart
    elif [ "$1" = "status" ]; then
        memory_status
    else
        echo "Memory System Wrapper - Virtual Environment Management"
        echo ""
        echo "Usage: source therapy_wrapper.sh [command]"
        echo "   OR: memory_start / memory_stop / memory_restart / memory_status"
        echo ""
        echo "Commands:"
        echo "  start   - Start memory system and activate virtual environment"
        echo "  stop    - Stop memory system and deactivate virtual environment"  
        echo "  restart - Restart memory system"
        echo "  status  - Check memory system and environment status"
        echo ""
        echo "After sourcing, you can use: memory_start, memory_stop, memory_restart, memory_status"
    fi
fi