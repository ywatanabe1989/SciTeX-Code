#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 03:24:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/gateway/_resolve_functions.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/gateway/_resolve_functions.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

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
from scitex.browser.debugging import browser_logger

from ._OpenURLResolver import OpenURLResolver

logger = logging.getLogger(__name__)


async def resolve_publisher_url_by_navigating_to_doi_page(
    doi: str,
    page: Page,
    func_name="resolve_publisher_url_by_navigating_to_doi_page",
) -> Optional[str]:
    """Resolve DOI to publisher URL by following redirects."""
    url_doi = f"https://doi.org/{doi}" if not doi.startswith("http") else doi

    await browser_logger.info(
        page,
        f"{func_name}: Finding Publisher URL by Navigating to DOI page...",
    )

    try:
        logger.info(f"{func_name}: Resolving DOI: {doi}")
        await page.goto(url_doi, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        url_publisher = page.url
        logger.success(
            f"{func_name}: Resolved Publisher URL by navigation: {doi}   ->   {url_publisher}"
        )
        return url_publisher
    except Exception as e:
        logger.error(
            f"{func_name}: Publisher URL not resolved by navigating to {doi}: {e}"
        )
        from pathlib import Path

        screenshot_dir = Path.home() / ".scitex/scholar/workspace/screenshots"
        await browser_logger.info(
            page,
            f"{func_name}: {doi} - Publisher URL not resolved by navigating",
            take_screenshot=True,
            screenshot_category="Resolve",
            screenshot_dir=screenshot_dir,
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
