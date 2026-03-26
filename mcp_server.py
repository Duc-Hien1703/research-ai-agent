import asyncio
import os
import sys
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv()

try:
    import streamlit as st
    TAVILY_KEY = st.secrets.get("TAVILY_API_KEY") or os.getenv("TAVILY_API_KEY")
except:
    TAVILY_KEY = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key=TAVILY_KEY)

server = Server("research-assistant")


def log(msg: str):
    """Ghi log ra stderr thay vì stdout — tránh conflict với MCP JSON-RPC"""
    sys.stderr.write(f"[MCP Server] {msg}\n")
    sys.stderr.flush()


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_search",
            description="Search for information on the web. Use when you need to find recent information or research any topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query in English, concise and specific"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="read_url",
            description="Read detailed content from a specific webpage. Use after web_search to read sources in depth.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the webpage to read"
                    }
                },
                "required": ["url"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "web_search":
        query = arguments["query"]
        log(f"web_search: {query}")

        results = tavily.search(query, max_results=5)
        output = ""
        for i, r in enumerate(results["results"]):
            output += f"[{i+1}] {r['title']}\n"
            output += f"    URL: {r['url']}\n"
            output += f"    Summary: {r['content'][:200]}\n\n"

        return [types.TextContent(type="text", text=output)]

    elif name == "read_url":
        url = arguments["url"]
        log(f"read_url: {url}")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            clean_text = "\n".join(lines)[:3000]

            return [types.TextContent(type="text", text=clean_text)]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error reading URL: {str(e)}")]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())