#!/usr/bin/env python3
"""
Setup Python virtual environment for Memory System
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("Setting up Python virtual environment for Memory System")
    print("=" * 60)
    
    # Get script directory
    script_dir = Path(__file__).parent
    venv_dir = script_dir / "memory_env"
    
    # Create virtual environment
    if venv_dir.exists():
        print(f"Virtual environment already exists at: {venv_dir}")
        print("Skipping creation...")
    else:
        print(f"Creating virtual environment at: {venv_dir}")
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_dir)
            ], check=True)
            print("✓ Virtual environment created")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create virtual environment: {e}")
            return 1
    
    # Install dependencies
    print("\nInstalling dependencies...")
    pip_exe = venv_dir / "bin" / "pip3"
    requirements_file = script_dir / "requirements_simple.txt"
    
    if not requirements_file.exists():
        print(f"✗ Requirements file not found: {requirements_file}")
        return 1
    
    try:
        subprocess.run([
            str(pip_exe), "install", "-r", str(requirements_file)
        ], check=True)
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nActivate the environment with:")
    print(f"  source {venv_dir}/bin/activate")
    print("\nOr start the system with:")
    print("  ./therapy.sh start")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
