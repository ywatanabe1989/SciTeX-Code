#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 10:16:17 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_wait_redirects.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_wait_redirects.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from typing import Dict

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)


async def wait_redirects(
    page: Page,
    timeout: int = 30000,
    max_redirects: int = 10,
    show_progress: bool = False,
    track_chain: bool = True,
    wait_for_idle: bool = True,
) -> Dict:
    """
    Wait for redirect chain to complete after navigation has been initiated.

    This function should be called AFTER clicking a link or navigating, not before.
    It will wait for all redirects to complete and return detailed information.

    Args:
        page: Playwright page object
        timeout: Maximum wait time in milliseconds
        max_redirects: Maximum number of redirects to follow
        show_progress: Show popup messages during redirects (requires show_popup_message_async)
        track_chain: Whether to track detailed redirect chain
        wait_for_idle: Whether to wait for network idle after redirects

    Returns:
        dict: {
            'success': bool,
            'final_url': str,
            'redirect_count': int,
            'redirect_chain': list,  # if track_chain=True
            'total_time_ms': float,
            'timed_out': bool,
        }
    """
    if show_progress:
        try:
            from ._show_popup_message_async import show_popup_message_async
        except ImportError:
            logger.warning(
                "show_popup_message_async not available, disabling progress messages"
            )
            show_progress = False

    start_time = asyncio.get_event_loop().time()
    start_url = page.url

    # Tracking variables
    redirect_chain = [] if track_chain else None
    redirect_count = 0
    navigation_complete = asyncio.Event()
    timed_out = False

    def track_response(response: Response):
        nonlocal redirect_count

        # Only track main frame responses
        if response.frame != page.main_frame:
            return

        status = response.status
        url = response.url
        timestamp = asyncio.get_event_loop().time()

        # Track chain if requested
        if track_chain:
            redirect_chain.append(
                {
                    "step": len(redirect_chain) + 1,
                    "url": url,
                    "status": status,
                    "is_redirect": 300 <= status < 400,
                    "timestamp": timestamp,
                    "time_from_start_ms": (timestamp - start_time) * 1000,
                }
            )

        logger.debug(f"Response: {url} ({status})")

        # Show progress if enabled
        if show_progress and 300 <= status < 400:
            redirect_count += 1
            asyncio.create_task(
                show_popup_message_async(
                    page,
                    f"Redirect {redirect_count}: {url[:40]}...",
                    duration_ms=1000,
                )
            )

        # Check completion conditions
        if 300 <= status < 400:
            redirect_count += 1
            if redirect_count >= max_redirects:
                logger.warning(f"Max redirects ({max_redirects}) reached")
                navigation_complete.set()
        elif 200 <= status < 300:
            # Successful final destination
            if show_progress:
                asyncio.create_task(
                    show_popup_message_async(
                        page, f"Final: {url[:40]}...", duration_ms=1500
                    )
                )
            navigation_complete.set()
        elif status >= 400:
            # Error status
            logger.warning(f"Error response: {status} for {url}")
            navigation_complete.set()

    # Set up response tracking
    page.on("response", track_response)

    try:
        # Wait for navigation to complete
        try:
            await asyncio.wait_for(
                navigation_complete.wait(), timeout=timeout / 1000
            )
        except asyncio.TimeoutError:
            timed_out = True
            logger.warning(f"Redirect wait timeout after {timeout}ms")
            if show_progress:
                await show_popup_message_async(
                    page, "Redirect timeout, finalizing...", duration_ms=1500
                )

        # Wait for network idle if requested
        if wait_for_idle:
            try:
                idle_timeout = min(5000, timeout // 4)
                await page.wait_for_load_state(
                    "networkidle", timeout=idle_timeout
                )
            except:
                logger.debug("Network idle wait failed")

        # Calculate results
        end_time = asyncio.get_event_loop().time()
        total_time_ms = (end_time - start_time) * 1000
        final_url = page.url
        success = not timed_out and (
            final_url != start_url or redirect_count > 0
        )

        result = {
            "success": success,
            "final_url": final_url,
            "redirect_count": redirect_count,
            "total_time_ms": round(total_time_ms, 2),
            "timed_out": timed_out,
        }

        if track_chain:
            result["redirect_chain"] = redirect_chain

        # Log results
        if success:
            logger.success(
                f"Redirects complete: {start_url} -> {final_url} "
                f"({redirect_count} redirects, {total_time_ms:.0f}ms)"
            )
        elif timed_out:
            logger.warning(
                f"Redirect wait timed out after {total_time_ms:.0f}ms"
            )
        else:
            logger.info("No redirects detected")

        return result

    except Exception as e:
        logger.error(f"Wait redirects failed: {e}")
        end_time = asyncio.get_event_loop().time()
        return {
            "success": False,
            "final_url": page.url,
            "redirect_count": redirect_count,
            "total_time_ms": round((end_time - start_time) * 1000, 2),
            "timed_out": False,
            "error": str(e),
        }
    finally:
        # Clean up event listener
        try:
            page.remove_listener("response", track_response)
        except:
            pass


# Usage examples:
"""
# 1. Use wait_redirects standalone after manual navigation
await page.goto("https://example.com")
redirect_result = await wait_redirects(page, show_progress=True)

# 2. Use wait_redirects after form submission
await page.click('button[type="submit"]')
redirect_result = await wait_redirects(
    page,
    timeout=20000,
    track_chain=True
)

# 3. Advanced usage with full redirect chain analysis
result = await wait_redirects(page, track_chain=True)
if result['success']:
    print(f"Final URL: {result['final_url']}")
    print(f"Total redirects: {result['redirect_count']}")
    print(f"Total time: {result['total_time_ms']}ms")

    if 'redirect_chain' in result:
        for step in result['redirect_chain']:
            print(f"  {step['step']}. {step['url']} ({step['status']}) "
                  f"at +{step['time_from_start_ms']:.0f}ms")

# 4. Simple usage after any navigation
await some_navigation_action()
result = await wait_redirects(page)
if result['success']:
    print(f"Navigation complete: {result['final_url']}")
"""

# EOF
