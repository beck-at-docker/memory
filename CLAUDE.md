# Claude Memory System Integration

This project includes a personal memory system that can be integrated with Claude conversations.

## Quick Start

1. **Start the memory server:**
   ```bash
   python3 memory_api.py
   ```
   The server runs on `http://127.0.0.1:5000`

2. **Test the connection:**
   ```bash
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

## For Claude Integration

When discussing topics related to A, N, X, trust, boundaries, trauma, or parenting, Claude can:

1. Query the memory system for relevant insights
2. Surface anchoring truths during difficult conversations
3. Automatically capture new insights from conversations

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

## Commands

- Test: `python3 claude_memory_client.py`
- Start API: `python3 memory_api.py`
- Interactive Demo: `python3 interactive_demo.py` (run outside Claude Code)