# Claude Memory System - Technical Documentation

This document contains detailed configuration options, API reference, and advanced usage instructions.

## System Architecture

### Core Components

1. **Insight System** (`insight_system_simple.py`)
   - Stores and retrieves contextual insights
   - No ML dependencies, uses keyword matching
   - Layered architecture (surface/mid/deep)

2. **Memory API** (`memory_api.py`)
   - HTTP API on port 5001
   - Endpoints: `/query`, `/add`, `/status`, `/entities`

3. **MCP Server** (`memory_mcp_server_simple.py`) 
   - Provides Claude Code integration
   - Tools: `query_memory`, `add_insight`, `get_memory_status`

4. **Hooks System** (`claude_hooks.py`)
   - Monitors conversations for insights
   - Automatic insight retrieval
   - Crisis detection and response

### Data Flow

1. **Input**: User mentions entity (e.g., "I'm worried about trusting my partner")
2. **Trigger Detection**: System identifies keywords and themes
3. **Retrieval**: Searches database for relevant insights
4. **Layering**: Returns surface/mid/deep insights based on relevance
5. **Display**: Claude surfaces insights naturally in conversation

### Insight Types

- **anchor**: Bedrock truths that remain constant (effectiveness 1.0)
- **breakthrough**: Major realizations and shifts
- **strategy**: Practical approaches that work
- **observation**: General patterns and insights

### Crisis Mode

Automatically activates when detecting crisis language:
- Surfaces ALL anchor insights immediately
- Prioritizes highest effectiveness strategies (>0.8)
- No progressive disclosure - everything accessible

## Detailed Setup Instructions

### Prerequisites

- Python 3.8+
- Claude Code (for full integration)

### Step 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/beck-at-docker/memory.git
cd memory

# Set up Python virtual environment and dependencies
python3 setup_env.py
```

This creates:
- `memory_env/` virtual environment
- Installs dependencies from `requirements_simple.txt`

### Step 2: Claude Code Integration Setup

```bash
python3 setup_claude_integration.py
```

This script will:
1. Install MCP dependencies
2. Create MCP server configuration
3. Set up Claude Code hooks
4. Generate startup scripts

### Step 3: Claude Code Configuration

#### Global MCP Server Configuration

Add to your Claude Code settings (`~/.config/claude-code/settings.json`):

```json
{
  "mcpServers": {
    "memory-system": {
      "command": "python3",
      "args": ["/path/to/memory/memory_mcp_server_simple.py"],
      "env": {
        "PYTHONPATH": "/path/to/memory",
        "PATH": "/path/to/memory/memory_env/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

#### Project-Specific Configuration

For project-specific memory integration, add to your project's `claude_code_config.json`:

```json
{
  "mcpServers": {
    "memory-system": {
      "command": "python3",
      "args": ["/Users/beck/Documents/private/memory/memory_mcp_server_simple.py"],
      "env": {
        "PYTHONPATH": "/Users/beck/Documents/private/memory"
      }
    }
  },
  "hooks": {
    "user-prompt-submit": "python3 /Users/beck/Documents/private/memory/claude_hooks/user_prompt_submit.py \"$PROMPT\"",
    "post-response": "python3 /Users/beck/Documents/private/memory/claude_hooks/post_response.py"
  }
}
```

#### Global Hooks Configuration

Add automatic conversation monitoring to global settings:

```json
{
  "hooks": {
    "user-prompt-submit": "python3 /path/to/memory/claude_hooks/user_prompt_submit.py \"$PROMPT\"",
    "post-response": "python3 /path/to/memory/claude_hooks/post_response.py"
  }
}
```

### Environment Variables

Set these in your shell environment:

```bash
export MEMORY_DB_PATH="$HOME/Documents/private/memory_data/personal_insights.db"
export MEMORY_API_PORT=5001
export MEMORY_LOG_LEVEL=INFO
```

## Configuration Options

### Memory System Configuration

Edit `insight_system_simple.py` to customize:

#### Entity Triggers

```python
def _initialize_triggers(self):
    return {
        "partner": SemanticTrigger(
            entity="partner",
            keywords={"trust", "relationship", "communication", "support"},
            max_surface_insights=3
        ),
        "child": SemanticTrigger(
            entity="child", 
            keywords={"boundaries", "parenting", "school", "routines"},
            max_surface_insights=2
        ),
        "work": SemanticTrigger(
            entity="work",
            keywords={"stress", "deadlines", "colleagues", "projects"},
            max_surface_insights=2
        )
    }
```

#### Insight Layers

```python
class LayeredArchitecture:
    def __init__(self):
        self.surface_limit = 5      # Most relevant insights
        self.mid_limit = 15         # Supporting context  
        self.deep_limit = 50        # Historical patterns
```

#### Crisis Detection Keywords

```python
crisis_keywords = [
    "crisis", "emergency", "panic", "overwhelmed",
    "falling apart", "can't handle", "too much",
    "breakdown", "meltdown", "desperate"
]
```

### Adding New Entities

To track new people or concepts:

1. Edit `insight_system_simple.py`:

```python
def _initialize_triggers(self):
    triggers = self._get_default_triggers()
    
    # Add new entity
    triggers["therapist"] = SemanticTrigger(
        entity="therapist",
        keywords={"therapy", "session", "counseling", "treatment"},
        max_surface_insights=3
    )
    
    return triggers
```

2. Restart the memory system

### Customizing Insight Classification

Edit insight type patterns in `insight_system_simple.py`:

```python
def _classify_insight_type(self, content: str) -> str:
    content_lower = content.lower()
    
    # Custom patterns
    if re.search(r'game.?changer|revolutionary', content, re.IGNORECASE):
        return "breakthrough"
    
    if re.search(r'works every time|proven strategy', content, re.IGNORECASE):
        return "strategy"
        
    if re.search(r'fundamental truth|always remember', content, re.IGNORECASE):
        return "anchor"
    
    # Default patterns...
```

## API Reference

### HTTP Endpoints

#### POST /query
Query for relevant insights.

**Request:**
```json
{
  "query": "worried about trusting partner",
  "max_insights": 10
}
```

**Response:**
```json
{
  "surface": [
    {
      "id": "uuid-1234",
      "content": "Trust builds through consistent actions over time",
      "entities": ["partner"],
      "themes": ["trust", "relationships"],
      "insight_type": "anchor",
      "effectiveness_score": 0.9,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "mid": [...],
  "deep": [...],
  "total_insights": 15,
  "triggers_activated": ["partner", "trust"]
}
```

#### POST /add
Add new insight.

**Request:**
```json
{
  "content": "Partner is trustworthy. Actions match words consistently.",
  "entities": ["partner"],
  "themes": ["trust", "relationships"],
  "insight_type": "anchor",
  "effectiveness_score": 1.0,
  "growth_stage": "current",
  "source_file": "conversation_2024-01-15.txt"
}
```

**Response:**
```json
{
  "success": true,
  "insight_id": "uuid-5678",
  "message": "Insight added successfully"
}
```

#### GET /status
System status and statistics.

**Response:**
```json
{
  "status": "running",
  "database_path": "/path/to/insights.db",
  "total_insights": 247,
  "entities": {
    "partner": 45,
    "child": 32,
    "work": 28
  },
  "insight_types": {
    "anchor": 15,
    "breakthrough": 23,
    "strategy": 67,
    "observation": 142
  },
  "uptime": "2h 34m"
}
```

#### GET /entities
Entity statistics and counts.

**Response:**
```json
{
  "entities": {
    "partner": {
      "count": 45,
      "themes": ["trust", "communication", "support"],
      "avg_effectiveness": 0.78,
      "recent_insights": 12
    },
    "child": {
      "count": 32,
      "themes": ["boundaries", "parenting", "school"],
      "avg_effectiveness": 0.82,
      "recent_insights": 8
    }
  }
}
```

### MCP Tools (Available to Claude)

#### query_memory
Search for relevant insights based on input text.

**Parameters:**
- `query` (string): Search text
- `max_insights` (integer, optional): Maximum insights to return

**Returns:**
- Layered insights (surface/mid/deep)
- Activated triggers
- Total count

#### add_insight
Capture new insights from conversations.

**Parameters:**
- `content` (string): Insight text
- `entities` (array): Related entities
- `themes` (array): Related themes  
- `insight_type` (string): Type of insight
- `effectiveness_score` (float): Effectiveness rating

**Returns:**
- Success status
- Generated insight ID

#### get_memory_status
Check system status and statistics.

**Returns:**
- System status
- Database statistics
- Entity counts
- Performance metrics

#### detect_conversation_insights
Analyze conversation text for potential insights.

**Parameters:**
- `text` (string): Conversation text to analyze

**Returns:**
- Suggested insights to capture
- Detected entities and themes
- Recommended insight types

## Database Management

### Database Schema

```sql
CREATE TABLE insights (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    entities TEXT,              -- JSON array of entities
    themes TEXT,                -- JSON array of themes
    timestamp TEXT,
    effectiveness_score REAL,
    growth_stage TEXT,
    layer TEXT,
    insight_type TEXT,
    supersedes TEXT,            -- JSON array of superseded insight IDs
    superseded_by TEXT,         -- ID of insight that supersedes this one
    source_file TEXT,
    context TEXT
);

CREATE INDEX idx_entities ON insights(entities);
CREATE INDEX idx_themes ON insights(themes);
CREATE INDEX idx_timestamp ON insights(timestamp);
CREATE INDEX idx_effectiveness ON insights(effectiveness_score);
CREATE INDEX idx_type ON insights(insight_type);
```

### Backup and Migration

#### Backup Database

```bash
# Simple file copy
cp ~/Documents/private/memory_data/personal_insights.db ~/backup/insights_backup_$(date +%Y%m%d).db

# SQLite dump
sqlite3 ~/Documents/private/memory_data/personal_insights.db .dump > ~/backup/insights_dump_$(date +%Y%m%d).sql
```

#### Export to JSON

```bash
source memory_env/bin/activate
python3 -c "
from claude_memory_client import MemoryClient
import json

client = MemoryClient()
# This would need to be implemented in the client
insights = client.export_all_insights()
with open('insights_backup.json', 'w') as f:
    json.dump(insights, f, indent=2)
"
```

#### Restore from Backup

```bash
# From SQLite backup
cp ~/backup/insights_backup_20240115.db ~/Documents/private/memory_data/personal_insights.db

# From SQL dump
sqlite3 ~/Documents/private/memory_data/personal_insights.db < ~/backup/insights_dump_20240115.sql
```

## Performance Tuning

### For Large Insight Databases

Edit `insight_system_simple.py`:

```python
class SimpleContextualInsightRetrieval:
    def __init__(self, db_path="insights.db"):
        # Reduce search results for faster queries
        self.max_search_results = 100
        
        # Increase cache size for better performance  
        self.cache_size = 100
        
        # Optimize database connections
        self.connection_pool_size = 5
```

### Database Optimization

```sql
-- Add indexes for better query performance
CREATE INDEX idx_content_fts ON insights USING fts(content);
CREATE INDEX idx_entities_gin ON insights USING gin(entities);

-- Analyze tables for query planner
ANALYZE insights;
```

### Memory Usage Optimization

```python
# In insight_system_simple.py
class LayeredArchitecture:
    def __init__(self):
        # Reduce limits for lower memory usage
        self.surface_limit = 3
        self.mid_limit = 8
        self.deep_limit = 20
```

## Advanced Debugging

### Enable Debug Logging

```bash
export MEMORY_LOG_LEVEL=DEBUG
export MEMORY_DEBUG_SQL=true
./start_interactive_memory.sh
```

### Log Files

```bash
# System logs
tail -f ~/Documents/private/memory_data/memory_system.log

# API access logs  
tail -f ~/Documents/private/memory_data/api_access.log

# Hook execution logs
tail -f ~/Documents/private/memory_data/hooks.log
```

### Database Inspection

```bash
sqlite3 ~/Documents/private/memory_data/personal_insights.db

# Useful queries
.schema insights
SELECT COUNT(*) FROM insights;
SELECT insight_type, COUNT(*) FROM insights GROUP BY insight_type;
SELECT * FROM insights WHERE effectiveness_score > 0.9;
```

### MCP Server Debugging

```bash
# Test MCP server directly
cd /path/to/memory
source memory_env/bin/activate
python3 memory_mcp_server_simple.py --debug
```

### Hook Debugging

```bash
# Test hooks manually
python3 claude_hooks/user_prompt_submit.py "test prompt"
python3 claude_hooks/post_response.py
```

## Security Considerations

### Data Privacy

- Insights database contains personal information
- Database file should have restrictive permissions:
  ```bash
  chmod 600 ~/Documents/private/memory_data/personal_insights.db
  ```

### Network Security

- API server runs on localhost only (127.0.0.1)
- No external network access required
- MCP server uses local pipes/sockets

### File Permissions

```bash
# Set secure permissions
chmod 700 ~/Documents/private/memory_data/
chmod 600 ~/Documents/private/memory_data/*
chmod +x claude_hooks/*.py
```

## Development and Contributing

### Code Structure

```
memory/
├── insight_system_simple.py         # Core insight system
├── memory_api.py                    # HTTP API server
├── claude_memory_client.py          # Client library
├── memory_mcp_server_simple.py      # MCP server
├── claude_hooks.py                  # Hook implementations
├── claude_hooks/                    # Hook scripts directory
│   ├── user_prompt_submit.py        #   Pre-prompt processing hook
│   └── post_response.py             #   Post-response processing hook
├── setup_env.py                     # Environment setup
├── setup_claude_integration.py      # Claude integration setup
├── therapy.sh                       # System management script
├── start_interactive_memory.sh      # Interactive memory launcher
├── start_mcp_server.sh             # MCP server startup
├── test_system.py                   # Main test suite
├── test_access_restriction.py       # Security tests
├── extract_conversation_insights.py # Conversation analysis
├── config.py                        # Configuration management
├── logging_config.py                # Logging configuration
├── requirements_simple.txt          # Python dependencies
├── .env.example                     # Environment template
├── CLAUDE.md                        # Claude Code integration docs
├── logs/                            # Log files directory
│   └── claude_memory.log            #   System log file
├── README.md                        # User documentation
└── README2.md                       # Technical documentation
```

### Adding New Features

1. **New Insight Types**: Edit `_classify_insight_type()` in `insight_system_simple.py`
2. **New Triggers**: Add to `_initialize_triggers()` 
3. **New API Endpoints**: Add routes to `memory_api.py`
4. **New MCP Tools**: Add methods to `memory_mcp_server_simple.py`

### Testing Changes

```bash
# Run full test suite
source memory_env/bin/activate
python3 test_system.py

# Test specific components
python3 -m pytest tests/ -v

# Manual API testing
curl -X POST http://localhost:5001/query -d '{"query": "test"}'
```

## License

Private repository - for personal use only.

---

*Technical documentation for the Claude Memory System*