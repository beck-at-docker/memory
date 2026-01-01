# Memory System - Quick Reference

## Daily Usage

### Start/Stop Commands

```bash
cd ~/Documents/private

# Start the system
./therapy.sh start

# Check if running
./therapy.sh status

# Stop the system
./therapy.sh stop

# Restart
./therapy.sh restart
```

### What You'll See

**When Running:**
```
✅ Memory API: Running and healthy
   PID: 12345
   URL: http://localhost:8001
```

**When Stopped:**
```
❌ Memory API: Not running
   Run './therapy.sh start' to start it
```

## Using with Claude

Once configured in Claude Code, Claude will automatically:
- **Surface relevant memories** when you mention topics, people, or themes
- **Detect breakthrough moments** and offer to save them
- **Provide context** from past conversations

### Manual Memory Commands

You can also explicitly ask Claude to:

```
"Search my memory for insights about [topic]"
"What do I have in memory about [person/project]?"
"Can you save this insight to my memory?"
"Show me my memory system status"
```

## Files & Locations

- **Database**: `~/Documents/private/memory_data/personal_insights.db`
- **Logs**: `~/Documents/private/logs/memory_api.log`
- **PID**: `~/Documents/private/pids/memory_api.pid`

## View Logs

```bash
# Watch logs in real-time
tail -f ~/Documents/private/logs/memory_api.log

# View recent errors
tail -50 ~/Documents/private/logs/memory_api.log | grep ERROR
```

## Troubleshooting

**Problem: Memory system won't start**
```bash
# Check what's wrong
./therapy.sh status

# View the logs
cat logs/memory_api.log

# Try restarting
./therapy.sh restart
```

**Problem: Port 8001 already in use**
```bash
# Find what's using it
lsof -i :8001

# Kill the old process
./therapy.sh stop

# Start fresh
./therapy.sh start
```

**Problem: Dependencies missing**
```bash
# Reinstall dependencies
source memory_env/bin/activate
pip install -r requirements_simple.txt
./therapy.sh restart
```

## When to Restart

Restart the system if:
- You update any Python files
- The system becomes unresponsive
- You see errors in the logs
- After a system reboot

## Testing

```bash
# Quick test
python3 test_memory_system.py

# Full client test
python3 claude_memory_client.py
```

## Configuration

The system is configured in `config.py`:
- API port: 8001
- Database location: `~/Documents/private/memory_data/`
- Allowed directories: Set in `ALLOWED_PROJECT_DIRS`

## Auto-Start (Optional)

To start automatically on login, add to your `~/.bash_profile` or `~/.zshrc`:

```bash
# Start memory system on login
~/Documents/private/therapy.sh start > /dev/null 2>&1
```

## Help

- **Full documentation**: `README.md`
- **Setup guide**: `CONFIGURE_CLAUDE_CODE.md`
- **Fix details**: `SYSTEM_FIXED.md`
- **This guide**: `QUICK_REFERENCE.md`

## Summary

**Start it:**  `./therapy.sh start`
**Check it:**  `./therapy.sh status`
**Use it:**    Ask Claude to access memory
**Stop it:**   `./therapy.sh stop`

That's all you need to know for daily use!
