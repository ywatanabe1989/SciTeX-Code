#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 12:05:00"
# Author: Yusuke Watanabe
# File: _screenshot_capturer.py

"""
Screenshot capture utilities for debugging PDF download failures.

This module provides functionality to capture screenshots during failed PDF downloads
to help diagnose authentication issues, page structure changes, or other problems.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
import asyncio
import logging

try:
    from playwright.async_api import Page, Browser, Error as PlaywrightError
except ImportError:
    # Playwright is optional for screenshot functionality
    Page = Any
    Browser = Any
    PlaywrightError = Exception

logger = logging.getLogger(__name__)


class ScreenshotCapturer:
    """Captures screenshots for debugging download failures."""
    
    def __init__(self, screenshot_dir: Optional[Path] = None):
        """
        Initialize screenshot capturer.
        
        Args:
            screenshot_dir: Directory to save screenshots. 
                          Defaults to ~/.scitex/scholar/debug_screenshots
        """
        if screenshot_dir is None:
            from ._scholar_paths import scholar_paths
            screenshot_dir = scholar_paths.get_screenshots_dir() / "debug"
        
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
    async def capture_on_failure(
        self,
        page: Page,
        error_info: Dict[str, Any],
        identifier: str = "unknown"
    ) -> Optional[Path]:
        """
        Capture screenshot when a download fails.
        
        Args:
            page: Playwright page instance
            error_info: Dictionary containing error details
            identifier: Paper identifier (DOI, PMID, etc.)
            
        Returns:
            Path to saved screenshot or None if capture fails
        """
        try:
            # Generate filename with timestamp and identifier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_id = identifier.replace("/", "_").replace(":", "_")[:50]
            filename = f"failure_{timestamp}_{safe_id}.png"
            filepath = self.screenshot_dir / filename
            
            # Capture full page screenshot
            await page.screenshot(
                path=str(filepath),
                full_page=True,
                timeout=10000  # 10 second timeout
            )
            
            # Also save page info
            info_file = filepath.with_suffix(".txt")
            await self._save_page_info(page, error_info, info_file)
            
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    async def _save_page_info(
        self,
        page: Page,
        error_info: Dict[str, Any],
        filepath: Path
    ) -> None:
        """Save page information alongside screenshot."""
        try:
            info = {
                "timestamp": datetime.now().isoformat(),
                "url": page.url,
                "title": await page.title(),
                "error": error_info,
                "viewport": page.viewport_size,
            }
            
            # Try to get page content type
            try:
                content_type = await page.evaluate(
                    "() => document.contentType"
                )
                info["content_type"] = content_type
            except:
                pass
            
            # Save to text file
            with open(filepath, "w") as f:
                f.write("=== Page Debug Information ===\n\n")
                for key, value in info.items():
                    f.write(f"{key}: {value}\n")
                    
        except Exception as e:
            logger.error(f"Failed to save page info: {e}")
    
    async def capture_workflow(
        self,
        page: Page,
        stage: str,
        identifier: str = "unknown",
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Optional[Path]:
        """
        Capture screenshot at a specific workflow stage.
        
        Args:
            page: Playwright page instance
            stage: Workflow stage (e.g., "pre_auth", "post_login", "resolver_page")
            identifier: Paper identifier
            additional_info: Extra information to save
            
        Returns:
            Path to saved screenshot
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_id = identifier.replace("/", "_").replace(":", "_")[:50]
            filename = f"{stage}_{timestamp}_{safe_id}.png"
            filepath = self.screenshot_dir / filename
            
            await page.screenshot(
                path=str(filepath),
                full_page=True,
                timeout=10000
            )
            
            # Save stage info
            if additional_info:
                info_file = filepath.with_suffix(".txt")
                with open(info_file, "w") as f:
                    f.write(f"=== {stage} Stage Information ===\n\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"URL: {page.url}\n")
                    for key, value in additional_info.items():
                        f.write(f"{key}: {value}\n")
            
            logger.debug(f"Workflow screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture workflow screenshot: {e}")
            return None
    
    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        Remove screenshots older than specified days.
        
        Args:
            days: Number of days to keep screenshots
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file in self.screenshot_dir.glob("*.png"):
            if file.stat().st_mtime < cutoff:
                try:
                    file.unlink()
                    # Also remove associated txt file if exists
                    txt_file = file.with_suffix(".txt")
                    if txt_file.exists():
                        txt_file.unlink()
                    deleted += 1
                except Exception as e:
                    logger.error(f"Failed to delete {file}: {e}")
                    
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old screenshots")
            
        return deleted
    
    async def capture_comparison(
        self,
        page: Page,
        expected_element: str,
        identifier: str = "unknown"
    ) -> Optional[Path]:
        """
        Capture screenshot with element highlighting for comparison.
        
        Args:
            page: Playwright page instance
            expected_element: CSS selector of expected element
            identifier: Paper identifier
            
        Returns:
            Path to screenshot with highlighting
        """
        try:
            # Inject CSS to highlight expected element
            await page.add_style_tag(content=f"""
                {expected_element} {{
                    outline: 3px solid red !important;
                    outline-offset: 2px !important;
                }}
            """)
            
            # Add annotation
            await page.evaluate(f"""
                (() => {{
                    const div = document.createElement('div');
                    div.style.cssText = 'position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;z-index:9999;font-family:monospace;';
                    div.textContent = 'Expected element: {expected_element}';
                    document.body.appendChild(div);
                }})()
            """)
            
            # Capture screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_id = identifier.replace("/", "_").replace(":", "_")[:50]
            filename = f"comparison_{timestamp}_{safe_id}.png"
            filepath = self.screenshot_dir / filename
            
            await page.screenshot(
                path=str(filepath),
                full_page=True,
                timeout=10000
            )
            
            logger.info(f"Comparison screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture comparison screenshot: {e}")
            return None