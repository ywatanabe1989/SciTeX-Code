#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 18:59:49 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/ScholarURLFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/ScholarURLFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
ScholarURLFinder - Main entry point for URL operations

Provides a clean API that wraps the functional modules.
Users can use this for convenience or directly import the functions.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

from .helpers import (
    build_url_doi,
    doi_to_url_publisher,
    extract_doi_from_url,
    find_all_urls,
    find_urls_pdf,
    generate_openurl_query,
    resolve_openurl,
)

logger = logging.getLogger(__name__)


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
        use_cache=True,
        clear_cache=False,
    ):
        """Initialize URL handler."""
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context
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

    async def find_urls(
        self, doi: str, page: Optional[Page] = None
    ) -> Dict[str, Any]:
        """Get all URL types for a doi following resolution pipeline."""
        # Check full results cache first
        if self.use_cache and doi in self._full_results_cache:
            logger.info(f"Using cached full results for DOI: {doi}")
            return self._full_results_cache[doi]

        urls = {}

        # Step 1: DOI URL
        urls["url_doi"] = build_url_doi(doi)

        # Step 2: Publisher URL (cached)
        url_publisher = await self._get_cached_publisher_url(doi)
        if url_publisher:
            urls["url_publisher"] = url_publisher

        # Step 3: OpenURL query
        if self.openurl_resolver_url:
            metadata = {"doi": doi}
            openurl_query = generate_openurl_query(
                metadata, self.openurl_resolver_url
            )
            if openurl_query:
                urls["url_openurl_query"] = openurl_query

                # Step 4: OpenURL resolved (cached)
                resolved_url = await self._get_cached_openurl(openurl_query)
                if resolved_url:
                    urls["url_openurl_resolved"] = resolved_url

        # Step 5: Collect PDF URLs
        urls_pdf = []

        # Try OpenURL resolved first (authenticated)
        if urls.get("url_openurl_resolved"):
            pdfs = await self._get_pdfs_from_url(
                urls["url_openurl_resolved"], page
            )
            urls_pdf.extend(pdfs)

        # Try publisher URL
        if urls.get("url_publisher"):
            pdfs = await self._get_pdfs_from_url(urls["url_publisher"], page)
            urls_pdf.extend(pdfs)

        if urls_pdf:
            urls["urls_pdf"] = urls_pdf

        # Cache full results
        if self.use_cache:
            self._full_results_cache[doi] = urls
            self._save_cache(
                self.full_results_cache_file, self._full_results_cache
            )

        return urls

    async def find_urls_batch(
        self, dois: List[str], max_concurrent: int = 8
    ) -> List[Dict[str, Any]]:
        """Get all URL types for multiple DOIs in batch with parallel processing."""
        if not dois:
            return []

        semaphore = asyncio.Semaphore(max_concurrent)

        async def find_urls_with_semaphore(doi: str):
            async with semaphore:
                # Check cache first - no page needed
                if self.use_cache and doi in self._full_results_cache:
                    return self._full_results_cache[doi]

                page = await self.context.new_page()
                try:
                    return await self.find_urls(doi=doi, page=page)
                finally:
                    await page.close()

        # Create tasks for parallel execution
        tasks = [find_urls_with_semaphore(doi) for doi in dois]

        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        batch_results = []
        for ii_result, result in enumerate(results):
            if isinstance(result, Exception):
                logger.debug(
                    f"Batch URL finding error for DOI {ii_result}: {result}"
                )
                batch_results.append({})
            else:
                # logger.info(
                #     f"Batch URL finder found for DOI {ii_result}: {result}"
                # )
                batch_results.append(result or {})

        # Success Rate
        n_dois = len(dois)
        if n_dois:
            n_found = sum(
                1
                for result in results
                if not isinstance(result, Exception)
                and result
                and result.get("urls_pdf")
            )
            msg = f"Found {n_found}/{n_dois} PDFs (= {100. * n_found / n_dois:.1f}%)"
            if n_found == n_dois:
                logger.success(msg)
            else:
                logger.warn(msg)

        # # Success Rate
        # n_dois = len(dois)
        # if n_dois:
        #     try:
        #         n_found = sum(
        #             [
        #                 True if result and result.get("urls_pdf") else False
        #                 for result in results
        #             ]
        #         )
        #     msg = f"Found {n_found}/{n_dois} PDFs (= {100. * n_found / n_dois:.1f}%)"
        #     if n_found == n_dois:
        #         logger.success(msg)
        #     else:
        #         logger.warn(msg)

        return batch_results

    async def _get_pdfs_from_url(
        self, url: str, page: Optional[Page], doi: str = None
    ) -> List[Dict]:
        """Get PDF URLs from a specific URL."""
        if not page:
            page = await self.context.new_page()
            should_close = True
        else:
            should_close = False

        try:
            # await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)

            pdfs = await find_urls_pdf(page)

            # Take screenshot if no PDFs found
            if not pdfs:
                await self._take_debug_screenshot(page, "no_pdfs_found", doi)

            return pdfs
        except Exception as e:
            # Take screenshot on error
            try:
                await self._take_debug_screenshot(page, "page_error", doi)
            except:
                pass
            return []
        finally:
            if should_close:
                try:
                    await page.close()
                except:
                    pass

    # async def _take_debug_screenshot(
    #     self, page: Page, context: str, doi: str = None
    # ):
    #     """Take screenshot for debugging when PDFs not found."""
    #     try:
    #         screenshot_dir = self.config.get_screenshots_dir("url_finder")
    #         screenshot_dir.mkdir(parents=True, exist_ok=True)

    #         # Generate filename with timestamp and context
    #         from datetime import datetime

    #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #         doi_clean = (
    #             doi.replace("/", "_").replace(":", "_") if doi else "unknown"
    #         )
    #         filename = f"{timestamp}_{context}_{doi_clean}.png"

    #         screenshot_path = screenshot_dir / filename
    #         await page.screenshot(path=str(screenshot_path), full_page=True)
    #         logger.success(f"Debug screenshot saved: {filename}")

    #     except Exception as e:
    #         logger.fail(f"Failed to take debug screenshot: {e}")
    async def _take_debug_screenshot(
        self, page: Page, context: str, doi: str = None
    ):
        """Take screenshot for debugging when PDFs not found."""
        try:
            screenshot_dir = self.config.get_screenshots_dir("url_finder")
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doi_clean = (
                doi.replace("/", "_").replace(":", "_") if doi else "unknown"
            )
            filename = f"{timestamp}_{context}_{doi_clean}.png"
            screenshot_path = screenshot_dir / filename

            # Skip font loading wait
            await page.screenshot(
                path=str(screenshot_path), full_page=True, timeout=10000
            )
            logger.success(f"Debug screenshot saved: {filename}")

        except Exception as e:
            logger.fail(f"Failed to take debug screenshot: {e}")

    async def find_urls_pdf_async(self, page_or_url) -> List[Dict]:
        """Find PDF URLs from a page or URL."""
        if isinstance(page_or_url, str):
            if not self.context:
                logger.error("Browser context required to navigate to URL")
                return []

            page = await self.context.new_page()
            try:
                # await page.goto(
                #     page_or_url, wait_until="networkidle", timeout=30000
                # )
                await page.goto(
                    page_or_url, wait_until="domcontentloaded", timeout=30000
                )

                pdfs = await find_urls_pdf(page)

                # Take screenshot if no PDFs found
                if not pdfs:
                    await self._take_debug_screenshot(
                        page, "no_pdfs_url", page_or_url
                    )

                return pdfs
            except Exception as e:
                logger.warning(f"Failed with networkidle: {e}")
                try:
                    await self._take_debug_screenshot(
                        page, "navigation_error", page_or_url
                    )
                except:
                    pass
                return []
            finally:
                await page.close()
        else:
            try:
                pdfs = await find_urls_pdf(page_or_url)

                # Take screenshot if no PDFs found
                if not pdfs:
                    await self._take_debug_screenshot(
                        page_or_url, "no_pdfs_page"
                    )

                return pdfs
            except Exception as e:
                logger.error(f"Error finding PDF URLs: {e}")
                try:
                    await self._take_debug_screenshot(
                        page_or_url, "pdf_search_error"
                    )
                except:
                    pass
                return []

    def generate_openurl(
        self, metadata: Dict, openurl_resolver_url: str
    ) -> Optional[str]:
        """Generate OpenURL query from metadata.

        Args:
            metadata: Paper metadata

        Returns:
            OpenURL query string
        """
        return generate_openurl_query(metadata, openurl_resolver_url)

    async def resolve_openurl_async(self, openurl_query: str) -> Optional[str]:
        """Resolve OpenURL to final authenticated URL."""
        if not self.context:
            logger.error("Browser context required for OpenURL resolution")
            return None
        return await resolve_openurl(openurl_query, self.context)

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

    @staticmethod
    def extract_doi(url: str) -> Optional[str]:
        """Extract DOI from a URL."""
        return extract_doi_from_url(url)

    # Cache
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
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_file}: {e}")

    async def _get_cached_publisher_url(self, doi: str) -> Optional[str]:
        """Get publisher URL with persistent caching."""
        if self.use_cache and doi in self._publisher_cache:
            logger.debug(f"Using cached publisher URL for DOI: {doi}")
            return self._publisher_cache[doi]

        result = await doi_to_url_publisher(doi, self.context)

        if self.use_cache:
            self._publisher_cache[doi] = result
            self._save_cache(self.publisher_cache_file, self._publisher_cache)

        return result

    async def _get_cached_openurl(self, openurl_query: str) -> Optional[str]:
        """Get resolved OpenURL with persistent caching."""
        if self.use_cache and openurl_query in self._openurl_cache:
            logger.debug(f"Using cached OpenURL resolution")
            return self._openurl_cache[openurl_query]

        result = await resolve_openurl(openurl_query, self.context)

        if self.use_cache:
            self._openurl_cache[openurl_query] = result
            self._save_cache(self.openurl_cache_file, self._openurl_cache)

        return result


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
            browser_mode="stealth",
            chrome_profile_name="system",
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        # Create URL handler
        url_finder = ScholarURLFinder(context, use_cache=False)

        # Get all URLs for a paper
        doi = "10.1016/j.cell.2025.07.007"  # Cell/Elsevier - Testing
        urls = await url_finder.find_urls(
            doi=doi,
        )
        pprint(urls)

    asyncio.run(main_async())

# python -m scitex.scholar.url.ScholarURLFinder

# EOF
