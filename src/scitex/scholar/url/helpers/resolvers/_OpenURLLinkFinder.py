#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:13:53 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/resolvers/_OpenURLLinkFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/resolvers/_OpenURLLinkFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import logging
from typing import List

from playwright.async_api import Locator, Page

from scitex.scholar import ScholarConfig
from scitex.scholar.browser.utils import (
    click_and_wait,
    highlight_element,
    take_screenshot,
)

logger = logging.getLogger(__name__)


class OpenURLLinkFinder:
    """Finds full-text links on resolver pages by publisher name."""

    def __init__(self, config: ScholarConfig = None):
        self.config = config or ScholarConfig()

    async def find_link_elements(self, page: Page, doi: str) -> List[Locator]:
        """Find and highlight publisher text on the page."""
        try:
            logger.info(f"Finding links from {page.url}")

            openurl_available_from_patterns = self.config.resolve(
                "openurl_available_from_patterns", None
            )
            seen_hrefs = set()
            found_links = []

            for pattern in openurl_available_from_patterns:
                publisher = pattern[len("Available from ") :]
                try:
                    link_element = page.locator(
                        f'a:has-text("{publisher}")'
                    ).first
                    if await link_element.count() > 0:
                        href = await link_element.get_attribute("href")
                        if href not in seen_hrefs:
                            # logger.success(f"Found link elements for: {publisher}")
                            await highlight_element(link_element, 500)
                            found_links.append(
                                {
                                    "publisher": publisher,
                                    "link_element": link_element,
                                }
                            )
                            seen_hrefs.add(href)
                except Exception as e:
                    logger.debug(f"Could not find {publisher}: {e}")

            if found_links:
                publishers = [
                    found_link.get("publisher") for found_link in found_links
                ]
                logger.success(
                    f"Found {len(publishers)} link elements for: {', '.join(publishers)}"
                )
                return found_links

        except Exception as e:
            logger.fail(
                f"OpenURLLinkFinder did not find any urls from {page.url}: {e}"
            )
            return []


if __name__ == "__main__":

    async def main():
        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )

        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode="interactive",
            chrome_profile_name="system",
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        page = await context.new_page()
        url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1126/science.aao0702"
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(3000)

        finder = OpenURLLinkFinder()
        links = await finder.find_link_elements(
            page, "10.1126/science.aao0702"
        )

        result = await click_and_wait(links[0].get("link_element"))

    asyncio.run(main())

# python -m scitex.scholar.url.helpers.resolvers._OpenURLLinkFinder

# EOF
