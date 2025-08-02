#!/usr/bin/env python
"""
Sequential workflow for stable DOI resolution.
Processes DOIs one at a time to avoid concurrency issues.
"""
import os
import asyncio
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Set up logging
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
    
    # 1. Initialize and authenticate
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    logger.info("Checking authentication...")
    is_auth = await auth_manager.is_authenticated()
    if not is_auth:
        logger.info("Not authenticated. Opening browser for login...")
        await auth_manager.authenticate()
    else:
        logger.info("Already authenticated.")
    
    logger.success("✅ Authentication confirmed")
    
    # 2. Initialize resolver
    resolver = OpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
        proxy_country="au"
    )
    
    # 3. Test DOIs one by one
    dois_to_test = [
        ("10.1002/hipo.22488", "Wiley"),
        ("10.1038/nature12373", "Nature"),
        ("10.1016/j.neuron.2018.01.048", "Elsevier"),
        ("10.1126/science.1172133", "Science"),
        ("10.1073/pnas.0608765104", "PNAS"),
    ]
    
    logger.info("\n=== Sequential DOI Resolution ===")
    successful = 0
    
    for doi, publisher in dois_to_test:
        logger.info(f"\nResolving {doi} ({publisher})...")
        
        try:
            # Resolve single DOI with lower concurrency
            result = resolver.resolve(doi, concurrency=1)
            
            if result and result.get("success"):
                url = result.get("resolved_url") or result.get("final_url")
                if url and "chrome-error" not in url:
                    logger.success(f"✅ {doi} -> {url}")
                    successful += 1
                else:
                    logger.warning(f"⚠️  {doi} -> Partial success: {url}")
            else:
                logger.error(f"❌ {doi} -> Failed")
                
        except Exception as e:
            logger.error(f"❌ {doi} -> Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    logger.info(f"\n\n📊 Final Score: {successful}/{len(dois_to_test)} successfully resolved")

if __name__ == "__main__":
    asyncio.run(main())