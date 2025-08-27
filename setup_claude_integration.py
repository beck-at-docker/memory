#!/usr/bin/env python3
"""
Setup script for Claude Code integration with memory system
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def setup_mcp_server():
    """Setup MCP server configuration for Claude"""
    
    # Install MCP dependencies
    print("📦 Installing MCP dependencies...")
    try:
        subprocess.run([
            "memory_env/bin/pip", "install", "mcp", "asyncio"
        ], check=True, capture_output=True)
        print("✅ MCP dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install MCP dependencies: {e}")
        return False
    
    # Create MCP configuration
    config_dir = Path.home() / ".config" / "claude-code"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    mcp_config = {
        "mcpServers": {
            "memory-system": {
                "command": "python3",
                "args": [str(Path.cwd() / "memory_mcp_server.py")],
                "env": {
                    "PYTHONPATH": str(Path.cwd()),
                    "PATH": f"{Path.cwd() / 'memory_env' / 'bin'}:{os.environ.get('PATH', '')}"
                }
            }
        }
    }
    
    config_file = config_dir / "mcp_servers.json"
    with open(config_file, "w") as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✅ MCP server configuration created at {config_file}")
    return True

def setup_claude_hooks():
    """Setup Claude Code hooks for automatic memory integration"""
    
    # Create hooks directory
    hooks_dir = Path.cwd() / "claude_hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Create submit hook script
    submit_hook = hooks_dir / "user_prompt_submit.py"
    with open(submit_hook, "w") as f:
        f.write(f"""#!/usr/bin/env python3
import sys
sys.path.append('{Path.cwd()}')
from claude_hooks import user_prompt_submit_hook
user_prompt_submit_hook()
""")
    
    os.chmod(submit_hook, 0o755)
    
    # Create response hook script
    response_hook = hooks_dir / "post_response.py"
    with open(response_hook, "w") as f:
        f.write(f"""#!/usr/bin/env python3
import sys
sys.path.append('{Path.cwd()}')
from claude_hooks import post_response_hook
post_response_hook()
""")
    
    os.chmod(response_hook, 0o755)
    
    print("✅ Claude Code hooks created")
    
    # Instructions for user
    print("""
📋 To enable Claude Code hooks, add these to your Claude settings:

1. Open Claude Code settings
2. Add hooks configuration:

{
  "hooks": {
    "user-prompt-submit": "python3 """ + str(submit_hook) + """ '$PROMPT'",
    "post-response": "python3 """ + str(response_hook) + """"
  }
}
""")
    
    return True

def setup_interactive_memory():
    """Setup the complete interactive memory system"""
    
    print("🧠 Setting up Claude Interactive Memory System...")
    print("=" * 60)
    
    # Check if virtual environment exists
    if not (Path.cwd() / "memory_env").exists():
        print("❌ Virtual environment not found. Please run: python3 setup_env.py")
        return False
    
    # Setup MCP server
    if not setup_mcp_server():
        return False
    
    # Setup hooks
    if not setup_claude_hooks():
        return False
    
    # Create startup script for both servers
    startup_script = Path.cwd() / "start_interactive_memory.sh"
    with open(startup_script, "w") as f:
        f.write("""#!/bin/bash
echo "🧠 Starting Interactive Memory System..."
echo "Starting memory API server..."

# Start memory API in background
source memory_env/bin/activate
python3 memory_api.py &
API_PID=$!

echo "✅ Memory API started (PID: $API_PID)"
echo "🔗 Memory system ready for Claude integration"
echo "📋 Configure Claude Code with MCP server and hooks as shown above"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo 'Stopping servers...'; kill $API_PID 2>/dev/null; exit" SIGINT SIGTERM

wait
""")
    
    os.chmod(startup_script, 0o755)
    
    print("✅ Interactive memory system setup complete!")
    print(f"""
🎉 Setup Complete! Here's what you can do now:

1. **Start the interactive memory system:**
   ./start_interactive_memory.sh

2. **Configure Claude Code:**
   - Enable MCP server: memory-system
   - Add hooks configuration (see above)

3. **Features now available:**
   ✅ Automatic insight retrieval during conversations
   ✅ MCP tools Claude can call: query_memory, add_insight, etc.
   ✅ Background monitoring for insight capture suggestions
   ✅ Crisis mode detection and anchoring

4. **Usage:**
   - Mention relationships, trust, boundaries → auto-surfaces insights
   - Express breakthroughs → suggests capturing to memory
   - Claude can call memory tools directly during conversation

Your memory system will now integrate seamlessly with Claude conversations!
""")
    
    return True

if __name__ == "__main__":
    setup_interactive_memory()