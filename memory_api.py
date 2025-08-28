#!/usr/bin/env python3
"""
Memory API for Claude Project Integration
Lightweight HTTP API for querying and adding insights
"""

from flask import Flask, request, jsonify
from insight_system_simple import SimpleContextualInsightRetrieval, Insight
from datetime import datetime
import uuid
import json
import threading
import os
import hashlib

app = Flask(__name__)

# Global memory system instance
memory_system = None

def verify_access_token():
    """Verify that requests come from authorized sources"""
    # Expected token: hash of the memory project directory path
    allowed_project = os.path.expanduser("~/Documents/private/memory")
    expected_token = hashlib.sha256(allowed_project.encode()).hexdigest()[:16]
    
    # Check for token in headers
    provided_token = request.headers.get('X-Memory-Token')
    
    if not provided_token or provided_token != expected_token:
        return False
    return True

def init_memory_system():
    """Initialize the memory system"""
    global memory_system
    
    # Check if running from allowed project directory
    allowed_project = os.path.expanduser("~/Documents/private/memory")
    current_dir = os.getcwd()
    
    if not current_dir.startswith(allowed_project):
        print(f"Memory system access denied from: {current_dir}")
        print(f"Must run from: {allowed_project}")
        return None
    
    # Store data in separate data directory
    data_dir = os.path.expanduser("~/Documents/private/memory_data")
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, "personal_insights.db")
    memory_system = SimpleContextualInsightRetrieval(db_path)
    
    # Only add demo data if database is completely empty
    if not os.path.exists(db_path) or os.path.getsize(db_path) < 1000:
        print(f"Setting up new memory database at: {db_path}")
        setup_demo_data()

def setup_demo_data():
    """Setup demo insights"""
    demo_insights = [
        Insight(
            id=str(uuid.uuid4()),
            content="A is trustworthy. His word is enough. This is bedrock truth.",
            entities={"A"},
            themes={"trust", "relationships"},
            effectiveness_score=1.0,
            layer="surface",
            insight_type="anchor",
            timestamp=datetime.now(),
            source_file="claude_integration",
            context="Core trust anchor for A"
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
            source_file="claude_integration",
            context="Effective strategy for managing activation"
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="Boundaries with N are love, not cruelty. Hold the line with love instead of fear.",
            entities={"N"},
            themes={"parenting", "boundaries", "strategies"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="strategy",
            timestamp=datetime.now(),
            source_file="claude_integration",
            context="Core parenting boundary philosophy"
        ),
        Insight(
            id=str(uuid.uuid4()),
            content="X's voice creates inadequacy-scanning. Recognize it as X, not truth.",
            entities={"X", "trauma_responses"},
            themes={"trauma", "strategies", "recognition"},
            effectiveness_score=0.9,
            layer="surface",
            insight_type="anchor",
            timestamp=datetime.now(),
            source_file="claude_integration",
            context="Recognition strategy for X's voice"
        )
    ]
    
    for insight in demo_insights:
        memory_system.add_insight(insight)

@app.route('/query', methods=['POST'])
def query_insights():
    """Query insights based on input text"""
    if not verify_access_token():
        return jsonify({"error": "Unauthorized access"}), 401
        
    data = request.json
    user_input = data.get('input', '')
    max_results = data.get('max_results', 3)
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    insights = memory_system.retrieve_contextual_insights(user_input)
    
    # Format for Claude
    formatted_insights = []
    for insight in insights.get("surface", [])[:max_results]:
        formatted_insights.append({
            "content": insight.content,
            "type": insight.insight_type,
            "entities": list(insight.entities),
            "themes": list(insight.themes),
            "effectiveness": insight.effectiveness_score,
            "timestamp": insight.timestamp.isoformat()
        })
    
    return jsonify({
        "insights": formatted_insights,
        "triggers": memory_system.detect_context_triggers(user_input),
        "total_available": len(insights.get("surface", []) + insights.get("mid", []))
    })

@app.route('/add', methods=['POST'])
def add_insight():
    """Add new insight"""
    if not verify_access_token():
        return jsonify({"error": "Unauthorized access"}), 401
        
    data = request.json
    
    insight = Insight(
        id=str(uuid.uuid4()),
        content=data.get('content', ''),
        entities=set(data.get('entities', [])),
        themes=set(data.get('themes', [])),
        effectiveness_score=data.get('effectiveness_score', 0.5),
        layer=data.get('layer', 'surface'),
        insight_type=data.get('insight_type', 'observation'),
        timestamp=datetime.now(),
        source_file=data.get('source_file', 'claude_conversation'),
        context=data.get('context', 'Added via Claude')
    )
    
    memory_system.add_insight(insight)
    
    return jsonify({
        "success": True,
        "insight_id": insight.id,
        "message": "Insight added successfully"
    })

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        # Get basic system info without querying database directly
        return jsonify({
            "status": "running",
            "total_insights": "available",
            "entities": ["A", "N", "X", "trauma_responses"],  # Known entities
            "version": "1.0.0",
            "port": 5001
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/entities', methods=['GET'])
def get_entities():
    """Get all entities being tracked"""
    try:
        # Get stats for known entities
        entities = ["A", "N", "X", "trauma_responses"]
        entity_stats = {}
        
        for entity in entities:
            try:
                insights = memory_system._get_insights_by_entity(entity)
                entity_stats[entity] = {
                    "count": len(insights),
                    "latest": max(i.timestamp for i in insights).isoformat() if insights else None
                }
            except Exception:
                entity_stats[entity] = {
                    "count": 0,
                    "latest": None
                }
        
        return jsonify(entity_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_server():
    """Run the Flask server"""
    init_memory_system()
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_server()