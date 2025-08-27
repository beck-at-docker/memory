#!/usr/bin/env python3
"""
MCP Server for Memory System Integration with Claude
Provides memory tools that Claude can call automatically during conversations
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime
import uuid

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    EmptyResult,
    ListToolsResult,
    TextContent,
    Tool,
    INVALID_PARAMS,
    INTERNAL_ERROR
)

from claude_memory_client import MemoryClient, extract_insights_from_conversation, format_insights_for_claude

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory-mcp-server")

class MemoryMCPServer:
    def __init__(self):
        self.memory_client = MemoryClient()
        self.conversation_buffer = []
        self.server = Server("memory-system")
        
    def setup_tools(self):
        """Define tools that Claude can call"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available memory tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="query_memory",
                        description="Query personal memory system for relevant insights based on current conversation context. Use when discussing relationships, trust, boundaries, trauma, parenting, or when user seems to need grounding/anchoring.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The current conversation context or user input to find relevant insights for"
                                },
                                "max_results": {
                                    "type": "integer", 
                                    "description": "Maximum number of insights to retrieve (default: 3)",
                                    "default": 3
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="add_insight",
                        description="Add a new insight to the memory system when user expresses a breakthrough, effective strategy, or important realization.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The insight content to store"
                                },
                                "entities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "People or concepts this insight relates to"
                                },
                                "themes": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "Themes this insight relates to (trust, boundaries, trauma, etc.)"
                                },
                                "insight_type": {
                                    "type": "string",
                                    "enum": ["anchor", "breakthrough", "strategy", "observation"],
                                    "description": "Type of insight",
                                    "default": "observation"
                                },
                                "effectiveness_score": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                    "description": "How effective this insight/strategy is (0-1)",
                                    "default": 0.5
                                }
                            },
                            "required": ["content"]
                        }
                    ),
                    Tool(
                        name="detect_conversation_insights",
                        description="Analyze recent conversation for potential insights to capture. Use when user shares breakthroughs, effective strategies, or important realizations.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "conversation_text": {
                                    "type": "string",
                                    "description": "Recent conversation text to analyze for insights"
                                }
                            },
                            "required": ["conversation_text"]
                        }
                    ),
                    Tool(
                        name="get_memory_status",
                        description="Get current status of the memory system including total insights and active entities.",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls from Claude"""
            try:
                if name == "query_memory":
                    return await self._query_memory(arguments)
                elif name == "add_insight":
                    return await self._add_insight(arguments)
                elif name == "detect_conversation_insights":
                    return await self._detect_insights(arguments)
                elif name == "get_memory_status":
                    return await self._get_status(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

    async def _query_memory(self, arguments: dict) -> CallToolResult:
        """Query memory for relevant insights"""
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 3)
        
        if not query.strip():
            return CallToolResult(
                content=[TextContent(type="text", text="Query cannot be empty")],
                isError=True
            )
        
        # Check if memory server is running
        if not self.memory_client.is_server_running():
            return CallToolResult(
                content=[TextContent(type="text", text="Memory server is not running. Please start it with: ./start_server.sh")],
                isError=True
            )
        
        # Query the memory system
        result = self.memory_client.query_memory(query, max_results)
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Memory query failed: {result['error']}")],
                isError=True
            )
        
        insights = result.get("insights", [])
        triggers = result.get("triggers", [])
        
        if not insights:
            return CallToolResult(
                content=[TextContent(type="text", text="No relevant insights found for this context.")]
            )
        
        # Format insights for Claude
        formatted = format_insights_for_claude(insights)
        
        if triggers:
            formatted += f"\n\n*Triggered by: {', '.join(triggers)}*"
        
        return CallToolResult(
            content=[TextContent(type="text", text=formatted)]
        )

    async def _add_insight(self, arguments: dict) -> CallToolResult:
        """Add new insight to memory"""
        content = arguments.get("content", "").strip()
        entities = arguments.get("entities", [])
        themes = arguments.get("themes", [])
        insight_type = arguments.get("insight_type", "observation")
        effectiveness_score = arguments.get("effectiveness_score", 0.5)
        
        if not content:
            return CallToolResult(
                content=[TextContent(type="text", text="Insight content cannot be empty")],
                isError=True
            )
        
        # Check if memory server is running
        if not self.memory_client.is_server_running():
            return CallToolResult(
                content=[TextContent(type="text", text="Memory server is not running. Please start it with: ./start_server.sh")],
                isError=True
            )
        
        result = self.memory_client.add_insight(
            content=content,
            entities=entities,
            themes=themes,
            insight_type=insight_type,
            effectiveness_score=effectiveness_score
        )
        
        if "error" in result:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Failed to add insight: {result['error']}")],
                isError=True
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"✅ Successfully added {insight_type} insight to memory system")]
        )

    async def _detect_insights(self, arguments: dict) -> CallToolResult:
        """Detect insights from conversation text"""
        conversation_text = arguments.get("conversation_text", "").strip()
        
        if not conversation_text:
            return CallToolResult(
                content=[TextContent(type="text", text="Conversation text cannot be empty")],
                isError=True
            )
        
        # Extract potential insights
        insights = extract_insights_from_conversation(conversation_text)
        
        if not insights:
            return CallToolResult(
                content=[TextContent(type="text", text="No clear insights detected in the conversation text.")]
            )
        
        # Format the detected insights
        formatted_insights = []
        for i, insight in enumerate(insights):
            formatted_insights.append(
                f"{i+1}. **{insight['insight_type'].title()}**: {insight['content']}\n"
                f"   *Entities*: {', '.join(insight['entities']) if insight['entities'] else 'None'}\n"
                f"   *Themes*: {', '.join(insight['themes']) if insight['themes'] else 'None'}"
            )
        
        result = "**Detected Insights:**\n\n" + "\n\n".join(formatted_insights)
        result += "\n\n*Use the add_insight tool to save any of these to your memory system.*"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result)]
        )

    async def _get_status(self, arguments: dict) -> CallToolResult:
        """Get memory system status"""
        # Check if memory server is running
        if not self.memory_client.is_server_running():
            return CallToolResult(
                content=[TextContent(type="text", text="❌ Memory server is not running. Start it with: ./start_server.sh")]
            )
        
        status = self.memory_client.get_status()
        
        if "error" in status:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting status: {status['error']}")],
                isError=True
            )
        
        formatted_status = f"""✅ **Memory System Status**

📊 **Statistics:**
- Total insights: {status.get('total_insights', 0)}
- Active entities: {', '.join(status.get('entities', [])) if status.get('entities') else 'None'}
- Status: {status.get('status', 'Unknown')}
- Version: {status.get('version', 'Unknown')}

🔗 **Server:** Running on http://127.0.0.1:5000"""
        
        return CallToolResult(
            content=[TextContent(type="text", text=formatted_status)]
        )

    async def run(self):
        """Run the MCP server"""
        self.setup_tools()
        
        # Configure server options
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="memory-system",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = MemoryMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())