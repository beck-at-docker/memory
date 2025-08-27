#!/usr/bin/env python3
"""
Data Migration Pipeline
Extracts insights from existing conversation files and populates the retrieval system
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple
import uuid

from insight_retrieval_system import (
    Insight, ContextualInsightRetrieval
)

class ConversationParser:
    """Parses conversation files and extracts insights"""
    
    def __init__(self):
        self.entity_patterns = {
            "A": [r'\bA\b', r'trusting A', r'relationship with A', r'his word', r'trustworthy'],
            "N": [r'\bN\b', r"N's", r'parenting', r'school', r'hygiene', r'boundaries', r'shower'],
            "X": [r'\bX\b', r"X's voice", r'X said', r'X convinced', r'X taught'],
            "trauma_responses": [r'trauma response', r'activation', r'triggered', r'nervous system', r'shutdown']
        }
        
        self.breakthrough_patterns = [
            r'shifted something fundamental',
            r'just clicked',
            r'finally understood',
            r'breakthrough',
            r'everything changed when',
            r'realized that',
            r'that reference.*Job when all is renewed',
            r'his word is enough',
            r'could I be so lucky',
            r'yes, his word is enough'
        ]
        
        self.crisis_anchor_patterns = [
            r'Crisis Anchor',
            r'anchor this',
            r'remember this',
            r'hold onto this',
            r'bedrock truth'
        ]
        
        self.strategy_patterns = [
            r'what worked',
            r'effective approach',
            r'strategy',
            r'what helps',
            r'try this',
            r'approach that',
            r'taking.*to therapy',
            r'holding the line'
        ]
    
    def parse_file(self, file_path: Path) -> List[Insight]:
        """Parse a single conversation file and extract insights"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Extract date from filename
        file_date = self._extract_date_from_filename(file_path.name)
        
        # Split into dialogue segments
        segments = self._split_into_segments(content)
        
        insights = []
        for i, segment in enumerate(segments):
            extracted_insights = self._extract_insights_from_segment(segment, file_path, file_date, i)
            insights.extend(extracted_insights)
        
        return insights
    
    def _extract_date_from_filename(self, filename: str) -> datetime:
        """Extract date from filename like '8-19-25'"""
        try:
            # Handle formats like 8-19-25, 7-28.2-25, etc.
            clean_name = filename.replace('.2', '').replace('.3', '').replace('.md', '')
            parts = clean_name.split('-')
            
            if len(parts) == 3:
                month, day, year = parts
                year = int(year) + 2000 if int(year) < 50 else int(year) + 1900
                return datetime(year, int(month), int(day))
        except ValueError:
            pass
        
        return datetime.now()
    
    def _split_into_segments(self, content: str) -> List[str]:
        """Split conversation into meaningful segments"""
        # Split by speaker changes or major topic shifts
        segments = []
        
        # Split by "Human:" and "Claude:" or "Assistant:"
        parts = re.split(r'\*\*(Human|Claude|Assistant):\*\*', content)
        
        current_segment = ""
        for part in parts:
            if part.strip() in ["Human", "Claude", "Assistant"]:
                if current_segment.strip():
                    segments.append(current_segment.strip())
                current_segment = ""
            else:
                current_segment += part
        
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        # Also try splitting by paragraph breaks for very long segments
        final_segments = []
        for segment in segments:
            if len(segment) > 1000:  # Split very long segments
                paragraphs = segment.split('\n\n')
                final_segments.extend([p for p in paragraphs if len(p.strip()) > 50])
            else:
                final_segments.append(segment)
        
        return [s for s in final_segments if len(s.strip()) > 30]
    
    def _extract_insights_from_segment(self, segment: str, file_path: Path, file_date: datetime, segment_index: int) -> List[Insight]:
        """Extract insights from a single segment"""
        insights = []
        
        # Identify entities mentioned
        entities = self._identify_entities(segment)
        
        # Identify themes
        themes = self._identify_themes(segment)
        
        # Check for different types of insights
        insight_type = self._classify_insight_type(segment)
        
        # Extract key sentences/insights
        key_insights = self._extract_key_insights(segment, insight_type)
        
        for insight_text in key_insights:
            insight = Insight(
                id=str(uuid.uuid4()),
                content=insight_text,
                entities=entities,
                themes=themes,
                timestamp=file_date,
                growth_stage="foundational",
                layer="surface" if insight_type in ["breakthrough", "anchor"] else "mid",
                insight_type=insight_type,
                source_file=str(file_path),
                context=segment[:200] + "..." if len(segment) > 200 else segment
            )
            insights.append(insight)
        
        return insights
    
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
        """Identify themes in the text"""
        themes = set()
        text_lower = text.lower()
        
        theme_keywords = {
            "trust": ["trust", "trustworthy", "trusting", "faith", "belief"],
            "boundaries": ["boundaries", "limits", "structure", "rules", "discipline"],
            "trauma": ["trauma", "triggered", "activation", "nervous system", "shutdown"],
            "parenting": ["parent", "parenting", "mother", "discipline", "hygiene"],
            "growth": ["growth", "progress", "breakthrough", "understanding", "healing"],
            "relationships": ["relationship", "connection", "love", "intimacy", "partnership"],
            "strategies": ["strategy", "approach", "method", "technique", "tool"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.add(theme)
        
        return themes
    
    def _classify_insight_type(self, text: str) -> str:
        """Classify the type of insight"""
        text_lower = text.lower()
        
        # Crisis anchors
        for pattern in self.crisis_anchor_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "anchor"
        
        # Breakthroughs
        for pattern in self.breakthrough_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "breakthrough"
        
        # Strategies
        for pattern in self.strategy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "strategy"
        
        return "observation"
    
    def _extract_key_insights(self, text: str, insight_type: str) -> List[str]:
        """Extract key insight sentences from text"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        key_insights = []
        
        if insight_type == "breakthrough":
            # Look for sentences with breakthrough language
            for sentence in sentences:
                for pattern in self.breakthrough_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        key_insights.append(sentence)
                        break
        
        elif insight_type == "anchor":
            # Look for anchor statements
            for sentence in sentences:
                for pattern in self.crisis_anchor_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        key_insights.append(sentence)
                        break
        
        elif insight_type == "strategy":
            # Look for strategy descriptions
            strategy_indicators = [
                r'what.*work', r'try.*this', r'approach.*that',
                r'strategy.*is', r'effective.*way', r'helps.*when'
            ]
            for sentence in sentences:
                for pattern in strategy_indicators:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        key_insights.append(sentence)
                        break
        
        else:
            # For observations, pick sentences with high insight value
            high_value_patterns = [
                r'the.*is that', r'what.*means', r'the.*thing.*is',
                r'important.*to', r'key.*insight', r'realize.*that'
            ]
            for sentence in sentences:
                for pattern in high_value_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        key_insights.append(sentence)
                        break
        
        # If no specific patterns found, take meaningful sentences
        if not key_insights:
            # Take sentences that are substantive and meaningful
            meaningful_sentences = []
            for sentence in sentences:
                if (len(sentence) > 50 and 
                    not sentence.startswith(("I", "You", "The", "That", "This")) and
                    any(entity in sentence for entity in ["trust", "boundary", "strategy", "trauma", "parent"])):
                    meaningful_sentences.append(sentence)
            
            key_insights = meaningful_sentences[:2]  # Limit to top 2
        
        return key_insights[:3]  # Max 3 insights per segment

class DataMigrationPipeline:
    """Main pipeline for migrating existing conversation data"""
    
    def __init__(self, source_dir: str, system: ContextualInsightRetrieval):
        self.source_dir = Path(source_dir)
        self.system = system
        self.parser = ConversationParser()
    
    def migrate_all_files(self) -> Dict[str, int]:
        """Migrate all conversation files in the source directory"""
        stats = {"files_processed": 0, "insights_extracted": 0, "errors": 0}
        
        # Get all conversation files
        conversation_files = []
        for pattern in ['*-*-*', '*.md']:
            conversation_files.extend(self.source_dir.glob(pattern))
        
        # Filter out summaries directory
        conversation_files = [f for f in conversation_files if 'summaries' not in str(f)]
        
        print(f"Found {len(conversation_files)} conversation files to process")
        
        for file_path in conversation_files:
            try:
                print(f"Processing: {file_path.name}")
                insights = self.parser.parse_file(file_path)
                
                # Add insights to system
                for insight in insights:
                    self.system.add_insight(insight)
                
                stats["files_processed"] += 1
                stats["insights_extracted"] += len(insights)
                
                print(f"  Extracted {len(insights)} insights")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                stats["errors"] += 1
        
        return stats
    
    def create_crisis_anchors(self):
        """Create specific crisis anchor insights based on your requirements"""
        crisis_anchors = [
            {
                "content": "A is trustworthy. His word is enough. This is bedrock truth.",
                "entities": {"A", "trust"},
                "themes": {"trust", "relationships"},
                "insight_type": "anchor"
            },
            {
                "content": "Taking trauma responses to therapy protects relationship with A",
                "entities": {"A", "trauma_responses"},
                "themes": {"strategies", "relationships", "trauma"},
                "insight_type": "strategy"
            },
            {
                "content": "X's voice creates inadequacy-scanning. Recognize it as X, not truth.",
                "entities": {"X", "trauma_responses"},
                "themes": {"trauma", "strategies"},
                "insight_type": "anchor"
            },
            {
                "content": "Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
                "entities": {"N"},
                "themes": {"parenting", "boundaries", "strategies"},
                "insight_type": "strategy"
            }
        ]
        
        for anchor_data in crisis_anchors:
            insight = Insight(
                id=str(uuid.uuid4()),
                content=anchor_data["content"],
                entities=anchor_data["entities"],
                themes=anchor_data["themes"],
                timestamp=datetime.now(),
                growth_stage="foundational",
                layer="surface",
                insight_type=anchor_data["insight_type"],
                effectiveness_score=1.0,  # Crisis anchors get max effectiveness
                source_file="crisis_anchors_manual",
                context="Manually created crisis anchor"
            )
            
            self.system.add_insight(insight)

def main():
    """Run the data migration"""
    source_directory = "/Users/beck/Documents/private"
    
    # Initialize the system
    system = ContextualInsightRetrieval()
    
    # Initialize migration pipeline
    pipeline = DataMigrationPipeline(source_directory, system)
    
    print("Starting data migration...")
    
    # Create crisis anchors first
    print("Creating crisis anchors...")
    pipeline.create_crisis_anchors()
    
    # Migrate all files
    print("Migrating conversation files...")
    stats = pipeline.migrate_all_files()
    
    print("\nMigration completed!")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Insights extracted: {stats['insights_extracted']}")
    print(f"Errors: {stats['errors']}")
    
    # Test the system
    print("\nTesting retrieval system...")
    test_cases = [
        "I'm worried about trusting A",
        "N is being difficult about boundaries",
        "I'm having trauma responses",
        "What strategies worked for parenting?"
    ]
    
    for test_input in test_cases:
        print(f"\nTest: '{test_input}'")
        insights = system.retrieve_contextual_insights(test_input)
        formatted = system.format_for_conversation(insights)
        if formatted:
            print("Retrieved:")
            print(formatted)
        else:
            print("No insights retrieved")

if __name__ == "__main__":
    main()