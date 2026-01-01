#!/bin/bash
# Memory System Wrapper with Virtual Environment Management
# Improved with PID files, health checks, and error handling

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/memory_env"
PID_DIR="$SCRIPT_DIR/pids"
API_PORT=8001
MAX_HEALTH_CHECK_ATTEMPTS=30
HEALTH_CHECK_INTERVAL=1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Utility functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Ensure PID directory exists
mkdir -p "$PID_DIR"

# Check if process is running by PID
is_process_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    if ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Read PID from file
read_pid() {
    local service=$1
    local pid_file="$PID_DIR/${service}.pid"
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    else
        echo ""
    fi
}

# Wait for server to be healthy
wait_for_health() {
    local attempts=0
    log_info "Waiting for memory API to be ready..."
    
    while [ $attempts -lt $MAX_HEALTH_CHECK_ATTEMPTS ]; do
        if curl -s -f "http://localhost:$API_PORT/status" > /dev/null 2>&1; then
            log_info "Memory API is healthy!"
            return 0
        fi
        
        attempts=$((attempts + 1))
        if [ $((attempts % 5)) -eq 0 ]; then
            log_info "Still waiting... ($attempts/$MAX_HEALTH_CHECK_ATTEMPTS)"
        fi
        sleep $HEALTH_CHECK_INTERVAL
    done
    
    log_error "Memory API did not become healthy within $MAX_HEALTH_CHECK_ATTEMPTS seconds"
    return 1
}

memory_start() {
    log_info "Starting memory system..."
    
    # Change to script directory
    cd "$SCRIPT_DIR" || {
        log_error "Failed to change to directory: $SCRIPT_DIR"
        return 1
    }
    
    # Check if already running
    local api_pid=$(read_pid "memory_api")
    if [ -n "$api_pid" ] && is_process_running "$api_pid"; then
        log_warn "Memory API is already running (PID: $api_pid)"
        return 0
    fi
    
    # Setup environment if needed
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Setting up Python virtual environment..."
        if ! python3 setup_env.py; then
            log_error "Failed to setup environment"
            return 1
        fi
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate" || {
        log_error "Failed to activate virtual environment"
        return 1
    }
    
    # Verify dependencies
    if ! python3 -c "import flask; import flask_limiter" 2>/dev/null; then
        log_error "Required Python packages not installed"
        log_info "Run: pip install -r requirements_simple.txt"
        return 1
    fi
    
    # Start memory API in background
    log_info "Starting memory API server..."
    nohup python3 memory_api.py > logs/memory_api.log 2>&1 &
    local api_pid=$!
    
    # Give it a moment to crash if there's an immediate problem
    sleep 2
    
    if ! is_process_running "$api_pid"; then
        log_error "Memory API failed to start"
        log_info "Check logs at: $SCRIPT_DIR/logs/memory_api.log"
        return 1
    fi
    
    log_info "Memory API started (PID: $api_pid)"
    
    # Wait for health check
    if wait_for_health; then
        log_info "✅ Memory system started successfully"
        log_info "   API: http://localhost:$API_PORT"
        log_info "   PID: $api_pid"
        log_info "   Logs: $SCRIPT_DIR/logs/memory_api.log"
        return 0
    else
        log_error "Memory system started but health check failed"
        log_info "Check logs at: $SCRIPT_DIR/logs/memory_api.log"
        # Kill the process since it's not healthy
        kill "$api_pid" 2>/dev/null
        return 1
    fi
}

memory_stop() {
    log_info "Stopping memory system..."
    
    cd "$SCRIPT_DIR" || {
        log_error "Failed to change to directory: $SCRIPT_DIR"
        return 1
    }
    
    local stopped_any=0
    
    # Stop memory API
    local api_pid=$(read_pid "memory_api")
    if [ -n "$api_pid" ] && is_process_running "$api_pid"; then
        log_info "Stopping memory API (PID: $api_pid)..."
        kill "$api_pid" 2>/dev/null || true
        
        # Wait for graceful shutdown
        local wait_count=0
        while [ $wait_count -lt 10 ] && is_process_running "$api_pid"; do
            sleep 0.5
            wait_count=$((wait_count + 1))
        done
        
        # Force kill if still running
        if is_process_running "$api_pid"; then
            log_warn "Force killing memory API..."
            kill -9 "$api_pid" 2>/dev/null || true
        fi
        
        stopped_any=1
        log_info "Stopped memory API"
    else
        log_info "Memory API was not running"
    fi
    
    # Stop MCP server if running
    local mcp_pid=$(read_pid "memory_mcp")
    if [ -n "$mcp_pid" ] && is_process_running "$mcp_pid"; then
        log_info "Stopping MCP server (PID: $mcp_pid)..."
        kill "$mcp_pid" 2>/dev/null || true
        stopped_any=1
        log_info "Stopped MCP server"
    fi
    
    # Clean up any orphaned processes (fallback)
    if pkill -f "python3.*memory_api.py" 2>/dev/null; then
        log_warn "Cleaned up orphaned memory_api processes"
        stopped_any=1
    fi
    
    if pkill -f "python3.*memory_mcp_server_simple.py" 2>/dev/null; then
        log_warn "Cleaned up orphaned MCP server processes"
        stopped_any=1
    fi
    
    # Deactivate virtual environment if active
    if [[ "${VIRTUAL_ENV:-}" == *"memory_env"* ]]; then
        log_info "Deactivating virtual environment..."
        deactivate 2>/dev/null || true
    fi
    
    if [ $stopped_any -eq 1 ]; then
        log_info "✅ Memory system stopped"
    else
        log_info "Nothing to stop"
    fi
}

memory_restart() {
    log_info "Restarting memory system..."
    memory_stop
    sleep 2
    memory_start
}

memory_status() {
    cd "$SCRIPT_DIR" || {
        log_error "Failed to change to directory: $SCRIPT_DIR"
        return 1
    }
    
    echo "Memory System Status"
    echo "===================="
    echo ""
    
    # Check API
    local api_pid=$(read_pid "memory_api")
    local api_running=0
    local api_healthy=0
    
    if [ -n "$api_pid" ] && is_process_running "$api_pid"; then
        api_running=1
        if curl -s -f "http://localhost:$API_PORT/status" > /dev/null 2>&1; then
            api_healthy=1
        fi
    fi
    
    if [ $api_healthy -eq 1 ]; then
        echo -e "${GREEN}✅ Memory API: Running and healthy${NC}"
        echo "   PID: $api_pid"
        echo "   URL: http://localhost:$API_PORT"
        echo "   Logs: $SCRIPT_DIR/logs/memory_api.log"
    elif [ $api_running -eq 1 ]; then
        echo -e "${YELLOW}⚠️  Memory API: Running but not responding${NC}"
        echo "   PID: $api_pid"
        echo "   Logs: $SCRIPT_DIR/logs/memory_api.log"
    else
        echo -e "${RED}❌ Memory API: Not running${NC}"
        echo "   Run './therapy.sh start' to start it"
    fi
    
    echo ""
    
    # Check virtual environment
    if [ -d "$VENV_DIR" ]; then
        if [[ "${VIRTUAL_ENV:-}" == *"memory_env"* ]]; then
            echo "Virtual environment: Active in this shell"
        else
            echo "Virtual environment: Installed (not active in this shell)"
        fi
    else
        echo -e "${YELLOW}Virtual environment: Not installed${NC}"
        echo "   Run './therapy.sh start' to set it up"
    fi
    
    echo ""
    
    # Show recent log entries if API is having issues
    if [ $api_running -eq 1 ] && [ $api_healthy -eq 0 ]; then
        echo "Recent log entries:"
        echo "-------------------"
        tail -n 10 "$SCRIPT_DIR/logs/memory_api.log" 2>/dev/null || echo "No log file found"
    fi
}

# Main entry point when sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
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
            echo "Memory System Wrapper"
            echo ""
            echo "Usage: $0 {start|stop|restart|status}"
            echo ""
            echo "Commands:"
            echo "  start   - Start memory system and activate virtual environment"
            echo "  stop    - Stop memory system and deactivate virtual environment"
            echo "  restart - Restart memory system"
            echo "  status  - Check memory system status"
            echo ""
            echo "Or source this script and use: memory_start, memory_stop, memory_restart, memory_status"
            exit 1
            ;;
    esac
fi
