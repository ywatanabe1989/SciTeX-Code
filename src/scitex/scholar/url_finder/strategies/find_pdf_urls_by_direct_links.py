#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/strategies/find_pdf_urls_by_direct_links.py
# ----------------------------------------
"""
Find PDF URLs from direct links (href attributes and dropdown buttons).

This strategy combines:
1. Href-based detection (with deny patterns and publisher rules)
2. Dropdown/button detection
"""

from typing import List
from playwright.async_api import Page
from scitex.browser.debugging import browser_logger
from scitex.scholar.config import PublisherRules, ScholarConfig


async def find_pdf_urls_by_direct_links(
    page: Page,
    url: str = None,
    config: ScholarConfig = None,
    func_name: str = "find_pdf_urls_by_direct_links",
) -> List[str]:
    """
    Find PDF URLs from direct links (href + dropdowns).

    Args:
        page: Playwright page object
        url: Current page URL
        config: ScholarConfig instance
        func_name: Function name for logging

    Returns:
        List of PDF URLs found
    """
    try:
        config = config or ScholarConfig()
        all_urls = set()

        # 1. Find from href attributes (main method)
        href_urls = await _find_from_href_attributes(page, config, func_name)
        all_urls.update(href_urls)

        # 2. Find from dropdown buttons
        dropdown_urls = await _find_from_dropdowns(page, config, func_name)
        all_urls.update(dropdown_urls)

        if all_urls:
            await browser_logger.debug(
                page,
                f"{func_name}: Found {len(all_urls)} URLs "
                f"({len(href_urls)} href, {len(dropdown_urls)} dropdown)"
            )

        return list(all_urls)

    except Exception as e:
        await browser_logger.debug(page, f"{func_name}: {str(e)}")
        return []


async def _find_from_href_attributes(
    page: Page,
    config: ScholarConfig,
    func_name: str,
) -> List[str]:
    """Find PDF URLs from href attributes using configured selectors."""
    try:
        # Get deny patterns from config file
        config_deny_selectors = config.resolve("deny_selectors", default=[])
        config_deny_classes = config.resolve("deny_classes", default=[])
        config_deny_text_patterns = config.resolve("deny_text_patterns", default=[])

        # Merge with publisher-specific patterns
        current_url = page.url
        publisher_rules = PublisherRules(config)
        merged_config = publisher_rules.merge_with_config(
            current_url,
            config_deny_selectors,
            config_deny_classes,
            config_deny_text_patterns,
        )

        # Use merged patterns
        deny_selectors = merged_config["deny_selectors"]
        deny_classes = merged_config["deny_classes"]
        deny_text_patterns = merged_config["deny_text_patterns"]

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

        download_selectors = (
            unique_selectors
            if unique_selectors
            else [
                'a[data-track-action*="download"]',
                'a:has-text("Download PDF")',
                "a.PdfLink",
            ]
        )

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
                            const match = selector.match(/:has-text\\(["'](.+?)["']\\)/);
                            if (match && elem.textContent.includes(match[1])) {
                                return true;
                            }
                        } else {
                            // Regular CSS selector
                            if (elem.closest(selector)) return true;
                        }
                    } catch (e) {
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
                                    // Accept if contains .pdf OR path includes /pdf
                                    if (href && (href.includes('.pdf') || href.match(/\/pdf\/?/))) {
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
                            // Accept if contains .pdf OR path includes /pdf
                            if (href && (href.includes('.pdf') || href.match(/\/pdf\/?/))) {
                                urls.add(href);
                            }
                        });
                    }
                } catch (e) {
                    console.warn('Invalid selector:', selector, e);
                }
            });

            // Also check for common PDF link patterns
            // Include links with .pdf extension OR /pdf/ in path (for arXiv, Frontiers, etc.)
            document.querySelectorAll('a[href*=".pdf"], a[href*="/pdf/"], a[href*="/pdf"]').forEach(link => {
                if (!shouldDenyElement(link) && link.href) {
                    // Accept if contains .pdf OR path includes /pdf
                    if (link.href.includes('.pdf') || link.href.match(/\/pdf\/?/)) {
                        urls.add(link.href);
                    }
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
                "downloadSelectors": download_selectors,
            },
        )

        return static_urls

    except Exception as e:
        await browser_logger.debug(page, f"{func_name} (href): {str(e)}")
        return []


async def _find_from_dropdowns(
    page: Page,
    config: ScholarConfig,
    func_name: str,
) -> List[str]:
    """Find PDF URLs from dropdown buttons and download elements."""
    try:
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
        await browser_logger.debug(page, f"{func_name} (dropdown): {str(e)}")
        return []


# EOF
