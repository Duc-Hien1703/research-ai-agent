import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()


async def get_mcp_tools():
    """Lấy danh sách tools từ MCP Server"""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=dict(os.environ)
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools.tools


async def call_mcp_tool(tool_name: str, tool_input: dict) -> str:
    """Gọi một tool cụ thể qua MCP Server"""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=dict(os.environ)
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_input)

            # Lấy text từ result
            if result.content:
                return result.content[0].text
            return "No result"


def run_mcp_tool(tool_name: str, tool_input: dict) -> str:
    """Wrapper sync cho async MCP call — dùng trong agent.py"""
    return asyncio.run(call_mcp_tool(tool_name, tool_input))


def get_tool_schemas() -> list:
    """Convert MCP tools sang format Groq hiểu được"""
    tools = asyncio.run(get_mcp_tools())

    schemas = []
    for tool in tools:
        schemas.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })
    return schemas