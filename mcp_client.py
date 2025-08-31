#!/usr/bin/env python3
"""
Groq MCP Calendar Client
Uses LlamaIndex FunctionAgent + MCP tools
"""

import asyncio
import nest_asyncio
nest_asyncio.apply()
import os
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context


llm = Groq(model="llama-3.1-8b-instant",api_key=os.getenv("GROQ_API_KEY"), request_timeout=120.0)
Settings.llm = llm

SYSTEM_PROMPT = """\You are a helpful assistant that can check calendar availability,
schedule meetings, send meeting links by email, and generate/send Minutes of Meeting (MoM).
You must use tools (via MCP) when users ask about schedules, meetings, availability, invites, or MoM.
You may only call these tools: check_availability, get_schedule, schedule_meeting, send_email, generate_mom, send_mom.
Do not invent new tools.

IMPORTANT WORKFLOW RULES:
- When generating and sending Minutes of Meeting (MoM), use the send_mom tool which handles the complete workflow
- The send_mom tool will: 1) Generate the MoM, 2) Send it via email
- This ensures the proper sequence and prevents sending emails before content is generated
- For other email needs, use send_email directly

"""

async def get_agent(mcp_tool: list[McpToolSpec]) -> FunctionAgent:
    all_tools = []
    for spec in mcp_tool:
        tools = await spec.to_tool_list_async()
        all_tools.extend(tools)

    print("🔧 Registered Tools:")
    for t in all_tools:
        print(f"- {t.metadata.name}")

    agent = FunctionAgent(
        name="MeetingAgent",
        description="Agent that works with Calendar + Gmail MCP servers.",
        tools=all_tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and isinstance(event, ToolCall):
            print(f"🔧 Calling tool {event.tool_name} with args {event.tool_kwargs}")
        elif verbose and isinstance(event, ToolCallResult):
            print(f"✅ Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

async def main():
    # Connect to MCP server (your calendar_server should expose this SSE endpoint)
    gmail_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    calendar_client = BasicMCPClient("http://127.0.0.1:8080/sse")
    mom_client=BasicMCPClient("http://127.0.0.1:8081/sse")
    mcp_tool = [
        McpToolSpec(client=gmail_client),
        McpToolSpec(client=calendar_client),
        McpToolSpec(client=mom_client)
    ]

    # Init agent
    agent = await get_agent(mcp_tool)
    agent_context = Context(agent)

    print("\n🤖 Calendar Agent Ready (Groq)! Type 'exit' to quit.\n")

    while True:
        user_input = input("❓ You: ")
        if user_input.strip().lower() == "exit":
            break
        response = await handle_user_message(user_input, agent, agent_context, verbose=True)
        print("🤖 Agent:", response, "\n")

if __name__ == "__main__":
    asyncio.run(main())
