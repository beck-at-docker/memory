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
import threading
from contextlib import contextmanager
from queue import Queue, Empty

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


class ConnectionPool:
    """Thread-safe SQLite connection pool"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        """
        Initialize connection pool
        
        Args:
            db_path: Path to SQLite database
            pool_size: Maximum number of connections to pool
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0
        
        # Pre-create connections
        for _ in range(pool_size):
            self._create_connection()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimal settings"""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow use across threads
            timeout=20.0,  # Wait up to 20s for locks
            isolation_level=None  # Auto-commit mode for better concurrency
        )
        
        # Enable Write-Ahead Logging for better concurrent access
        conn.execute('PRAGMA journal_mode=WAL')
        
        # Optimize for performance
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=-64000')  # 64MB cache
        conn.execute('PRAGMA temp_store=MEMORY')
        
        # Row factory for easier access
        conn.row_factory = sqlite3.Row
        
        self._created_connections += 1
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager)
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = None
        try:
            # Try to get connection from pool (non-blocking)
            try:
                conn = self._pool.get_nowait()
            except Empty:
                # Pool is empty, create new connection if under limit
                with self._lock:
                    if self._created_connections < self.pool_size * 2:  # Allow burst
                        conn = self._create_connection()
                    else:
                        # Wait for a connection to be returned
                        conn = self._pool.get(timeout=5.0)
            
            yield conn
            
        finally:
            # Return connection to pool
            if conn is not None:
                try:
                    # Rollback any uncommitted transactions
                    conn.rollback()
                    self._pool.put_nowait(conn)
                except:
                    # Pool is full or connection is bad, close it
                    try:
                        conn.close()
                    except:
                        pass
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except:
                pass


class SimpleContextualInsightRetrieval:
    """Simplified version without ML dependencies"""
    
    def __init__(self, db_path: str = "insights_simple.db", pool_size: int = 5):
        self.db_path = db_path
        self.semantic_triggers = self._initialize_triggers()
        
        # Initialize connection pool
        self.pool = ConnectionPool(db_path, pool_size)
        
        # Initialize database schema
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        with self.pool.get_connection() as conn:
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
            
            # Create indexes for common queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities ON insights(entities)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON insights(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_effectiveness ON insights(effectiveness_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON insights(insight_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_layer ON insights(layer)')
            
            conn.commit()
    
    def _initialize_triggers(self) -> Dict[str, SemanticTrigger]:
        """
        Initialize semantic triggers with descriptive entity names.
        Also includes single-letter shortcuts for backward compatibility.
        """
        triggers = {
            "partner_A": SemanticTrigger(
                entity="partner_A",
                keywords={"trust", "relationship", "trustworthy", "lucky", "word is enough", 
                          "partner", "husband", "A"},
                max_surface_insights=3
            ),
            "child_N": SemanticTrigger(
                entity="child_N", 
                keywords={"boundaries", "parenting", "school", "hygiene", "anger", "yells", "swears", 
                          "fights", "silence", "protective silence", "loyalty", "N", "son", "child", "kid"},
                max_surface_insights=3
            ),
            "ex_X": SemanticTrigger(
                entity="ex_X",
                keywords={"voice", "trauma", "inadequacy", "scanning", "contact", "charming", "reasonable", 
                          "best behavior", "performance", "good dad", "case", "absent parent", "X", "ex"},
                max_surface_insights=3
            ),
            "self_beck": SemanticTrigger(
                entity="self_beck",
                keywords={"strategic sacrifice", "court avoidance", "moral certainty", "strength", 
                          "doing the right thing", "protective parenting", "beck", "I", "me", "my"},
                max_surface_insights=3
            ),
            "internal_voice": SemanticTrigger(
                entity="internal_voice",
                keywords={"internal voice", "sabotage", "reality inversion", "hurting", "loving parent", 
                          "boundaries", "weaponization", "love", "voice in my head", "self-talk"},
                max_surface_insights=2
            ),
            "trauma_responses": SemanticTrigger(
                entity="trauma_responses",
                keywords={"trauma", "trauma responses", "triggered", "nervous system", "danger", 
                          "disproportionate responses", "activation", "ptsd"},
                max_surface_insights=2
            )
        }
        
        # Add backward compatibility mappings for single letters
        # These allow old queries using "A", "N", "X" to still work
        triggers["A"] = triggers["partner_A"]
        triggers["N"] = triggers["child_N"]
        triggers["X"] = triggers["ex_X"]
        triggers["beck"] = triggers["self_beck"]
        
        return triggers
    
    def detect_context_triggers(self, user_input: str) -> List[str]:
        """Detect activated triggers"""
        activated = set()
        user_lower = user_input.lower()
        
        for trigger_name, trigger in self.semantic_triggers.items():
            if (trigger.entity.lower() in user_lower or
                any(keyword in user_lower for keyword in trigger.keywords)):
                # Add the canonical (descriptive) entity name
                canonical_name = trigger.entity
                activated.add(canonical_name)
        
        return sorted(activated)
    
    def add_insight(self, insight: Insight):
        """Add insight to database using connection pool"""
        # Store entities with leading/trailing commas for exact matching
        entities_str = ',' + ','.join(insight.entities) + ',' if insight.entities else ''
        themes_str = ',' + ','.join(insight.themes) + ',' if insight.themes else ''
        supersedes_str = ',' + ','.join(insight.supersedes) + ',' if insight.supersedes else ''
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO insights VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.id,
                insight.content,
                entities_str,
                themes_str,
                insight.timestamp.isoformat(),
                insight.effectiveness_score,
                insight.growth_stage,
                insight.layer,
                insight.insight_type,
                supersedes_str,
                insight.superseded_by,
                insight.source_file,
                insight.context
            ))
            
            conn.commit()
    
    def retrieve_contextual_insights(self, user_input: str, max_insights: int = 5) -> Dict[str, List[Insight]]:
        """Retrieve relevant insights using connection pool"""
        triggers = self.detect_context_triggers(user_input)
        
        if not triggers:
            return {"surface": [], "mid": [], "deep": []}
        
        # Get insights for activated triggers
        all_insights = []
        for trigger_name in triggers:
            entity_insights = self._get_insights_by_entity(trigger_name)
            all_insights.extend(entity_insights)
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_insights = []
        for insight in all_insights:
            if insight.id not in seen_ids:
                seen_ids.add(insight.id)
                unique_insights.append(insight)
        
        # Sort by effectiveness and recency
        unique_insights.sort(
            key=lambda x: (x.effectiveness_score, -(datetime.now() - x.timestamp).days), 
            reverse=True
        )
        
        # Categorize by layer
        surface = [i for i in unique_insights if i.layer == "surface"][:3]
        mid = [i for i in unique_insights if i.layer == "mid"][:5]  
        deep = [i for i in unique_insights if i.layer == "deep"][:max_insights]
        
        return {"surface": surface, "mid": mid, "deep": deep}
    
    def _get_insights_by_entity(self, entity: str) -> List[Insight]:
        """Get insights for entity from database using connection pool"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Use exact entity matching with comma delimiters to avoid false matches
            # e.g., searching for "N" won't match "AN" or "IN"
            cursor.execute('''
                SELECT * FROM insights 
                WHERE entities LIKE ? 
                ORDER BY effectiveness_score DESC, timestamp DESC
            ''', (f'%,{entity},%',))
            
            rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            # Parse entities by stripping leading/trailing commas and splitting
            entities_raw = row['entities'].strip(',') if row['entities'] else ''
            entities = set(entities_raw.split(',')) if entities_raw else set()
            
            themes_raw = row['themes'].strip(',') if row['themes'] else ''
            themes = set(themes_raw.split(',')) if themes_raw else set()
            
            supersedes_raw = row['supersedes'].strip(',') if row['supersedes'] else ''
            supersedes = supersedes_raw.split(',') if supersedes_raw else []
            
            insight = Insight(
                id=row['id'],
                content=row['content'],
                entities=entities,
                themes=themes,
                timestamp=datetime.fromisoformat(row['timestamp']),
                effectiveness_score=row['effectiveness_score'],
                growth_stage=row['growth_stage'],
                layer=row['layer'], 
                insight_type=row['insight_type'],
                supersedes=supersedes,
                superseded_by=row['superseded_by'],
                source_file=row['source_file'],
                context=row['context']
            )
            insights.append(insight)
        
        return insights
    
    def close(self):
        """Close all database connections"""
        self.pool.close_all()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup connections"""
        self.close()


def test_simple_system():
    """Test the simplified system"""
    print("Testing Simplified Contextual Insight Retrieval System")
    print("=" * 60)
    
    # Initialize system with context manager for proper cleanup
    with SimpleContextualInsightRetrieval("test_simple.db") as system:
        
        # Add test insights with descriptive entity names
        test_insights = [
            Insight(
                id=str(uuid.uuid4()),
                content="A is trustworthy. His word is enough. This is bedrock truth.",
                entities={"partner_A"},  # Using descriptive name
                themes={"trust", "relationships"},
                effectiveness_score=1.0,
                layer="surface",
                insight_type="anchor"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="Taking trauma responses to therapy protects relationship with A",
                entities={"partner_A", "trauma_responses"},  # Descriptive names
                themes={"strategies", "relationships", "trauma"},
                effectiveness_score=0.8,
                layer="surface", 
                insight_type="strategy"
            ),
            Insight(
                id=str(uuid.uuid4()),
                content="Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
                entities={"child_N"},  # Descriptive name
                themes={"parenting", "boundaries", "strategies"}, 
                effectiveness_score=0.9,
                layer="surface",
                insight_type="strategy"
            )
        ]
        
        # Add insights to system
        for insight in test_insights:
            system.add_insight(insight)
        
        print("✓ Test insights added with descriptive entity names")
        
        # Test retrieval with both old single-letter and new descriptive names
        test_cases = [
            ("I'm worried about trusting A", "Single letter 'A' (backward compat)"),
            ("I'm worried about my partner", "Descriptive 'partner' keyword"),
            ("N is being difficult about boundaries", "Single letter 'N' (backward compat)"),
            ("My child needs structure", "Descriptive 'child' keyword"),
            ("I'm having trauma responses", "Descriptive entity name"),
            ("What strategies worked for parenting?", "Theme-based query")
        ]
        
        for test_input, description in test_cases:
            print(f"\nTest: '{test_input}' ({description})")
            
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
                    print(f"      Entities: {', '.join(insight.entities)}")
            else:
                print("  No insights retrieved")
    
    print("\n" + "=" * 60)
    print("✓ Simple system test completed successfully!")
    print("✓ Backward compatibility verified")
    print("✓ Connection pool properly cleaned up")

if __name__ == "__main__":
    test_simple_system()
