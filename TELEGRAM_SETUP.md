# Meeting-Scheduler with Telegram Bot

A comprehensive meeting scheduler assistant that can be accessed via Telegram bot, supporting calendar management, email sending, and meeting scheduling.

## Features

- **Calendar Management**: Check availability, schedule meetings, get schedules
- **Email Integration**: Send emails to contacts from contacts.txt
- **Meeting Scheduling**: Schedule meetings for today, tomorrow, or specific dates
- **Minutes of Meeting**: Generate and send MoM from transcripts
- **Telegram Bot Interface**: Natural language interaction via Telegram

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Telegram Bot API Key (get from @BotFather on Telegram)
TELEGRAM_API_KEY=your_telegram_bot_token_here

# Groq API Key (get from https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Telegram Bot Setup

1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token and add it to `.env` as `TELEGRAM_API_KEY`
4. Start a chat with your bot on Telegram

### 3. Google Calendar & Gmail Setup

Run the setup scripts to configure Google Calendar and Gmail APIs:

```bash
python setup_google_calendar.py
python setup_email.py
```

### 4. Contacts Setup

Edit `contacts.txt` to add your contacts:

```
Arun=arunsrinivasan003@gmail.com
Arvind=arunsrinvasan003@gmail.com
Srinivasan=srinivasanuma107@gmail.com
```

## Running the Application

### Option 1: Start Everything at Once

```bash
python start_telegram_bot.py
```

This will start:
- Calendar MCP server (port 8080)
- Gmail MCP server (port 8000)  
- MoM MCP server (port 8081)
- Telegram bot

### Option 2: Start Services Manually

1. Start MCP servers:
```bash
python calendarServer.py --server_type sse
python gmailServer.py --server_type sse  
python momServer.py --server_type sse
```

2. Start Telegram bot:
```bash
python telegram_bot.py
```

## Usage Examples

Send these messages to your Telegram bot:

### Availability & Scheduling
- "is arun free on 2025-10-25 at 10:00"
- "schedule meeting today at 2:00 PM"
- "schedule meeting tomorrow"
- "what's my schedule on 2025-10-25"

### Email & Communication
- "send email to arun"
- "generate mom from transcript"

### Commands
- `/start` - Welcome message
- `/help` - Show available commands

## Architecture

```
Telegram Bot (telegram_bot.py)
    ↓
MCP Client (mcp_client.py logic)
    ↓
MCP Servers:
    ├── Calendar Server (calendarServer.py)
    ├── Gmail Server (gmailServer.py)
    └── MoM Server (momServer.py)
```

## Error Handling

The bot includes comprehensive error handling:
- Invalid commands are handled gracefully
- Unknown contacts show available contacts
- MCP server connection issues are reported
- Tool call loops are prevented

## Dependencies

All dependencies are listed in `requirements.txt`:
- python-telegram-bot
- llama-index-llms-groq
- fastmcp
- google-api-python-client
- And more...

Install with:
```bash
pip install -r requirements.txt
```
