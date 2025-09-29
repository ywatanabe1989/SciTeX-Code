#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _wait_redirects_v02-auth-aware.py
# ----------------------------------------

"""
Enhanced redirect waiter that handles authentication endpoints properly.

This version continues waiting even after receiving 200 status from auth endpoints,
as they often perform client-side redirects.
"""

import asyncio
from typing import Dict, List
from urllib.parse import urlparse

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)

# Known authentication/intermediate endpoints that perform client-side redirects
AUTH_ENDPOINTS = [
    "auth.elsevier.com",
    "login.elsevier.com",
    "idp.nature.com",
    "secure.jbs.elsevierhealth.com",
    "go.openathens.net",
    "login.openathens.net",
    "shibboleth",
    "saml",
    "/ShibAuth/",
    "/authenticate",
    "/login",
    "/signin",
    "/sso/",
]

def is_auth_endpoint(url: str) -> bool:
    """Check if URL is likely an authentication/intermediate endpoint."""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    
    # Check hostname
    for auth_pattern in AUTH_ENDPOINTS:
        if auth_pattern in parsed.hostname:
            return True
    
    # Check path
    for auth_pattern in AUTH_ENDPOINTS:
        if auth_pattern.startswith("/") and auth_pattern in parsed.path:
            return True
            
    return False

def is_final_article_url(url: str) -> bool:
    """Check if URL looks like a final article page."""
    indicators = [
        "/science/article/",
        "/articles/",
        "/content/",
        "/full/",
        "/fulltext/",
        "/doi/full/",
        "/doi/abs/",
        "/doi/pdf/",
        ".pdf",
    ]
    
    url_lower = url.lower()
    for indicator in indicators:
        if indicator in url_lower:
            return True
    return False


async def wait_redirects(
    page: Page,
    timeout: int = 30000,
    max_redirects: int = 30,
    show_progress: bool = False,
    track_chain: bool = True,
    wait_for_idle: bool = True,
    auth_aware: bool = True,  # New parameter
) -> Dict:
    """
    Wait for redirect chain to complete, handling authentication endpoints.
    
    Args:
        page: Playwright page object
        timeout: Maximum wait time in milliseconds
        max_redirects: Maximum number of redirects to follow
        show_progress: Show popup messages during redirects
        track_chain: Whether to track detailed redirect chain
        wait_for_idle: Whether to wait for network idle after redirects
        auth_aware: Continue waiting after auth endpoints (default: True)
    
    Returns:
        dict with redirect information
    """
    if show_progress:
        try:
            from ._show_popup_message_async import show_popup_message_async
        except ImportError:
            logger.warning("show_popup_message_async not available")
            show_progress = False

    start_time = asyncio.get_event_loop().time()
    start_url = page.url
    
    # Tracking variables
    redirect_chain = [] if track_chain else None
    redirect_count = 0
    navigation_complete = asyncio.Event()
    timed_out = False
    last_url = start_url
    last_response_time = start_time
    found_article = False
    
    def track_response(response: Response):
        nonlocal redirect_count, last_url, last_response_time, found_article
        
        # Only track main frame responses
        if response.frame != page.main_frame:
            return
        
        status = response.status
        url = response.url
        timestamp = asyncio.get_event_loop().time()
        last_response_time = timestamp
        
        # Track chain if requested
        if track_chain:
            redirect_chain.append({
                "step": len(redirect_chain) + 1,
                "url": url,
                "status": status,
                "is_redirect": 300 <= status < 400,
                "is_auth": is_auth_endpoint(url),
                "timestamp": timestamp,
                "time_from_start_ms": (timestamp - start_time) * 1000,
            })
        
        logger.debug(f"Response: {url[:80]} ({status})")
        
        # Show progress if enabled
        if show_progress and (300 <= status < 400 or is_auth_endpoint(url)):
            redirect_count += 1
            asyncio.create_task(
                show_popup_message_async(
                    page,
                    f"{'Auth' if is_auth_endpoint(url) else 'Redirect'} {redirect_count}: {url[:40]}...",
                    duration_ms=1000,
                )
            )
        
        # Check if we reached final article
        if is_final_article_url(url) and 200 <= status < 300:
            found_article = True
            logger.info(f"Found article page: {url[:80]}")
            if show_progress:
                asyncio.create_task(
                    show_popup_message_async(
                        page, f"Article found: {url[:40]}...", duration_ms=2000
                    )
                )
            # Don't set complete immediately - wait a bit for any final redirects
            asyncio.create_task(_delayed_complete())
        
        # Handle different response types
        if 300 <= status < 400:
            redirect_count += 1
            if redirect_count >= max_redirects:
                logger.warning(f"Max redirects ({max_redirects}) reached")
                navigation_complete.set()
                
        elif 200 <= status < 300:
            # For auth endpoints, continue waiting
            if auth_aware and is_auth_endpoint(url):
                logger.debug(f"Auth endpoint reached, continuing to wait: {url[:80]}")
                if show_progress:
                    asyncio.create_task(
                        show_popup_message_async(
                            page, "Processing authentication...", duration_ms=2000
                        )
                    )
                # Don't complete yet - auth endpoints often do client-side redirects
            elif not auth_aware or found_article:
                # Non-auth endpoint or article found - likely complete
                asyncio.create_task(_delayed_complete())
                
        elif status >= 400:
            logger.warning(f"Error response: {status} for {url}")
            navigation_complete.set()
        
        last_url = url
    
    async def _delayed_complete():
        """Set navigation complete after a short delay to catch final redirects."""
        await asyncio.sleep(2)  # Wait 2 seconds for any final redirects
        if not navigation_complete.is_set():
            navigation_complete.set()
    
    async def check_url_stability():
        """Monitor URL changes even without network responses."""
        stable_count = 0
        last_checked_url = page.url
        
        while not navigation_complete.is_set():
            await asyncio.sleep(1)
            current_url = page.url
            
            # Check if URL changed
            if current_url != last_checked_url:
                logger.debug(f"URL changed via client-side: {current_url[:80]}")
                last_checked_url = current_url
                stable_count = 0
                
                # Check if we reached an article
                if is_final_article_url(current_url):
                    found_article = True
                    logger.info(f"Article URL detected: {current_url[:80]}")
                    await asyncio.sleep(2)  # Wait a bit for page to stabilize
                    navigation_complete.set()
                    break
            else:
                stable_count += 1
                
                # If URL stable for 5 seconds and not on auth page, complete
                if stable_count >= 5:
                    if not is_auth_endpoint(current_url) or found_article:
                        logger.debug(f"URL stable for 5s, completing: {current_url[:80]}")
                        navigation_complete.set()
                        break
                    elif stable_count >= 10:
                        # Even auth pages shouldn't take more than 10s
                        logger.warning(f"Auth page stable for 10s, completing: {current_url[:80]}")
                        navigation_complete.set()
                        break
    
    # Set up response tracking
    page.on("response", track_response)
    
    # Start URL stability checker
    stability_task = asyncio.create_task(check_url_stability())
    
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
        
        # Cancel stability checker
        stability_task.cancel()
        
        # Wait for network idle if requested
        if wait_for_idle and not timed_out:
            try:
                idle_timeout = min(5000, timeout // 4)
                await page.wait_for_load_state("networkidle", timeout=idle_timeout)
            except:
                logger.debug("Network idle wait failed")
        
        # Calculate results
        end_time = asyncio.get_event_loop().time()
        total_time_ms = (end_time - start_time) * 1000
        final_url = page.url
        
        # Determine success
        success = (
            not timed_out and 
            (final_url != start_url or redirect_count > 0) and
            (not is_auth_endpoint(final_url) or found_article)
        )
        
        result = {
            "success": success,
            "final_url": final_url,
            "redirect_count": redirect_count,
            "total_time_ms": round(total_time_ms, 2),
            "timed_out": timed_out,
            "found_article": found_article,
            "stopped_at_auth": is_auth_endpoint(final_url) and not found_article,
        }
        
        if track_chain:
            result["redirect_chain"] = redirect_chain
        
        # Log results
        if success:
            logger.success(
                f"Redirects complete: {start_url[:40]} -> {final_url[:40]} "
                f"({redirect_count} redirects, {total_time_ms:.0f}ms)"
            )
        elif result.get("stopped_at_auth"):
            logger.warning(
                f"Stopped at auth endpoint: {final_url[:80]} "
                f"(after {redirect_count} redirects, {total_time_ms:.0f}ms)"
            )
        elif timed_out:
            logger.warning(f"Redirect wait timed out after {total_time_ms:.0f}ms")
        else:
            logger.debug("No redirects detected")
        
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
        # Clean up
        try:
            page.remove_listener("response", track_response)
            stability_task.cancel()
        except:
            pass