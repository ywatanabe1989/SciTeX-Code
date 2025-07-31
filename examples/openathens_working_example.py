#!/usr/bin/env python3
"""Working example of OpenAthens authentication with OpenURL resolver.

This example properly handles async/await and demonstrates the correct
way to use OpenAthens authentication with the OpenURL resolver.
"""

import asyncio
import os
from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver

logger = logging.getLogger(__name__)


async def main():
    """Main async function to handle authentication and resolution."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create authentication manager with OpenAthens
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        raise ValueError("Please set SCITEX_SCHOLAR_OPENATHENS_EMAIL environment variable")
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager(
        email_openathens=email,
        browser_backend="local",  # Use local browser for OpenAthens
    )
    
    # Get OpenURL resolver URL from environment
    resolver_url = os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    if not resolver_url:
        raise ValueError("Please set SCITEX_SCHOLAR_OPENURL_RESOLVER_URL environment variable")
    
    try:
        # Authenticate with OpenAthens (async)
        logger.info("Authenticating with OpenAthens...")
        auth_result = await auth_manager.authenticate(
            provider_name="openathens",
            force=True  # Force fresh authentication
        )
        
        if auth_result and auth_result.get("success"):
            logger.info("✅ Successfully authenticated with OpenAthens")
        else:
            logger.error("❌ Authentication failed")
            return
        
        # Create OpenURL resolver
        resolver = OpenURLResolver(
            auth_manager=auth_manager,
            resolver_url=resolver_url
        )
        
        # Test DOIs
        dois = [
            "10.1038/s41593-024-01990-7",  # Nature Neuroscience article
            "10.1002/hipo.22488",           # Hippocampus journal article
        ]
        
        logger.info(f"\nResolving {len(dois)} DOIs via OpenURL resolver...")
        
        # Resolve DOIs (this handles async internally)
        results = resolver.resolve(dois, concurrency=1)
        
        # Display results
        for doi, result in zip(dois, results):
            logger.info(f"\nDOI: {doi}")
            if result and result.get("success"):
                logger.info(f"✅ Resolved URL: {result.get('final_url')}")
                logger.info(f"   Access type: {result.get('access_type')}")
            else:
                logger.warning(f"❌ Failed to resolve")
                logger.warning(f"   Reason: {result.get('access_type', 'unknown error')}")
                
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'resolver' in locals() and hasattr(resolver, 'browser'):
            if hasattr(resolver.browser, 'cleanup'):
                await resolver.browser.cleanup()


def run_example():
    """Synchronous wrapper to run the example."""
    # Use asyncio.run() to properly handle the event loop
    asyncio.run(main())


if __name__ == "__main__":
    # Check environment variables
    required_vars = [
        "SCITEX_SCHOLAR_OPENATHENS_EMAIL",
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<your_value>")
        print("\nExample:")
        print("  export SCITEX_SCHOLAR_OPENATHENS_EMAIL=your.email@institution.edu")
        print("  export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL=https://your-institution.hosted.exlibrisgroup.com/sfxlcl41")
        exit(1)
    
    # Run the example
    run_example()