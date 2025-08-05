#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-31 23:30:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/remote/_ZenRowsAPIBrowser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = "./src/scitex/scholar/browser/remote/_ZenRowsAPIBrowser.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
ZenRows API-based browser for reliable page rendering and screenshot capture.
This uses the ZenRows API directly instead of WebSocket for better reliability.
"""

import json
import base64
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiohttp

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class ZenRowsAPIBrowser:
    """Browser-like interface using ZenRows API for page rendering.
    
    This provides a simpler, more reliable alternative to WebSocket-based
    browser connections. It's especially good for:
    - Taking screenshots
    - Handling CAPTCHAs automatically
    - Getting rendered HTML content
    - Bypassing anti-bot measures
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        proxy_country: str = "au",
        enable_antibot: bool = True,
        premium_proxy: bool = True
    ):
        """Initialize ZenRows API browser.
        
        Args:
            api_key: ZenRows API key (or from env)
            proxy_country: Country code for proxy
            enable_antibot: Enable anti-bot bypass features
            premium_proxy: Use premium residential proxies
        """
        self.api_key = api_key or os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ZenRows API key required. Set SCITEX_SCHOLAR_ZENROWS_API_KEY"
            )
        
        self.proxy_country = proxy_country
        self.enable_antibot = enable_antibot
        self.premium_proxy = premium_proxy
        self.base_url = "https://api.zenrows.com/v1/"
        
    async def navigate_and_screenshot_async(
        self,
        url: str,
        screenshot_path: Optional[str] = None,
        wait_ms: int = 5000,
        js_instructions: Optional[List[Dict]] = None,
        return_html: bool = False
    ) -> Dict[str, Any]:
        """Navigate to URL and optionally take screenshot.
        
        Args:
            url: Target URL
            screenshot_path: Path to save screenshot (None to skip)
            wait_ms: Additional wait time in milliseconds
            js_instructions: Custom JavaScript instructions
            return_html: Whether to return rendered HTML
            
        Returns:
            Dict with results including screenshot info and HTML
        """
        # Default JS instructions for reliable rendering
        if js_instructions is None:
            js_instructions = [
                {"wait": 3000},  # Initial wait
                {"wait_event": "networkidle"},  # Wait for network
                {"scroll_y": 300},  # Trigger lazy loading
                {"wait": 2000},  # Final wait
            ]
        
        # Build parameters
        params = {
            "url": url,
            "apikey": self.api_key,
            "js_render": "true",
            "js_instructions": json.dumps(js_instructions),
            "wait": str(wait_ms),
        }
        
        # Add optional features
        if self.enable_antibot:
            params["antibot"] = "true"
        
        if self.premium_proxy:
            params["premium_proxy"] = "true"
            
        if self.proxy_country:
            params["proxy_country"] = self.proxy_country
            
        if screenshot_path:
            params["screenshot"] = "true"
            
        if return_html or screenshot_path:
            params["json_response"] = "true"
        
        logger.info(f"Navigating to: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=60)
                
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=timeout
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ZenRows error {response.status}: {error_text[:200]}")
                        return {
                            "success": False,
                            "error": f"API error {response.status}",
                            "url": url
                        }
                    
                    # Handle response based on content type
                    content_type = response.headers.get("content-type", "")
                    
                    if "json" in content_type:
                        # JSON response with detailed data
                        data = await response.json()
                        result = {
                            "success": True,
                            "url": url,
                            "html": data.get("html", "") if return_html else None,
                            "html_length": len(data.get("html", "")),
                        }
                        
                        # Handle screenshot
                        if screenshot_path and data.get("screenshot"):
                            screenshot_data = data["screenshot"]
                            if screenshot_data.get("data"):
                                image_bytes = base64.b64decode(screenshot_data["data"])
                                
                                Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                                with open(screenshot_path, "wb") as f:
                                    f.write(image_bytes)
                                
                                result["screenshot"] = {
                                    "saved": True,
                                    "path": screenshot_path,
                                    "width": screenshot_data.get("width"),
                                    "height": screenshot_data.get("height")
                                }
                                logger.success(f"Screenshot saved: {screenshot_path}")
                        
                        # Check JS execution report
                        if data.get("js_instructions_report"):
                            report = data["js_instructions_report"]
                            result["js_report"] = {
                                "executed": report.get("instructions_executed", 0),
                                "succeeded": report.get("instructions_succeeded", 0),
                                "failed": report.get("instructions_failed", 0)
                            }
                            
                            # Check for CAPTCHA solving
                            for inst in report.get("instructions", []):
                                if inst.get("instruction") == "solve_captcha" and inst.get("success"):
                                    result["captcha_solved"] = True
                                    logger.info(f"CAPTCHA solved: {inst['params']['type']}")
                        
                        return result
                        
                    else:
                        # Direct response (image or HTML)
                        content = await response.read()
                        
                        if screenshot_path and len(content) > 1000:
                            # Save as image
                            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                            with open(screenshot_path, "wb") as f:
                                f.write(content)
                            
                            logger.success(f"Screenshot saved: {screenshot_path}")
                            return {
                                "success": True,
                                "url": url,
                                "screenshot": {
                                    "saved": True,
                                    "path": screenshot_path,
                                    "size_bytes": len(content)
                                }
                            }
                        elif return_html:
                            # Return as HTML
                            html = content.decode('utf-8', errors='ignore')
                            return {
                                "success": True,
                                "url": url,
                                "html": html,
                                "html_length": len(html)
                            }
                        
                        return {"success": True, "url": url}
                        
        except asyncio.TimeoutError:
            logger.error("Request timed out - page may require manual intervention")
            return {
                "success": False,
                "error": "Timeout",
                "url": url
            }
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def get_pdf_url_async(self, doi: str, use_openurl: bool = True) -> Optional[str]:
        """Try to get PDF URL for a DOI.
        
        Args:
            doi: DOI to resolve
            use_openurl: Whether to try OpenURL resolver first
            
        Returns:
            PDF URL if found, None otherwise
        """
        urls_to_try = []
        
        # Try OpenURL first if requested
        if use_openurl:
            openurl_base = os.getenv(
                "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
                "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
            )
            openurl = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
            urls_to_try.append(openurl)
        
        # Direct DOI
        urls_to_try.append(f"https://doi.org/{doi}")
        
        for url in urls_to_try:
            result = await self.navigate_and_screenshot_async(
                url,
                return_html=True,
                wait_ms=8000  # Longer wait for redirects
            )
            
            if result.get("success") and result.get("html"):
                html = result["html"]
                
                # Simple PDF URL extraction
                import re
                pdf_patterns = [
                    r'href="([^"]+\.pdf[^"]*)"',
                    r'content="([^"]+\.pdf[^"]*)"',
                    r'url["\']?\s*:\s*["\']([^"\']+\.pdf[^"\']*)',
                ]
                
                for pattern in pdf_patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        pdf_url = match.group(1)
                        logger.info(f"Found PDF URL: {pdf_url}")
                        return pdf_url
        
        return None
    
    async def batch_screenshot_async(
        self,
        urls: List[str],
        output_dir: str,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Take screenshots of multiple URLs concurrently.
        
        Args:
            urls: List of URLs to screenshot
            output_dir: Directory to save screenshots
            max_concurrent: Max concurrent requests
            
        Returns:
            List of results for each URL
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        async def process_url_async(url: str, index: int) -> Dict[str, Any]:
            """Process single URL."""
            filename = f"screenshot_{index:03d}.png"
            filepath = os.path.join(output_dir, filename)
            
            result = await self.navigate_and_screenshot_async(url, filepath)
            result["index"] = index
            return result
        
        # Process with limited concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit_async(url: str, index: int):
            async with semaphore:
                return await process_url_async(url, index)
        
        tasks = [
            process_with_limit_async(url, i) 
            for i, url in enumerate(urls)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    "success": False,
                    "error": str(result),
                    "url": urls[i],
                    "index": i
                })
            else:
                final_results.append(result)
        
        # Summary
        successful = sum(1 for r in final_results if r.get("success"))
        logger.info(f"Screenshots: {successful}/{len(urls)} successful")
        
        return final_results