#!/usr/bin/env python3
"""
Test manual SSO login through ZenRows remote browser.

This script demonstrates how to:
1. Connect to ZenRows remote browser
2. Navigate to your university's OpenURL resolver
3. Allow manual SSO login
4. Resolve DOIs to PDFs using the authenticated session
"""

import asyncio
import os
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_manual_sso_login():
    """Test manual SSO login on ZenRows remote browser."""
    
    # Check environment
    print("Checking environment variables...")
    openathens_email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    
    print(f"✓ Email: {openathens_email}")
    print(f"✓ Resolver URL: {resolver_url}")
    print(f"✓ ZenRows API Key: {zenrows_api_key[:10]}..." if zenrows_api_key else "Not set")
    
    if not all([resolver_url, zenrows_api_key]):
        print("\nError: Missing required environment variables!")
        return
    
    # Initialize authentication manager with ZenRows backend
    print("\nInitializing ZenRows browser connection...")
    auth_manager = AuthenticationManager(
        email_openathens=openathens_email,
        browser_backend="zenrows",
        zenrows_api_key=zenrows_api_key,
        proxy_country="au"  # Australian proxy for UniMelb
    )
    
    # Create resolver with ZenRows backend
    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=resolver_url,
        browser_backend="zenrows",
        zenrows_api_key=zenrows_api_key,
        proxy_country="au"
    )
    
    print("\n" + "="*70)
    print("MANUAL SSO LOGIN TEST - ZENROWS REMOTE BROWSER")
    print("="*70)
    print("\nThis test will:")
    print("1. Connect to a remote browser on ZenRows servers")
    print("2. Navigate to your university's OpenURL resolver")
    print("3. Allow you to manually login through SSO")
    print("4. Test DOI resolution using the authenticated session")
    print("="*70 + "\n")
    
    # Test DOIs
    test_dois = [
        "10.1002/hipo.22488",  # Hippocampus journal
        "10.1038/nature12373", # Nature
        "10.1016/j.neuron.2018.01.048", # Neuron
    ]
    
    print("Testing DOI resolution with manual authentication...\n")
    
    for doi in test_dois[:1]:  # Test just one first
        print(f"Resolving DOI: {doi}")
        try:
            # The resolver will:
            # 1. Open ZenRows browser
            # 2. Navigate to OpenURL resolver
            # 3. Detect if login is needed
            # 4. Allow manual login if required
            # 5. Find and return PDF URL
            
            # Check if resolve is async or sync
            import inspect
            if inspect.iscoroutinefunction(resolver.resolve):
                result = await resolver.resolve(doi)
            else:
                # Run sync method in thread to avoid blocking
                import asyncio
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, resolver.resolve, doi)
            
            if result.get("pdf_url"):
                print(f"✓ SUCCESS! Found PDF URL")
                print(f"  Title: {result.get('title', 'Unknown')}")
                print(f"  PDF URL: {result['pdf_url']}")
                print(f"  Source: {result.get('source', 'OpenURL')}")
                
                # If first DOI worked, the session is authenticated
                # Try more DOIs with the same session
                if len(test_dois) > 1:
                    print("\n✓ Session authenticated! Testing more DOIs...\n")
                    
                    for doi in test_dois[1:]:
                        print(f"Resolving DOI: {doi}")
                        result = await resolver.resolve(doi)
                        if result.get("pdf_url"):
                            print(f"  ✓ Found: {result.get('title', 'Unknown')[:50]}...")
                        else:
                            print(f"  ✗ No PDF URL found")
            else:
                print(f"✗ No PDF URL found")
                print(f"  Debug info: {result}")
                
                if "error" in result:
                    print(f"\nError details: {result['error']}")
                    
                print("\nPossible reasons:")
                print("- Login was not completed")
                print("- Session expired")
                print("- Journal not accessible through your institution")
                print("- Anti-bot detection (should be bypassed by ZenRows)")
                
        except KeyboardInterrupt:
            print("\n\n✗ Test cancelled by user")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("MANUAL LOGIN TIPS:")
    print("="*70)
    print("1. When the browser opens, you'll see your university's login page")
    print("2. Enter your credentials manually")
    print("3. Complete any 2FA requirements")
    print("4. Once logged in, the script will continue automatically")
    print("5. The session will be maintained for subsequent requests")
    print("\nNOTE: ZenRows browser runs on their servers, not locally")
    print("This helps bypass anti-bot measures that block local automation")
    print("="*70)

if __name__ == "__main__":
    # Source environment variables and run
    print("ZenRows Remote Browser - Manual SSO Login Test")
    print("=" * 50 + "\n")
    
    # Import and source env vars
    import subprocess
    env_file = "/home/ywatanabe/.dotfiles/.bash.d/secrets/001_ENV_SCITEX.src"
    
    # Source the file properly
    result = subprocess.run(
        f"source {env_file} && env",
        shell=True,
        capture_output=True,
        text=True,
        executable="/bin/bash"
    )
    
    if result.returncode == 0:
        # Parse environment variables
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('SCITEX_'):
                    os.environ[key] = value
    
    # Run the test
    asyncio.run(test_manual_sso_login())