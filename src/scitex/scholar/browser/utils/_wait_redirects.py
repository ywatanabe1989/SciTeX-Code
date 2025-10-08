#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 00:34:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/utils/_wait_redirects.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_wait_redirects.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Enhanced redirect waiter that handles authentication endpoints properly.

This version continues waiting even after receiving 200 status from auth endpoints,
as they often perform client-side redirects.

Auth patterns are loaded from Scholar config (authentication.auth_endpoint_patterns).
"""

import asyncio
from typing import Dict, List
from urllib.parse import urlparse

from playwright.async_api import Page, Response

from scitex import logging

logger = logging.getLogger(__name__)

# Cache for config-loaded patterns
_AUTH_ENDPOINTS: List[str] | None = None
_ARTICLE_PATTERNS: List[str] | None = None


def _load_auth_patterns() -> tuple[List[str], List[str]]:
    """Load authentication patterns from Scholar config."""
    global _AUTH_ENDPOINTS, _ARTICLE_PATTERNS

    if _AUTH_ENDPOINTS is not None and _ARTICLE_PATTERNS is not None:
        return _AUTH_ENDPOINTS, _ARTICLE_PATTERNS

    try:
        from ...config import ScholarConfig

        config = ScholarConfig()
        _AUTH_ENDPOINTS = config.resolve("auth_endpoint_patterns", None)
        _ARTICLE_PATTERNS = config.resolve("article_url_patterns", None)

        if not _AUTH_ENDPOINTS:
            logger.warning(
                "No auth_endpoint_patterns in config, using fallback"
            )
            _AUTH_ENDPOINTS = _get_fallback_auth_patterns()
        if not _ARTICLE_PATTERNS:
            logger.warning("No article_url_patterns in config, using fallback")
            _ARTICLE_PATTERNS = _get_fallback_article_patterns()

    except Exception as e:
        logger.warning(
            f"Failed to load patterns from config: {e}, using fallback"
        )
        _AUTH_ENDPOINTS = _get_fallback_auth_patterns()
        _ARTICLE_PATTERNS = _get_fallback_article_patterns()

    return _AUTH_ENDPOINTS, _ARTICLE_PATTERNS


def _get_fallback_auth_patterns() -> List[str]:
    """Fallback auth patterns if config fails."""
    return [
        "go.openathens.net",
        "login.openathens.net",
        "auth.elsevier.com",
        "login.elsevier.com",
        "idp.nature.com",
        "secure.jbs.elsevierhealth.com",
        "shibboleth",
        "saml",
        "/ShibAuth/",
        "/authenticate",
        "/login",
        "/signin",
        "/sso/",
    ]


def _get_fallback_article_patterns() -> List[str]:
    """Fallback article patterns if config fails."""
    return [
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


def is_auth_endpoint(url: str) -> bool:
    """Check if URL is likely an authentication/intermediate endpoint."""
    auth_patterns, _ = _load_auth_patterns()
    url_lower = url.lower()
    parsed = urlparse(url_lower)

    # Check hostname
    for auth_pattern in auth_patterns:
        if not auth_pattern.startswith("/"):  # Hostname pattern
            if parsed.hostname and auth_pattern in parsed.hostname:
                return True

    # Check path
    for auth_pattern in auth_patterns:
        if auth_pattern.startswith("/"):  # Path pattern
            if auth_pattern in parsed.path:
                return True

    return False


def is_final_article_url(url: str) -> bool:
    """Check if URL looks like a final article page."""
    # Exclude chrome extensions and other non-article URLs
    if (
        url.startswith("chrome-extension://")
        or url.startswith("about:")
        or url.startswith("data:")
    ):
        return False

    _, article_patterns = _load_auth_patterns()
    url_lower = url.lower()

    for indicator in article_patterns:
        if indicator in url_lower:
            return True
    return False


def is_captcha_page(url: str) -> bool:
    """Check if URL or page indicates a CAPTCHA challenge."""
    url_lower = url.lower()

    # Cloudflare CAPTCHA indicators
    captcha_indicators = [
        "__cf_chl_rt_tk=",  # Cloudflare challenge runtime token
        "__cf_chl_tk=",  # Cloudflare challenge token
        "/cdn-cgi/challenge-platform/",  # Cloudflare challenge page
        "captcha",
        "challenge",
        "cf_clearance",
    ]

    return any(indicator in url_lower for indicator in captcha_indicators)


async def detect_captcha_on_page(page: Page) -> bool:
    """Detect if the current page shows a CAPTCHA challenge."""
    try:
        # Check URL first
        if is_captcha_page(page.url):
            return True

        # Check for Cloudflare challenge elements
        captcha_selectors = [
            "#challenge-form",
            ".cf-challenge",
            "[data-ray]",  # Cloudflare Ray ID
            "iframe[src*='captcha']",
            "iframe[src*='recaptcha']",
            "#cf-wrapper",
        ]

        for selector in captcha_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=500)
                if element:
                    return True
            except:
                continue

        # Check page title
        try:
            title = await page.title()
            if "challenge" in title.lower() or "captcha" in title.lower():
                return True
        except:
            pass

        return False

    except Exception as e:
        logger.debug(f"CAPTCHA detection error: {e}")
        return False


async def wait_redirects(
    page: Page,
    timeout: int = 15_000,
    max_redirects: int = 30,
    show_progress: bool = True,
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
        from scitex.browser import show_popup_and_capture_async

    start_time = asyncio.get_event_loop().time()
    start_url = page.url

    if show_progress:
        await show_popup_and_capture_async(
            page,
            f"Waiting for redirects (max {timeout/1000:.0f}s)...",
            duration_ms=timeout,
        )

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
            redirect_chain.append(
                {
                    "step": len(redirect_chain) + 1,
                    "url": url,
                    "status": status,
                    "is_redirect": 300 <= status < 400,
                    "is_auth": is_auth_endpoint(url),
                    "timestamp": timestamp,
                    "time_from_start_ms": (timestamp - start_time) * 1000,
                }
            )

        logger.debug(f"Response: {url[:80]} ({status})")

        # Show progress if enabled
        if show_progress and (300 <= status < 400 or is_auth_endpoint(url)):
            redirect_count += 1
            asyncio.create_task(
                show_popup_and_capture_async(
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
                    show_popup_and_capture_async(
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
                logger.debug(
                    f"Auth endpoint reached, continuing to wait: {url[:80]}"
                )
                if show_progress:
                    asyncio.create_task(
                        show_popup_and_capture_async(
                            page,
                            "Processing authentication...",
                            duration_ms=2000,
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
        await asyncio.sleep(2)  # Reduced from 5 to 2 seconds
        if not navigation_complete.is_set():
            navigation_complete.set()

    async def check_url_stability():
        """Monitor URL changes, network activity, and page state for robust completion."""
        stable_count = 0
        last_checked_url = page.url
        last_dom_state = None
        dom_stable_count = 0
        captcha_detected = False
        captcha_wait_start = None

        while not navigation_complete.is_set():
            try:
                await asyncio.sleep(1)
                current_url = page.url
                current_time = asyncio.get_event_loop().time()

                # Calculate time since last network activity
                time_since_activity = current_time - last_response_time

                # Check for CAPTCHA
                if not captcha_detected:
                    captcha_detected = await detect_captcha_on_page(page)
                    if captcha_detected:
                        captcha_wait_start = current_time
                        logger.warning(
                            f"CAPTCHA detected on page: {current_url[:80]}"
                        )
                        if show_progress:
                            from scitex.browser import (
                                show_popup_and_capture_async,
                            )

                            asyncio.create_task(
                                show_popup_and_capture_async(
                                    page,
                                    "CAPTCHA detected - waiting for solver extension...",
                                    duration_ms=5000,
                                )
                            )

                # Check page load state
                try:
                    load_state = await page.evaluate(
                        "() => document.readyState"
                    )
                    page_loaded = load_state == "complete"
                except:
                    page_loaded = False

                # Check DOM stability (body exists and has content)
                try:
                    dom_state = await page.evaluate(
                        """
                        () => {
                            const body = document.body;
                            if (!body) return 'no-body';
                            const links = document.querySelectorAll('a').length;
                            const scripts = document.querySelectorAll('script').length;
                            return `${body.childElementCount}-${links}-${scripts}`;
                        }
                    """
                    )
                    dom_changed = dom_state != last_dom_state
                    if not dom_changed and last_dom_state:
                        dom_stable_count += 1
                    else:
                        dom_stable_count = 0
                    last_dom_state = dom_state
                except:
                    dom_state = None
                    dom_stable_count = 0

                # Check if URL changed
                if current_url != last_checked_url:
                    logger.debug(f"URL changed: {current_url[:80]}")
                    last_checked_url = current_url
                    stable_count = 0
                    dom_stable_count = 0

                    # Check if we reached an article
                    if is_final_article_url(current_url):
                        found_article = True
                        logger.info(
                            f"Article URL detected: {current_url[:80]}"
                        )
                        await asyncio.sleep(
                            1
                        )  # Short wait for final resources
                        navigation_complete.set()
                        break
                else:
                    stable_count += 1

                # ROBUST COMPLETION LOGIC:
                # Combine multiple signals: URL stability, network inactivity, page loaded, DOM stable

                # CAPTCHA path: Wait much longer for CAPTCHA solver extension
                if captcha_detected:
                    captcha_wait_time = (
                        current_time - captcha_wait_start
                        if captcha_wait_start
                        else 0
                    )

                    # Check if CAPTCHA is still present
                    still_captcha = await detect_captcha_on_page(page)

                    if not still_captcha:
                        # CAPTCHA solved! Wait a bit for redirect
                        logger.success(
                            "CAPTCHA appears to be solved, waiting for redirect..."
                        )
                        if show_progress:
                            from scitex.browser import (
                                show_popup_and_capture_async,
                            )

                            asyncio.create_task(
                                show_popup_and_capture_async(
                                    page,
                                    "CAPTCHA solved! Waiting for redirect...",
                                    duration_ms=2000,
                                )
                            )
                        await asyncio.sleep(
                            3
                        )  # Wait for redirect after CAPTCHA
                        captcha_detected = False
                        captcha_wait_start = None
                        stable_count = 0
                        dom_stable_count = 0
                        continue

                    # Give CAPTCHA solver up to 60 seconds
                    if captcha_wait_time < 60:
                        if (
                            int(captcha_wait_time) % 10 == 0
                            and captcha_wait_time > 0
                        ):
                            logger.info(
                                f"CAPTCHA solver working... ({int(60 - captcha_wait_time)}s remaining)"
                            )
                        continue
                    else:
                        logger.warning(
                            "CAPTCHA solver timeout (60s) - continuing anyway"
                        )
                        if show_progress:
                            from scitex.browser import (
                                show_popup_and_capture_async,
                            )

                            asyncio.create_task(
                                show_popup_and_capture_async(
                                    page,
                                    "CAPTCHA solver timeout - manual intervention may be needed",
                                    duration_ms=3000,
                                )
                            )
                        captcha_detected = False  # Stop waiting for CAPTCHA

                # Fast path: Everything stable and page loaded
                if (
                    stable_count >= 2
                    and time_since_activity >= 2
                    and page_loaded
                    and dom_stable_count >= 2
                ):
                    if not is_auth_endpoint(current_url) or found_article:
                        logger.debug(
                            f"Complete: URL+network+DOM stable (2s), page loaded"
                        )
                        navigation_complete.set()
                        break

                # Medium path: URL and network stable for longer
                elif stable_count >= 3 and time_since_activity >= 3:
                    if not is_auth_endpoint(current_url) or found_article:
                        logger.debug(f"Complete: URL+network stable (3s)")
                        navigation_complete.set()
                        break

                # Auth page path: Wait longer for delayed redirects
                elif stable_count >= 5 and time_since_activity >= 5:
                    if is_auth_endpoint(current_url):
                        # Extra check: make sure DOM is stable too
                        if dom_stable_count >= 3:
                            logger.debug(
                                f"Complete: Auth page stable (5s) with stable DOM"
                            )
                            navigation_complete.set()
                            break

                # Timeout path: Absolute max wait (extended for potential CAPTCHA)
                elif stable_count >= 30:
                    logger.warning(
                        f"Complete: Timeout (30s) - URL: {current_url[:80]}"
                    )
                    navigation_complete.set()
                    break

            except Exception as e:
                logger.debug(f"Error in stability check: {e}")
                # On error, if we've waited a reasonable time, complete
                if stable_count >= 5:
                    logger.warning(f"Complete: Error after 5s - {str(e)[:50]}")
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
                await show_popup_and_capture_async(
                    page, "Redirect timeout, finalizing...", duration_ms=1500
                )

        # Cancel stability checker
        stability_task.cancel()

        # Wait for network idle if requested
        if wait_for_idle and not timed_out:
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

        # Determine success
        success = (
            not timed_out
            and (final_url != start_url or redirect_count > 0)
            and (not is_auth_endpoint(final_url) or found_article)
        )

        result = {
            "success": success,
            "final_url": final_url,
            "redirect_count": redirect_count,
            "total_time_ms": round(total_time_ms, 2),
            "timed_out": timed_out,
            "found_article": found_article,
            "stopped_at_auth": is_auth_endpoint(final_url)
            and not found_article,
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
            logger.warning(
                f"Redirect wait timed out after {total_time_ms:.0f}ms"
            )
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

# EOF
