#!/usr/bin/env python3
"""
Contextual Insight Retrieval System
Core architecture for intelligent, context-aware insight retrieval
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Insight:
    """Core insight data structure"""
    id: str
    content: str
    entities: Set[str] = field(default_factory=set)
    themes: Set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=datetime.now)
    effectiveness_score: float = 0.0
    growth_stage: str = "foundational"  # foundational, evolved, superseded
    layer: str = "surface"  # surface, mid, deep
    insight_type: str = "observation"  # observation, strategy, breakthrough, anchor
    supersedes: List[str] = field(default_factory=list)
    superseded_by: Optional[str] = None
    source_file: str = ""
    context: str = ""
    embedding: Optional[np.ndarray] = None

@dataclass
class SemanticTrigger:
    """Semantic trigger for topic-based retrieval"""
    entity: str
    keywords: Set[str]
    priority_insights: List[str] = field(default_factory=list)
    max_surface_insights: int = 3
    context_patterns: List[str] = field(default_factory=list)

class TemporalWeight:
    """Handles temporal weighting of insights"""
    
    @staticmethod
    def calculate_weight(insight_date: datetime, current_date: datetime) -> float:
        """Calculate temporal weight with exponential decay"""
        days_diff = (current_date - insight_date).days
        
        # Recent insights (last 30 days) get full weight
        if days_diff <= 30:
            return 1.0
        
        # Exponential decay over time, but never below 0.1
        decay_rate = 0.02
        weight = max(0.1, np.exp(-decay_rate * (days_diff - 30)))
        return weight
    
    @staticmethod
    def is_bedrock_truth(insight: Insight) -> bool:
        """Identify bedrock truths that maintain relevance regardless of age"""
        bedrock_patterns = [
            r"X's voice",
            r"Crisis Anchor",
            r"foundational pattern",
            r"his word is enough",
            r"trauma response",
            r"core truth"
        ]
        
        for pattern in bedrock_patterns:
            if re.search(pattern, insight.content, re.IGNORECASE):
                return True
        return False

class GrowthTrajectoryTracker:
    """Tracks growth trajectories and insight evolution"""
    
    def __init__(self):
        self.trajectories: Dict[str, List[Insight]] = {}
    
    def identify_inflection_points(self, insights: List[Insight]) -> List[Insight]:
        """Identify significant shifts in understanding"""
        inflection_points = []
        
        # Pattern matching for breakthrough language
        breakthrough_patterns = [
            r"shifted something fundamental",
            r"just clicked",
            r"finally understood",
            r"breakthrough",
            r"everything changed when",
            r"realized that"
        ]
        
        for insight in insights:
            for pattern in breakthrough_patterns:
                if re.search(pattern, insight.content, re.IGNORECASE):
                    insight.insight_type = "breakthrough"
                    inflection_points.append(insight)
                    break
        
        return inflection_points
    
    def track_progression(self, entity: str, insights: List[Insight]) -> Dict[str, List[Insight]]:
        """Track progression of understanding for specific entity/theme"""
        entity_insights = [i for i in insights if entity in i.entities]
        entity_insights.sort(key=lambda x: x.timestamp)
        
        progression = {
            "early": entity_insights[:len(entity_insights)//3],
            "middle": entity_insights[len(entity_insights)//3:2*len(entity_insights)//3],
            "recent": entity_insights[2*len(entity_insights)//3:]
        }
        
        return progression

class StrategyEffectivenessTracker:
    """Tracks effectiveness of strategies and approaches"""
    
    def __init__(self):
        self.strategy_outcomes: Dict[str, float] = {}
    
    def assess_strategy_effectiveness(self, insight: Insight) -> float:
        """Assess effectiveness based on content markers"""
        content_lower = insight.content.lower()
        
        # Positive outcome markers
        positive_markers = [
            "worked", "effective", "helped", "breakthrough", "success",
            "able to", "finally", "strength", "trust", "clarity"
        ]
        
        # Negative outcome markers  
        negative_markers = [
            "failed", "couldn't", "impossible", "gave up", "collapsed",
            "didn't work", "backfired", "made it worse"
        ]
        
        # Experimental/ongoing markers
        experimental_markers = [
            "trying", "experimenting", "testing", "attempting", "exploring"
        ]
        
        positive_count = sum(1 for marker in positive_markers if marker in content_lower)
        negative_count = sum(1 for marker in negative_markers if marker in content_lower)
        experimental_count = sum(1 for marker in experimental_markers if marker in content_lower)
        
        if positive_count > negative_count:
            return min(1.0, 0.6 + 0.1 * positive_count)
        elif negative_count > positive_count:
            return max(0.0, 0.4 - 0.1 * negative_count)
        else:
            return 0.5  # Neutral/experimental

class LayeredArchitecture:
    """Manages layered information architecture with progressive disclosure"""
    
    def __init__(self):
        self.surface_limit = 3
        self.mid_limit = 8
        
    def categorize_by_layer(self, insights: List[Insight], context: str) -> Dict[str, List[Insight]]:
        """Categorize insights into surface/mid/deep layers"""
        
        # Surface layer: Crisis anchors, recent breakthroughs, current strategies
        surface_insights = []
        mid_insights = []
        deep_insights = []
        
        for insight in insights:
            # Surface: Crisis anchors and recent high-impact insights
            if (insight.insight_type in ["anchor", "breakthrough"] or 
                insight.effectiveness_score > 0.7 or
                (datetime.now() - insight.timestamp).days < 30):
                surface_insights.append(insight)
            
            # Mid: Supporting context, recent developments
            elif (insight.effectiveness_score > 0.4 or
                  (datetime.now() - insight.timestamp).days < 90):
                mid_insights.append(insight)
            
            # Deep: Historical patterns, comprehensive background
            else:
                deep_insights.append(insight)
        
        return {
            "surface": surface_insights[:self.surface_limit],
            "mid": mid_insights[:self.mid_limit],
            "deep": deep_insights
        }

class ContextualInsightRetrieval:
    """Main system for contextual insight retrieval"""
    
    def __init__(self, db_path: str = "insights.db"):
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.temporal_weight = TemporalWeight()
        self.growth_tracker = GrowthTrajectoryTracker()
        self.strategy_tracker = StrategyEffectivenessTracker()
        self.layered_arch = LayeredArchitecture()
        self.semantic_triggers = self._initialize_triggers()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for insights storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                entities TEXT,
                themes TEXT,
                timestamp TEXT,
                effectiveness_score REAL,
                growth_stage TEXT,
                layer TEXT,
                insight_type TEXT,
                supersedes TEXT,
                superseded_by TEXT,
                source_file TEXT,
                context TEXT,
                embedding BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_entities ON insights(entities);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON insights(timestamp);
            CREATE INDEX IF NOT EXISTS idx_effectiveness ON insights(effectiveness_score);
            CREATE INDEX IF NOT EXISTS idx_type ON insights(insight_type);
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_triggers(self) -> Dict[str, SemanticTrigger]:
        """Initialize semantic triggers for key entities"""
        triggers = {
            "A": SemanticTrigger(
                entity="A",
                keywords={"trust", "relationship", "trustworthy", "lucky", "word is enough"},
                max_surface_insights=3,
                context_patterns=["trusting", "relationship with A", "his word"]
            ),
            
            "N": SemanticTrigger(
                entity="N",
                keywords={"boundaries", "parenting", "school", "hygiene", "anger", "structure"},
                max_surface_insights=3,
                context_patterns=["parenting", "boundaries with N", "school"]
            ),
            
            "X": SemanticTrigger(
                entity="X",
                keywords={"voice", "trauma", "inadequacy", "scanning", "X's voice"},
                max_surface_insights=2,
                context_patterns=["X's voice", "trauma response", "inadequacy"]
            ),
            
            "trauma_responses": SemanticTrigger(
                entity="trauma_responses",
                keywords={"activation", "triggered", "nervous system", "shutdown", "scanning"},
                max_surface_insights=3,
                context_patterns=["trauma response", "activation", "nervous system"]
            )
        }
        
        return triggers
    
    def detect_context_triggers(self, user_input: str) -> List[str]:
        """Detect which semantic triggers are activated by user input"""
        activated_triggers = []
        user_lower = user_input.lower()
        
        for trigger_name, trigger in self.semantic_triggers.items():
            # Check for entity name or keywords
            if (trigger.entity.lower() in user_lower or 
                any(keyword in user_lower for keyword in trigger.keywords)):
                activated_triggers.append(trigger_name)
        
        return activated_triggers
    
    def retrieve_contextual_insights(self, user_input: str, max_insights: int = 5) -> Dict[str, List[Insight]]:
        """Retrieve contextually relevant insights based on user input"""
        activated_triggers = self.detect_context_triggers(user_input)
        
        if not activated_triggers:
            return {"surface": [], "mid": [], "deep": []}
        
        # Retrieve insights for activated triggers
        all_insights = []
        
        for trigger_name in activated_triggers:
            trigger = self.semantic_triggers[trigger_name]
            entity_insights = self._get_insights_by_entity(trigger.entity)
            all_insights.extend(entity_insights)
        
        # Apply temporal weighting and effectiveness scoring
        current_time = datetime.now()
        scored_insights = []
        
        for insight in all_insights:
            temporal_score = self.temporal_weight.calculate_weight(insight.timestamp, current_time)
            
            # Boost bedrock truths
            if self.temporal_weight.is_bedrock_truth(insight):
                temporal_score = min(1.0, temporal_score * 1.5)
            
            final_score = (insight.effectiveness_score * 0.5 + temporal_score * 0.5)
            insight.final_score = final_score
            scored_insights.append(insight)
        
        # Sort by score and remove duplicates
        scored_insights.sort(key=lambda x: x.final_score, reverse=True)
        unique_insights = []
        seen_content = set()
        
        for insight in scored_insights:
            content_key = insight.content[:100]  # Use first 100 chars to identify duplicates
            if content_key not in seen_content:
                unique_insights.append(insight)
                seen_content.add(content_key)
        
        # Apply layered architecture
        layered_insights = self.layered_arch.categorize_by_layer(unique_insights[:max_insights], user_input)
        
        return layered_insights
    
    def _get_insights_by_entity(self, entity: str) -> List[Insight]:
        """Retrieve insights from database for specific entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM insights 
            WHERE entities LIKE ? 
            ORDER BY effectiveness_score DESC, timestamp DESC
        ''', (f'%{entity}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in rows:
            insight = Insight(
                id=row[0],
                content=row[1],
                entities=set(row[2].split(',') if row[2] else []),
                themes=set(row[3].split(',') if row[3] else []),
                timestamp=datetime.fromisoformat(row[4]),
                effectiveness_score=row[5],
                growth_stage=row[6],
                layer=row[7],
                insight_type=row[8],
                supersedes=row[9].split(',') if row[9] else [],
                superseded_by=row[10],
                source_file=row[11],
                context=row[12]
            )
            insights.append(insight)
        
        return insights
    
    def add_insight(self, insight: Insight):
        """Add new insight to the system"""
        # Generate embedding
        insight.embedding = self.model.encode([insight.content])[0]
        
        # Assess effectiveness
        insight.effectiveness_score = self.strategy_tracker.assess_strategy_effectiveness(insight)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO insights VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            insight.id,
            insight.content,
            ','.join(insight.entities),
            ','.join(insight.themes),
            insight.timestamp.isoformat(),
            insight.effectiveness_score,
            insight.growth_stage,
            insight.layer,
            insight.insight_type,
            ','.join(insight.supersedes),
            insight.superseded_by,
            insight.source_file,
            insight.context,
            insight.embedding.tobytes() if insight.embedding is not None else None
        ))
        
        conn.commit()
        conn.close()
    
    def format_for_conversation(self, layered_insights: Dict[str, List[Insight]]) -> str:
        """Format insights for natural conversation integration"""
        if not any(layered_insights.values()):
            return ""
        
        surface_insights = layered_insights.get("surface", [])
        
        if not surface_insights:
            return ""
        
        # Format for natural integration
        formatted_parts = []
        
        for insight in surface_insights:
            # Prioritize crisis anchors and breakthroughs
            if insight.insight_type in ["anchor", "breakthrough"]:
                formatted_parts.append(f"[Key insight: {insight.content}]")
            else:
                formatted_parts.append(f"[Context: {insight.content}]")
        
        return "\n".join(formatted_parts)

if __name__ == "__main__":
    # Example usage
    system = ContextualInsightRetrieval()
    
    # Test retrieval
    test_input = "I'm worried about trusting A"
    insights = system.retrieve_contextual_insights(test_input)
    formatted = system.format_for_conversation(insights)
    
    print("Retrieved insights:")
    print(formatted)