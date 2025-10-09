#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:22:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/interaction/handle_popups.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Universal popup handler for browser automation.

Detects and closes various types of popups including:
- Cookie consent banners
- Newsletter/subscription modals
- AI assistant promotions
- Authentication prompts
- General modal dialogs

This is a universal utility that works across any website.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from playwright.async_api import Page, ElementHandle

from scitex import logging

logger = logging.getLogger(__name__)


class PopupHandler:
    """Handle various types of popups on web pages."""
    
    # Common selectors for different popup types
    COOKIE_SELECTORS = [
        'button#onetrust-accept-btn-handler',
        'button#onetrust-pc-btn-handler',
        'button[id*="accept-cookie"]',
        'button[id*="accept-all"]',
        'button[aria-label*="accept cookie"]',
        'button[aria-label*="Accept cookie"]',
        'button:has-text("Accept all")',
        'button:has-text("Accept All")',
        'button:has-text("I agree")',
        'button:has-text("I Agree")',
        'button:has-text("Accept")',
        '.cookie-notice button.accept',
        '[class*="cookie"] button[class*="accept"]',
    ]
    
    CLOSE_SELECTORS = [
        'button[aria-label="Close"]',
        'button[aria-label="close"]',
        'button[aria-label*="Close"]',
        'button[aria-label*="close"]',
        'button[aria-label*="dismiss"]',
        'button[aria-label*="Dismiss"]',
        'button.close',
        'button.close-button',
        'button.modal-close',
        'button.popup-close',
        'button.dialog-close',
        'a.close',
        'a.close-button',
        'span.close',
        '[class*="close-button"]',
        '[class*="close-icon"]',
        'svg[class*="close"]',
        'button:has-text("No thanks")',
        'button:has-text("No Thanks")',
        'button:has-text("Maybe later")',
        'button:has-text("Maybe Later")',
        'button:has-text("Skip")',
        'button:has-text("Dismiss")',
        'button:has-text("Not now")',
        'button:has-text("Not Now")',
    ]
    
    MODAL_SELECTORS = [
        '.modal',
        '.overlay',
        '[role="dialog"]',
        '.popup',
        '#onetrust-banner-sdk',
        '.onetrust-pc-dark-filter',
        '[class*="modal"]',
        '[class*="popup"]',
        '[class*="overlay"]',
        '[class*="dialog"]',
        '[class*="banner"]',
        'div[aria-modal="true"]',
    ]

    def __init__(self, page: Page):
        """Initialize popup handler with a page."""
        self.page = page
        self.handled_popups = []

    async def detect_popups(self) -> List[Dict]:
        """
        Detect all visible popups on the page.
        
        Returns:
            List of detected popups with their details
        """
        detected = []
        
        try:
            # Check for visible modal/popup elements
            popup_info = await self.page.evaluate('''
                () => {
                    const modalSelectors = %s;
                    const found = [];
                    
                    for (const selector of modalSelectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const style = window.getComputedStyle(el);
                                const rect = el.getBoundingClientRect();
                                
                                // Check if element is visible
                                if (style.display !== 'none' && 
                                    style.visibility !== 'hidden' && 
                                    rect.width > 0 && 
                                    rect.height > 0 &&
                                    style.opacity !== '0') {
                                    
                                    // Get text preview
                                    let text = el.innerText || el.textContent || '';
                                    text = text.substring(0, 200).trim();
                                    
                                    // Try to identify popup type
                                    let type = 'unknown';
                                    const lowerText = text.toLowerCase();
                                    if (lowerText.includes('cookie') || lowerText.includes('privacy')) {
                                        type = 'cookie';
                                    } else if (lowerText.includes('subscribe') || lowerText.includes('newsletter')) {
                                        type = 'newsletter';
                                    } else if (lowerText.includes('sign in') || lowerText.includes('login')) {
                                        type = 'auth';
                                    } else if (lowerText.includes('ai') || lowerText.includes('assistant')) {
                                        type = 'ai_promotion';
                                    }
                                    
                                    found.push({
                                        selector: selector,
                                        type: type,
                                        text: text,
                                        zIndex: style.zIndex || '0',
                                        position: {
                                            top: rect.top,
                                            left: rect.left,
                                            width: rect.width,
                                            height: rect.height
                                        }
                                    });
                                }
                            }
                        } catch (e) {
                            // Ignore selector errors
                        }
                    }
                    
                    // Sort by z-index (highest first)
                    found.sort((a, b) => {
                        const zA = parseInt(a.zIndex) || 0;
                        const zB = parseInt(b.zIndex) || 0;
                        return zB - zA;
                    });
                    
                    return found;
                }
            ''' % str(self.MODAL_SELECTORS))
            
            detected = popup_info
            
            if detected:
                logger.info(f"Detected {len(detected)} popup(s)")
                for popup in detected[:3]:  # Log first 3
                    logger.debug(f"  - Type: {popup['type']}, Text preview: {popup['text'][:50]}...")
            
        except Exception as e:
            logger.debug(f"Error detecting popups: {e}")
        
        return detected

    async def handle_cookie_popup(self) -> bool:
        """
        Handle cookie consent popups.
        
        Returns:
            True if handled, False otherwise
        """
        for selector in self.COOKIE_SELECTORS:
            try:
                button = await self.page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    logger.success(f"Accepted cookies with selector: {selector}")
                    await self.page.wait_for_timeout(1000)
                    self.handled_popups.append(('cookie', selector))
                    return True
            except Exception as e:
                logger.debug(f"Cookie selector {selector} failed: {e}")
                continue
        
        return False

    async def close_popup(self, popup_info: Optional[Dict] = None) -> bool:
        """
        Close a popup using various strategies.
        
        Args:
            popup_info: Optional popup information from detect_popups
            
        Returns:
            True if closed, False otherwise
        """
        # Try close buttons
        for selector in self.CLOSE_SELECTORS:
            try:
                button = await self.page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    logger.success(f"Closed popup with selector: {selector}")
                    await self.page.wait_for_timeout(500)
                    self.handled_popups.append(('close', selector))
                    return True
            except Exception:
                continue
        
        # Try ESC key as fallback
        try:
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(500)
            
            # Check if popup is gone
            if popup_info:
                still_visible = await self.page.evaluate(
                    f'!!document.querySelector("{popup_info["selector"]}")'
                )
                if not still_visible:
                    logger.success("Closed popup with ESC key")
                    self.handled_popups.append(('escape', popup_info['selector']))
                    return True
        except Exception as e:
            logger.debug(f"ESC key failed: {e}")
        
        return False

    async def handle_all_popups(self, max_attempts: int = 3, delay_ms: int = 1000) -> int:
        """
        Detect and handle all popups on the page.
        
        Args:
            max_attempts: Maximum number of attempts to clear popups
            delay_ms: Delay between attempts in milliseconds
            
        Returns:
            Number of popups handled
        """
        total_handled = 0
        
        for attempt in range(max_attempts):
            # Detect popups
            popups = await self.detect_popups()
            
            if not popups:
                if attempt == 0:
                    logger.debug("No popups detected")
                break
            
            logger.info(f"Attempt {attempt + 1}: Found {len(popups)} popup(s)")
            
            # Handle each popup
            for popup in popups:
                handled = False
                
                # Try cookie handling first if it's a cookie popup
                if popup['type'] == 'cookie':
                    handled = await self.handle_cookie_popup()
                
                # Otherwise try to close it
                if not handled:
                    handled = await self.close_popup(popup)
                
                if handled:
                    total_handled += 1
                    await self.page.wait_for_timeout(delay_ms)
                else:
                    logger.warning(f"Could not handle popup: {popup['type']}")
            
            # Small delay before next detection
            await self.page.wait_for_timeout(500)
        
        if total_handled > 0:
            logger.success(f"Successfully handled {total_handled} popup(s)")
        
        return total_handled

    async def wait_and_handle_popups(self, timeout_ms: int = 5000) -> int:
        """
        Wait for popups to appear and handle them.
        
        Args:
            timeout_ms: Maximum time to wait for popups
            
        Returns:
            Number of popups handled
        """
        start_time = asyncio.get_event_loop().time()
        total_handled = 0
        
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout_ms:
            popups = await self.detect_popups()
            
            if popups:
                for popup in popups:
                    if popup['type'] == 'cookie':
                        if await self.handle_cookie_popup():
                            total_handled += 1
                    elif await self.close_popup(popup):
                        total_handled += 1
                
                if total_handled > 0:
                    break
            
            await self.page.wait_for_timeout(500)
        
        return total_handled


async def close_popups_async(
    page: Page,
    handle_cookies: bool = True,
    close_others: bool = True,
    max_attempts: int = 3,
    wait_first: bool = True,
    wait_ms: int = 2000
) -> Tuple[int, List]:
    """
    Convenience function to handle all popups on a page.
    
    Args:
        page: Playwright page object
        handle_cookies: Whether to accept cookie popups
        close_others: Whether to close other popups
        max_attempts: Maximum attempts to clear popups
        wait_first: Whether to wait for popups to appear first
        wait_ms: Time to wait for popups to appear
        
    Returns:
        Tuple of (number handled, list of handled popups)
    """
    handler = PopupHandler(page)
    
    # Wait for popups to appear if requested
    if wait_first:
        await page.wait_for_timeout(wait_ms)
    
    # Handle all popups
    total = await handler.handle_all_popups(max_attempts=max_attempts)
    
    return total, handler.handled_popups


async def ensure_no_popups_async(page: Page, check_interval_ms: int = 1000) -> bool:
    """
    Ensure no popups are blocking the page.

    Args:
        page: Playwright page object
        check_interval_ms: Interval to check for popups

    Returns:
        True if page is clear of popups
    """
    handler = PopupHandler(page)

    # Check multiple times
    for _ in range(3):
        popups = await handler.detect_popups()
        if popups:
            await handler.handle_all_popups(max_attempts=1)
            await page.wait_for_timeout(check_interval_ms)
        else:
            return True

    # Final check
    final_popups = await handler.detect_popups()
    return len(final_popups) == 0


def main(args):
    """Demonstrate PopupHandler functionality."""
    import asyncio
    from playwright.async_api import async_playwright

    async def demo():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            logger.info("PopupHandler: Starting demo")

            # Navigate to a page with popups
            await page.goto("https://www.springer.com", timeout=30000)
            await asyncio.sleep(2)

            # Demonstrate popup handling
            handler = PopupHandler(page)

            logger.info("Detecting popups...")
            popups = await handler.detect_popups()
            logger.info(f"Found {len(popups)} popup(s)")

            logger.info("Handling popups...")
            handled = await handler.handle_all_popups()
            logger.success(f"Successfully handled {handled} popup(s)")

            # Verify page is clear
            is_clear = await ensure_no_popups_async(page)
            if is_clear:
                logger.success("Page is clear of popups")
            else:
                logger.warning("Some popups may still be present")

            logger.success("PopupHandler demonstration complete")

            await asyncio.sleep(2)
            await browser.close()

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description="Popup handler demo")
    return parser.parse_args()


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# python -m scitex.browser.interaction.close_popups

# EOF