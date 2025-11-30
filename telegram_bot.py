#!/usr/bin/env python3
"""
Telegram Bot Integration for Meeting-Scheduler
Handles Telegram messages and integrates with MCP client
"""
import asyncio
import os
import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramMeetingScheduler:
    """Telegram bot integration for Meeting-Scheduler"""
    
    def __init__(self):
        """Initialize the Telegram bot with MCP client integration"""
        self.telegram_token = os.getenv("TELEGRAM_API_KEY")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_API_KEY environment variable is required")
        
        # Initialize Groq LLM
        self.llm = Groq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            request_timeout=120.0
        )
        Settings.llm = self.llm
        
        # Initialize MCP clients
        self.mcp_clients = None
        self.agent = None
        self.agent_context = None
        
        # System prompt for the assistant
        self.system_prompt = """You are a helpful assistant that can check calendar availability, schedule meetings, send emails, and generate/send Minutes of Meeting (MoM).

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
            logger.info("Initializing MCP clients...")
            
            # Connect to MCP servers
            gmail_client = BasicMCPClient("http://127.0.0.1:8000/sse")
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
            
            logger.info("MCP clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP clients: {e}")
            raise
    
    async def _get_agent(self, mcp_tool: list[McpToolSpec]) -> FunctionAgent:
        """Create and configure the function agent"""
        all_tools = []
        for spec in mcp_tool:
            tools = await spec.to_tool_list_async()
            all_tools.extend(tools)
        
        logger.info(f"Registered {len(all_tools)} tools")
        
        agent = FunctionAgent(
            name="TelegramMeetingAgent",
            description="Agent that works with Calendar + Gmail MCP servers via Telegram.",
            tools=all_tools,
            llm=self.llm,
            system_prompt=self.system_prompt,
        )
        return agent
    
    async def handle_user_message(self, message_content: str) -> str:
        """Handle user message and return response"""
        try:
            if not self.agent or not self.agent_context:
                return "❌ Meeting scheduler is not initialized. Please try again later."
            
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
            return str(response)
            
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
**Meeting Scheduler Bot**

I can help you with:
• Check availability"
• Schedule meetings
• Send emails
• Get schedule
• Generate MoM

Just send me a message and I'll help you!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📋 **Available Commands:**

**Availability & Scheduling:**
• "is [person] free on [date] at [time]"
• "schedule meeting today"
• "schedule meeting tomorrow"
• "what's my schedule on [date]"

**Email & Communication:**
• "send email to [person]"
• "generate mom from [transcript]"

**Examples:**
• "is arun free on 2025-10-25 at 10:00"
• "schedule meeting today at 2:00 PM"
• "send email to arun"
• "what's my schedule on 2025-10-25"

Type any of these commands and I'll help you!
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        try:
            user_message = update.message.text
            user_id = update.message.from_user.id
            username = update.message.from_user.username or "Unknown"
            
            logger.info(f"Received message from {username} ({user_id}): {user_message}")
            
            # Show typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Process the message
            response = await self.handle_user_message(user_message)
            
            # Send response back to user
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("❌ Sorry, I encountered an error processing your message.")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors gracefully"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Sorry, something went wrong. Please try again later."
            )
    
    async def run_bot_async(self):
        """Run the Telegram bot asynchronously"""
        try:
            # Create application
            application = Application.builder().token(self.telegram_token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            application.add_error_handler(self.error_handler)
            
            logger.info("Starting Telegram bot...")
            
            # Initialize the application
            await application.initialize()
            await application.start()
            
            # Start polling
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            
            logger.info("Telegram bot is running! Press Ctrl+C to stop.")
            
            # Keep the bot running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping Telegram bot...")
            finally:
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
            
        except Exception as e:
            logger.error(f"Failed to run Telegram bot: {e}")
            raise

async def main():
    """Main function to run the Telegram bot"""
    try:
        # Create bot instance
        bot = TelegramMeetingScheduler()
        
        # Initialize MCP clients
        await bot.initialize_mcp_clients()
        
        # Run the bot asynchronously
        await bot.run_bot_async()
        
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
