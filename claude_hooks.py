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
from config import Config
from logging_config import get_logger

class ConversationMonitor:
    def __init__(self):
        self.memory_client = MemoryClient()
        self.logger = get_logger('claude_hooks')
        
        # Pre-compile regex patterns for better performance
        self.trigger_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in Config.INSIGHT_PATTERNS]
        
        # Crisis detection patterns - pre-compiled
        self.crisis_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in Config.CRISIS_PATTERNS]
        
        # Patterns that suggest insights should be captured - pre-compiled
        insight_pattern_strings = [
            r'I (?:realized|learned|discovered|understood) that',
            r'What worked was',
            r'The strategy that helped',
            r'I now (?:understand|see) that',
            r'(?:breakthrough|insight|realization)',
            r'This (?:really|finally) (?:worked|helped|clicked)'
        ]
        self.insight_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in insight_pattern_strings]
        
        # Pre-compile extraction patterns for better performance
        self.realized_pattern = re.compile(
            r'I (?:realized|learned|discovered|understood) that (.+?)(?:[.!]|$)',
            re.IGNORECASE
        )
        self.worked_pattern = re.compile(
            r'(?:What worked was|The strategy that helped (?:was|me)?) (.+?)(?:[.!]|$)',
            re.IGNORECASE
        )
    
    def should_query_memory(self, text: str) -> bool:
        """Check if text contains triggers that should query memory"""
        for pattern in self.trigger_patterns:
            if pattern.search(text):
                self.logger.debug(f"Memory trigger detected: {pattern.pattern}")
                return True
        
        return False
    
    def detect_crisis(self, text: str) -> bool:
        """Check if text contains crisis indicators"""
        for pattern in self.crisis_patterns:
            if pattern.search(text):
                self.logger.warning(f"Crisis pattern detected: {pattern.pattern}")
                return True
        return False
    
    def should_capture_insight(self, text: str) -> bool:
        """Check if text contains patterns suggesting new insights"""
        for pattern in self.insight_patterns:
            if pattern.search(text):
                self.logger.debug(f"Insight pattern detected: {pattern.pattern}")
                return True
        
        return False
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return memory insights if relevant"""
        if not user_input.strip():
            return ""
        
        try:
            # Check if memory server is running
            if not self.memory_client.is_server_running():
                self.logger.debug("Memory server not running")
                return ""
            
            insights_text = ""
            
            # Check for crisis indicators first
            if self.detect_crisis(user_input):
                insights_text += "\n\n**🚨 Crisis Support Detected - Anchoring Context:**\n"
                # Query for anchor-type insights specifically
                result = self.memory_client.query_memory(f"anchor trust {user_input}", max_results=3)
            elif self.should_query_memory(user_input):
                # Regular memory query
                result = self.memory_client.query_memory(user_input, max_results=2)
            else:
                return ""
            
            if "error" not in result and result.get("insights"):
                insights = result["insights"]
                if insights:
                    if not insights_text:  # Only add header if not already added for crisis
                        insights_text += "\n\n**🧠 Memory System - Relevant Context:**\n"
                    
                    for insight in insights:
                        type_emoji = {
                            "anchor": "⚓",
                            "breakthrough": "💡", 
                            "strategy": "🎯",
                            "observation": "👁️"
                        }.get(insight.get("type", "observation"), "•")
                        
                        insights_text += f"{type_emoji} {insight['content']}\n"
                    
                    self.logger.info(f"Retrieved {len(insights)} relevant insights")
            
            return insights_text
            
        except Exception as e:
            self.logger.error(f"Error processing user input: {e}")
            return ""
    
    def suggest_insight_capture(self, conversation_text: str) -> str:
        """Suggest capturing insights from conversation"""
        try:
            if not self.should_capture_insight(conversation_text):
                return ""
            
            # Extract potential insights using pre-compiled patterns
            insights = []
            
            # Look for "I realized" patterns
            realized_matches = self.realized_pattern.findall(conversation_text)
            for match in realized_matches:
                match_stripped = match.strip()
                if len(match_stripped) > 10 and len(match_stripped) < 500:
                    insights.append({
                        "content": match_stripped,
                        "type": "observation",
                        "entities": extract_entities_from_text(match),
                        "themes": extract_themes_from_text(match)
                    })
            
            # Look for "what worked" patterns
            worked_matches = self.worked_pattern.findall(conversation_text)
            for match in worked_matches:
                match_stripped = match.strip()
                if len(match_stripped) > 10 and len(match_stripped) < 500:
                    insights.append({
                        "content": match_stripped,
                        "type": "strategy",
                        "entities": extract_entities_from_text(match),
                        "themes": extract_themes_from_text(match)
                    })
            
            if insights:
                self.logger.info(f"Detected {len(insights)} potential insights to capture")
                suggestion = "\n\n**💡 Potential insights detected to add to memory:**\n"
                for i, insight in enumerate(insights):
                    suggestion += f"{i+1}. [{insight['type'].title()}] {insight['content']}\n"
                
                return suggestion
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error suggesting insight capture: {e}")
            return ""

def user_prompt_submit_hook():
    """Hook that runs when user submits a prompt"""
    logger = get_logger('claude_hooks')
    try:
        # Get user input from command line arguments
        if len(sys.argv) < 2:
            return
        
        user_input = " ".join(sys.argv[1:])
        logger.debug(f"Processing user input: {user_input[:100]}...")
        
        monitor = ConversationMonitor()
        insights = monitor.process_user_input(user_input)
        
        if insights:
            print(insights, file=sys.stderr)
            logger.info("Insights provided to user")
            
    except Exception as e:
        logger.error(f"Error in user prompt submit hook: {e}")
        # Continue without disrupting Claude

def post_response_hook():
    """Hook that runs after Claude responds"""
    logger = get_logger('claude_hooks')
    try:
        # Read the full conversation from stdin
        conversation = sys.stdin.read()
        logger.debug(f"Processing conversation: {len(conversation)} characters")
        
        monitor = ConversationMonitor()
        suggestions = monitor.suggest_insight_capture(conversation)
        
        if suggestions:
            print(suggestions, file=sys.stderr)
            logger.info("Insight suggestions provided")
            
    except Exception as e:
        logger.error(f"Error in post response hook: {e}")
        # Continue without disrupting Claude

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