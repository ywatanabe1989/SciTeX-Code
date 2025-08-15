#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 22:01:33 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/_resolve_functions.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/_resolve_functions.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

"""
URL Resolver Functions

Simple functions to resolve/convert between different URL types.
No classes, just functions that do one thing well.
"""

import asyncio
from typing import Dict, Optional
from urllib.parse import quote

from playwright.async_api import BrowserContext, Page

from scitex import logging

logger = logging.getLogger(__name__)


async def doi_to_url_publisher(
    doi: str, context: BrowserContext = None
) -> Optional[str]:
    """
    Resolve DOI to publisher URL by following redirects.

    Args:
        doi: DOI string (with or without https://doi.org/ prefix)
        context: Browser context for authenticated resolution

    Returns:
        Publisher URL after following DOI redirect
    """
    # Ensure DOI URL format
    if not doi.startswith("http"):
        url_doi = f"https://doi.org/{doi}"
    else:
        url_doi = doi

    if context:
        # Use browser to follow redirects (handles authentication)
        page = await context.new_page()
        try:
            logger.info(f"Resolving DOI: {doi}")
            await page.goto(
                url_doi, wait_until="domcontentloaded", timeout=30000
            )
            await asyncio.sleep(2)  # Let redirects settle

            url_publisher = page.url
            logger.info(f"Resolved to: {url_publisher}")
            return url_publisher

        except Exception as e:
            logger.error(f"Failed to resolve DOI: {e}")
            return None
        finally:
            await page.close()
    else:
        # Simple HTTP redirect following (no authentication)
        import httpx

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url_doi)
                return str(response.url)
        except Exception as e:
            logger.error(f"Failed to resolve DOI: {e}")
            return None


def generate_openurl_query(
    metadata: Dict,
    openurl_resolver_url: str,
) -> Optional[str]:
    """
    Generate OpenURL query from metadata.

    Args:
        metadata: Paper metadata dict
        openurl_resolver_url: Institution's OpenURL resolver base URL

    Returns:
        OpenURL query string
    """
    params = []

    # Add source identifier
    params.append("sid=scitex")

    # Add DOI if available
    if metadata.get("doi"):
        params.append(f"doi={metadata['doi']}")

    # Add title
    if metadata.get("title"):
        params.append(f"atitle={quote(metadata['title'][:200])}")

    # Add journal
    if metadata.get("journal"):
        params.append(f"jtitle={quote(metadata['journal'])}")

    # Add year
    if metadata.get("year"):
        params.append(f"date={metadata['year']}")

    # Add volume/issue/pages
    if metadata.get("volume"):
        params.append(f"volume={metadata['volume']}")
    if metadata.get("issue"):
        params.append(f"issue={metadata['issue']}")
    if metadata.get("pages"):
        params.append(f"pages={metadata['pages']}")

    # Add first author
    if metadata.get("authors"):
        authors = metadata["authors"]
        if isinstance(authors, list) and authors:
            first_author = authors[0]
            if isinstance(first_author, str):
                # Parse "Last, First" or "First Last" format
                if "," in first_author:
                    last, first = first_author.split(",", 1)
                    params.append(f"aulast={quote(last.strip())}")
                    params.append(f"aufirst={quote(first.strip())}")
                else:
                    parts = first_author.strip().split()
                    if parts:
                        params.append(f"aulast={quote(parts[-1])}")
                        if len(parts) > 1:
                            params.append(f"aufirst={quote(parts[0])}")
            elif isinstance(first_author, dict):
                if first_author.get("lastName"):
                    params.append(f"aulast={quote(first_author['lastName'])}")
                if first_author.get("firstName"):
                    params.append(
                        f"aufirst={quote(first_author['firstName'])}"
                    )

    # Add ISSN if available
    if metadata.get("issn"):
        params.append(f"issn={metadata['issn']}")

    if params:
        return f"{openurl_resolver_url}?{'&'.join(params)}"

    return None


from ._ResolverLinkFinder import ResolverLinkFinder


async def resolve_openurl(
    openurl_query: str, context: BrowserContext
) -> Optional[str]:
    page = await context.new_page()
    try:
        await page.goto(
            openurl_query, wait_until="domcontentloaded", timeout=60000
        )
        await page.wait_for_timeout(3000)

        # Debug all links on the page
        links_info = await page.evaluate(
            """
            () => {
                return Array.from(document.querySelectorAll('a[href]')).map(link => ({
                    href: link.href,
                    text: link.textContent.trim(),
                    classes: link.className,
                    id: link.id
                }));
            }
        """
        )

        for link_info in links_info:
            logger.debug(
                f"Link: {link_info['text'][:30]} -> {link_info['href'][:60]}"
            )

        doi_match = re.search(r"doi=([^&]+)", openurl_query)
        doi = doi_match.group(1) if doi_match else ""

        finder = ResolverLinkFinder()
        link = await finder.find_link(page, doi)

        if link:
            success = await finder.click_and_wait(page, link)
            if success:
                return page.url

        return None

    except Exception as e:
        logger.error(f"OpenURL resolution failed: {e}")
    finally:
        await page.close()

    return None


async def _wait_for_captcha_resolution_async(page: Page, max_wait: int = 60):
    """Wait for CAPTCHA to be resolved by extensions or manual intervention."""
    for attempt in range(max_wait):
        # Check if CAPTCHA is still present
        captcha_present = await page.evaluate(
            """
            () => {
                // Common CAPTCHA indicators
                const captchaElements = [
                    'iframe[src*="captcha"]',
                    'iframe[src*="recaptcha"]',
                    '.cf-challenge-form',
                    '[data-captcha]',
                    '#captcha'
                ];

                return captchaElements.some(selector => {
                    const element = document.querySelector(selector);
                    return element && element.offsetParent !== null;
                });
            }
        """
        )

        if not captcha_present:
            logger.success("CAPTCHA resolved")
            return True

        if attempt % 10 == 0:
            logger.info(f"Waiting for CAPTCHA resolution... ({attempt}s)")

        await page.wait_for_timeout(1000)

    logger.error("CAPTCHA resolution timeout")
    return False


def build_url_doi(doi: str) -> str:
    """
    Build standard DOI URL from DOI string.

    Args:
        doi: DOI string (with or without prefix)

    Returns:
        Full DOI URL
    """
    if doi.startswith("http"):
        return doi
    if doi.startswith("doi:"):
        doi = doi[4:]
    return f"https://doi.org/{doi}"


def extract_doi_from_url(url: str) -> Optional[str]:
    """
    Extract DOI from a URL if present.

    Args:
        url: Any URL that might contain a DOI

    Returns:
        DOI string if found
    """
    import re

    # Pattern for DOI
    doi_pattern = r"10\.\d{4,}(?:\.\d+)*/[-._;()/:\w]+"

    match = re.search(doi_pattern, url)
    if match:
        return match.group(0)

    return None


# Convenience function to resolve all URL types
async def resolve_all_urls(
    metadata: Dict, openurl_resolver_url: str, context: BrowserContext = None
) -> Dict[str, any]:
    """
    Resolve all URL types from metadata.

    Args:
        metadata: Paper metadata
        context: Browser context for authenticated resolution

    Returns:
        Dict with all resolved URLs
    """
    urls = {}

    # Build DOI URL
    if metadata.get("doi"):
        urls["url_doi"] = build_url_doi(metadata["doi"])

        # Resolve to publisher
        if context:
            url_publisher = await doi_to_url_publisher(
                metadata["doi"], context
            )
            if url_publisher:
                urls["url_publisher"] = url_publisher

    # Generate OpenURL query
    openurl_query = generate_openurl_query(metadata, openurl_resolver_url)
    if openurl_query:
        urls["url_openurl_query"] = openurl_query

        # Resolve OpenURL if context available
        if context:
            resolved = await resolve_openurl(openurl_query, context)
            if resolved:
                urls["url_openurl_resolved"] = resolved

    return urls

# EOF
