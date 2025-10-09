#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 01:34:13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders/_find_pdf_urls_by_view_button.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/_find_pdf_urls_by_view_button.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Find PDF URLs by navigating to PDF links and following redirects.

Handles publishers like ScienceDirect that require navigation
through redirect chains to reach the actual PDF URL.
"""

from typing import List, Optional

from playwright.async_api import Page

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser.utils._wait_redirects import wait_redirects

logger = logging.getLogger(__name__)


async def find_pdf_urls_by_navigation(
    page: Page,
    config: ScholarConfig = None,
    func_name: str = "find_pdf_urls_by_navigation",
) -> List[str]:
    """
    Find PDF URLs by navigating to PDF links and capturing final URLs.

    This handles cases like ScienceDirect where:
    1. Direct PDF links exist (/pdfft? endpoints)
    2. Navigating to them triggers redirects
    3. Final destination is the actual PDF on pdf.sciencedirectassets.com
    """
    config = config or ScholarConfig()
    pdf_urls = []

    try:
        # Check if we already have direct PDF links
        current_url = page.url.lower()
        is_sciencedirect = any(
            domain in current_url
            for domain in [
                "sciencedirect.com",
                "cell.com",
                "elsevier.com",
                "ssrn.com",
            ]
        )

        if not is_sciencedirect:
            return []

        # Look for existing PDF links on the page
        pdf_link_selectors = [
            'a[href*="/pdfft?"]',  # ScienceDirect PDF endpoint
            'a[aria-label*="Download PDF"]',
            'a[aria-label*="Download This Paper"]',
            'a:has-text("View PDF")',
            "a.pdf-link",
            'a[href*="/pdf/"]',
        ]

        pdf_href = None
        for selector in pdf_link_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute("href")
                    if href and ("/pdfft?" in href or "/pdf/" in href):
                        # Make absolute URL if needed
                        if href.startswith("/"):
                            from urllib.parse import urljoin

                            href = urljoin(page.url, href)
                        pdf_href = href
                        logger.info(
                            f"{func_name}: Found PDF link: {href[:80]}..."
                        )
                        break
            except Exception as e:
                logger.debug(
                    f"{func_name}: Error checking selector {selector}: {e}"
                )
                continue

        if not pdf_href:
            logger.debug(f"{func_name}: No PDF links found on page")
            return []

        # Navigate to PDF URL in a new page to capture final URL
        context = page.context
        new_page = None

        try:
            logger.info(
                f"{func_name}: Navigating to PDF URL to capture final destination..."
            )
            new_page = await context.new_page()

            # Navigate and wait for redirects - be patient!
            await new_page.goto(pdf_href, wait_until="commit", timeout=60000)

            # Wait for redirects to complete with longer timeout
            redirect_result = await wait_redirects(
                new_page,
                timeout=60000,  # 60 seconds timeout
                show_progress=False,
                track_chain=True,
                auth_aware=True,
                wait_for_idle=True,  # Wait for network idle
            )

            final_url = redirect_result.get("final_url", new_page.url)
            redirect_chain = redirect_result.get("redirect_chain", [])

            # Additional wait to ensure PDF loads
            await new_page.wait_for_timeout(2000)

            # Check again for final URL
            final_url = new_page.url

            logger.info(
                f"{func_name}: Redirect complete after {len(redirect_chain)} steps"
            )
            logger.info(f"{func_name}: Final URL: {final_url[:80]}...")

            # Check if final URL is a PDF
            if any(
                indicator in final_url
                for indicator in [
                    "pdf.sciencedirectassets.com",
                    ".pdf",
                    "application/pdf",
                    "/pdf/",
                    "pdfft?",
                ]
            ):
                pdf_urls.append(final_url)
                logger.success(
                    f"{func_name}: Captured final PDF URL via navigation"
                )
            else:
                logger.debug(
                    f"{func_name}: Final URL doesn't appear to be a PDF: {final_url}"
                )

        except Exception as e:
            logger.error(f"{func_name}: Error navigating to PDF: {e}")
        finally:
            if new_page:
                try:
                    await new_page.close()
                except:
                    pass

        return pdf_urls

    except Exception as e:
        logger.error(f"{func_name}: Error finding PDFs via navigation: {e}")
        return []


async def find_pdf_url_from_sciencedirect_api(
    page: Page, func_name="find_pdf_url_from_sciencedirect_api"
) -> Optional[str]:
    """
    Extract PDF URL from ScienceDirect page using their JavaScript context.

    ScienceDirect pages often have the PDF URL in JavaScript variables.
    """
    try:
        # Try to extract from page's JavaScript context
        pdf_info = await page.evaluate(
            """
            () => {
                // Look for PDF URL in various places

                // Check for download URL in page data
                const pdfLinks = document.querySelectorAll('a[href*="/pdfft?"]');
                if (pdfLinks.length > 0) {
                    return pdfLinks[0].href;
                }

                // Check window.SDM object (ScienceDirect)
                if (window.SDM && window.SDM.pdfUrl) {
                    return window.SDM.pdfUrl;
                }

                // Check for entitlement info
                if (window.SD && window.SD.article && window.SD.article.pdfDownloadUrl) {
                    return window.SD.article.pdfDownloadUrl;
                }

                // Look for View PDF button
                const viewPdfBtn = document.querySelector('a[aria-label*="View PDF"]');
                if (viewPdfBtn && viewPdfBtn.href) {
                    return viewPdfBtn.href;
                }

                // Check meta tags
                const pdfMeta = document.querySelector('meta[name="citation_pdf_url"]');
                if (pdfMeta && pdfMeta.content) {
                    return pdfMeta.content;
                }

                return null;
            }
        """
        )

        if pdf_info:
            logger.info(
                f"{func_name}: Found PDF info from page context: {pdf_info[:80]}..."
            )
            return pdf_info

    except Exception as e:
        logger.debug(f"Could not extract PDF info from page context: {e}")

    return None

# EOF
