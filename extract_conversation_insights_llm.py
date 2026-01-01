#!/usr/bin/env python3
"""
Extract insights from conversation files and add them to the memory system
Now with LOCAL LLM support via Docker Model Runner
"""

import os
import re
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from insight_system_simple import SimpleContextualInsightRetrieval, Insight

# Try to import LLM client
try:
    from llm_client import LocalLlama
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠ LLM client not available, will use pattern matching only")


class ConversationInsightExtractor:
    def __init__(self, db_path: str, use_llm: bool = True):
        self.memory_system = SimpleContextualInsightRetrieval(db_path)
        self.use_llm = use_llm and LLM_AVAILABLE
        
        # Try to initialize LLM
        if self.use_llm:
            try:
                self.llm = LocalLlama()
                if self.llm.is_available():
                    print("✓ Using local Llama 3.3 for insight extraction")
                else:
                    print("⚠ Docker Model Runner not available, falling back to pattern matching")
                    self.use_llm = False
            except Exception as e:
                print(f"⚠ Could not initialize LLM: {e}")
                print("  Falling back to pattern matching")
                self.use_llm = False
        else:
            print("ℹ Using pattern-based insight extraction")
        
        # Entity patterns for fallback
        self.entity_patterns = {
            "N": [r'\bN\b', r'N is', r'N was', r'N said', r'N did', r'with N', r'about N'],
            "A": [r'\bA\b', r'A is', r'A was', r'A said', r'A did', r'with A', r'about A', r'trusting A'],
            "B": [r'\bB\b', r'B is', r'B was', r'B said', r'B did', r'with B', r'about B'],
            "E": [r'\bE\b', r'E is', r'E was', r'E said', r'E did', r'with E', r'about E'],
            "X": [r'\bX\b', r'X is', r'X was', r'X said', r'X did', r'with X', r'about X', r"X's voice"]
        }
        
        # Theme keywords for fallback
        self.theme_patterns = {
            "trust": ["trust", "trustworthy", "faith", "reliable", "dependable"],
            "boundaries": ["boundary", "boundaries", "limit", "limits", "say no"],
            "parenting": ["parenting", "parent", "child", "kid", "discipline", "routine"],
            "trauma": ["trauma", "triggered", "activation", "nervous system", "hypervigilant"],
            "healing": ["healing", "recovery", "growth", "breakthrough", "progress"],
            "relationships": ["relationship", "connection", "communication", "conflict"],
            "strategies": ["strategy", "technique", "approach", "method", "works", "effective"],
            "emotions": ["emotion", "feeling", "angry", "sad", "fear", "anxiety", "joy"],
            "communication": ["communicate", "talk", "discuss", "conversation", "express"]
        }
        
        # Insight type patterns for fallback
        self.insight_type_patterns = {
            "anchor": [
                r"fundamental truth", r"bedrock", r"always remember", r"core belief",
                r"foundational", r"unchanging", r"constant", r"reliable truth"
            ],
            "breakthrough": [
                r"breakthrough", r"clicked", r"realized", r"shifted", r"changed everything",
                r"game changer", r"revelation", r"aha moment", r"finally understood"
            ],
            "strategy": [
                r"strategy", r"technique", r"approach", r"method", r"works", r"effective",
                r"helps", r"solution", r"way to", r"how to", r"practice"
            ],
            "observation": [
                r"notice", r"pattern", r"tend to", r"often", r"usually", r"seems like",
                r"appears", r"observe"
            ]
        }
    
    def extract_insights_from_file(self, file_path: str) -> List[Dict]:
        """Extract insights from a single conversation file"""
        insights = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return insights
        
        # Try LLM extraction first
        if self.use_llm:
            try:
                print(f"  → Using LLM to extract insights...")
                llm_insights = self.llm.extract_insights_from_conversation(
                    content, 
                    max_insights=15
                )
                
                if llm_insights:
                    print(f"  → LLM extracted {len(llm_insights)} insights")
                    for insight_data in llm_insights:
                        insight_data['source_file'] = os.path.basename(file_path)
                        insights.append(insight_data)
                    return insights
                else:
                    print(f"  → LLM returned no insights, trying pattern matching...")
                    
            except Exception as e:
                print(f"  → LLM extraction failed ({e}), using pattern matching...")
        
        # Fallback to pattern-based extraction
        chunks = self._split_conversation(content)
        
        for chunk in chunks:
            potential_insights = self._find_insights_in_chunk(chunk)
            for insight_data in potential_insights:
                insight_data['source_file'] = os.path.basename(file_path)
                insights.append(insight_data)
        
        return insights
    
    def _split_conversation(self, content: str) -> List[str]:
        """Split conversation into Human/Assistant pairs"""
        # Split on Human: or Assistant: markers
        parts = re.split(r'(Human:|Assistant:)', content)
        
        chunks = []
        current_chunk = ""
        
        for part in parts:
            if part.strip() in ["Human:", "Assistant:"]:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = part + " "
            else:
                current_chunk += part
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _find_insights_in_chunk(self, chunk: str) -> List[Dict]:
        """Find insights in a conversation chunk using patterns"""
        insights = []
        
        # Look for sentences that contain entity mentions
        sentences = self._split_into_sentences(chunk)
        
        for sentence in sentences:
            # Check if this sentence contains insights
            entities = self._identify_entities(sentence)
            themes = self._identify_themes(sentence)
            insight_type = self._classify_insight_type(sentence)
            
            # Only create insight if it has entities or strong themes
            if entities or len(themes) >= 2:
                # Skip very short sentences or questions
                if len(sentence.split()) < 8 or sentence.strip().endswith('?'):
                    continue
                
                insights.append({
                    'content': sentence.strip(),
                    'entities': list(entities),
                    'themes': list(themes),
                    'insight_type': insight_type,
                    'effectiveness_score': self._assess_effectiveness(sentence),
                    'timestamp': datetime.now().isoformat()
                })
        
        return insights
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - could be improved
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _identify_entities(self, text: str) -> Set[str]:
        """Identify entities mentioned in text"""
        entities = set()
        text_lower = text.lower()
        
        for entity, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    entities.add(entity)
                    break
        
        return entities
    
    def _identify_themes(self, text: str) -> Set[str]:
        """Identify themes in text"""
        themes = set()
        text_lower = text.lower()
        
        for theme, keywords in self.theme_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    themes.add(theme)
                    break
        
        return themes
    
    def _classify_insight_type(self, text: str) -> str:
        """Classify the type of insight"""
        text_lower = text.lower()
        
        for insight_type, patterns in self.insight_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return insight_type
        
        return "observation"  # default
    
    def _assess_effectiveness(self, text: str) -> float:
        """Assess the effectiveness/importance of an insight"""
        text_lower = text.lower()
        
        # High effectiveness indicators
        if any(word in text_lower for word in ["always", "fundamental", "breakthrough", "game changer", "works every time"]):
            return 1.0
        
        # Good effectiveness indicators  
        if any(word in text_lower for word in ["effective", "helps", "works", "successful", "breakthrough"]):
            return 0.8
        
        # Moderate effectiveness
        if any(word in text_lower for word in ["sometimes", "often", "usually", "tends to"]):
            return 0.6
        
        # Low effectiveness
        if any(word in text_lower for word in ["tried", "might", "could", "maybe", "perhaps"]):
            return 0.4
        
        return 0.5  # neutral
    
    def process_all_conversations(self, conversations_dir: str) -> int:
        """Process all conversation files and add insights to database"""
        conversations_path = Path(conversations_dir)
        total_insights = 0
        
        if not conversations_path.exists():
            print(f"Conversations directory not found: {conversations_dir}")
            return 0
        
        print(f"Processing conversations from: {conversations_dir}")
        print("=" * 60)
        
        for file_path in conversations_path.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                print(f"\nProcessing: {file_path.name}")
                insights = self.extract_insights_from_file(str(file_path))
                
                # Add insights to database
                added = 0
                for insight_data in insights:
                    insight = Insight(
                        id=str(uuid.uuid4()),
                        content=insight_data['content'],
                        entities=set(insight_data['entities']),
                        themes=set(insight_data['themes']),
                        insight_type=insight_data['insight_type'],
                        effectiveness_score=insight_data['effectiveness_score'],
                        source_file=insight_data['source_file'],
                        timestamp=datetime.now()
                    )
                    
                    self.memory_system.add_insight(insight)
                    added += 1
                
                total_insights += added
                print(f"  ✓ Added {added} insights to database")
        
        print("\n" + "=" * 60)
        print(f"Total insights extracted and added: {total_insights}")
        return total_insights


def main():
    """Main function to run the extraction"""
    db_path = os.path.expanduser("~/Documents/private/memory_data/personal_insights.db")
    conversations_dir = "/Users/beck/Documents/private/conversations"
    
    print("=" * 60)
    print("CONVERSATION INSIGHT EXTRACTOR")
    print("=" * 60)
    
    # Check if conversations directory exists
    if not os.path.exists(conversations_dir):
        print(f"\n⚠ Conversations directory not found: {conversations_dir}")
        print("Please create it or update the path in the script.")
        return
    
    # Ask user if they want to use LLM
    use_llm = True
    try:
        response = input("\nUse local Llama 3.3 for extraction? (Y/n): ").strip().lower()
        if response == 'n':
            use_llm = False
    except (EOFError, KeyboardInterrupt):
        print("\n\nCancelled.")
        return
    
    extractor = ConversationInsightExtractor(db_path, use_llm=use_llm)
    total_insights = extractor.process_all_conversations(conversations_dir)
    
    if total_insights > 0:
        print(f"\n✓ Extraction complete! Added {total_insights} new insights to your memory system.")
        
        # Show some stats
        print("\nTesting retrieval with sample query...")
        result = extractor.memory_system.retrieve_contextual_insights("worried about trust with A")
        print(f"Found {len(result['surface'])} surface insights")
        
        if result['surface']:
            print("\nTop 3 insights:")
            for i, insight in enumerate(result['surface'][:3], 1):
                print(f"{i}. {insight.content[:100]}...")
    else:
        print("\n⚠ No insights were extracted.")


if __name__ == "__main__":
    main()
