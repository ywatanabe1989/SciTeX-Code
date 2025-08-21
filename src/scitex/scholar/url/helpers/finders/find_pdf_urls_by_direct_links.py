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
from .publisher_pdf_configs import PublisherPDFConfig

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
        
        # Filter URLs based on publisher-specific rules
        current_url = page.url
        filtered_urls = PublisherPDFConfig.filter_pdf_urls(current_url, list(all_urls))
        
        # Log if we filtered out many URLs (like the 35 from ScienceDirect)
        if len(all_urls) > len(filtered_urls):
            logger.info(f"Filtered {len(all_urls)} URLs down to {len(filtered_urls)} valid PDFs")

        return filtered_urls
    except Exception as e:
        logger.error(f"Error finding PDF URLs: {e}")
        return []


async def _find_pdf_urls_by_href(
    page: Page,
    download_selectors: List[str] = None,
    config: ScholarConfig = None,
) -> List[str]:
    """Find PDF URLs from href attributes using configured selectors."""
    try:
        config = config or ScholarConfig()
        
        # Get deny patterns from config file
        config_deny_selectors = config.resolve("deny_selectors", default=[])
        config_deny_classes = config.resolve("deny_classes", default=[])
        config_deny_text_patterns = config.resolve("deny_text_patterns", default=[])
        
        # Merge with publisher-specific patterns
        current_url = page.url
        merged_config = PublisherPDFConfig.merge_with_config(
            current_url,
            config_deny_selectors,
            config_deny_classes,
            config_deny_text_patterns
        )
        
        # Use merged patterns
        deny_selectors = merged_config["deny_selectors"]
        deny_classes = merged_config["deny_classes"] 
        deny_text_patterns = merged_config["deny_text_patterns"]

        await show_popup_message_async(
            page, "Finding PDF URLs by href selectors..."
        )

        # Use merged download selectors (config + publisher-specific)
        config_download_selectors = config.resolve("download_selectors", default=[])
        publisher_download_selectors = merged_config.get("download_selectors", [])
        
        # Combine selectors (config first, then publisher-specific)
        all_download_selectors = list(config_download_selectors)
        all_download_selectors.extend(publisher_download_selectors)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_selectors = []
        for selector in all_download_selectors:
            if selector not in seen:
                seen.add(selector)
                unique_selectors.append(selector)
        
        download_selectors = unique_selectors if unique_selectors else [
            'a[data-track-action*="download"]',
            'a:has-text("Download PDF")',
            "a.PdfLink",
        ]

        static_urls = await page.evaluate(
            """(args) => {
            const urls = new Set();
            const denySelectors = args.denySelectors || [];
            const denyClasses = args.denyClasses || [];
            const denyTextPatterns = args.denyTextPatterns || [];
            const downloadSelectors = args.downloadSelectors || [];

            function shouldDenyElement(elem) {
                // Check deny classes
                for (const denyClass of denyClasses) {
                    if (elem.classList.contains(denyClass)) return true;
                }

                // Check deny text patterns
                const text = elem.textContent.toLowerCase();
                for (const pattern of denyTextPatterns) {
                    if (text.includes(pattern.toLowerCase())) return true;
                }

                // Check if element is inside denied selectors
                for (const selector of denySelectors) {
                    try {
                        // Handle Playwright :has-text() selectors
                        if (selector.includes(':has-text(')) {
                            // Extract text from :has-text("...")
                            const match = selector.match(/:has-text\\(["'](.+?)["']\\)/);
                            if (match && elem.textContent.includes(match[1])) {
                                return true;
                            }
                        } else {
                            // Regular CSS selector
                            if (elem.closest(selector)) return true;
                        }
                    } catch (e) {
                        // Invalid selector, skip it
                        console.warn('Invalid deny selector:', selector);
                    }
                }

                return false;
            }

            // Check download selectors
            downloadSelectors.forEach(selector => {
                try {
                    // Handle Playwright :has-text() selectors
                    if (selector.includes(':has-text(')) {
                        const match = selector.match(/^(.+?):has-text\\(["'](.+?)["']\\)/);
                        if (match) {
                            const [, baseSelector, text] = match;
                            document.querySelectorAll(baseSelector || 'a, button').forEach(elem => {
                                if (elem.textContent.includes(text) && !shouldDenyElement(elem)) {
                                    const href = elem.href || elem.getAttribute('href');
                                    if (href && (href.includes('.pdf') || href.includes('/pdf/'))) {
                                        urls.add(href);
                                    }
                                }
                            });
                        }
                    } else {
                        // Regular CSS selector
                        document.querySelectorAll(selector).forEach(elem => {
                            if (shouldDenyElement(elem)) return;
                            
                            const href = elem.href || elem.getAttribute('href');
                            if (href && (href.includes('.pdf') || href.includes('/pdf/'))) {
                                urls.add(href);
                            }
                        });
                    }
                } catch (e) {
                    console.warn('Invalid selector:', selector, e);
                }
            });
            
            // Also check for common PDF link patterns
            document.querySelectorAll('a[href*=".pdf"], a[href*="/pdf/"]').forEach(link => {
                if (!shouldDenyElement(link) && link.href) {
                    urls.add(link.href);
                }
            });
            
            // Check meta tags for PDF URLs
            const pdfMeta = document.querySelector('meta[name="citation_pdf_url"]');
            if (pdfMeta && pdfMeta.content) {
                urls.add(pdfMeta.content);
            }

            return Array.from(urls);
        }""",
            {
                "denySelectors": deny_selectors,
                "denyClasses": deny_classes,
                "denyTextPatterns": deny_text_patterns,
                "downloadSelectors": download_selectors
            }
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
