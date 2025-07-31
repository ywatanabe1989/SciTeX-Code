#!/usr/bin/env python
"""Debug authentication session issues."""

import os
import asyncio
from pathlib import Path
from scitex.scholar.auth import AuthenticationManager
from scitex import logging
import json

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

async def main():
    """Debug authentication session."""
    print("=== Authentication Session Debug ===\n")
    
    # Check cache directory
    cache_dir = Path.home() / ".scitex" / "scholar"
    print(f"Cache directory: {cache_dir}")
    print(f"Exists: {cache_dir.exists()}")
    
    if cache_dir.exists():
        print("\nCache contents:")
        for item in cache_dir.rglob("*"):
            if item.is_file():
                print(f"  {item.relative_to(cache_dir)}")
                if item.name.endswith("_session.json"):
                    try:
                        with open(item) as f:
                            data = json.load(f)
                            print(f"    Cookies: {len(data.get('cookies', []))} items")
                            print(f"    Expiry: {data.get('expiry', 'N/A')}")
                    except:
                        print("    (Could not read)")
    
    print("\n" + "="*50 + "\n")
    
    # Initialize auth manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Check authentication
    is_auth = await auth_manager.is_authenticated()
    print(f"Authentication status: {is_auth}")
    
    if is_auth:
        # Get cookies
        try:
            cookies = await auth_manager.get_auth_cookies()
            print(f"Retrieved {len(cookies)} cookies")
            
            # Show some cookie details
            print("\nCookie domains:")
            domains = set()
            for cookie in cookies:
                domain = cookie.get('domain', 'N/A')
                domains.add(domain)
            for domain in sorted(domains):
                print(f"  {domain}")
                
        except Exception as e:
            print(f"Error getting cookies: {e}")
    else:
        print("\nNot authenticated. The session may have:")
        print("  • Expired")
        print("  • Been saved to a different user directory")
        print("  • Failed to save properly")
        print("\nTry authenticating again with --force flag")

if __name__ == "__main__":
    asyncio.run(main())