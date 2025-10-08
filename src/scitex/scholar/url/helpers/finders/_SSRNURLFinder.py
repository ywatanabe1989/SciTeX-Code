"""Simple SSRN PDF URL finder.

Bypasses Zotero translator complexity and directly extracts PDF download link.
Based on SSRN.js translator line 124: attr(doc, 'a.primary[data-abstract-id]', 'href')
"""

from typing import List, Optional
from playwright.async_api import Page


class SSRNURLFinder:
    """Find PDF URLs on SSRN pages."""

    @staticmethod
    async def extract_pdf_url_async(page: Page) -> Optional[str]:
        """Extract PDF download URL from SSRN page.

        Args:
            page: Playwright page on SSRN paper page

        Returns:
            PDF URL if found, None otherwise
        """
        # Wait for download button to load (up to 5 seconds)
        try:
            await page.wait_for_selector('a.primary[data-abstract-id]', timeout=5000)
        except:
            pass  # Continue even if timeout

        # Extract the PDF URL
        pdf_url = await page.evaluate("""
            () => {
                const link = document.querySelector('a.primary[data-abstract-id]');
                return link ? link.href : null;
            }
        """)

        return pdf_url

    @staticmethod
    def matches_url(url: str) -> bool:
        """Check if URL is an SSRN paper page.

        Args:
            url: URL to check

        Returns:
            True if URL matches SSRN pattern
        """
        return 'ssrn.com' in url.lower() and 'abstract' in url.lower()
