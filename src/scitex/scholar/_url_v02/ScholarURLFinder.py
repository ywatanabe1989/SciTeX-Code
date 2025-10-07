#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 18:12:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/ScholarURLFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
ScholarURLFinder - Main entry point for URL operations

Provides a clean API that wraps the functional modules.
Users can use this for convenience or directly import the functions.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

from .helpers import (
    find_pdf_urls,
    normalize_doi_as_http,
    resolve_openurl,
    resolve_publisher_url_by_navigating_to_doi_page,
)
from .helpers.openurl_helpers import (
    click_openurl_link_and_capture_popup,
    find_openurl_access_links,
    select_best_access_route,
)
from .helpers.publisher_strategies import get_strategy_for_url

logger = logging.getLogger(__name__)


from scitex.scholar.browser.utils import take_screenshot


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
        use_cache=False,
        clear_cache=False,
    ):
        """Initialize URL handler."""
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context
        self._page = None

        # Cache
        self.use_cache = self.config.resolve("use_cache_url_finder", use_cache)

        # Use Scholar's URL finder cache directory
        self.cache_dir = self.config.get_url_finder_cache_dir()
        self.publisher_cache_file = self.cache_dir / "publisher_urls.json"
        self.openurl_cache_file = self.cache_dir / "openurl_resolved.json"
        self.full_results_cache_file = self.cache_dir / "full_results.json"

        # Clear cache if requested
        if clear_cache:
            self._clear_all_cache()

        # Load existing caches
        if use_cache:
            self._publisher_cache = self._load_cache(self.publisher_cache_file)
            self._openurl_cache = self._load_cache(self.openurl_cache_file)
            self._full_results_cache = self._load_cache(
                self.full_results_cache_file
            )
        else:
            self._publisher_cache = {}
            self._openurl_cache = {}
            self._full_results_cache = {}

    async def get_page(self):
        if self._page is None or self._page.is_closed():
            self._page = await self.context.new_page()
        return self._page

    async def find_urls(self, doi: str) -> Dict[str, Any]:
        """Get all URL types for a doi following resolution pipeline."""

        # Check full results cache first
        if self.use_cache and doi in self._full_results_cache:
            logger.info(f"Using cached full results for DOI: {doi}")
            return self._full_results_cache[doi]

        urls = {}

        # Step 1: DOI URL
        urls["url_doi"] = normalize_doi_as_http(doi)

        # Step 2: Publisher URL (cached)
        url_publisher = await self._get_cached_publisher_url(doi)
        if url_publisher:
            urls["url_publisher"] = url_publisher

        logger.info(
            f"\n{'-'*40}\nScholarURLFinder finding PDF URLs for {doi}...\n{'-'*40}"
        )

        # Step 3: Try PDF extraction from Publisher URL FIRST
        urls_pdf = []

        if url_publisher:
            # SHORTCUT: IEEE papers - extract article number directly from publisher URL
            if "ieeexplore.ieee.org/document/" in url_publisher:
                logger.info(
                    "IEEE publisher URL detected, trying direct article number extraction..."
                )
                match = re.search(r"/document/(\d+)", url_publisher)
                if match:
                    article_num = match.group(1)
                    pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
                    logger.success(
                        f"Built IEEE PDF URL from publisher URL: {pdf_url}"
                    )
                    urls_pdf.append(pdf_url)

            # Try Zotero translators if no shortcut worked
            if not urls_pdf:
                logger.debug(
                    f"Trying PDF extraction from publisher URL first..."
                )
                pdfs = await self._get_pdfs_from_url(url_publisher, doi)
                urls_pdf.extend(pdfs)

            if urls_pdf:
                logger.success(
                    f"Found {len(urls_pdf)} PDFs from publisher URL - skipping OpenURL resolution"
                )
                # Skip OpenURL entirely - we have PDFs!
                urls["url_openurl_query"] = (
                    f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi={doi}"
                )
                urls["url_openurl_resolved"] = (
                    "skipped"  # Skipped because PDFs found from publisher
                )

        # Step 4: Only do OpenURL if no PDFs found from publisher
        if not urls_pdf:
            logger.info("No PDFs from publisher URL, resolving OpenURL...")
            openurl_results = await self._get_cached_openurl(doi)
            urls.update(openurl_results)

            # Try PDF extraction from OpenURL resolved URL
            if urls.get("url_openurl_resolved"):
                logger.debug(
                    f"Trying PDF extraction from OpenURL resolved URL..."
                )
                pdfs = await self._get_pdfs_from_url(
                    urls["url_openurl_resolved"], doi
                )
                urls_pdf.extend(pdfs)

                if pdfs:
                    logger.info(f"Found {len(pdfs)} PDFs from OpenURL")

            # Step 5: NEW - Try OpenURL institutional access route if still no PDFs
            if not urls_pdf and urls.get("url_openurl_query"):
                logger.info(
                    "No PDFs from OpenURL resolved URL, trying institutional access route..."
                )
                openurl_pdfs = await self.find_pdf_urls_via_openurl(
                    doi, urls["url_openurl_query"]
                )
                if openurl_pdfs:
                    logger.success(
                        f"Found {len(openurl_pdfs)} PDFs via OpenURL institutional access"
                    )
                    urls_pdf.extend(openurl_pdfs)

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

        # Cache full results
        if self.use_cache:
            self._full_results_cache[doi] = urls
            self._save_cache(
                self.full_results_cache_file, self._full_results_cache
            )

        return urls

    # # Now, this is not working; probably, we need to prepare multiple contexts or browsers
    # async def find_urls_batch(
    #     self, dois: List[str], max_concurrent: int = 4
    # ) -> List[Dict[str, Any]]:
    #     """Get all URL types for multiple DOIs in batch with parallel processing."""
    #     if not dois:
    #         return []

    #     semaphore = asyncio.Semaphore(max_concurrent)

    #     async def find_urls_with_semaphore(doi: str):
    #         async with semaphore:
    #             # Check cache first - no page needed
    #             if self.use_cache and doi in self._full_results_cache:
    #                 return self._full_results_cache[doi]

    #             page = await self.context.new_page()
    #             try:
    #                 return await self.find_urls(doi=doi)
    #             except Exception as e:
    #                 logger.error(f"Error finding URLs for {doi}: {e}")
    #                 return {}
    #             finally:
    #                 await page.close()

    #     # Create tasks for parallel execution
    #     tasks = [find_urls_with_semaphore(doi) for doi in dois]

    #     # Execute with controlled concurrency
    #     results = await asyncio.gather(*tasks, return_exceptions=True)

    #     # Process results
    #     batch_results = []
    #     for ii_result, result in enumerate(results):
    #         if isinstance(result, Exception):
    #             logger.debug(
    #                 f"Batch URL finding error for DOI {dois[ii_result]}: {result}"
    #             )
    #             batch_results.append({})
    #         else:
    #             batch_results.append(result or {})

    #     # Success Rate
    #     n_dois = len(dois)
    #     if n_dois:
    #         n_found = sum(
    #             1
    #             for result in results
    #             if not isinstance(result, Exception)
    #             and result
    #             and result.get("urls_pdf")
    #         )
    #         msg = f"Found {n_found}/{n_dois} PDFs (= {100. * n_found / n_dois:.1f}%)"
    #         if n_found == n_dois:
    #             logger.success(msg)
    #         else:
    #             logger.warn(msg)

    #     return batch_results

    async def find_urls_batch(
        self, dois: List[str], max_concurrent: int = 1
    ) -> List[Dict[str, Any]]:
        """Process DOIs sequentially to avoid network issues."""
        if not dois:
            return []

        batch_results = []

        for doi in dois:
            try:
                if self.use_cache and doi in self._full_results_cache:
                    result = self._full_results_cache[doi]
                else:
                    result = await self.find_urls(doi=doi)
                batch_results.append(result or {})
            except Exception as e:
                logger.debug(f"Batch URL finding error for DOI {doi}: {e}")
                batch_results.append({})

        n_dois = len(dois)
        if n_dois:
            n_found = sum(
                1 for result in batch_results if result.get("urls_pdf")
            )
            msg = f"Found {n_found}/{n_dois} PDFs (= {100. * n_found / n_dois:.1f}%)"
            if n_found == n_dois:
                logger.success(msg)
            else:
                logger.warn(msg)

        return batch_results

    async def _get_pdfs_from_url(
        self,
        url: str,
        doi: str,
    ) -> List[Dict]:
        """Get PDF URLs from a specific URL."""
        try:
            page = await self.get_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)

            pdfs = await find_pdf_urls(page)

            # Take screenshot if no PDFs found
            if not pdfs:
                await take_screenshot(
                    page, "ScholarURLFinder", f"{doi} - No PDFs Found"
                )

            return pdfs
        except Exception as e:
            # Take screenshot on error
            try:
                await take_screenshot(
                    page, "ScholarURLFinder", f"{doi} - Page Error"
                )
            except:
                pass
            logger.error(f"Error getting PDFs from {url}: {e}")
            return []

    async def find_pdf_urls_via_openurl(
        self,
        doi: str,
        openurl_query: str,
    ) -> List[str]:
        """
        Find PDF URLs via OpenURL institutional access route.

        This method handles paywalled papers with institutional access by:
        1. Navigating to OpenURL resolver
        2. Finding and clicking access links (IEEE, Elsevier, etc.)
        3. Capturing popup windows (JavaScript links)
        4. Applying publisher-specific strategies
        5. Extracting PDF URLs

        Args:
            doi: Paper DOI
            openurl_query: OpenURL resolver query URL

        Returns:
            List of PDF URLs found via institutional access
        """
        # Create a fresh page for OpenURL workflow (don't reuse existing page)
        page = None
        try:
            # Check if context is still valid
            if self.context.browser is None:
                logger.error("Browser context is invalid")
                return []

            page = await self.context.new_page()

            # Step 1: Navigate to OpenURL
            logger.info(f"Navigating to OpenURL for {doi}...")
            await page.goto(
                openurl_query, wait_until="networkidle", timeout=30000
            )
            await asyncio.sleep(2)

            await take_screenshot(
                page, "ScholarURLFinder", f"{doi} - OpenURL Page"
            )

            # Step 2: Find access links
            logger.info("Finding institutional access links...")
            links = await find_openurl_access_links(page)

            if not links:
                logger.warning("No access links found on OpenURL page")
                return []

            # Step 3: Select best route (open access > institutional)
            best_link = await select_best_access_route(links)
            if not best_link:
                return []

            # Step 4: Click link and capture popup
            logger.info(f"Clicking '{best_link['text']}'...")
            popup_page = await click_openurl_link_and_capture_popup(
                page, best_link["text"]
            )

            if not popup_page:
                logger.error("Failed to capture popup window")
                return []

            await take_screenshot(
                popup_page, "ScholarURLFinder", f"{doi} - Popup Page"
            )

            # Step 5: Apply publisher strategy
            logger.info(f"Applying publisher strategy for {popup_page.url}...")
            strategy = await get_strategy_for_url(popup_page.url)

            if not strategy:
                logger.warning(f"No strategy for {popup_page.url}")
                # Fallback: try direct PDF extraction
                pdfs = await find_pdf_urls(popup_page)
                return [
                    pdf.get("url") if isinstance(pdf, dict) else pdf
                    for pdf in pdfs
                ]

            # Step 6: Get PDF URL using strategy
            pdf_url = await strategy.get_pdf_url(popup_page)

            if pdf_url:
                logger.success(f"Found PDF via OpenURL: {pdf_url}")
                return [pdf_url]
            else:
                logger.warning("Strategy did not find PDF URL")
                return []

        except Exception as e:
            logger.error(
                f"OpenURL access failed for {doi}: {e}", exc_info=True
            )
            try:
                if page and not page.is_closed():
                    await take_screenshot(
                        page, "ScholarURLFinder", f"{doi} - OpenURL Error"
                    )
            except:
                pass
            return []
        finally:
            # Always close the page we created
            if page and not page.is_closed():
                try:
                    await page.close()
                except:
                    pass

    async def find_pdf_urls_async(self, page_or_url) -> List[Dict]:
        """Find PDF URLs from a page or URL."""
        if isinstance(page_or_url, str):
            if not self.context:
                logger.error("Browser context required to navigate to URL")
                return []

            page = await self.context.new_page()
            try:
                await page.goto(
                    page_or_url, wait_until="domcontentloaded", timeout=30000
                )

                pdfs = await find_pdf_urls(page)

                # Take screenshot if no PDFs found
                if not pdfs:
                    await take_screenshot(
                        page,
                        "ScholarURLFinder",
                        f"No PDFs from URL: {page_or_url[:50]}",
                    )

                return pdfs
            except Exception as e:
                logger.warning(f"Failed to load page: {e}")
                try:
                    await take_screenshot(
                        page, "ScholarURLFinder", "Navigation Error"
                    )
                except:
                    pass
                return []
            finally:
                await page.close()

        else:
            try:
                pdfs = await find_pdf_urls(page_or_url)

                # Take screenshot if no PDFs found
                if not pdfs:
                    await take_screenshot(
                        page_or_url, "ScholarURLFinder", "No PDFs Page"
                    )
                return pdfs
            except Exception as e:
                logger.error(f"Error finding PDF URLs: {e}")
                try:
                    await take_screenshot(
                        page_or_url, "ScholarURLFinder", "PDF Search Error"
                    )
                except:
                    pass
                return []

    # async def resolve_openurl_async(
    #     self, openurl_query: str, page: Page
    # ) -> Optional[str]:
    #     """Resolve OpenURL to final authenticated URL."""
    #     return await resolve_openurl(openurl_query, page)

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

            logger.success(f"Updated metadata: {metadata_path.parent.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False

    def get_urls_from_metadata(self, metadata_path: Path) -> Dict:
        """Get URLs from metadata file."""
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            return metadata.get("urls", {})
        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return {}

    # Cache methods
    def _clear_all_cache(self):
        """Clear all cache files."""
        cache_files = [
            self.publisher_cache_file,
            self.openurl_cache_file,
            self.full_results_cache_file,
        ]

        for cache_file in cache_files:
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cleared cache: {cache_file.name}")

    def _load_cache(self, cache_file: Path) -> dict:
        """Load cache from file."""
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self, cache_file: Path, cache_data: dict):
        """Save cache to file."""
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_file}: {e}")

    async def _get_cached_publisher_url(self, doi: str) -> Optional[str]:
        """Get publisher URL with persistent caching."""

        if self.use_cache and doi in self._publisher_cache:
            logger.debug(f"Using cached publisher URL for DOI: {doi}")
            return self._publisher_cache[doi]

        page = await self.get_page()
        result = await resolve_publisher_url_by_navigating_to_doi_page(
            doi, page
        )

        if self.use_cache:
            self._publisher_cache[doi] = result
            self._save_cache(self.publisher_cache_file, self._publisher_cache)

        return result

    # async def _get_cached_openurl(self, doi: str) -> Dict[str, str]:
    #     """Get OpenURL results with caching using DOI as key."""
    #     results = {}

    #     if not self.openurl_resolver_url:
    #         return results

    #     from .helpers.resolvers._OpenURLResolver import OpenURLResolver

    #     resolver = OpenURLResolver(config=self.config)

    #     openurl_query = resolver._build_query(doi)
    #     if openurl_query:
    #         results["url_openurl_query"] = openurl_query

    #     if self.use_cache and doi in self._openurl_cache:
    #         logger.debug(f"Using cached OpenURL resolution for DOI: {doi}")
    #         resolved_url = self._openurl_cache[doi]
    #     else:
    #         page = await self.get_page()
    #         resolved_url = await resolver.resolve_doi(doi, page)

    #         if self.use_cache:
    #             self._openurl_cache[doi] = resolved_url
    #             self._save_cache(self.openurl_cache_file, self._openurl_cache)

    #     if resolved_url:
    #         results["url_openurl_resolved"] = resolved_url

    #     return results

    async def _get_cached_openurl(self, doi: str) -> Dict[str, str]:
        """Get OpenURL results with caching and delay."""
        results = {}
        if not self.openurl_resolver_url:
            return results

        from .helpers.resolvers._OpenURLResolver import OpenURLResolver

        resolver = OpenURLResolver(config=self.config)
        openurl_query = resolver._build_query(doi)

        if openurl_query:
            results["url_openurl_query"] = openurl_query

        if self.use_cache and doi in self._openurl_cache:
            resolved_url = self._openurl_cache[doi]
        else:
            page = await self.get_page()
            # Add delay to avoid overwhelming resolver
            await page.wait_for_timeout(5000)
            resolved_url = await resolver.resolve_doi(doi, page)

            if self.use_cache:
                self._openurl_cache[doi] = resolved_url
                self._save_cache(self.openurl_cache_file, self._openurl_cache)

        if resolved_url:
            results["url_openurl_resolved"] = resolved_url
        return results


if __name__ == "__main__":
    import asyncio

    async def main_async():
        from pprint import pprint

        from scitex.scholar import (
            ScholarAuthManager,
            ScholarBrowserManager,
            ScholarURLFinder,
        )

        # Initialize with authenticated browser context
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            browser_mode="interactive",
            chrome_profile_name="system",
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        # Create URL handler
        url_finder = ScholarURLFinder(context, use_cache=False)

        # Get all URLs for a paper
        doi = "10.1016/j.cell.2025.07.007"
        doi = "10.1126/science.aao0702"
        doi = "10.1109/niles56402.2022.9942397"
        doi = "10.1109/jbhi.2025.3556775"
        urls = await url_finder.find_urls(
            doi=doi,
        )
        pprint(urls)

    asyncio.run(main_async())

# python -m scitex.scholar.url.ScholarURLFinder

# EOF
