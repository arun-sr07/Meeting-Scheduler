#!/usr/bin/env python3
"""
Gmail Setup Helper
Run this script to set up Gmail API access for sending emails
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Only Gmail send permission
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_gmail():
    """Set up Gmail API access"""
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\n📋 To set up Gmail access:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable the Gmail API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download the credentials.json file")
        print("6. Place it in this directory")
        return False
    
    print("🔧 Setting up Gmail API access...")
    
    creds = None
    
    # Check if we already have a token
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8888)
        
        # Save the credentials for the next run
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Gmail API access set up successfully!")
    print("🎉 You can now run your email MCP server")
    return True

if __name__ == "__main__":
    setup_gmail()
