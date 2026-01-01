#!/usr/bin/env python3
"""
Setup script for Local LLM integration with Docker Model Runner
"""

import subprocess
import sys
import os

def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            return True
        else:
            if result.stderr:
                print(f"Error: {result.stderr}")
            print(f"✗ {description} - FAILED")
            return False
            
    except FileNotFoundError:
        print(f"✗ Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def check_docker():
    """Check if Docker is installed and running"""
    print("\n" + "=" * 60)
    print("CHECKING DOCKER")
    print("=" * 60)
    
    # Check docker command exists
    result = subprocess.run(
        ["docker", "--version"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("✗ Docker not found")
        print("\nPlease install Docker Desktop from:")
        print("  https://www.docker.com/products/docker-desktop")
        return False
    
    print(f"✓ Docker found: {result.stdout.strip()}")
    
    # Check docker is running
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("✗ Docker is not running")
        print("\nPlease start Docker Desktop")
        return False
    
    print("✓ Docker is running")
    return True


def check_model_runner():
    """Check if Docker Model Runner is available"""
    print("\n" + "=" * 60)
    print("CHECKING DOCKER MODEL RUNNER")
    print("=" * 60)
    
    result = subprocess.run(
        ["docker", "model", "--help"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("✗ Docker Model Runner not found")
        print("\nDocker Model Runner requires:")
        print("  - Docker Desktop 4.40+ (macOS/Windows)")
        print("  - Docker Engine with Model Runner (Linux)")
        print("\nPlease update Docker Desktop or install Docker Model Runner")
        return False
    
    print("✓ Docker Model Runner available")
    return True


def enable_model_runner_tcp():
    """Enable TCP access for Docker Model Runner"""
    print("\n" + "=" * 60)
    print("ENABLING MODEL RUNNER TCP ACCESS")
    print("=" * 60)
    
    result = subprocess.run(
        ["docker", "desktop", "enable", "model-runner", "--tcp", "12434"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("⚠ Could not enable via CLI (this is OK on some systems)")
        print("\nPlease enable manually in Docker Desktop:")
        print("  Settings → Features → Enable 'Docker Model Runner'")
        print("  Settings → Features → Enable 'host-side TCP support' on port 12434")
        return False
    
    print("✓ TCP access enabled on port 12434")
    return True


def pull_llama_model():
    """Pull Llama 3.3 model"""
    return run_command(
        ["docker", "model", "pull", "ai/llama3.3"],
        "Pulling Llama 3.3 model (this will take a few minutes, ~4GB download)",
        check=False
    )


def list_models():
    """List available models"""
    return run_command(
        ["docker", "model", "ls"],
        "Listing available models",
        check=False
    )


def test_model():
    """Test the model with a simple query"""
    return run_command(
        ["docker", "model", "run", "ai/llama3.3", "Hello, respond with just 'working'"],
        "Testing Llama 3.3 model",
        check=False
    )


def install_python_deps():
    """Install Python dependencies"""
    print("\n" + "=" * 60)
    print("INSTALLING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠ Not in a virtual environment")
        print("\nRecommended: activate your virtual environment first:")
        print("  source memory_env/bin/activate")
        
        response = input("\nContinue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Cancelled")
            return False
    
    # Install from requirements_llm.txt
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements_llm.txt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("✗ Failed to install dependencies")
        print(result.stderr)
        return False
    
    print("✓ Python dependencies installed")
    return True


def test_llm_client():
    """Test the LLM client"""
    print("\n" + "=" * 60)
    print("TESTING LLM CLIENT")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, "llm_client.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print("✗ LLM client test failed")
        if result.stderr:
            print(result.stderr)
        return False
    
    print("✓ LLM client working")
    return True


def main():
    """Main setup flow"""
    print("\n" + "=" * 60)
    print("DOCKER MODEL RUNNER + LLAMA 3.3 SETUP")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Check Docker installation")
    print("  2. Check Docker Model Runner")
    print("  3. Enable TCP access")
    print("  4. Pull Llama 3.3 model")
    print("  5. Install Python dependencies")
    print("  6. Test the integration")
    
    response = input("\nContinue? (Y/n): ").strip().lower()
    if response == 'n':
        print("Cancelled")
        return
    
    # Check Docker
    if not check_docker():
        print("\n✗ Setup cannot continue without Docker")
        return
    
    # Check Model Runner
    if not check_model_runner():
        print("\n✗ Setup cannot continue without Docker Model Runner")
        return
    
    # Enable TCP
    enable_model_runner_tcp()  # May fail on some systems, that's OK
    
    # Check if model already exists
    list_models()
    
    response = input("\nPull Llama 3.3 model? (Y/n): ").strip().lower()
    if response != 'n':
        if pull_llama_model():
            print("\n✓ Model pulled successfully")
            test_model()
        else:
            print("\n⚠ Model pull failed or was interrupted")
    
    # Install Python dependencies
    response = input("\nInstall Python dependencies? (Y/n): ").strip().lower()
    if response != 'n':
        install_python_deps()
    
    # Test LLM client
    if os.path.exists("llm_client.py"):
        response = input("\nTest LLM client? (Y/n): ").strip().lower()
        if response != 'n':
            test_llm_client()
    
    # Final summary
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Test extraction: python3 extract_conversation_insights_llm.py")
    print("  2. Test retrieval: python3 insight_system_llm.py")
    print("  3. Check logs in: logs/memory_api.log")
    print("\nUseful commands:")
    print("  docker model ls              - List downloaded models")
    print("  docker model status          - Check Model Runner status")
    print("  docker model rm ai/llama3.3  - Remove model if needed")


if __name__ == "__main__":
    main()
