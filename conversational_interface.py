#!/usr/bin/env python3
"""
Conversational Interface for Contextual Insight Retrieval
Provides natural conversation flow with intelligent insight integration
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

from insight_retrieval_system import ContextualInsightRetrieval, Insight

class ConversationFlow:
    """Manages natural conversation flow with insight integration"""
    
    def __init__(self, system: ContextualInsightRetrieval):
        self.system = system
        self.conversation_history = []
        self.active_entities = set()
        self.last_insights_surfaced = []
        
    def process_user_input(self, user_input: str) -> Tuple[str, Dict[str, List[Insight]]]:
        """Process user input and determine if insights should be surfaced"""
        
        # Store user input in history
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "speaker": "user",
            "content": user_input
        })
        
        # Detect if insights should be retrieved
        should_surface_insights, confidence = self._should_surface_insights(user_input)
        
        if should_surface_insights:
            insights = self.system.retrieve_contextual_insights(user_input, max_insights=5)
            
            # Update active entities based on retrieved insights
            self._update_active_entities(insights)
            
            # Store what insights were surfaced to avoid repetition
            self.last_insights_surfaced = insights.get("surface", [])
            
            return self._format_insights_for_conversation(insights), insights
        
        return "", {}
    
    def _should_surface_insights(self, user_input: str) -> Tuple[bool, float]:
        """Determine if insights should be surfaced based on user input"""
        user_lower = user_input.lower()
        
        # High confidence triggers - direct entity mentions
        high_confidence_triggers = [
            r'\bA\b', r'trusting A', r'trust.*A', r'relationship with A',
            r'\bN\b', r'parenting', r'boundaries.*N', r'school',
            r'\bX\b', r"X's voice", r'trauma response', r'triggered',
            r'strategies', r'what worked', r'help.*with'
        ]
        
        for pattern in high_confidence_triggers:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True, 0.9
        
        # Medium confidence triggers - thematic mentions
        medium_confidence_triggers = [
            r'trust', r'boundaries', r'trauma', r'activation',
            r'nervous system', r'shutdown', r'hygiene', r'shower',
            r'anger', r'structure', r'discipline'
        ]
        
        medium_matches = sum(1 for pattern in medium_confidence_triggers 
                           if re.search(pattern, user_input, re.IGNORECASE))
        
        if medium_matches >= 2:
            return True, 0.7
        elif medium_matches == 1:
            return True, 0.5
        
        # Low confidence triggers - emotional states that might benefit from context
        emotional_triggers = [
            r'worried', r'scared', r'anxious', r'overwhelmed',
            r'struggling', r'difficult', r'hard', r'challenging'
        ]
        
        emotional_matches = sum(1 for pattern in emotional_triggers 
                              if re.search(pattern, user_input, re.IGNORECASE))
        
        if emotional_matches >= 1 and len(user_input) > 50:
            return True, 0.3
        
        return False, 0.0
    
    def _update_active_entities(self, insights: Dict[str, List[Insight]]):
        """Update active entities based on retrieved insights"""
        for layer_insights in insights.values():
            for insight in layer_insights:
                self.active_entities.update(insight.entities)
        
        # Keep only recent entities (last 10 turns)
        if len(self.conversation_history) > 20:
            self.active_entities = set()
    
    def _format_insights_for_conversation(self, insights: Dict[str, List[Insight]]) -> str:
        """Format insights for natural conversation integration"""
        surface_insights = insights.get("surface", [])
        
        if not surface_insights:
            return ""
        
        # Group insights by type for better presentation
        anchors = [i for i in surface_insights if i.insight_type == "anchor"]
        breakthroughs = [i for i in surface_insights if i.insight_type == "breakthrough"]
        strategies = [i for i in surface_insights if i.insight_type == "strategy"]
        observations = [i for i in surface_insights if i.insight_type == "observation"]
        
        formatted_parts = []
        
        # Prioritize crisis anchors
        if anchors:
            for anchor in anchors[:1]:  # Usually just show one anchor
                formatted_parts.append(f"[Anchor: {anchor.content}]")
        
        # Show breakthroughs
        if breakthroughs:
            for breakthrough in breakthroughs[:1]:
                formatted_parts.append(f"[Breakthrough: {breakthrough.content}]")
        
        # Show relevant strategies
        if strategies:
            for strategy in strategies[:2]:
                formatted_parts.append(f"[Strategy: {strategy.content}]")
        
        # Show key observations if space allows
        if observations and len(formatted_parts) < 3:
            for observation in observations[:1]:
                formatted_parts.append(f"[Context: {observation.content}]")
        
        return "\n".join(formatted_parts) if formatted_parts else ""
    
    def get_conversation_summary(self) -> Dict[str, any]:
        """Get summary of current conversation state"""
        return {
            "active_entities": list(self.active_entities),
            "conversation_length": len(self.conversation_history),
            "last_insights_count": len(self.last_insights_surfaced),
            "recent_themes": self._extract_recent_themes()
        }
    
    def _extract_recent_themes(self) -> List[str]:
        """Extract themes from recent conversation"""
        recent_messages = self.conversation_history[-5:]  # Last 5 messages
        themes = set()
        
        for msg in recent_messages:
            content = msg["content"].lower()
            
            # Theme detection
            if any(word in content for word in ["trust", "trusting", "faith"]):
                themes.add("trust")
            if any(word in content for word in ["boundary", "boundaries", "limit", "structure"]):
                themes.add("boundaries")
            if any(word in content for word in ["trauma", "triggered", "activation"]):
                themes.add("trauma")
            if any(word in content for word in ["parent", "parenting", "discipline"]):
                themes.add("parenting")
        
        return list(themes)

class CrisisMode:
    """Special mode for crisis situations requiring immediate anchoring"""
    
    def __init__(self, system: ContextualInsightRetrieval):
        self.system = system
        self.crisis_keywords = [
            "crisis", "emergency", "panic", "overwhelmed", "can't handle",
            "falling apart", "breaking down", "too much", "spiral"
        ]
    
    def detect_crisis(self, user_input: str) -> bool:
        """Detect if user is in crisis mode"""
        user_lower = user_input.lower()
        
        crisis_count = sum(1 for keyword in self.crisis_keywords 
                         if keyword in user_lower)
        
        # Also check for intensity markers
        intensity_markers = ["really", "so", "very", "extremely", "completely"]
        intensity_count = sum(1 for marker in intensity_markers 
                            if marker in user_lower)
        
        return crisis_count >= 1 or (intensity_count >= 2 and len(user_input) > 100)
    
    def get_crisis_anchors(self, context: str = "") -> List[Insight]:
        """Retrieve crisis anchors immediately"""
        # Get all anchor-type insights
        insights = self.system.retrieve_contextual_insights(context + " crisis anchor", max_insights=10)
        
        # Filter to only anchors and high-effectiveness insights
        crisis_anchors = []
        for layer_insights in insights.values():
            for insight in layer_insights:
                if (insight.insight_type == "anchor" or 
                    insight.effectiveness_score > 0.8):
                    crisis_anchors.append(insight)
        
        # Sort by effectiveness and recency
        crisis_anchors.sort(key=lambda x: (x.effectiveness_score, 
                                         (datetime.now() - x.timestamp).days * -1), 
                          reverse=True)
        
        return crisis_anchors[:3]  # Top 3 crisis anchors

class InsightAPI:
    """API-style interface for the insight retrieval system"""
    
    def __init__(self, db_path: str = "insights.db"):
        self.system = ContextualInsightRetrieval(db_path)
        self.conversation = ConversationFlow(self.system)
        self.crisis_mode = CrisisMode(self.system)
    
    def chat(self, user_input: str, force_insights: bool = False) -> Dict[str, any]:
        """Main chat interface"""
        
        # Check for crisis mode
        is_crisis = self.crisis_mode.detect_crisis(user_input)
        
        if is_crisis:
            crisis_anchors = self.crisis_mode.get_crisis_anchors(user_input)
            return {
                "mode": "crisis",
                "insights": self._format_crisis_response(crisis_anchors),
                "raw_insights": crisis_anchors,
                "conversation_state": self.conversation.get_conversation_summary()
            }
        
        # Normal conversation flow
        formatted_insights, raw_insights = self.conversation.process_user_input(user_input)
        
        response = {
            "mode": "normal",
            "insights": formatted_insights,
            "raw_insights": raw_insights,
            "conversation_state": self.conversation.get_conversation_summary()
        }
        
        # Add progressive disclosure if requested
        if force_insights or len(raw_insights.get("mid", [])) > 0:
            response["mid_layer_available"] = True
            response["mid_layer_count"] = len(raw_insights.get("mid", []))
        
        if len(raw_insights.get("deep", [])) > 0:
            response["deep_layer_available"] = True
            response["deep_layer_count"] = len(raw_insights.get("deep", []))
        
        return response
    
    def get_deeper_context(self, layer: str = "mid") -> Dict[str, any]:
        """Retrieve deeper layers of context"""
        if not self.conversation.last_insights_surfaced:
            return {"error": "No recent insights to expand on"}
        
        # Get the entities from last surfaced insights
        entities = set()
        for insight in self.conversation.last_insights_surfaced:
            entities.update(insight.entities)
        
        # Retrieve deeper insights for those entities
        context_query = " ".join(entities)
        insights = self.system.retrieve_contextual_insights(context_query, max_insights=15)
        
        if layer == "mid":
            return {
                "layer": "mid",
                "insights": self._format_layer_insights(insights.get("mid", [])),
                "count": len(insights.get("mid", []))
            }
        elif layer == "deep":
            return {
                "layer": "deep", 
                "insights": self._format_layer_insights(insights.get("deep", [])),
                "count": len(insights.get("deep", []))
            }
        
        return {"error": "Invalid layer specified"}
    
    def _format_crisis_response(self, crisis_anchors: List[Insight]) -> str:
        """Format crisis anchors for immediate use"""
        if not crisis_anchors:
            return "[Crisis Mode: No specific anchors found, but you are not alone]"
        
        formatted = ["[CRISIS ANCHORS - Hold onto these:]"]
        for anchor in crisis_anchors:
            formatted.append(f"• {anchor.content}")
        
        return "\n".join(formatted)
    
    def _format_layer_insights(self, insights: List[Insight]) -> str:
        """Format insights for a specific layer"""
        if not insights:
            return "No additional context available at this layer."
        
        formatted = []
        for insight in insights:
            type_label = insight.insight_type.title()
            formatted.append(f"[{type_label}] {insight.content}")
            
            # Add context if it's a strategy
            if insight.insight_type == "strategy" and insight.effectiveness_score > 0.6:
                formatted.append(f"  → Effectiveness: {insight.effectiveness_score:.1f}/1.0")
        
        return "\n".join(formatted)
    
    def add_new_insight(self, content: str, entities: List[str], themes: List[str], 
                       insight_type: str = "observation") -> Dict[str, any]:
        """Add a new insight to the system"""
        insight = Insight(
            id=str(uuid.uuid4()),
            content=content,
            entities=set(entities),
            themes=set(themes),
            insight_type=insight_type,
            timestamp=datetime.now(),
            source_file="manual_entry",
            context="Manually added insight"
        )
        
        self.system.add_insight(insight)
        
        return {
            "success": True,
            "insight_id": insight.id,
            "message": "Insight added successfully"
        }

def main():
    """CLI interface for testing"""
    api = InsightAPI()
    
    print("Contextual Insight Retrieval System")
    print("Type 'quit' to exit, 'deeper' for more context, 'crisis' to test crisis mode")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if user_input.lower() == 'deeper':
            result = api.get_deeper_context("mid")
            print("\nDeeper Context:")
            print(result.get("insights", "No additional context available"))
            continue
        
        if user_input.lower() == 'crisis':
            user_input = "I'm in crisis and everything is falling apart"
        
        response = api.chat(user_input)
        
        if response["insights"]:
            print(f"\nInsights ({response['mode']} mode):")
            print(response["insights"])
        
        if response.get("mid_layer_available"):
            print(f"\n💡 {response['mid_layer_count']} additional insights available (type 'deeper')")

if __name__ == "__main__":
    main()