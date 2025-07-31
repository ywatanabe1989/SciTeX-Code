#!/usr/bin/env python
"""Interactive authentication and DOI resolution."""

import os
import asyncio
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # Less verbose for interactive use

# Configure environment
os.environ.update({
    "SCITEX_SCHOLAR_ZENROWS_API_KEY": "822225799f9a4d847163f397ef86bb81b3f5ceb5",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME": "f5RFwXBC6ZQ2",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD": "kFPQY46gHZEA",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN": "superproxy.zenrows.com",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PORT": "1337",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY": "au",
    "SCITEX_SCHOLAR_ZENROWS_USE_LOCAL_BROWSER": "true"
})

async def main():
    """Interactive authentication."""
    print("=== SciTeX Scholar Authentication ===\n")
    
    # Initialize auth manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Check current status
    is_auth = await auth_manager.is_authenticated()
    print(f"Current status: {'Authenticated ✅' if is_auth else 'Not authenticated ❌'}")
    
    if not is_auth:
        print("\n🔐 Opening browser for OpenAthens login...")
        print("\nPlease:")
        print("1. Enter your institutional email")
        print("2. Complete the login process")
        print("3. Wait for the success message\n")
        
        try:
            await auth_manager.authenticate()
            print("\n✅ Authentication completed!")
            
            # Verify
            is_auth = await auth_manager.is_authenticated()
            if is_auth:
                print("✅ Session verified and saved")
                print("\nYou can now resolve DOIs with your authenticated session!")
                print("\nNext step: Run the resolution script or use IPython:")
                print("  python check_doi_resolution.py")
            else:
                print("❌ Authentication verification failed")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("\nYou're already authenticated! Session is active.")
        print("You can proceed with DOI resolution.")

if __name__ == "__main__":
    asyncio.run(main())