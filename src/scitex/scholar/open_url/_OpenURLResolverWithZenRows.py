#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 21:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_OpenURLResolverWithZenRows.py
# ----------------------------------------
"""OpenURL resolver with ZenRows integration for bypassing bot detection.

This implementation uses the correct cookie handling approach based on ZenRows FAQ:
1. Cookies are returned in Zr-Cookies response header
2. Use session_id to maintain same IP for 10 minutes
3. Send cookies as Custom Headers in subsequent requests
"""

from __future__ import annotations
import os
import uuid
import aiohttp
import asyncio
from typing import Dict, Optional, Any, List
from urllib.parse import urlencode

from scitex import logging
from ...errors import ScholarError
from ._OpenURLResolver import OpenURLResolver

logger = logging.getLogger(__name__)


class OpenURLResolverWithZenRows(OpenURLResolver):
    """OpenURL resolver enhanced with ZenRows anti-bot bypass capabilities."""
    
    def __init__(
        self, 
        auth_manager,
        resolver_url: str,
        zenrows_api_key: Optional[str] = None,
        use_zenrows: bool = True
    ):
        """Initialize resolver with optional ZenRows support.
        
        Args:
            auth_manager: Authentication manager
            resolver_url: Base URL of institutional OpenURL resolver
            zenrows_api_key: ZenRows API key (uses env var if not provided)
            use_zenrows: Whether to use ZenRows for anti-bot bypass
        """
        super().__init__(auth_manager, resolver_url)
        
        self.use_zenrows = use_zenrows
        self.zenrows_api_key = zenrows_api_key or os.environ.get(
            "ZENROWS_API_KEY", 
            os.environ.get("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        )
        
        # Session management for ZenRows
        self.zenrows_session_id = None
        self.zenrows_cookies: Dict[str, str] = {}
        
        if self.use_zenrows and not self.zenrows_api_key:
            logger.warning("ZenRows enabled but no API key found")
            self.use_zenrows = False
            
    def _generate_session_id(self) -> str:
        """Generate unique session ID for maintaining same IP in ZenRows."""
        # ZenRows requires numeric session_id
        import random
        return str(random.randint(100000, 999999))
        
    def _parse_cookie_header(self, cookie_header: str) -> Dict[str, str]:
        """Parse cookie header string into dictionary."""
        cookies = {}
        
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                cookies[name.strip()] = value.strip()
                
        return cookies
        
    async def _zenrows_request(
        self, 
        url: str,
        use_cookies: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Make request through ZenRows API with proper cookie handling.
        
        Args:
            url: Target URL
            use_cookies: Whether to include stored cookies
            
        Returns:
            Dict with response data or None if failed
        """
        if not self.zenrows_session_id:
            self.zenrows_session_id = self._generate_session_id()
            logger.info(f"Created ZenRows session: {self.zenrows_session_id}")
            
        params = {
            "url": url,
            "apikey": self.zenrows_api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "session_id": self.zenrows_session_id,
            "wait": "5"  # Wait for page to load
        }
        
        headers = {}
        if use_cookies and self.zenrows_cookies:
            # Send cookies as HTTP headers with custom_headers=true
            cookie_string = "; ".join([
                f"{k}={v}" for k, v in self.zenrows_cookies.items()
            ])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            logger.info(f"Sending {len(self.zenrows_cookies)} cookies")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"ZenRows request failed: {response.status}")
                        return None
                        
                    content = await response.text()
                    
                    # Extract cookies from response headers
                    zr_cookies = response.headers.get('Zr-Cookies', '')
                    if zr_cookies:
                        new_cookies = self._parse_cookie_header(zr_cookies)
                        self.zenrows_cookies.update(new_cookies)
                        logger.info(f"Updated cookies, total: {len(self.zenrows_cookies)}")
                        
                    # Get final URL
                    final_url = response.headers.get('Zr-Final-Url', url)
                    
                    return {
                        "content": content,
                        "final_url": final_url,
                        "cookies": self.zenrows_cookies,
                        "status": response.status
                    }
                    
        except Exception as e:
            logger.error(f"ZenRows request error: {e}")
            return None
            
    async def _resolve_single_async_zenrows(
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
        """Resolve using ZenRows for anti-bot bypass."""
        
        if not self.resolver_url:
            logger.warning("No OpenURL resolver URL configured")
            return None
            
        # Build OpenURL
        openurl = self.build_openurl(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
        
        logger.info(f"Resolving via ZenRows: {openurl}")
        
        # Step 1: Initial request to OpenURL resolver
        result = await self._zenrows_request(openurl, use_cookies=False)
        
        if not result:
            logger.error("Failed to access OpenURL resolver")
            return None
            
        content = result["content"]
        final_url = result["final_url"]
        
        # Check if we reached publisher directly
        if self._is_publisher_url(final_url, doi):
            logger.info(f"Reached publisher directly: {final_url}")
            
            # Check for access
            has_access = any(
                phrase in content.lower()
                for phrase in ["full text", "download pdf", "view pdf"]
            )
            
            return {
                "final_url": final_url,
                "resolver_url": openurl,
                "access_type": "direct_zenrows",
                "success": has_access,
                "has_cookies": len(self.zenrows_cookies) > 0
            }
            
        # Step 2: Look for full-text links
        # This is simplified - in production would parse HTML properly
        if "no full text available" in content.lower():
            logger.info("No access available")
            return {
                "final_url": None,
                "resolver_url": openurl,
                "access_type": "no_access",
                "success": False
            }
            
        # Step 3: If we have cookies, try accessing publisher with them
        if self.zenrows_cookies and doi:
            publisher_url = f"https://doi.org/{doi}"
            logger.info(f"Attempting publisher access with cookies: {publisher_url}")
            
            publisher_result = await self._zenrows_request(
                publisher_url, 
                use_cookies=True
            )
            
            if publisher_result:
                final_url = publisher_result["final_url"]
                content = publisher_result["content"]
                
                has_access = any(
                    phrase in content.lower()
                    for phrase in ["full text", "download pdf", "view pdf"]
                ) and not any(
                    phrase in content.lower()
                    for phrase in ["purchase", "subscribe", "get access"]
                )
                
                return {
                    "final_url": final_url,
                    "resolver_url": openurl,
                    "access_type": "zenrows_with_cookies",
                    "success": has_access,
                    "cookie_count": len(self.zenrows_cookies)
                }
                
        # Default response
        return {
            "final_url": final_url,
            "resolver_url": openurl,
            "access_type": "zenrows_attempted",
            "success": False
        }
        
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
        """Override to use ZenRows when enabled."""
        
        if self.use_zenrows:
            logger.info("Using ZenRows for resolution")
            return await self._resolve_single_async_zenrows(
                title, authors, journal, year, volume, issue, pages, doi, pmid
            )
        else:
            # Fall back to regular browser-based resolution
            logger.info("Using standard browser resolution")
            return await super()._resolve_single_async(
                title, authors, journal, year, volume, issue, pages, doi, pmid
            )
            
    def reset_zenrows_session(self):
        """Reset ZenRows session (new IP and clear cookies)."""
        self.zenrows_session_id = None
        self.zenrows_cookies = {}
        logger.info("ZenRows session reset")


# Convenience function for testing
async def test_zenrows_resolver():
    """Test the ZenRows-enhanced resolver."""
    from ..auth import AuthenticationManager
    
    # Initialize
    auth_manager = AuthenticationManager()
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    
    resolver = OpenURLResolverWithZenRows(
        auth_manager,
        resolver_url,
        use_zenrows=True
    )
    
    # Test with a DOI
    result = await resolver._resolve_single_async(
        doi="10.1038/nature12373",
        title="A mesoscale connectome of the mouse brain",
        journal="Nature",
        year=2014
    )
    
    if result:
        print(f"Success: {result['success']}")
        print(f"Final URL: {result.get('final_url')}")
        print(f"Access type: {result.get('access_type')}")
        print(f"Cookies: {result.get('cookie_count', 0)}")
    else:
        print("Resolution failed")
        
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_zenrows_resolver())