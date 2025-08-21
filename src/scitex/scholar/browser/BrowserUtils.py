#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 18:40:35 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/BrowserUtils.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/BrowserUtils.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from typing import Any, Dict, List, Optional

"""Shared browser utilities to avoid circular dependencies.

This module contains browser automation utilities that can be used
by both BrowserAuthenticator and SSO automators without creating
circular dependencies.
"""

from playwright.async_api import Browser, BrowserContext, Page, TimeoutError

from scitex import log

logger = log.getLogger(__name__)


class BrowserUtils:
    """Shared browser automation utilities."""

    @staticmethod
    async def capture_debug_info(
        page: Page, prefix: str = "debug"
    ) -> Dict[str, str]:
        """Capture screenshot and HTML for debugging failed operations.

        Args:
            page: Browser page
            prefix: Filename prefix for debug files

        Returns:
            Dict with screenshot_path and html_path
        """
        import time

        timestamp = int(time.time())

        try:
            screenshot_path = f"/tmp/{prefix}_screenshot_{timestamp}.png"
            html_path = f"/tmp/{prefix}_page_{timestamp}.html"

            await page.screenshot(path=screenshot_path, full_page=True)
            html_content = await page.content()

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.debug(f"Debug info saved: {screenshot_path}, {html_path}")
            return {"screenshot": screenshot_path, "html": html_path}

        except Exception as e:
            logger.error(f"Failed to capture debug info: {e}")
            return {"screenshot": "", "html": ""}

    @staticmethod
    async def debug_element_info(page: Page, selector: str) -> Dict[str, Any]:
        """Get detailed information about an element for debugging.

        Args:
            page: Browser page
            selector: CSS selector for element

        Returns:
            Dict with element information
        """
        try:
            info = await page.evaluate(
                """(selector) => {
                const element = document.querySelector(selector);
                if (!element) return {'exists': false};

                const rect = element.getBoundingClientRect();
                const styles = window.getComputedStyle(element);

                return {
                    'exists': true,
                    'tagName': element.tagName,
                    'type': element.type || 'N/A',
                    'name': element.name || 'N/A',
                    'id': element.id || 'N/A',
                    'className': element.className || 'N/A',
                    'visible': styles.display !== 'none' && styles.visibility !== 'hidden',
                    'disabled': element.disabled || false,
                    'readonly': element.readonly || false,
                    'position': {
                        'x': rect.x,
                        'y': rect.y,
                        'width': rect.width,
                        'height': rect.height
                    },
                    'value': element.value || '',
                    'innerHTML': element.innerHTML.substring(0, 100)
                };
            }""",
                selector,
            )

            logger.debug(f"Element info for {selector}: {info}")
            return info

        except Exception as e:
            logger.error(f"Failed to get element info for {selector}: {e}")
            return {"exists": False, "error": str(e)}

    @staticmethod
    async def reliable_fill_async(
        page: Page,
        selector: str,
        value: str,
        method: str = "auto",
        capture_on_failure: bool = True,
    ) -> bool:
        """Perform reliable form fill with multiple methods.

        Args:
            page: Browser page
            selector: CSS selector for input element
            value: Value to set
            method: Fill method ('auto', 'playwright', 'type', 'js')
            capture_on_failure: Whether to capture debug info on failure

        Returns:
            True if fill successful, False otherwise
        """
        if method == "auto":
            methods_order = ["playwright", "type", "js"]
        else:
            methods_order = [method]

        methods = {
            "playwright": BrowserUtils._fill_with_playwright,
            "type": BrowserUtils._fill_with_typing,
            "js": BrowserUtils._fill_with_js,
        }

        for method_name in methods_order:
            if method_name in methods:
                success = await methods[method_name](page, selector, value)
                if success:
                    logger.debug(
                        f"Fill successful with {method_name}: {selector}"
                    )
                    return True
                else:
                    logger.debug(f"Fill failed with {method_name}: {selector}")

        logger.error(f"All fill methods failed for {selector}")

        if capture_on_failure:
            debug_info = await BrowserUtils.capture_debug_info(
                page,
                f"fill_failed_{selector.replace('[', '_').replace(']', '_')}",
            )
            logger.error(f"Debug files: {debug_info}")

            element_info = await BrowserUtils.debug_element_info(
                page, selector
            )
            logger.error(f"Element info: {element_info}")

        return False

    @staticmethod
    async def _fill_with_playwright(
        page: Page, selector: str, value: str
    ) -> bool:
        """Fill using Playwright's fill method."""
        try:
            await page.fill(selector, value, timeout=5000)
            logger.debug(f"Playwright fill successful: {selector}")
            return True
        except Exception as e:
            logger.debug(f"Playwright fill failed for {selector}: {e}")
            return False

    @staticmethod
    async def _fill_with_typing(page: Page, selector: str, value: str) -> bool:
        """Fill using Playwright's type method."""
        try:
            await page.click(selector, timeout=5000)
            await page.keyboard.press("Control+a")
            await page.type(selector, value, delay=50)
            logger.debug(f"Type fill successful: {selector}")
            return True
        except Exception as e:
            logger.debug(f"Type fill failed for {selector}: {e}")
            return False

    @staticmethod
    async def _fill_with_js(page: Page, selector: str, value: str) -> bool:
        """Fill using JavaScript evaluation."""
        try:
            result = await page.evaluate(
                """(selector, value) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    return 'success';
                }
                return 'element not found';
            }""",
                selector,
                value,
            )

            if result == "success":
                logger.debug(f"JS fill successful: {selector}")
                return True
            return False
        except Exception as e:
            logger.debug(f"JS fill failed for {selector}: {e}")
            return False

    @staticmethod
    async def reliable_click_async(
        page: Page,
        selector: str,
        method: str = "auto",
        capture_on_failure: bool = True,
    ) -> bool:
        """Perform reliable click with multiple methods.

        Args:
            page: Browser page
            selector: CSS selector for element to click
            method: Click method ('auto', 'playwright', 'force', 'js')
            capture_on_failure: Whether to capture debug info on failure

        Returns:
            True if click successful, False otherwise
        """
        if method == "auto":
            methods_order = ["playwright", "force", "js"]
        else:
            methods_order = [method]

        methods = {
            "playwright": BrowserUtils._click_with_playwright,
            "force": BrowserUtils._click_with_force,
            "js": BrowserUtils._click_with_js,
        }

        for method_name in methods_order:
            if method_name in methods:
                success = await methods[method_name](page, selector)
                if success:
                    logger.debug(
                        f"Click successful with {method_name}: {selector}"
                    )
                    return True
                else:
                    logger.debug(
                        f"Click failed with {method_name}: {selector}"
                    )

        logger.error(f"All click methods failed for {selector}")

        if capture_on_failure:
            debug_info = await BrowserUtils.capture_debug_info(
                page,
                f"click_failed_{selector.replace('[', '_').replace(']', '_')}",
            )
            logger.error(f"Debug files: {debug_info}")

            element_info = await BrowserUtils.debug_element_info(
                page, selector
            )
            logger.error(f"Element info: {element_info}")

        return False

    @staticmethod
    async def _click_with_playwright(page: Page, selector: str) -> bool:
        """Click using Playwright's click method."""
        try:
            await page.click(selector, timeout=5000)
            logger.debug(f"Playwright click successful: {selector}")
            return True
        except Exception as e:
            logger.debug(f"Playwright click failed for {selector}: {e}")
            return False

    @staticmethod
    async def _click_with_force(page: Page, selector: str) -> bool:
        """Click using Playwright's force click."""
        try:
            await page.click(selector, force=True, timeout=5000)
            logger.debug(f"Force click successful: {selector}")
            return True
        except Exception as e:
            logger.debug(f"Force click failed for {selector}: {e}")
            return False

    @staticmethod
    async def _click_with_js(page: Page, selector: str) -> bool:
        """Click using JavaScript evaluation."""
        try:
            result = await page.evaluate(
                """(selector) => {
                const element = document.querySelector(selector);
                if (element) {
                    element.click();
                    return 'success';
                }
                return 'element not found';
            }""",
                selector,
            )

            if result == "success":
                logger.debug(f"JS click successful: {selector}")
                return True
            return False
        except Exception as e:
            logger.debug(f"JS click failed for {selector}: {e}")
            return False

    @staticmethod
    async def wait_for_element_async(
        page: Page, selector: str, timeout: int = 5000, state: str = "visible"
    ) -> bool:
        """Wait for element to appear with different states.

        Args:
            page: Browser page
            selector: CSS selector for element
            timeout: Timeout in milliseconds
            state: Element state ('visible', 'attached', 'detached', 'hidden')

        Returns:
            True if element appeared, False if timeout
        """
        try:
            await page.wait_for_selector(
                selector, timeout=timeout, state=state
            )
            return True
        except TimeoutError:
            logger.debug(f"Element not found within timeout: {selector}")
            return False

    @staticmethod
    async def find_first_element_async(
        page: Page, selectors: List[str], timeout: int = 5000
    ) -> Optional[str]:
        """Find first available element from a list of selectors.

        Args:
            page: Browser page
            selectors: List of CSS selectors
            timeout: Timeout in milliseconds

        Returns:
            First matching selector or None if timeout
        """
        for selector in selectors:
            if await BrowserUtils.wait_for_element_async(
                page, selector, timeout=timeout
            ):
                return selector
        return None

    @staticmethod
    async def perform_login_sequence_async(
        page: Page, login_steps: List[Dict[str, Any]]
    ) -> bool:
        """Perform a sequence of login steps.

        Args:
            page: Browser page
            login_steps: List of step dictionaries with 'action', 'selector', 'value'

        Returns:
            True if all steps successful, False otherwise
        """
        for step_idx, step in enumerate(login_steps):
            action = step.get("action")
            selector = step.get("selector")
            value = step.get("value", "")
            timeout = step.get("timeout", 5000)

            logger.debug(f"Step {step_idx + 1}: {action} on {selector}")

            if action == "wait":
                if not await BrowserUtils.wait_for_element_async(
                    page, selector, timeout
                ):
                    logger.error(f"Wait step failed: {selector}")
                    return False

            elif action == "fill":
                if not await BrowserUtils.wait_for_element_async(
                    page, selector, timeout
                ):
                    logger.error(f"Element not found for fill: {selector}")
                    return False
                if not await BrowserUtils.reliable_fill_async(
                    page, selector, value
                ):
                    logger.error(f"Fill step failed: {selector}")
                    return False

            elif action == "click":
                if not await BrowserUtils.wait_for_element_async(
                    page, selector, timeout
                ):
                    logger.error(f"Element not found for click: {selector}")
                    return False
                if not await BrowserUtils.reliable_click_async(page, selector):
                    logger.error(f"Click step failed: {selector}")
                    return False

            elif action == "navigate":
                try:
                    await page.goto(value, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_load_state("networkidle")
                except Exception as e:
                    logger.error(f"Navigation failed: {e}")
                    return False

            delay = step.get("delay", 0)
            if delay > 0:
                await asyncio.sleep(delay / 1000)

        return True


async def main():
    """Demonstrate BrowserUtils functionality."""
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()

        print("=== GitHub Login Sequence ===")
        await page.goto("https://github.com/login", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        login_exists = await BrowserUtils.wait_for_element_async(
            page, "input[name='login']", timeout=5000
        )
        print(f"Login form found: {login_exists}")

        if login_exists:
            fill_success = await BrowserUtils.reliable_fill_async(
                page, "input[name='login']", "demo@example.com"
            )
            print(f"Username fill success: {fill_success}")
            await asyncio.sleep(2)

            pass_success = await BrowserUtils.reliable_fill_async(
                page, "input[name='password']", "demopass"
            )
            print(f"Password fill success: {pass_success}")
            await asyncio.sleep(3)

        print("\n=== Google Search Demo ===")
        await page.goto("https://google.com", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        search_selectors = [
            "input[name='q']",
            "textarea[name='q']",
            "[role='combobox']",
        ]

        found_selector = await BrowserUtils.find_first_element_async(
            page, search_selectors, timeout=5000
        )
        print(f"Found search element: {found_selector}")

        if found_selector:
            fill_success = await BrowserUtils.reliable_fill_async(
                page, found_selector, "playwright automation demo"
            )
            print(f"Search fill success: {fill_success}")
            await asyncio.sleep(2)

            print("\n=== Fill Method Comparison ===")
            methods = ["playwright", "type", "js"]
            for method in methods:
                success = await BrowserUtils.reliable_fill_async(
                    page, found_selector, f"test with {method}", method=method
                )
                print(f"{method} method success: {success}")
                await asyncio.sleep(1)

        print("\nDemo completed. Browser will close in 5 seconds...")
        await asyncio.sleep(5)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())


# python -m scitex.scholar.browser.BrowserUtils

# EOF
