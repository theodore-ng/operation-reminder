#!/usr/bin/env python3
"""
First-time OAuth setup — run this once to authenticate with Google.
After running, a token.json file will be saved and subsequent runs
of main.py will work without a browser.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from auth import get_credentials

if __name__ == "__main__":
    print("Opening browser for Google OAuth authorization...")
    print("Please log in and grant access to Gmail (read) and Google Calendar (create events).\n")
    try:
        creds = get_credentials()
        print("\nAuthorization successful!")
        print(f"Token saved to: {os.path.join(SCRIPT_DIR, 'token.json')}")
        print("\nYou can now run main.py to test the script.")
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
