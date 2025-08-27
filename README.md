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
./start_interactive_memory.sh
```

### 3. Configure Claude Code

Follow the instructions from the setup script to:
- Enable MCP server: `memory-system`
- Add hooks configuration for automatic monitoring

## How to Use

### Starting the System

You must start the memory system before each use:

```bash
./start_interactive_memory.sh
```

**Important**: The system doesn't start automatically. Run this script each time you want to use memory features.

### Using with Claude

Once running, the memory system works automatically in Claude conversations.

#### Automatic Insight Retrieval

The system surfaces relevant insights when you mention:

**People or Relationships:**
```
You: "I'm worried about trusting my partner"
Claude: [Automatically retrieves insights about trust and relationships]
```

**Themes or Topics:**
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

When memory triggers activate, Claude naturally integrates insights:

```
You: "I'm second-guessing whether my partner is trustworthy"

Claude: I understand that uncertainty can be challenging. Based on your previous insights, there are some important anchors to remember:

- Trust builds through consistent actions over time
- Past relationship patterns can create doubt even in healthy relationships
- Taking concerns to therapy helps process relationship fears without damaging the partnership

These insights from your experience suggest that the second-guessing might be more about processing old patterns than about your partner's actual trustworthiness. What specifically is triggering these doubts today?
```

### Using Memory Tools

Claude can access memory tools when you ask:

**Search Memory:**
```
You: "Can you search my memory for insights about parenting strategies?"
Claude: [Uses query_memory tool to search and return relevant insights]
```

**Save Insights:**
```
You: "I just realized something important - can you save this breakthrough to my memory?"
Claude: [Uses add_insight tool to capture the new understanding]
```

**Check Statistics:**
```
You: "How many insights do I have stored about trust?"
Claude: [Uses get_memory_status tool to provide statistics]
```

### Conversation Monitoring

With hooks enabled, the system automatically watches for:

**Breakthrough Language:**
```
You: "That just clicked - I realized that critical voice isn't actually truth"
Claude: "That sounds like an important breakthrough! Would you like me to save this realization to your memory system for future reference?"
```

**Strategy Success:**
```
You: "That boundary technique really worked with my child"
Claude: "I'm glad that approach was effective! Let me capture this successful strategy in your memory."
```

**Crisis Detection:**
```
You: "I'm in complete panic and everything feels overwhelming"
Claude: [Immediately surfaces crisis anchors without being asked]
- "You have survived difficult moments before and can do so again"
- "Critical thoughts are not facts - they are old patterns that can change"
- "Professional support is available and effective"
```

## Example Conversation

```
You: "I'm having trouble with my child about bedtime routines again. The usual approaches aren't working."

Claude: I can see this is an ongoing challenge. From your previous insights:

**Current Strategies:**
- Boundaries are love, not punishment - hold the line with compassion
- Structure provides security even when there's initial resistance  
- Consistent routines work better than power struggles

**What's different this time?** The fact that usual approaches aren't working might mean your child is going through a developmental shift. Would you like me to help brainstorm modifications to your existing strategies, or search for any insights you might have about handling resistance to established routines?

You: "That's helpful. Can you check if I have any insights about what to do when established routines stop working?"

Claude: [Uses query_memory tool] I found a few relevant insights:

- "When old strategies stop working, it's often a sign of growth, not failure"
- "Sometimes resistance means the child is ready for more autonomy in the routine"
- "Taking a step back and involving children in problem-solving can rebuild cooperation"

Would you like to try involving your child in redesigning the bedtime routine?
```

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
# Check if port 5001 is in use
lsof -i :5001

# Kill existing process  
pkill -f memory_api.py

# Restart
./start_interactive_memory.sh
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
./start_interactive_memory.sh
source memory_env/bin/activate
python3 claude_memory_client.py
```

## Technical Documentation

For detailed configuration options, API reference, database schema, and advanced usage, see [README2.md](README2.md).

---

*Built for intelligent conversation continuity and contextual memory support.*