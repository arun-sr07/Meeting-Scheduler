#!/usr/bin/env python3
"""
Gmail MCP Server (real MCP compliant)
Exposes: send_email
"""
import os
import argparse
import json
from typing import Dict
from fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ---- Contact Resolver ----
def load_contacts(file_path: str = "contacts.txt") -> Dict[str, str]:
    contacts = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                if "=" in line:
                    name, email = line.strip().split("=", 1)
                    contacts[name.lower().strip()] = email.strip()
    return contacts

def resolve_emails(names: list, contacts_file="contacts.txt") -> list:
    contacts = load_contacts(contacts_file)
    resolved = []
    for n in names:
        key = n.lower().strip()
        if key in contacts:
            resolved.append(contacts[key])
        else:
            resolved.append(n)  # assume it's already an email
    return resolved

class GmailMCPServer:
    def __init__(self):
        self.creds = Credentials.from_authorized_user_file("token_gmail.json", SCOPES)
        self.service = build("gmail", "v1", credentials=self.creds)

    def send_email(self, to: list, subject: str, body: str) -> Dict[str, str]:
        try:
            print(body)
            recipients=resolve_emails(to)
            message = MIMEText(body)
            message["to"] = ",".join(recipients)
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            sent = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )
            return {"success": True, "message": f"Email sent to {recipients}", "id": sent["id"]}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

# ---- MCP Server ----
gmail_server = GmailMCPServer()
server = FastMCP("GmailMCP")

@server.tool()
def send_email(to: list, subject: str, body: str) -> str:
    """Send an email with subject and body to recipient.
    
    Args:
        to: List of email addresses or names to send to
        subject: Email subject
        body: Email body content
    """
    return json.dumps(gmail_server.send_email(to, subject, body), indent=2)

if __name__ == "__main__":
    print("🚀 Starting Gmail MCP server...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    server.run(args.server_type)
