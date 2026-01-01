#!/usr/bin/env python3
"""
Simple MCP Server for Memory System - Fixed Implementation
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional

# Configure logging to stderr so we can see what's happening
logging.basicConfig(level=logging.INFO, stream=sys.stderr, 
                    format='%(asctime)s [MCP] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from claude_memory_client import MemoryClient

class SimpleMemoryMCPServer:
    def __init__(self):
        self.memory_client = MemoryClient()
        
    async def handle_message(self, message: dict) -> dict:
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            params = message.get("params", {})
            msg_id = message.get("id")
            # Ensure msg_id is never null for responses
            if msg_id is None:
                msg_id = 0
            
            logger.info(f"Received method: {method}")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "memory-system",
                            "version": "1.0.0"
                        }
                    }
                }
                
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "get_memory_status",
                                "description": "Get current status of the memory system",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            {
                                "name": "query_memory",
                                "description": "Query memory for relevant insights",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "The query to search for"
                                        }
                                    },
                                    "required": ["query"]
                                }
                            }
                        ]
                    }
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_memory_status":
                    return await self.get_memory_status(msg_id)
                elif tool_name == "query_memory":
                    return await self.query_memory(msg_id, arguments)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                    
            elif method == "prompts/list":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "prompts": []
                    }
                }
                
            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "resources": []
                    }
                }
                    
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def get_memory_status(self, msg_id):
        """Get memory system status"""
        try:
            if self.memory_client.is_server_running():
                status = self.memory_client.get_status()
                result_text = f"✅ Memory system is running\nPort: 8001\nStatus: {status.get('status', 'unknown')}"
            else:
                result_text = "❌ Memory server is not running. Start with: ./start_server.sh"
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0", 
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error checking status: {e}"
                        }
                    ]
                }
            }
    
    async def query_memory(self, msg_id, arguments):
        """Query memory system"""
        try:
            query = arguments.get("query", "")
            if not query:
                result_text = "No query provided"
            else:
                result = self.memory_client.query_memory(query)
                if "error" in result:
                    result_text = f"Query failed: {result['error']}"
                else:
                    insights = result.get("insights", [])
                    if insights:
                        result_text = "**Found insights:**\n" + "\n".join([f"• {insight['content']}" for insight in insights])
                    else:
                        result_text = "No relevant insights found"
            
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text", 
                            "text": result_text
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error querying memory: {e}"
                        }
                    ]
                }
            }

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting simple MCP server...")
        
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                logger.info(f"Received: {line}")
                message = json.loads(line)
                
                response = await self.handle_message(message)
                response_json = json.dumps(response)
                
                logger.info(f"Sending: {response_json}")
                print(response_json, flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                continue
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                continue

async def main():
    server = SimpleMemoryMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())