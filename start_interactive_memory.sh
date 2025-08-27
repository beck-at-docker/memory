#!/bin/bash
echo "🧠 Starting Interactive Memory System..."
echo "Starting memory API server..."

# Start memory API in background
source memory_env/bin/activate
python3 memory_api.py &
API_PID=$!

echo "✅ Memory API started (PID: $API_PID)"
echo "🔗 Memory system ready for Claude integration"
echo "📋 Configure Claude Code with MCP server and hooks as shown above"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo 'Stopping servers...'; kill $API_PID 2>/dev/null; exit" SIGINT SIGTERM

wait
