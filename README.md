# 🤖 AI-Powered Meeting Scheduler & MoM Generator

A comprehensive **Multi-Agent MCP-based system** that automates meeting scheduling, email management, and generates professional Minutes of Meeting (MoM) using AI. Built with **FastMCP**, **LlamaIndex**, and **Google APIs**.

## ✨ Features

### 📅 **Smart Calendar Management**
- **Availability Checking**: Check free slots for specific dates/times
- **Schedule Viewing**: Get complete daily schedules
- **Automated Scheduling**: AI-powered meeting scheduling with conflict detection
- **Google Calendar Integration**: Seamless sync with your Google Calendar

### 📧 **Intelligent Email System**
- **Automatic Invitations**: Send meeting invites when scheduling
- **Custom Recipients**: Support for multiple participants
- **Gmail API Integration**: Professional email management
- **Template Support**: Structured email formatting

### 📝 **AI-Powered MoM Generation**
- **Transcript to MoM**: Convert meeting transcripts to structured Minutes of Meeting
- **Smart Formatting**: Includes Agenda, Key Points, Decisions, and Action Items
- **Automated Distribution**: Send generated MoM to participants via email
- **Groq LLM Integration**: High-quality AI processing using Llama 3.1

### 🔧 **MCP Architecture**
- **Modular Design**: Separate servers for Calendar, Gmail, and MoM
- **Multi-Agent System**: LlamaIndex FunctionAgent for intelligent interactions
- **FastMCP Framework**: High-performance MCP server implementation
- **Extensible Tools**: Easy to add new functionality

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Google Calendar API** credentials
- **Gmail API** credentials  
- **Groq API Key** for MoM generation

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/arun-sr07/Meeting-Scheduler.git
cd Meeting-Scheduler
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

4. **Configure Google APIs**
```bash
# Run setup scripts
python setup_google_calendar.py
python setup_email.py
```

---

## 🛠️ Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Required Files
- `token_calendar.json` - Google Calendar API credentials
- `token_gmail.json` - Gmail API credentials
- `contacts.txt` - Contact information for participants
- `.env` - Environment variables (not tracked in git)

---

## 📖 Usage

### Starting the Servers

1. **Calendar Server**
```bash
python calendarServer.py
```

2. **Gmail Server**
```bash
python gmailServer.py
```

3. **MoM Server**
```bash
python momServer.py
```

4. **MCP Client**
```bash
python mcp_client.py
```

### API Endpoints

#### Calendar Operations
- `check_availability(date, time)` - Check free slots
- `get_schedule(date)` - Get daily schedule
- `schedule_meeting(title, date, time, duration, attendees)` - Schedule meeting

#### Email Operations
- `send_email(to, subject, body)` - Send email
- `send_meeting_invite(attendees, meeting_details)` - Send meeting invitation

#### MoM Operations
- `generate_mom(transcript)` - Generate MoM from transcript
- `send_mom(names, transcript)` - Generate and send MoM via email

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Calendar       │    │  Gmail          │    │  MoM            │
│  Server         │    │  Server         │    │  Server         │
│  (MCP)         │    │  (MCP)          │    │  (MCP)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  MCP Client     │
                    │  (Multi-Agent)  │
                    └─────────────────┘
```

---

## 📦 Dependencies

### Core MCP Framework
- `mcp>=1.0.0` - MCP protocol implementation
- `fastmcp>=1.0.0` - High-performance MCP server

### Google APIs
- `google-api-python-client` - Google Calendar & Gmail APIs
- `google-auth-httplib2` - Authentication
- `google-auth-oauthlib` - OAuth2 support

### AI & LLM
- `llama-index-core` - LlamaIndex framework
- `llama-index-llms-groq` - Groq LLM integration
- `llama-index-tools-mcp` - MCP tool integration

### Utilities
- `python-dotenv` - Environment variable management
- `dateparser` - Date parsing utilities
- `nest_asyncio` - Async support

---

## 🔐 Security

- **API Keys**: Stored in environment variables, never hardcoded
- **OAuth2**: Secure Google API authentication
- **Git Protection**: GitHub secret scanning enabled
- **Credentials**: Sensitive files excluded from version control

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/arun-sr07/Meeting-Scheduler/issues)
- **Documentation**: Check the code comments and docstrings
- **API Keys**: Ensure all required API keys are properly configured

---

## 🔄 Changelog

### Latest Updates
- ✨ Added AI-powered MoM generation
- 🔧 Enhanced MCP server architecture
- 📧 Improved email automation
- 🎯 Better error handling and logging
- 📚 Comprehensive documentation

---

**Built with ❤️ using FastMCP, LlamaIndex, and Google APIs**
