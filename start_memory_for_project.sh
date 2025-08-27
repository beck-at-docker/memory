#!/bin/bash
# Auto-start memory system for Claude projects

echo "🧠 Checking memory system status..."

# Check if memory server is already running
if curl -s http://127.0.0.1:5001/status > /dev/null 2>&1; then
    echo "✅ Memory system already running"
else
    echo "🚀 Starting memory system..."
    cd /Users/beck/Documents/private/memory
    ./start_interactive_memory.sh &
    
    # Wait a moment for startup
    sleep 3
    
    if curl -s http://127.0.0.1:5001/status > /dev/null 2>&1; then
        echo "✅ Memory system started successfully"
    else
        echo "❌ Failed to start memory system"
    fi
fi

echo "📋 Memory system ready for Claude integration"