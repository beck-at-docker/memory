#!/bin/bash
# Git commit script for memory system improvements

cd ~/Documents/private

echo "Preparing git commit for memory system improvements..."
echo ""

# Check git status
echo "Current git status:"
git status --short

echo ""
echo "Files to commit:"
echo "================"

# Add all the fixed files
git add -v \
  therapy.sh \
  therapy_wrapper.sh \
  start_interactive_memory.sh \
  setup_env.py \
  requirements_simple.txt \
  config.py \
  logging_config.py \
  insight_system_simple.py \
  claude_memory_client.py \
  memory_api.py \
  README.md \
  README2.md \
  QUICK_REFERENCE.md \
  test_mcp_server.py \
  test_memory_system.py \
  2>&1

echo ""
echo "Creating commit..."

git commit -m "feat: comprehensive memory system improvements and fixes

Major improvements to reliability, maintainability, and developer experience:

Process Management & Health Checks:
- Implemented PID file management in pids/ directory
- Added wait_for_health() with 30-second polling and HTTP verification
- Replaced fragile pkill -f patterns with safe PID-based process control
- Added graceful shutdown with SIGTERM → SIGKILL fallback
- PID files auto-cleanup on exit via signal handlers

Error Handling & Logging:
- Replaced bare except: with specific exception handling throughout
- Added MemoryClientError custom exception class
- Comprehensive logging with context in all error paths
- Color-coded console output (INFO/WARN/ERROR)
- Detailed error messages with troubleshooting hints
- Stack traces logged for unexpected errors

Shell Script Improvements:
- Added set -euo pipefail for strict error handling
- Implemented is_process_running() PID validation
- Added read_pid() for safe PID file reading
- Color-coded status reporting (green/yellow/red)
- Clear success/failure messages with actionable next steps

Configuration & Security:
- Added Config.BASE_DIR for dynamic path resolution
- Implemented PID file methods (get/write/read/remove)
- Added health check configuration (retries, interval)
- Improved token authentication error messages
- Better timeout configuration (connection vs read)

Type Safety:
- Added type hints to all function signatures
- Used Optional[] for nullable returns
- Proper return type annotations

Documentation:
- Updated README.md with correct paths and current setup
- Updated README2.md with technical details and new features
- Created QUICK_REFERENCE.md for daily usage
- Added inline documentation for all new functions
- Accurate troubleshooting instructions

Testing Infrastructure:
- Created test_memory_system.py for API validation
- Created test_mcp_server.py for MCP integration testing
- Both tests provide clear pass/fail output

Path Consolidation:
- Standardized all paths to /Users/beck/Documents/private/
- Removed /memory/ subdirectory references
- Dynamic SCRIPT_DIR usage in all shell scripts

Files Modified:
- config.py: PID management, BASE_DIR, better security
- therapy_wrapper.sh: Complete rewrite (1KB → 9KB)
- therapy.sh: Simplified wrapper with clear interface
- claude_memory_client.py: Better error handling
- memory_api.py: PID files, signal handlers
- insight_system_simple.py: Consistent error handling
- README.md: Updated for current structure
- README2.md: Added new features documentation

Files Added:
- QUICK_REFERENCE.md: Daily usage guide
- test_memory_system.py: API testing
- test_mcp_server.py: MCP testing

These changes transform the system from hope-driven to professional-grade
with proper monitoring, error handling, and process lifecycle management.
The system is now production-ready for personal use with clear debugging
paths when issues arise." || echo "Error creating commit"

echo ""
echo "Commit created! Review with:"
echo "  git log -1"
echo "  git show"
echo ""
echo "Push with:"
echo "  git push"
