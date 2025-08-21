#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _click_and_wait_v02-with-monitor.py
# ----------------------------------------

"""
Enhanced click and wait with JavaScript redirect monitor integration.

This version uses the JavaScript RedirectMonitor for better tracking.
"""

from typing import Dict, Optional
import asyncio

from playwright.async_api import Locator

from scitex import log
from scitex.scholar.browser.utils.JSLoader import JSLoader

logger = log.getLogger(__name__)


async def click_and_wait(
    link: Locator,
    message: str = "Clicking link...",
    wait_redirects_options: Optional[Dict] = None,
) -> dict:
    """
    Click link with JavaScript redirect monitoring for complete tracking.
    
    This enhanced version uses the RedirectMonitor JavaScript module for
    comprehensive redirect chain tracking including client-side redirects.
    
    Args:
        link: Playwright locator for the element to click
        message: Message to display during clicking
        wait_redirects_options: Options for redirect waiting
            - timeout: Maximum wait time in milliseconds (default: 30000)
            - use_js_monitor: Use JavaScript RedirectMonitor (default: True)
            - wait_for_article: Wait for article URL pattern (default: True)
    
    Returns:
        dict with redirect information and final URL
    """
    from ._highlight_element import highlight_element
    from ._show_popup_message_async import show_popup_message_async
    from ._wait_redirects import wait_redirects
    
    page = link.page
    context = page.context
    
    # Default options
    default_options = {
        "timeout": 30000,
        "use_js_monitor": True,
        "wait_for_article": True,
        "show_progress": True,
    }
    redirect_options = {**default_options, **(wait_redirects_options or {})}
    
    # Initial UI feedback
    await show_popup_message_async(page, message, duration_ms=1500)
    await highlight_element(link, 1000)
    
    initial_url = page.url
    href = await link.get_attribute("href") or ""
    text = await link.inner_text() or ""
    logger.debug(f"Clicking: '{text[:30]}' -> {href[:50]}")
    
    try:
        # If using JavaScript monitor, inject and start it
        if redirect_options.get("use_js_monitor"):
            # Load redirect monitor JavaScript
            js_loader = JSLoader()
            redirect_monitor_js = js_loader.load("utils/network/redirect_monitor.js")
            
            # Inject and start monitor
            await page.evaluate(f"""
                {redirect_monitor_js}
                
                // Create global monitor instance
                window.__redirectMonitor = new RedirectMonitor();
                
                // Start monitoring with callbacks
                window.__redirectMonitor.start({{
                    maxRedirects: 30,
                    onRedirect: (info) => {{
                        console.log('Redirect detected:', info.url);
                    }},
                    onComplete: (result) => {{
                        console.log('Redirect complete:', result.finalUrl);
                    }}
                }});
            """)
            
            logger.debug("JavaScript redirect monitor started")
        
        # Handle potential new page opening
        new_page_opened = False
        try:
            async with context.expect_page(timeout=5000) as new_page_info:
                await link.click()
                new_page = await new_page_info.value
                page = new_page
                new_page_opened = True
                logger.debug("New page opened, switching context")
                
                # Re-inject monitor on new page if needed
                if redirect_options.get("use_js_monitor"):
                    await page.evaluate(f"""
                        {redirect_monitor_js}
                        window.__redirectMonitor = new RedirectMonitor();
                        window.__redirectMonitor.start();
                    """)
        except:
            await link.click()
        
        # If using JS monitor, wait for stable URL
        if redirect_options.get("use_js_monitor"):
            # Wait for URL to stabilize
            stability_result = await page.evaluate("""
                async () => {
                    if (window.__redirectMonitor) {
                        // Wait for stable URL (no changes for 3 seconds)
                        const result = await window.__redirectMonitor.waitForStableUrl(3000, 30000);
                        
                        // Stop monitoring and get chain
                        const finalData = window.__redirectMonitor.stop();
                        
                        return {
                            ...result,
                            ...finalData
                        };
                    }
                    return null;
                }
            """)
            
            if stability_result:
                logger.info(f"JS Monitor: {stability_result.get('redirectCount', 0)} redirects tracked")
                logger.info(f"Final URL: {stability_result.get('finalUrl', page.url)}")
                
                # Show redirect chain if available
                if stability_result.get("chain"):
                    for step in stability_result.get("chain", []):
                        if step.get("step", 0) > 0:  # Skip initial URL
                            logger.debug(
                                f"  Step {step['step']}: {step['type']} -> {step['url'][:60]}... "
                                f"({step.get('duration', 0)}ms)"
                            )
                
                # Return enhanced result
                return {
                    "success": True,
                    "final_url": stability_result.get("finalUrl", page.url),
                    "page": page,
                    "new_page_opened": new_page_opened,
                    "redirect_count": stability_result.get("redirectCount", 0),
                    "total_time_ms": stability_result.get("totalTime", 0),
                    "redirect_chain": stability_result.get("chain", []),
                    "found_article": any(
                        step.get("isFinal", False) 
                        for step in stability_result.get("chain", [])
                    ),
                    "js_monitor_used": True,
                }
        
        # Fallback to Python-based wait_redirects
        redirect_result = await wait_redirects(page, **redirect_options)
        
        # Combine results
        result = {
            "success": redirect_result["success"] or new_page_opened,
            "final_url": redirect_result["final_url"],
            "page": page,
            "new_page_opened": new_page_opened,
            "js_monitor_used": False,
            **redirect_result,
        }
        
        # Final feedback
        if result["success"]:
            await show_popup_message_async(
                page,
                f"Complete: {result['final_url'][:40]}... "
                f"({result.get('redirect_count', 0)} redirects)",
                duration_ms=2000,
            )
            logger.success(f"Navigation: {initial_url} -> {result['final_url']}")
        else:
            logger.warning("Navigation failed or incomplete")
        
        return result
        
    except Exception as e:
        logger.error(f"Click and wait failed: {e}")
        return {
            "success": False,
            "final_url": page.url,
            "page": page,
            "error": str(e),
            "js_monitor_used": redirect_options.get("use_js_monitor", False),
        }