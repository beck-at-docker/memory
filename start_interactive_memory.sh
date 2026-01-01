#!/bin/bash
# Start interactive memory system
# This script is called by therapy_wrapper.sh but can also be run standalone

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/memory_env"

echo "🧠 Starting Interactive Memory System..."
echo "Script directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at: $VENV_DIR"
    echo "Run: python3 setup_env.py"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Verify dependencies
if ! python3 -c "import flask; import flask_limiter" 2>/dev/null; then
    echo "❌ Required dependencies not found"
    echo "Run: pip install -r requirements_simple.txt"
    exit 1
fi

echo "Starting memory API server..."

# Start memory API
python3 memory_api.py &
API_PID=$!

echo "✅ Memory API started (PID: $API_PID)"
echo "🔗 Memory system ready for Claude integration"
echo "📋 Configure Claude Code with MCP server as shown in README.md"
echo ""
echo "Memory API will run in the background"
echo "Check status with: ./therapy.sh status"
echo "Stop with: ./therapy.sh stop"
echo ""
echo "Or press Ctrl+C to stop now..."

# Handle Ctrl+C gracefully
trap "echo ''; echo 'Stopping server...'; kill $API_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for the API process
wait $API_PID 2>/dev/null || true
