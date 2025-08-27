#!/usr/bin/env python3
"""
Simplified Contextual Insight Retrieval System (without ML dependencies)
For initial testing and demonstration
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
import uuid

@dataclass
class Insight:
    """Core insight data structure"""
    id: str
    content: str
    entities: Set[str] = field(default_factory=set)
    themes: Set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=datetime.now)
    effectiveness_score: float = 0.0
    growth_stage: str = "foundational"
    layer: str = "surface"
    insight_type: str = "observation"
    supersedes: List[str] = field(default_factory=list)
    superseded_by: Optional[str] = None
    source_file: str = ""
    context: str = ""

@dataclass
class SemanticTrigger:
    """Semantic trigger for topic-based retrieval"""
    entity: str
    keywords: Set[str]
    priority_insights: List[str] = field(default_factory=list)
    max_surface_insights: int = 3
    context_patterns: List[str] = field(default_factory=list)

class SimpleContextualInsightRetrieval:
    """Simplified version without ML dependencies"""
    
    def __init__(self, db_path: str = "insights_simple.db"):
        self.db_path = db_path
        self.semantic_triggers = self._initialize_triggers()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
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
                context TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities ON insights(entities)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON insights(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_effectiveness ON insights(effectiveness_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON insights(insight_type)')
        
        conn.commit()
        conn.close()
    
    def _initialize_triggers(self) -> Dict[str, SemanticTrigger]:
        """Initialize semantic triggers"""
        return {
            "A": SemanticTrigger(
                entity="A",
                keywords={"trust", "relationship", "trustworthy", "lucky", "word is enough"},
                max_surface_insights=3
            ),
            "N": SemanticTrigger(
                entity="N", 
                keywords={"boundaries", "parenting", "school", "hygiene", "anger"},
                max_surface_insights=3
            ),
            "X": SemanticTrigger(
                entity="X",
                keywords={"voice", "trauma", "inadequacy", "scanning"},
                max_surface_insights=2
            )
        }
    
    def detect_context_triggers(self, user_input: str) -> List[str]:
        """Detect activated triggers"""
        activated = []
        user_lower = user_input.lower()
        
        for trigger_name, trigger in self.semantic_triggers.items():
            if (trigger.entity.lower() in user_lower or
                any(keyword in user_lower for keyword in trigger.keywords)):
                activated.append(trigger_name)
        
        return activated
    
    def add_insight(self, insight: Insight):
        """Add insight to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO insights VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            insight.context
        ))
        
        conn.commit()
        conn.close()
    
    def retrieve_contextual_insights(self, user_input: str, max_insights: int = 5) -> Dict[str, List[Insight]]:
        """Retrieve relevant insights"""
        triggers = self.detect_context_triggers(user_input)
        
        if not triggers:
            return {"surface": [], "mid": [], "deep": []}
        
        # Get insights for activated triggers
        all_insights = []
        for trigger_name in triggers:
            entity_insights = self._get_insights_by_entity(trigger_name)
            all_insights.extend(entity_insights)
        
        # Sort by effectiveness and recency
        all_insights.sort(key=lambda x: (x.effectiveness_score, 
                                       -(datetime.now() - x.timestamp).days), 
                         reverse=True)
        
        # Categorize by layer
        surface = [i for i in all_insights if i.layer == "surface"][:3]
        mid = [i for i in all_insights if i.layer == "mid"][:5]  
        deep = [i for i in all_insights if i.layer == "deep"][:max_insights]
        
        return {"surface": surface, "mid": mid, "deep": deep}
    
    def _get_insights_by_entity(self, entity: str) -> List[Insight]:
        """Get insights for entity from database"""
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

def test_simple_system():
    """Test the simplified system"""
    print("Testing Simplified Contextual Insight Retrieval System")
    print("=" * 60)
    
    # Initialize system
    system = SimpleContextualInsightRetrieval("test_simple.db")
    
    # Add test insights
    test_insights = [
        Insight(
            id=str(uuid.uuid4()),
            content="A is trustworthy. His word is enough. This is bedrock truth.",
            entities={"A"},
            themes={"trust", "relationships"},
            effectiveness_score=1.0,
            layer="surface",
            insight_type="anchor"
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Taking trauma responses to therapy protects relationship with A",
            entities={"A", "trauma_responses"},
            themes={"strategies", "relationships", "trauma"},
            effectiveness_score=0.8,
            layer="surface", 
            insight_type="strategy"
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
            entities={"N"},
            themes={"parenting", "boundaries", "strategies"}, 
            effectiveness_score=0.9,
            layer="surface",
            insight_type="strategy"
        )
    ]
    
    # Add insights to system
    for insight in test_insights:
        system.add_insight(insight)
    
    print("✓ Test insights added")
    
    # Test retrieval
    test_cases = [
        "I'm worried about trusting A",
        "N is being difficult about boundaries", 
        "I'm having trauma responses",
        "What strategies worked for parenting?"
    ]
    
    for test_input in test_cases:
        print(f"\nTest: '{test_input}'")
        
        # Detect triggers
        triggers = system.detect_context_triggers(test_input)
        print(f"Triggers detected: {triggers}")
        
        # Retrieve insights
        insights = system.retrieve_contextual_insights(test_input)
        surface_insights = insights.get("surface", [])
        
        if surface_insights:
            print("Retrieved insights:")
            for insight in surface_insights:
                print(f"  [{insight.insight_type.upper()}] {insight.content}")
        else:
            print("  No insights retrieved")
    
    print("\n" + "=" * 60)
    print("✓ Simple system test completed successfully!")

if __name__ == "__main__":
    test_simple_system()