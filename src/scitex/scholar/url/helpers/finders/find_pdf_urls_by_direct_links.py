#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 12:09:57 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/finders/find_pdf_urls_by_direct_links.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/find_pdf_urls_by_direct_links.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import List

from playwright.async_api import Page

from scitex import log
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.utils import show_popup_message_async

logger = log.getLogger(__name__)


async def find_pdf_urls_by_direct_links(
    page: Page, config: ScholarConfig = None
) -> List[str]:
    """Find direct PDF links in the page."""
    config = config or ScholarConfig()

    try:
        all_urls = set()

        dropdown_urls = await _find_pdf_urls_from_dropdown(page, config)
        all_urls.update(dropdown_urls)

        href_urls = await _find_pdf_urls_by_href(page, config)
        all_urls.update(href_urls)

        return list(all_urls)
    except:
        return []


async def _find_pdf_urls_by_href(
    page: Page,
    download_selectors: List[str] = None,
    config: ScholarConfig = None,
) -> List[str]:
    """Find PDF URLs from href attributes using configured selectors."""
    try:
        config = config or ScholarConfig()

        deny_selectors = config.resolve("deny_selectors", default=[])
        deny_classes = config.resolve("deny_classes", default=[])
        deny_text_patterns = config.resolve("deny_text_patterns", default=[])

        await show_popup_message_async(
            page, "Finding PDF URLs by href selectors..."
        )

        download_selectors = config.resolve(
            "download_selectors",
            download_selectors,
            default=[
                'a[data-track-action*="download"]',
                'a:has-text("Download PDF")',
                "a.PdfLink",
            ],
        )

        static_urls = await page.evaluate(
            f"""() => {{
            const urls = new Set();
            const denySelectors = {deny_selectors};
            const denyClasses = {deny_classes};
            const denyTextPatterns = {deny_text_patterns};

            function shouldDenyElement(elem) {{
                // Check deny classes
                for (const denyClass of denyClasses) {{
                    if (elem.classList.contains(denyClass)) return true;
                }}

                // Check deny text patterns
                const text = elem.textContent.toLowerCase();
                for (const pattern of denyTextPatterns) {{
                    if (text.includes(pattern.toLowerCase())) return true;
                }}

                // Check if element is inside denied selectors
                for (const selector of denySelectors) {{
                    if (elem.closest(selector)) return true;
                }}

                return false;
            }}

            // Check download selectors
            const downloadSelectors = {download_selectors};
            downloadSelectors.forEach(selector => {{
                document.querySelectorAll(selector).forEach(elem => {{
                    if (shouldDenyElement(elem)) return;
                    
                    const href = elem.href || elem.getAttribute('href');
                    if (href && (href.includes('.pdf') || href.includes('/pdf/'))) {{
                        urls.add(href);
                    }}
                }});
            }});
            
            // Also check for common PDF link patterns
            document.querySelectorAll('a[href*=".pdf"], a[href*="/pdf/"]').forEach(link => {{
                if (!shouldDenyElement(link) && link.href) {{
                    urls.add(link.href);
                }}
            }});
            
            // Check meta tags for PDF URLs
            const pdfMeta = document.querySelector('meta[name="citation_pdf_url"]');
            if (pdfMeta && pdfMeta.content) {{
                urls.add(pdfMeta.content);
            }}

            return Array.from(urls);
        }}"""
        )

        return static_urls
    except Exception as e:
        logger.info(e)
        return []


async def _find_pdf_urls_from_dropdown(
    page: Page, config: ScholarConfig = None
) -> List[str]:
    try:
        config = config or ScholarConfig()

        dropdown_selectors = config.resolve(
            "dropdown_selectors",
            default=[
                'button:has-text("Download PDF")',
                'button:has-text("PDF")',
                'a:has-text("Download PDF")',
                ".pdf-download-button",
            ],
        )

        pdf_urls = []
        for selector in dropdown_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute("href")
                    if href and "pdf" in href.lower():
                        pdf_urls.append(href)
            except:
                continue

        return pdf_urls
    except Exception as e:
        logger.info(e)
        return []

# EOF
