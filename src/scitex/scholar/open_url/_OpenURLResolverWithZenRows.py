#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 00:59:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_OpenURLResolverWithZenRows.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_OpenURLResolverWithZenRows.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""OpenURL resolver with ZenRows integration for bypassing bot detection.

This implementation uses the correct cookie handling approach based on ZenRows FAQ:
1. Cookies are returned in Zr-Cookies response header
2. Use session_id to maintain same IP for 10 minutes
3. Send cookies as Custom Headers in subsequent requests
"""

import asyncio
import random
import uuid
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp

from scitex import logging

from ...errors import ScholarError
from ._OpenURLResolver import OpenURLResolver

logger = logging.getLogger(__name__)


class OpenURLResolverWithZenRows(OpenURLResolver):
    """OpenURL resolver enhanced with ZenRows anti-bot bypass capabilities.
    
    This resolver uses ZenRows to bypass anti-bot detection and rate limits.
    However, it has limitations with institutional authentication:
    
    Limitations:
        - Cannot fully replicate browser-based authentication flows
        - Institutional cookies (e.g., OpenAthens) don't transfer to publisher domains
        - Shows "Purchase" options instead of "Download PDF" for paywalled content
        
    Best used for:
        - Open access content detection
        - Bypassing anti-bot measures on public content
        - High-volume URL resolution
        
    For authenticate_async access to paywalled content, use the standard OpenURLResolver
    which handles the full authentication flow through a real browser.
    """

    def __init__(
        self,
        auth_manager,
        resolver_url: str,
        zenrows_api_key: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_API_KEY"
        ),
        use_browser_cookies: bool = True,
    ):
        """Initialize resolver with optional ZenRows support.

        Args:
            auth_manager: Authentication manager
            resolver_url: Base URL of institutional OpenURL resolver
            zenrows_api_key: ZenRows API key (uses env var if not provided)
            use_browser_cookies: If True, attempts to get publisher cookies via browser first
        """
        super().__init__(auth_manager, resolver_url)

        self.zenrows_api_key = zenrows_api_key
        self.use_browser_cookies = use_browser_cookies
        
        if self.zenrows_api_key:
            logger.info(f"ZenRows API key loaded (length: {len(self.zenrows_api_key)})")
        else:
            logger.warning("No ZenRows API key provided")

        # Session management for ZenRows
        self.zenrows_session_id = None
        self.zenrows_cookies: Dict[str, str] = {}
        self._last_page_content = None  # For debugging

    def _generate_session_id(self) -> str:
        """Generate unique session ID for maintaining same IP in ZenRows."""
        # ZenRows requires numeric session_id with max value of 10000
        import random

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

    async def _zenrows_request_async(
        self, url: str, use_cookies: bool = True, auth_cookies: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make request through ZenRows API with proper cookie handling.

        Args:
            url: Target URL
            use_cookies: Whether to include stored cookies
            auth_cookies: Optional authentication cookies from auth_manager

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
            "wait": "5",  # Wait for page to load
        }

        # Merge auth cookies with session cookies
        request_cookies = self.zenrows_cookies.copy()
        if auth_cookies:
            request_cookies.update(auth_cookies)
            logger.info(f"Added {len(auth_cookies)} auth cookies to request")

        headers = {}
        if use_cookies and request_cookies:
            # Send cookies as HTTP headers with custom_headers=true
            cookie_string = "; ".join(
                [f"{k}={v}" for k, v in request_cookies.items()]
            )
            headers["Cookie"] = cookie_string
            params["custom_headers"] = "true"
            logger.info(f"Sending {len(request_cookies)} total cookies")

        try:
            async with aiohttp.ClientSession() as session:
                # If we have custom headers, we need to send them separately
                request_headers = headers if headers else None
                
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    headers=request_headers,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"ZenRows request failed: {response.status}\n"
                            f"Error: {error_text}"
                        )
                        return None

                    content = await response.text()
                    
                    # Store for debugging
                    self._last_page_content = content

                    # Extract cookies from response headers
                    zr_cookies = response.headers.get("Zr-Cookies", "")
                    if zr_cookies:
                        new_cookies = self._parse_cookie_header(zr_cookies)
                        self.zenrows_cookies.update(new_cookies)
                        logger.debug(
                            f"Updated cookies, total: {len(self.zenrows_cookies)}"
                        )

                    # Get final URL
                    final_url = response.headers.get("Zr-Final-Url", url)

                    return {
                        "content": content,
                        "final_url": final_url,
                        "cookies": self.zenrows_cookies,
                        "status": response.status,
                    }

        except Exception as e:
            logger.error(f"ZenRows request error: {e}")
            return None

    async def _get_all_browser_cookies_async(self) -> Dict[str, str]:
        """Get all cookies from authenticate_async browser context."""
        try:
            if not self.auth_manager or not await self.auth_manager.is_authenticate_async():
                return {}
            
            # Get all cookies from the authenticate_async browser context
            browser, context = await self.browser.get_authenticate_async_context()
            cookies = await context.cookies()
            
            # Convert to simple dict
            all_cookies = {}
            for cookie in cookies:
                all_cookies[cookie['name']] = cookie['value']
            
            logger.info(f"Retrieved {len(all_cookies)} total cookies from browser context")
            
            # Log domains for debugging
            domains = set(cookie.get('domain', '') for cookie in cookies)
            logger.debug(f"Cookie domains: {domains}")
            
            return all_cookies
            
        except Exception as e:
            logger.error(f"Failed to get browser cookies: {e}")
            return {}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    async def _resolve_single_async_zenrows_async(
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
        """Resolve using ZenRows with authenticate_async cookies through OpenURL."""

        if not self.resolver_url:
            logger.warning("No OpenURL resolver URL configured")
            return None

        # Build OpenURL
        openurl = self.build_openurl(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )

        logger.info(f"Resolving via ZenRows: {openurl}")

        # Get ALL cookies from authenticate_async browser context
        auth_cookies_dict = {}
        if self.use_browser_cookies and self.auth_manager and await self.auth_manager.is_authenticate_async():
            logger.info("Getting all cookies from authenticate_async browser context...")
            auth_cookies_dict = await self._get_all_browser_cookies_async()
        elif self.auth_manager and await self.auth_manager.is_authenticate_async():
            logger.info("Getting OpenAthens cookies...")
            try:
                auth_cookies_list = await self.auth_manager.get_auth_cookies_async()
                auth_cookies_dict = {c['name']: c['value'] for c in auth_cookies_list}
                logger.info(f"Successfully loaded {len(auth_cookies_dict)} auth cookies.")
            except Exception as e:
                logger.error(f"Failed to get auth cookies: {e}")

        # CORRECT FLOW: Access OpenURL with authenticate_async cookies via ZenRows
        # This handles bot detection while maintaining authentication
        result = await self._zenrows_request_async(openurl, use_cookies=True, auth_cookies=auth_cookies_dict)

        if not result:
            logger.error("Failed to access OpenURL resolver")
            return None

        content = result["content"]
        final_url = result["final_url"]

        # Check if we're still at the resolver
        if self.resolver_url and self.resolver_url in final_url:
            logger.info("Still at institutional resolver, looking for links...")
            # Try to find and follow institutional access links
            if "full text" in content.lower() or "get it" in content.lower():
                logger.info("Found potential access links at resolver")
                # In a real implementation, we would parse and follow these links
                # For now, we'll note this as a limitation
                return {
                    "final_url": final_url,
                    "resolver_url": openurl,
                    "access_type": "resolver_with_links",
                    "success": False,
                    "note": "Resolver show_asyncs links but ZenRows cannot follow interactive elements"
                }
        
        # Check if we reached publisher directly
        elif self._is_publisher_url(final_url, doi):
            logger.info(f"Reached publisher directly: {final_url}")

            # Check for access
            access_indicators = [
                "full text", "download_async pdf", "view pdf", "pdf download_async",
                "article pdf", "get pdf", "download_async article", "read the full",
                "access pdf", "open pdf", "full article", "read online",
                "download_async full", "view full text", "read full text"
            ]
            no_access_indicators = [
                "purchase", "subscribe", "get access", "buy now",
                "request access", "institutional login", "sign in to access",
                "paywall", "subscription required", "access denied",
                "please log in", "authentication required", "members only",
                "preview of subscription content", "buy or subscribe"
            ]
            
            # Also check for specific publisher patterns
            nature_access = "nature.com" in final_url and "full.pdf" in content.lower()
            elsevier_access = "sciencedirect.com" in final_url and "pdfft" in content.lower()
            wiley_access = "wiley.com" in final_url and "epdf" in content.lower()
            
            # More nuanced access detection
            # If we find strong access indicators, we likely have access even if purchase options exist
            strong_access_indicators = [
                "download_async pdf", "view pdf", "pdf download_async", "get pdf",
                "download_async article", "access pdf", "open pdf"
            ]
            critical_no_access = [
                "preview of subscription content", "access denied",
                "authentication required", "please log in"
            ]
            
            has_strong_access = any(phrase in content.lower() for phrase in strong_access_indicators)
            has_critical_no_access = any(phrase in content.lower() for phrase in critical_no_access)
            has_any_access = any(phrase in content.lower() for phrase in access_indicators)
            
            # Access is likely if:
            # 1. Strong access indicators present AND no critical blockers
            # 2. Publisher-specific patterns detected
            # 3. We reached publisher URL (implicit access check)
            has_access = (
                (has_strong_access and not has_critical_no_access) or
                nature_access or elsevier_access or wiley_access or
                (has_any_access and not has_critical_no_access and self._is_publisher_url(final_url, doi))
            )

            return {
                "final_url": final_url,
                "resolver_url": openurl,
                "access_type": "direct_zenrows",
                "success": has_access,
                "has_cookies": len(self.zenrows_cookies) > 0,
            }

        # Step 2: Look for full-text links
        # This is simplified - in production would parse HTML properly
        if "no full text available" in content.lower():
            logger.info("No access available")
            return {
                "final_url": None,
                "resolver_url": openurl,
                "access_type": "no_access",
                "success": False,
            }

        # Step 3: If we have cookies, try accessing publisher with them
        if self.zenrows_cookies and doi:
            publisher_url = f"https://doi.org/{doi}"
            logger.info(
                f"Attempting publisher access with cookies: {publisher_url}"
            )

            publisher_result = await self._zenrows_request_async(
                publisher_url, use_cookies=True, auth_cookies=auth_cookies_dict
            )

            if publisher_result:
                final_url = publisher_result["final_url"]
                content = publisher_result["content"]

                # More comprehensive access detection
                access_indicators = [
                    "full text", "download_async pdf", "view pdf", "pdf download_async",
                    "article pdf", "get pdf", "download_async article", "read the full",
                    "access pdf", "open pdf", "full article", "read online",
                    "download_async full", "view full text", "read full text"
                ]
                no_access_indicators = [
                    "purchase", "subscribe", "get access", "buy now",
                    "request access", "institutional login", "sign in to access",
                    "paywall", "subscription required", "access denied",
                    "please log in", "authentication required", "members only",
                    "preview of subscription content", "buy or subscribe"
                ]
                
                # Also check for specific publisher patterns
                nature_access = "nature.com" in final_url and "full.pdf" in content.lower()
                elsevier_access = "sciencedirect.com" in final_url and "pdfft" in content.lower()
                wiley_access = "wiley.com" in final_url and "epdf" in content.lower()
                
                # More nuanced access detection (same logic as above)
                strong_access_indicators = [
                    "download_async pdf", "view pdf", "pdf download_async", "get pdf",
                    "download_async article", "access pdf", "open pdf"
                ]
                critical_no_access = [
                    "preview of subscription content", "access denied",
                    "authentication required", "please log in"
                ]
                
                has_strong_access = any(phrase in content.lower() for phrase in strong_access_indicators)
                has_critical_no_access = any(phrase in content.lower() for phrase in critical_no_access)
                has_any_access = any(phrase in content.lower() for phrase in access_indicators)
                
                has_access = (
                    (has_strong_access and not has_critical_no_access) or
                    nature_access or elsevier_access or wiley_access or
                    (has_any_access and not has_critical_no_access and self._is_publisher_url(final_url, doi))
                )
                
                # Log some debug info
                logger.debug(f"Access detection for {final_url}")
                logger.debug(f"Found access indicators: {[p for p in access_indicators if p in content.lower()]}")
                logger.debug(f"Found no-access indicators: {[p for p in no_access_indicators if p in content.lower()]}")

                # Add authentication suggestion if access is blocked
                suggestion = None
                found_no_access = [p for p in no_access_indicators if p in content.lower()]
                if not has_access and any(
                    phrase in found_no_access 
                    for phrase in ["institutional login", "subscribe", "purchase"]
                ):
                    suggestion = (
                        "Content appears to require institutional authentication. "
                        "Consider using browser-based OpenURLResolver for authenticate_async access."
                    )
                
                return {
                    "final_url": final_url,
                    "resolver_url": openurl,
                    "access_type": "zenrows_with_cookies",
                    "success": has_access,
                    "cookie_count": len(self.zenrows_cookies),
                    "suggestion": suggestion
                }

        # Default response
        return {
            "final_url": final_url,
            "resolver_url": openurl,
            "access_type": "zenrows_attempted",
            "success": False,
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

        if self.zenrows_api_key:
            logger.info("Using ZenRows for resolution")
            return await self._resolve_single_async_zenrows_async(
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
    
    def get_access_details(self, content: str, url: str = "", doi: str = "") -> Dict[str, Any]:
        """Analyze page content for detailed access information."""
        access_indicators = [
            "full text", "download_async pdf", "view pdf", "pdf download_async",
            "article pdf", "get pdf", "download_async article", "read the full",
            "access pdf", "open pdf", "full article", "read online",
            "download_async full", "view full text", "read full text"
        ]
        strong_access_indicators = [
            "download_async pdf", "view pdf", "pdf download_async", "get pdf",
            "download_async article", "access pdf", "open pdf"
        ]
        no_access_indicators = [
            "purchase", "subscribe", "get access", "buy now",
            "request access", "institutional login", "sign in to access",
            "paywall", "subscription required", "access denied",
            "please log in", "authentication required", "members only",
            "preview of subscription content", "buy or subscribe"
        ]
        critical_no_access = [
            "preview of subscription content", "access denied",
            "authentication required", "please log in"
        ]
        
        found_access = [p for p in access_indicators if p in content.lower()]
        found_strong_access = [p for p in strong_access_indicators if p in content.lower()]
        found_no_access = [p for p in no_access_indicators if p in content.lower()]
        found_critical_no_access = [p for p in critical_no_access if p in content.lower()]
        
        # Apply same nuanced logic
        has_access = (
            (len(found_strong_access) > 0 and len(found_critical_no_access) == 0) or
            (len(found_access) > 0 and len(found_critical_no_access) == 0 and 
             url and doi and self._is_publisher_url(url, doi))
        )
        
        return {
            "has_access": has_access,
            "access_indicators_found": found_access,
            "strong_access_indicators_found": found_strong_access,
            "no_access_indicators_found": found_no_access,
            "critical_no_access_found": found_critical_no_access,
            "likely_reason": found_critical_no_access[0] if found_critical_no_access else 
                           (found_no_access[0] if found_no_access else "Unknown")
        }

    async def resolve_async(
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
        """Public method for resolving - delegates to _resolve_single_async."""
        return await self._resolve_single_async(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
    
    async def _resolve_parallel_async(
        self, dois: Union[str, List[str]], concurrency: int = 5
    ) -> List[Optional[Dict[str, Any]]]:
        """Resolves a list of DOIs in parallel with controlled concurrency.

        Args:
            dois: A list of DOI strings to resolve.
            concurrency: Maximum number of concurrent tasks (default: 5)

        Returns:
            A list of result dictionaries, in the same order as the input DOIs.
        """
        if not dois:
            return []

        is_single = False
        if isinstance(dois, str):
            dois = [dois]
            is_single = True

        logger.info(
            f"--- Starting parallel resolution for {len(dois)} DOIs (concurrency: {concurrency}) ---"
        )

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def worker_async(doi):
            async with semaphore:
                # Add random delay between requests to appear more human
                await asyncio.sleep(random.uniform(0.5, 2.0))
                return await self._resolve_single_async(doi=doi)

        # Create tasks using the worker_async function
        tasks = [worker_async(doi) for doi in dois]
        results = await asyncio.gather(*tasks)

        logger.info("--- Parallel resolution finished ---")
        return results[0] if is_single else results

    def _resolve_single(self, **kwargs) -> Optional[str]:
        """Synchronous wrapper for _resolve_single_async."""
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio

            nest_asyncio.apply()
            result = asyncio.run(self._resolve_single_async(**kwargs))
        except RuntimeError:
            # No running loop, create new one
            result = asyncio.run(self._resolve_single_async(**kwargs))

        self._validate_final_url(kwargs.get("doi", ""), result)
        return result.get("resolved_url") if result else None

    def resolve(
        self, dois: Union[str, List[str]], concurrency: int = 5
    ) -> Union[str, List[str]]:
        """Synchronous wrapper for _resolve_parallel_async."""
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio

            nest_asyncio.apply()
            results = asyncio.run(
                self._resolve_parallel_async(dois, concurrency)
            )
        except RuntimeError:
            results = asyncio.run(
                self._resolve_parallel_async(dois, concurrency)
            )

        # Validate results
        dois_list = [dois] if isinstance(dois, str) else dois
        results_list = [results] if not isinstance(results, list) else results
        for doi, result in zip(dois_list, results_list):
            self._validate_final_url(doi, result)

        return results

    def _validate_final_url(self, doi, result):
        """Validate and log the resolution result."""
        if (
            result
            and result.get("success")
            and self._is_publisher_url(result["final_url"], doi=doi)
        ):
            logger.success(f"{doi}: {result['final_url']}")
            result["resolved_url"] = result["final_url"]
            return True
        else:
            final_url = result.get("final_url") if result else "N/A"
            logger.fail(f"{doi}: Landed at {final_url}")
            result["resolved_url"] = None
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup if needed."""
        # Reset ZenRows session on exit if needed
        if self.zenrows_session_id:
            self.reset_zenrows_session()


# Convenience function for testing
async def test_zenrows_resolver_async():
    """Test the ZenRows-enhanced resolver."""
    from ..auth import AuthenticationManager
    import tempfile
    from pathlib import Path

    # Enable debug logging
    logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)

    # Initialize
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    zenrows_api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")

    resolver = OpenURLResolverWithZenRows(
        auth_manager,
        resolver_url,
        zenrows_api_key,
    )

    # Test with a DOI
    result = await resolver._resolve_single_async(
        doi="10.1038/nature12373",
        title="A mesoscale connectome of the mouse brain",
        journal="Nature",
        year=2014,
    )

    if result:
        print(f"\nResolution Result:")
        print(f"  Success: {result['success']}")
        print(f"  Final URL: {result.get('final_url')}")
        print(f"  Access type: {result.get('access_type')}")
        print(f"  Cookies collected: {result.get('cookie_count', 0)}")
        
        # Save debug page if available
        if hasattr(resolver, '_last_page_content') and resolver._last_page_content:
            debug_file = Path(tempfile.gettempdir()) / "zenrows_debug.html"
            debug_file.write_text(resolver._last_page_content)
            print(f"  Debug page saved to: {debug_file}")
    else:
        print("Resolution failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_zenrows_resolver_async())

# python -m scitex.scholar.open_url._OpenURLResolverWithZenRows

# EOF
