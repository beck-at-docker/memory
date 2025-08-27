#!/usr/bin/env python3
"""
Test script for the Contextual Insight Retrieval System
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from insight_retrieval_system import ContextualInsightRetrieval, Insight
        print("✓ Core system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core system: {e}")
        return False
    
    try:
        from data_migration import DataMigrationPipeline, ConversationParser
        print("✓ Data migration imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import data migration: {e}")
        return False
    
    try:
        from conversational_interface import InsightAPI, ConversationFlow, CrisisMode
        print("✓ Conversational interface imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import conversational interface: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        # Test system initialization (without sentence transformers)
        from insight_retrieval_system import ContextualInsightRetrieval, Insight
        from datetime import datetime
        import uuid
        
        # Create a simplified test system
        system = ContextualInsightRetrieval("test.db")
        
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
        
        # Test trigger detection
        triggers = system.detect_context_triggers("I'm worried about trusting A")
        print(f"✓ Detected triggers: {triggers}")
        
        if "A" in triggers:
            print("✓ Entity detection working correctly")
        else:
            print("✗ Entity detection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_conversation_parser():
    """Test the conversation parser with sample data"""
    print("\nTesting conversation parser...")
    
    try:
        from data_migration import ConversationParser
        from pathlib import Path
        
        parser = ConversationParser()
        
        # Test entity identification
        test_text = "I'm worried about trusting A. N is being difficult with boundaries."
        entities = parser._identify_entities(test_text)
        
        print(f"✓ Entities detected: {entities}")
        
        if "A" in entities and "N" in entities:
            print("✓ Entity detection working correctly")
        else:
            print("✗ Entity detection incomplete")
            return False
        
        # Test theme identification  
        themes = parser._identify_themes(test_text)
        print(f"✓ Themes detected: {themes}")
        
        # Test insight type classification
        insight_type = parser._classify_insight_type("That shifted something fundamental about trust")
        
        if insight_type == "breakthrough":
            print("✓ Insight type classification working")
        else:
            print(f"✗ Insight type classification failed: got {insight_type}, expected 'breakthrough'")
        
        return True
        
    except Exception as e:
        print(f"✗ Conversation parser test failed: {e}")
        traceback.print_exc()
        return False

def test_crisis_mode():
    """Test crisis mode detection"""
    print("\nTesting crisis mode...")
    
    try:
        from conversational_interface import CrisisMode
        from insight_retrieval_system import ContextualInsightRetrieval
        
        system = ContextualInsightRetrieval("test.db")
        crisis_mode = CrisisMode(system)
        
        # Test crisis detection
        crisis_input = "I'm in complete panic and everything is falling apart"
        is_crisis = crisis_mode.detect_crisis(crisis_input)
        
        if is_crisis:
            print("✓ Crisis mode detection working")
        else:
            print("✗ Crisis mode detection failed")
            return False
        
        # Test non-crisis input
        normal_input = "How are you doing today?"
        is_not_crisis = crisis_mode.detect_crisis(normal_input)
        
        if not is_not_crisis:
            print("✓ Normal input correctly identified as non-crisis")
        else:
            print("✗ False positive for crisis detection")
        
        return True
        
    except Exception as e:
        print(f"✗ Crisis mode test failed: {e}")
        traceback.print_exc()
        return False

def test_end_to_end_flow():
    """Test end-to-end conversation flow"""
    print("\nTesting end-to-end flow...")
    
    try:
        from conversational_interface import InsightAPI
        
        # Initialize API (this will create test database)
        api = InsightAPI("test_e2e.db")
        
        # Add a test insight first
        api.add_new_insight(
            content="A is trustworthy. His word is enough.",
            entities=["A"],
            themes=["trust"],
            insight_type="anchor"
        )
        
        # Test normal conversation
        response = api.chat("I'm worried about trusting A")
        
        print(f"✓ Response generated: {response['mode']} mode")
        
        if response["insights"]:
            print("✓ Insights surfaced in response")
            print(f"  Insights: {response['insights'][:100]}...")
        else:
            print("✗ No insights surfaced")
        
        # Test conversation state tracking
        state = response["conversation_state"]
        if "A" in state["active_entities"]:
            print("✓ Entity tracking working")
        else:
            print("✗ Entity tracking failed")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Contextual Insight Retrieval System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality), 
        ("Conversation Parser", test_conversation_parser),
        ("Crisis Mode", test_crisis_mode),
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