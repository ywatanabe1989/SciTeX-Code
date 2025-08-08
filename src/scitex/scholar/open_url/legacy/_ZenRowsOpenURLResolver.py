#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 01:55:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_ZenRowsOpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_ZenRowsOpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenURL resolver using ZenRows API for anti-bot bypass.

This resolver uses ZenRows API directly to bypass anti-bot measures.
It tracks the final URL via the Zr-Final-Url header.

LIMITATIONS:
- Cannot follow JavaScript links that require authentication context
- Better suited for direct HTTP redirects than JavaScript-based navigation
- For full JavaScript support with authentication, use the browser-based OpenURLResolver

BEST USE CASES:
- High-volume resolution where some failures are acceptable
- Bypassing rate limits and anti-bot measures
- Initial discovery of which papers have institutional access
"""

import random
from typing import Optional, Dict, Any, List, Union
import aiohttp

from scitex import logging
from ._OpenURLResolver import OpenURLResolver

logger = logging.getLogger(__name__)


class ZenRowsOpenURLResolver(OpenURLResolver):
    """OpenURL resolver using ZenRows API for anti-bot bypass.
    
    This resolver uses ZenRows API directly (not browser) to:
    - Bypass anti-bot measures (CAPTCHAs, rate limits)
    - Follow HTTP redirects automatically
    - Return final URL via Zr-Final-Url header
    
    Limitations:
    - Cannot execute JavaScript that requires authentication cookies
    - May not work with all institutional resolvers
    - Better for discovery than guaranteed access
    
    Benefits:
    - High performance and scalability
    - No browser overhead
    - Good for batch processing
    
    Usage:
        resolver = ZenRowsOpenURLResolver(
            auth_manager,
            resolver_url="https://your.institution.resolver/",
            zenrows_api_key="your_api_key"  # or set SCITEX_SCHOLAR_ZENROWS_API_KEY
        )
        
        result = await resolver.resolve_async(doi="10.1073/pnas.0608765104")
        
    For full authentication support, use the standard OpenURLResolver instead.
    """
    
    def __init__(
        self,
        auth_manager,
        resolver_url: str,
        zenrows_api_key: Optional[str] = None,
        enable_captcha_solving: bool = True,
    ):
        """Initialize resolver with ZenRows API.
        
        Args:
            auth_manager: Authentication manager
            resolver_url: Base URL of institutional OpenURL resolver
            zenrows_api_key: ZenRows API key (or from env var)
            enable_captcha_solving: Enable 2Captcha integration (requires ZenRows integration setup)
        """
        # Initialize parent class
        super().__init__(auth_manager, resolver_url)
        
        # Get API key
        self.zenrows_api_key = zenrows_api_key or os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        
        if not self.zenrows_api_key:
            raise ValueError(
                "ZenRows API key required. Set SCITEX_SCHOLAR_ZENROWS_API_KEY env var "
                "or pass zenrows_api_key parameter"
            )
        
        # Session management
        self.zenrows_session_id = None
        self.zenrows_cookies: Dict[str, str] = {}
        
        # CAPTCHA solving
        self._captcha_enabled = enable_captcha_solving and os.getenv("SCITEX_SCHOLAR_2CAPTCHA_API_KEY")
        
        if self._captcha_enabled:
            logger.info("Initialized ZenRows OpenURL resolver with 2Captcha integration")
        else:
            logger.info("Initialized ZenRows OpenURL resolver (API mode)")
    
    def _generate_session_id(self) -> str:
        """Generate session ID for ZenRows (maintains same IP for 10 minutes)."""
        return str(random.randint(1, 10000))
    
    def _parse_cookie_header(self, cookie_header: str) -> Dict[str, str]:
        """Parse cookie header string into dictionary."""
        cookies = {}
        for cookie in cookie_header.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                cookies[name.strip()] = value.strip()
        return cookies
    
    async def _zenrows_request_async(self, url: str) -> Optional[Dict[str, Any]]:
        """Make request through ZenRows API.
        
        Returns:
            Dict with content, final_url, and cookies
        """
        if not self.zenrows_session_id:
            self.zenrows_session_id = self._generate_session_id()
            logger.info(f"Created ZenRows session: {self.zenrows_session_id}")
        
        params = {
            "url": url,
            "apikey": self.zenrows_api_key,
            "js_render": "true",  # Render JavaScript but can't handle auth-required clicks
            "premium_proxy": "true",
            "session_id": self.zenrows_session_id,
            "wait": "3",  # Wait for initial page load
        }
        
        # Add CAPTCHA solving if configured
        if hasattr(self, '_captcha_enabled') and self._captcha_enabled:
            import json
            js_instructions = [
                {"wait": 2000},
                {"solve_captcha": {"type": "recaptcha"}},
                {"wait": 2000},
            ]
            params["js_instructions"] = json.dumps(js_instructions)
        
        # Add cookies if we have them
        headers = {}
        if self.zenrows_cookies:
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.zenrows_cookies.items()])
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=headers if headers else None,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ZenRows request failed: {response.status} - {error_text}")
                        return None
                    
                    content = await response.text()
                    
                    # Extract cookies from response
                    zr_cookies = response.headers.get("Zr-Cookies", "")
                    if zr_cookies:
                        new_cookies = self._parse_cookie_header(zr_cookies)
                        self.zenrows_cookies.update(new_cookies)
                        logger.debug(f"Updated cookies: {len(self.zenrows_cookies)}")
                    
                    # Get final URL after all redirects
                    final_url = response.headers.get("Zr-Final-Url", url)
                    logger.info(f"ZenRows final URL: {final_url}")
                    
                    return {
                        "content": content,
                        "final_url": final_url,
                        "cookies": self.zenrows_cookies,
                        "status": response.status,
                    }
                    
        except Exception as e:
            logger.error(f"ZenRows request error: {e}")
            return None
    
    async def _resolve_single_async(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Resolve URL using ZenRows API."""
        openurl = self.build_openurl(**kwargs)
        doi = kwargs.get("doi", "")
        
        logger.info(f"Resolving via ZenRows API: {openurl}")
        
        # Make request through ZenRows
        result = await self._zenrows_request_async(openurl)
        
        if not result:
            return {
                "final_url": None,
                "resolver_url": openurl,
                "access_type": "zenrows_error",
                "success": False,
            }
        
        final_url = result["final_url"]
        content = result["content"]
        
        # Check if we reached the publisher
        if self._is_publisher_url(final_url, doi):
            logger.info(f"ZenRows reached publisher: {final_url}")
            
            # Check for access indicators
            has_access = self._check_access_indicators(content, final_url)
            
            return {
                "final_url": final_url,
                "resolver_url": openurl,
                "access_type": "zenrows_direct",
                "success": has_access,
                "cookie_count": len(self.zenrows_cookies),
            }
        
        # If still at resolver, try to find the link in content
        if self.resolver_url and self.resolver_url in final_url:
            logger.info("Still at resolver, checking for JavaScript links in content...")
            
            # Simple check for common patterns
            if "javascript:" in content.lower() and doi in content:
                logger.info("Found JavaScript link in content, but ZenRows should have followed it")
                
                # ZenRows with js_render=true should follow JavaScript redirects
                # If we're still at resolver, it might need authentication
                return {
                    "final_url": final_url,
                    "resolver_url": openurl,
                    "access_type": "zenrows_auth_required",
                    "success": False,
                    "note": "JavaScript redirect found but may require authentication"
                }
        
        # No access found
        return {
            "final_url": final_url,
            "resolver_url": openurl,
            "access_type": "zenrows_no_access",
            "success": False,
        }
    
    def _check_access_indicators(self, content: str, url: str) -> bool:
        """Check if content indicates full-text access."""
        content_lower = content.lower()
        
        # Strong access indicators
        strong_access = [
            "download pdf", "view pdf", "pdf download", "get pdf",
            "download article", "access pdf", "open pdf"
        ]
        
        # No access indicators
        no_access = [
            "purchase", "subscribe", "get access", "buy now",
            "institutional login", "sign in to access",
            "authentication required", "please log in"
        ]
        
        # Publisher-specific patterns
        if "nature.com" in url and "full.pdf" in content_lower:
            return True
        if "sciencedirect.com" in url and "pdfft" in content_lower:
            return True
        if "wiley.com" in url and "epdf" in content_lower:
            return True
        
        # Check indicators
        has_strong_access = any(phrase in content_lower for phrase in strong_access)
        has_no_access = any(phrase in content_lower for phrase in no_access)
        
        return has_strong_access and not has_no_access
    
    def reset_session(self):
        """Reset ZenRows session (new IP and clear cookies)."""
        self.zenrows_session_id = None
        self.zenrows_cookies = {}
        logger.info("ZenRows session reset")
    
    async def close(self):
        """Clean up (for compatibility with base class)."""
        self.reset_session()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Convenience function for testing
async def test_zenrows_openurl_resolver():
    """Test the ZenRows API-based OpenURL resolver."""
    from ..auth import AuthenticationManager
    
    # Enable logging
    logging.getLogger("scitex.scholar").setLevel(logging.INFO)
    
    # Initialize
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    
    # Test resolver with CAPTCHA solving enabled
    async with ZenRowsOpenURLResolver(
        auth_manager,
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        enable_captcha_solving=True
    ) as resolver:
        
        # Test 1: Nature paper
        print("\n=== Test 1: Nature paper ===")
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
            if result.get('note'):
                print(f"Note: {result['note']}")
        
        # Test 2: PNAS paper (known anti-bot issues)
        print("\n=== Test 2: PNAS paper (anti-bot) ===")
        result = await resolver._resolve_single_async(
            doi="10.1073/pnas.0608765104",
            title="PNAS paper with anti-bot detection",
            journal="PNAS",
            year=2007
        )
        
        if result:
            print(f"Success: {result['success']}")
            print(f"Final URL: {result.get('final_url')}")
            print(f"Access type: {result.get('access_type')}")
            print(f"Cookies collected: {result.get('cookie_count', 0)}")
    
    # No need to close auth_manager


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_zenrows_openurl_resolver())

# python -m scitex.scholar.open_url._ZenRowsOpenURLResolver

# EOF