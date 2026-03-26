from mcp_client import run_mcp_tool, get_tool_schemas

print("=== Test get schemas ===")
schemas = get_tool_schemas()
for s in schemas:
    print(f"Tool: {s['function']['name']}")

print("\n=== Test web_search ===")
result = run_mcp_tool("web_search", {"query": "MCP Model Context Protocol"})
print(result[:300])

print("\n=== Test read_url ===")
result = run_mcp_tool("read_url", {"url": "https://www.bbc.com"})
print(result[:300])

print("\n=== Test read_url ===")
result = run_mcp_tool("read_url", {"url": "https://vnexpress.net"})
print(result[:300])