#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 06:16:27 (ywatanabe)"
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
        use_cache=True,
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
            logger.debug(f"Trying PDF extraction from publisher URL first...")
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
            # await page.goto(url, wait_until="networkidle", timeout=30_000)

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
        doi = "https://doi.org/10.1109/jbhi.2025.3556775"
        doi = "https://doi.org/10.1088/1741-2552/aaf92e"
        urls = await url_finder.find_urls(
            doi=doi,
        )
        pprint(urls)

    asyncio.run(main_async())


# Navigation: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=https://doi.org/10.1109/jbhi.2025.3556775 -> https://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=%22Publication%20Number%22:6221020&searchWithin=%22Volume%22:29&searchWithin=%22Issue%22:8&searchWithin=%22Start%20Page%22:5541
# INFO: Loaded 681 Zotero translators
# INFO: Loaded Zotero JavaScript modules successfully
# INFO: Executing Zotero translator: HighWire 2.0
# INFO: Closed popup with selector: button.close
# Translator error: ZU.fieldIsValidForType is not a function
# Zotero Translator did not extract any URLs from https://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=%22Publication%20Number%22:6221020&searchWithin=%22Volume%22:29&searchWithin=%22Issue%22:8&searchWithin=%22Start%20Page%22:5541
# FAIL: Not found any PDF URLs from https://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=%22Publication%20Number%22:6221020&searchWithin=%22Volume%22:29&searchWithin=%22Issue%22:8&searchWithin=%22Start%20Page%22:5541
# Screenshot saved: /home/ywatanabe/.scitex/scholar/workspace/screenshots/ScholarURLFinder/https:/doi.org/10.1109/jbhi.2025.3556775 - No PDFs Found-20251008_000358.png
# {'url_doi': 'https://doi.org/10.1109/jbhi.2025.3556775',
#  'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=https://doi.org/10.1109/jbhi.2025.3556775',
#  'url_openurl_resolved': 'https://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=%22Publication%20Number%22:6221020&searchWithin=%22Volume%22:29&searchWithin=%22Issue%22:8&searchWithin=%22Start%20Page%22:5541',
#  'url_publisher': 'https://ieeexplore.ieee.org/document/10946758'}

# python -m scitex.scholar.url.ScholarURLFinder

# EOF
