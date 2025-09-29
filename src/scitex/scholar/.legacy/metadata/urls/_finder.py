#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 01:01:43 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/urls/_finder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/urls/_finder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL Finder Functions

Simple functions to find/extract URLs from web pages and metadata.
No classes, just functions that do one thing well.
"""

from typing import Dict, List
from urllib.parse import urljoin

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


async def find_pdf_urls(page: Page, base_url: str = None) -> List[Dict]:
    """
    Find PDF URLs in a web page using multiple strategies.

    Args:
        page: Playwright page object
        base_url: Base URL for relative links

    Returns:
        List of dicts with url, source, and reliability info
    """
    if base_url is None:
        base_url = page.url

    pdf_urls = []
    seen_urls = set()

    # Strategy 1: Try Zotero translator FIRST (most reliable)
    translator_urls = await _find_with_zotero_translator(page, base_url)
    for url in translator_urls:
        if url not in seen_urls:
            seen_urls.add(url)
            pdf_urls.append(
                {
                    "url": url,
                    "source": "zotero_translator",
                    "reliability": "high",
                }
            )

    # Strategy 2: Find direct PDF links (fallback if no translator)
    direct_links = await _find_direct_pdf_links(page)
    for url in direct_links:
        if url not in seen_urls:
            seen_urls.add(url)
            pdf_urls.append(
                {"url": url, "source": "direct_link", "reliability": "medium"}
            )

    # Strategy 3: Check for publisher patterns (additional URLs)
    pattern_urls = _get_publisher_pdf_patterns(base_url)
    for url in pattern_urls:
        if url not in seen_urls:
            seen_urls.add(url)
            pdf_urls.append(
                {
                    "url": url,
                    "source": "publisher_pattern",
                    "reliability": "low",
                }
            )

    logger.success(f"Found {len(pdf_urls)} unique PDF URLs")

    # Log breakdown by source
    source_counts = {}
    for item in pdf_urls:
        source = item["source"]
        source_counts[source] = source_counts.get(source, 0) + 1

    for source, count in source_counts.items():
        logger.info(f"  - {source}: {count} URLs")

    return pdf_urls


async def find_supplementary_urls(page: Page) -> List[Dict]:
    """
    Find supplementary material URLs in a web page.

    Args:
        page: Playwright page object

    Returns:
        List of dicts with url, description, type, source, and reliability
    """
    try:
        supplementary = await page.evaluate(
            """
            () => {
                const results = [];

                // Common supplementary selectors
                const selectors = [
                    'a[href*="supplementary"]',
                    'a[href*="supplement"]',
                    'a[href*="additional"]',
                    'a[href*="supporting"]',
                    'a[href*="SI"]',
                    'a[href*="ESM"]'
                ];

                const seen_urls = new Set();

                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(link => {
                        if (link.href && !seen_urls.has(link.href)) {
                            seen_urls.add(link.href);

                            // Determine file type from URL
                            let type = 'unknown';
                            const url_lower = link.href.toLowerCase();
                            if (url_lower.includes('.pdf')) type = 'pdf';
                            else if (url_lower.includes('.xlsx') || url_lower.includes('.xls')) type = 'excel';
                            else if (url_lower.includes('.docx') || url_lower.includes('.doc')) type = 'word';
                            else if (url_lower.includes('.zip')) type = 'archive';
                            else if (url_lower.includes('.mp4') || url_lower.includes('.avi')) type = 'video';

                            results.push({
                                url: link.href,
                                description: link.textContent.trim(),
                                type: type,
                                source: 'href_pattern',
                                reliability: 'low'
                            });
                        }
                    });
                });

                return results;
            }
        """
        )

        logger.success(
            f"Found {len(supplementary)} supplementary URLs by href pattern matching"
        )
        return supplementary

    except Exception as e:
        logger.error(f"Error finding supplementary URLs: {e}")
        return []


async def _find_direct_pdf_links(page: Page) -> List[str]:
    """Find direct PDF links in the page."""
    try:
        pdf_urls = await page.evaluate(
            """
            () => {
                const urls = new Set();

                // Find all links ending with .pdf
                document.querySelectorAll('a[href$=".pdf"]').forEach(link => {
                    urls.add(link.href);
                });

                // Find download buttons/links
                const downloadSelectors = [
                    'a[data-track-action*="download"]',
                    'button[data-track-action*="download"]',
                    'a:has-text("Download PDF")',
                    'button:has-text("Download PDF")',
                    'a[download][href*="pdf"]',
                    '.pdf-download-btn',
                    'a[href*="/pdf/"]',
                    'a[href*="/doi/pdf/"]'
                ];

                downloadSelectors.forEach(selector => {
                    try {
                        document.querySelectorAll(selector).forEach(elem => {
                            const href = elem.getAttribute('href') || elem.dataset.href;
                            if (href) {
                                const fullUrl = new URL(href, window.location.href).href;
                                if (fullUrl.includes('pdf')) {
                                    urls.add(fullUrl);
                                }
                            }
                        });
                    } catch {}
                });

                return Array.from(urls);
            }
        """
        )

        return pdf_urls
    except:
        return []


def _get_publisher_pdf_patterns(url: str) -> List[str]:
    """Generate PDF URLs based on publisher patterns."""
    pdf_urls = []

    # Nature
    if "nature.com" in url and not url.endswith(".pdf"):
        pdf_urls.append(url.rstrip("/") + ".pdf")

    # Science
    elif "science.org" in url and "/doi/10." in url and "/pdf/" not in url:
        pdf_urls.append(url.replace("/doi/", "/doi/pdf/"))

    # Elsevier/ScienceDirect
    elif "sciencedirect.com" in url and "/pii/" in url:
        pii = url.split("/pii/")[-1].split("/")[0].split("?")[0]
        pdf_urls.append(
            f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
        )

    # Wiley
    elif "wiley.com" in url and "/doi/" in url and "/pdfdirect" not in url:
        pdf_urls.append(url.replace("/doi/", "/doi/pdfdirect/"))

    # Frontiers
    elif "frontiersin.org" in url and "/full" in url:
        pdf_urls.append(url.replace("/full", "/pdf"))

    # Springer
    elif (
        "springer.com" in url or "link.springer.com" in url
    ) and "/article/" in url:
        if not url.endswith(".pdf"):
            pdf_urls.append(url.rstrip("/") + ".pdf")

    # IEEE
    elif "ieee.org" in url and "/document/" in url:
        doc_id = url.split("/document/")[-1].split("/")[0]
        pdf_urls.append(
            f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_id}"
        )

    # MDPI
    elif "mdpi.com" in url and "/htm" in url:
        pdf_urls.append(url.replace("/htm", "/pdf"))

    # BMC
    elif "biomedcentral.com" in url and "/articles/" in url:
        pdf_urls.append(url.replace("/articles/", "/track/pdf/"))

    if len(pdf_urls) > 0:
        logger.success(
            f"Publisher-specific pattern matching found {len(pdf_urls)} PDF URLs"
        )
    else:
        logger.warning(
            f"Publisher-specific patterns did not match any PDF URLs"
        )

    return pdf_urls


async def _find_with_zotero_translator(page: Page, url: str) -> List[str]:
    """
    Find PDF URLs using Zotero translator (FIRST strategy - most reliable).

    Args:
        page: Playwright page object with loaded content
        url: Current page URL

    Returns:
        List of PDF URLs extracted by Zotero translator
    """
    try:
        from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner

        runner = ZoteroTranslatorRunner()

        # Execute translator if one matches this URL
        pdf_urls = await runner.extract_pdf_urls_async(page)

        if pdf_urls:
            logger.success(f"Zotero translator found {len(pdf_urls)} PDF URLs")
            for pdf_url in pdf_urls:
                logger.debug(f"  - {pdf_url}")
        else:
            logger.warning(f"Zotero translator did not find any PDF URLs")

        return pdf_urls

    except ImportError as e:
        logger.warning(f"ZoteroTranslatorRunner not available: {e}")
        return []
    except Exception as e:
        logger.error(f"Error running Zotero translator: {e}")
        return []


async def find_all_urls(page: Page) -> Dict[str, List[Dict]]:
    """
    Find all URL types in a page.

    Returns:
        Dict with 'pdf' and 'supplementary' keys, each containing list of dicts with source info
    """
    return {
        "pdf": await find_pdf_urls(page),
        "supplementary": await find_supplementary_urls(page),
    }

# EOF
