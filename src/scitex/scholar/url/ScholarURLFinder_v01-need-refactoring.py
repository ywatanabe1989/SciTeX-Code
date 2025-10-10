#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 06:38:22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/ScholarURLFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Optional

"""
ScholarURLFinder - Main entry point for URL operations

Provides a clean API that wraps the functional modules.
Users can use this for convenience or directly import the functions.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar.config import ScholarConfig

from .strategies import (
    find_pdf_urls_by_dropdown,
    find_pdf_urls_by_href,
    find_pdf_urls_by_publisher_patterns,
    find_pdf_urls_by_navigation,
    find_pdf_urls_by_zotero_translators,
)
from scitex.scholar.config import PublisherRules
from scitex.scholar.auth.gateway import (
    normalize_doi_as_http,
    resolve_publisher_url_by_navigating_to_doi_page,
)
from scitex.scholar.auth.gateway import OpenURLResolver

logger = logging.getLogger(__name__)

from scitex.browser.debugging import browser_logger


class ScholarURLFinder:
    """Main entry point for all URL operations."""

    URL_TYPES = [
        "urls_pdf",
        "url_doi",
        "url_openurl_query",
        "url_openurl_resolved",
        "url_publisher",
    ]

    def __init__(
        self,
        context: BrowserContext,
        openurl_resolver_url=None,
        config=None,
    ):
        """Initialize URL handler."""
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context
        self._page = None

    async def get_page(self):
        if self._page is None or self._page.is_closed():
            self._page = await self.context.new_page()
        return self._page

    async def find_urls(self, doi: str) -> Dict[str, Any]:
        """Get all URL types for a doi following resolution pipeline."""
        urls = {}

        # Step 1: DOI URL
        urls["url_doi"] = normalize_doi_as_http(doi)

        # Step 2: Publisher URL
        url_publisher = await self._resolve_publisher_url(doi)
        if url_publisher:
            urls["url_publisher"] = url_publisher

        # Step 3: Try PDF extraction from Publisher URL FIRST
        urls_pdf = []

        if url_publisher:
            pdfs = await self._get_pdfs_from_url(url_publisher, doi)
            urls_pdf.extend(pdfs)

            if urls_pdf:
                logger.success(
                    f"{self.name}: Found {len(urls_pdf)} PDFs from publisher",
                )
                # Skip OpenURL entirely - we have PDFs!
                urls["url_openurl_query"] = (
                    f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi={doi}"
                )
                urls["url_openurl_resolved"] = "skipped"

        # Step 4: Only do OpenURL if no PDFs found from publisher
        if not urls_pdf:
            logger.info(
                f"{self.name}: Trying OpenURL resolution...",
            )
            openurl_results = await self._resolve_openurl(doi)
            urls.update(openurl_results)

            # Try PDF extraction from OpenURL resolved URL
            if urls.get("url_openurl_resolved"):
                pdfs = await self._get_pdfs_from_url(
                    urls["url_openurl_resolved"], doi
                )
                urls_pdf.extend(pdfs)
                if pdfs:
                    logger.success(
                        f"{self.name}: Found {len(pdfs)} PDFs from OpenURL",
                    )

        if urls_pdf:
            # Deduplicate PDFs
            unique_pdfs = []
            seen_urls = set()
            for pdf in urls_pdf:
                pdf_url = pdf.get("url") if isinstance(pdf, dict) else pdf
                if pdf_url not in seen_urls:
                    seen_urls.add(pdf_url)
                    unique_pdfs.append(pdf)
            urls["urls_pdf"] = unique_pdfs

        return urls

    async def find_urls_batch(
        self, dois: List[str], max_concurrent: int = 1
    ) -> List[Dict[str, Any]]:
        """Process DOIs sequentially to avoid network issues."""
        if not dois:
            return []

        batch_results = []

        for doi in dois:
            try:
                result = await self.find_urls(doi=doi)
                batch_results.append(result or {})
            except Exception as e:
                logger.debug(
                    f"{self.name}: Batch URL finding error for DOI {doi}: {e}"
                )
                batch_results.append({})

        n_dois = len(dois)
        if n_dois:
            n_found = sum(
                1 for result in batch_results if result.get("urls_pdf")
            )
            msg = f"{self.name}: Found {n_found}/{n_dois} PDFs (= {100. * n_found / n_dois:.1f}%)"
            if n_found == n_dois:
                logger.success(msg)
            else:
                logger.warn(msg)

        return batch_results

    async def _find_pdf_urls_async(
        self,
        page: Page,
        base_url: str = None,
    ) -> List[Dict]:
        """
        Find PDF URLs using multiple strategies.

        Tries strategies in order until PDFs are found:
        1. Zotero Translators
        2. Direct Links
        3. Navigation (Elsevier only)
        4. Publisher Patterns

        Args:
            page: Playwright page object
            base_url: Base URL (defaults to page.url)

        Returns:
            List of dicts with 'url' and 'source' keys
        """
        base_url = base_url or page.url
        urls_pdf = []
        seen_urls = set()

        await browser_logger.info(
            page, f"{self.name}: Finding PDFs at {base_url[:60]}..."
        )

        # Helper to add URLs with deduplication
        async def add_urls(urls: List[str], source_name: str):
            for url in urls:
                if url not in seen_urls:
                    seen_urls.add(url)
                    urls_pdf.append({"url": url, "source": source_name})

        # Strategy 1: Zotero Translators
        try:
            await browser_logger.info(
                page,
                f"{self.name}: 1/4 Finding PDF URLs by Python Zotero translators...",
            )
            translator_urls = await find_pdf_urls_by_zotero_translators(
                page, base_url, self.name
            )
            await add_urls(translator_urls, "zotero_translator")

            if translator_urls:
                await browser_logger.info(
                    page,
                    f"{self.name}: ✓ Python Zotero found {len(translator_urls)} URLs",
                )
                await page.wait_for_timeout(1000)
                return urls_pdf  # Return early on success
        except Exception as e:
            logger.warn(f"{self.name}: Zotero strategy failed: {e}")

        # Strategy 2: Direct Links (dropdown + href + publisher filtering)
        try:
            await browser_logger.info(
                page, f"{self.name}: 2/4 Finding PDF URLs by Direct Links..."
            )

            all_direct_urls = set()

            # 2a. Find from dropdown
            dropdown_urls = await find_pdf_urls_by_dropdown(page, self.config, self.name)
            all_direct_urls.update(dropdown_urls)

            # 2b. Find from href
            href_urls = await find_pdf_urls_by_href(page, self.config, self.name)
            all_direct_urls.update(href_urls)

            # 2c. Filter using publisher rules
            publisher_rules = PublisherRules(self.config)
            filtered_urls = publisher_rules.filter_pdf_urls(page.url, list(all_direct_urls))

            if len(all_direct_urls) > len(filtered_urls):
                logger.info(
                    f"{self.name}: Filtered {len(all_direct_urls)} URLs down to {len(filtered_urls)} valid PDFs"
                )

            await add_urls(filtered_urls, "direct_link")

            if filtered_urls:
                await browser_logger.info(
                    page, f"{self.name}: ✓ Direct links found {len(filtered_urls)} URLs"
                )
                await page.wait_for_timeout(1000)
                return urls_pdf  # Return early on success
        except Exception as e:
            logger.warn(f"{self.name}: Direct links strategy failed: {e}")

        # Strategy 3: Navigation (Elsevier only)
        try:
            elsevier_domains = ["sciencedirect.com", "cell.com", "elsevier.com"]
            if any(domain in page.url.lower() for domain in elsevier_domains):
                await browser_logger.info(
                    page, f"{self.name}: 3/4 Finding PDF URLs by Navigation..."
                )

                navigation_urls = await find_pdf_urls_by_navigation(
                    page, self.config, self.name
                )

                # Special handling for Elsevier - replace pdfft URLs
                for url in navigation_urls:
                    if url not in seen_urls:
                        seen_urls.add(url)

                        replaced = False
                        for ii, existing in enumerate(urls_pdf):
                            if (
                                "/pdfft?" in existing["url"]
                                and "pdf.sciencedirectassets.com" in url
                            ):
                                urls_pdf[ii] = {"url": url, "source": "navigation"}
                                replaced = True
                                break

                        if not replaced:
                            urls_pdf.append({"url": url, "source": "navigation"})

                if navigation_urls:
                    return urls_pdf  # Return early on success
        except Exception as e:
            logger.warn(f"{self.name}: Navigation strategy failed: {e}")

        # Strategy 4: Publisher Patterns
        try:
            await browser_logger.info(
                page, f"{self.name}: 4/4 Finding PDF URLs by Publisher Patterns..."
            )
            pattern_urls = find_pdf_urls_by_publisher_patterns(
                page, base_url, self.name
            )
            await add_urls(pattern_urls, "publisher_pattern")

            if pattern_urls:
                await browser_logger.info(
                    page, f"{self.name}: ✓ Patterns found {len(pattern_urls)} URLs"
                )
                await page.wait_for_timeout(1000)
        except Exception as e:
            logger.warn(f"{self.name}: Publisher patterns strategy failed: {e}")

        return urls_pdf

    async def _get_pdfs_from_url(
        self,
        url: str,
        doi: str,
    ) -> List[Dict]:
        """Get PDF URLs from a specific URL."""
        try:
            # Create fresh page for each URL to avoid cached state
            page = await self.context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            # await page.goto(url, wait_until="networkidle", timeout=30_000)

            pdfs = await self._find_pdf_urls_async(page)

            # Take screenshot if no PDFs found
            if not pdfs:
                screenshot_dir = (
                    Path.home() / ".scitex/scholar/workspace/screenshots"
                )
                await browser_logger.info(
                    page,
                    f"{doi} - No PDFs Found",
                    take_screenshot=True,
                    screenshot_dir=screenshot_dir,
                )

            return pdfs
        except Exception as e:
            # Take screenshot on error
            try:
                screenshot_dir = (
                    Path.home() / ".scitex/scholar/workspace/screenshots"
                )
                await browser_logger.info(
                    page,
                    f"{doi} - Page Error",
                    take_screenshot=True,
                    screenshot_dir=screenshot_dir,
                )
            except:
                pass
            logger.error(f"{self.name}: Error getting PDFs from {url}: {e}")
            return []
        finally:
            # Always close the page to prevent leaks
            try:
                await page.close()
            except:
                pass

    async def find_pdf_urls_async(self, page_or_url) -> List[Dict]:
        """Find PDF URLs from a page or URL."""
        if isinstance(page_or_url, str):
            if not self.context:
                logger.error(
                    f"{self.name}: Browser context required to navigate to URL"
                )
                return []

            page = await self.context.new_page()
            try:
                await page.goto(
                    page_or_url, wait_until="domcontentloaded", timeout=30000
                )

                pdfs = await self._find_pdf_urls_async(page)

                # Take screenshot if no PDFs found
                if not pdfs:
                    screenshot_dir = (
                        Path.home() / ".scitex/scholar/workspace/screenshots"
                    )
                    await browser_logger.info(
                        page,
                        f"No PDFs from URL: {page_or_url[:50]}",
                        take_screenshot=True,
                        screenshot_dir=screenshot_dir,
                    )

                return pdfs
            except Exception as e:
                logger.warning(f"{self.name}: Failed to load page: {e}")
                try:
                    screenshot_dir = (
                        Path.home() / ".scitex/scholar/workspace/screenshots"
                    )
                    await browser_logger.info(
                        page,
                        "Navigation Error",
                        take_screenshot=True,
                        screenshot_dir=screenshot_dir,
                    )
                except:
                    pass
                return []
            finally:
                await page.close()

        else:
            try:
                pdfs = await self._find_pdf_urls_async(page_or_url)

                # Take screenshot if no PDFs found
                if not pdfs:
                    screenshot_dir = (
                        Path.home() / ".scitex/scholar/workspace/screenshots"
                    )
                    await browser_logger.info(
                        page_or_url,
                        "No PDFs Page",
                        take_screenshot=True,
                        screenshot_dir=screenshot_dir,
                    )
                return pdfs
            except Exception as e:
                logger.error(f"{self.name}: Error finding PDF URLs: {e}")
                try:
                    screenshot_dir = (
                        Path.home() / ".scitex/scholar/workspace/screenshots"
                    )
                    await browser_logger.info(
                        page_or_url,
                        "PDF Search Error",
                        take_screenshot=True,
                        screenshot_dir=screenshot_dir,
                    )
                except:
                    pass
                return []

    def update_metadata(self, metadata_path: Path, urls: Dict) -> bool:
        """Update metadata file with resolved URLs."""
        try:
            # Load existing metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Initialize urls section if not present
            if "urls" not in metadata:
                metadata["urls"] = {}

            # Update with new URLs
            metadata["urls"].update(urls)

            # Save back
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.success(
                f"{self.name}: Updated metadata: {metadata_path.parent.name}"
            )
            return True
        except Exception as e:
            logger.error(f"{self.name}: Failed to update metadata: {e}")
            return False

    def get_urls_from_metadata(self, metadata_path: Path) -> Dict:
        """Get URLs from metadata file."""
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            return metadata.get("urls", {})
        except Exception as e:
            logger.error(f"{self.name}: Failed to read metadata: {e}")
            return {}

    async def _resolve_publisher_url(self, doi: str) -> Optional[str]:
        """Resolve publisher URL"""
        page = await self.get_page()
        result = await resolve_publisher_url_by_navigating_to_doi_page(
            doi, page
        )
        return result

    async def _resolve_openurl(self, doi: str) -> Dict[str, str]:
        """Resolve OpenURL"""
        results = {}
        if not self.openurl_resolver_url:
            logger.info(f"{self.name}: OpenURL Resolver URL not set")
            return results

        resolver = OpenURLResolver(config=self.config)
        openurl_query = resolver._build_query(doi)

        page = await self.get_page()

        # Add delay to avoid overwhelming resolver
        await page.wait_for_timeout(5000)
        resolved_url = await resolver.resolve_doi(doi, page)

        return {
            "url_openurl_query": openurl_query if openurl_query else None,
            "url_openurl_resolved": resolved_url if resolved_url else None,
        }


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Find PDF URLs and resolve DOIs through various methods"
    )
    parser.add_argument(
        "--doi",
        type=str,
        required=True,
        help="DOI to resolve (e.g., 10.1038/nature12373)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["interactive", "headless"],
        default="interactive",
        help="Browser mode (default: %(default)s)",
    )
    parser.add_argument(
        "--chrome-profile",
        type=str,
        default="system_worker_0",
        help="Chrome profile name (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from pprint import pprint

        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )

        args = parse_args()

        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode=args.browser_mode,
            chrome_profile_name=args.chrome_profile,
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        from scitex.scholar.auth import AuthenticationGateway

        auth_gateway = AuthenticationGateway(
            auth_manager=auth_manager,
            browser_manager=browser_manager,
        )
        _url_context = await auth_gateway.prepare_context_async(
            doi=args.doi, context=context
        )

        url_finder = ScholarURLFinder(context)
        urls = await url_finder.find_urls(
            doi=args.doi,
        )
        pprint(urls)

    asyncio.run(main_async())

# python -m scitex.scholar.url.ScholarURLFinder --doi "10.2139/ssrn.5293145"

# EOF
