#!/usr/bin/env python3
"""
Local LLM Client for Docker Model Runner
Provides interface to Llama 3.3 running locally via Docker
"""

import json
import re
from typing import List, Dict, Optional
from openai import OpenAI
from logging_config import get_logger

logger = get_logger('llm_client')

class LocalLlama:
    """Local Llama 3.3 client via Docker Model Runner"""
    
    def __init__(
        self, 
        base_url: str = "http://localhost:12434/engines/v1",
        model: str = "ai/llama3.3"
    ):
        """
        Initialize local LLM client.
        
        Args:
            base_url: Docker Model Runner endpoint
            model: Model identifier (default: ai/llama3.3)
        """
        self.base_url = base_url
        self.model = model
        
        try:
            self.client = OpenAI(
                base_url=base_url,
                api_key="not-needed"  # Required by SDK but unused for local
            )
            logger.info(f"Initialized local LLM client: {model} at {base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Docker Model Runner is accessible"""
        try:
            # Try a minimal completion request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.warning(f"LLM not available: {e}")
            return False
    
    def extract_insights_from_conversation(
        self, 
        conversation_text: str,
        max_insights: int = 10
    ) -> List[Dict]:
        """
        Extract meaningful insights from conversation text.
        
        Args:
            conversation_text: The conversation to analyze
            max_insights: Maximum number of insights to extract
            
        Returns:
            List of insight dictionaries with keys:
                - content: The insight text
                - entities: List of entity names (A, N, X, etc.)
                - themes: List of theme keywords
                - insight_type: anchor/breakthrough/strategy/observation
                - effectiveness_score: 0.0-1.0
        """
        
        system_prompt = """You are an insight extraction system for personal therapy/growth conversations.

Extract meaningful, actionable insights from conversations. Focus on:
- Key realizations and breakthroughs
- Effective strategies and techniques
- Important patterns about people and relationships
- Foundational truths and anchors

For each insight, identify:
- content: The actual insight (1-2 clear sentences)
- entities: People mentioned by single letters (A, N, X, B, E, etc.) or concepts (trauma_responses, internal_voice)
- themes: Topics from: trust, boundaries, trauma, parenting, healing, relationships, strategies, emotions, communication, growth
- insight_type: 
  * anchor = fundamental unchanging truth
  * breakthrough = major realization/shift
  * strategy = actionable technique that works
  * observation = pattern noticed
- effectiveness_score: 0.0-1.0 based on clarity and actionability

Return ONLY valid JSON array, no markdown, no explanation:
[
  {
    "content": "insight text here",
    "entities": ["A", "N"],
    "themes": ["trust", "boundaries"],
    "insight_type": "strategy",
    "effectiveness_score": 0.8
  }
]"""

        user_prompt = f"""Extract the {max_insights} most important insights from this conversation:

{conversation_text[:8000]}

Return ONLY the JSON array."""

        try:
            logger.info(f"Extracting insights from {len(conversation_text)} chars of conversation")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower for more consistent structured output
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            insights = self._parse_json_response(content)
            
            logger.info(f"Successfully extracted {len(insights)} insights")
            return insights[:max_insights]
            
        except Exception as e:
            logger.error(f"Insight extraction failed: {e}")
            return []
    
    def semantic_match_score(
        self, 
        query: str, 
        insight_content: str
    ) -> float:
        """
        Score how semantically relevant an insight is to a query.
        
        Args:
            query: The user's search query
            insight_content: The insight text to score
            
        Returns:
            Relevance score from 0.0 (not relevant) to 1.0 (highly relevant)
        """
        
        prompt = f"""Rate how relevant this insight is to the query. Consider semantic meaning, not just keywords.

Query: {query}

Insight: {insight_content}

Return ONLY a single number between 0.0 and 1.0, nothing else.
- 1.0 = directly answers or addresses the query
- 0.7-0.9 = very relevant, related topic
- 0.4-0.6 = somewhat relevant, tangential
- 0.0-0.3 = not relevant

Score:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Very low for consistent scoring
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            
            # Extract first number found (handles 0, 1, 0.5, 1.0, 0.75, etc.)
            # Pattern matches: 0, 1, 0.5, 1.0, 0.123, etc.
            numbers = re.findall(r'[01](?:\.\d+)?', score_text)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))  # Clamp to 0-1
            
            logger.warning(f"Could not parse score from: {score_text}")
            return 0.5  # Neutral fallback
            
        except Exception as e:
            logger.error(f"Semantic scoring failed: {e}")
            return 0.5
    
    def batch_semantic_scores(
        self,
        query: str,
        insights: List[str]
    ) -> List[float]:
        """
        Score multiple insights at once (more efficient than one-by-one).
        
        Args:
            query: The search query
            insights: List of insight texts to score
            
        Returns:
            List of scores corresponding to each insight
        """
        
        if not insights:
            return []
        
        # For now, do one-by-one (could optimize later with batch prompting)
        scores = []
        for insight in insights:
            score = self.semantic_match_score(query, insight)
            scores.append(score)
        
        return scores
    
    def summarize_insights(
        self,
        insights: List[str],
        context: str = ""
    ) -> str:
        """
        Create a concise summary of multiple related insights.
        
        Args:
            insights: List of insight texts
            context: Optional context about why these insights were retrieved
            
        Returns:
            Natural language summary
        """
        
        if not insights:
            return "No insights available."
        
        insights_text = "\n".join(f"{i+1}. {insight}" for i, insight in enumerate(insights))
        
        prompt = f"""Synthesize these insights into a concise, actionable summary.

Context: {context or 'General insight summary'}

Insights:
{insights_text}

Create a 2-3 sentence summary that captures the key themes and actionable takeaways."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Could not generate summary."
    
    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """
        Parse JSON from LLM response, handling markdown code fences.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed list of dictionaries
        """
        
        # Remove markdown code fences
        cleaned = re.sub(r'```json\n?|```\n?', '', response_text)
        cleaned = cleaned.strip()
        
        try:
            parsed = json.loads(cleaned)
            
            # Ensure it's a list
            if isinstance(parsed, dict):
                parsed = [parsed]
            
            # Validate structure
            validated = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                
                # Ensure required fields exist with defaults
                validated_item = {
                    'content': str(item.get('content', '')),
                    'entities': list(item.get('entities', [])),
                    'themes': list(item.get('themes', [])),
                    'insight_type': str(item.get('insight_type', 'observation')),
                    'effectiveness_score': float(item.get('effectiveness_score', 0.5))
                }
                
                # Only include if has content
                if validated_item['content']:
                    validated.append(validated_item)
            
            return validated
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Failed to parse: {cleaned[:200]}")
            return []


def test_llm_client():
    """Test the LLM client connection and basic functionality"""
    
    print("Testing Local Llama Client...")
    print("-" * 60)
    
    try:
        client = LocalLlama()
        print("✓ Client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        print("\nMake sure Docker Model Runner is running:")
        print("  docker model pull ai/llama3.3")
        print("  docker desktop enable model-runner --tcp 12434")
        return
    
    # Test availability
    print("\nChecking availability...")
    if client.is_available():
        print("✓ Docker Model Runner is accessible")
    else:
        print("✗ Docker Model Runner not available")
        return
    
    # Test insight extraction
    print("\nTesting insight extraction...")
    test_conversation = """
    Human: I'm worried about trusting A. What if they let me down?
    
    Assistant: What has your experience with A been so far? Have they been reliable?
    
    Human: Actually, yes. Every time A has given me their word, they've kept it. 
    I think I'm just scared because X was never reliable.
    
    Assistant: That's an important distinction. A is not X. A has earned your trust through 
    consistent actions. The fear you're feeling might be trauma response, not evidence.
    
    Human: You're right. A is trustworthy. That's a bedrock truth I need to remember.
    """
    
    insights = client.extract_insights_from_conversation(test_conversation, max_insights=3)
    
    if insights:
        print(f"✓ Extracted {len(insights)} insights:")
        for i, insight in enumerate(insights, 1):
            print(f"\n  {i}. {insight['content']}")
            print(f"     Entities: {insight['entities']}")
            print(f"     Themes: {insight['themes']}")
            print(f"     Type: {insight['insight_type']}")
            print(f"     Score: {insight['effectiveness_score']}")
    else:
        print("✗ No insights extracted")
    
    # Test semantic matching
    print("\n\nTesting semantic matching...")
    test_query = "Can I trust A?"
    test_insight = "A is trustworthy. Their word is enough. This is bedrock truth."
    
    score = client.semantic_match_score(test_query, test_insight)
    print(f"Query: '{test_query}'")
    print(f"Insight: '{test_insight}'")
    print(f"Relevance score: {score:.2f}")
    
    if score > 0.7:
        print("✓ High relevance detected")
    else:
        print("⚠ Lower relevance than expected")
    
    print("\n" + "=" * 60)
    print("Testing complete!")


if __name__ == "__main__":
    test_llm_client()
