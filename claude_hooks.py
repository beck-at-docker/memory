#!/usr/bin/env python3
"""
Claude Code Hooks for Automatic Memory Integration
Monitors conversations and automatically surfaces relevant insights
"""

import sys
import json
import re
import os
from claude_memory_client import MemoryClient, extract_entities_from_text, extract_themes_from_text

class ConversationMonitor:
    def __init__(self):
        self.memory_client = MemoryClient()
        
        # Patterns that trigger memory queries
        self.trigger_patterns = [
            # Entity mentions
            r'\bA\b(?:\s|[.,!?])', r'\btrust(?:ing)?\s+A\b',
            r'\bN\b(?:\s|[.,!?])', r'\bparenting\b', r'\bboundaries\b',
            r'\bX\b(?:\s|[.,!?])', r"X's voice", r'\btrauma\b',
            
            # Emotional triggers
            r'\bworried\b', r'\bscared\b', r'\banxious\b', r'\boverwhelmed\b',
            r'\bcrisis\b', r'\bpanic\b', r'\bfalling apart\b',
            
            # Relationship themes
            r'\btrust(?:ing)?\b', r'\brelationship\b', r'\bconnection\b',
            
            # Therapeutic themes
            r'\bactivation\b', r'\btriggered\b', r'\bnervous system\b',
            r'\bstrategies\b', r'\bwhat worked\b', r'\bbreakthrough\b'
        ]
        
        # Patterns that suggest insights should be captured
        self.insight_patterns = [
            r'I (?:realized|learned|discovered|understood) that',
            r'What worked was',
            r'The strategy that helped',
            r'I now (?:understand|see) that',
            r'(?:breakthrough|insight|realization)',
            r'This (?:really|finally) (?:worked|helped|clicked)'
        ]
    
    def should_query_memory(self, text: str) -> bool:
        """Check if text contains triggers that should query memory"""
        text_lower = text.lower()
        
        for pattern in self.trigger_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def should_capture_insight(self, text: str) -> bool:
        """Check if text contains patterns suggesting new insights"""
        text_lower = text.lower()
        
        for pattern in self.insight_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return memory insights if relevant"""
        if not user_input.strip():
            return ""
        
        # Check if memory server is running
        if not self.memory_client.is_server_running():
            return ""
        
        insights_text = ""
        
        # Query memory if triggers are detected
        if self.should_query_memory(user_input):
            result = self.memory_client.query_memory(user_input, max_results=2)
            
            if "error" not in result and result.get("insights"):
                insights = result["insights"]
                if insights:
                    insights_text += "\n\n**🧠 Memory System - Relevant Context:**\n"
                    for insight in insights:
                        type_emoji = {
                            "anchor": "⚓",
                            "breakthrough": "💡", 
                            "strategy": "🎯",
                            "observation": "👁️"
                        }.get(insight.get("type", "observation"), "•")
                        
                        insights_text += f"{type_emoji} {insight['content']}\n"
        
        return insights_text
    
    def suggest_insight_capture(self, conversation_text: str) -> str:
        """Suggest capturing insights from conversation"""
        if not self.should_capture_insight(conversation_text):
            return ""
        
        # Extract potential insights
        insights = []
        
        # Look for "I realized" patterns
        realized_matches = re.findall(r'I (?:realized|learned|discovered|understood) that (.+?)(?:[.!]|$)', 
                                    conversation_text, re.IGNORECASE)
        for match in realized_matches:
            if len(match.strip()) > 10:
                insights.append({
                    "content": match.strip(),
                    "type": "observation",
                    "entities": extract_entities_from_text(match),
                    "themes": extract_themes_from_text(match)
                })
        
        # Look for "what worked" patterns
        worked_matches = re.findall(r'(?:What worked was|The strategy that helped (?:was|me)?) (.+?)(?:[.!]|$)', 
                                  conversation_text, re.IGNORECASE)
        for match in worked_matches:
            if len(match.strip()) > 10:
                insights.append({
                    "content": match.strip(),
                    "type": "strategy",
                    "entities": extract_entities_from_text(match),
                    "themes": extract_themes_from_text(match)
                })
        
        if insights:
            suggestion = "\n\n**💡 Potential insights detected to add to memory:**\n"
            for i, insight in enumerate(insights):
                suggestion += f"{i+1}. [{insight['type'].title()}] {insight['content']}\n"
            
            return suggestion
        
        return ""

def user_prompt_submit_hook():
    """Hook that runs when user submits a prompt"""
    try:
        # Get user input from command line arguments
        if len(sys.argv) < 2:
            return
        
        user_input = " ".join(sys.argv[1:])
        
        monitor = ConversationMonitor()
        insights = monitor.process_user_input(user_input)
        
        if insights:
            print(insights, file=sys.stderr)
            
    except Exception as e:
        # Silently fail to avoid disrupting Claude
        pass

def post_response_hook():
    """Hook that runs after Claude responds"""
    try:
        # Read the full conversation from stdin
        conversation = sys.stdin.read()
        
        monitor = ConversationMonitor()
        suggestions = monitor.suggest_insight_capture(conversation)
        
        if suggestions:
            print(suggestions, file=sys.stderr)
            
    except Exception:
        # Silently fail to avoid disrupting Claude
        pass

if __name__ == "__main__":
    # Determine which hook to run based on script name or argument
    script_name = os.path.basename(sys.argv[0])
    
    if "submit" in script_name or (len(sys.argv) > 1 and sys.argv[1] == "submit"):
        user_prompt_submit_hook()
    elif "response" in script_name or (len(sys.argv) > 1 and sys.argv[1] == "response"):
        post_response_hook()
    else:
        # Default to submit hook
        user_prompt_submit_hook()