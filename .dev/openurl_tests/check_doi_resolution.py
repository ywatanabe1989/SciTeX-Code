#!/usr/bin/env python
"""Check if DOIs resolve to actual publisher URLs."""

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

async def main():
    """Check DOI resolution."""
    
    print("=== Checking DOI Resolution ===\n")
    
    # Initialize auth manager
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Check auth status
    is_authenticated = await auth_manager.is_authenticated()
    print(f"Authentication status: {is_authenticated}\n")
    
    # Initialize resolver
    resolver = OpenURLResolver(
        auth_manager,
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )
    
    # DOIs to check
    dois = [
        "10.1002/hipo.22488",      # Hippocampus - Wiley
        "10.1038/nature12373",     # Nature
        "10.1016/j.neuron.2018.01.048",  # Neuron - Cell Press/Elsevier
        "10.1126/science.1172133", # Science - AAAS
        "10.1073/pnas.0608765104", # PNAS
    ]
    
    print("Resolving DOIs...\n")
    
    # Expected publisher domains
    expected_domains = {
        "10.1002/hipo.22488": ["wiley.com", "onlinelibrary.wiley.com"],
        "10.1038/nature12373": ["nature.com"],
        "10.1016/j.neuron.2018.01.048": ["cell.com", "sciencedirect.com"],
        "10.1126/science.1172133": ["science.org", "sciencemag.org"],
        "10.1073/pnas.0608765104": ["pnas.org"],
    }
    
    # Resolve DOIs one by one for detailed results
    for doi in dois:
        print(f"\n{'='*60}")
        print(f"DOI: {doi}")
        print(f"Expected: {', '.join(expected_domains.get(doi, ['Unknown']))}")
        
        try:
            result = await resolver._resolve_single_async(doi=doi)
            
            if result and result.get("success"):
                final_url = result.get("final_url", "")
                access_type = result.get("access_type", "unknown")
                
                # Check if we reached the publisher
                reached_publisher = any(domain in final_url for domain in expected_domains.get(doi, []))
                
                if reached_publisher:
                    print(f"✅ SUCCESS - Reached publisher!")
                    print(f"   URL: {final_url}")
                    print(f"   Access: {access_type}")
                elif "openathens" in final_url or "sso" in final_url:
                    print(f"🔐 AUTHENTICATION REQUIRED")
                    print(f"   Stuck at: {final_url[:80]}...")
                    print(f"   Need to authenticate first")
                else:
                    print(f"⚠️  PARTIAL SUCCESS")
                    print(f"   URL: {final_url[:80]}...")
                    print(f"   Access: {access_type}")
            else:
                print(f"❌ FAILED")
                print(f"   Error: {result.get('access_type', 'unknown') if result else 'No result'}")
                if result and result.get('resolver_url'):
                    print(f"   Resolver: {result['resolver_url'][:80]}...")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n{'='*60}")
    print("\nSummary:")
    if not is_authenticated:
        print("⚠️  You're not authenticated. Most resolutions will fail at login page.")
        print("   Run: await auth_manager.authenticate() to login first")
    else:
        print("✅ You're authenticated. Resolutions should reach publishers.")

if __name__ == "__main__":
    asyncio.run(main())