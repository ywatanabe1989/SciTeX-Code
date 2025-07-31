#!/usr/bin/env python3
"""Hybrid OpenURL resolver that combines browser and ZenRows approaches."""

import asyncio
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url._OpenURLResolver import OpenURLResolver
from scitex.scholar.open_url._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows

logger = logging.getLogger(__name__)


class HybridOpenURLResolver(OpenURLResolver):
    """OpenURL resolver that intelligently switches between browser and ZenRows.
    
    Strategy:
    1. Try browser-based resolution first (handles JavaScript and complex auth flows)
    2. If anti-bot measures are detected, fallback to ZenRows
    3. Pass all browser cookies through ZenRows for authenticated access
    """
    
    def __init__(self, auth_manager, resolver_url, zenrows_api_key=None):
        super().__init__(auth_manager, resolver_url)
        self.zenrows_api_key = zenrows_api_key
        self._zenrows_resolver = None
        
        if zenrows_api_key:
            self._zenrows_resolver = OpenURLResolverWithZenRows(
                auth_manager,
                resolver_url,
                zenrows_api_key,
                use_browser_cookies=True
            )
    
    async def _resolve_single_async(
        self,
        title: str = "",
        authors: Optional[list] = None,
        journal: str = "",
        year: Optional[int] = None,
        volume: Optional[int] = None,
        issue: Optional[int] = None,
        pages: str = "",
        doi: str = "",
        pmid: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Resolve using hybrid approach."""
        
        # First, try browser-based resolution
        logger.info("Attempting browser-based resolution...")
        
        try:
            # Try the standard browser approach
            result = await super()._resolve_single_async(
                title, authors, journal, year, volume, issue, pages, doi, pmid
            )
            
            if result and result.get("success"):
                logger.info("Browser resolution successful")
                return result
                
            # Check if we hit anti-bot measures
            if result and result.get("access_type") in ["captcha_required", "rate_limited", "bot_detected"]:
                logger.warning("Anti-bot measures detected, switching to ZenRows")
                
                if self._zenrows_resolver:
                    return await self._zenrows_resolver._resolve_single_async(
                        title, authors, journal, year, volume, issue, pages, doi, pmid
                    )
                else:
                    logger.error("No ZenRows API key configured for anti-bot bypass")
                    return result
                    
        except Exception as e:
            # Check for specific anti-bot errors
            error_msg = str(e).lower()
            if any(indicator in error_msg for indicator in [
                "captcha", "rate limit", "bot", "403", "429", "timeout"
            ]):
                logger.warning(f"Browser failed with possible anti-bot error: {e}")
                
                if self._zenrows_resolver:
                    logger.info("Falling back to ZenRows...")
                    return await self._zenrows_resolver._resolve_single_async(
                        title, authors, journal, year, volume, issue, pages, doi, pmid
                    )
            else:
                logger.error(f"Browser resolution failed: {e}")
                raise
        
        return None


async def test_hybrid_resolver():
    """Test the hybrid resolver approach."""
    import os
    
    # Initialize
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Check authentication
    if not await auth_manager.is_authenticated():
        print("Authenticating...")
        await auth_manager.authenticate()
    
    resolver = HybridOpenURLResolver(
        auth_manager,
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    )
    
    # Test case
    result = await resolver._resolve_single_async(
        doi="10.1038/nature12373",
        title="A mesoscale connectome of the mouse brain",
        journal="Nature",
        year=2014
    )
    
    print(f"Result: {result}")
    
    await auth_manager.close()


if __name__ == "__main__":
    logging.getLogger("scitex.scholar").setLevel(logging.INFO)
    asyncio.run(test_hybrid_resolver())