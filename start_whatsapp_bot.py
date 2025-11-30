#!/usr/bin/env python3
"""
Startup script for Meeting-Scheduler with WhatsApp Bot
Runs all MCP servers and the Flask WhatsApp app
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
        print(f"✅ Started {script_name} on port {port}")
        return process
    except Exception as e:
        print(f"❌ Failed to start {script_name}: {e}")
        return None

def start_flask_app():
    """Start the Flask WhatsApp app"""
    try:
        process = subprocess.Popen([
            sys.executable, "run.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Started Flask WhatsApp app")
        return process
    except Exception as e:
        print(f"❌ Failed to start Flask app: {e}")
        return None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down servers...")
    for process in processes:
        if process:
            process.terminate()
    sys.exit(0)

def main():
    """Main function to start all services"""
    print("🚀 Starting Meeting-Scheduler with WhatsApp Bot...")
    
    # Check if required environment variables are set
    required_vars = ["GROQ_API_KEY", "ACCESS_TOKEN", "VERIFY_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        return
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    global processes
    processes = []
    
    # Start MCP servers
    print("\n📡 Starting MCP servers...")
    processes.append(start_mcp_server("calendarServer.py", 8080))
    processes.append(start_mcp_server("gmailServer.py", 8051))
    processes.append(start_mcp_server("momServer.py", 8081))
    
    # Wait a moment for servers to start
    print("\n⏳ Waiting for servers to initialize...")
    time.sleep(3)
    
    # Start Flask WhatsApp app
    print("\n📱 Starting Flask WhatsApp app...")
    processes.append(start_flask_app())
    
    print("\n✅ All services started!")
    print("📱 Your WhatsApp bot is now running on http://localhost:8000")
    print("🔗 Webhook URL: http://your-domain.com/webhook")
    print("🛑 Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
