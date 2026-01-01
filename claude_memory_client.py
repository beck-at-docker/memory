#!/usr/bin/env python3
"""
Claude Memory Client
Tools for Claude to interact with the memory system
"""

import requests
import json
import re
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Set
from config import Config
from logging_config import get_logger

# Entity mapping - converts single letter codes to descriptive names
ENTITY_MAPPING = {
    'A': 'partner_A',
    'N': 'child_N', 
    'X': 'ex_X',
    'beck': 'self_beck'
}

# Reverse mapping for backward compatibility
REVERSE_ENTITY_MAPPING = {v: k for k, v in ENTITY_MAPPING.items()}

# Known entity patterns - descriptive names with detection rules
ENTITY_PATTERNS = {
    'partner_A': {
        'indicators': [r'\bA\b', r'\bpartner\b', r'\bhusband\b', r'\brelationship with A\b'],
        'context_keywords': ['trust', 'relationship', 'word', 'lucky'],
        'priority': 1
    },
    'child_N': {
        'indicators': [r'\bN\b', r'\bson\b', r'\bchild\b', r'\bkid\b'],
        'context_keywords': ['school', 'hygiene', 'parenting', 'boundaries', 'yells', 'swears'],
        'priority': 1
    },
    'ex_X': {
        'indicators': [r'\bX\b', r'\bex\b', r'\babsent parent\b'],
        'context_keywords': ['voice', 'trauma', 'contact', 'charming', 'case'],
        'priority': 1
    },
    'self_beck': {
        'indicators': [r'\bbeck\b', r'\bI\s+', r'\bmy\s+', r'\bmyself\b', r'\bme\b'],
        'context_keywords': ['strength', 'doing the right thing', 'protective', 'strategic'],
        'priority': 2  # Lower priority since "I/my/me" are common
    },
    'trauma_responses': {
        'indicators': [r'\btrauma\b', r'\btriggered\b', r'\bactivation\b', r'\bnervous system\b'],
        'context_keywords': ['danger', 'response', 'disproportionate'],
        'priority': 1
    },
    'internal_voice': {
        'indicators': [r'\binternal voice\b', r'\bvoice in my head\b', r'\bself-talk\b', r'\bsabotage\b'],
        'context_keywords': ['reality inversion', 'weaponization'],
        'priority': 1
    }
}


def normalize_entity(entity: str) -> str:
    """
    Convert entity to normalized form (descriptive name).
    
    Args:
        entity: Entity name (could be single letter or descriptive)
    
    Returns:
        Normalized descriptive entity name
    """
    # If it's already a descriptive name, return as-is
    if entity in REVERSE_ENTITY_MAPPING:
        return entity
    
    # If it's a single letter, convert to descriptive
    if entity in ENTITY_MAPPING:
        return ENTITY_MAPPING[entity]
    
    # Otherwise return as-is (might be a new entity)
    return entity


def denormalize_entity(entity: str) -> str:
    """
    Convert descriptive entity name back to single letter if applicable.
    
    Args:
        entity: Descriptive entity name
    
    Returns:
        Single letter code if one exists, otherwise original name
    """
    return REVERSE_ENTITY_MAPPING.get(entity, entity)


class MemoryClient:
    """Client for interacting with memory API"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8001"):
        self.api_url = api_url
        self.logger = get_logger('claude_memory_client')
        
        # Check if running from allowed project directory
        allowed_project = os.path.expanduser("~/Documents/private")
        current_dir = os.getcwd()
        
        if not current_dir.startswith(allowed_project):
            raise PermissionError(f"Memory client access denied from: {current_dir}. Must run from: {allowed_project}")
        
        # Generate token based on memory project directory using same method as server
        self.access_token = Config.generate_secure_token(current_dir)
        self.headers = {"X-Memory-Token": self.access_token}
        
    def is_server_running(self) -> bool:
        """Check if memory server is running"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def query_memory(self, user_input: str, max_results: int = 3) -> Dict:
        """Query memory for relevant insights"""
        if not user_input.strip():
            self.logger.warning("Empty input provided to query_memory")
            return {"error": "Empty input"}
        
        try:
            self.logger.debug(f"Querying memory with input: {user_input[:100]}...")
            
            response = requests.post(
                f"{self.api_url}/query", 
                json={"input": user_input, "max_results": max_results},
                headers=self.headers,
                timeout=Config.READ_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Query returned {len(result.get('insights', []))} insights")
                return result
            else:
                error_msg = f"API error: {response.status_code}"
                self.logger.error(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Connection error: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}
    
    def add_insight(self, content: str, entities: List[str], themes: List[str], 
                   insight_type: str = "observation", effectiveness_score: float = 0.5) -> Dict:
        """
        Add new insight to memory.
        
        Args:
            content: The insight content
            entities: List of entities (will be normalized to descriptive names)
            themes: List of themes
            insight_type: Type of insight
            effectiveness_score: Score from 0-1
        
        Returns:
            Result dictionary
        """
        if not content.strip():
            self.logger.warning("Empty content provided to add_insight")
            return {"error": "Empty content"}
        
        # Normalize all entities to descriptive names
        normalized_entities = [normalize_entity(e) for e in entities]
        
        try:
            self.logger.debug(f"Adding insight: {content[:100]}...")
            
            response = requests.post(
                f"{self.api_url}/add", 
                json={
                    "content": content,
                    "entities": normalized_entities,
                    "themes": themes,
                    "insight_type": insight_type,
                    "effectiveness_score": effectiveness_score,
                    "context": f"Added by Claude at {datetime.now().isoformat()}"
                },
                headers=self.headers,
                timeout=Config.READ_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Successfully added insight: {result.get('insight_id')}")
                return result
            else:
                error_msg = f"API error: {response.status_code}"
                self.logger.error(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Connection error: {str(e)}")
            return {"error": f"Connection error: {str(e)}"}
    
    def get_status(self) -> Dict:
        """Get memory system status"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=Config.CONNECTION_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                self.logger.debug(f"Memory system status: {result.get('status')}")
                return result
            else:
                error_msg = f"API error: {response.status_code}"
                self.logger.error(error_msg)
                return {"error": error_msg}
        except Exception as e:
            self.logger.error(f"Cannot connect to memory server: {e}")
            return {"error": "Cannot connect to memory server"}


def extract_insights_from_conversation(conversation_text: str) -> List[Dict]:
    """
    Extract potential insights from conversation text.
    This is a simple pattern-based extractor.
    """
    insights = []
    
    # Patterns that might indicate insights
    insight_patterns = [
        r"I realized that (.+)",
        r"What worked was (.+)",
        r"The strategy that helped was (.+)",
        r"I learned that (.+)",
        r"It's important to remember (.+)",
        r"The key insight is (.+)",
        r"What I discovered is (.+)",
        r"I now understand that (.+)"
    ]
    
    for pattern in insight_patterns:
        matches = re.findall(pattern, conversation_text, re.IGNORECASE)
        for match in matches:
            if len(match.strip()) > 10:  # Only meaningful insights
                insights.append({
                    "content": match.strip(),
                    "entities": extract_entities_from_text(match),
                    "themes": extract_themes_from_text(match),
                    "insight_type": "observation",
                    "effectiveness_score": 0.6
                })
    
    return insights


def extract_entities_from_text(text: str) -> List[str]:
    """
    Extract entity mentions from text using pattern matching.
    Returns normalized descriptive entity names.
    
    Args:
        text: Text to extract entities from
    
    Returns:
        List of normalized entity names
    """
    entities = set()
    text_lower = text.lower()
    
    # Check each entity pattern
    for entity_name, pattern_info in ENTITY_PATTERNS.items():
        matched = False
        
        # Check if any indicator pattern matches
        for indicator_pattern in pattern_info['indicators']:
            if re.search(indicator_pattern, text, re.IGNORECASE):
                matched = True
                break
        
        # For high-priority entities, also check context keywords for confidence
        if matched:
            if pattern_info['priority'] == 1:
                # High priority - add immediately
                entities.add(entity_name)
            else:
                # Lower priority - require context keyword confirmation
                has_context = any(
                    keyword.lower() in text_lower 
                    for keyword in pattern_info.get('context_keywords', [])
                )
                if has_context or len([i for i in pattern_info['indicators'] if re.search(i, text, re.IGNORECASE)]) > 1:
                    entities.add(entity_name)
    
    return sorted(entities)


def extract_themes_from_text(text: str) -> List[str]:
    """Extract themes from text"""
    themes = []
    text_lower = text.lower()
    
    theme_keywords = {
        "trust": ["trust", "trusting", "trustworthy", "faith", "reliable"],
        "boundaries": ["boundary", "boundaries", "limit", "limits", "structure", "line"],
        "trauma": ["trauma", "triggered", "activation", "nervous system", "ptsd"],
        "parenting": ["parent", "parenting", "discipline", "school", "child", "kid"],
        "relationships": ["relationship", "connection", "bond", "partnership"],
        "strategies": ["strategy", "approach", "method", "technique", "worked", "effective"],
        "growth": ["growth", "progress", "breakthrough", "learning", "development", "improvement"],
        "safety": ["safety", "safe", "protection", "secure"],
        "love": ["love", "loving", "care", "caring", "compassion"],
        "fear": ["fear", "afraid", "scared", "worry", "anxious"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    return themes


def format_insights_for_claude(insights: List[Dict]) -> str:
    """Format insights for Claude to use in conversation"""
    if not insights:
        return ""
    
    formatted = ["**Relevant Memory Insights:**"]
    
    for insight in insights:
        type_emoji = {
            "anchor": "⚓",
            "breakthrough": "💡", 
            "strategy": "🎯",
            "observation": "👁️"
        }.get(insight.get("type", "observation"), "•")
        
        formatted.append(f"{type_emoji} {insight['content']}")
        
        if insight.get('entities'):
            # Display entities in readable format
            entity_display = ', '.join([denormalize_entity(e) for e in insight['entities']])
            formatted.append(f"   *Relates to: {entity_display}*")
    
    return "\n".join(formatted)


# CLI functions for testing
def test_entity_extraction():
    """Test the improved entity extraction"""
    test_cases = [
        "I'm worried about trusting A",
        "N is being difficult about boundaries today",
        "X's voice is making me feel inadequate",
        "I had trauma responses when thinking about the situation",
        "My internal voice is sabotaging me",
        "The child needs structure",  # Should match child_N
        "A says I'm doing well",  # Should match partner_A
        "Contact with X triggers me",  # Should match ex_X and trauma_responses
    ]
    
    print("Testing Entity Extraction")
    print("=" * 60)
    
    for test_text in test_cases:
        entities = extract_entities_from_text(test_text)
        themes = extract_themes_from_text(test_text)
        print(f"\nText: {test_text}")
        print(f"Entities: {entities}")
        print(f"Themes: {themes}")


def test_memory_system():
    """Test the memory system connection"""
    client = MemoryClient()
    
    print("\nTesting Memory System Connection")
    print("=" * 60)
    
    # Test server status
    if not client.is_server_running():
        print("❌ Memory server is not running")
        print("Start it with: python3 memory_api.py")
        return
    
    print("✅ Memory server is running")
    
    # Test status endpoint
    status = client.get_status()
    print(f"📊 Status: {status}")
    
    # Test query
    print("\nTesting query...")
    result = client.query_memory("I'm worried about trusting A")
    print(f"🔍 Query result: {json.dumps(result, indent=2)}")
    
    # Test adding insight with new entity names
    print("\nTesting add insight with normalized entities...")
    add_result = client.add_insight(
        content="Testing improved entity extraction with descriptive names",
        entities=["partner_A", "trauma_responses"],  # Using descriptive names
        themes=["testing", "integration"],
        insight_type="observation"
    )
    print(f"➕ Add result: {add_result}")


if __name__ == "__main__":
    print("Entity Extraction Tests:")
    test_entity_extraction()
    
    print("\n" + "=" * 60)
    print("\nMemory System Tests:")
    test_memory_system()
