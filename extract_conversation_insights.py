#!/usr/bin/env python3
"""
Extract insights from conversation files and add them to the memory system
"""

import os
import re
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from insight_system_simple import SimpleContextualInsightRetrieval, Insight

class ConversationInsightExtractor:
    def __init__(self, db_path: str):
        self.memory_system = SimpleContextualInsightRetrieval(db_path)
        
        # Entity patterns to look for
        self.entity_patterns = {
            "N": [r'\bN\b', r'N is', r'N was', r'N said', r'N did', r'with N', r'about N'],
            "A": [r'\bA\b', r'A is', r'A was', r'A said', r'A did', r'with A', r'about A', r'trusting A'],
            "B": [r'\bB\b', r'B is', r'B was', r'B said', r'B did', r'with B', r'about B'],
            "E": [r'\bE\b', r'E is', r'E was', r'E said', r'E did', r'with E', r'about E'],
            "X": [r'\bX\b', r'X is', r'X was', r'X said', r'X did', r'with X', r'about X', r"X's voice"]
        }
        
        # Theme keywords
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
        
        # Insight type patterns
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
        
        # Split into conversation chunks (Human: ... Assistant: ...)
        chunks = self._split_conversation(content)
        
        for chunk in chunks:
            # Look for insights in each chunk
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
        """Find insights in a conversation chunk"""
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
                    'entities': entities,
                    'themes': themes,
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
        
        for file_path in conversations_path.iterdir():
            if file_path.is_file():
                print(f"Processing: {file_path.name}")
                insights = self.extract_insights_from_file(str(file_path))
                
                # Add insights to database
                for insight_data in insights:
                    insight = Insight(
                        id=str(uuid.uuid4()),
                        content=insight_data['content'],
                        entities=insight_data['entities'],
                        themes=insight_data['themes'],
                        insight_type=insight_data['insight_type'],
                        effectiveness_score=insight_data['effectiveness_score'],
                        source_file=insight_data['source_file'],
                        timestamp=datetime.fromisoformat(insight_data['timestamp'])
                    )
                    
                    self.memory_system.add_insight(insight)
                    total_insights += 1
                
                print(f"  Extracted {len(insights)} insights")
        
        print(f"\nTotal insights extracted and added: {total_insights}")
        return total_insights

def main():
    """Main function to run the extraction"""
    db_path = os.path.expanduser("~/Documents/private/memory_data/personal_insights.db")
    conversations_dir = "/Users/beck/Documents/private/conversations"
    
    extractor = ConversationInsightExtractor(db_path)
    total_insights = extractor.process_all_conversations(conversations_dir)
    
    print(f"\nExtraction complete! Added {total_insights} new insights to your memory system.")
    
    # Show some stats
    print("\nTesting N-related insights:")
    result = extractor.memory_system.retrieve_contextual_insights("N is being difficult about boundaries")
    print(f"Found {len(result['surface'])} surface insights about N and boundaries")
    for insight in result['surface'][:3]:
        print(f"  - {insight.content[:80]}...")

if __name__ == "__main__":
    main()