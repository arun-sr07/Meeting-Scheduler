#!/usr/bin/env python3
"""
Gmail MCP Server (real MCP compliant)
Exposes: send_email
"""

import argparse
import json
from typing import Dict
from fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

class GmailMCPServer:
    def __init__(self):
        self.creds = Credentials.from_authorized_user_file("token_gmail.json", SCOPES)
        self.service = build("gmail", "v1", credentials=self.creds)

    def send_email(self, to: str, subject: str, body: str) -> Dict[str, str]:
        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            sent = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )
            return {"success": True, "message": f"Email sent to {to}", "id": sent["id"]}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

# ---- MCP Server ----
gmail_server = GmailMCPServer()
server = FastMCP("GmailMCP")

@server.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email with subject and body to recipient."""
    return json.dumps(gmail_server.send_email(to, subject, body), indent=2)

if __name__ == "__main__":
    print("🚀 Starting Gmail MCP server...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    server.run(args.server_type)
