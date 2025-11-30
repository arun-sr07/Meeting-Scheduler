#!/usr/bin/env python3
"""
Startup script for Meeting-Scheduler with Telegram Bot
Runs all MCP servers and the Telegram bot
"""
import asyncio
import subprocess
import time
import os
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
def start_mcp_server(script_name: str, port: int):
    """Start an MCP server in the background"""
    try:
        process = subprocess.Popen([
            sys.executable, script_name, "--server_type", "sse"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f" Started {script_name} on port {port}")
        return process
    except Exception as e:
        print(f"Failed to start {script_name}: {e}")
        return None

def start_telegram_bot():
    """Start the Telegram bot"""
    try:
        process = subprocess.Popen([
            sys.executable, "telegram_bot.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(" Started Telegram bot")
        return process
    except Exception as e:
        print(f" Failed to start Telegram bot: {e}")
        return None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n Shutting down servers...")
    for process in processes:
        if process:
            process.terminate()
    sys.exit(0)

def main():
    """Main function to start all services"""
    print(" Starting Meeting-Scheduler with Telegram Bot...")
    
    
    required_vars = ["TELEGRAM_API_KEY", "GROQ_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f" Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return
    
   
    signal.signal(signal.SIGINT, signal_handler)
    
    global processes
    processes = []
    
   
    print("\n Starting MCP servers...")
    processes.append(start_mcp_server("calendarServer.py", 8080))
    processes.append(start_mcp_server("gmailServer.py", 8000))
    processes.append(start_mcp_server("momServer.py", 8081))
    
    
    print("\n Waiting for servers to initialize...")
    time.sleep(3)
    
    
    print("\n Starting Telegram bot...")
    processes.append(start_telegram_bot())
    
    print("\n All services started!")
    print(" Your Telegram bot is now running")
    print(" Press Ctrl+C to stop all services")
    
    try:
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
