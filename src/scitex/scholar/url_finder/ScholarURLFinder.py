#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 04:38:44 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/ScholarURLFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
ScholarURLFinder - Find PDF URLs from web pages.

Simple, focused responsibility: Given a page or URL, find PDF URLs.
"""

from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Union

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar.auth.gateway import OpenURLResolver
from scitex.scholar.config import PublisherRules, ScholarConfig

# Import strategies
from .strategies import (
    find_pdf_urls_by_direct_links,
    find_pdf_urls_by_navigation,
    find_pdf_urls_by_publisher_patterns,
    find_pdf_urls_by_zotero_translators,
)

# Strategy execution order (priority order)
STRATEGIES = [
    # 1. Zotero translators (most reliable)
    {
        "name": "Python Zotero Translators",
        "function": find_pdf_urls_by_zotero_translators,
        "source_label": "zotero_translator",
    },
    # 2. Direct links (combined: href + dropdown)
    {
        "name": "Direct Links",
        "function": find_pdf_urls_by_direct_links,
        "source_label": "direct_link",
    },
    # 3. Navigation (Elsevier only)
    {
        "name": "Navigation",
        "function": find_pdf_urls_by_navigation,
        "source_label": "navigation",
        "publisher_filter": "elsevier",  # Only for Elsevier domains
    },
    # 4. Publisher patterns (fallback)
    {
        "name": "Publisher Patterns",
        "function": find_pdf_urls_by_publisher_patterns,
        "source_label": "publisher_pattern",
    },
]

logger = logging.getLogger(__name__)


class ScholarURLFinder:
    """Find PDF URLs from web pages.

    Simple, focused responsibility:
    - Input: Page or URL string
    - Output: List of PDF URLs

    Authentication/DOI resolution should be handled BEFORE calling this.
    """

    PAGE_LOAD_TIMEOUT = 30_000

    def __init__(
        self,
        context: BrowserContext,
        config: Optional[ScholarConfig] = None,
    ):
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()
        self.context = context
        self.openurl_resolver = OpenURLResolver(config=self.config)

    # ==========================================================================
    # Public API
    # ==========================================================================

    async def find_pdf_urls(
        self, page_or_url: Union[Page, str], base_url: Optional[str] = None
    ) -> List[Dict]:
        """Find PDF URLs from page or URL string.

        Args:
            page_or_url: Playwright Page object or URL string
            base_url: Optional base URL for the page

        Returns:
            List of PDF URL dicts: [{"url": "...", "source": "zotero_translator"}]
        """
        if isinstance(page_or_url, str):
            return await self._find_from_url_string(page_or_url)
        else:
            return await self._find_from_page(page_or_url, base_url)

    # ==========================================================================
    # PDF Finding Implementation
    # ==========================================================================

    async def _find_pdf_urls_with_strategies(
        self, page: Page, base_url: Optional[str] = None
    ) -> List[Dict]:
        """Try strategies in priority order."""
        base_url = base_url or page.url
        n_strategies = len(STRATEGIES)

        for i_strategy, strategy in enumerate(STRATEGIES, 1):
            # Check if strategy should run for this URL
            publisher_filter = strategy.get("publisher_filter")
            if (
                publisher_filter
                and publisher_filter.lower() not in base_url.lower()
            ):
                # logger.debug(
                #     f"{self.name}: Skipping {strategy['name']} (filtered)"
                # )
                continue

            # Log progress
            await browser_logger.info(
                page,
                f"{self.name}: {i_strategy}/{n_strategies} Trying {strategy['name']}",
            )

            try:
                # Execute strategy
                urls = await strategy["function"](page, base_url, self.config)

                if urls:
                    result = self._as_pdf_dicts(urls, strategy["source_label"])
                    await browser_logger.success(
                        page,
                        f"{self.name}: ✓ {strategy['name']} found {len(result)} URLs",
                    )
                    return result

            except Exception as e:
                await browser_logger.debug(
                    page, f"{self.name}: {strategy['name']} failed: {e}"
                )
                continue

        return []

    def _extract_doi(self, url: str) -> Optional[str]:
        """Extract DOI from string if present.

        Args:
            url: URL string or DOI

        Returns:
            DOI string if found, None otherwise

        Examples:
            >>> _extract_doi("10.1038/nature12345")
            "10.1038/nature12345"
            >>> _extract_doi("doi:10.1038/nature12345")
            "10.1038/nature12345"
            >>> _extract_doi("https://example.com")
            None
        """
        import re

        url = url.strip()

        # Already a valid URL - not a DOI
        if url.startswith(("http://", "https://")):
            return None

        # Remove common DOI prefixes
        doi_pattern = r"^(?:doi:\s*|DOI:\s*)?(.+)$"
        match = re.match(doi_pattern, url, re.IGNORECASE)
        if match:
            potential_doi = match.group(1).strip()

            # Check if it looks like a DOI (starts with 10.)
            if potential_doi.startswith("10."):
                return potential_doi

        # If it starts with 10., assume it's a DOI
        if url.startswith("10."):
            return url

        return None

    async def _find_from_url_string(self, url: str) -> List[Dict]:
        """Find PDFs from URL string or DOI."""
        if not self.context:
            logger.error(f"{self.name}: Browser context required")
            return []

        # Check if input is a DOI and resolve it to publisher URL
        doi = self._extract_doi(url)
        if doi:
            logger.info(f"{self.name}: Detected DOI: {doi}")
            async with self._managed_page() as page:
                resolved_url = await self.openurl_resolver.resolve_doi(
                    doi, page
                )
                if resolved_url:
                    logger.info(
                        f"{self.name}: Resolved DOI to: {resolved_url}"
                    )
                    url = resolved_url
                else:
                    # Fallback to direct DOI URL (works for open access papers like arXiv)
                    url = f"https://doi.org/{doi}"
                    logger.info(
                        f"{self.name}: OpenURL failed, using direct DOI URL: {url}"
                    )

        logger.info(f"{self.name}: Finding PDFs from URL: {url}")

        async with self._managed_page() as page:
            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.PAGE_LOAD_TIMEOUT,
                )
                pdfs = await self._find_pdf_urls_with_strategies(page)

                if not pdfs:
                    await browser_logger.warning(
                        page, f"{self.name}: No PDFs from URL: {url[:50]}"
                    )

                return pdfs
            except Exception as e:
                # logger.warning(f"{self.name}: Failed to load page: {e}")
                await browser_logger.error(
                    page, f"{self.name}: Navigation Error {e}"
                )
                return []

    async def _find_from_page(
        self, page: Page, base_url: Optional[str] = None
    ) -> List[Dict]:
        """Find PDFs from existing page."""
        try:
            pdfs = await self._find_pdf_urls_with_strategies(page, base_url)

            if not pdfs:
                await browser_logger.warning(
                    page, f"{self.name}: No PDFs on page"
                )

            return pdfs
        except Exception as e:
            # logger.error(f"{self.name}: Error finding PDFs: {e}")
            await browser_logger.error(
                page, f"{self.name}: PDF Search Error {e}"
            )
            return []

    # ==========================================================================
    # Utilities
    # ==========================================================================

    @asynccontextmanager
    async def _managed_page(self):
        """Context manager for page lifecycle."""
        page = await self.context.new_page()
        try:
            yield page
        finally:
            try:
                await page.close()
            except:
                pass

    def _as_pdf_dicts(self, urls: List[str], source: str) -> List[Dict]:
        """Convert URL strings to dict format with source."""
        return [{"url": url, "source": source} for url in urls]


# ==============================================================================
# CLI
# ==============================================================================


def parse_args():
    """Parse CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Find PDF URLs from a publisher page or DOI"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL or DOI to search for PDFs (e.g., 'https://...' or '10.1038/...' or 'doi:10.1038/...')",
    )
    parser.add_argument(
        "--browser-mode",
        choices=["interactive", "stealth"],
        default="interactive",
    )
    parser.add_argument("--chrome-profile", default="system_worker_0")
    return parser.parse_args()


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from pprint import pprint

        from scitex.scholar import ScholarAuthManager, ScholarBrowserManager

        args = parse_args()

        # Setup auth manager and browser
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode=args.browser_mode,
            chrome_profile_name=args.chrome_profile,
        )
        _, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        # time.sleep(1)

        # Find PDFs
        url_finder = ScholarURLFinder(context)
        pdfs = await url_finder.find_pdf_urls(args.url)

        print(f"\nFound {len(pdfs)} PDF URLs:")
        pprint(pdfs)

        await browser_manager.close()

    asyncio.run(main_async())

"""
# With URL
python -m scitex.scholar.url.ScholarURLFinder \
	--url "https://arxiv.org/abs/2308.09312" \
	--browser-mode stealth

# With DOI
python -m scitex.scholar.url.ScholarURLFinder \
	--url "10.1038/s41598-017-02626-y" \
	--browser-mode stealth

# With doi: prefix
python -m scitex.scholar.url.ScholarURLFinder \
	--url "doi:10.3389/fnins.2024.1472747" \
	--browser-mode stealth

# No doi prefix
python -m scitex.scholar.url.ScholarURLFinder \
	--url "10.1016/j.clinph.2024.09.017" \
	--browser-mode stealth

# Found 1 PDF URLs:
# [{'source': 'zotero_translator',
#   'url': 'https://www.sciencedirect.com/science/article/pii/S1388245724002761/pdfft?download=true'}]
"""

# EOF
