# MCP Calendar & Gmail Integration

This project provides a multi-agent MCP-based system to manage Google Calendar events and send email invites automatically. It uses **FastMCP** for server creation, **LlamaIndex FunctionAgent** for AI-based user interactions, and **Gmail API** for sending invites.

---

## Features

- **Calendar Management**  
  - Check availability for a specific date/time  
  - Get full schedule for a specific date  
  - Schedule a new meeting  

- **Email Integration**  
  - Automatically sends email invitations when a meeting is scheduled  
  - Supports custom recipients  

- **MCP Server/Client Architecture**  
  - Separate MCP servers for Calendar and Gmail  
  - Multi-agent setup with FunctionAgent for AI-driven interactions  

---

## Prerequisites

- Python 3.10+
- Google Calendar API credentials (`token_calendar.json`)
- Gmail API credentials (`token_gmail.json`)
- Install required Python packages:

```bash
pip install -r requirements.txt
