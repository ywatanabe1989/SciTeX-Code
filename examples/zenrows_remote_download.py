#!/usr/bin/env python3
"""
ZenRows Remote Download with Authentication

This script uses ZenRows remote browser to handle bot barriers and CAPTCHAs
while using your institutional credentials for paper access.
"""

import os
import asyncio
from dotenv import load_dotenv
from scitex.scholar import Scholar
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager

# Load environment variables
load_dotenv()

async def download_with_zenrows():
    """Download papers using ZenRows remote browser"""
    
    print("ZenRows Remote Download")
    print("="*60)
    print("Using ZenRows to bypass bot barriers and handle CAPTCHAs")
    print("While authenticating with your institutional credentials")
    print("="*60 + "\n")
    
    # Ensure we're using ZenRows backend
    os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "zenrows"
    
    # Get configuration
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    
    if not zenrows_api_key:
        print("ERROR: SCITEX_SCHOLAR_ZENROWS_API_KEY not found in environment")
        return
    
    # Test DOIs
    test_dois = [
        "10.1111/acer.15478",  # Behind paywall, needs institutional access
        "10.1371/journal.pone.0021079",  # Open access for comparison
        "10.1038/s41586-020-2649-2",  # Nature paper
    ]
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager()
    
    # Create OpenURL resolver with ZenRows
    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=resolver_url,
        browser_backend="zenrows",
        zenrows_api_key=zenrows_api_key,
        proxy_country="au"  # Use Australian proxy for University of Melbourne
    )
    
    print(f"Resolver URL: {resolver_url}")
    print(f"Browser backend: zenrows")
    print(f"Proxy country: au")
    print("-"*60 + "\n")
    
    # Test each DOI
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}/{len(test_dois)}] Testing DOI: {doi}")
        print("-"*40)
        
        try:
            # Resolve using OpenURL
            result = await resolver._resolve_single_async(doi=doi)
            
            print(f"Resolution result:")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Access type: {result.get('access_type', 'N/A')}")
            print(f"  Final URL: {result.get('final_url', 'N/A')[:80]}...")
            
            if result.get('success') and result.get('final_url'):
                print(f"  ✓ Successfully resolved to publisher URL")
                
                # Here you could add download logic using the final URL
                # For example, using PDFDownloader with the resolved URL
            else:
                print(f"  ✗ Could not resolve to full text")
                print(f"  Reason: {result.get('access_type', 'unknown')}")
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Add delay between requests
        if i < len(test_dois):
            print(f"\nWaiting before next request...")
            await asyncio.sleep(3)
    
    print("\n" + "="*60)
    print("Summary:")
    print("ZenRows handles:")
    print("  - Bot detection bypass")
    print("  - CAPTCHA solving (if configured)")
    print("  - JavaScript rendering")
    print("  - Proxy rotation")
    print("\nYour credentials handle:")
    print("  - Institutional authentication")
    print("  - Full-text access rights")
    print("="*60)

async def test_zenrows_with_manual_auth():
    """Test ZenRows with manual authentication flow"""
    
    print("\nAlternative: ZenRows with Manual Authentication")
    print("="*60)
    print("This approach opens ZenRows browser for manual login")
    print("then continues with automated downloads")
    print("-"*60 + "\n")
    
    # You can implement manual login flow here using
    # the zenrows_remote_control.py approach, then
    # save cookies/session for subsequent requests

if __name__ == "__main__":
    # Run the automated approach
    asyncio.run(download_with_zenrows())
    
    # Optionally test manual approach
    # asyncio.run(test_zenrows_with_manual_auth())