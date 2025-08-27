#!/usr/bin/env python3
"""
Simple script to start the memory server in the background
"""

import subprocess
import sys
import time
import requests
import os

def is_server_running():
    """Check if server is already running"""
    try:
        response = requests.get("http://127.0.0.1:5000/status", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the memory server"""
    if is_server_running():
        print("✅ Memory server is already running")
        return True
    
    print("🚀 Starting memory server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "memory_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment and check if it started
        time.sleep(3)
        
        if is_server_running():
            print("✅ Memory server started successfully on http://127.0.0.1:5000")
            return True
        else:
            print("❌ Failed to start memory server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def stop_server():
    """Stop any running memory servers"""
    try:
        # Kill any python processes running memory_api.py
        subprocess.run(["pkill", "-f", "memory_api.py"], capture_output=True)
        print("🛑 Memory server stopped")
    except:
        print("❌ Could not stop memory server")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_server()
    else:
        start_server()