#!/usr/bin/env python3
"""
OpenURL Resolution with OpenAthens Authentication

This example shows how to use OpenAthens authentication with OpenURL resolver.
The ZenRows stealth browser (if API key is set) helps bypass anti-bot detection
during the authentication process.
"""

import asyncio
import os
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def openurl_with_openathens():
    """Use OpenURL resolver with OpenAthens authentication."""
    
    print("\n=== OpenURL Resolution with OpenAthens ===\n")
    
    # Check configuration
    openathens_email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not openathens_email:
        print("⚠️  Please set SCITEX_SCHOLAR_OPENATHENS_EMAIL environment variable")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL=your@university.edu")
        return
    
    print(f"OpenAthens email: {openathens_email}")
    
    # Initialize authentication manager with OpenAthens
    auth_manager = AuthenticationManager(
        email_openathens=openathens_email
    )
    
    # Check if ZenRows is available for anti-bot protection
    if os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
        print("✅ ZenRows stealth browser enabled (helps with authentication)")
    else:
        print("⚠️  No ZenRows API key (may encounter anti-bot blocks)")
    
    # Authenticate with OpenAthens
    print("\n📝 Authenticating with OpenAthens...")
    print("   A browser window will open for login")
    print("   Complete your institutional login")
    print("   The browser will use ZenRows proxy if available\n")
    
    try:
        # Force authentication to ensure fresh login
        auth_result = await auth_manager.authenticate(force=True)
        print(f"✅ Authentication successful: {auth_result}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("   Continuing without authentication...")
    
    # Initialize OpenURL resolver
    resolver_url = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    print(f"\nResolver URL: {resolver_url}")
    
    resolver = OpenURLResolver(
        auth_manager,
        resolver_url
    )
    
    # Test DOIs
    dois = [
        "10.1038/nature12373",  # Nature
        "10.1016/j.cell.2023.08.040",  # Cell
        "10.1126/science.abm0829",  # Science
        "10.1073/pnas.0608765104",  # PNAS (anti-bot issues)
    ]
    
    print(f"\n📚 Testing {len(dois)} DOIs with authenticated access...\n")
    
    # Test resolution with authentication
    for i, doi in enumerate(dois, 1):
        print(f"[{i}/{len(dois)}] Resolving {doi}")
        
        try:
            result = await resolver._resolve_single_async(doi=doi)
            
            if result:
                if result.get('success'):
                    print(f"   ✅ Success!")
                    print(f"   URL: {result.get('final_url', 'N/A')[:80]}...")
                    print(f"   Access: {result.get('access_type', 'unknown')}")
                else:
                    print(f"   ❌ Failed: {result.get('access_type', 'unknown')}")
            else:
                print("   ❌ No result returned")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # Small delay between requests
        if i < len(dois):
            await asyncio.sleep(2)
    
    print("✅ Test complete!\n")
    print("Note: With OpenAthens authentication, you should have access to")
    print("      paywalled content from your institution's subscriptions.")


def main():
    """Run the OpenAthens + OpenURL test."""
    
    print("\n🎓 OpenURL Resolution with OpenAthens Authentication")
    print("=" * 55)
    print("\nThis test will:")
    print("1. Authenticate with OpenAthens (browser login)")
    print("2. Use authenticated session for OpenURL resolution")
    print("3. Test access to paywalled papers\n")
    
    print("Requirements:")
    print("- SCITEX_SCHOLAR_OPENATHENS_EMAIL (required)")
    print("- SCITEX_SCHOLAR_ZENROWS_API_KEY (optional, for anti-bot)")
    print("- SCITEX_SCHOLAR_OPENURL_RESOLVER_URL (optional)\n")
    
    # Check required configuration
    if not os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"):
        print("❌ Missing required environment variable!")
        print("\nPlease run:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL=your@university.edu")
        return
    
    ready = input("\nReady to authenticate? (Y/n): ").strip().lower() != 'n'
    
    if ready:
        asyncio.run(openurl_with_openathens())
    else:
        print("\nCancelled.")


if __name__ == "__main__":
    main()

# EOF