#!/usr/bin/env python
"""OpenURL resolver with properly configured ZenRows proxy."""

import os
import asyncio
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Set up ZenRows proxy credentials
os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "822225799f9a4d847163f397ef86bb81b3f5ceb5"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME"] = "f5RFwXBC6ZQ2"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD"] = "kFPQY46gHZEA"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN"] = "superproxy.zenrows.com"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_PORT"] = "1337"
os.environ["SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY"] = "au"

# Enable local browser with stealth
os.environ["SCITEX_SCHOLAR_ZENROWS_USE_LOCAL_BROWSER"] = "true"

async def main():
    """Main async function."""
    # Initialize authentication
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Check authentication status
    is_authenticated = await auth_manager.is_authenticated()
    print(f"Authentication status: {is_authenticated}")
    
    # Initialize resolver with ZenRows
    resolver = OpenURLResolver(
        auth_manager, 
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )
    
    # Test with a single DOI first
    test_doi = "10.1002/hipo.22488"
    print(f"\nTesting single DOI: {test_doi}")
    
    result = await resolver._resolve_single_async(doi=test_doi)
    
    if result and result.get("success"):
        print(f"✅ Success: {result.get('final_url')}")
    else:
        print(f"❌ Failed: {result}")
    
    # If single test works, try multiple
    if result and result.get("success"):
        dois = [
            "10.1038/nature12373",
            "10.1016/j.neuron.2018.01.048",
            "10.1126/science.1172133",
            "10.1073/pnas.0608765104",
        ]
        
        print(f"\n\nResolving {len(dois)} DOIs in parallel...")
        results = await resolver._resolve_parallel_async(dois, concurrency=2)
        
        for doi, result in zip(dois, results):
            if result and result.get("success"):
                print(f"✅ {doi}: {result.get('final_url')}")
            else:
                print(f"❌ {doi}: {result.get('access_type', 'error') if result else 'No result'}")

if __name__ == "__main__":
    asyncio.run(main()