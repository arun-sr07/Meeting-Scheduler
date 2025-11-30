# Meeting-Scheduler with WhatsApp Bot

A comprehensive meeting scheduler assistant that can be accessed via WhatsApp, supporting calendar management, email sending, and meeting scheduling.

## Features

- **Calendar Management**: Check availability, schedule meetings, get schedules
- **Email Integration**: Send emails to contacts from contacts.txt
- **Meeting Scheduling**: Schedule meetings for today, tomorrow, or specific dates
- **Minutes of Meeting**: Generate and send MoM from transcripts
- **WhatsApp Bot Interface**: Natural language interaction via WhatsApp

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Groq API Key (get from https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here

# WhatsApp API Configuration (get from Meta for Developers)
ACCESS_TOKEN=your_whatsapp_access_token
APP_ID=your_app_id
APP_SECRET=your_app_secret
RECIPIENT_WAID=+1234567890  # Your WhatsApp number with country code
VERSION=v22.0
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_verify_token
```

### 2. WhatsApp Business API Setup

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app and add WhatsApp Business API
3. Get your access token, app ID, app secret, and phone number ID
4. Set up a webhook URL pointing to your server: `https://your-domain.com/webhook`
5. Use your chosen verify token for webhook verification

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

### Option 1: Start Everything at Once (Recommended)

```bash
python start_whatsapp_bot.py
```

This will start:
- Calendar MCP server (port 8080)
- Gmail MCP server (port 8000)  
- MoM MCP server (port 8081)
- Flask WhatsApp app (port 8000)

### Option 2: Start Services Manually

1. Start MCP servers:
```bash
python calendarServer.py --server_type sse
python gmailServer.py --server_type sse  
python momServer.py --server_type sse
```

2. Start Flask WhatsApp app:
```bash
python run.py
```

## Usage Examples

Send these messages to your WhatsApp bot:

### Availability & Scheduling
- "is arun free on 2025-10-25 at 10:00"
- "schedule meeting today at 2:00 PM"
- "schedule meeting tomorrow"
- "what's my schedule on 2025-10-25"

### Email & Communication
- "send email to arun"
- "generate mom from transcript"

### Commands
- "help" - Show available commands
- "status" - Check if bot is working

## Architecture

```
WhatsApp Users
    ↓
WhatsApp Business API
    ↓
Flask App (run.py)
    ↓
WhatsApp Utils (whatsapp_utils.py)
    ↓
MCP Client Service (mcp_client_service.py)
    ↓
MCP Servers:
    ├── Calendar Server (calendarServer.py)
    ├── Gmail Server (gmailServer.py)
    └── MoM Server (momServer.py)
```

## Webhook Configuration

### Local Development
For local testing, use ngrok to expose your local server:

```bash
# Install ngrok
# Download from https://ngrok.com/

# Expose your local server
ngrok http 8000

# Use the ngrok URL as your webhook URL
# Example: https://abc123.ngrok.io/webhook
```

### Production Deployment
Deploy your Flask app to a cloud service (Heroku, AWS, etc.) and use the production URL as your webhook endpoint.

## Error Handling

The bot includes comprehensive error handling:
- Invalid commands are handled gracefully
- Unknown contacts show available contacts
- MCP server connection issues are reported
- Tool call loops are prevented
- All errors are logged for debugging

## Dependencies

All dependencies are listed in `requirements.txt`:
- flask
- requests
- aiohttp
- llama-index-llms-groq
- fastmcp
- google-api-python-client
- And more...

Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **MCP Servers Not Starting**: Ensure all MCP servers are running before starting the Flask app
2. **Webhook Verification Failed**: Check your VERIFY_TOKEN matches the one in Meta settings
3. **Access Token Expired**: WhatsApp access tokens expire after 24 hours, get a new one
4. **Message Not Received**: Check webhook URL is accessible and correctly configured

### Logs

Check the console output for detailed logs:
- MCP server connections
- WhatsApp message processing
- Tool calls and responses
- Error messages

## Security Notes

- Keep your access tokens secure
- Use HTTPS for webhook URLs in production
- Implement proper authentication for production use
- Monitor webhook traffic for suspicious activity
