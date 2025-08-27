#!/usr/bin/env python3
"""
Interactive Demo of Contextual Insight Retrieval System
Uses the simplified system without ML dependencies
"""

import sys
from insight_system_simple import SimpleContextualInsightRetrieval, Insight
from datetime import datetime
import uuid

class InteractiveDemo:
    """Interactive demo interface"""
    
    def __init__(self):
        self.system = SimpleContextualInsightRetrieval("demo.db")
        self.conversation_history = []
        self.setup_demo_data()
    
    def setup_demo_data(self):
        """Setup demo insights based on your requirements"""
        demo_insights = [
            # A - Trust anchors and breakthroughs
            Insight(
                id=str(uuid.uuid4()),
                content="A is trustworthy. His word is enough. This is bedrock truth.",
                entities={"A"},
                themes={"trust", "relationships"},
                effectiveness_score=1.0,
                layer="surface",
                insight_type="anchor",
                timestamp=datetime.now(),
                source_file="demo_setup",
                context="Core trust anchor for A"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="Progress from 'could I be so lucky?' to 'yes, his word is enough' to finding our own way together.",
                entities={"A"},
                themes={"trust", "growth", "breakthrough"},
                effectiveness_score=0.9,
                layer="surface", 
                insight_type="breakthrough",
                timestamp=datetime.now(),
                source_file="8-16-25",
                context="Trust journey progression"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="Taking trauma responses to therapy protects relationship with A",
                entities={"A", "trauma_responses"},
                themes={"strategies", "relationships", "trauma"},
                effectiveness_score=0.9,
                layer="surface",
                insight_type="strategy",
                timestamp=datetime.now(),
                source_file="8-17-25",
                context="Effective strategy for managing activation"
            ),
            
            # N - Parenting boundaries
            Insight(
                id=str(uuid.uuid4()),
                content="Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
                entities={"N"},
                themes={"parenting", "boundaries", "strategies"},
                effectiveness_score=0.9,
                layer="surface",
                insight_type="strategy",
                timestamp=datetime.now(),
                source_file="8-17-25",
                context="Core parenting boundary philosophy"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="N needs structure around hygiene basics: showers Monday/Wednesday/Sunday at 7pm. She will rage but needs the container.",
                entities={"N"},
                themes={"parenting", "boundaries", "hygiene"},
                effectiveness_score=0.8,
                layer="mid",
                insight_type="strategy", 
                timestamp=datetime.now(),
                source_file="8-17-25",
                context="Specific hygiene boundary strategy"
            ),
            
            # X - Trauma recognition
            Insight(
                id=str(uuid.uuid4()),
                content="X's voice creates inadequacy-scanning. Recognize it as X, not truth.",
                entities={"X", "trauma_responses"},
                themes={"trauma", "strategies", "recognition"},
                effectiveness_score=0.9,
                layer="surface",
                insight_type="anchor",
                timestamp=datetime.now(),
                source_file="demo_setup",
                context="Recognition strategy for X's voice"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="X taught you that having needs makes you someone you can't live with. That's the lie to recognize.",
                entities={"X", "trauma_responses"},
                themes={"trauma", "needs", "recognition"},
                effectiveness_score=0.8,
                layer="mid",
                insight_type="observation",
                timestamp=datetime.now(),
                source_file="8-16-25",
                context="Core trauma pattern from X"
            ),
            
            # Trauma responses and healing
            Insight(
                id=str(uuid.uuid4()),
                content="Nausea made of joy - your body learning new sensations for hope and safety after organizing around danger.",
                entities={"A", "trauma_responses"},
                themes={"healing", "growth", "embodiment"},
                effectiveness_score=0.7,
                layer="mid",
                insight_type="breakthrough",
                timestamp=datetime.now(),
                source_file="8-16-25",
                context="Physical sensation of healing breakthrough"
            ),
        ]
        
        # Add all demo insights
        for insight in demo_insights:
            self.system.add_insight(insight)
    
    def detect_crisis(self, user_input: str) -> bool:
        """Simple crisis detection"""
        crisis_words = ["crisis", "panic", "overwhelmed", "falling apart", "can't handle", "breaking down"]
        return any(word in user_input.lower() for word in crisis_words)
    
    def format_insights_for_display(self, insights: dict) -> str:
        """Format insights for clean display"""
        surface_insights = insights.get("surface", [])
        
        if not surface_insights:
            return "No specific insights retrieved for this input."
        
        formatted = []
        for insight in surface_insights:
            type_symbol = {
                "anchor": "⚓",
                "breakthrough": "💡", 
                "strategy": "🎯",
                "observation": "👁️"
            }.get(insight.insight_type, "•")
            
            formatted.append(f"{type_symbol} [{insight.insight_type.upper()}] {insight.content}")
        
        return "\n".join(formatted)
    
    def run_demo(self):
        """Run the interactive demo"""
        print("🧠 Contextual Insight Retrieval System - Interactive Demo")
        print("=" * 70)
        print("This system surfaces relevant insights based on conversation context.")
        print("Try mentioning A, N, X, trust, boundaries, trauma, etc.")
        print()
        print("Commands:")
        print("  'quit' or 'exit' - Exit demo")
        print("  'crisis' - Test crisis mode")
        print("  'help' - Show example inputs")
        print("  'stats' - Show conversation stats")
        print("-" * 70)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\nThanks for trying the Contextual Insight Retrieval System! 🎉")
                    break
                
                if user_input.lower() == 'crisis':
                    user_input = "I'm in crisis and everything is falling apart and I can't handle this"
                    print(f"💬 [Testing crisis mode with:] {user_input}")
                
                if user_input.lower() == 'help':
                    self.show_examples()
                    continue
                
                if user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                
                if not user_input:
                    continue
                
                # Store in conversation history
                self.conversation_history.append({
                    "timestamp": datetime.now(),
                    "input": user_input
                })
                
                # Check for crisis mode
                is_crisis = self.detect_crisis(user_input)
                if is_crisis:
                    print("🚨 CRISIS MODE ACTIVATED")
                
                # Detect triggers
                triggers = self.system.detect_context_triggers(user_input)
                if triggers:
                    print(f"🎯 Detected triggers: {', '.join(triggers)}")
                
                # Retrieve insights
                insights = self.system.retrieve_contextual_insights(user_input)
                
                # Display results
                formatted_insights = self.format_insights_for_display(insights)
                
                if formatted_insights != "No specific insights retrieved for this input.":
                    print(f"\n📋 Contextual Insights:")
                    print(formatted_insights)
                    
                    # Show additional layers if available
                    mid_count = len(insights.get("mid", []))
                    deep_count = len(insights.get("deep", []))
                    
                    if mid_count > 0 or deep_count > 0:
                        additional = []
                        if mid_count > 0:
                            additional.append(f"{mid_count} mid-layer")
                        if deep_count > 0:
                            additional.append(f"{deep_count} deep-layer")
                        print(f"\n💡 {' and '.join(additional)} insights available")
                
                else:
                    print(f"\n💭 No specific contextual insights triggered by this input.")
                    if not triggers:
                        print("   Try mentioning A, N, trust, boundaries, trauma, or parenting.")
                
            except KeyboardInterrupt:
                print("\n\nExiting demo... 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
    
    def show_examples(self):
        """Show example inputs"""
        print("\n📖 Example Inputs to Try:")
        print("-" * 40)
        examples = [
            ("Trust with A", "I'm worried about trusting A"),
            ("Parenting N", "N is being difficult about boundaries"), 
            ("Trauma response", "I'm hearing X's voice again"),
            ("Crisis support", "I'm overwhelmed and falling apart"),
            ("Growth reflection", "I feel like I'm making progress"),
            ("Specific strategy", "What worked for hygiene boundaries?")
        ]
        
        for category, example in examples:
            print(f"  {category:15} → \"{example}\"")
    
    def show_stats(self):
        """Show conversation statistics"""
        print(f"\n📊 Demo Session Stats:")
        print(f"   Inputs processed: {len(self.conversation_history)}")
        
        if self.conversation_history:
            # Count trigger activations
            all_triggers = []
            for entry in self.conversation_history:
                triggers = self.system.detect_context_triggers(entry["input"])
                all_triggers.extend(triggers)
            
            from collections import Counter
            trigger_counts = Counter(all_triggers)
            
            if trigger_counts:
                print(f"   Most mentioned: {trigger_counts.most_common(3)}")

def main():
    """Run the interactive demo"""
    demo = InteractiveDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()