#!/usr/bin/env python3
"""Enhanced PDF downloader with screenshot capture capabilities for debugging."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union, Dict, Tuple

from playwright.async_api import BrowserContext, Page

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader

logger = logging.getLogger(__name__)


class ScholarPDFDownloaderWithScreenshots(ScholarPDFDownloader):
    """PDF downloader that captures screenshots at intervals and on failure."""

    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
        use_cache=False,
        screenshot_interval: float = 2.0,  # seconds between screenshots
        capture_on_failure: bool = True,
        capture_during_success: bool = True,  # Always capture for documentation
    ):
        super().__init__(context, config, use_cache)
        self.screenshot_interval = screenshot_interval
        self.capture_on_failure = capture_on_failure
        self.capture_during_success = capture_during_success
        self.screenshot_tasks = {}  # Track screenshot tasks per page

    def _get_screenshot_dir(self, doi: str = None, paper_id: str = None) -> Path:
        """Get the screenshot directory for a paper.

        WARNING: paper_id should always be provided to ensure consistency.
        Generating paper_id from DOI alone can cause ID mismatches.
        """
        library_dir = self.config.get_library_dir()

        if paper_id:
            # Use paper ID directly if provided (PREFERRED)
            screenshot_dir = library_dir / "MASTER" / paper_id / "screenshots"
        elif doi:
            # DEPRECATED: Generating paper ID from DOI alone
            # This can cause inconsistencies - caller should use PathManager._generate_paper_id()
            logger.warning(
                f"Generating paper_id from DOI alone for screenshots. "
                f"This may cause ID mismatches. Please pass paper_id explicitly."
            )
            # Use PathManager for consistency
            paper_id = self.config.path_manager._generate_paper_id(doi=doi)
            screenshot_dir = library_dir / "MASTER" / paper_id / "screenshots"
        else:
            # Fallback to temp directory
            screenshot_dir = Path("/tmp/scholar_screenshots")

        screenshot_dir.mkdir(parents=True, exist_ok=True)
        return screenshot_dir

    def _get_logs_dir(self, doi: str = None, paper_id: str = None) -> Path:
        """Get the logs directory for a paper.

        WARNING: paper_id should always be provided to ensure consistency.
        Generating paper_id from DOI alone can cause ID mismatches.
        """
        library_dir = self.config.get_library_dir()

        if paper_id:
            logs_dir = library_dir / "MASTER" / paper_id / "logs"
        elif doi:
            # DEPRECATED: Generating paper ID from DOI alone
            # This can cause inconsistencies - caller should use PathManager._generate_paper_id()
            logger.warning(
                f"Generating paper_id from DOI alone for logs. "
                f"This may cause ID mismatches. Please pass paper_id explicitly."
            )
            # Use PathManager for consistency
            paper_id = self.config.path_manager._generate_paper_id(doi=doi)
            logs_dir = library_dir / "MASTER" / paper_id / "logs"
        else:
            logs_dir = Path("/tmp/scholar_logs")

        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    async def _save_download_log(
        self,
        doi: str,
        paper_id: str,
        method: str,
        url: str,
        success: bool,
        error_message: str = None,
        console_logs: List[str] = None,
        network_logs: List[Dict] = None
    ) -> Optional[Path]:
        """Save detailed download attempt log."""
        import json

        logs_dir = self._get_logs_dir(doi, paper_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

        log_data = {
            "timestamp": timestamp,
            "doi": doi,
            "paper_id": paper_id,
            "method": method,
            "url": url,
            "success": success,
            "error_message": error_message,
            "console_logs": console_logs or [],
            "network_logs": network_logs or []
        }

        log_path = logs_dir / f"{timestamp}-{method}.json"

        try:
            with open(log_path, "w") as f:
                json.dump(log_data, f, indent=2, default=str)
            logger.debug(f"Saved log: {log_path.name}")
            return log_path
        except Exception as e:
            logger.warning(f"Failed to save log: {e}")
            return None

    async def _capture_screenshot_async(
        self,
        page: Page,
        description: str,
        doi: str = None,
        paper_id: str = None
    ) -> Optional[Path]:
        """Capture a single screenshot with timestamp and description."""
        try:
            screenshot_dir = self._get_screenshot_dir(doi, paper_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds

            # Sanitize description for filename
            safe_description = "".join(
                c if c.isalnum() or c in "-_" else "_"
                for c in description
            )[:50]  # Limit length

            screenshot_path = screenshot_dir / f"{timestamp}-{safe_description}.png"

            logger.debug(f"Attempting to save screenshot to: {screenshot_path}")

            # Wait for page to be fully loaded before screenshot (helps with Xvfb rendering)
            try:
                await page.wait_for_load_state("networkidle", timeout=3000)
                await page.wait_for_timeout(500)  # Additional 500ms for Xvfb to render
            except:
                pass  # Continue even if timeout

            # Capture full page screenshot
            await page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                timeout=5000  # 5 second timeout for screenshot
            )

            logger.success(f"Screenshot saved: {screenshot_path}")
            logger.info(f"  Directory: {screenshot_dir}")
            logger.info(f"  Filename: {screenshot_path.name}")
            logger.info(f"  Size: {screenshot_path.stat().st_size} bytes")
            return screenshot_path

        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            logger.error(f"  DOI: {doi}")
            logger.error(f"  Paper ID: {paper_id}")
            logger.error(f"  Description: {description}")
            return None

    async def _capture_screenshots_periodically(
        self,
        page: Page,
        doi: str = None,
        paper_id: str = None,
        stop_event: asyncio.Event = None
    ):
        """Capture screenshots at regular intervals until stopped."""
        screenshot_count = 0

        try:
            while not stop_event or not stop_event.is_set():
                screenshot_count += 1
                await self._capture_screenshot_async(
                    page,
                    f"interval_{screenshot_count:03d}",
                    doi,
                    paper_id
                )

                # Wait for interval or stop signal
                try:
                    await asyncio.wait_for(
                        stop_event.wait(),
                        timeout=self.screenshot_interval
                    )
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    continue  # Continue capturing

        except asyncio.CancelledError:
            logger.debug("Screenshot capture task cancelled")
        except Exception as e:
            logger.warning(f"Error in periodic screenshot capture: {e}")

    async def download_from_url_with_screenshots(
        self,
        pdf_url: str,
        output_path: Union[str, Path],
        doi: str = None,
        paper_id: str = None,
        retry_with_screenshots: bool = True
    ) -> Tuple[Optional[Path], List[Path]]:
        """
        Download PDF with screenshot capture.

        Returns:
            Tuple of (downloaded_path, screenshot_paths)
        """
        screenshot_paths = []

        # First attempt - normal download
        result = await self.download_from_url(pdf_url, output_path)

        if result:
            if self.capture_during_success:
                # Capture a success screenshot
                page = await self.context.new_page()
                try:
                    await page.goto(pdf_url, timeout=10000)
                    screenshot_path = await self._capture_screenshot_async(
                        page, "download_success", doi, paper_id
                    )
                    if screenshot_path:
                        screenshot_paths.append(screenshot_path)
                finally:
                    await page.close()
            return result, screenshot_paths

        # If failed and retry with screenshots is enabled
        if retry_with_screenshots and self.capture_on_failure:
            logger.info(f"Retrying download with screenshot documentation for {pdf_url}")

            # Retry each method with screenshots
            methods = [
                ("chrome_pdf", self._retry_chrome_pdf_with_screenshots),
                ("direct", self._retry_direct_with_screenshots),
                ("response", self._retry_response_with_screenshots)
            ]

            for method_name, method_func in methods:
                logger.info(f"Retrying with {method_name} method and screenshots")
                result, method_screenshots = await method_func(
                    pdf_url, output_path, doi, paper_id
                )
                screenshot_paths.extend(method_screenshots)

                if result:
                    logger.success(f"Download succeeded with {method_name} method")
                    return result, screenshot_paths

        # All methods failed - capture final failure state
        if self.capture_on_failure:
            page = await self.context.new_page()
            try:
                await page.goto(pdf_url, timeout=30000, wait_until="networkidle")

                # Capture multiple aspects of the failure
                await self._capture_screenshot_async(page, "final_failure_state", doi, paper_id)

                # Check for common error indicators
                if await page.query_selector("text=/access denied/i"):
                    await self._capture_screenshot_async(page, "access_denied", doi, paper_id)

                if await page.query_selector("text=/captcha/i"):
                    await self._capture_screenshot_async(page, "captcha_detected", doi, paper_id)

                if await page.query_selector("text=/404|not found/i"):
                    await self._capture_screenshot_async(page, "not_found_error", doi, paper_id)

            except Exception as e:
                logger.warning(f"Error capturing failure screenshots: {e}")
            finally:
                await page.close()

        return None, screenshot_paths

    async def _retry_chrome_pdf_with_screenshots(
        self,
        pdf_url: str,
        output_path: Path,
        doi: str = None,
        paper_id: str = None
    ) -> Tuple[Optional[Path], List[Path]]:
        """Retry Chrome PDF viewer method with screenshots and logging."""
        screenshots = []
        console_logs = []
        network_logs = []
        page = None
        stop_event = asyncio.Event()
        screenshot_task = None

        try:
            page = await self.context.new_page()

            # Set up console log capture
            page.on("console", lambda msg: console_logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": msg.type,
                "text": msg.text
            }))

            # Set up network log capture
            page.on("response", lambda response: network_logs.append({
                "timestamp": datetime.now().isoformat(),
                "url": response.url,
                "status": response.status,
                "headers": dict(response.headers)
            }))

            # Start periodic screenshots
            screenshot_task = asyncio.create_task(
                self._capture_screenshots_periodically(
                    page, doi, paper_id, stop_event
                )
            )

            # Initial screenshot
            ss = await self._capture_screenshot_async(page, "chrome_pdf_initial", doi, paper_id)
            if ss:
                screenshots.append(ss)

            # Navigate to URL
            await page.goto(pdf_url, wait_until="load", timeout=60000)
            await page.wait_for_timeout(3000)

            # Check if PDF viewer loaded
            ss = await self._capture_screenshot_async(page, "chrome_pdf_loaded", doi, paper_id)
            if ss:
                screenshots.append(ss)

            # Try download button
            from scitex.scholar.browser import (
                detect_pdf_viewer_async,
                click_download_button_from_chrome_pdf_viewer_async
            )

            is_pdf_viewer = await detect_pdf_viewer_async(page)
            if is_pdf_viewer:
                await self._capture_screenshot_async(page, "chrome_pdf_viewer_detected", doi, paper_id)

                # Set up download handler
                download_path = None

                async def handle_download(download):
                    nonlocal download_path
                    await download.save_as(output_path)
                    download_path = output_path

                page.on("download", handle_download)

                # Click download
                await click_download_button_from_chrome_pdf_viewer_async(page)
                await page.wait_for_timeout(5000)

                if download_path and download_path.exists():
                    await self._capture_screenshot_async(page, "chrome_pdf_success", doi, paper_id)
                    # Save success log
                    await self._save_download_log(
                        doi, paper_id, "chrome_pdf", pdf_url, True,
                        console_logs=console_logs, network_logs=network_logs
                    )
                    return output_path, screenshots

        except Exception as e:
            logger.warning(f"Chrome PDF method failed: {e}")
            if page:
                await self._capture_screenshot_async(page, f"chrome_pdf_error_{str(e)[:30]}", doi, paper_id)
            # Save failure log
            await self._save_download_log(
                doi, paper_id, "chrome_pdf", pdf_url, False,
                error_message=str(e), console_logs=console_logs, network_logs=network_logs
            )
        finally:
            stop_event.set()
            if screenshot_task:
                screenshot_task.cancel()
            if page:
                await page.close()

        return None, screenshots

    async def _retry_direct_with_screenshots(
        self,
        pdf_url: str,
        output_path: Path,
        doi: str = None,
        paper_id: str = None
    ) -> Tuple[Optional[Path], List[Path]]:
        """Retry direct download method with screenshots."""
        screenshots = []
        page = None
        stop_event = asyncio.Event()
        screenshot_task = None

        try:
            page = await self.context.new_page()

            # Start periodic screenshots
            screenshot_task = asyncio.create_task(
                self._capture_screenshots_periodically(
                    page, doi, paper_id, stop_event
                )
            )

            # Set up download handler
            download_occurred = False

            async def handle_download(download):
                nonlocal download_occurred
                await download.save_as(output_path)
                download_occurred = True

            page.on("download", handle_download)

            # Initial screenshot
            ss = await self._capture_screenshot_async(page, "direct_initial", doi, paper_id)
            if ss:
                screenshots.append(ss)

            try:
                # Try navigation - may trigger download
                await page.goto(pdf_url, wait_until="load", timeout=30000)
            except Exception as nav_error:
                if "ERR_ABORTED" in str(nav_error):
                    logger.info("ERR_ABORTED detected - likely direct download")
                    await page.wait_for_timeout(5000)

            # Check if download occurred
            if download_occurred and output_path.exists():
                await self._capture_screenshot_async(page, "direct_success", doi, paper_id)
                return output_path, screenshots

            # Capture final state
            await self._capture_screenshot_async(page, "direct_final_state", doi, paper_id)

        except Exception as e:
            logger.warning(f"Direct download method failed: {e}")
            if page:
                await self._capture_screenshot_async(page, f"direct_error_{str(e)[:30]}", doi, paper_id)
        finally:
            stop_event.set()
            if screenshot_task:
                screenshot_task.cancel()
            if page:
                await page.close()

        return None, screenshots

    async def _retry_response_with_screenshots(
        self,
        pdf_url: str,
        output_path: Path,
        doi: str = None,
        paper_id: str = None
    ) -> Tuple[Optional[Path], List[Path]]:
        """Retry response body method with screenshots."""
        screenshots = []
        page = None

        try:
            page = await self.context.new_page()

            # Initial screenshot
            ss = await self._capture_screenshot_async(page, "response_initial", doi, paper_id)
            if ss:
                screenshots.append(ss)

            response = await page.goto(pdf_url, wait_until="load", timeout=60000)

            # Screenshot after navigation
            ss = await self._capture_screenshot_async(page, "response_loaded", doi, paper_id)
            if ss:
                screenshots.append(ss)

            if response and response.ok:
                content = await response.body()

                # Check if it's a PDF
                if content[:4] == b"%PDF" and len(content) > 1024:
                    with open(output_path, "wb") as f:
                        f.write(content)

                    await self._capture_screenshot_async(page, "response_success", doi, paper_id)
                    return output_path, screenshots
                else:
                    await self._capture_screenshot_async(page, "response_not_pdf", doi, paper_id)
            else:
                await self._capture_screenshot_async(page, f"response_status_{response.status if response else 'none'}", doi, paper_id)

        except Exception as e:
            logger.warning(f"Response body method failed: {e}")
            if page:
                await self._capture_screenshot_async(page, f"response_error_{str(e)[:30]}", doi, paper_id)
        finally:
            if page:
                await page.close()

        return None, screenshots


# Enhanced download method for Scholar class
async def download_pdf_with_screenshots(
    self,
    doi: str,
    pdf_urls: List[str],
    paper_id: str = None,
    output_dir: Path = None
) -> Tuple[Optional[Path], List[Path]]:
    """
    Download PDF with screenshot documentation.

    Args:
        doi: DOI of the paper
        pdf_urls: List of potential PDF URLs
        paper_id: Optional paper ID for storage
        output_dir: Output directory for PDF

    Returns:
        Tuple of (pdf_path, screenshot_paths)
    """
    from scitex.scholar.download.ScholarPDFDownloaderWithScreenshots import (
        ScholarPDFDownloaderWithScreenshots
    )

    if not paper_id:
        # Generate using PathManager for consistency
        # Note: This only uses DOI, which may not match IDs generated with full metadata
        logger.warning(
            "Generating paper_id from DOI alone. "
            "For consistency, caller should pass paper_id explicitly."
        )
        paper_id = self.config.path_manager._generate_paper_id(doi=doi)

    # Get browser context
    browser, context = await self._browser_manager.get_authenticated_browser_and_context_async()

    # Create enhanced downloader
    downloader = ScholarPDFDownloaderWithScreenshots(
        context=context,
        config=self.config,
        screenshot_interval=2.0,
        capture_on_failure=True,
        capture_during_success=True  # Always capture for documentation
    )

    # Try each PDF URL
    all_screenshots = []
    for pdf_url in pdf_urls:
        temp_output = Path("/tmp") / f"{doi.replace('/', '_').replace(':', '_')}.pdf"

        pdf_path, screenshots = await downloader.download_from_url_with_screenshots(
            pdf_url=pdf_url,
            output_path=temp_output,
            doi=doi,
            paper_id=paper_id,
            retry_with_screenshots=True
        )

        all_screenshots.extend(screenshots)

        if pdf_path and pdf_path.exists():
            # Move to final location
            if output_dir:
                final_path = output_dir / f"DOI_{doi.replace('/', '_')}.pdf"
                final_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.move(str(pdf_path), str(final_path))
                return final_path, all_screenshots

            return pdf_path, all_screenshots

    logger.warning(f"All download attempts failed for DOI {doi}. Screenshots saved: {len(all_screenshots)}")
    return None, all_screenshots