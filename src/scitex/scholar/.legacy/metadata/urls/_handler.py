#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 16:21:23 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/urls/_handler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/urls/_handler.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URLHandler - Main entry point for URL operations

Provides a clean API that wraps the functional modules.
Users can use this for convenience or directly import the functions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar.config import ScholarConfig

# Import functional modules
from ._finder import find_all_urls, find_pdf_urls, find_supplementary_urls
from ._resolver import (
    build_url_doi,
    doi_to_url_publisher,
    extract_doi_from_url,
    generate_openurl_query,
    resolve_all_urls,
    resolve_openurl,
)

logger = logging.getLogger(__name__)


class URLHandler:
    """
    Main entry point for all URL operations.

    Wraps functional modules for convenience while keeping them accessible
    for direct use when needed.
    """

    def __init__(
        self,
        context: BrowserContext = None,
        openurl_resolver_url=None,
        config=None,
    ):
        """
        Initialize URL handler.

        Args:
            context: Authenticated browser context (optional)
        """
        self.context = context
        self.config = config or ScholarConfig()
        self.openurl_resolver_url = self.config.resolve(
            "openurl_resolver_url", openurl_resolver_url
        )

    async def get_all_urls(
        self,
        doi: str = None,
        title: str = None,
        metadata: Dict = None,
        page: Page = None,
    ) -> Dict[str, Any]:
        """
        Get all URL types for a paper.

        Args:
            doi: DOI string
            title: Paper title (for OpenURL)
            metadata: Full metadata dict (for OpenURL)
            page: Current page (for PDF extraction)

        Returns:
            Dict with all resolved URLs
        """
        urls = {}

        # If we have metadata, use it
        if metadata:
            # Use the functional resolver
            urls = await resolve_all_urls(
                metadata, self.openurl_resolver_url, self.context
            )

        # If we have a DOI, resolve it
        elif doi:
            urls["url_doi"] = build_url_doi(doi)

            if self.context:
                try:
                    url_publisher = await doi_to_url_publisher(
                        doi, self.context
                    )
                    if url_publisher:
                        urls["url_publisher"] = url_publisher

                        # Try to get PDF URLs from publisher page
                        if not page:
                            page = await self.context.new_page()
                        try:
                            await page.goto(
                                url_publisher,
                                wait_until="domcontentloaded",
                                timeout=30000,
                            )
                            pdf_urls = await find_pdf_urls(page)
                            if pdf_urls:
                                urls["url_pdf"] = pdf_urls
                        except Exception as e:
                            logger.warning(
                                f"Failed to navigate to publisher URL: {e}"
                            )
                            # Try with networkidle instead
                            try:
                                await page.goto(
                                    url_publisher,
                                    wait_until="networkidle",
                                    timeout=30000,
                                )
                                pdf_urls = await find_pdf_urls(page)
                                if pdf_urls:
                                    urls["url_pdf"] = pdf_urls
                            except Exception as e2:
                                logger.error(
                                    f"Could not access publisher page: {e2}"
                                )

                        # Extract all URLs from page before closing
                        if page:
                            try:
                                page_urls = await find_all_urls(page)
                                if page_urls.get("pdf"):
                                    urls["url_pdf"] = page_urls["pdf"]
                                if page_urls.get("supplementary"):
                                    urls["url_supplementary"] = page_urls[
                                        "supplementary"
                                    ]
                            except Exception as e:
                                logger.error(
                                    f"Error extracting URLs from page: {e}"
                                )

                        # Now close the page
                        try:
                            await page.close()
                        except:
                            pass  # Page might already be closed

                except Exception as e:
                    logger.error(f"Error resolving DOI {doi}: {e}")

        return urls

    async def find_pdf_urls_async(self, page_or_url) -> List[Dict]:
        """
        Find PDF URLs from a page or URL.

        Args:
            page_or_url: Page object or URL string

        Returns:
            List of dicts with url, source, and reliability
        """
        if isinstance(page_or_url, str):
            # Create a page and navigate
            if not self.context:
                logger.error("Browser context required to navigate to URL")
                return []

            page = await self.context.new_page()
            try:
                await page.goto(
                    page_or_url, wait_until="domcontentloaded", timeout=30000
                )
                return await find_pdf_urls(page)
            except Exception as e:
                logger.warning(
                    f"Failed with domcontentloaded, trying networkidle: {e}"
                )
                try:
                    await page.goto(
                        page_or_url, wait_until="networkidle", timeout=30000
                    )
                    return await find_pdf_urls(page)
                except Exception as e2:
                    logger.error(f"Could not navigate to {page_or_url}: {e2}")
                    return []
            finally:
                await page.close()
        else:
            # Assume it's a Page object
            try:
                return await find_pdf_urls(page_or_url)
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


# Convenience functions for direct use without instantiating the class


async def get_all_urls(
    doi: str = None,
    title: str = None,
    metadata: Dict = None,
    context: BrowserContext = None,
) -> Dict[str, Any]:
    """
    Convenience function to get all URLs without instantiating URLHandler.

    See URLHandler.get_all_urls for details.
    """
    handler = URLHandler(context)
    return await handler.get_all_urls(doi, title, metadata)


def update_metadata_urls(metadata_path: Path, urls: Dict) -> bool:
    """
    Convenience function to update metadata without instantiating URLHandler.

    See URLHandler.update_metadata for details.
    """
    handler = URLHandler()
    return handler.update_metadata(metadata_path, urls)

# EOF
