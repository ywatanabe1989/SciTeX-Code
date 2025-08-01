#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 12:10:00"
# Author: Yusuke Watanabe
# File: _DownloadWorkflowEnhanced.py

"""
Enhanced download workflow with integrated screenshot capture.

This module demonstrates how to integrate screenshot capture into the PDF download
workflow for better debugging and troubleshooting.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from ..utils import RetryHandler, ErrorDiagnostics, ScreenshotCapturer
from ..validation import PreflightChecker

logger = logging.getLogger(__name__)


class EnhancedDownloadWorkflow:
    """PDF download workflow with screenshot capture on failure."""
    
    def __init__(
        self,
        download_dir: Optional[Path] = None,
        screenshot_dir: Optional[Path] = None,
        enable_screenshots: bool = True
    ):
        """
        Initialize enhanced download workflow.
        
        Args:
            download_dir: Directory for PDFs
            screenshot_dir: Directory for debug screenshots
            enable_screenshots: Whether to capture screenshots on failure
        """
        self.download_dir = Path(download_dir or Path.home() / ".scitex" / "scholar" / "pdfs")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_screenshots = enable_screenshots
        self.screenshot_capturer = ScreenshotCapturer(screenshot_dir) if enable_screenshots else None
        self.preflight_checker = PreflightChecker()
        self.error_diagnostics = ErrorDiagnostics()
        self.retry_handler = RetryHandler()
        
    async def download_with_diagnostics(
        self,
        doi: str,
        browser_context: Any,
        auth_cookies: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Download PDF with comprehensive diagnostics and screenshots.
        
        Args:
            doi: DOI to download
            browser_context: Playwright browser context
            auth_cookies: Authentication cookies if available
            
        Returns:
            Dict with download result and diagnostic information
        """
        result = {
            "doi": doi,
            "success": False,
            "pdf_path": None,
            "error": None,
            "screenshots": [],
            "diagnostics": {},
            "retry_count": 0
        }
        
        # Run pre-flight checks
        preflight = await self.preflight_checker.run_all_checks(
            download_dir=self.download_dir
        )
        
        if not all(preflight.values()):
            result["error"] = "Pre-flight checks failed"
            result["diagnostics"]["preflight"] = preflight
            return result
        
        # Create new page for download attempt
        page = await browser_context.new_page()
        
        try:
            # Set auth cookies if available
            if auth_cookies:
                await page.context.add_cookies(auth_cookies)
            
            # Capture pre-download screenshot if enabled
            if self.enable_screenshots:
                pre_screenshot = await self.screenshot_capturer.capture_workflow(
                    page,
                    "pre_download",
                    doi,
                    {"status": "Starting download attempt"}
                )
                if pre_screenshot:
                    result["screenshots"].append(str(pre_screenshot))
            
            # Attempt download with retry logic
            async def download_attempt():
                # This is where the actual download logic would go
                # For now, we'll simulate a failure to demonstrate screenshot capture
                await page.goto(f"https://doi.org/{doi}")
                
                # Simulate checking for PDF link
                pdf_link = await page.query_selector("a[href$='.pdf']")
                if not pdf_link:
                    raise Exception("PDF link not found on page")
                
                # Download PDF
                # ... actual download logic ...
                
            # Use retry handler
            try:
                await self.retry_handler.with_retry(
                    download_attempt,
                    max_attempts=3
                )
                result["success"] = True
                result["pdf_path"] = str(self.download_dir / f"{doi.replace('/', '_')}.pdf")
                
            except Exception as e:
                # Capture failure screenshot
                if self.enable_screenshots:
                    error_info = {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    failure_screenshot = await self.screenshot_capturer.capture_on_failure(
                        page,
                        error_info,
                        doi
                    )
                    
                    if failure_screenshot:
                        result["screenshots"].append(str(failure_screenshot))
                    
                    # Capture comparison screenshot if expected element missing
                    if "PDF link not found" in str(e):
                        comparison = await self.screenshot_capturer.capture_comparison(
                            page,
                            "a[href$='.pdf']",
                            doi
                        )
                        if comparison:
                            result["screenshots"].append(str(comparison))
                
                # Get error diagnostics
                result["error"] = str(e)
                result["diagnostics"]["error_analysis"] = self.error_diagnostics.diagnose_error(e)
                result["diagnostics"]["suggested_solutions"] = \
                    self.error_diagnostics.get_solutions(str(e))
                
        finally:
            await page.close()
            
        return result
    
    async def batch_download_with_reporting(
        self,
        dois: List[str],
        browser_context: Any,
        auth_cookies: Optional[List[Dict]] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Download multiple PDFs with comprehensive reporting.
        
        Args:
            dois: List of DOIs to download
            browser_context: Playwright browser context
            auth_cookies: Authentication cookies
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            Summary report with all results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_limit(doi: str):
            async with semaphore:
                return await self.download_with_diagnostics(
                    doi, browser_context, auth_cookies
                )
        
        # Download all PDFs
        results = await asyncio.gather(
            *[download_with_limit(doi) for doi in dois],
            return_exceptions=True
        )
        
        # Process results
        report = {
            "total": len(dois),
            "successful": 0,
            "failed": 0,
            "results": [],
            "error_summary": {},
            "screenshots_captured": 0
        }
        
        for result in results:
            if isinstance(result, Exception):
                report["failed"] += 1
                report["error_summary"][str(result)] = \
                    report["error_summary"].get(str(result), 0) + 1
            else:
                report["results"].append(result)
                if result["success"]:
                    report["successful"] += 1
                else:
                    report["failed"] += 1
                    error_type = result.get("error", "Unknown")
                    report["error_summary"][error_type] = \
                        report["error_summary"].get(error_type, 0) + 1
                
                report["screenshots_captured"] += len(result.get("screenshots", []))
        
        # Generate summary report file
        await self._generate_report(report)
        
        return report
    
    async def _generate_report(self, report: Dict[str, Any]) -> None:
        """Generate a human-readable report of download results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.download_dir / f"download_report_{timestamp}.txt"
        
        with open(report_file, "w") as f:
            f.write("=== PDF Download Report ===\n\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total attempts: {report['total']}\n")
            f.write(f"Successful: {report['successful']}\n")
            f.write(f"Failed: {report['failed']}\n")
            f.write(f"Screenshots captured: {report['screenshots_captured']}\n\n")
            
            if report["error_summary"]:
                f.write("=== Error Summary ===\n")
                for error, count in report["error_summary"].items():
                    f.write(f"  {error}: {count} occurrences\n")
                f.write("\n")
            
            f.write("=== Detailed Results ===\n")
            for result in report["results"]:
                f.write(f"\nDOI: {result['doi']}\n")
                f.write(f"  Success: {result['success']}\n")
                if result["error"]:
                    f.write(f"  Error: {result['error']}\n")
                if result["screenshots"]:
                    f.write(f"  Screenshots: {', '.join(result['screenshots'])}\n")
                if result.get("diagnostics", {}).get("suggested_solutions"):
                    f.write("  Suggested solutions:\n")
                    for solution in result["diagnostics"]["suggested_solutions"]:
                        f.write(f"    - {solution}\n")
                        
        logger.info(f"Download report saved: {report_file}")