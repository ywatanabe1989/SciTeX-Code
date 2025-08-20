#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 09:21:09 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/resolvers/_OpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/resolvers/_OpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Optional
from urllib.parse import quote

from playwright.async_api import Locator, Page

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.utils import (
    click_and_wait,
    show_popup_message_async,
    take_screenshot,
)

from ._OpenURLLinkFinder import OpenURLLinkFinder

logger = logging.getLogger(__name__)


class OpenURLResolver:
    """Handles OpenURL resolution and authentication flow."""

    def __init__(self, config: ScholarConfig = None):
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

        return f"{self.resolver_url}?{'&'.join(params)}"

    async def _resolve_query(
        self, query: str, page: Page, doi: str
    ) -> Optional[str]:
        """Resolve OpenURL query to final authenticated URL."""
        logger.info(f"OpenURLResolver query URL: {query}")
        try:
            await page.goto(
                query, wait_until="domcontentloaded", timeout=60000
            )
            await show_popup_message_async(
                page, "Resolving authenticated URL by OpenURL..."
            )
            await page.wait_for_timeout(3000)

            # Use find_link_element to get a Locator object
            found_links = await self.finder.find_link_elements(page, doi)

            if not found_links:
                return None

            for found_link in found_links:

                publisher = found_link.get("publisher")
                link_element = found_link.get("link_element")

                result = await click_and_wait(
                    link_element,
                    f"Clicking {publisher} link for {doi[:20]}...",
                )
                if result.get("success"):
                    return result.get("final_url")

        except Exception as e:
            logger.error(f"OpenURL resolution failed: {e}")
            await take_screenshot(
                page, "OpenURLResolver", f"{doi} - query not resolved"
            )

        return None

    # def _is_publisher_destination(self, url: str, doi: str) -> bool:
    #     """Check if URL is valid publisher destination."""
    #     doi_match = re.match(r"(10\.\d{4,})", doi)
    #     if not doi_match:
    #         return True

    #     prefix = doi_match.group(1)
    #     expected_domains = self.finder.doi_to_domain.get(prefix, [])

    #     if not expected_domains:
    #         return True

    #     return any(domain in url for domain in expected_domains)

    # async def _handle_abstract_page(self, page: Page) -> Optional[str]:
    #     """Handle abstract pages by finding PDF view button."""
    #     await show_popup_message_async(page, "Handling abstract page...")
    #     current_url = page.url

    #     if "/abs/" in current_url or "abstract" in current_url:
    #         logger.info(
    #             "Detected abstract page, looking for PDF view button..."
    #         )

    #         pdf_selectors = self.config.resolve(
    #             "pdf_view_selectors",
    #             default=[
    #                 'a:has-text("View PDF")',
    #                 'a:has-text("PDF")',
    #                 'a[href*="/pdf/"]',
    #             ],
    #         )

    #         for selector in pdf_selectors:
    #             try:
    #                 # Use Playwright's Locator API instead of query_selector
    #                 pdf_link = page.locator(selector).first
    #                 if (
    #                     await pdf_link.count() > 0
    #                     and await pdf_link.is_visible()
    #                 ):
    #                     href = await pdf_link.get_attribute("href")
    #                     if href and "pdf" in href.lower():
    #                         logger.info("Found PDF view link, clicking...")
    #                         await pdf_link.click()
    #                         await page.wait_for_load_state(
    #                             "domcontentloaded", timeout=15000
    #                         )
    #                         await page.wait_for_timeout(2000)
    #                         return page.url
    #             except:
    #                 continue

    #     return current_url


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

# python -m scitex.scholar.url.helpers.resolvers._OpenURLResolver

# EOF
