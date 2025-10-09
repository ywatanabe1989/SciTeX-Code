#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 03:24:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/find_pdf_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/find_pdf_urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, List

from playwright.async_api import Page

from scitex import logging
from scitex.browser import browser_logger
from scitex.scholar import ScholarConfig

from ._find_pdf_urls_by_direct_links import find_pdf_urls_by_direct_links
from ._find_pdf_urls_by_publisher_patterns import (
    find_pdf_urls_by_publisher_patterns,
)
from ._find_pdf_urls_by_view_button import find_pdf_urls_by_navigation
from ._find_pdf_urls_by_zotero_translators import (
    find_pdf_urls_by_zotero_translators,
)

logger = logging.getLogger(__name__)


async def _add_urls_to_collection(
    urls: List[str], source_name: str, urls_pdf: List[Dict], seen_urls: set
) -> None:
    for url in urls:
        if url not in seen_urls:
            seen_urls.add(url)
            urls_pdf.append({"url": url, "source": source_name})


async def _apply_strategy_zotero(
    page: Page,
    base_url: str,
    urls_pdf: List[Dict],
    seen_urls: set,
    func_name: str,
) -> None:
    await browser_logger.info(
        page,
        f"{func_name}: 1/4 Finding PDF URLs by Python Zotero translators...",
    )
    translator_urls = await find_pdf_urls_by_zotero_translators(
        page, base_url, func_name
    )
    await _add_urls_to_collection(
        translator_urls, "zotero_translator", urls_pdf, seen_urls
    )

    if translator_urls:
        await browser_logger.info(
            page,
            f"{func_name}: ✓ Python Zotero found {len(translator_urls)} URLs ({translator_urls})",
        )
        await page.wait_for_timeout(1000)

    return urls_pdf


async def _apply_strategy_direct_links(
    page: Page,
    config: ScholarConfig,
    urls_pdf: List[Dict],
    seen_urls: set,
    func_name: str,
) -> None:

    await browser_logger.info(
        page, f"{func_name}: 2/4 Finding PDF URLs by Direct PDF Links..."
    )
    direct_links = await find_pdf_urls_by_direct_links(page, config, func_name)
    await _add_urls_to_collection(
        direct_links, "direct_link", urls_pdf, seen_urls
    )

    if direct_links:
        await browser_logger.info(
            page, f"{func_name}: ✓ Direct links found {len(direct_links)} URLs"
        )
        await page.wait_for_timeout(1000)

    return urls_pdf


async def _apply_strategy_navigation(
    page: Page,
    config: ScholarConfig,
    urls_pdf: List[Dict],
    seen_urls: set,
    func_name: str,
) -> None:

    await browser_logger.info(
        page, f"{func_name}: 3/4 Finding PDF URLs by Navigation..."
    )

    elsevier_domains = ["sciencedirect.com", "cell.com", "elsevier.com"]
    if not any(domain in page.url.lower() for domain in elsevier_domains):
        return urls_pdf

    navigation_urls = await find_pdf_urls_by_navigation(
        page, config, func_name
    )

    for url in navigation_urls:
        if url not in seen_urls:
            seen_urls.add(url)

            replaced = False
            for ii, existing in enumerate(urls_pdf):
                if (
                    "/pdfft?" in existing["url"]
                    and "pdf.sciencedirectassets.com" in url
                ):
                    urls_pdf[ii] = {"url": url, "source": "navigation"}
                    replaced = True
                    break

            if not replaced:
                urls_pdf.append({"url": url, "source": "navigation"})

    return urls_pdf


async def _apply_strategy_publisher_patterns(
    page: Page,
    base_url: str,
    urls_pdf: List[Dict],
    seen_urls: set,
    func_name: str,
) -> None:

    await browser_logger.info(
        page, f"{func_name}: 4/4 Finding PDF URLs by Publisher Patterns..."
    )
    pattern_urls = find_pdf_urls_by_publisher_patterns(
        page, base_url, func_name
    )
    await _add_urls_to_collection(
        pattern_urls, "publisher_pattern", urls_pdf, seen_urls
    )

    if pattern_urls:
        await browser_logger.info(
            page, f"{func_name}: ✓ Patterns found {len(pattern_urls)} URLs"
        )
        await page.wait_for_timeout(1000)

    return urls_pdf


async def find_pdf_urls(
    page: Page,
    base_url: str = None,
    config: ScholarConfig = None,
    func_name="find_pdf_urls",
) -> List[Dict]:

    func_name = "find_pdf_urls"
    config = config or ScholarConfig()
    base_url = base_url or page.url

    urls_pdf = []
    seen_urls = set()

    await browser_logger.info(
        page, f"{func_name}: Finding PDFs at {base_url[:60]}..."
    )

    strategies = {
        "Zotero Translators": _apply_strategy_zotero,
        "Direct Links": _apply_strategy_direct_links,
        "Navigation": _apply_strategy_navigation,
        "Publisher Patterns": _apply_strategy_publisher_patterns,
    }
    strategies_tried = []
    for strategy_str, strategy in strategies.items():
        try:
            urls_pdf = await strategy(
                page, base_url, urls_pdf, seen_urls, func_name
            )
            strategies_tried.append(strategy_str)
            if urls_pdf:
                break
        except Exception as e:
            logger.warn(f"{func_name}: {str(e)}")

    strategies_not_tried = list(set(strategies.keys()) - set(strategies_tried))
    logger.success(f"Skippped {strategies_not_tried}")

    # await _log_final_results(page, urls_pdf, func_name)

    return urls_pdf

# EOF
