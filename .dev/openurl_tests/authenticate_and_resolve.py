#!/usr/bin/env python
"""Authenticate with OpenAthens and resolve DOIs."""

import os
import asyncio
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable info logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure ZenRows proxy
os.environ.update({
    "SCITEX_SCHOLAR_ZENROWS_API_KEY": "822225799f9a4d847163f397ef86bb81b3f5ceb5",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME": "f5RFwXBC6ZQ2",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD": "kFPQY46gHZEA",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN": "superproxy.zenrows.com",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PORT": "1337",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY": "au",
    "SCITEX_SCHOLAR_ZENROWS_USE_LOCAL_BROWSER": "true"
})

async def authenticate_if_needed(auth_manager):
    """Check and perform authentication if needed."""
    is_authenticated = await auth_manager.is_authenticated()
    
    if not is_authenticated:
        print("\n🔐 Not authenticated. Opening browser for OpenAthens login...")
        print("Please complete the login process in the browser window.")
        print("(Enter your institutional credentials)")
        
        try:
            await auth_manager.authenticate()
            print("\n✅ Authentication completed!")
            
            # Verify authentication
            is_authenticated = await auth_manager.is_authenticated()
            if is_authenticated:
                print("✅ Authentication verified - session is active")
                return True
            else:
                print("❌ Authentication failed - please try again")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    else:
        print("✅ Already authenticated - using existing session")
        return True

async def resolve_dois_with_auth():
    """Resolve DOIs after ensuring authentication."""
    
    print("=== SciTeX Scholar: Authenticated DOI Resolution ===\n")
    
    # Initialize auth manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Ensure we're authenticated
    if not await authenticate_if_needed(auth_manager):
        print("\n⚠️  Cannot proceed without authentication")
        return
    
    # Now we're authenticated - initialize resolver
    print("\n📚 Initializing resolver with authenticated session + ZenRows proxy...")
    resolver = OpenURLResolver(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )
    
    # DOIs to resolve
    dois = [
        "10.1002/hipo.22488",      # Hippocampus - Wiley
        "10.1038/nature12373",     # Nature
        "10.1016/j.neuron.2018.01.048",  # Neuron - Cell Press
        "10.1126/science.1172133", # Science - AAAS
        "10.1073/pnas.0608765104", # PNAS
    ]
    
    print(f"\n🔍 Resolving {len(dois)} DOIs with authenticated access...\n")
    
    # Expected domains for verification
    expected_domains = {
        "10.1002/hipo.22488": ["wiley.com"],
        "10.1038/nature12373": ["nature.com"],
        "10.1016/j.neuron.2018.01.048": ["cell.com", "sciencedirect.com"],
        "10.1126/science.1172133": ["science.org"],
        "10.1073/pnas.0608765104": ["pnas.org"],
    }
    
    # Resolve with single concurrency for stability
    results = await resolver._resolve_parallel_async(dois, concurrency=1)
    
    # Analyze results
    print("\n=== 📊 Resolution Results ===")
    successful = 0
    
    for doi, result in zip(dois, results):
        if result and result.get("success"):
            final_url = result.get("final_url", "")
            
            # Check if we reached the expected publisher
            reached_publisher = any(
                domain in final_url 
                for domain in expected_domains.get(doi, [])
            )
            
            if reached_publisher:
                print(f"\n✅ {doi}")
                print(f"   Publisher URL: {final_url}")
                print(f"   Status: Successfully reached publisher content")
                successful += 1
            elif "openathens" in final_url.lower() or "sso" in final_url.lower():
                print(f"\n⚠️  {doi}")
                print(f"   URL: {final_url[:80]}...")
                print(f"   Status: Still at authentication page")
            else:
                print(f"\n❓ {doi}")
                print(f"   URL: {final_url[:80]}...")
                print(f"   Status: Reached a page, but not the expected publisher")
        else:
            print(f"\n❌ {doi}")
            print(f"   Error: {result.get('access_type', 'unknown') if result else 'No result'}")
    
    print(f"\n\n📈 Summary: {successful}/{len(dois)} DOIs successfully resolved to publisher content")
    
    if successful < len(dois):
        print("\n💡 Troubleshooting tips:")
        print("  • Ensure your institution has access to these journals")
        print("  • Try logging in manually first to verify access")
        print("  • Some publishers may have additional authentication steps")

async def main():
    """Main function."""
    try:
        await resolve_dois_with_auth()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())