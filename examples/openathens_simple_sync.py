#!/usr/bin/env python3
"""Simple synchronous example of using Scholar with OpenAthens.

This example shows the easiest way to use the Scholar module
with OpenAthens authentication in a synchronous manner.
"""

import os
import asyncio
from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def authenticate_and_resolve(dois):
    """Synchronous wrapper for authentication and resolution."""
    
    async def _async_work():
        """Async function that does the actual work."""
        # Create authentication manager
        auth_manager = AuthenticationManager(
            email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"),
            browser_backend="local",
        )
        
        # Authenticate
        logger.info("Authenticating with OpenAthens...")
        auth_result = await auth_manager.authenticate(
            provider_name="openathens",
            force=True
        )
        
        if not auth_result or not auth_result.get("success"):
            raise Exception("Authentication failed")
        
        logger.info("✅ Authentication successful")
        
        # Create resolver
        resolver = OpenURLResolver(
            auth_manager=auth_manager,
            resolver_url=os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
        )
        
        # Resolve DOIs
        results = []
        for doi in dois:
            logger.info(f"\nResolving DOI: {doi}")
            result = await resolver._resolve_single_async(doi=doi)
            results.append(result)
            
            if result and result.get("success"):
                logger.info(f"✅ Resolved to: {result.get('final_url')}")
            else:
                logger.warning(f"❌ Failed to resolve")
        
        # Cleanup
        if hasattr(resolver.browser, 'cleanup'):
            await resolver.browser.cleanup()
            
        return results
    
    # Run async function in sync context
    return asyncio.run(_async_work())


def main():
    """Main function demonstrating OpenAthens with OpenURL resolver."""
    
    # Test DOIs
    dois = [
        "10.1038/s41593-024-01990-7",  # Nature Neuroscience
        "10.1002/hipo.22488",           # Hippocampus
    ]
    
    try:
        # Authenticate and resolve
        results = authenticate_and_resolve(dois)
        
        # Summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        
        for doi, result in zip(dois, results):
            print(f"\nDOI: {doi}")
            if result and result.get("success"):
                print(f"Status: ✅ Success")
                print(f"URL: {result.get('final_url')}")
                print(f"Type: {result.get('access_type')}")
            else:
                print(f"Status: ❌ Failed")
                if result:
                    print(f"Reason: {result.get('access_type', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check environment variables
    required = {
        "SCITEX_SCHOLAR_OPENATHENS_EMAIL": "your.email@institution.edu",
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL": "https://your-institution.hosted.exlibrisgroup.com/sfxlcl41"
    }
    
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print("Missing required environment variables:\n")
        for var in missing:
            print(f"export {var}={required[var]}")
        print("\nFind your resolver URL at: https://www.zotero.org/openurl_resolvers")
        exit(1)
    
    main()