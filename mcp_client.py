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
from dotenv import load_dotenv
load_dotenv()


llm = Groq(model="llama-3.1-8b-instant",api_key=os.getenv("GROQ_API_KEY"), request_timeout=120.0)
Settings.llm = llm

SYSTEM_PROMPT = """You are a helpful assistant that can check calendar availability, schedule meetings, send emails, and generate/send Minutes of Meeting (MoM).

CRITICAL RULE: ONLY PERFORM THE EXACT ACTION REQUESTED BY THE USER. DO NOT ADD EXTRA ACTIONS.

Available tools: check_availability, get_schedule, schedule_meeting, schedule_meeting_today, schedule_meeting_tomorrow, send_email, send_email_to_person, generate_mom, send_mom

STRICT USAGE RULES - CALL EACH TOOL ONLY ONCE PER USER REQUEST:
- If user asks "is [person] free on [date] at [time]", call check_availability ONCE
- If user asks "what's my schedule on [date]", call get_schedule ONCE
- If user asks "schedule meeting", call schedule_meeting ONCE
- If user asks "schedule meeting today", call schedule_meeting_today ONCE
- If user asks "schedule meeting tomorrow", call schedule_meeting_tomorrow ONCE
- If user asks "send email to [person]", call send_email_to_person ONCE
- If user asks "generate mom", call generate_mom or send_mom ONCE

DO NOT:
- Call the same tool multiple times for the same request
- Automatically schedule meetings when checking availability
- Send emails when checking availability
- Add extra actions not explicitly requested
- Loop or repeat tool calls

FUNCTION CALLING RULES:
- For check_availability: Use date in YYYY-MM-DD format, time in HH:MM format
- For send_email: Use to parameter as list format ["email@example.com"]
- For send_email_to_person: Use name parameter (will look up email from contacts.txt)
- For schedule_meeting: Use date in YYYY-MM-DD format, times in HH:MM format
- For schedule_meeting_today/tomorrow: Use times in HH:MM format (date is automatic)

EXAMPLES:
- "is arun free on 2025-10-25 at 10:00" → Call check_availability ONCE with date="2025-10-25", time="10:00"
- "send email to arun" → Call send_email_to_person ONCE with name="arun"
- "schedule meeting today" → Call schedule_meeting_today ONCE with start_time and end_time

IMPORTANT: After calling a tool once, provide the result to the user. Do not call the same tool again.

"""

async def get_agent(mcp_tool: list[McpToolSpec]) -> FunctionAgent:
    all_tools = []
    for spec in mcp_tool:
        tools = await spec.to_tool_list_async()
        all_tools.extend(tools)

    print("Registered Tools:")
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
    try:
        # Add timeout to prevent infinite loops
        handler = agent.run(message_content, ctx=agent_context)
        tool_call_count = 0
        max_tool_calls = 5  # Prevent infinite loops
        
        async for event in handler.stream_events():
            if verbose and isinstance(event, ToolCall):
                tool_call_count += 1
                if tool_call_count > max_tool_calls:
                    print(f"[WARNING] Too many tool calls ({tool_call_count}), stopping to prevent loop")
                    break
                print(f"[TOOL] Calling tool {event.tool_name} with args {event.tool_kwargs}")
            elif verbose and isinstance(event, ToolCallResult):
                print(f"[RESULT] Tool {event.tool_name} returned {event.tool_output}")

        response = await handler
        return str(response)
    except Exception as e:
        print(f"[ERROR] Error handling user message: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I encountered an error: {str(e)}"

async def main():
    try:
        # Connect to MCP server (your calendar_server should expose this SSE endpoint)
        print("Connecting to MCP servers...")
        gmail_client = BasicMCPClient("http://127.0.0.1:8051/sse")
        calendar_client = BasicMCPClient("http://127.0.0.1:8080/sse")
        mom_client = BasicMCPClient("http://127.0.0.1:8081/sse")
        
        mcp_tool = [
            McpToolSpec(client=gmail_client),
            McpToolSpec(client=calendar_client),
            McpToolSpec(client=mom_client)
        ]

        # Init agent
        print("Initializing agent...")
        agent = await get_agent(mcp_tool)
        agent_context = Context(agent)

        print("\nCalendar Agent Ready (Groq)! Type 'exit' to quit.\n")

        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == "exit":
                break
            response = await handle_user_message(user_input, agent, agent_context, verbose=True)
            print("Agent:", response, "\n")
    except Exception as e:
        print(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
