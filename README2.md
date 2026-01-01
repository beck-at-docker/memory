# Claude Memory System - Technical Documentation

This document contains detailed configuration options, API reference, and advanced usage instructions.

## System Architecture

### Core Components

1. **Insight System** (`insight_system_simple.py`)
   - Stores and retrieves contextual insights
   - No ML dependencies, uses keyword matching
   - Layered architecture (surface/mid/deep)
   - SQLite database backend

2. **Memory API** (`memory_api.py`)
   - Flask-based HTTP API on port 8001
   - Endpoints: `/query`, `/add`, `/status`, `/entities`
   - Rate limiting (60 requests/minute)
   - Token-based authentication

3. **MCP Server** (`memory_mcp_server_simple.py`) 
   - Provides Claude Code integration
   - Tools: `query_memory`, `get_memory_status`
   - JSON-RPC 2.0 protocol

4. **Configuration** (`config.py`)
   - Centralized settings
   - PID file management
   - Security token generation
   - Path validation

### Data Flow

1. **Input**: User mentions entity (e.g., "I'm worried about trusting A")
2. **Trigger Detection**: System identifies keywords and themes
3. **Retrieval**: Searches database for relevant insights
4. **Layering**: Returns surface/mid/deep insights based on relevance
5. **Display**: Claude surfaces insights naturally in conversation

### Insight Types

- **anchor**: Bedrock truths that remain constant (effectiveness 1.0)
- **breakthrough**: Major realizations and shifts
- **strategy**: Practical approaches that work
- **observation**: General patterns and insights

## API Reference

### HTTP Endpoints

#### POST /query
Query for relevant insights.

**Request:**
```json
{
  "input": "worried about trusting A",
  "max_results": 3
}
```

**Headers:**
```
Content-Type: application/json
X-Memory-Token: <generated-token>
```

**Response:**
```json
{
  "insights": [
    {
      "content": "A is trustworthy. His word is enough.",
      "type": "anchor",
      "entities": ["A"],
      "themes": ["trust", "relationships"],
      "effectiveness": 1.0,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "triggers": ["A", "trust"],
  "total_available": 5,
  "query_time": 0.023
}
```

#### POST /add
Add new insight.

**Request:**
```json
{
  "content": "Taking trauma responses to therapy protects relationships",
  "entities": ["A", "trauma_responses"],
  "themes": ["strategies", "relationships"],
  "insight_type": "strategy",
  "effectiveness_score": 0.9
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
System status.

**Response:**
```json
{
  "status": "running",
  "total_insights": "available",
  "entities": ["A", "N", "X", "trauma_responses"],
  "version": "1.0.0",
  "port": 8001
}
```

#### GET /entities
Entity statistics.

**Response:**
```json
{
  "A": {
    "count": 12,
    "latest": "2024-01-15T14:22:00Z"
  },
  "N": {
    "count": 8,
    "latest": "2024-01-14T09:15:00Z"
  }
}
```

### MCP Tools (Available to Claude)

#### query_memory
Search for relevant insights.

**Parameters:**
```json
{
  "query": "trust and relationships"
}
```

**Returns:**
```
**Found insights:**
• A is trustworthy. His word is enough.
• Taking trauma responses to therapy protects relationships
```

#### get_memory_status
Check system status.

**Returns:**
```
✅ Memory system is running
Port: 8001
Status: running
```

## Database Schema

```sql
CREATE TABLE insights (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    entities TEXT,              -- Comma-separated list
    themes TEXT,                -- Comma-separated list
    timestamp TEXT,             -- ISO format
    effectiveness_score REAL,   -- 0.0 to 1.0
    growth_stage TEXT,
    layer TEXT,                 -- surface/mid/deep
    insight_type TEXT,          -- anchor/breakthrough/strategy/observation
    supersedes TEXT,
    superseded_by TEXT,
    source_file TEXT,
    context TEXT
);

CREATE INDEX idx_entities ON insights(entities);
CREATE INDEX idx_timestamp ON insights(timestamp);
CREATE INDEX idx_effectiveness ON insights(effectiveness_score);
CREATE INDEX idx_type ON insights(insight_type);
```

## Configuration

### Environment Variables

```bash
# Database location
export MEMORY_DB_PATH="$HOME/Documents/private/memory_data/personal_insights.db"

# API settings
export MEMORY_API_HOST="127.0.0.1"
export MEMORY_API_PORT="8001"

# Security
export SECRET_KEY="your-secret-key-here"

# Rate limiting
export RATE_LIMIT_PER_MINUTE="60"

# Timeouts
export CONNECTION_TIMEOUT="5"
export READ_TIMEOUT="10"

# Logging
export LOG_LEVEL="INFO"

# Allowed directories (comma-separated)
export ALLOWED_PROJECT_DIRS="~/Documents/private"
```

### Security Configuration

**Access Control:**
- API validates requests with HMAC tokens
- Only allowed directories can access the system
- Default allowed: `~/Documents/private`

**Token Generation:**
```python
# In config.py
token = hmac.new(
    SECRET_KEY.encode(),
    current_directory.encode(),
    hashlib.sha256
).hexdigest()
```

**File Permissions:**
```bash
# Secure the database
chmod 700 ~/Documents/private/memory_data/
chmod 600 ~/Documents/private/memory_data/*.db

# Secure logs
chmod 700 ~/Documents/private/logs/
```

## Process Management

The system uses PID files for reliable process tracking:

### PID Files

Located in `~/Documents/private/pids/`:
- `memory_api.pid` - API server process ID
- `memory_mcp.pid` - MCP server process ID (if running)

### Health Checks

The startup script polls the `/status` endpoint for up to 30 seconds:
- Checks every 1 second
- Verifies HTTP 200 response
- Confirms JSON response format

### Graceful Shutdown

1. Reads PID from file
2. Sends SIGTERM for graceful shutdown
3. Waits up to 5 seconds
4. Sends SIGKILL if still running
5. Removes PID file

## Customization

### Adding New Entities

Edit `insight_system_simple.py`:

```python
def _initialize_triggers(self):
    return {
        "A": SemanticTrigger(
            entity="A",
            keywords={"trust", "relationship", "trustworthy"},
            max_surface_insights=3
        ),
        # Add your own:
        "project_name": SemanticTrigger(
            entity="project_name",
            keywords={"deadline", "milestone", "deliverable"},
            max_surface_insights=2
        )
    }
```

### Adjusting Insight Retrieval

```python
# In insight_system_simple.py
def retrieve_contextual_insights(self, user_input: str, max_insights: int = 5):
    # Adjust these limits:
    surface = [i for i in all_insights if i.layer == "surface"][:3]  # Top 3
    mid = [i for i in all_insights if i.layer == "mid"][:5]          # Top 5
    deep = [i for i in all_insights if i.layer == "deep"][:max_insights]
```

## Database Management

### Backup

```bash
# Simple backup
cp ~/Documents/private/memory_data/personal_insights.db \
   ~/Documents/private/memory_data/backup_$(date +%Y%m%d).db

# SQL dump
sqlite3 ~/Documents/private/memory_data/personal_insights.db .dump > backup.sql
```

### Restore

```bash
# From backup file
cp ~/Documents/private/memory_data/backup_20240115.db \
   ~/Documents/private/memory_data/personal_insights.db

# From SQL dump
sqlite3 ~/Documents/private/memory_data/personal_insights.db < backup.sql
```

### Inspect Database

```bash
sqlite3 ~/Documents/private/memory_data/personal_insights.db

# Useful queries:
.schema insights
SELECT COUNT(*) FROM insights;
SELECT insight_type, COUNT(*) FROM insights GROUP BY insight_type;
SELECT * FROM insights WHERE effectiveness_score > 0.9;
SELECT DISTINCT entities FROM insights;
```

## Troubleshooting

### Common Issues

**1. Memory server won't start**
```bash
# Check what's wrong
./therapy.sh status

# View logs
cat logs/memory_api.log

# Check if port is in use
lsof -i :8001

# Full restart
./therapy.sh stop
./therapy.sh start
```

**2. Dependencies missing**
```bash
# Reinstall
source memory_env/bin/activate
pip install -r requirements_simple.txt
deactivate
./therapy.sh restart
```

**3. Claude Code can't connect**
```bash
# Ensure system is running
./therapy.sh status

# Test MCP server
python3 test_mcp_server.py

# Check config
cat ~/.config/claude-code/mcp_servers.json

# Restart Claude Code completely
```

**4. Permission denied errors**
```bash
# Make scripts executable
chmod +x therapy.sh therapy_wrapper.sh start_interactive_memory.sh

# Check database permissions
ls -la memory_data/
```

**5. Health check fails**
```bash
# Check logs for errors
cat logs/memory_api.log

# Test manually
curl http://localhost:8001/status

# Check if Python process started
ps aux | grep memory_api
```

## Testing

### Quick Tests

```bash
# Test API connection
python3 test_memory_system.py

# Test MCP server
python3 test_mcp_server.py

# Run full suite
python3 test_system.py
```

### Manual API Testing

```bash
# Activate environment
source memory_env/bin/activate

# Test status endpoint
curl http://localhost:8001/status

# Test query (requires token)
python3 -c "
from claude_memory_client import MemoryClient
client = MemoryClient()
result = client.query_memory('trust')
print(result)
"
```

## Performance

The system is designed for personal use:
- Handles hundreds of insights efficiently
- Query time typically < 50ms
- Low memory footprint (~50MB)
- Startup time ~2-3 seconds

For larger datasets, see optimization tips in the Technical Documentation section below.

## Security

- **Local only**: API binds to 127.0.0.1 (localhost)
- **Token authentication**: HMAC-based tokens per directory
- **No external access**: No internet connection required
- **Private data**: Database stored locally only

## Logging

Logs are written to `logs/memory_api.log`:

```bash
# Watch logs in real-time
tail -f logs/memory_api.log

# View errors only
grep ERROR logs/memory_api.log

# Last 50 lines
tail -50 logs/memory_api.log
```

## Auto-Start on Login (Optional)

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
# Start memory system on login
~/Documents/private/therapy.sh start > /dev/null 2>&1
```

## Support Files

- **QUICK_REFERENCE.md** - Daily usage commands
- **CLAUDE.md** - Claude Code integration details
- **.env.example** - Environment variable template

## Technical Details

For advanced topics, see sections below:
- API authentication details
- Database optimization
- Custom trigger configuration
- Hook system implementation
- Performance tuning

---

## Advanced Topics

### Custom Semantic Triggers

Create specialized triggers for your use case:

```python
# In insight_system_simple.py
SemanticTrigger(
    entity="work_project",
    keywords={"deadline", "sprint", "standup", "backlog"},
    max_surface_insights=3,
    context_patterns=[
        r"project.*stuck",
        r"team.*struggling",
        r"deadline.*approaching"
    ]
)
```

### Effectiveness Scoring

Insights are ranked by effectiveness (0.0 to 1.0):
- **1.0**: Absolute truths, always helpful
- **0.8-0.9**: Highly effective strategies
- **0.6-0.7**: Usually helpful observations
- **0.4-0.5**: Context-dependent insights
- **< 0.4**: Historical or deprecated

### Layer System

**Surface** (limit: 3) - Most immediately relevant
- Displayed first in responses
- Highest effectiveness scores
- Most recent and applicable

**Mid** (limit: 5) - Supporting context
- Additional relevant insights
- Moderate effectiveness
- Broader applicability

**Deep** (limit: configurable) - Historical patterns
- Long-term trends
- Lower immediate relevance
- Useful for comprehensive analysis

### Crisis Detection

The system activates special handling when detecting:

```python
CRISIS_PATTERNS = [
    r'\b(?:kill|harm|hurt|suicide)\s+(?:myself|me)\b',
    r'\bsuicidal\s+(?:thoughts|ideation)\b',
    r'\bcan\'?t\s+(?:take|handle)\s+this\s+anymore\b',
    r'\beveryone.*better.*without\s+me\b',
]
```

**Crisis Mode Behavior:**
- Surfaces ALL anchor insights immediately
- Returns strategies with effectiveness > 0.8
- No progressive disclosure
- Focuses on grounding and coping

### Database Optimization

For datasets with 1000+ insights:

```sql
-- Additional indexes
CREATE INDEX idx_content_lower ON insights(LOWER(content));
CREATE INDEX idx_composite ON insights(effectiveness_score DESC, timestamp DESC);

-- Vacuum database periodically
VACUUM;

-- Analyze for query optimization
ANALYZE;
```

### Rate Limiting Configuration

Edit `config.py`:

```python
# Requests per minute
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))

# In memory_api.py, can set per-endpoint limits:
@app.route('/query', methods=['POST'])
@limiter.limit("30 per minute")  # More restrictive for expensive queries
def query_insights():
    ...
```

### Timeout Configuration

```python
# In config.py
CONNECTION_TIMEOUT = 5   # Initial connection
READ_TIMEOUT = 10        # Wait for response

# Health check settings
HEALTH_CHECK_RETRIES = 30        # Number of attempts
HEALTH_CHECK_INTERVAL = 1.0      # Seconds between attempts
```

## Development

### Running Tests

```bash
source memory_env/bin/activate

# Unit tests
python3 test_system.py

# Integration tests  
python3 test_access_restriction.py

# Manual testing
python3 claude_memory_client.py
```

### Adding New API Endpoints

Edit `memory_api.py`:

```python
@app.route('/new_endpoint', methods=['GET'])
@limiter.limit("60 per minute")
def new_endpoint():
    """Description of what this does"""
    if not verify_access_token():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Your logic here
        return jsonify({"result": "success"})
    except Exception as e:
        logger.error(f"Error in new_endpoint: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
```

### Adding New MCP Tools

Edit `memory_mcp_server_simple.py`:

```python
# In tools/list response
{
    "name": "new_tool",
    "description": "What this tool does",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
}

# In tools/call handler
elif tool_name == "new_tool":
    return await self.new_tool(msg_id, arguments)
```

### Logging Configuration

Edit `logging_config.py`:

```python
# Change log level
logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR

# Change log format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Rotate logs more frequently
file_handler = logging.handlers.RotatingFileHandler(
    'logs/memory.log',
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=10  # Keep 10 old logs
)
```

## Performance Tuning

### For Large Datasets (1000+ insights)

```python
# In insight_system_simple.py
class SimpleContextualInsightRetrieval:
    def retrieve_contextual_insights(self, user_input: str, max_insights: int = 5):
        # Limit database queries
        all_insights.sort(
            key=lambda x: (x.effectiveness_score, -(datetime.now() - x.timestamp).days),
            reverse=True
        )[:50]  # Only consider top 50
```

### Memory Usage

The system uses minimal memory:
- ~20MB baseline (Flask + dependencies)
- ~5-10MB per 1000 insights in memory
- SQLite uses minimal RAM (queries on disk)

### Query Optimization

```python
# In insight_system_simple.py
def _get_insights_by_entity(self, entity: str) -> List[Insight]:
    # Add LIMIT clause to SQL
    cursor.execute('''
        SELECT * FROM insights 
        WHERE entities LIKE ? 
        ORDER BY effectiveness_score DESC, timestamp DESC
        LIMIT 100
    ''', (f'%{entity}%',))
```

## Security Best Practices

### 1. Set a Strong Secret Key

```bash
# Generate a random key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Set it in your environment
export SECRET_KEY="<generated-key>"
```

### 2. Restrict File Permissions

```bash
chmod 600 ~/Documents/private/memory_data/personal_insights.db
chmod 700 ~/Documents/private/memory_data/
chmod 700 ~/Documents/private/pids/
chmod 700 ~/Documents/private/logs/
```

### 3. Limit Network Access

The API already binds to localhost only (127.0.0.1), but you can additionally:

```bash
# Firewall rule (if needed)
sudo iptables -A INPUT -p tcp --dport 8001 ! -s 127.0.0.1 -j DROP
```

### 4. Allowed Directories

Restrict which directories can access the API:

```python
# In config.py
ALLOWED_PROJECT_DIRS = os.getenv('ALLOWED_PROJECT_DIRS', 
    '~/Documents/private,~/Projects/therapy').split(',')
```

## Maintenance

### Log Rotation

Logs rotate automatically:
- Max size: 10MB per file
- Keep 5 backup files
- Total max: 50MB of logs

### Database Cleanup

```sql
-- Remove old low-effectiveness insights
DELETE FROM insights 
WHERE effectiveness_score < 0.3 
AND timestamp < datetime('now', '-6 months');

-- Remove superseded insights
DELETE FROM insights WHERE superseded_by IS NOT NULL;

-- Vacuum to reclaim space
VACUUM;
```

### System Health Checks

```bash
# Check system health
./therapy.sh status

# Check database integrity
sqlite3 ~/Documents/private/memory_data/personal_insights.db "PRAGMA integrity_check;"

# Check disk space
df -h ~/Documents/private/memory_data/

# Check log size
du -h ~/Documents/private/logs/
```

## Monitoring

### Key Metrics to Watch

1. **Query Performance**
   - Should be < 100ms for most queries
   - Check `query_time` in API responses

2. **Database Size**
   - Typical: ~1KB per insight
   - Alert if > 100MB

3. **Log Growth**
   - Should stay under 50MB total
   - Rotate if growing quickly

4. **Memory Usage**
   - Normal: 20-50MB
   - Alert if > 200MB

### Log Analysis

```bash
# Count queries per hour
grep "Querying insights" logs/memory_api.log | wc -l

# Average query time
grep "Query completed" logs/memory_api.log | \
  awk '{print $NF}' | \
  awk '{sum+=$1; count++} END {print sum/count}'

# Error rate
grep ERROR logs/memory_api.log | wc -l
```

## File Structure

```
~/Documents/private/
├── config.py                      # Configuration
├── logging_config.py              # Logging setup
├── insight_system_simple.py       # Core insight system
├── claude_memory_client.py        # Client library
├── memory_api.py                  # API server
├── memory_mcp_server_simple.py    # MCP server
├── therapy.sh                     # Control script
├── therapy_wrapper.sh             # Implementation
├── start_interactive_memory.sh    # Alternative starter
├── setup_env.py                   # Environment setup
├── requirements_simple.txt        # Dependencies
├── README.md                      # User docs
├── README2.md                     # This file
├── QUICK_REFERENCE.md             # Quick commands
├── logs/                          # Log files
│   └── memory_api.log
├── pids/                          # Process IDs
│   └── memory_api.pid
├── memory_data/                   # Database
│   └── personal_insights.db
└── memory_env/                    # Virtual environment
    ├── bin/
    ├── lib/
    └── pyvenv.cfg
```

## License

Private repository - for personal use only.

---

*Technical documentation for the Claude Memory System*
