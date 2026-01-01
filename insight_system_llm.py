#!/usr/bin/env python3
"""
Enhanced Insight System with Optional LLM Support
Adds semantic ranking via local Llama 3.3
"""

import os
from typing import Dict, List
from insight_system_simple import SimpleContextualInsightRetrieval, Insight
from logging_config import get_logger

logger = get_logger('insight_system_llm')

# Try to import LLM client
try:
    from llm_client import LocalLlama
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class LLMEnhancedInsightRetrieval(SimpleContextualInsightRetrieval):
    """
    Enhanced version of SimpleContextualInsightRetrieval with optional LLM support.
    
    Falls back gracefully to keyword matching if LLM is unavailable.
    """
    
    def __init__(
        self, 
        db_path: str = "insights_simple.db",
        use_llm_ranking: bool = False,
        llm_ranking_threshold: int = 5
    ):
        """
        Initialize enhanced retrieval system.
        
        Args:
            db_path: Path to SQLite database
            use_llm_ranking: Whether to use LLM for semantic re-ranking
            llm_ranking_threshold: Only use LLM if more than N results from keyword search
        """
        # Initialize base system
        super().__init__(db_path)
        
        self.use_llm_ranking = use_llm_ranking and LLM_AVAILABLE
        self.llm_ranking_threshold = llm_ranking_threshold
        self.llm = None
        
        # Try to initialize LLM if requested
        if self.use_llm_ranking:
            try:
                self.llm = LocalLlama()
                if self.llm.is_available():
                    logger.info("LLM-enhanced semantic ranking enabled")
                else:
                    logger.warning("LLM not available, using keyword-only matching")
                    self.use_llm_ranking = False
            except Exception as e:
                logger.warning(f"Could not initialize LLM: {e}")
                self.use_llm_ranking = False
    
    def retrieve_contextual_insights(
        self, 
        user_input: str,
        use_semantic_ranking: bool = None
    ) -> Dict:
        """
        Retrieve insights with optional LLM semantic re-ranking.
        
        Args:
            user_input: User's query text
            use_semantic_ranking: Override default LLM ranking setting for this query
            
        Returns:
            Dict with 'surface' and 'mid' insight lists
        """
        
        # First: Fast keyword-based retrieval (existing logic)
        results = super().retrieve_contextual_insights(user_input)
        surface_insights = results.get("surface", [])
        
        # Determine if we should use LLM ranking for this query
        should_rank = (
            use_semantic_ranking if use_semantic_ranking is not None 
            else self.use_llm_ranking
        )
        
        # Only use LLM if we have enough results to rank
        if (should_rank and 
            self.llm and 
            len(surface_insights) > self.llm_ranking_threshold):
            
            try:
                logger.info(f"Re-ranking {len(surface_insights)} insights with LLM")
                
                # Score each insight semantically
                scored_insights = []
                for insight in surface_insights:
                    score = self.llm.semantic_match_score(user_input, insight.content)
                    scored_insights.append((score, insight))
                
                # Sort by score (highest first)
                scored_insights.sort(reverse=True, key=lambda x: x[0])
                
                # Extract sorted insights
                surface_insights = [insight for _, insight in scored_insights]
                
                logger.info(f"LLM re-ranking complete. Top score: {scored_insights[0][0]:.2f}")
                
            except Exception as e:
                logger.error(f"LLM ranking failed: {e}, using keyword-only results")
                # Fall back to keyword-only results (already in surface_insights)
        
        return {
            "surface": surface_insights,
            "mid": results.get("mid", [])
        }
    
    def get_llm_summary(self, user_input: str, max_insights: int = 5) -> str:
        """
        Get an LLM-generated summary of relevant insights.
        
        Args:
            user_input: User's query
            max_insights: Number of insights to summarize
            
        Returns:
            Natural language summary or empty string if LLM unavailable
        """
        
        if not self.llm:
            return ""
        
        try:
            # Retrieve insights
            results = self.retrieve_contextual_insights(user_input)
            insights = results.get("surface", [])[:max_insights]
            
            if not insights:
                return ""
            
            # Extract content
            insight_texts = [i.content for i in insights]
            
            # Generate summary
            summary = self.llm.summarize_insights(
                insight_texts,
                context=user_input
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return ""


def test_llm_enhanced_system():
    """Test the LLM-enhanced system"""
    import uuid
    from datetime import datetime
    
    print("=" * 60)
    print("TESTING LLM-ENHANCED INSIGHT RETRIEVAL")
    print("=" * 60)
    
    # Create test database
    db_path = "/tmp/test_llm_insights.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize with LLM ranking enabled
    print("\nInitializing system with LLM ranking...")
    system = LLMEnhancedInsightRetrieval(
        db_path=db_path,
        use_llm_ranking=True,
        llm_ranking_threshold=3
    )
    
    if not system.use_llm_ranking:
        print("⚠ LLM not available, this will only test keyword matching")
    else:
        print("✓ LLM ranking enabled")
    
    # Add test insights
    print("\nAdding test insights...")
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
        )
    ]
    
    for insight in test_insights:
        system.add_insight(insight)
    
    print(f"✓ Added {len(test_insights)} test insights")
    
    # Test queries
    test_queries = [
        "Can I really trust A?",
        "I'm worried about whether A will disappoint me",
        "How do I handle N's behavior?",
        "I'm feeling triggered and unsafe"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: '{query}'")
        print("=" * 60)
        
        # Test keyword-only retrieval
        print("\n1. Keyword-only results:")
        results_keywords = system.retrieve_contextual_insights(
            query, 
            use_semantic_ranking=False
        )
        for i, insight in enumerate(results_keywords['surface'][:3], 1):
            print(f"   {i}. {insight.content[:80]}...")
        
        # Test LLM-enhanced retrieval (if available)
        if system.llm:
            print("\n2. LLM-ranked results:")
            results_llm = system.retrieve_contextual_insights(
                query,
                use_semantic_ranking=True
            )
            for i, insight in enumerate(results_llm['surface'][:3], 1):
                print(f"   {i}. {insight.content[:80]}...")
            
            # Test summary generation
            print("\n3. LLM-generated summary:")
            summary = system.get_llm_summary(query, max_insights=3)
            if summary:
                print(f"   {summary}")
            else:
                print("   (No summary generated)")
    
    print("\n" + "=" * 60)
    print("✓ Testing complete!")
    
    # Cleanup
    os.remove(db_path)


if __name__ == "__main__":
    test_llm_enhanced_system()
