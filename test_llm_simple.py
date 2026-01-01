#!/usr/bin/env python3
"""
Simple test runner for LLM integration
Run this to verify everything is working
"""

import subprocess
import sys
import os

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def run_test(description, command, check_output=None):
    """Run a test command"""
    print(f"→ {description}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"  ✓ SUCCESS")
            if check_output and check_output in result.stdout:
                print(f"  ✓ Found expected output")
            if result.stdout:
                print(f"\n{result.stdout}\n")
            return True
        else:
            print(f"  ✗ FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ⚠ TIMEOUT (this might be OK for first LLM query)")
        return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def main():
    print_header("LLM INTEGRATION TEST SUITE")
    
    # Change to project directory
    os.chdir(os.path.expanduser("~/Documents/private"))
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Docker
    print_header("TEST 1: Docker Environment")
    tests_total += 1
    if run_test("Checking Docker", "docker --version"):
        tests_passed += 1
    
    tests_total += 1
    if run_test("Checking Docker Model Runner", "docker model --help | head -5"):
        tests_passed += 1
    
    tests_total += 1
    if run_test("Listing models", "docker model ls"):
        tests_passed += 1
    
    tests_total += 1
    if run_test("Checking Model Runner status", "docker model status"):
        tests_passed += 1
    
    # Test 2: Python environment
    print_header("TEST 2: Python Environment")
    tests_total += 1
    if run_test("Checking Python version", "python3 --version"):
        tests_passed += 1
    
    tests_total += 1
    if run_test("Checking OpenAI package", "python3 -c 'from openai import OpenAI; print(\"OpenAI package available\")'"):
        tests_passed += 1
    
    # Test 3: LLM Client
    print_header("TEST 3: LLM Client (May take 30-60 sec)")
    print("NOTE: First query is slow as model loads into memory\n")
    tests_total += 1
    if run_test("Running LLM client test", "python3 llm_client.py", "Testing complete"):
        tests_passed += 1
    
    # Test 4: Quick functionality test
    print_header("TEST 4: Quick Functionality Test")
    tests_total += 1
    
    test_code = """
from llm_client import LocalLlama
llm = LocalLlama()
print("✓ LLM client initialized")
if llm.is_available():
    print("✓ LLM is available")
else:
    print("✗ LLM not available")
"""
    
    if run_test("Testing LLM availability", f"python3 -c \"{test_code}\""):
        tests_passed += 1
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("\n✓ ALL TESTS PASSED")
        print("\nNext steps:")
        print("  1. Try: python3 demo_llm_comparison.py")
        print("  2. Extract insights: python3 extract_conversation_insights_llm.py")
        print("  3. Read docs: cat README_LLM.md")
        return 0
    else:
        print(f"\n⚠ {tests_total - tests_passed} tests failed")
        print("\nTroubleshooting:")
        print("  - Make sure Docker Desktop is running")
        print("  - Run: docker model pull ai/llama3.3")
        print("  - Enable TCP: docker desktop enable model-runner --tcp 12434")
        print("  - Install deps: pip install -r requirements_llm.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
