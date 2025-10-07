#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 13:17:53 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/resolvers/_resolve_functions.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

"""
URL Resolver Functions

Simple functions to resolve/convert between different URL types.
No classes, just functions that do one thing well.
"""

import asyncio
from typing import Optional

from playwright.async_api import Page

from scitex import logging
from scitex.scholar.browser.utils import show_popup_message_async, take_screenshot

from ._OpenURLResolver import OpenURLResolver

logger = logging.getLogger(__name__)


async def resolve_publisher_url_by_navigating_to_doi_page(
    doi: str, page: Page
) -> Optional[str]:
    """Resolve DOI to publisher URL by following redirects."""
    url_doi = f"https://doi.org/{doi}" if not doi.startswith("http") else doi

    await show_popup_message_async(
        page, "Finding Publisher URL by Navigating to DOI page..."
    )

    try:
        logger.info(f"Resolving DOI: {doi}")
        await page.goto(url_doi, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        url_publisher = page.url
        logger.success(
            f"Resolved Publisher URL by navigation: {doi}   ->   {url_publisher}"
        )
        return url_publisher
    except Exception as e:
        logger.error(f"Publisher URL not resolved by navigating to {doi}: {e}")
        await take_screenshot(
            page,
            "Resolve",
            f"{doi} - Publisher URL not resolved by navigating",
        )
        return None


async def resolve_openurl(openurl_query: str, page: Page) -> Optional[str]:
    """Resolve OpenURL to final authenticated URL."""
    resolver = OpenURLResolver()
    doi_match = re.search(r"doi=([^&]+)", openurl_query)
    doi = doi_match.group(1) if doi_match else ""

    return await resolver._resolve_query(openurl_query, page, doi)


def normalize_doi_as_http(doi: str) -> str:
    if doi.startswith("http"):
        return doi
    if doi.startswith("doi:"):
        doi = doi[4:]
    return f"https://doi.org/{doi}"


def extract_doi_from_url(url: str) -> Optional[str]:
    doi_pattern = r"10\.\d{4,}(?:\.\d+)*/[-._;()/:\w]+"
    match = re.search(doi_pattern, url)
    if match:
        return match.group(0)
    return None

# EOF
