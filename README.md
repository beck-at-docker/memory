# Claude Memory System

A contextual insight retrieval system that integrates with Claude conversations to provide intelligent memory and conversation continuity. Instead of information dumps, it surfaces relevant insights based on conversation topics and provides crisis anchoring when needed.

## 🎯 What This Does

- **Contextual Memory**: Automatically surfaces relevant insights when you mention specific people, topics, or themes
- **Crisis Support**: Detects crisis language and immediately provides grounding insights
- **Conversation Continuity**: Maintains context across conversations without overwhelming detail
- **Growth Tracking**: Focuses on transformation and progress rather than static facts
- **Seamless Integration**: Works automatically with Claude Code through MCP and hooks

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/beck-at-docker/memory.git
cd memory
python3 setup_env.py
```

### 2. Choose Your Integration Level

#### Option A: Full Claude Code Integration (Recommended)

Complete integration with automatic insight retrieval and conversation monitoring:

```bash
python3 setup_claude_integration.py
./start_interactive_memory.sh
```

Then follow the setup script instructions to configure Claude Code.

#### Option B: Manual API Usage

Just the memory system without Claude integration:

```bash
./start_interactive_memory.sh
```

Test manually:
```bash
source memory_env/bin/activate
python3 claude_memory_client.py
```

## 📋 Detailed Setup Guide

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

After running the setup script, you need to configure Claude Code:

#### Enable MCP Server

Add this to your Claude Code settings (`~/.config/claude-code/settings.json`):

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

#### Enable Hooks (Optional but Recommended)

Add automatic conversation monitoring:

```json
{
  "hooks": {
    "user-prompt-submit": "python3 /path/to/memory/claude_hooks/user_prompt_submit.py \"$PROMPT\"",
    "post-response": "python3 /path/to/memory/claude_hooks/post_response.py"
  }
}
```

### Step 4: Start the System

```bash
./start_interactive_memory.sh
```

This starts:
- Memory API server on port 5001
- Background process for Claude integration

## 💬 Using the Memory System with Claude

### Automatic Insight Retrieval

Once the memory system is **running** (after starting `./start_interactive_memory.sh`), it works automatically in your Claude conversations. No special commands needed in your conversations - just start the system first!

> **⚠️ Remember**: You must run `./start_interactive_memory.sh` each time you want to use the memory system. It doesn't start automatically with your computer.

#### Triggering Memory Retrieval

The system automatically surfaces relevant insights when you mention:

**People/Entities:**
```
You: "I'm worried about trusting my partner"
Claude: [Automatically retrieves insights about trust and relationships]
```

**Themes:**
```
You: "Having boundary issues with my child again"
Claude: [Surfaces boundary strategies and parenting insights]
```

**Crisis Language:**
```
You: "I'm falling apart and can't handle this"
Claude: [Immediately provides crisis anchors and grounding insights]
```

#### What You'll See

When memory triggers activate, Claude will naturally integrate insights into the conversation:

```
You: "I'm second-guessing whether my partner is trustworthy"

Claude: I understand that uncertainty can be challenging. Based on your previous insights, there are some important anchors to remember:

• Trust builds through consistent actions over time
• Past relationship patterns can create doubt even in healthy relationships
• Taking concerns to therapy helps process relationship fears without damaging the partnership

These insights from your experience suggest that the second-guessing might be more about processing old patterns than about your partner's actual trustworthiness. What specifically is triggering these doubts today?
```

### Using MCP Tools Directly

Claude also has access to memory tools you can request explicitly:

#### Query Memory
```
You: "Can you search my memory for insights about parenting strategies?"
Claude: [Uses query_memory tool to search and return relevant insights]
```

#### Add New Insights
```
You: "I just realized something important - can you save this breakthrough to my memory?"
Claude: [Uses add_insight tool to capture the new understanding]
```

#### Check Memory Status
```
You: "How many insights do I have stored about trust?"
Claude: [Uses get_memory_status tool to provide statistics]
```

### Conversation Monitoring (With Hooks Enabled)

The system automatically watches for:

#### Breakthrough Language
```
You: "That just clicked - I realized that critical voice isn't actually truth"
Claude: "That sounds like an important breakthrough! Would you like me to save this realization to your memory system for future reference?"
```

#### Strategy Effectiveness
```
You: "That boundary technique really worked with my child"
Claude: "I'm glad that approach was effective! Let me capture this successful strategy in your memory."
```

#### Crisis Detection
```
You: "I'm in complete panic and everything feels overwhelming"
Claude: [Immediately surfaces crisis anchors without being asked]
- "You have survived difficult moments before and can do so again"
- "Critical thoughts are not facts - they are old patterns that can change"
- "Professional support is available and effective"
```

### Memory Integration Modes

#### Surface Mode (Default)
- Shows 3-5 most relevant insights
- Recent breakthroughs and high-effectiveness strategies
- Crisis anchors when needed

#### Deeper Context (On Request)
```
You: "Can you give me more context about my trust journey?"
Claude: [Provides mid-layer insights with supporting background]
```

#### Historical Patterns (On Request)
```
You: "Show me the full history of my insights about trauma responses"
Claude: [Provides deep-layer comprehensive view]
```

### Example Conversation Flow

```
You: "I'm having trouble with my child about bedtime routines again. The usual approaches aren't working."

Claude: I can see this is an ongoing challenge. From your previous insights:

**Current Strategies:**
• Boundaries are love, not punishment - hold the line with compassion
• Structure provides security even when there's initial resistance  
• Consistent routines work better than power struggles

**What's different this time?** The fact that usual approaches aren't working might mean your child is going through a developmental shift. Would you like me to help brainstorm modifications to your existing strategies, or search for any insights you might have about handling resistance to established routines?

You: "That's helpful. Can you check if I have any insights about what to do when established routines stop working?"

Claude: [Uses query_memory tool] I found a few relevant insights:

• "When old strategies stop working, it's often a sign of growth, not failure"
• "Sometimes resistance means the child is ready for more autonomy in the routine"
• "Taking a step back and involving children in problem-solving can rebuild cooperation"

Would you like to try involving your child in redesigning the bedtime routine?
```

## 🔧 Configuration Options

### Memory System Configuration

Edit `insight_system_simple.py` to customize:

#### Entity Triggers
```python
triggers = {
    "partner": SemanticTrigger(
        entity="partner",
        keywords={"trust", "relationship", "communication", "support"},
        max_surface_insights=3
    ),
    "child": SemanticTrigger(
        entity="child", 
        keywords={"boundaries", "parenting", "school", "routines"},
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

#### Crisis Detection
```python
crisis_keywords = [
    "crisis", "emergency", "panic", "overwhelmed",
    "falling apart", "can't handle", "too much"
]
```

### Claude Code Project Configuration

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

### Environment Variables

Set these in your shell environment:

```bash
export MEMORY_DB_PATH="$HOME/Documents/private/memory_data/personal_insights.db"
export MEMORY_API_PORT=5001
export MEMORY_LOG_LEVEL=INFO
```

## 🧠 How It Works

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

1. **Input**: User mentions entity (e.g., "I'm worried about trusting A")
2. **Trigger Detection**: System identifies "A" and "trust" keywords
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

## 🔌 API Reference

### HTTP Endpoints

#### `POST /query`
Query for relevant insights.

```bash
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "worried about trusting A"}'
```

Response:
```json
{
  "surface": [...],
  "mid": [...], 
  "deep": [...],
  "total_insights": 15
}
```

#### `POST /add`
Add new insight.

```bash
curl -X POST http://localhost:5001/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "A is trustworthy. His word is enough.",
    "entities": ["A"],
    "themes": ["trust"],
    "insight_type": "anchor",
    "effectiveness_score": 1.0
  }'
```

#### `GET /status`
System status and statistics.

```bash
curl http://localhost:5001/status
```

#### `GET /entities`
Entity statistics and counts.

```bash
curl http://localhost:5001/entities
```

### MCP Tools (Available to Claude)

#### `query_memory`
Search for relevant insights based on input text.

#### `add_insight` 
Capture new insights from conversations.

#### `get_memory_status`
Check system status and statistics.

#### `detect_conversation_insights`
Analyze conversation text for potential insights.

## 💾 Data Storage

### Database Location
Personal insights are stored in:
```
~/Documents/private/memory_data/personal_insights.db
```

This file is **NOT** part of the repository and remains private.

### Database Schema

```sql
CREATE TABLE insights (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    entities TEXT,  -- JSON array
    themes TEXT,    -- JSON array
    timestamp TEXT,
    effectiveness_score REAL,
    growth_stage TEXT,
    layer TEXT,
    insight_type TEXT,
    supersedes TEXT,
    superseded_by TEXT,
    source_file TEXT,
    context TEXT
);
```

### Backup and Migration

```bash
# Backup insights database
cp ~/Documents/private/memory_data/personal_insights.db ~/backup/

# Export insights to JSON
source memory_env/bin/activate
python3 -c "
from claude_memory_client import MemoryClient
client = MemoryClient()
client.export_insights('backup.json')
"
```

## 🧪 Testing

### Run Test Suite

```bash
source memory_env/bin/activate
python3 test_system.py
```

Tests include:
- Import verification
- Basic functionality
- Memory client communication
- Crisis detection
- End-to-end flow

### Manual Testing

```bash
# Test memory client
source memory_env/bin/activate
python3 claude_memory_client.py

# Test API endpoints
curl http://localhost:5001/status
curl -X POST http://localhost:5001/query -d '{"query": "test"}'
```

## 🚨 Troubleshooting

### Common Issues

#### Memory Server Won't Start
```bash
# Check if port 5001 is in use
lsof -i :5001

# Kill existing process
pkill -f memory_api.py

# Restart
./start_interactive_memory.sh
```

#### MCP Server Not Connecting
1. Check Claude Code MCP configuration
2. Verify Python path in MCP server args
3. Check virtual environment activation:
   ```bash
   which python3  # Should show memory_env/bin/python3
   ```

#### Hooks Not Working
1. Verify hook scripts are executable:
   ```bash
   ls -la claude_hooks/
   chmod +x claude_hooks/*.py
   ```

2. Check Claude Code hooks configuration
3. Test hooks manually:
   ```bash
   python3 claude_hooks/user_prompt_submit.py "test prompt"
   ```

#### Database Issues
```bash
# Check database file exists and is writable
ls -la ~/Documents/private/memory_data/

# Recreate database
rm ~/Documents/private/memory_data/personal_insights.db
python3 -c "
from insight_system_simple import SimpleContextualInsightRetrieval
system = SimpleContextualInsightRetrieval()
print('Database recreated')
"
```

### Debug Mode

Enable detailed logging:

```bash
export MEMORY_LOG_LEVEL=DEBUG
./start_interactive_memory.sh
```

Check logs:
```bash
tail -f ~/Documents/private/memory_data/memory_system.log
```

### Performance Tuning

For large insight databases:

```python
# In insight_system_simple.py
class SimpleContextualInsightRetrieval:
    def __init__(self, db_path="insights.db"):
        self.max_search_results = 100  # Reduce for faster queries
        self.cache_size = 50          # Increase for better performance
```

## 🔄 Updates and Maintenance

### Updating the System

```bash
git pull origin main
source memory_env/bin/activate
pip install -r requirements_simple.txt --upgrade
```

### Adding New Entities

Edit `insight_system_simple.py`:

```python
def _initialize_triggers(self):
    return {
        "NewEntity": SemanticTrigger(
            entity="NewEntity",
            keywords={"keyword1", "keyword2"},
            max_surface_insights=3
        )
    }
```

### Customizing Insight Classification

Edit insight type patterns in `insight_system_simple.py`:

```python
def _classify_insight_type(self, content: str) -> str:
    # Add your custom patterns
    if re.search(r'new_pattern', content, re.IGNORECASE):
        return "custom_type"
```

## 🤝 Contributing

This is a personal memory system, but if you find bugs or have suggestions:

1. Open an issue on GitHub
2. Describe the problem or enhancement
3. Include logs and system information

## 📄 License

Private repository - for personal use only.

## 📞 Support

For issues:
1. Check troubleshooting section
2. Run test suite to identify problems
3. Check logs for error messages
4. Open GitHub issue with details

---

*Built for intelligent conversation continuity and contextual memory support.*