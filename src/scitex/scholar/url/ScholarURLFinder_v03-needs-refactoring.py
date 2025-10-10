#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 21:32:22 (ywatanabe)"
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
ScholarURLFinder - URL resolution and PDF finding orchestrator

Clean, functional API for DOI resolution and PDF URL discovery.
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar.auth.gateway import (
    OpenURLResolver,
    normalize_doi_as_http,
    resolve_publisher_url_by_navigating_to_doi_page,
)
from scitex.scholar.config import PublisherRules, ScholarConfig

from .strategies import (
    find_pdf_urls_by_dropdown,
    find_pdf_urls_by_href,
    find_pdf_urls_by_navigation,
    find_pdf_urls_by_publisher_patterns,
    find_pdf_urls_by_zotero_translators,
)

logger = logging.getLogger(__name__)


class ScholarURLFinder:
    """URL resolution and PDF finding orchestrator."""

    PAGE_LOAD_TIMEOUT = 30_000
    OPENURL_DELAY = 5000
    STRATEGY_SUCCESS_DELAY = 1000

    def __init__(
        self,
        context: BrowserContext,
        openurl_resolver_url: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context
        self._page = None

    # ==========================================================================
    # Public API
    # ==========================================================================

    async def find_urls(self, doi: str) -> Dict[str, Any]:
        """Get all URLs for a DOI: DOI → Publisher → PDFs → OpenURL (fallback)."""
        urls = {"url_doi": normalize_doi_as_http(doi)}

        # Try publisher URL first
        url_publisher = await self._resolve_publisher_url(doi)
        urls["url_publisher"] = url_publisher

        # Extract PDFs from publisher URL
        urls_pdf = (
            await self._try_extract_pdf_urls(url_publisher, doi)
            if url_publisher
            else []
        )

        # Fallback to OpenURL if no PDFs found
        if not urls_pdf:
            urls_pdf = await self._try_openurl_extraction(doi, urls)

        # Store deduplicated PDFs
        urls["urls_pdf"] = self._deduplicate_pdfs(urls_pdf) if urls_pdf else []

        return urls

    async def find_urls_batch(self, dois: List[str]) -> List[Dict[str, Any]]:
        """Process multiple DOIs sequentially."""
        results = [await self._safe_find_urls(doi) for doi in dois]
        self._log_batch_statistics(dois, results)
        return results

    async def find_pdf_urls_async(self, page_or_url) -> List[Dict]:
        """Find PDF URLs from page or URL string."""
        return (
            await self._find_pdfs_from_url_string(page_or_url)
            if isinstance(page_or_url, str)
            else await self._find_pdfs_from_page(page_or_url)
        )

    # ==========================================================================
    # PDF Finding Strategies
    # ==========================================================================

    async def _find_pdf_urls_with_strategies(
        self, page: Page, base_url: Optional[str] = None
    ) -> List[Dict]:
        """Try strategies in priority order, return early on success."""
        base_url = base_url or page.url
        await browser_logger.info(
            page, f"{self.name}: Finding PDFs at {base_url[:60]}..."
        )

        # Try each strategy in order
        for strategy_result in [
            await self._try_zotero_strategy(page, base_url),
            await self._try_direct_links_strategy(page, base_url),
            await self._try_navigation_strategy(page, base_url),
            await self._try_pattern_strategy(page, base_url),
        ]:
            if strategy_result:
                await page.wait_for_timeout(self.STRATEGY_SUCCESS_DELAY)
                return strategy_result

        return []

    async def _try_zotero_strategy(
        self, page: Page, base_url: str
    ) -> List[Dict]:
        """Strategy 1: Zotero translators."""
        urls = await find_pdf_urls_by_zotero_translators(
            page, base_url, self.config, self.name
        )
        return self._as_pdf_dicts(urls, "zotero_translator")

    async def _try_direct_links_strategy(
        self, page: Page, base_url: str
    ) -> List[Dict]:
        """Strategy 2: Direct links (dropdown + href + filtering)."""
        await browser_logger.info(
            page, f"{self.name}: 2/4 Finding PDF URLs by Direct Links..."
        )

        # Collect from both sources
        urls = set()
        urls.update(
            await find_pdf_urls_by_dropdown(
                page, base_url, self.config, self.name
            )
        )
        urls.update(
            await find_pdf_urls_by_href(page, base_url, self.config, self.name)
        )

        # Filter and return
        filtered = self._filter_by_publisher_rules(base_url, urls)
        if filtered:
            await browser_logger.success(
                page, f"{self.name}: ✓ Direct links found {len(filtered)} URLs"
            )
        return self._as_pdf_dicts(filtered, "direct_link")

    async def _try_navigation_strategy(
        self, page: Page, base_url: str
    ) -> List[Dict]:
        """Strategy 3: Navigation (Elsevier only)."""
        if not self._is_elsevier_domain(base_url):
            return []

        await browser_logger.info(
            page, f"{self.name}: 3/4 Finding PDF URLs by Navigation..."
        )
        urls = await find_pdf_urls_by_navigation(
            page, base_url, self.config, self.name
        )
        return self._as_pdf_dicts(urls, "navigation")

    async def _try_pattern_strategy(
        self, page: Page, base_url: str
    ) -> List[Dict]:
        """Strategy 4: Publisher patterns."""
        await browser_logger.info(
            page, f"{self.name}: 4/4 Finding PDF URLs by Publisher Patterns..."
        )
        urls = find_pdf_urls_by_publisher_patterns(
            page, base_url, self.config, self.name
        )
        if urls:
            await browser_logger.success(
                page, f"{self.name}: ✓ Patterns found {len(urls)} URLs"
            )
        return self._as_pdf_dicts(urls, "publisher_pattern")

    # ==========================================================================
    # URL Resolution
    # ==========================================================================

    async def _resolve_publisher_url(self, doi: str) -> Optional[str]:
        """Resolve publisher URL from DOI."""
        page = await self.get_page()
        return await resolve_publisher_url_by_navigating_to_doi_page(doi, page)

    async def _resolve_openurl(self, doi: str) -> Dict[str, Optional[str]]:
        """Resolve OpenURL for DOI."""
        if not self.openurl_resolver_url:
            return {"url_openurl_query": None, "url_openurl_resolved": None}

        resolver = OpenURLResolver(config=self.config)
        page = await self.get_page()
        await page.wait_for_timeout(self.OPENURL_DELAY)

        return {
            "url_openurl_query": resolver._build_query(doi),
            "url_openurl_resolved": await resolver.resolve_doi(doi, page),
        }

    # ==========================================================================
    # PDF Extraction Helpers
    # ==========================================================================

    async def _try_extract_pdf_urls(self, url: str, doi: str) -> List[Dict]:
        """Extract PDFs from URL, with error handling."""
        async with self._managed_page() as page:
            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.PAGE_LOAD_TIMEOUT,
                )
                pdfs = await self._find_pdf_urls_with_strategies(page)

                if pdfs:
                    logger.success(
                        f"{self.name}: Found {len(pdfs)} PDFs from publisher"
                    )
                else:
                    await browser_logger.warn(
                        page, f"{self.name}: {doi} - No PDFs Found"
                    )

                return pdfs
            except Exception as e:
                logger.error(
                    f"{self.name}: Error extracting PDFs from {url}: {e}"
                )
                await browser_logger.error(
                    page, f"{self.name}: {doi} - Page Error"
                )
                return []

    async def _try_openurl_extraction(
        self, doi: str, urls: Dict
    ) -> List[Dict]:
        """Try OpenURL resolution as fallback."""
        logger.info(f"{self.name}: Trying OpenURL resolution...")
        openurl_results = await self._resolve_openurl(doi)
        urls.update(openurl_results)

        # Set default values if no publisher PDFs found
        urls.setdefault("url_openurl_query", self._build_openurl_query(doi))
        urls.setdefault("url_openurl_resolved", "skipped")

        # Try extracting from resolved URL
        resolved_url = urls.get("url_openurl_resolved")
        if resolved_url and resolved_url != "skipped":
            pdfs = await self._try_extract_pdf_urls(resolved_url, doi)
            if pdfs:
                logger.success(
                    f"{self.name}: Found {len(pdfs)} PDFs from OpenURL"
                )
            return pdfs

        return []

    async def _find_pdfs_from_url_string(self, url: str) -> List[Dict]:
        """Find PDFs from URL string."""
        if not self.context:
            logger.error(f"{self.name}: Browser context required")
            return []

        async with self._managed_page() as page:
            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.PAGE_LOAD_TIMEOUT,
                )
                pdfs = await self._find_pdf_urls_with_strategies(page)

                if not pdfs:
                    await browser_logger.warn(
                        page, f"{self.name}: No PDFs from URL: {url[:50]}"
                    )

                return pdfs
            except Exception as e:
                logger.warning(f"{self.name}: Failed to load page: {e}")
                await browser_logger.error(
                    page, f"{self.name}: Navigation Error"
                )
                return []

    async def _find_pdfs_from_page(self, page: Page) -> List[Dict]:
        """Find PDFs from existing page."""
        try:
            pdfs = await self._find_pdf_urls_with_strategies(page)

            if not pdfs:
                await browser_logger.warn(
                    page, f"{self.name}: No PDFs on page"
                )

            return pdfs
        except Exception as e:
            logger.error(f"{self.name}: Error finding PDFs: {e}")
            await browser_logger.error(page, f"{self.name}: PDF Search Error")
            return []

    # ==========================================================================
    # Utilities
    # ==========================================================================

    async def get_page(self) -> Page:
        """Get or create a page."""
        if self._page is None or self._page.is_closed():
            self._page = await self.context.new_page()
        return self._page

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

    async def _safe_find_urls(self, doi: str) -> Dict[str, Any]:
        """Find URLs with error handling."""
        try:
            return await self.find_urls(doi)
        except Exception as e:
            logger.debug(f"{self.name}: Error for DOI {doi}: {e}")
            return {}

    def _filter_by_publisher_rules(self, url: str, urls: set) -> List[str]:
        """Filter URLs by publisher rules."""
        filtered = PublisherRules(self.config).filter_pdf_urls(url, list(urls))
        if len(urls) > len(filtered):
            logger.info(
                f"{self.name}: Filtered {len(urls)} → {len(filtered)} valid PDFs"
            )
        return filtered

    def _as_pdf_dicts(self, urls: List[str], source: str) -> List[Dict]:
        """Convert URL strings to dict format with source."""
        return [{"url": url, "source": source} for url in urls]

    def _deduplicate_pdfs(self, urls_pdf: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs."""
        seen = set()
        unique = []
        for pdf in urls_pdf:
            url = pdf.get("url") if isinstance(pdf, dict) else pdf
            if url not in seen:
                seen.add(url)
                unique.append(pdf)
        return unique

    def _build_openurl_query(self, doi: str) -> str:
        """Build OpenURL query."""
        return f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi={doi}"

    def _is_elsevier_domain(self, url: str) -> bool:
        """Check if URL is Elsevier."""
        return any(
            d in url.lower()
            for d in ["sciencedirect.com", "cell.com", "elsevier.com"]
        )

    def _log_batch_statistics(self, dois: List[str], results: List[Dict]):
        """Log batch processing statistics."""
        if not dois:
            return

        found = sum(1 for r in results if r.get("urls_pdf"))
        pct = 100.0 * found / len(dois)
        msg = f"{self.name}: Found {found}/{len(dois)} PDFs ({pct:.1f}%)"

        (logger.success if found == len(dois) else logger.warn)(msg)


# ==============================================================================
# CLI
# ==============================================================================


def parse_args():
    """Parse CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Find PDF URLs and resolve DOIs"
    )
    parser.add_argument(
        "--doi", required=True, help="DOI (e.g., 10.1038/nature12373)"
    )
    parser.add_argument(
        "--browser-mode",
        choices=["interactive", "headless"],
        default="interactive",
    )
    parser.add_argument("--chrome-profile", default="system_worker_0")
    return parser.parse_args()


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from pprint import pprint

        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )
        from scitex.scholar.auth import AuthenticationGateway

        args = parse_args()

        # Setup
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode=args.browser_mode,
            chrome_profile_name=args.chrome_profile,
        )
        _, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        # Authenticate
        auth_gateway = AuthenticationGateway(auth_manager, browser_manager)
        await auth_gateway.prepare_context_async(doi=args.doi, context=context)

        # Find URLs
        url_finder = ScholarURLFinder(context)
        pprint(await url_finder.find_urls(args.doi))

    asyncio.run(main_async())

# EOF
