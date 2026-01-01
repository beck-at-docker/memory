# Claude Memory System

A contextual insight retrieval system that integrates with Claude conversations to provide intelligent memory and conversation continuity.

## What This Does

- Automatically surfaces relevant insights when you mention specific people, topics, or themes
- Provides crisis support by detecting distress language and offering grounding insights  
- Maintains conversation continuity without overwhelming detail
- Tracks growth and focuses on transformation rather than static facts
- Integrates seamlessly with Claude Code

## Quick Start

### 1. Install Dependencies

```bash
cd ~/Documents/private
python3 setup_env.py
```

This creates a virtual environment and installs required packages (Flask, Flask-Limiter, Requests).

### 2. Start the System

```bash
./therapy.sh start
```

You should see:
```
[INFO] Activating virtual environment...
[INFO] Starting memory API server...
[INFO] Memory API started (PID: 12345)
[INFO] Waiting for memory API to be ready...
[INFO] Memory API is healthy!
✅ Memory system started successfully
   API: http://localhost:8001
```

### 3. Check Status

```bash
./therapy.sh status
```

### 4. Claude Code Integration

The system is already configured for Claude Code at:
```
~/.config/claude-code/mcp_servers.json
```

**Restart Claude Code** to load the memory system.

## Daily Usage

### Control Commands

```bash
./therapy.sh start    # Start the memory system
./therapy.sh status   # Check if running
./therapy.sh stop     # Stop the memory system
./therapy.sh restart  # Restart
```

### Using with Claude

Once Claude Code is restarted, Claude will automatically:
- Surface relevant memories when you discuss related topics
- Detect breakthrough moments
- Offer to save important insights

You can also explicitly ask:
```
"Search my memory for insights about [topic]"
"Check my memory system status"
"Save this insight to my memory"
```

## How It Works

### Automatic Insight Retrieval

The system surfaces insights when you mention:

**People or Relationships:**
```
You: "I'm having trust issues in my relationship"
Claude: [Automatically retrieves insights about trust and relationships]
```

**Themes or Topics:**
```
You: "I'm struggling with setting boundaries at work"
Claude: [Surfaces boundary strategies and workplace insights]
```

### Example Interaction

```
You: "I'm worried about whether I can trust someone new in my life"

Claude: Based on your insights:

⚓ A is trustworthy. His word is enough. This is bedrock truth.
🎯 Taking trauma responses to therapy protects relationships
👁️ Trust builds through consistent actions over time

These patterns suggest the doubts might be protective rather 
than evidence-based. What specific behaviors are triggering concern?
```

## System Architecture

### Core Components

- **insight_system_simple.py** - Database and retrieval logic
- **memory_api.py** - HTTP API server (port 8001)
- **memory_mcp_server_simple.py** - MCP server for Claude Code
- **claude_memory_client.py** - Client library for API
- **config.py** - Configuration management
- **logging_config.py** - Logging setup

### Control Scripts

- **therapy.sh** - Main control interface
- **therapy_wrapper.sh** - Implementation with health checks
- **start_interactive_memory.sh** - Alternative starter
- **setup_env.py** - Virtual environment setup

### Data Storage

- **Database**: `~/Documents/private/memory_data/personal_insights.db`
- **Logs**: `~/Documents/private/logs/memory_api.log`
- **PIDs**: `~/Documents/private/pids/memory_api.pid`

## Files and Directories

```
/Users/beck/Documents/private/
├── config.py                    # Configuration
├── memory_api.py                # API server
├── claude_memory_client.py      # Client library
├── insight_system_simple.py     # Core logic
├── logging_config.py            # Logging
├── memory_mcp_server_simple.py  # MCP server
├── therapy.sh                   # Control script
├── therapy_wrapper.sh           # Implementation
├── start_interactive_memory.sh  # Alternative starter
├── setup_env.py                 # Setup script
├── requirements_simple.txt      # Dependencies
├── README.md                    # This file
├── README2.md                   # Technical docs
├── QUICK_REFERENCE.md           # Daily commands
├── logs/                        # Log files
│   └── memory_api.log
├── pids/                        # Process IDs
│   └── memory_api.pid
├── memory_data/                 # Database
│   └── personal_insights.db
└── memory_env/                  # Virtual environment
```

## Troubleshooting

### Memory Server Won't Start

```bash
# Check status
./therapy.sh status

# View logs
cat logs/memory_api.log

# Restart
./therapy.sh restart
```

### Port Already in Use

```bash
# Find what's using port 8001
lsof -i :8001

# Stop and restart
./therapy.sh stop
./therapy.sh start
```

### Dependencies Missing

```bash
# Reinstall
source memory_env/bin/activate
pip install -r requirements_simple.txt
./therapy.sh restart
```

### Claude Code Not Connecting

1. Make sure memory system is running: `./therapy.sh status`
2. Restart Claude Code completely
3. Test MCP server: `python3 test_mcp_server.py`
4. Check config: `cat ~/.config/claude-code/mcp_servers.json`

## Testing

```bash
# Test the API
python3 test_memory_system.py

# Test the MCP server
python3 test_mcp_server.py

# Run full test suite
python3 test_system.py
```

## Advanced Configuration

See [README2.md](README2.md) for:
- API reference
- Database schema
- Performance tuning
- Custom entity configuration
- Security settings

## Auto-Start (Optional)

Add to your `~/.zshrc` or `~/.bash_profile`:

```bash
# Start memory system on login
~/Documents/private/therapy.sh start > /dev/null 2>&1
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./therapy.sh start` | Start memory system |
| `./therapy.sh status` | Check if running |
| `./therapy.sh stop` | Stop memory system |
| `./therapy.sh restart` | Restart |

**In Claude:** "Search my memory for [topic]"

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more daily usage tips.

---

*Built for intelligent conversation continuity and contextual memory support.*
