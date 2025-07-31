#!/usr/bin/env python3
"""
Simple fix for taking screenshots with ZenRows browser after CAPTCHA/verification pages.
This example shows how to properly wait for content before taking screenshots.
"""

import os
import asyncio
from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

logger = logging.getLogger(__name__)


async def take_screenshot_with_retry(page, filepath, max_attempts=3):
    """Take screenshot with retry logic for handling navigation issues."""
    
    for attempt in range(max_attempts):
        try:
            # Wait for any ongoing navigation
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check if we're on a verification page
            try:
                body_text = await page.text_content("body", timeout=2000) or ""
                if "Verifying you are human" in body_text or "Just a moment" in body_text:
                    logger.info(f"Verification page detected, waiting... (attempt {attempt + 1})")
                    await page.wait_for_timeout(5000)
                    continue
            except:
                pass
            
            # Take screenshot
            await page.screenshot(path=filepath, full_page=True)
            logger.success(f"Screenshot saved: {filepath}")
            return True
            
        except Exception as e:
            logger.warning(f"Screenshot attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                await page.wait_for_timeout(2000)
    
    return False


async def main():
    """Simple example to fix screenshot issues."""
    
    # Initialize with authentication
    auth_manager = AuthenticationManager()
    await auth_manager.authenticate()
    
    # Create browser manager
    browser_manager = ZenRowsRemoteBrowserManager(auth_manager=auth_manager)
    
    try:
        # Get authenticated context
        browser, context = await browser_manager.get_authenticated_context()
        page = await context.new_page()
        
        # Test URL that was having issues
        test_url = "https://doi.org/10.1016/j.neuron.2018.01.048"
        
        logger.info(f"Navigating to: {test_url}")
        
        # Navigate with proper error handling
        try:
            await page.goto(test_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.warning(f"Navigation warning (may be normal): {e}")
        
        # Wait for verification to complete if needed
        logger.info("Waiting for page to stabilize...")
        
        # Multiple strategies to ensure content loads
        try:
            # Strategy 1: Wait for specific content that indicates page loaded
            await page.wait_for_selector(
                'body:not(:has-text("Verifying you are human"))',
                timeout=20000
            )
        except:
            # Strategy 2: Just wait a fixed time
            logger.info("Using timeout strategy...")
            await page.wait_for_timeout(10000)
        
        # Now take screenshot with retry
        os.makedirs("screenshots_zenrows", exist_ok=True)
        screenshot_path = "screenshots_zenrows/fixed_screenshot.png"
        
        success = await take_screenshot_with_retry(page, screenshot_path)
        
        if success:
            # Also log some page info
            title = await page.title()
            url = page.url
            logger.info(f"Page title: {title}")
            logger.info(f"Final URL: {url}")
            
            # Check if we reached content
            try:
                content = await page.text_content("body") or ""
                if len(content) > 1000:
                    logger.success("Page has substantial content")
                else:
                    logger.warning(f"Page may still be loading (only {len(content)} chars)")
            except:
                pass
        
        await page.close()
        
    finally:
        await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
    print("\nCheck screenshots_zenrows/fixed_screenshot.png")