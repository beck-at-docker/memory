#!/usr/bin/env python3
"""
Setup script to create virtual environment and install dependencies
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_environment():
    """Setup virtual environment and install dependencies"""
    
    # Create virtual environment
    if not run_command("python3 -m venv memory_env", "Creating virtual environment"):
        return False
    
    # Install requirements
    if not run_command("memory_env/bin/pip install -r requirements.txt", "Installing requirements"):
        return False
    
    # Create activation script
    activation_script = """#!/bin/bash
# Activate virtual environment and start memory server
source memory_env/bin/activate
python3 memory_api.py
"""
    
    with open("start_server.sh", "w") as f:
        f.write(activation_script)
    
    os.chmod("start_server.sh", 0o755)
    
    print("\n🎉 Setup complete!")
    print("\n📋 To start the memory server:")
    print("   ./start_server.sh")
    print("\n📋 To use the virtual environment manually:")
    print("   source memory_env/bin/activate")
    print("   python3 memory_api.py")
    
    return True

if __name__ == "__main__":
    setup_environment()