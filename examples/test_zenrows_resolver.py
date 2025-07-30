#!/usr/bin/env python3
"""Test ZenRowsOpenURLResolver with proper authentication."""

import asyncio
import os
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

async def test_zenrows_resolver():
    """Test the ZenRows OpenURL resolver."""
    
    # Source environment variables
    openathens_email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    
    print(f"OpenAthens Email: {openathens_email}")
    print(f"Resolver URL: {resolver_url}")
    print(f"ZenRows API Key: {zenrows_api_key[:10]}..." if zenrows_api_key else "Not set")
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager(
        email_openathens=openathens_email,
        browser_backend="zenrows",
        zenrows_api_key=zenrows_api_key,
        proxy_country="au"
    )
    
    # Create ZenRows-enabled resolver
    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=resolver_url,
        browser_backend="zenrows",
        zenrows_api_key=zenrows_api_key,
        proxy_country="au"
    )
    
    # DOIs to test
    dois = [
        "10.1002/hipo.22488",
        "10.1038/nature12373",
        "10.1016/j.neuron.2018.01.048",
        "10.1126/science.1172133",
        "10.1073/pnas.0608765104",  # Known anti-bot issues
    ]
    
    print("\n" + "="*60)
    print("Testing ZenRows OpenURL Resolver")
    print("="*60)
    
    # Test single DOI resolution
    print(f"\nTesting single DOI: {dois[0]}")
    try:
        # Initialize browser
        await resolver.browser.initialize()
        
        # Resolve DOI
        result = await resolver.resolve(dois[0])
        
        if result.get("pdf_url"):
            print(f"✓ Success! PDF URL: {result['pdf_url']}")
            print(f"  Title: {result.get('title', 'Unknown')}")
            print(f"  Via: {result.get('source', 'OpenURL')}")
        else:
            print(f"✗ No PDF URL found")
            print(f"  Result: {result}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await resolver.browser.close()
    
    print("\nTest complete!")

if __name__ == "__main__":
    # Source environment variables
    import subprocess
    subprocess.run(['source', '/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src'], 
                   shell=True, executable='/bin/bash')
    
    # Run test
    asyncio.run(test_zenrows_resolver())