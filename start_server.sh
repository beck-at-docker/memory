#!/bin/bash
# Activate virtual environment and start memory server
echo "🧠 Starting Memory Server..."
source memory_env/bin/activate
echo "✅ Virtual environment activated"
echo "🚀 Starting API server on http://127.0.0.1:5000"
python3 memory_api.py