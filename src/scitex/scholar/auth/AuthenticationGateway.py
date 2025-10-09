#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 03:24:07 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/AuthenticationGateway.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/AuthenticationGateway.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Authentication Gateway Pattern for Scholar Module

Provides transparent authentication layer that:
- Determines if URL requires authentication (config-based)
- Prepares authenticated browser context before URL finding
- Visits authentication gateways (OpenURL) to establish sessions
- Caches authentication state to avoid redundant operations

This keeps URL finders and PDF downloaders free of authentication logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


@dataclass
class URLContext:
    """
    Context for URL operations with authentication information.

    This dataclass carries all information needed for URL resolution
    and PDF download, including authentication state.
    """

    doi: str
    title: Optional[str] = None
    url: Optional[str] = None  # Publisher landing page URL
    pdf_urls: List[str] = field(default_factory=list)
    requires_auth: Optional[bool] = None
    auth_provider: Optional[str] = None  # openathens, ezproxy, shibboleth
    auth_gateway_url: Optional[str] = None  # OpenURL for establishing session


class AuthenticationGateway:
    """
    Transparent authentication layer for Scholar operations.

    Responsibilities:
    - Determine if URL requires authentication (config-based, no hardcoding)
    - Prepare authenticated browser context
    - Visit authentication gateways (OpenURL) to establish publisher sessions
    - Cache authentication state for performance

    This gateway sits between Scholar and URL/Download operations,
    preparing authentication transparently before content access.
    """

    @property
    def name(self):
        return self.__class__.__name__

    def __init__(
        self,
        auth_manager,  # ScholarAuthManager
        browser_manager,  # ScholarBrowserManager
        config: ScholarConfig = None,
    ):
        """
        Initialize authentication gateway.

        Args:
            auth_manager: ScholarAuthManager instance
            browser_manager: ScholarBrowserManager instance
            config: ScholarConfig instance
        """
        self.auth_manager = auth_manager
        self.browser_manager = browser_manager
        self.config = config or ScholarConfig()
        self._auth_cache: Dict[str, bool] = {}  # Cache visited gateways

    async def prepare_context_async(
        self, doi: str, context: BrowserContext, title: Optional[str] = None
    ) -> URLContext:
        """
        Prepare URL context with authentication if needed.

        This is the main entry point - called BEFORE URL finding.

        Flow:
        1. Build OpenURL (authentication gateway)
        2. Check if DOI needs authentication (based on known publishers)
        3. If auth needed: Visit OpenURL to establish publisher cookies
        4. Resolve to final publisher URL
        5. Return prepared context with authenticated session

        Args:
            doi: Paper DOI
            context: Browser context (will be updated with auth cookies)
            title: Optional paper title

        Returns:
            URLContext with authentication prepared and ready
        """
        url_context = URLContext(doi=doi, title=title)

        # Step 1: Build OpenURL
        from scitex.scholar.url.helpers.resolvers._OpenURLResolver import (
            OpenURLResolver,
        )

        resolver = OpenURLResolver(config=self.config)
        openurl = resolver._build_query(url_context.doi)
        url_context.auth_gateway_url = openurl

        # Step 2: Try to determine if auth needed from DOI patterns
        # (IEEE DOIs start with 10.1109, Springer with 10.1007, etc.)
        url_context = self._check_auth_requirements_from_doi(url_context)

        # Step 3: If authentication needed, visit OpenURL and establish cookies
        # This also resolves to the publisher URL as a side effect
        if url_context.requires_auth:
            publisher_url = await self._establish_authentication_async(
                url_context, context
            )
            url_context.url = publisher_url or openurl
        else:
            # Step 4: For open access, just resolve to publisher URL
            page = await context.new_page()
            try:
                publisher_url = await resolver.resolve_doi(
                    url_context.doi, page
                )
                url_context.url = publisher_url
                logger.debug(
                    f"{self.name}: Resolved {url_context.doi} → {publisher_url}"
                )
            except Exception as e:
                logger.warning(
                    f"{self.name}: Failed to resolve DOI {url_context.doi}: {e}"
                )
                url_context.url = openurl  # Fallback to OpenURL
            finally:
                await page.close()

        return url_context

    async def _resolve_publisher_url_async(
        self, url_context: URLContext, context: BrowserContext
    ) -> URLContext:
        """
        Resolve DOI to publisher landing page URL.

        Uses OpenURLResolver which already exists and works.
        The OpenURL is the authentication gateway for paywalled content.

        Args:
            url_context: URLContext with DOI
            context: Browser context

        Returns:
            URLContext with url and auth_gateway_url populated
        """
        from scitex.scholar.url.helpers.resolvers._OpenURLResolver import (
            OpenURLResolver,
        )

        resolver = OpenURLResolver(config=self.config)

        # Build OpenURL (this is the authentication gateway)
        # Use the private _build_query method since no public method exists
        openurl = resolver._build_query(url_context.doi)
        url_context.auth_gateway_url = openurl

        # Resolve to publisher URL (may redirect through OpenAthens)
        page = await context.new_page()
        try:
            publisher_url = await resolver.resolve_doi(url_context.doi, page)
            url_context.url = publisher_url
            logger.debug(
                f"{self.name}: Resolved {url_context.doi} → {publisher_url}"
            )
        except Exception as e:
            logger.warning(
                f"{self.name}: Failed to resolve DOI {url_context.doi}: {e}"
            )
            url_context.url = openurl  # Fallback to OpenURL
        finally:
            await page.close()

        return url_context

    def _check_auth_requirements_from_doi(
        self, url_context: URLContext
    ) -> URLContext:
        """
        Determine if DOI requires authentication based on DOI prefix patterns.

        This allows early detection before resolving URL.
        IEEE DOIs start with 10.1109, Springer with 10.1007, etc.

        Args:
            url_context: URLContext with doi populated

        Returns:
            URLContext with requires_auth and auth_provider populated
        """
        # Get authenticated publishers from config
        # auth_config = self.config.get("authentication") or {}
        # paywalled_publishers = auth_config.get("paywalled_publishers") or []
        paywalled_publishers = self.config.resolve(
            "paywalled_publishers", None, default=[]
        )

        doi = url_context.doi or ""

        for publisher_config in paywalled_publishers:
            doi_prefixes = publisher_config.get("doi_prefixes", [])
            for prefix in doi_prefixes:
                if doi.startswith(prefix):
                    url_context.requires_auth = True
                    url_context.auth_provider = publisher_config.get(
                        "preferred_provider", "openathens"
                    )
                    logger.info(
                        f"{self.name}: Authentication required for {publisher_config.get('name')} "
                        f"(DOI prefix: {prefix}, provider: {url_context.auth_provider})"
                    )
                    return url_context

        # Fallback: check by URL if DOI detection didn't match
        # (for cases where DOI prefix is not in config)
        url_context.requires_auth = False
        return url_context

    def _check_auth_requirements(self, url_context: URLContext) -> URLContext:
        """
        Determine if URL requires authentication based on config.

        This is config-based (no hardcoded domain lists).
        Checks URL against paywalled_publishers in config.

        Args:
            url_context: URLContext with url populated

        Returns:
            URLContext with requires_auth and auth_provider populated
        """
        # Get authenticated publishers from config
        # auth_config = self.config.get("authentication") or {}
        # paywalled_publishers = auth_config.get("paywalled_publishers") or []
        paywalled_publishers = self.config.resolve(
            "paywalled_publishers", None, default=[]
        )

        # Check if URL matches any paywalled publisher
        url_lower = (url_context.url or "").lower()

        for publisher_config in paywalled_publishers:
            domain_patterns = publisher_config.get("domain_patterns", [])
            for pattern in domain_patterns:
                if pattern.lower() in url_lower:
                    url_context.requires_auth = True
                    url_context.auth_provider = publisher_config.get(
                        "preferred_provider", "openathens"
                    )
                    logger.info(
                        f"{self.name}: Authentication required for {publisher_config.get('name')} "
                        f"(provider: {url_context.auth_provider})"
                    )
                    return url_context

        # No authentication required
        url_context.requires_auth = False
        return url_context

    async def _establish_authentication_async(
        self, url_context: URLContext, context: BrowserContext
    ) -> Optional[str]:
        """
        Establish authentication by visiting gateway URL and clicking through to publisher.

        This is the KEY OPERATION that solves the IEEE issue:
        1. Visit OpenURL (library resolver)
        2. Find publisher link on resolver page
        3. Click link → redirects through OpenAthens → lands at publisher
        4. Publisher session cookies established in browser context

        Without this step:
        - OpenAthens cookies exist at openathens.net
        - NO cookies exist at ieee.org
        - Chrome PDF viewer opens but download fails

        With this step:
        - Visit OpenURL
        - Click IEEE link → redirect through OpenAthens
        - Land at ieee.org → IEEE session cookies established
        - Now ieee.org has cookies, Chrome PDF viewer works

        Args:
            url_context: URLContext with auth_gateway_url and doi
            context: Browser context (will receive publisher cookies)

        Returns:
            Publisher URL if successful, None otherwise
        """
        gateway_url = url_context.auth_gateway_url

        if not gateway_url:
            logger.warning(
                f"{self.name}: No gateway URL available for authentication"
            )
            return None

        # Check cache - avoid redundant visits
        cache_key = f"{url_context.doi}"
        if cache_key in self._auth_cache:
            logger.debug(
                f"{self.name}: Authentication already established for {url_context.doi}"
            )
            # Return cached URL if available
            return self._auth_cache.get(f"{cache_key}_url")

        logger.info(
            f"{self.name}: Establishing auth via OpenURL",
        )

        # Visit OpenURL and click through to publisher
        # This uses the existing OpenURLResolver flow
        from scitex.browser import browser_logger
        from scitex.scholar.url.helpers.resolvers._OpenURLResolver import (
            OpenURLResolver,
        )

        resolver = OpenURLResolver(config=self.config)
        page = await context.new_page()

        try:
            # Show visual progress
            await browser_logger.info(
                page,
                f"{self.name}: Establishing session for {url_context.doi[:50]}...",
            )

            # resolve_doi already does the full flow:
            # 1. Visits OpenURL
            # 2. Finds publisher link
            # 3. Clicks link
            # 4. Waits for publisher page to load
            # This establishes the publisher cookies
            publisher_url = await resolver.resolve_doi(url_context.doi, page)

            if publisher_url:
                logger.success(f"{self.name}: Auth established")
                await browser_logger.info(
                    page,
                    f"{self.name}: ✓ Session established at {publisher_url[:60]}",
                )
                await page.wait_for_timeout(2000)
                # Cache successful authentication
                self._auth_cache[cache_key] = True
                self._auth_cache[f"{cache_key}_url"] = publisher_url
                return publisher_url
            else:
                logger.warning(f"{self.name}: OpenURL resolution failed")
                await browser_logger.info(
                    page, f"{self.name}: ✗ Could not resolve to publisher URL"
                )
                await page.wait_for_timeout(2000)
                return None

        except Exception as e:
            logger.warning(f"{self.name}: Auth setup failed: {e}")
            try:
                await browser_logger.info(
                    page, f"{self.name}: ✗ EXCEPTION: {str(e)[:80]}"
                )
                await page.wait_for_timeout(2000)
            except:
                pass
            # Don't raise - allow downstream to try anyway
            return None
        finally:
            await page.close()


async def main_async():
    """
    Demonstration of AuthenticationGateway usage.

    Shows how to:
    1. Initialize authentication components
    2. Prepare authenticated browser context
    3. Use the context for subsequent operations
    """
    from scitex.scholar.auth.ScholarAuthManager import ScholarAuthManager
    from scitex.scholar.browser.ScholarBrowserManager import (
        ScholarBrowserManager,
    )
    from scitex.scholar.config import ScholarConfig

    # Initialize components
    config = ScholarConfig()
    auth_manager = ScholarAuthManager(config=config)
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager, config=config
    )

    # Initialize gateway
    gateway = AuthenticationGateway(
        auth_manager=auth_manager,
        browser_manager=browser_manager,
        config=config,
    )

    # Example DOIs - one paywalled (IEEE), one open access
    test_dois = [
        "10.1109/JBHI.2024.1234567",  # IEEE (paywalled)
        "10.1088/1741-2552/aaf92e",  # IOP Publishing (paywalled)
        "10.1038/s41467-020-12345-6",  # Nature Communications (open access)
    ]

    # Get authenticated browser context
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    try:
        for doi in test_dois:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing DOI: {doi}")
            logger.info(f"{'='*60}")

            # Prepare authentication (this is the key operation)
            url_context = await gateway.prepare_context_async(
                doi=doi, context=context
            )

            # Show results
            logger.info(f"Publisher URL: {url_context.url}")
            logger.info(f"Requires auth: {url_context.requires_auth}")
            logger.info(f"Auth provider: {url_context.auth_provider}")
            logger.info(f"Gateway URL: {url_context.auth_gateway_url}")

            # At this point, the browser context has publisher cookies
            # You can now use it for URL finding or PDF download

    finally:
        await context.close()
        await browser.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main_async())

# EOF
