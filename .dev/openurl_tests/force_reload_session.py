#!/usr/bin/env python
"""Force reload authentication session."""

import os
import asyncio
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver
from scitex import logging

# Enable info logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure ZenRows
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
    """Force reload session and test resolution."""
    print("=== Force Reload Session and Test ===\n")
    
    # Initialize auth manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Force reload from cache
    print("Forcing cache reload...")
    if hasattr(auth_manager, '_providers'):
        for provider in auth_manager._providers.values():
            if hasattr(provider, '_load_session_cache'):
                await provider._load_session_cache()
    
    # Check status
    is_auth = await auth_manager.is_authenticated()
    print(f"Authentication status after reload: {is_auth}")
    
    if is_auth:
        # Get session info
        provider = auth_manager.get_active_provider()
        if provider and hasattr(provider, 'get_session_info'):
            info = await provider.get_session_info()
            print(f"Session info: {info}")
        
        # Try to get cookies
        try:
            cookies = await auth_manager.get_auth_cookies()
            print(f"\nRetrieved {len(cookies)} cookies")
            
            # Test with one DOI
            print("\nTesting DOI resolution with authenticated session...")
            resolver = OpenURLResolver(
                auth_manager,
                os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
                zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
                proxy_country="au"
            )
            
            test_doi = "10.1002/hipo.22488"
            result = await resolver._resolve_single_async(doi=test_doi)
            
            if result and result.get("success"):
                print(f"✅ Success: {result.get('final_url')}")
            else:
                print(f"❌ Failed: {result}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nStill not authenticated after reload.")
        print("The session may have expired or been corrupted.")
        print("\nRun authentication again:")
        print("  python interactive_auth_and_resolve.py")

if __name__ == "__main__":
    asyncio.run(main())