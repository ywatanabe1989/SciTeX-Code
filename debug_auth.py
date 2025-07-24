#!/usr/bin/env python3
"""Debug authentication status."""

import asyncio
import logging
import json
from pathlib import Path
from scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator

logging.basicConfig(level=logging.DEBUG)

async def check_auth():
    # Check if session file exists
    cache_dir = Path.home() / ".scitex" / "scholar" / "openathens_sessions"
    print(f"\nChecking cache directory: {cache_dir}")
    
    if cache_dir.exists():
        print("Session files:")
        for f in cache_dir.glob("*.enc"):
            print(f"  - {f.name}")
        for f in cache_dir.glob("*.json"):
            print(f"  - {f.name}")
            # Check if we can read the JSON file
            try:
                with open(f, 'r') as jf:
                    data = json.load(jf)
                    print(f"    Email in file: {data.get('email', 'N/A')}")
                    print(f"    Cookies: {len(data.get('cookies', {}))} items")
                    print(f"    Expiry: {data.get('expiry', 'N/A')}")
            except Exception as e:
                print(f"    Error reading file: {e}")
    
    # Create authenticator (same as PDFDownloader does)
    # Use the email that was used for authentication
    auth = OpenAthensAuthenticator(
        email="yusuke.watanabe@unimelb.edu.au",  # Use the email that matches the session file
        debug_mode=True
    )
    
    # Load session
    print("\nLoading session...")
    await auth._load_session_cache_async()
    
    # Check authentication status
    is_auth = await auth.is_authenticated_async()
    print(f"\nAuthenticated: {is_auth}")
    
    if hasattr(auth, '_cookies'):
        print(f"Cookies loaded: {len(auth._cookies) if auth._cookies else 0}")
    
    if hasattr(auth, '_session_expiry'):
        print(f"Session expiry: {auth._session_expiry}")
    
    # Do a live check
    print("\nDoing live verification...")
    is_auth_live, details = await auth.verify_authentication_async()
    print(f"Live check: {is_auth_live}")
    print(f"Details: {details}")

asyncio.run(check_auth())