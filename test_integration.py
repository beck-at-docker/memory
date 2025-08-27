#!/usr/bin/env python3
"""
Test script for Claude memory integration
"""

import sys
import time
from claude_memory_client import MemoryClient
from claude_hooks import ConversationMonitor

def test_memory_client():
    """Test basic memory client functionality"""
    print("🔍 Testing Memory Client...")
    
    client = MemoryClient()
    
    # Check server status
    if not client.is_server_running():
        print("❌ Memory server is not running")
        print("   Start it with: ./start_server.sh")
        return False
    
    print("✅ Memory server is running")
    
    # Test query
    result = client.query_memory("I'm worried about trusting someone")
    if "error" in result:
        print(f"❌ Query failed: {result['error']}")
        return False
    
    insights = result.get("insights", [])
    print(f"✅ Query returned {len(insights)} insights")
    
    return True

def test_conversation_monitor():
    """Test conversation monitoring"""
    print("🎯 Testing Conversation Monitor...")
    
    monitor = ConversationMonitor()
    
    # Test trigger detection
    test_inputs = [
        "I'm worried about trusting A",
        "N is being difficult with boundaries", 
        "I'm hearing X's voice again",
        "I realized that taking breaks really helps",
        "What worked was setting clear limits"
    ]
    
    for test_input in test_inputs:
        should_query = monitor.should_query_memory(test_input)
        should_capture = monitor.should_capture_insight(test_input)
        
        print(f"   Input: '{test_input[:30]}...'")
        print(f"   → Query: {should_query}, Capture: {should_capture}")
    
    print("✅ Conversation monitor working")
    return True

def test_insight_processing():
    """Test insight processing and suggestions"""
    print("💡 Testing Insight Processing...")
    
    monitor = ConversationMonitor()
    
    # Test conversation with insights
    conversation = """
    I realized that setting boundaries with N actually helps our relationship.
    What worked was staying calm and explaining why the limit matters.
    I discovered that when I don't get activated, she responds much better.
    """
    
    suggestions = monitor.suggest_insight_capture(conversation)
    
    if suggestions:
        print("✅ Insight suggestions generated:")
        print(suggestions[:200] + "..." if len(suggestions) > 200 else suggestions)
    else:
        print("⚠️  No insights detected in test conversation")
    
    return True

def run_full_test():
    """Run complete integration test"""
    print("🧠 Claude Memory Integration Test")
    print("=" * 50)
    
    tests = [
        ("Memory Client", test_memory_client),
        ("Conversation Monitor", test_conversation_monitor), 
        ("Insight Processing", test_insight_processing)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your memory system is ready for Claude integration.")
        print("\nNext steps:")
        print("1. Run: python3 setup_claude_integration.py")
        print("2. Configure Claude Code with MCP and hooks")
        print("3. Start: ./start_interactive_memory.sh")
    else:
        print("\n⚠️  Some tests failed. Check the setup and try again.")
    
    return all_passed

if __name__ == "__main__":
    run_full_test()