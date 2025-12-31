#!/usr/bin/env python3
"""
Test script to verify access restriction works
"""

import os
import hashlib
import requests
import sys

def test_api_access_restriction():
    """Test that memory API requires correct token"""
    
    # Correct token
    allowed_project = os.path.expanduser("~/Documents/private/memory")
    correct_token = hashlib.sha256(allowed_project.encode()).hexdigest()[:16]
    
    # Wrong token
    wrong_token = "invalid_token"
    
    api_url = "http://127.0.0.1:8001"
    
    print("Testing memory API access restriction...")
    print(f"Current directory: {os.getcwd()}")
    
    # Test with correct token
    try:
        response = requests.post(f"{api_url}/query",
                               json={"input": "test query"},
                               headers={"X-Memory-Token": correct_token},
                               timeout=5)
        print(f"With correct token: {response.status_code}")
    except Exception as e:
        print(f"Error with correct token: {e}")
    
    # Test with wrong token
    try:
        response = requests.post(f"{api_url}/query",
                               json={"input": "test query"},
                               headers={"X-Memory-Token": wrong_token},
                               timeout=5)
        print(f"With wrong token: {response.status_code}")
    except Exception as e:
        print(f"Error with wrong token: {e}")
    
    # Test with no token
    try:
        response = requests.post(f"{api_url}/query",
                               json={"input": "test query"},
                               timeout=5)
        print(f"With no token: {response.status_code}")
    except Exception as e:
        print(f"Error with no token: {e}")

def test_client_access_restriction():
    """Test that memory client blocks access from wrong directory"""
    print("\nTesting memory client access restriction...")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        sys.path.insert(0, os.path.expanduser("~/Documents/private/memory"))
        from claude_memory_client import MemoryClient
        
        client = MemoryClient()
        print("Client initialization: SUCCESS")
        
        # Try to query
        result = client.query_memory("test query")
        print(f"Query result: {result}")
        
    except PermissionError as e:
        print(f"Client initialization blocked: {e}")
    except Exception as e:
        print(f"Client error: {e}")

if __name__ == "__main__":
    test_api_access_restriction()
    test_client_access_restriction()