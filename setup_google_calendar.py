#!/usr/bin/env python3
"""
Google Calendar Setup Helper
Run this script to set up Google Calendar API access
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar']

def setup_google_calendar():
    """Set up Google Calendar API access"""
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\n📋 To set up Google Calendar access:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable the Google Calendar API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download the credentials.json file")
        print("6. Place it in this directory")
        return False
    
    print("🔧 Setting up Google Calendar access...")
    
    creds = None
    
    # Check if we already have a token
    if os.path.exists('token_calendar.json'):
        creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080,access_type='offline',prompt='consent')
        
        # Save the credentials for the next run
        with open('token_calendar.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Google Calendar access set up successfully!")
    print("🎉 You can now run the calendar agent with: python client.py")
    return True

if __name__ == "__main__":
    setup_google_calendar()
    