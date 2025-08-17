#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 20:17:32 (ywatanabe)"
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

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

# from .helpers import # resolve_all_urls
# from .helpers import # find_supplementary_urls
# Import functional modules
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
    """
    Main entry point for all URL operations.

    Wraps functional modules for convenience while keeping them accessible
    for direct use when needed.
    """

    URL_TYPES = [
        "urls_pdf",
        "url_doi" "url_openurl_query",
        "url_openurl_resolved",
        "url_publisher",
    ]

    def __init__(
        self,
        context: BrowserContext,
        openurl_resolver_url=None,
        config=None,
    ):
        """
        Initialize URL handler.

        Args:
            context: Authenticated browser context (optional)
        """
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )
        self.context = context

    async def find_urls(
        self, doi: str, page: Optional[Page] = None
    ) -> Dict[str, Any]:
        """Get all URL types for a doi following resolution pipeline."""
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

        # Step 5: Collect PDF URLs from all sources
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

        return urls

    async def _get_pdfs_from_url(
        self, url: str, page: Optional[Page]
    ) -> List[Dict]:
        """Get PDF URLs from a specific URL."""
        if not page:
            page = await self.context.new_page()
            should_close = True
        else:
            should_close = False

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            return await find_urls_pdf(page)
        except:
            return []
        finally:
            if should_close:
                try:
                    await page.close()
                except:
                    pass

    async def _try_openurl_resolution(
        self, doi: str, urls: Dict, page: Optional[Page]
    ) -> None:
        """Try OpenURL resolution for PDFs."""
        if not self.openurl_resolver_url:
            return

        metadata = {"doi": doi}
        openurl_query = generate_openurl_query(
            metadata, self.openurl_resolver_url
        )
        if not openurl_query:
            return

        urls["url_openurl_query"] = openurl_query
        resolved_url = await resolve_openurl(openurl_query, self.context)
        if not resolved_url:
            return

        urls["url_openurl_resolved"] = resolved_url
        await self._extract_pdfs_from_url(resolved_url, urls, page)

    async def _try_publisher_resolution(
        self, doi: str, urls: Dict, page: Optional[Page]
    ) -> None:
        """Try direct publisher resolution for PDFs."""
        url_publisher = await doi_to_url_publisher(doi, self.context)
        if not url_publisher:
            return

        urls["url_publisher"] = url_publisher
        await self._extract_pdfs_from_url(url_publisher, urls, page)

    async def _extract_pdfs_from_url(
        self, url: str, urls: Dict, page: Optional[Page]
    ) -> None:
        """Extract PDF URLs from a given URL."""
        if not page:
            page = await self.context.new_page()
            should_close = True
        else:
            should_close = False

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            urls_pdf = await find_urls_pdf(page)
            if urls_pdf:
                urls["url_pdf"] = urls_pdf
        except Exception as e:
            logger.warning(f"Failed with domcontentloaded: {e}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                urls_pdf = await find_urls_pdf(page)
                if urls_pdf:
                    urls["url_pdf"] = urls_pdf
            except Exception as e2:
                logger.error(f"Could not access URL {url}: {e2}")

        try:
            page_urls = await find_all_urls(page)
            if page_urls.get("pdf"):
                urls["url_pdf"] = page_urls["pdf"]
            if page_urls.get("supplementary"):
                urls["url_supplementary"] = page_urls["supplementary"]
        except Exception as e:
            logger.error(f"Error extracting URLs from page: {e}")

        if should_close:
            try:
                await page.close()
            except:
                pass

    async def find_urls_pdf_async(self, page_or_url) -> List[Dict]:
        """
        Find PDF URLs from a page or URL.

        Args:
            page_or_url: Page object or URL string

        Returns:
            List of dicts with url and source
        """
        if isinstance(page_or_url, str):
            # Create a page and navigate
            if not self.context:
                logger.error("Browser context required to navigate to URL")
                return []

            page = await self.context.new_page()
            try:
                await page.goto(
                    page_or_url, wait_until="networkidle", timeout=30000
                )
                return await find_urls_pdf(page)
            except Exception as e:
                logger.warning(
                    f"Failed with domcontentloaded, trying networkidle: {e}"
                )
                try:
                    await page.goto(
                        page_or_url, wait_until="networkidle", timeout=30000
                    )
                    return await find_urls_pdf(page)
                except Exception as e2:
                    logger.error(f"Could not navigate to {page_or_url}: {e2}")
                    return []
            finally:
                await page.close()
        else:
            # Assume it's a Page object
            try:
                return await find_urls_pdf(page_or_url)
            except Exception as e:
                logger.error(f"Error finding PDF URLs: {e}")
                return []

    def generate_openurl(
        self, metadata: Dict, openurl_resolver_url: str
    ) -> Optional[str]:
        """
        Generate OpenURL query from metadata.

        Args:
            metadata: Paper metadata

        Returns:
            OpenURL query string
        """
        return generate_openurl_query(metadata, openurl_resolver_url)

    async def resolve_openurl_async(self, openurl_query: str) -> Optional[str]:
        """
        Resolve OpenURL to final authenticated URL.

        Args:
            openurl_query: OpenURL query string

        Returns:
            Final resolved URL
        """
        if not self.context:
            logger.error("Browser context required for OpenURL resolution")
            return None

        return await resolve_openurl(openurl_query, self.context)

    def update_metadata(self, metadata_path: Path, urls: Dict) -> bool:
        """
        Update metadata file with resolved URLs.

        Args:
            metadata_path: Path to metadata.json
            urls: URLs to add/update

        Returns:
            True if updated successfully
        """
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
        """
        Get URLs from metadata file.

        Args:
            metadata_path: Path to metadata.json

        Returns:
            URLs dict from metadata
        """
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            return metadata.get("urls", {})

        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return {}

    @staticmethod
    def extract_doi(url: str) -> Optional[str]:
        """
        Extract DOI from a URL.

        Args:
            url: Any URL that might contain a DOI

        Returns:
            DOI string if found
        """
        return extract_doi_from_url(url)


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
