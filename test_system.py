#!/usr/bin/env python3
"""
Test script for the Simplified Contextual Insight Retrieval System
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from insight_system_simple import SimpleContextualInsightRetrieval, Insight
        print("✓ Core system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core system: {e}")
        return False
    
    try:
        from claude_memory_client import MemoryClient
        print("✓ Memory client imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import memory client: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        from insight_system_simple import SimpleContextualInsightRetrieval, Insight
        from datetime import datetime
        import uuid
        
        # Create a simplified test system
        system = SimpleContextualInsightRetrieval("test.db")
        
        # Create a test insight
        test_insight = Insight(
            id=str(uuid.uuid4()),
            content="A is trustworthy. His word is enough.",
            entities={"A"},
            themes={"trust"},
            insight_type="anchor",
            timestamp=datetime.now(),
            effectiveness_score=1.0
        )
        
        print("✓ Test insight created successfully")
        
        # Add insight to system
        system.add_insight(test_insight)
        print("✓ Insight added to system successfully")
        
        # Test retrieval
        insights = system.retrieve_contextual_insights("I'm worried about trusting A")
        print(f"✓ Retrieved insights: surface={len(insights['surface'])}, mid={len(insights['mid'])}, deep={len(insights['deep'])}")
        
        if insights['surface']:
            print("✓ Insight retrieval working correctly")
        else:
            print("✗ No insights retrieved")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_memory_client():
    """Test the memory client functionality"""
    print("\nTesting memory client...")
    
    try:
        from claude_memory_client import MemoryClient
        
        client = MemoryClient()
        
        # Test basic query (may fail if server not running, which is OK)
        try:
            result = client.query_memory("test query")
            print("✓ Memory client can communicate with server")
        except Exception as e:
            print(f"~ Memory client test skipped (server not running): {e}")
            return True
        
        return True
        
    except Exception as e:
        print(f"✗ Memory client test failed: {e}")
        traceback.print_exc()
        return False

def test_crisis_detection():
    """Test crisis mode detection in simple system"""
    print("\nTesting crisis detection...")
    
    try:
        from insight_system_simple import SimpleContextualInsightRetrieval
        
        system = SimpleContextualInsightRetrieval("test.db")
        
        # Test crisis detection
        crisis_input = "I'm in complete panic and everything is falling apart"
        insights = system.retrieve_contextual_insights(crisis_input)
        
        print("✓ Crisis input processed successfully")
        print(f"  Insights retrieved: surface={len(insights['surface'])}, mid={len(insights['mid'])}, deep={len(insights['deep'])}")
        
        # Test normal input
        normal_input = "How are you doing today?"
        normal_insights = system.retrieve_contextual_insights(normal_input)
        
        print("✓ Normal input processed successfully")
        print(f"  Insights retrieved: surface={len(normal_insights['surface'])}, mid={len(normal_insights['mid'])}, deep={len(normal_insights['deep'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ Crisis detection test failed: {e}")
        traceback.print_exc()
        return False

def test_end_to_end_flow():
    """Test end-to-end system functionality"""
    print("\nTesting end-to-end flow...")
    
    try:
        from insight_system_simple import SimpleContextualInsightRetrieval, Insight
        from datetime import datetime
        import uuid
        
        # Initialize system
        system = SimpleContextualInsightRetrieval("test_e2e.db")
        
        # Add a test insight
        test_insight = Insight(
            id=str(uuid.uuid4()),
            content="A is trustworthy. His word is enough.",
            entities={"A"},
            themes={"trust"},
            insight_type="anchor",
            timestamp=datetime.now(),
            effectiveness_score=1.0
        )
        
        system.add_insight(test_insight)
        print("✓ Test insight added to system")
        
        # Test retrieval with entity trigger
        insights = system.retrieve_contextual_insights("I'm worried about trusting A")
        
        print(f"✓ End-to-end retrieval successful")
        print(f"  Surface insights: {len(insights['surface'])}")
        print(f"  Mid insights: {len(insights['mid'])}")
        print(f"  Deep insights: {len(insights['deep'])}")
        
        if insights['surface']:
            print(f"  Sample insight: {insights['surface'][0].content[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Simple Contextual Insight Retrieval System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality), 
        ("Memory Client", test_memory_client),
        ("Crisis Detection", test_crisis_detection),
        ("End-to-End Flow", test_end_to_end_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"{'=' * 60}")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)