#!/bin/bash
# Wrapper script to start MCP server with proper virtual environment

cd /Users/beck/Documents/private/memory
source memory_env/bin/activate
python3 memory_mcp_server_simple.py "$@"