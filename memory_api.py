#!/usr/bin/env python3
"""
Memory API for Claude Project Integration
Lightweight HTTP API for querying and adding insights
"""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from insight_system_simple import SimpleContextualInsightRetrieval, Insight
from datetime import datetime
from config import Config
from logging_config import get_logger
import uuid
import json
import threading
import os
import time
from functools import wraps

app = Flask(__name__)

# Setup rate limiting (using in-memory storage for local development)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{Config.RATE_LIMIT_PER_MINUTE} per minute"]
)
limiter.init_app(app)

# Setup logging
logger = get_logger('memory_api')

# Global memory system instance
memory_system = None

def validate_input(required_fields=None):
    """Decorator to validate request input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                logger.warning(f"Invalid content type for {request.endpoint}")
                return jsonify({"error": "Content-Type must be application/json"}), 400
            
            data = request.get_json(silent=True)
            if data is None:
                logger.warning(f"Invalid JSON for {request.endpoint}")
                return jsonify({"error": "Invalid JSON"}), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logger.warning(f"Missing required fields: {missing_fields}")
                    return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def verify_access_token():
    """Verify that requests come from authorized sources"""
    provided_token = request.headers.get('X-Memory-Token')
    
    if not provided_token:
        logger.warning(f"Missing access token from {request.remote_addr}")
        return False
    
    # Verify against any allowed project directory
    # Client generates token based on their current directory
    for allowed_dir in Config.ALLOWED_PROJECT_DIRS:
        # Expand user paths consistently
        allowed_path = os.path.expanduser(allowed_dir)
        expected_token = Config.generate_secure_token(allowed_path)
        
        if provided_token == expected_token:
            logger.debug(f"Valid access token from {request.remote_addr}")
            return True
    
    # Also check token for current server directory (expanded)
    current_dir = os.path.expanduser(os.getcwd())
    expected_token = Config.generate_secure_token(current_dir)
    
    if provided_token == expected_token:
        logger.debug(f"Valid access token from {request.remote_addr}")
        return True
    
    logger.warning(f"Invalid access token from {request.remote_addr}")
    return False

def init_memory_system():
    """Initialize the memory system"""
    global memory_system
    
    try:
        current_dir = os.getcwd()
        
        # Check if running from allowed project directory
        if not Config.is_path_allowed(current_dir):
            logger.error(f"Memory system access denied from: {current_dir}")
            logger.error(f"Must run from allowed directories: {Config.ALLOWED_PROJECT_DIRS}")
            return None
        
        # Get database path from config (handles directory creation)
        db_path = Config.get_database_path()
        
        logger.info(f"Initializing memory system with database: {db_path}")
        
        # Check if database needs initialization
        needs_init = not os.path.exists(db_path) or os.path.getsize(db_path) < 1000
        
        memory_system = SimpleContextualInsightRetrieval(db_path)
        
        # Only add demo data if database is new
        if needs_init:
            logger.info(f"Setting up new memory database at: {db_path}")
            setup_demo_data()
        
        logger.info("Memory system initialized successfully")
        return memory_system
        
    except Exception as e:
        logger.error(f"Failed to initialize memory system: {e}")
        return None

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
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@validate_input(required_fields=['input'])
def query_insights():
    """Query insights based on input text"""
    if not verify_access_token():
        return jsonify({"error": "Unauthorized access"}), 401
    
    if memory_system is None:
        logger.error("Memory system not initialized")
        return jsonify({"error": "Memory system not available"}), 503
    
    try:
        data = request.json
        user_input = data.get('input', '').strip()
        max_results = min(data.get('max_results', 3), 10)  # Cap at 10 results
        
        if len(user_input) > 5000:  # Limit input length
            logger.warning(f"Input too long: {len(user_input)} characters")
            return jsonify({"error": "Input too long (max 5000 characters)"}), 400
        
        logger.info(f"Querying insights for input: {user_input[:100]}...")
        
        start_time = time.time()
        insights = memory_system.retrieve_contextual_insights(user_input)
        query_time = time.time() - start_time
        
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
        
        logger.info(f"Query completed in {query_time:.3f}s, returned {len(formatted_insights)} insights")
        
        return jsonify({
            "insights": formatted_insights,
            "triggers": memory_system.detect_context_triggers(user_input),
            "total_available": len(insights.get("surface", []) + insights.get("mid", [])),
            "query_time": query_time
        })
        
    except Exception as e:
        logger.error(f"Error querying insights: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/add', methods=['POST'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@validate_input(required_fields=['content'])
def add_insight():
    """Add new insight"""
    if not verify_access_token():
        return jsonify({"error": "Unauthorized access"}), 401
    
    if memory_system is None:
        logger.error("Memory system not initialized")
        return jsonify({"error": "Memory system not available"}), 503
    
    try:
        data = request.json
        
        content = data.get('content', '').strip()
        if not content or len(content) > 2000:
            return jsonify({"error": "Content must be between 1 and 2000 characters"}), 400
        
        # Validate effectiveness score
        effectiveness_score = data.get('effectiveness_score', 0.5)
        if not isinstance(effectiveness_score, (int, float)) or not 0 <= effectiveness_score <= 1:
            return jsonify({"error": "Effectiveness score must be between 0 and 1"}), 400
        
        insight = Insight(
            id=str(uuid.uuid4()),
            content=content,
            entities=set(data.get('entities', [])),
            themes=set(data.get('themes', [])),
            effectiveness_score=effectiveness_score,
            layer=data.get('layer', 'surface'),
            insight_type=data.get('insight_type', 'observation'),
            timestamp=datetime.now(),
            source_file=data.get('source_file', 'claude_conversation'),
            context=data.get('context', 'Added via Claude')
        )
        
        memory_system.add_insight(insight)
        logger.info(f"Added insight: {insight.id} - {content[:100]}...")
        
        return jsonify({
            "success": True,
            "insight_id": insight.id,
            "message": "Insight added successfully"
        })
        
    except Exception as e:
        logger.error(f"Error adding insight: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    # Check if memory system is initialized
    if memory_system is None:
        return jsonify({
            "status": "error",
            "error": "Memory system not initialized"
        }), 503
    
    try:
        # Get basic system info without querying database directly
        return jsonify({
            "status": "running",
            "total_insights": "available",
            "entities": ["A", "N", "X", "trauma_responses"],  # Known entities
            "version": "1.0.0",
            "port": Config.API_PORT
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/entities', methods=['GET'])
def get_entities():
    """Get all entities being tracked"""
    if memory_system is None:
        return jsonify({"error": "Memory system not initialized"}), 503
    
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
    logger.info("Starting Memory API Server")
    logger.info(f"Configuration: {Config.get_config_dict()}")
    
    if not init_memory_system():
        logger.error("Failed to initialize memory system, exiting")
        return
    
    logger.info(f"Starting server on {Config.API_HOST}:{Config.API_PORT}")
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    run_server()
