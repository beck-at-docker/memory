# Claude Memory System

A contextual insight retrieval system that integrates with Claude conversations to provide intelligent memory and conversation continuity.

## What This Does

- Automatically surfaces relevant insights when you mention specific people, topics, or themes
- Provides crisis support by detecting distress language and offering grounding insights  
- Maintains conversation continuity without overwhelming detail
- Tracks growth and focuses on transformation rather than static facts
- Integrates seamlessly with Claude Code

## Quick Start

### 1. Setup

```bash
git clone https://github.com/beck-at-docker/memory.git
cd memory
python3 setup_env.py
python3 setup_claude_integration.py
```

### 2. Start the System

```bash
# Start the memory system
./therapy.sh start

# Or use the individual script
./start_interactive_memory.sh
```

### 3. Configure Claude Code

#### Edit Claude Code Configuration File

Add the following sections to your Claude Code configuration file:

**Config file locations:**
- **macOS**: `~/.config/claude-code/settings.json`
- **Linux**: `~/.config/claude-code/settings.json`
- **Windows**: `%APPDATA%/claude-code/settings.json`

**Add MCP Server:**
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

**Add Hooks (Optional but Recommended):**
```json
{
  "hooks": {
    "user-prompt-submit": "python3 /path/to/memory/claude_hooks/user_prompt_submit.py \"$PROMPT\"",
    "post-response": "python3 /path/to/memory/claude_hooks/post_response.py"
  }
}
```

**Complete Example Configuration:**
```json
{
  "mcpServers": {
    "memory-system": {
      "command": "python3", 
      "args": ["/Users/yourname/memory/memory_mcp_server_simple.py"],
      "env": {
        "PYTHONPATH": "/Users/yourname/memory",
        "PATH": "/Users/yourname/memory/memory_env/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  },
  "hooks": {
    "user-prompt-submit": "python3 /Users/yourname/memory/claude_hooks/user_prompt_submit.py \"$PROMPT\"",
    "post-response": "python3 /Users/yourname/memory/claude_hooks/post_response.py"
  }
}
```

**Important:** Replace `/path/to/memory` or `/Users/yourname/memory` with your actual installation path.

#### Restart and Verify

1. Save the configuration file
2. Restart Claude Code
3. Test by asking Claude: "Can you check my memory system status?"

## How to Use

### Managing the System

The `therapy.sh` script provides unified control over the memory system:

```bash
# Start the memory system
./therapy.sh start

# Check if components are running
./therapy.sh status

# Stop all memory system processes
./therapy.sh stop
```

**Alternative**: You can also use the individual script:
```bash
./start_interactive_memory.sh
```

**Important**: The system doesn't start automatically. Run the start command each time you want to use memory features.

### Using with Claude

Once running, the memory system works automatically in Claude conversations.

#### Automatic Insight Retrieval

The system surfaces relevant insights when you mention:

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

**Crisis Language:**
```
You: "I'm overwhelmed and don't know how to handle this situation"
Claude: [Immediately provides coping strategies and grounding insights]
```

#### What You'll See

When memory triggers activate, Claude naturally integrates insights:

```
You: "I'm having doubts about whether I can trust someone new in my life"

Claude: I understand that uncertainty can be challenging. Based on your previous insights, there are some important anchors to remember:

- Trust builds through consistent actions over time
- Past experiences can create doubt even in potentially healthy relationships
- Processing concerns with support helps navigate trust-building without self-sabotage

These insights from your experience suggest that the doubts might be more about protective patterns than about the person's actual trustworthiness. What specifically is triggering these concerns?
```

### Using Memory Tools

Claude can access memory tools when you ask:

**Search Memory:**
```
You: "Can you search my memory for insights about communication strategies?"
Claude: [Uses query_memory tool to search and return relevant insights]
```

**Save Insights:**
```
You: "I just realized something important - can you save this breakthrough to my memory?"
Claude: [Uses add_insight tool to capture the new understanding]
```

**Check Statistics:**
```
You: "How many insights do I have stored about relationships?"
Claude: [Uses get_memory_status tool to provide statistics]
```

### Conversation Monitoring

With hooks enabled, the system automatically watches for:

**Breakthrough Language:**
```
You: "That just clicked - I realized that negative self-talk isn't actually truth"
Claude: "That sounds like an important breakthrough! Would you like me to save this realization to your memory system for future reference?"
```

**Strategy Success:**
```
You: "That communication technique really worked in my meeting today"
Claude: "I'm glad that approach was effective! Let me capture this successful strategy in your memory."
```

**Crisis Detection:**
```
You: "I'm feeling completely overwhelmed and don't know what to do"
Claude: [Immediately surfaces coping strategies without being asked]
- "You have navigated difficult situations before and can do so again"
- "Overwhelming thoughts are temporary - they will pass"
- "Support systems are available when you need them"
```

## Example Conversation

```
You: "I'm having trouble with communication in my team meetings. The usual approaches aren't working."

Claude: I can see this is an ongoing challenge. From your previous insights:

**Current Strategies:**
- Clear expectations reduce confusion and conflict
- Active listening builds trust even during disagreements
- Regular check-ins prevent small issues from becoming big problems

**What's different this time?** The fact that usual approaches aren't working might mean the team dynamic is shifting. Would you like me to help brainstorm modifications to your existing strategies, or search for any insights you might have about handling resistance to established communication patterns?

You: "That's helpful. Can you check if I have any insights about what to do when established approaches stop working?"

Claude: [Uses query_memory tool] I found a few relevant insights:

- "When old strategies stop working, it's often a sign of growth, not failure"
- "Sometimes resistance means people are ready for more collaborative decision-making"
- "Taking a step back and involving the team in problem-solving can rebuild cooperation"

Would you like to try involving your team in redesigning the meeting structure?
```

## Repository Structure

### Core System Files
- **`insight_system_simple.py`** - Main contextual insight retrieval system with SQLite database
- **`memory_api.py`** - Flask-based REST API server for memory operations  
- **`memory_mcp_server_simple.py`** - MCP server for Claude Code integration
- **`claude_memory_client.py`** - Client for interacting with the memory API

### Setup & Management Scripts
- **`setup_claude_integration.py`** - Automated setup for Claude Code integration
- **`setup_env.py`** - Environment configuration
- **`therapy.sh`** - System management (start/stop/status)
- **`start_interactive_memory.sh`** - Interactive memory session launcher
- **`start_mcp_server.sh`** - MCP server startup script

### Hook System
- **`claude_hooks.py`** - Hook management system
- **`claude_hooks/user_prompt_submit.py`** - Pre-prompt processing hook  
- **`claude_hooks/post_response.py`** - Post-response processing hook

### Testing & Configuration
- **`test_system.py`** - System functionality tests
- **`test_access_restriction.py`** - Access control testing
- **`extract_conversation_insights.py`** - Conversation analysis tool
- **`config.py`** - Configuration management
- **`logging_config.py`** - Logging setup
- **`.env.example`** - Environment variable template
- **`requirements_simple.txt`** - Python dependencies

## Data Storage

Personal insights are stored in:
```
~/Documents/private/memory_data/personal_insights.db
```

This file is private and not part of the repository.

## Testing

Run the test suite to verify everything works:

```bash
source memory_env/bin/activate
python3 test_system.py
```

## Troubleshooting

### Memory Server Won't Start

```bash
# Check system status
./therapy.sh status

# Stop all processes and restart
./therapy.sh stop
./therapy.sh start

# Manual troubleshooting
lsof -i :8001  # Check if port 8001 is in use
pkill -f memory_api.py  # Kill existing process
```

### MCP Server Not Connecting

1. Check Claude Code MCP configuration
2. Verify Python path in MCP server settings
3. Ensure virtual environment is activated

### Hooks Not Working

1. Check hook scripts are executable:
   ```bash
   ls -la claude_hooks/
   chmod +x claude_hooks/*.py
   ```

2. Verify Claude Code hooks configuration

## Manual Usage (Without Claude Integration)

If you prefer to use the API directly:

```bash
# Start the memory system
./therapy.sh start

# Or start manually
./start_interactive_memory.sh

# Use the client
source memory_env/bin/activate
python3 claude_memory_client.py
```

## Technical Documentation

For detailed configuration options, API reference, database schema, and advanced usage, see [README2.md](README2.md).

---

*Built for intelligent conversation continuity and contextual memory support.*