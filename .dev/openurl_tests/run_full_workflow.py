#!/usr/bin/env python
"""
A single, consolidated script to perform the full workflow:
1. Authenticate using a local, visible browser with ZenRows proxy.
2. Resolve a list of DOIs using the authenticated session.
"""
import os
import asyncio
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Main execution function."""
    
    # 1. Initialize the Authentication Manager
    # This will use the local browser + ZenRows proxy method.
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # 2. Authenticate
    # This will open a local browser window. You must complete the login manually.
    # The script will wait until you have successfully logged in.
    logger.info("Starting authentication process...")
    
    # Check if already authenticated
    is_auth = await auth_manager.is_authenticated()
    if not is_auth:
        logger.info("Not authenticated. Opening browser for login...")
        await auth_manager.authenticate()
    else:
        logger.info("Already authenticated. Using existing session.")
    
    logger.success("Authentication successful! Session is now active.")
    
    # 3. Initialize the OpenURL Resolver WITH the authenticated manager
    # It will automatically use the same browser and session.
    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )
    
    dois_to_resolve = [
        "10.1002/hipo.22488",        # Wiley
        "10.1038/nature12373",      # Nature
        "10.1016/j.neuron.2018.01.048", # Elsevier
        "10.1126/science.1172133",      # Science
        "10.1073/pnas.0608765104",      # PNAS (often has strong bot detection)
    ]
    
    # 4. Resolve DOIs using the now-authenticated session
    logger.info(f"Attempting to resolve {len(dois_to_resolve)} DOIs...")
    
    # Use the synchronous wrapper for simplicity here
    results = resolver.resolve(dois_to_resolve)
    
    logger.info("--- Resolution Complete ---")
    for doi, result in zip(dois_to_resolve, results):
        if result and result.get("success"):
            logger.success(f"✓ {doi} -> {result.get('final_url')}")
        else:
            logger.error(f"✗ {doi} -> FAILED ({result.get('access_type', 'Unknown Error')})")

if __name__ == "__main__":
    # This allows running the async main function
    asyncio.run(main())