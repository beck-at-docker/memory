# Claude Memory System Integration

This project includes a personal memory system that can be integrated with Claude conversations.

## Quick Start

### Option A: Full Interactive Integration with Claude

1. **Setup (first time only):**
   ```bash
   python3 setup_env.py
   python3 setup_claude_integration.py
   ```

2. **Start interactive memory system:**
   ```bash
   ./start_interactive_memory.sh
   ```

3. **Configure Claude Code** (follow instructions from setup script):
   - Enable MCP server: `memory-system`
   - Add hooks configuration for automatic monitoring

### Option B: Basic Memory Server Only

1. **Setup (first time only):**
   ```bash
   python3 setup_env.py
   ```

2. **Start the memory server:**
   ```bash
   ./start_server.sh
   ```

3. **Test manually:**
   ```bash
   source memory_env/bin/activate
   python3 claude_memory_client.py
   ```

## How It Works

The memory system provides contextual insights based on conversation content. It tracks:

- **Entities**: A, N, X, trauma_responses
- **Themes**: trust, boundaries, trauma, parenting, strategies, growth
- **Insight Types**: anchor (bedrock truths), breakthrough, strategy, observation

## API Endpoints

- `POST /query` - Get relevant insights for input text
- `POST /add` - Add new insight
- `GET /status` - System status
- `GET /entities` - Entity statistics

## Interactive Claude Integration

With the full integration setup, Claude automatically:

### 🔍 **Auto-Insight Retrieval**
- Detects when you mention relationships, trust, boundaries, trauma, parenting
- Automatically surfaces relevant insights without you asking
- Provides anchoring during crisis or difficult moments

### 🧠 **MCP Tools Available to Claude**
- `query_memory` - Search for relevant insights
- `add_insight` - Capture new breakthroughs or strategies  
- `detect_conversation_insights` - Analyze conversations for patterns
- `get_memory_status` - Check system status

### 📝 **Conversation Monitoring**
- Watches for breakthrough language ("I realized that...")
- Suggests capturing effective strategies
- Detects crisis language and offers anchoring
- Learns from your conversations automatically

## Example Usage

```python
from claude_memory_client import MemoryClient

client = MemoryClient()
result = client.query_memory("I'm worried about trusting A")
# Returns relevant insights about trust and A
```

## Files

- `memory_api.py` - HTTP API server
- `claude_memory_client.py` - Client library and conversation parser
- `insight_system_simple.py` - Core memory system (no ML dependencies)
- `interactive_demo.py` - Standalone interactive demo

## Data Storage

Personal insights are stored separately in `~/Documents/private/memory_data/personal_insights.db` - this is NOT part of the repository and remains private.

## Repository Location

This code is maintained in `/Users/beck/Documents/private/memory/` - keeping the memory system close to your personal data while maintaining privacy.

## Commands

- Test: `python3 claude_memory_client.py`
- Start API: `python3 memory_api.py`
- Interactive Demo: `python3 interactive_demo.py` (run outside Claude Code)