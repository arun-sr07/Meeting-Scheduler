# utils/call_mcp_tool.py

async def call_mcp_tool(client, tool_name: str, args: dict):
    """
    Generic helper to call an MCP tool by name with arguments.
    """
    try:
        result = await client.call_tool(tool_name, args)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error calling tool {tool_name}: {str(e)}"
        }
