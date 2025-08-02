#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 20:09:03 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_DOIToURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_DOIToURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-08-01 13:15:00"
# Author: Claude

"""
Convert DOIs to accessible publisher URLs using OpenURL resolvers.

This module implements Critical Task #5: Resolve publisher URLs from DOIs
using institutional OpenURL resolvers for authenticated access.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote, urlencode

import aiohttp
from playwright.async_api import Browser, Page, async_playwright

from scitex import logging

from ..browser.local import BrowserManager
from ..config import ScholarConfig
from ._OpenURLResolver import OpenURLResolver
from .KNOWN_RESOLVERS import KNOWN_RESOLVERS

logger = logging.getLogger(__name__)


class DOIToURLResolver:
    """Resolve DOIs to accessible publisher URLs via OpenURL."""

    def __init__(self, config: Optional[ScholarConfig] = None):
        """
        Initialize DOI to URL resolver.

        Args:
            config: Scholar configuration (uses default if not provided)
        """
        self.config = config or ScholarConfig()
        self.openurl_resolver = OpenURLResolver(config=self.config)

        # Cache for resolved URLs
        self.cache_dir = Path.home() / ".scitex" / "scholar" / "url_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "doi_url_cache.json"
        self.cache = self._load_cache()

        # Track failures for adaptive behavior
        self.failures = {}

    def _load_cache(self) -> Dict[str, Dict[str, any]]:
        """Load URL cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {}

    def _save_cache(self):
        """Save URL cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def _extract_doi_info(self, doi: str) -> Dict[str, str]:
        """Extract publisher and article ID from DOI."""
        # Common DOI patterns
        patterns = {
            "elsevier": r"10\.1016/(.+)",
            "springer": r"10\.1007/(.+)",
            "nature": r"10\.1038/(.+)",
            "wiley": r"10\.1002/(.+)",
            "ieee": r"10\.1109/(.+)",
            "acs": r"10\.1021/(.+)",
            "rsc": r"10\.1039/(.+)",
            "plos": r"10\.1371/(.+)",
            "frontiers": r"10\.3389/(.+)",
            "mdpi": r"10\.3390/(.+)",
            "oxford": r"10\.1093/(.+)",
            "sage": r"10\.1177/(.+)",
            "taylor_francis": r"10\.1080/(.+)",
            "apa": r"10\.1037/(.+)",
            "iop": r"10\.1088/(.+)",
        }

        for publisher, pattern in patterns.items():
            match = re.match(pattern, doi)
            if match:
                return {
                    "publisher": publisher,
                    "article_id": match.group(1),
                    "doi": doi,
                }

        # Generic pattern
        match = re.match(r"(10\.\d+)/(.+)", doi)
        if match:
            return {
                "publisher": "unknown",
                "prefix": match.group(1),
                "article_id": match.group(2),
                "doi": doi,
            }

        return {"doi": doi, "publisher": "unknown"}

    def _build_direct_urls(self, doi: str) -> List[str]:
        """Build potential direct publisher URLs for a DOI."""
        info = self._extract_doi_info(doi)
        urls = []

        # Always include standard DOI URL
        urls.append(f"https://doi.org/{doi}")

        # Publisher-specific patterns
        if info["publisher"] == "elsevier":
            # ScienceDirect pattern
            urls.append(
                f"https://www.sciencedirect.com/science/article/pii/{info['article_id']}"
            )

        elif info["publisher"] == "springer":
            # SpringerLink pattern
            urls.append(f"https://link.springer.com/article/{doi}")
            urls.append(f"https://link.springer.com/chapter/{doi}")

        elif info["publisher"] == "nature":
            # Nature pattern
            urls.append(
                f"https://www.nature.com/articles/{info['article_id']}"
            )

        elif info["publisher"] == "wiley":
            # Wiley Online Library pattern
            urls.append(f"https://onlinelibrary.wiley.com/doi/abs/{doi}")
            urls.append(f"https://onlinelibrary.wiley.com/doi/full/{doi}")

        elif info["publisher"] == "ieee":
            # IEEE Xplore pattern (needs document ID)
            urls.append(
                f"https://ieeexplore.ieee.org/document/{info['article_id']}"
            )

        elif info["publisher"] == "oxford":
            # Oxford Academic pattern
            urls.append(f"https://academic.oup.com/article-lookup/doi/{doi}")

        return urls

    async def resolve_single_async(
        self, doi: str, use_openurl: bool = True, verify_access: bool = True
    ) -> Optional[Dict[str, any]]:
        """
        Resolve a single DOI to accessible URL.

        Args:
            doi: DOI to resolve
            use_openurl: Whether to use OpenURL resolver
            verify_access: Whether to verify PDF access

        Returns:
            Dict with 'url', 'access_type', 'verified' fields if successful
        """
        # Check cache first
        if doi in self.cache:
            logger.debug(f"Using cached URL for {doi}")
            return self.cache[doi]

        result = None

        try:
            # Try OpenURL resolver first if configured
            if use_openurl and self.config.university_openurl:
                logger.info(f"Trying OpenURL resolver for {doi}")
                openurl_result = await self._try_openurl(doi)
                if openurl_result:
                    result = openurl_result

            # Try direct publisher URLs
            if not result:
                logger.info(f"Trying direct publisher URLs for {doi}")
                direct_result = await self._try_direct_urls(doi, verify_access)
                if direct_result:
                    result = direct_result

            # Cache successful result
            if result:
                self.cache[doi] = result
                self._save_cache()
                logger.success(f"Resolved {doi} to {result['url']}")
            else:
                logger.warning(f"Failed to resolve {doi}")

            return result

        except Exception as e:
            logger.error(f"Error resolving {doi}: {e}")
            return None

    async def _try_openurl(self, doi: str) -> Optional[Dict[str, any]]:
        """Try to resolve DOI using OpenURL."""
        try:
            # Build OpenURL query
            params = {
                "rft_id": f"info:doi/{doi}",
                "rft.genre": "article",
                "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
                "req_dat": "format=pdf",
            }

            openurl = f"{self.config.university_openurl}?{urlencode(params)}"

            # Use the OpenURL resolver to navigate
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    # Navigate to OpenURL
                    await page.goto(
                        openurl, wait_until="networkidle", timeout=30000
                    )

                    # Wait for potential redirects
                    await page.wait_for_timeout(3000)

                    # Get final URL
                    final_url = page.url

                    # Check if we reached a publisher page
                    if "doi.org" not in final_url and any(
                        domain in final_url
                        for domain in [
                            "sciencedirect",
                            "springer",
                            "nature",
                            "wiley",
                            "ieee",
                        ]
                    ):
                        # Check for PDF access
                        pdf_available = await self._check_pdf_access(page)

                        return {
                            "url": final_url,
                            "access_type": "openurl",
                            "pdf_available": pdf_available,
                            "verified": True,
                        }

                finally:
                    await browser.close()

        except Exception as e:
            logger.debug(f"OpenURL resolution failed for {doi}: {e}")

        return None

    async def _try_direct_urls(
        self, doi: str, verify_access: bool = True
    ) -> Optional[Dict[str, any]]:
        """Try direct publisher URLs."""
        urls = self._build_direct_urls(doi)

        for url in urls:
            try:
                if verify_access:
                    # Verify with browser
                    result = await self._verify_url_access(url)
                    if result:
                        return {
                            "url": url,
                            "access_type": "direct",
                            "pdf_available": result.get(
                                "pdf_available", False
                            ),
                            "verified": True,
                        }
                else:
                    # Just check if URL responds
                    async with aiohttp.ClientSession() as session:
                        async with session.head(
                            url, allow_redirects=True
                        ) as resp:
                            if resp.status == 200:
                                return {
                                    "url": url,
                                    "access_type": "direct",
                                    "verified": False,
                                }

            except Exception as e:
                logger.debug(f"Failed to access {url}: {e}")
                continue

        return None

    async def _verify_url_access(self, url: str) -> Optional[Dict[str, any]]:
        """Verify URL provides article access."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    # Navigate to URL
                    await page.goto(
                        url, wait_until="networkidle", timeout=30000
                    )

                    # Check for common paywall indicators
                    paywall_indicators = [
                        "purchase",
                        "buy",
                        "subscribe",
                        "access denied",
                        "log in",
                        "sign in",
                        "institutional login",
                    ]

                    page_text = await page.content()
                    page_text_lower = page_text.lower()

                    has_paywall = any(
                        indicator in page_text_lower
                        for indicator in paywall_indicators
                    )

                    # Check for PDF access
                    pdf_available = await self._check_pdf_access(page)

                    if not has_paywall or pdf_available:
                        return {
                            "pdf_available": pdf_available,
                            "has_paywall": has_paywall,
                        }

                finally:
                    await browser.close()

        except Exception as e:
            logger.debug(f"Failed to verify {url}: {e}")

        return None

    async def _check_pdf_access(self, page: Page) -> bool:
        """Check if PDF download is available on the page."""
        try:
            # Look for PDF download links/buttons
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="/pdf/"]',
                'button:has-text("Download PDF")',
                'a:has-text("Download PDF")',
                'a:has-text("View PDF")',
                'a:has-text("Full Text PDF")',
                ".pdf-download",
                '[class*="pdf-link"]',
            ]

            for selector in pdf_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    return True

            # Check for embedded PDF viewer
            pdf_viewers = await page.query_selector_all(
                'iframe[src*="pdf"], embed[type="application/pdf"]'
            )
            if pdf_viewers:
                return True

        except Exception as e:
            logger.debug(f"Error checking PDF access: {e}")

        return False

    async def resolve_batch_async(
        self, dois: List[str], max_concurrent: int = 3, progress_callback=None
    ) -> Dict[str, Dict[str, any]]:
        """
        Resolve multiple DOIs concurrently.

        Args:
            dois: List of DOIs to resolve
            max_concurrent: Maximum concurrent resolutions
            progress_callback: Optional callback for progress updates

        Returns:
            Dict mapping DOIs to resolution results
        """
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)

        async def resolve_with_limit(doi: str, index: int):
            async with semaphore:
                if progress_callback:
                    progress_callback(index, len(dois), f"Resolving {doi}")

                result = await self.resolve_single_async(doi)
                results[doi] = result
                return doi, result

        # Create tasks
        tasks = [resolve_with_limit(doi, i) for i, doi in enumerate(dois)]

        # Process all DOIs
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def resolve_from_bibtex(
        self, bibtex_path: Path, output_path: Optional[Path] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        Resolve URLs for all DOIs in a BibTeX file.

        Args:
            bibtex_path: Path to BibTeX file
            output_path: Optional path for updated BibTeX

        Returns:
            Dict mapping DOIs to resolution results
        """
        import bibtexparser

        # Load BibTeX
        with open(bibtex_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        # Extract DOIs
        dois = []
        doi_to_entry = {}

        for entry in bib_db.entries:
            if "doi" in entry:
                doi = entry["doi"]
                dois.append(doi)
                doi_to_entry[doi] = entry

        logger.info(f"Found {len(dois)} DOIs in {bibtex_path}")

        # Resolve URLs
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(self.resolve_batch_async(dois))
        finally:
            loop.close()

        # Update BibTeX entries with URLs
        success_count = 0
        for doi, result in results.items():
            if result and result.get("url"):
                entry = doi_to_entry[doi]
                entry["url"] = result["url"]
                entry["url_source"] = result["access_type"]
                if result.get("pdf_available"):
                    entry["pdf_available"] = "yes"
                success_count += 1

        logger.info(f"Resolved URLs for {success_count}/{len(dois)} DOIs")

        # Save updated BibTeX if requested
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                bibtexparser.dump(bib_db, f)
            logger.info(f"Saved updated BibTeX to {output_path}")

        return results


async def main():
    """Command-line interface for DOI to URL resolution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Resolve DOIs to accessible publisher URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve single DOI
  python -m scitex.scholar.open_url.resolve_urls --doi "10.1038/nature12373"

  # Resolve DOIs from BibTeX file
  python -m scitex.scholar.open_url.resolve_urls --bibtex papers.bib

  # Save URLs to new BibTeX file
  python -m scitex.scholar.open_url.resolve_urls --bibtex papers.bib --output papers-with-urls.bib
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument("--doi", type=str, help="Single DOI to resolve")

    input_group.add_argument(
        "--bibtex", "-b", type=str, help="BibTeX file containing DOIs"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output BibTeX file (for --bibtex mode)",
    )

    parser.add_argument(
        "--no-verify", action="store_true", help="Skip access verification"
    )

    args = parser.parse_args()

    # Initialize resolver
    resolver = DOIToURLResolver()

    if args.doi:
        # Single DOI mode
        result = await resolver.resolve_single_async(
            args.doi, verify_access=not args.no_verify
        )

        if result:
            print(f"\nResolved URL: {result['url']}")
            print(f"Access type: {result['access_type']}")
            if "pdf_available" in result:
                print(
                    f"PDF available: {'Yes' if result['pdf_available'] else 'No'}"
                )
        else:
            print("\nFailed to resolve DOI")

    else:
        # BibTeX mode
        results = resolver.resolve_from_bibtex(
            Path(args.bibtex), Path(args.output) if args.output else None
        )

        # Print summary
        success = sum(1 for r in results.values() if r and r.get("url"))
        print(f"\nResolved {success}/{len(results)} DOIs")

        # Show first few results
        for doi, result in list(results.items())[:5]:
            if result:
                print(f"\n{doi}:")
                print(f"  URL: {result['url']}")
                print(f"  Type: {result['access_type']}")


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))

# EOF
