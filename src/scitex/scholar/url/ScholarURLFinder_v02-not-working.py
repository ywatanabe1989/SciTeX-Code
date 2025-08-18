#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 05:58:01 (ywatanabe)"
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
import hashlib
import json
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
    """Main entry point for all URL operations with caching."""

    def __init__(
        self,
        context: BrowserContext,
        openurl_resolver_url=None,
        config=None,
        cache_dir: Optional[Path] = None,
    ):
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context

        # Cache setup
        self.cache_dir = (
            cache_dir or Path.home() / ".scitex" / "scholar" / "url_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, doi: str) -> Path:
        """Get cache file path for DOI."""
        cache_key = hashlib.md5(doi.encode()).hexdigest()
        return self.cache_dir / f"{cache_key}.json"

    def _load_cache(self, doi: str) -> Optional[Dict[str, Any]]:
        """Load cached URLs for DOI."""
        cache_path = self._get_cache_path(doi)
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    cached_data = json.load(f)
                logger.debug(f"Loaded cached URLs for DOI: {doi}")
                return cached_data
            except Exception as ee:
                logger.warning(f"Failed to load cache: {ee}")
        return None

    def _save_cache(self, doi: str, urls: Dict[str, Any]) -> None:
        """Save URLs to cache."""
        cache_path = self._get_cache_path(doi)
        try:
            with open(cache_path, "w") as f:
                json.dump(urls, f, indent=2)
            logger.debug(f"Saved URLs to cache for DOI: {doi}")
        except Exception as ee:
            logger.warning(f"Failed to save cache: {ee}")

    async def find_urls(
        self, doi: str, page: Optional[Page] = None, use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get all URL types for a doi with caching."""
        # Try cache first
        if use_cache:
            cached_urls = self._load_cache(doi)
            if cached_urls:
                return cached_urls

        # Generate URLs
        urls = {}

        # Step 1: DOI URL
        urls["url_doi"] = build_url_doi(doi)

        # Step 2: Publisher URL (DOI resolution)
        url_publisher = await doi_to_url_publisher(doi, self.context)
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

                # Step 4: OpenURL resolved
                resolved_url = await resolve_openurl(
                    openurl_query, self.context
                )
                if resolved_url:
                    urls["url_openurl_resolved"] = resolved_url

        # Step 5: Collect PDF URLs
        urls_pdf = []

        # Try OpenURL resolved first
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

        # Save to cache
        if use_cache:
            self._save_cache(doi, urls)

        return urls

    async def find_urls_batch(
        self, dois: List[str], max_concurrent: int = 5, use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Get URLs for multiple DOIs with caching."""
        if not dois:
            return []

        semaphore = asyncio.Semaphore(max_concurrent)

        async def find_urls_with_semaphore(doi: str):
            async with semaphore:
                page = await self.context.new_page()
                try:
                    return await self.find_urls(
                        doi=doi, page=page, use_cache=use_cache
                    )
                finally:
                    await page.close()

        tasks = [find_urls_with_semaphore(doi) for doi in dois]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_results = []
        for ii_result, result in enumerate(results):
            if isinstance(result, Exception):
                logger.debug(
                    f"Batch URL finding error for DOI {ii_result}: {result}"
                )
                batch_results.append({})
            else:
                batch_results.append(result or {})

        return batch_results


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
            # browser_mode="stealth",
            browser_mode="interactive",
            chrome_profile_name="system",
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )

        # Create URL handler
        url_finder = ScholarURLFinder(context)

        # Get all URLs for a paper
        doi = "10.1016/j.cell.2025.07.007"  # Cell/Elsevier - Testing
        urls = await url_finder.find_urls(
            doi=doi,
        )
        pprint(urls)

    asyncio.run(main_async())

# python -m scitex.scholar.url.ScholarURLFinder

# EOF
