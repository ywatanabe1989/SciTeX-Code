#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:08:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/utils/_click_and_wait.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Dict, Optional

from playwright.async_api import Locator

from scitex import logging

logger = logging.getLogger(__name__)


async def click_and_wait(
    link: Locator,
    message: str = "Clicking link...",
    wait_redirects_options: Optional[Dict] = None,
) -> dict:
    """
    Click link with visual feedback and wait for redirect chain to complete.

    This function combines clicking logic with redirect waiting using the
    standalone wait_redirects function for better modularity.

    Args:
        link: Playwright locator for the element to click
        message: Message to display during clicking
        wait_redirects_options: Options to pass to wait_redirects function
            - timeout: Maximum wait time in milliseconds (default: 30000)
            - max_redirects: Maximum number of redirects to follow (default: 10)
            - show_progress: Show popup messages during redirects (default: False)
            - track_chain: Whether to track detailed redirect chain (default: True)
            - wait_for_idle: Whether to wait for network idle (default: True)

    Returns:
        dict: {
            'success': bool,
            'final_url': str,
            'page': Page,
            'new_page_opened': bool,
            'redirect_count': int,
            'redirect_chain': list,  # if track_chain=True
            'total_time_ms': float,
            'timed_out': bool,
        }
    """
    from scitex.browser.debugging import highlight_element_async
    from ._show_popup_and_capture_async import show_popup_and_capture_async
    from ._wait_redirects import wait_redirects

    page = link.page
    context = page.context

    # Initial UI feedback
    await show_popup_and_capture_async(page, message, duration_ms=1500)
    await highlight_element_async(link, 1000)

    initial_url = page.url
    href = await link.get_attribute("href") or ""
    text = await link.inner_text() or ""
    logger.debug(f"Clicking: '{text[:30]}' -> {href[:50]}")

    try:
        # Handle potential new page opening
        new_page_opened = False
        try:
            async with context.expect_page(timeout=5000) as new_page_info:
                await link.click()
                new_page = await new_page_info.value
                page = new_page
                new_page_opened = True
                logger.debug("New page opened, switching context")
        except:
            await link.click()

        # Use standalone wait_redirects function
        redirect_options = wait_redirects_options or {}
        redirect_result = await wait_redirects(page, **redirect_options)

        # Combine results
        result = {
            "success": redirect_result["success"] or new_page_opened,
            "final_url": redirect_result["final_url"],
            "page": page,
            "new_page_opened": new_page_opened,
            **redirect_result,  # Include all redirect details
        }

        # Final feedback
        if result["success"]:
            await show_popup_and_capture_async(
                page,
                f"Complete: {result['final_url'][:40]}... "
                f"({redirect_result['redirect_count']} redirects)",
                duration_ms=2000,
            )
            logger.success(
                f"Navigation: {initial_url} -> {result['final_url']}"
            )
        else:
            logger.warning("Navigation failed or no change")

        return result

    except Exception as e:
        logger.error(f"Click and wait failed: {e}")
        return {
            "success": False,
            "final_url": initial_url,
            "page": page,
            "error": str(e),
        }


# Convenience function with common redirect options
async def click_and_wait_with_progress(
    link: Locator,
    message: str = "Clicking link...",
    timeout: int = 30000,
) -> dict:
    """
    Click and wait with progress messages enabled.

    This is a convenience function for the common case of wanting
    to see redirect progress messages.
    """
    return await click_and_wait(
        link,
        message,
        wait_redirects_options={
            "timeout": timeout,
            "show_progress": True,
            "track_chain": True,
        },
    )


# Convenience function for fast clicking without detailed tracking
async def click_and_wait_fast(
    link: Locator,
    message: str = "Clicking link...",
    timeout: int = 15000,
) -> dict:
    """
    Click and wait with minimal overhead for faster execution.

    This disables chain tracking and progress messages for speed.
    """
    return await click_and_wait(
        link,
        message,
        wait_redirects_options={
            "timeout": timeout,
            "show_progress": False,
            "track_chain": False,
            "wait_for_idle": False,
        },
    )


# Usage examples:
"""
# 1. Basic click and wait (same as before)
result = await click_and_wait(link)

# 2. Click and wait with custom redirect options
result = await click_and_wait(
    link,
    wait_redirects_options={
        "timeout": 15000,
        "show_progress": True,
        "track_chain": True
    }
)

# 3. Click and wait with progress (convenience function)
result = await click_and_wait_with_progress(link, "Loading paper...")

# 4. Fast click and wait (minimal overhead)
result = await click_and_wait_fast(link, timeout=10000)

# 5. Access detailed redirect information
result = await click_and_wait(link, wait_redirects_options={"track_chain": True})
if result['success'] and 'redirect_chain' in result:
    print(f"Redirect chain:")
    for step in result['redirect_chain']:
        print(f"  {step['step']}. {step['url']} ({step['status']})")
"""

# EOF
