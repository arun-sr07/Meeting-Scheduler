#!/usr/bin/env python3
"""
MCP Client Service for WhatsApp Integration
Handles MCP client logic for meeting scheduler functionality
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class WhatsAppMCPClient:
    """MCP Client service for WhatsApp integration"""
    
    def __init__(self):
        """Initialize the MCP client for WhatsApp"""
        self.agent = None
        self.agent_context = None
        self.initialized = False
        
        # Initialize Groq LLM
        self.llm = Groq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            request_timeout=120.0
        )
        Settings.llm = self.llm
        
        # System prompt for WhatsApp assistant
        self.system_prompt = """You are a helpful WhatsApp assistant that can check calendar availability, schedule meetings, send emails, and generate/send Minutes of Meeting (MoM).

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
    
    async def initialize_mcp_clients(self):
        """Initialize MCP clients and agent"""
        try:
            logger.info("Initializing MCP clients for WhatsApp...")
            
            # Connect to MCP servers
            gmail_client = BasicMCPClient("http://127.0.0.1:8051/sse")
            calendar_client = BasicMCPClient("http://127.0.0.1:8080/sse")
            mom_client = BasicMCPClient("http://127.0.0.1:8081/sse")
            
            mcp_tool = [
                McpToolSpec(client=gmail_client),
                McpToolSpec(client=calendar_client),
                McpToolSpec(client=mom_client)
            ]
            
            # Initialize agent
            self.agent = await self._get_agent(mcp_tool)
            self.agent_context = Context(self.agent)
            self.initialized = True
            
            logger.info("MCP clients initialized successfully for WhatsApp")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP clients for WhatsApp: {e}")
            self.initialized = False
            raise
    
    async def _get_agent(self, mcp_tool: list[McpToolSpec]) -> FunctionAgent:
        """Create and configure the function agent"""
        all_tools = []
        for spec in mcp_tool:
            tools = await spec.to_tool_list_async()
            all_tools.extend(tools)
        
        logger.info(f"Registered {len(all_tools)} tools for WhatsApp")
        
        agent = FunctionAgent(
            name="WhatsAppMeetingAgent",
            description="Agent that works with Calendar + Gmail MCP servers via WhatsApp.",
            tools=all_tools,
            llm=self.llm,
            system_prompt=self.system_prompt,
        )
        return agent
    
    async def handle_user_message(self, message_content: str) -> str:
        """Handle user message and return response"""
        try:
            if not self.initialized or not self.agent or not self.agent_context:
                return "❌ Meeting scheduler is not initialized. Please try again later."
            
            logger.info(f"Processing WhatsApp message: {message_content}")
            
            handler = self.agent.run(message_content, ctx=self.agent_context)
            tool_call_count = 0
            max_tool_calls = 5  # Prevent infinite loops
            
            async for event in handler.stream_events():
                if isinstance(event, ToolCall):
                    tool_call_count += 1
                    if tool_call_count > max_tool_calls:
                        logger.warning(f"Too many tool calls ({tool_call_count}), stopping to prevent loop")
                        break
                    logger.info(f"Calling tool {event.tool_name} with args {event.tool_kwargs}")
                elif isinstance(event, ToolCallResult):
                    logger.info(f"Tool {event.tool_name} completed")
            
            response = await handler
            logger.info(f"Generated response: {str(response)}")
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def is_initialized(self) -> bool:
        """Check if the MCP client is initialized"""
        return self.initialized

async def process_message_with_mcp(message: str) -> str:
    """Process a WhatsApp message using MCP client"""
    try:
        # Create a fresh MCP client instance for each request
        # This prevents event loop binding issues
        mcp_client = WhatsAppMCPClient()
        await mcp_client.initialize_mcp_clients()
        
        # Process the message
        response = await mcp_client.handle_user_message(message)
        return response
        
    except Exception as e:
        logger.error(f"Error processing message with MCP: {e}")
        return f"Sorry, I encountered an error processing your request: {str(e)}"

def get_help_message() -> str:
    """Get help message for WhatsApp users"""
    return """*Meeting Scheduler Bot*

I can help you with:
- *Check availability*
- *Schedule meetings*
- *Send emails*
- *Get schedule*
- *Generate MoM*

*Commands:*
- Type "help" for this message
- Type "status" to check if I'm working

Just send me a message and I'll help you!"""

def is_help_command(message: str) -> bool:
    """Check if the message is a help command"""
    help_commands = ["help", "hi", "hello", "start", "menu"]
    return message.lower().strip() in help_commands

def is_status_command(message: str) -> bool:
    """Check if the message is a status command"""
    return message.lower().strip() == "status"
