#!/usr/bin/env python3
"""
Publisher-Specific PDF Access Strategies

Each publisher has different workflows for accessing PDFs through institutional
authentication. This module provides strategies for each major publisher.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional, List
from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


class PublisherStrategy(ABC):
    """Base class for publisher-specific PDF access strategies."""

    @abstractmethod
    async def can_handle(self, url: str) -> bool:
        """Check if this strategy can handle the given URL."""
        pass

    @abstractmethod
    async def get_pdf_url(self, page: Page) -> Optional[str]:
        """Extract or build PDF URL from publisher page."""
        pass


class IEEEStrategy(PublisherStrategy):
    """
    IEEE Xplore access strategy.

    Proven to work in tests. Pattern:
    1. Article URL: https://ieeexplore.ieee.org/document/9942397/
    2. Extract article number: 9942397
    3. Build PDF URL: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397
    """

    async def can_handle(self, url: str) -> bool:
        """Check if URL is from IEEE Xplore."""
        return 'ieeexplore.ieee.org' in url

    async def get_pdf_url(self, page: Page) -> Optional[str]:
        """
        Build IEEE PDF viewer URL from article number.

        Args:
            page: Page currently on IEEE article or search results

        Returns:
            PDF viewer URL or None if article number not found
        """
        try:
            current_url = page.url

            # Method 1: Extract from current URL if already on article page
            match = re.search(r'/document/(\d+)', current_url)
            if match:
                article_num = match.group(1)
                pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
                logger.success(f"Built IEEE PDF URL from current page: {pdf_url}")
                return pdf_url

            # Method 2: On search results - navigate to article page
            if '/search/' in current_url:
                logger.info("On IEEE search results, looking for article link...")

                # Check if page is still open
                if page.is_closed():
                    logger.error("Page was closed unexpectedly")
                    return None

                # Strategy 1: Find article links and navigate to the first one
                try:
                    article_links = await page.evaluate("""
                        () => {
                            const links = [];
                            document.querySelectorAll('a').forEach(a => {
                                if (a.href && a.href.includes('/document/')) {
                                    links.push(a.href);
                                }
                            });
                            return [...new Set(links)]; // Remove duplicates
                        }
                    """)

                    logger.debug(f"Page evaluate result: {len(article_links) if article_links else 0} links")

                    if article_links:
                        logger.info(f"Found {len(article_links)} article links")
                        # Navigate to first article page
                        article_url = article_links[0]
                        logger.info(f"Navigating to article page: {article_url}")
                        await page.goto(article_url, wait_until="networkidle", timeout=30000)
                        import asyncio
                        await asyncio.sleep(2)

                        # Now extract article number from the article page URL
                        current_url = page.url
                        match = re.search(r'/document/(\d+)', current_url)
                        if match:
                            article_num = match.group(1)
                            pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
                            logger.success(f"Built IEEE PDF URL after navigating to article: {pdf_url}")
                            return pdf_url
                    else:
                        logger.warning("No /document/ links found on search results page")
                        # Fallback: Try to extract from page HTML directly
                        page_html = await page.content()
                        doc_matches = re.findall(r'/document/(\d+)', page_html)
                        if doc_matches:
                            article_num = doc_matches[0]
                            pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
                            logger.success(f"Built IEEE PDF URL from page HTML: {pdf_url}")
                            return pdf_url

                except Exception as e:
                    logger.error(f"Error finding article links: {e}")
                    return None

                logger.warning("Could not navigate to article page or extract article number")
                return None

            logger.error(f"Unknown IEEE page type: {current_url}")
            return None

        except Exception as e:
            logger.error(f"IEEE strategy failed: {e}", exc_info=True)
            return None


class ElsevierStrategy(PublisherStrategy):
    """
    Elsevier/ScienceDirect access strategy.

    Workflow:
    1. OpenURL leads to "Access through institution" page
    2. Click "View PDF" or "Download PDF" button
    3. Extract PDF URL from viewer
    """

    async def can_handle(self, url: str) -> bool:
        """Check if URL is from ScienceDirect/Elsevier."""
        return any(domain in url for domain in [
            'sciencedirect.com',
            'elsevier.com'
        ])

    async def get_pdf_url(self, page: Page) -> Optional[str]:
        """
        Find PDF download button on ScienceDirect page.

        Args:
            page: Page currently on ScienceDirect article

        Returns:
            PDF URL or None if not found
        """
        try:
            # Look for PDF buttons
            pdf_buttons = await page.query_selector_all('a:has-text("PDF")')

            for button in pdf_buttons:
                href = await button.get_attribute('href')
                if href and '.pdf' in href:
                    logger.success(f"Found Elsevier PDF: {href}")
                    return href

            # Alternative: look for download link
            download_link = await page.query_selector('a[download]')
            if download_link:
                href = await download_link.get_attribute('href')
                if href:
                    logger.success(f"Found Elsevier download link: {href}")
                    return href

            logger.warning("No PDF link found on Elsevier page")
            return None

        except Exception as e:
            logger.error(f"Elsevier strategy failed: {e}", exc_info=True)
            return None


class IOPStrategy(PublisherStrategy):
    """
    IOP Publishing (Institute of Physics) access strategy.

    Workflow:
    1. OpenURL leads to IOP article page
    2. Find "Full Text" or "PDF" download button
    3. Extract PDF URL
    """

    async def can_handle(self, url: str) -> bool:
        """Check if URL is from IOP Publishing."""
        return any(domain in url for domain in [
            'iopscience.iop.org',
            'iop.org'
        ])

    async def get_pdf_url(self, page: Page) -> Optional[str]:
        """
        Find PDF download on IOP page.

        Args:
            page: Page currently on IOP article

        Returns:
            PDF URL or None if not found
        """
        try:
            # Look for PDF download link
            pdf_link = await page.query_selector('a[href*=".pdf"]')
            if pdf_link:
                href = await pdf_link.get_attribute('href')
                if href:
                    logger.success(f"Found IOP PDF: {href}")
                    return href

            logger.warning("No PDF link found on IOP page")
            return None

        except Exception as e:
            logger.error(f"IOP strategy failed: {e}", exc_info=True)
            return None


class UnpaywallStrategy(PublisherStrategy):
    """
    Unpaywall / Open Access strategy.

    Workflow:
    1. OpenURL provides "Open Access via Unpaywall" link
    2. Direct link to PDF or article page
    3. Download PDF directly
    """

    async def can_handle(self, url: str) -> bool:
        """Check if URL is open access repository."""
        return any(domain in url for domain in [
            'unpaywall',
            'arxiv.org',
            'biorxiv.org',
            'medrxiv.org',
            'pmc.ncbi.nlm.nih.gov'
        ])

    async def get_pdf_url(self, page: Page) -> Optional[str]:
        """
        Find open access PDF.

        Args:
            page: Page currently on open access repository

        Returns:
            PDF URL or None if not found
        """
        try:
            current_url = page.url

            # If already PDF URL
            if current_url.endswith('.pdf'):
                logger.success(f"Direct PDF URL: {current_url}")
                return current_url

            # Look for PDF links
            pdf_links = await page.query_selector_all('a[href*=".pdf"]')
            if pdf_links:
                href = await pdf_links[0].get_attribute('href')
                if href:
                    # Handle relative URLs
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(current_url, href)
                    logger.success(f"Found open access PDF: {href}")
                    return href

            logger.warning("No open access PDF found")
            return None

        except Exception as e:
            logger.error(f"Unpaywall strategy failed: {e}", exc_info=True)
            return None


# Strategy registry
STRATEGIES: List[PublisherStrategy] = [
    IEEEStrategy(),
    ElsevierStrategy(),
    IOPStrategy(),
    UnpaywallStrategy(),
]


async def get_strategy_for_url(url: str) -> Optional[PublisherStrategy]:
    """
    Get appropriate strategy for given URL.

    Args:
        url: Publisher page URL

    Returns:
        Strategy instance or None if no strategy matches
    """
    for strategy in STRATEGIES:
        if await strategy.can_handle(url):
            logger.info(f"Selected strategy: {strategy.__class__.__name__}")
            return strategy

    logger.warning(f"No strategy found for URL: {url}")
    return None
