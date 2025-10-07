#!/usr/bin/env python3
"""
OpenURL Access Helpers

Provides functions to navigate OpenURL resolvers and capture popup windows
for institutional access to paywalled papers.
"""

import asyncio
from typing import Optional, List, Dict
from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


async def click_openurl_link_and_capture_popup(
    page: Page,
    link_text: str,
    timeout: int = 15000
) -> Optional[Page]:
    """
    Click OpenURL JavaScript link and capture the popup window.

    OpenURL resolvers use JavaScript links like:
    javascript:openSFXMenuLink(this, 'basic1', undefined, '_blank');

    These must be clicked to trigger navigation. This function sets up
    a popup listener, clicks the link, and returns the popup page.

    Args:
        page: Current page with OpenURL resolver
        link_text: Text of the link to click (e.g., "IEEE", "ScienceDirect")
        timeout: Milliseconds to wait for popup (default: 15000)

    Returns:
        Popup page if successful, None if link not found or timeout
    """
    try:
        # Find the link
        link = await page.query_selector(f'a:has-text("{link_text}")')
        if not link:
            logger.warning(f"Link not found: {link_text}")
            return None

        # Set up popup listener BEFORE clicking (critical for capture)
        popup_future = page.wait_for_event("popup", timeout=timeout)

        # Click the link
        await link.click()

        # Wait for popup
        popup_page = await popup_future

        # Wait for popup to load
        await popup_page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(2)  # Extra wait for JavaScript

        logger.info(f"Popup captured: {popup_page.url}")
        return popup_page

    except Exception as e:
        logger.error(f"Failed to capture popup for '{link_text}': {e}")
        return None


async def find_openurl_access_links(page: Page) -> List[Dict[str, str]]:
    """
    Find all 'Available from' access links on OpenURL page.

    Returns list of dicts with:
        - text: Link text (e.g., "IEEE Electronic Library")
        - href: Link href (usually JavaScript)
        - type: Access type (institutional/open_access/paywall)
    """
    try:
        links = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('a').forEach(a => {
                    const text = a.textContent.trim();
                    // Look for "Available from" links
                    if (text.includes('IEEE') ||
                        text.includes('ScienceDirect') ||
                        text.includes('Elsevier') ||
                        text.includes('Institute of Physics') ||
                        text.includes('Unpaywall') ||
                        text.includes('Open Access')) {

                        let access_type = 'institutional';
                        if (text.toLowerCase().includes('open access') ||
                            text.toLowerCase().includes('unpaywall')) {
                            access_type = 'open_access';
                        }

                        results.push({
                            text: text,
                            href: a.href,
                            type: access_type
                        });
                    }
                });
                return results;
            }
        """)

        logger.info(f"Found {len(links)} access links")
        for link in links:
            logger.debug(f"  - {link['text']} ({link['type']})")

        return links

    except Exception as e:
        logger.error(f"Failed to find access links: {e}")
        return []


async def select_best_access_route(links: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Select best access route from available links.

    Priority:
    1. Open Access / Unpaywall (free, no auth needed)
    2. Institutional access (requires auth but usually works)
    3. Direct paywall (last resort)

    Args:
        links: List of link dicts from find_openurl_access_links()

    Returns:
        Best link dict, or None if no links available
    """
    if not links:
        return None

    # Priority 1: Open access
    for link in links:
        if link['type'] == 'open_access':
            logger.info(f"Selected open access route: {link['text']}")
            return link

    # Priority 2: Institutional access
    for link in links:
        if link['type'] == 'institutional':
            logger.info(f"Selected institutional route: {link['text']}")
            return link

    # Fallback: First available
    logger.warning(f"No preferred route, using: {links[0]['text']}")
    return links[0]
