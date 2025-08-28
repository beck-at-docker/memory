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
from typing import List, Dict, Optional

class MemoryClient:
    """Client for interacting with memory API"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url
        
        # Check if running from allowed project directory
        allowed_project = os.path.expanduser("~/Documents/private/memory")
        current_dir = os.getcwd()
        
        if not current_dir.startswith(allowed_project):
            raise PermissionError(f"Memory client access denied from: {current_dir}. Must run from: {allowed_project}")
        
        # Generate token based on memory project directory
        self.access_token = hashlib.sha256(allowed_project.encode()).hexdigest()[:16]
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
        """Add new insight to memory"""
        if not content.strip():
            self.logger.warning("Empty content provided to add_insight")
            return {"error": "Empty content"}
        
        try:
            self.logger.debug(f"Adding insight: {content[:100]}...")
            
            response = requests.post(
                f"{self.api_url}/add", 
                json={
                    "content": content,
                    "entities": entities,
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
    Extract potential insights from conversation text
    This is a simple pattern-based extractor
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
    """Extract entity mentions from text"""
    entities = []
    text_upper = text.upper()
    
    # Known entities
    if re.search(r'\bA\b', text_upper):
        entities.append("A")
    if re.search(r'\bN\b', text_upper):
        entities.append("N")  
    if re.search(r'\bX\b', text_upper):
        entities.append("X")
    
    # Common entity patterns
    if any(word in text.lower() for word in ["trauma", "triggered", "activation"]):
        entities.append("trauma_responses")
        
    return entities

def extract_themes_from_text(text: str) -> List[str]:
    """Extract themes from text"""
    themes = []
    text_lower = text.lower()
    
    theme_keywords = {
        "trust": ["trust", "trusting", "trustworthy", "faith"],
        "boundaries": ["boundary", "boundaries", "limit", "limits", "structure"],
        "trauma": ["trauma", "triggered", "activation", "nervous system"],
        "parenting": ["parent", "parenting", "discipline", "school"],
        "relationships": ["relationship", "connection", "bond"],
        "strategies": ["strategy", "approach", "method", "technique", "worked"],
        "growth": ["growth", "progress", "breakthrough", "learning", "development"]
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
            formatted.append(f"   *Relates to: {', '.join(insight['entities'])}*")
    
    return "\n".join(formatted)

# CLI functions for testing
def test_memory_system():
    """Test the memory system connection"""
    client = MemoryClient()
    
    print("Testing Memory System Connection...")
    
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
    
    # Test adding insight
    print("\nTesting add insight...")
    add_result = client.add_insight(
        content="Testing Claude integration with memory system",
        entities=["claude"],
        themes=["testing", "integration"],
        insight_type="observation"
    )
    print(f"➕ Add result: {add_result}")

if __name__ == "__main__":
    test_memory_system()