#!/usr/bin/env python3
"""
Demo: Compare Keyword vs LLM-based insight extraction and retrieval

This script demonstrates the difference between pattern matching and LLM-based
approaches for working with insights.
"""

import os
import sys
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from insight_system_simple import SimpleContextualInsightRetrieval, Insight

try:
    from insight_system_llm import LLMEnhancedInsightRetrieval
    from llm_client import LocalLlama
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_results(insights, max_show=5):
    """Print insight results"""
    if not insights:
        print("  (No insights found)")
        return
    
    for i, insight in enumerate(insights[:max_show], 1):
        print(f"  {i}. {insight.content}")
        print(f"     Entities: {list(insight.entities)}")
        print(f"     Themes: {list(insight.themes)}")
        print(f"     Type: {insight.insight_type}")
        print()


def setup_test_data(system):
    """Add test insights to the system"""
    print("Setting up test insights...")
    
    test_insights = [
        Insight(
            id=str(uuid.uuid4()),
            content="A is trustworthy. His word is enough. This is bedrock truth.",
            entities={"A"},
            themes={"trust", "relationships"},
            effectiveness_score=1.0,
            layer="surface",
            insight_type="anchor",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Taking trauma responses to therapy protects relationship with A",
            entities={"A", "trauma_responses"},
            themes={"strategies", "relationships", "trauma"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="strategy",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Trust builds through consistent actions over time, not words alone",
            entities=set(),
            themes={"trust", "relationships"},
            effectiveness_score=0.8,
            layer="surface",
            insight_type="observation",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="When A makes a promise, they follow through. This pattern is reliable.",
            entities={"A"},
            themes={"trust", "relationships"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="observation",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
            entities={"N"},
            themes={"parenting", "boundaries", "strategies"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="strategy",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="X's voice creates inadequacy-scanning. Recognize it as X, not truth.",
            entities={"X", "trauma_responses"},
            themes={"trauma", "strategies", "recognition"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="anchor",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="When feeling unsafe, pause and check: Is this danger real or remembered?",
            entities={"trauma_responses"},
            themes={"trauma", "strategies"},
            effectiveness_score=0.8,
            layer="surface",
            insight_type="strategy",
            timestamp=datetime.now()
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="A has never broken a commitment to me. This is evidence-based trust.",
            entities={"A"},
            themes={"trust", "relationships"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="observation",
            timestamp=datetime.now()
        )
    ]
    
    for insight in test_insights:
        system.add_insight(insight)
    
    print(f"✓ Added {len(test_insights)} test insights\n")


def test_extraction():
    """Test insight extraction from conversation"""
    print_section("TEST 1: Insight Extraction from Conversation")
    
    test_conversation = """
    Human: I'm really worried about whether I can trust A. What if they let me down 
    like everyone else has?
    
    Assistant: I understand that fear. What has your actual experience with A been like?
    Have there been specific situations where their reliability was tested?
    
    Human: Well, now that you mention it... Every time A has said they would do something,
    they've done it. Even small things. Like when they said they'd call at 3pm, they called
    at 3pm. When they said they'd help me move, they showed up early with a truck.
    
    Assistant: That's really important data. So you have consistent evidence of A following
    through on commitments, both big and small.
    
    Human: Yeah, I do. I think my fear is about X, not A. X was never reliable. But A 
    has proven themselves over and over.
    
    Assistant: Exactly. A has earned your trust through their actions. The fear you're feeling
    might be a trauma response from past experiences with X, not evidence about A's character.
    
    Human: You're right. A is trustworthy. That's a bedrock truth I need to remember when
    the fear comes up.
    """
    
    print("Sample conversation:")
    print("-" * 70)
    print(test_conversation[:300] + "...")
    print("-" * 70)
    
    if LLM_AVAILABLE:
        print("\n🤖 USING LOCAL LLAMA 3.3 FOR EXTRACTION")
        print("(This may take 30-60 seconds on first run as model loads)")
        
        try:
            llm = LocalLlama()
            insights = llm.extract_insights_from_conversation(test_conversation, max_insights=5)
            
            print(f"\nExtracted {len(insights)} insights:\n")
            for i, insight in enumerate(insights, 1):
                print(f"{i}. {insight['content']}")
                print(f"   Entities: {insight['entities']}")
                print(f"   Themes: {insight['themes']}")
                print(f"   Type: {insight['insight_type']}")
                print(f"   Score: {insight['effectiveness_score']}")
                print()
            
        except Exception as e:
            print(f"\n⚠ LLM extraction failed: {e}")
    else:
        print("⚠ LLM not available - skipping extraction test")


def test_retrieval():
    """Test insight retrieval comparison"""
    print_section("TEST 2: Keyword vs LLM Retrieval Comparison")
    
    # Create test database
    db_path = "/tmp/demo_insights.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Setup keyword system
    keyword_system = SimpleContextualInsightRetrieval(db_path)
    setup_test_data(keyword_system)
    
    # Test queries
    test_queries = [
        "Can I really trust A?",
        "Is A reliable?",
        "Should I believe what A tells me?"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 70)
        
        # Keyword results
        print("\n📝 KEYWORD MATCHING:")
        keyword_results = keyword_system.retrieve_contextual_insights(query)
        print_results(keyword_results['surface'], max_show=3)
        
        # LLM results
        if LLM_AVAILABLE:
            print("🤖 LLM SEMANTIC MATCHING:")
            print("(Re-ranking based on semantic relevance...)")
            
            try:
                llm_system = LLMEnhancedInsightRetrieval(
                    db_path,
                    use_llm_ranking=True,
                    llm_ranking_threshold=2
                )
                
                llm_results = llm_system.retrieve_contextual_insights(
                    query,
                    use_semantic_ranking=True
                )
                print_results(llm_results['surface'], max_show=3)
                
                # Show summary
                print("📊 LLM-GENERATED SUMMARY:")
                summary = llm_system.get_llm_summary(query, max_insights=3)
                if summary:
                    print(f"  {summary}\n")
                
            except Exception as e:
                print(f"  ⚠ LLM retrieval failed: {e}\n")
        else:
            print("⚠ LLM not available - install with: pip install -r requirements_llm.txt\n")
        
        print()
    
    # Cleanup
    os.remove(db_path)


def main():
    """Run the demo"""
    print("\n" + "=" * 70)
    print("  KEYWORD vs LLM COMPARISON DEMO")
    print("=" * 70)
    
    if not LLM_AVAILABLE:
        print("\n⚠ WARNING: LLM features not available")
        print("  Install with: pip install -r requirements_llm.txt")
        print("  Setup with: ./setup_llm_quick.sh or python3 setup_llm.py")
        print("\n  This demo will show keyword matching only.\n")
    
    # Check if Docker Model Runner is available
    if LLM_AVAILABLE:
        try:
            llm = LocalLlama()
            if not llm.is_available():
                print("\n⚠ Docker Model Runner not responding")
                print("  Make sure it's running: docker model status")
                print("  Pull model if needed: docker model pull ai/llama3.3\n")
        except Exception as e:
            print(f"\n⚠ Could not connect to LLM: {e}\n")
    
    # Run tests
    try:
        test_extraction()
        test_retrieval()
        
        print_section("SUMMARY")
        print("Key Differences:\n")
        print("KEYWORD MATCHING:")
        print("  ✓ Fast (<100ms)")
        print("  ✓ Predictable")
        print("  ✓ Works offline")
        print("  ✗ Misses semantic matches")
        print("  ✗ Requires exact keywords\n")
        
        print("LLM SEMANTIC MATCHING:")
        print("  ✓ Understands meaning")
        print("  ✓ Finds related concepts")
        print("  ✓ Natural language queries")
        print("  ✗ Slower (2-5 sec)")
        print("  ✗ First query is slow (30-60 sec)\n")
        
        print("RECOMMENDATION:")
        print("  • Use KEYWORD for: Real-time conversation")
        print("  • Use LLM for: Batch extraction, deep search")
        print("  • Use HYBRID: LLM for top results, keywords for speed\n")
        
    except KeyboardInterrupt:
        print("\n\n✗ Demo cancelled")
    except Exception as e:
        print(f"\n\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
