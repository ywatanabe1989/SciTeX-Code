#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 07:52:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/gateway/_OpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/gateway/_OpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from typing import Optional
from urllib.parse import quote

from playwright.async_api import Locator, Page

from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.utils import click_and_wait

from ._OpenURLLinkFinder import OpenURLLinkFinder

logger = logging.getLogger(__name__)


class OpenURLResolver:
    """Handles OpenURL resolution and authentication flow."""

    def __init__(self, config: ScholarConfig = None):
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()
        self.resolver_url = self.config.resolve("openurl_resolver_url")
        self.finder = OpenURLLinkFinder(config=config)

    async def resolve_doi(self, doi: str, page: Page) -> Optional[str]:
        """Main entry point: resolve DOI through OpenURL to authenticated URL."""
        openurl_query = self._build_query(doi)
        if not openurl_query:
            return None
        return await self._resolve_query(openurl_query, page, doi)

    def _build_query(self, doi: str, title: str = None) -> Optional[str]:
        """Build OpenURL query string."""
        if not self.resolver_url:
            return None

        params = [f"doi={doi}"]
        if title:
            params.append(f"atitle={quote(title[:200])}")

        built_query = f"{self.resolver_url}?{'&'.join(params)}"
        logger.debug(f"{self.name}: Built query URL: {built_query}")
        return built_query

    async def _resolve_query(
        self, query: str, page: Page, doi: str
    ) -> Optional[str]:
        """Resolve OpenURL query to final authenticated URL with retry."""
        logger.debug(f"{self.name}: Resolving query URL: {query}...")

        for attempt in range(3):
            try:
                # DEBUG: Check page status before navigation
                logger.info(f"DEBUG [{self.name}]: BEFORE page.goto()")
                logger.info(f"  Page is closed: {page.is_closed()}")
                logger.info(f"  Query URL: {query[:80]}")
                logger.info(f"  Attempt: {attempt + 1}/3")

                # Visual: Navigating to OpenURL
                await browser_logger.debug(
                    page,
                    f"{self.name}: Navigating to resolver for {doi[:30]}...",
                )

                logger.info(f"DEBUG [{self.name}]: CALLING page.goto()...")
                await page.goto(
                    query, wait_until="domcontentloaded", timeout=60000
                )
                logger.info(f"DEBUG [{self.name}]: AFTER page.goto() SUCCESS")
                await browser_logger.debug(
                    page,
                    f"{self.name}: Loaded resolver page at {page.url[:60]}",
                )

                # Visual: Waiting for page to stabilize
                await browser_logger.debug(
                    page,
                    f"{self.name}: Waiting for resolver to load (networkidle)...",
                )
                try:
                    await page.wait_for_load_state(
                        "networkidle", timeout=15_000
                    )
                    await browser_logger.debug(
                        page, f"{self.name}: ✓ Resolver page ready"
                    )
                except Exception:
                    await browser_logger.info(
                        page, f"{self.name}: Page still loading, continuing..."
                    )
                await page.wait_for_timeout(1000)

                # Visual: Finding publisher links
                await browser_logger.info(
                    page, f"{self.name}: Searching for publisher links..."
                )
                found_links = await self.finder.find_link_elements(page, doi)

                if not found_links:
                    await browser_logger.info(
                        page, f"{self.name}: No publisher links found"
                    )
                    await page.wait_for_timeout(2000)
                    return None

                # Visual: Found links
                await browser_logger.debug(
                    page,
                    f"{self.name}: Found {len(found_links)} publisher link(s)",
                )
                await page.wait_for_timeout(1000)

                # Visual: Try each publisher link
                for i, found_link in enumerate(found_links, 1):
                    publisher = found_link.get("publisher")
                    link_element = found_link.get("link_element")

                    await browser_logger.debug(
                        page,
                        f"{self.name}: Clicking {publisher} link ({i}/{len(found_links)})...",
                    )

                    result = await click_and_wait(
                        link_element,
                        f"Clicking {publisher} link for {doi[:20]}...",
                    )

                    if result.get("success"):
                        final_url = result.get("final_url")
                        await browser_logger.success(
                            page,
                            f"{self.name}: ✓ Landed at {final_url[:60]}",
                        )
                        await page.wait_for_timeout(2000)
                        return final_url
                    else:
                        await browser_logger.info(
                            page,
                            f"{self.name}: ✗ {publisher} link failed, trying next...",
                        )
                        await page.wait_for_timeout(1000)

                # All links failed
                await browser_logger.info(
                    page, f"{self.name}: ✗ All publisher links failed"
                )
                await page.wait_for_timeout(2000)
                return None

            except Exception as e:
                if attempt < 2:
                    wait_time = (attempt + 1) * 2
                    logger.warning(
                        f"OpenURL attempt {attempt + 1} failed: {e}, retrying in {wait_time}s"
                    )
                    await browser_logger.info(
                        page,
                        f"{self.name}: ✗ Attempt {attempt + 1} failed, retrying in {wait_time}s...",
                    )
                    await page.wait_for_timeout(wait_time * 1000)
                    continue
                else:
                    logger.error(
                        f"OpenURL resolution failed after 3 attempts: {e}"
                    )
                    await browser_logger.info(
                        page,
                        f"{self.name}: ✗ FAILED after 3 attempts: {str(e)[:80]}",
                    )
                    await page.wait_for_timeout(2000)
                    await browser_logger.info(
                        page, f"{self.name}: f{doi} - query not resolved"
                    )
                    return None


if __name__ == "__main__":
    import asyncio

    from scitex.scholar import ScholarAuthManager, ScholarBrowserManager

    async def main():
        # Initialize browser with authentication
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode="stealth",
            chrome_profile_name="system",
        )

        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        page = await context.new_page()

        # Test OpenURL resolver
        resolver = OpenURLResolver()
        doi = "10.1126/science.aao0702"

        resolved_url = await resolver.resolve_doi(doi, page)

        await browser.close()

    asyncio.run(main())

# python -m scitex.scholar.auth.gateway._OpenURLResolver

# EOF
