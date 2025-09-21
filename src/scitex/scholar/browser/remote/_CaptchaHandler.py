#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-31 17:45:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/remote/_CaptchaHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/scholar/browser/remote/_CaptchaHandler.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Captcha handler for browser automation using 2Captcha service."""

import asyncio
import time
from typing import Optional, Dict, Any, Union
from playwright.async_api import Page, Frame
import aiohttp
import json

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class CaptchaHandler:
    """Handles CAPTCHA solving using 2Captcha service."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with 2Captcha API key."""
        self.api_key = api_key or os.getenv("SCITEX_SCHOLAR_2CAPTCHA_API_KEY")
        if not self.api_key:
            logger.warn("2Captcha API key not configured - CAPTCHA solving disabled")
        
        self.base_url = "http://2captcha.com"
        self.timeout = 180  # 3 minutes max wait time
        
    async def handle_page_async(self, page: Page) -> bool:
        """Check and handle captcha on the current page.
        
        Returns:
            bool: True if captcha was found and solved, False otherwise
        """
        if not self.api_key:
            return False
            
        # Check for common captcha indicators
        captcha_found = await self._detect_captcha_async(page)
        if not captcha_found:
            return False
            
        logger.debug("Captcha detected on page - attempting to solve")
        
        # Determine captcha type and solve
        if await self._is_cloudflare_challenge_async(page):
            return await self._solve_cloudflare_challenge_async(page)
        elif await self._has_recaptcha_async(page):
            return await self._solve_recaptcha_async(page)
        elif await self._has_hcaptcha_async(page):
            return await self._solve_hcaptcha_async(page)
        else:
            logger.warn("Unknown captcha type detected")
            return False
    
    async def _detect_captcha_async(self, page: Page) -> bool:
        """Detect if page has a captcha."""
        # Check for common captcha elements
        selectors = [
            # Cloudflare
            "iframe[title*='Cloudflare']",
            "#cf-challenge-running",
            ".cf-challenge",
            "div:has-text('Verifying you are human')",
            "div:has-text('Checking your browser')",
            # reCAPTCHA
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#g-recaptcha",
            # hCaptcha
            "iframe[src*='hcaptcha']",
            ".h-captcha",
            # Generic
            "div:has-text('I am not a robot')",
            "div:has-text('Verify you are human')",
            "div:has-text('Security check')"
        ]
        
        for selector in selectors:
            try:
                if await page.locator(selector).first.is_visible():
                    return True
            except:
                continue
                
        return False
    
    async def _is_cloudflare_challenge_async(self, page: Page) -> bool:
        """Check if this is a Cloudflare challenge."""
        try:
            # Check for Cloudflare-specific elements
            cf_indicators = [
                "iframe[title*='Cloudflare']",
                "#cf-challenge-running", 
                ".cf-challenge",
                "div:has-text('Verifying you are human')",
                "div:has-text('Checking your browser')"
            ]
            
            for indicator in cf_indicators:
                if await page.locator(indicator).first.is_visible():
                    return True
                    
            # Check page title
            title = await page.title()
            if "Just a moment" in title or "Attention Required" in title:
                return True
                
            return False
        except:
            return False
    
    async def _solve_cloudflare_challenge_async(self, page: Page) -> bool:
        """Handle Cloudflare challenge/turnstile."""
        logger.debug("Handling Cloudflare challenge")
        
        try:
            # First, wait a bit to see if it auto-solves
            logger.debug("Waiting for Cloudflare auto-solve...")
            await asyncio.sleep(5)
            
            # Check if still on challenge page
            if not await self._is_cloudflare_challenge_async(page):
                logger.debug("Cloudflare challenge auto-solved")
                return True
            
            # If Turnstile captcha is present, solve it
            turnstile_frame = page.frame_locator("iframe[title*='Cloudflare']").first
            if turnstile_frame:
                logger.debug("Cloudflare Turnstile detected - solving with 2Captcha")
                
                # Get site key
                site_key = await self._extract_turnstile_key_async(page)
                if not site_key:
                    logger.error("Could not extract Turnstile site key")
                    return False
                
                # Submit to 2Captcha
                task_id = await self._submit_turnstile_async(page.url, site_key)
                if not task_id:
                    return False
                
                # Get solution
                solution = await self._get_captcha_result_async(task_id)
                if not solution:
                    return False
                
                # Inject solution
                await page.evaluate(f"""
                    window.turnstile.render.solutions = window.turnstile.render.solutions || [];
                    window.turnstile.render.solutions.push('{solution}');
                """)
                
                # Click verify if needed
                verify_btn = page.locator("input[type='submit'][value*='Verify']")
                if await verify_btn.is_visible():
                    await verify_btn.click()
                
                # Wait for navigation
                await page.wait_for_load_state("networkidle", timeout=30000)
                
                return not await self._is_cloudflare_challenge_async(page)
            
            # For other Cloudflare challenges, just wait
            logger.debug("Waiting for Cloudflare challenge to complete...")
            await page.wait_for_function(
                "!document.querySelector('#cf-challenge-running')",
                timeout=30000
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to solve Cloudflare challenge: {e}")
            return False
    
    async def _has_recaptcha_async(self, page: Page) -> bool:
        """Check if page has reCAPTCHA."""
        try:
            return await page.locator("iframe[src*='recaptcha']").first.is_visible()
        except:
            return False
    
    async def _solve_recaptcha_async(self, page: Page) -> bool:
        """Solve reCAPTCHA v2."""
        logger.debug("Solving reCAPTCHA")
        
        try:
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const elem = document.querySelector('[data-sitekey]');
                    return elem ? elem.getAttribute('data-sitekey') : null;
                }
            """)
            
            if not site_key:
                logger.error("Could not find reCAPTCHA site key")
                return False
            
            # Submit to 2Captcha
            task_id = await self._submit_recaptcha_async(page.url, site_key)
            if not task_id:
                return False
            
            # Get solution
            solution = await self._get_captcha_result_async(task_id)
            if not solution:
                return False
            
            # Inject solution
            await page.evaluate(f"""
                document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                if (typeof ___grecaptcha_cfg !== 'undefined') {{
                    Object.entries(___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                        if (client.callback) {{
                            client.callback('{solution}');
                        }}
                    }});
                }}
            """)
            
            # Submit form if present
            submit_btn = page.locator("button[type='submit'], input[type='submit']").first
            if await submit_btn.is_visible():
                await submit_btn.click()
                await page.wait_for_load_state("networkidle", timeout=10000)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to solve reCAPTCHA: {e}")
            return False
    
    async def _has_hcaptcha_async(self, page: Page) -> bool:
        """Check if page has hCaptcha."""
        try:
            return await page.locator("iframe[src*='hcaptcha']").first.is_visible()
        except:
            return False
    
    async def _solve_hcaptcha_async(self, page: Page) -> bool:
        """Solve hCaptcha."""
        logger.debug("Solving hCaptcha")
        
        try:
            # Get site key
            site_key = await page.evaluate("""
                () => {
                    const elem = document.querySelector('[data-sitekey]');
                    return elem ? elem.getAttribute('data-sitekey') : null;
                }
            """)
            
            if not site_key:
                logger.error("Could not find hCaptcha site key")
                return False
            
            # Submit to 2Captcha
            task_id = await self._submit_hcaptcha_async(page.url, site_key)
            if not task_id:
                return False
            
            # Get solution
            solution = await self._get_captcha_result_async(task_id)
            if not solution:
                return False
            
            # Inject solution
            await page.evaluate(f"""
                document.querySelector('[name="h-captcha-response"]').value = '{solution}';
                document.querySelector('[name="g-recaptcha-response"]').value = '{solution}';
                if (window.hcaptcha) {{
                    window.hcaptcha.execute();
                }}
            """)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to solve hCaptcha: {e}")
            return False
    
    async def _extract_turnstile_key_async(self, page: Page) -> Optional[str]:
        """Extract Cloudflare Turnstile site key."""
        try:
            # Try different methods to get the key
            site_key = await page.evaluate("""
                () => {
                    // Method 1: Check data attributes
                    const elem = document.querySelector('[data-sitekey]');
                    if (elem) return elem.getAttribute('data-sitekey');
                    
                    // Method 2: Check Turnstile config
                    if (window.turnstile?.config?.sitekey) {
                        return window.turnstile.config.sitekey;
                    }
                    
                    // Method 3: Parse from script
                    const scripts = Array.from(document.scripts);
                    for (const script of scripts) {
                        const match = script.textContent.match(/sitekey['"]\s*:\s*['"]([^'"]+)/);
                        if (match) return match[1];
                    }
                    
                    return null;
                }
            """)
            
            return site_key
            
        except Exception as e:
            logger.error(f"Failed to extract Turnstile key: {e}")
            return None
    
    async def _submit_recaptcha_async(self, page_url: str, site_key: str) -> Optional[str]:
        """Submit reCAPTCHA to 2Captcha."""
        return await self._submit_captcha_async({
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": page_url,
            "json": 1
        })
    
    async def _submit_hcaptcha_async(self, page_url: str, site_key: str) -> Optional[str]:
        """Submit hCaptcha to 2Captcha."""
        return await self._submit_captcha_async({
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": page_url,
            "json": 1
        })
    
    async def _submit_turnstile_async(self, page_url: str, site_key: str) -> Optional[str]:
        """Submit Turnstile to 2Captcha."""
        return await self._submit_captcha_async({
            "key": self.api_key,
            "method": "turnstile",
            "sitekey": site_key,
            "pageurl": page_url,
            "json": 1
        })
    
    async def _submit_captcha_async(self, params: Dict[str, Any]) -> Optional[str]:
        """Submit captcha to 2Captcha and get task ID."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/in.php",
                    data=params
                ) as response:
                    result = await response.json()
                    
                    if result.get("status") == 1:
                        task_id = result.get("request")
                        logger.debug(f"Captcha submitted, task ID: {task_id}")
                        return task_id
                    else:
                        logger.error(f"2Captcha submission failed: {result}")
                        return None
                        
        except Exception as e:
            logger.error(f"Failed to submit captcha: {e}")
            return None
    
    async def _get_captcha_result_async(self, task_id: str) -> Optional[str]:
        """Poll 2Captcha for result."""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/res.php",
                        params={
                            "key": self.api_key,
                            "action": "get",
                            "id": task_id,
                            "json": 1
                        }
                    ) as response:
                        result = await response.json()
                        
                        if result.get("status") == 1:
                            solution = result.get("request")
                            logger.debug("Captcha solved successfully")
                            return solution
                        elif result.get("request") == "CAPCHA_NOT_READY":
                            logger.debug("Captcha not ready yet, waiting...")
                            await asyncio.sleep(5)
                        else:
                            logger.error(f"2Captcha error: {result}")
                            return None
                            
            except Exception as e:
                logger.error(f"Failed to get captcha result: {e}")
                await asyncio.sleep(5)
        
        logger.error("Captcha solving timeout")
        return None