#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 08:03:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdf_download/strategies/manual_download_utils.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdf_download/strategies/manual_download_utils.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Manual Download Utilities

This module provides shared utilities for manual download workflows:
1. FlexibleFilenameGenerator - DOI-based filename generation
2. DownloadMonitorAndSync - Monitor downloads directory and sync to library
3. UI button functions - Show buttons in browser for manual interaction
"""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.async_api import Page

from scitex.browser.debugging import browser_logger


class FlexibleFilenameGenerator:
    """Generate flexible filenames for PDFs with DOI-based naming."""

    @property
    def name(
        self,
    ):
        return self.__class__.__name__

    @staticmethod
    def sanitize_doi(doi: str) -> str:
        """Convert DOI to filesystem-safe format."""
        # Replace / with _ and remove other problematic characters
        safe = doi.replace("/", "_").replace("\\", "_")
        safe = re.sub(r'[<>:"|?*]', "", safe)
        return safe

    @staticmethod
    def generate_filename(
        doi: Optional[str] = None,
        url: Optional[str] = None,
        content_type: str = "main",
        sequence_index: Optional[int] = None,
        add_timestamp: bool = False,
    ) -> str:
        """
        Generate flexible filename for PDF.

        Args:
            doi: DOI of the article (preferred identifier)
            url: URL if DOI not available
            content_type: Type of content ("main", "supp", "figures", etc.)
            sequence_index: Index for supplements (1, 2, 3, ...)
            add_timestamp: Whether to add timestamp to avoid collisions

        Returns:
            Filename like: 10_1016_S1474-4422_13_70075-9_main.pdf
                          10_1016_S1474-4422_13_70075-9_supp_01.pdf
                          10_1016_S1474-4422_13_70075-9_supp_02_20251010_082215.pdf
        """
        # Generate base identifier
        if doi:
            base = FlexibleFilenameGenerator.sanitize_doi(doi)
        elif url:
            # Use domain and path as fallback
            from urllib.parse import urlparse

            parsed = urlparse(url)
            base = f"{parsed.netloc}_{parsed.path}".replace("/", "_").replace(
                ".", "_"
            )
            base = re.sub(r'[<>:"|?*]', "", base)
        else:
            # Last resort: timestamp-based
            base = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Build filename parts
        parts = [base]

        # Add content type if not main
        if content_type != "main":
            parts.append(content_type)

        # Add sequence index for supplements
        if sequence_index is not None:
            parts.append(f"{sequence_index:02d}")

        # Add timestamp if requested
        if add_timestamp:
            parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

        # Join parts and add extension
        filename = "_".join(parts) + ".pdf"
        return filename


class DownloadMonitorAndSync:
    """Monitor temp downloads directory and sync files to final destination."""

    def __init__(self, temp_downloads_dir: Path, final_pdfs_dir: Path):
        """
        Initialize monitor.

        Args:
            temp_downloads_dir: Temporary browser downloads directory (library/downloads/)
            final_pdfs_dir: Final organized PDFs directory (library/pdfs/)
        """
        self.temp_dir = Path(temp_downloads_dir)
        self.final_dir = Path(final_pdfs_dir)
        self.baseline_files = self._get_current_files()

        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.final_dir.mkdir(parents=True, exist_ok=True)

    def _get_current_files(self) -> set:
        """Get set of current files in temp directory."""
        if not self.temp_dir.exists():
            return set()
        return {f.name for f in self.temp_dir.iterdir() if f.is_file()}

    def _is_pdf_file(self, file_path: Path) -> bool:
        """Check if file is a valid PDF by magic number."""
        if not file_path.exists() or file_path.stat().st_size == 0:
            return False

        try:
            with open(file_path, "rb") as f:
                header = f.read(5)
                return header == b"%PDF-"
        except Exception:
            return False

    def _is_file_stable(self, file_path: Path, wait_ms: int = 300) -> bool:
        """Check if file has finished downloading (size unchanged)."""
        import time

        if not file_path.exists():
            return False

        size1 = file_path.stat().st_size
        time.sleep(wait_ms / 1000)
        size2 = file_path.stat().st_size

        return size1 == size2 and size1 > 0

    async def monitor_for_new_download_async(
        self,
        timeout_sec: float = 120,
        check_interval_sec: float = 1.0,
        logger_func=None,
    ) -> Optional[Path]:
        """
        Monitor temp directory for new PDF files.

        Args:
            timeout_sec: Maximum time to wait for download
            check_interval_sec: How often to check for new files
            logger_func: Optional logging function to report progress

        Returns:
            Path to new PDF file, or None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        last_progress_time = start_time
        progress_interval = 10.0  # Report progress every 10 seconds

        if logger_func:
            logger_func(
                f"{self.name}: Monitoring {self.temp_dir} for new downloads (timeout: {timeout_sec}s)"
            )

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = timeout_sec - elapsed

            if elapsed > timeout_sec:
                if logger_func:
                    logger_func(
                        f"{self.name}: Download monitoring timeout - no new PDF detected"
                    )
                return None

            # Report progress periodically
            if (
                logger_func
                and (elapsed - last_progress_time) >= progress_interval
            ):
                current_file_count = len(self._get_current_files())
                logger_func(
                    f"{self.name}: Still waiting for download... ({remaining:.0f}s remaining, "
                    f"{self.name}: {current_file_count} files in directory)"
                )
                last_progress_time = elapsed

            # Get current files
            current_files = self._get_current_files()
            new_files = current_files - self.baseline_files

            # Check each new file
            for filename in new_files:
                file_path = self.temp_dir / filename

                # Log detection
                if logger_func:
                    logger_func(
                        f"{self.name}: Detected new file: {filename}, checking if complete..."
                    )

                # Check if it's a stable file first
                if not self._is_file_stable(file_path):
                    if logger_func:
                        logger_func(
                            f"{self.name}:   File still downloading, waiting..."
                        )
                    continue

                # Check if it's a valid PDF (by magic number, not extension)
                if self._is_pdf_file(file_path):
                    if logger_func:
                        size_mb = file_path.stat().st_size / 1e6
                        logger_func(
                            f"{self.name}: Found valid PDF: {filename} ({size_mb:.2f} MB)"
                        )
                    return file_path
                else:
                    if logger_func:
                        logger_func(
                            f"{self.name}:   File is not a PDF, skipping: {filename}"
                        )

            # Wait before next check
            await asyncio.sleep(check_interval_sec)

    def sync_to_final_destination(
        self,
        temp_file: Path,
        doi: Optional[str] = None,
        url: Optional[str] = None,
        content_type: str = "main",
        sequence_index: Optional[int] = None,
    ) -> Path:
        """
        Move file from temp to final destination with proper naming.

        Args:
            temp_file: Path to temporary downloaded file
            doi: DOI for filename generation
            url: URL fallback for filename generation
            content_type: Type of content ("main", "supp", etc.)
            sequence_index: Index for supplements

        Returns:
            Path to final destination file
        """
        # Generate proper filename
        filename = FlexibleFilenameGenerator.generate_filename(
            doi=doi,
            url=url,
            content_type=content_type,
            sequence_index=sequence_index,
            add_timestamp=False,
        )

        final_path = self.final_dir / filename

        # Handle collision by adding timestamp
        if final_path.exists():
            filename = FlexibleFilenameGenerator.generate_filename(
                doi=doi,
                url=url,
                content_type=content_type,
                sequence_index=sequence_index,
                add_timestamp=True,
            )
            final_path = self.final_dir / filename

        # Move file
        import shutil

        shutil.move(str(temp_file), str(final_path))

        return final_path


def get_manual_button_init_script(target_filename: str) -> str:
    """Get JavaScript init script that injects manual mode button on ALL pages.

    This script is added to browser context via add_init_script, so it runs
    on EVERY page load, including redirects and new tabs.

    Args:
        target_filename: Target filename to display

    Returns:
        JavaScript code to inject the button
    """
    return f"""
    (() => {{
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', injectManualButton);
        }} else {{
            injectManualButton();
        }}

        function injectManualButton() {{
            // Remove any existing button
            document.getElementById('scitex-manual-button')?.remove();

            // Create button
            const button = document.createElement('button');
            button.id = 'scitex-manual-button';
            button.setAttribute('data-scitex-no-auto-click', 'true');
            button.style.cssText = `
                position: fixed !important;
                top: 50% !important;
                left: 20px !important;
                transform: translateY(-50%) !important;
                z-index: 2147483647 !important;
                background: linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%) !important;
                color: #1a2332 !important;
                padding: 24px 36px !important;
                border: 3px solid #34495e !important;
                border-radius: 8px !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
                font-size: 17px !important;
                font-weight: 700 !important;
                cursor: pointer !important;
                box-shadow: 0 8px 24px rgba(26, 35, 50, 0.4) !important;
                display: block !important;
                visibility: visible !important;
                text-align: center !important;
                line-height: 1.5 !important;
                min-width: 220px !important;
                text-shadow: 0 1px 2px rgba(255,255,255,0.5) !important;
            `;

            button.innerHTML = 'PRESS \\'M\\'<br>FOR MANUAL';

            if (document.documentElement) {{
                document.documentElement.appendChild(button);
            }} else if (document.body) {{
                document.body.appendChild(button);
            }}

            // Keyboard handler - Press 'M' key
            document.addEventListener('keydown', (e) => {{
                if ((e.key === 'm' || e.key === 'M') && !e.ctrlKey && !e.altKey && !e.metaKey) {{
                    if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                        console.log('SciTeX: Key M pressed - Manual mode activated!');
                        button.setAttribute('data-scitex-clicked', 'true');
                        button.innerHTML = 'MANUAL MODE<br>ACTIVATED';
                        button.style.background = 'linear-gradient(135deg, #1a2332 0%, #2d3748 50%, #34495e 100%)';
                        button.style.border = '3px solid #8fa4b0';
                        window._scitexManualModeActivated = true;
                    }}
                }}
            }});

            // Click shows reminder
            button.addEventListener('click', () => {{
                if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                    button.innerHTML = 'PRESS M KEY!';
                    button.style.background = 'linear-gradient(135deg, #6c8ba0 0%, #8fa4b0 100%)';
                    setTimeout(() => {{
                        if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                            button.innerHTML = 'PRESS \\'M\\'<br>FOR MANUAL';
                            button.style.background = 'linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%)';
                        }}
                    }}, 500);
                }}
            }});

            console.log('SciTeX: Manual mode button injected on page!');
        }}
    }})();
    """


async def wait_for_manual_mode_activation_async(
    page: Page,
    stop_event: "asyncio.Event",
) -> None:
    """Wait for user to press 'M' key to activate manual mode.

    Args:
        page: Playwright page
        stop_event: Event to set when manual mode is activated
    """
    try:
        # Wait for the button to be activated (data-scitex-clicked='true')
        await page.wait_for_selector(
            "#scitex-manual-button[data-scitex-clicked='true']",
            timeout=0,  # No timeout - wait forever
        )

        # Set the stop event
        stop_event.set()

        # Update button to monitoring state
        await page.evaluate(
            """
            () => {
                const button = document.getElementById('scitex-manual-button');
                if (button) {
                    button.innerHTML = 'MONITORING<br>DOWNLOADS';
                    button.style.background = 'linear-gradient(135deg, #6b8fb3 0%, #7a9fc3 100%)';
                    button.style.border = '3px solid #506b7a';
                    button.style.cursor = 'default';
                }
            }
        """
        )

    except Exception as e:
        pass


async def show_stop_automation_button_async(
    page: Page,
    stop_event: "asyncio.Event",
    target_filename: str,
) -> None:
    """
    Show 'Download Manually' button that user can click ANYTIME to skip automation.

    This button is shown IMMEDIATELY when PDF page opens and allows users
    to bypass all automation attempts and go straight to manual download mode.

    Args:
        page: Playwright page
        stop_event: Event to signal automation stop
        target_filename: Target filename to display
    """
    try:
        # Log that we're about to show the button
        from scitex import logging

        logger = logging.getLogger(__name__)
        logger.info(
            f"show_stop_automation_button_async: Injecting manual download button on page"
        )

        # Wait a moment for page to be ready
        await page.wait_for_timeout(500)

        # Inject button overlay - wait for body to be ready first
        await page.evaluate(
            f"""
        () => {{
            console.log('SciTeX: Injecting manual download controls...');

            // Wait for body to exist
            if (!document.body) {{
                console.error('SciTeX: document.body not found!');
                return;
            }}

            // Remove any existing button
            document.getElementById('scitex-manual-button')?.remove();

            // ===== MIDDLE-RIGHT FLOATING BUTTON (SciTeX branded) =====
            const button = document.createElement('button');
            button.id = 'scitex-manual-button';
            button.setAttribute('data-scitex-no-auto-click', 'true');
            button.style.cssText = `
                position: fixed !important;
                top: 50% !important;
                left: 20px !important;
                transform: translateY(-50%) !important;
                z-index: 2147483647 !important;
                background: linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%) !important;
                color: #1a2332 !important;
                padding: 24px 36px !important;
                border: 3px solid #34495e !important;
                border-radius: 8px !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
                font-size: 17px !important;
                font-weight: 700 !important;
                cursor: pointer !important;
                box-shadow: 0 8px 24px rgba(26, 35, 50, 0.4) !important;
                display: block !important;
                visibility: visible !important;
                text-align: center !important;
                line-height: 1.5 !important;
                min-width: 220px !important;
                text-shadow: 0 1px 2px rgba(255,255,255,0.5) !important;
            `;

            button.innerHTML = `
                PRESS 'M'<br>FOR MANUAL
            `;

            document.documentElement.appendChild(button);

            // Hover effects
            button.addEventListener('mouseenter', () => {{
                button.style.background = 'linear-gradient(135deg, #34495e 0%, #506b7a 30%, #6c8ba0 60%, #8fa4b0 100%)';
                button.style.transform = 'translateY(-50%) scale(1.08)';
                button.style.boxShadow = '0 12px 32px rgba(26, 35, 50, 0.5)';
            }});
            button.addEventListener('mouseleave', () => {{
                button.style.background = 'linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%)';
                button.style.transform = 'translateY(-50%)';
                button.style.boxShadow = '0 8px 24px rgba(26, 35, 50, 0.4)';
            }});

            // KEYBOARD handler - Press 'M' key (auto-clickers can't do this!)
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'm' || e.key === 'M') {{
                    if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                        console.log('SciTeX: Key M pressed - Manual mode activated!');
                        button.setAttribute('data-scitex-clicked', 'true');
                        button.innerHTML = 'MANUAL MODE<br>ACTIVATED';
                        button.style.background = 'linear-gradient(135deg, #1a2332 0%, #2d3748 50%, #34495e 100%)';
                        button.style.border = '3px solid #8fa4b0';
                    }}
                }}
            }}, {{ capture: true }});

            // Click handler just for feedback (doesn't activate)
            button.addEventListener('click', (e) => {{
                if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                    button.innerHTML = 'PRESS M KEY!';
                    button.style.background = 'linear-gradient(135deg, #6c8ba0 0%, #8fa4b0 100%)';
                    setTimeout(() => {{
                        if (button.getAttribute('data-scitex-clicked') !== 'true') {{
                            button.innerHTML = 'PRESS \\'M\\'<br>FOR MANUAL';
                            button.style.background = 'linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%)';
                        }}
                    }}, 500);
                }}
            }}, {{ capture: true }});

            // Periodically ensure button stays visible and on top
            setInterval(() => {{
                const existing = document.getElementById('scitex-manual-button');
                if (!existing) {{
                    document.documentElement.appendChild(button);
                }} else if (existing.parentElement) {{
                    existing.parentElement.appendChild(existing);
                }}
            }}, 2000);

            console.log('SciTeX: Manual mode button injected at MIDDLE-RIGHT!');
        }}
    """
        )

        logger.info(
            f"show_stop_automation_button_async: Button injected, waiting for user click..."
        )

        # Show browser notification that button is ready
        await browser_logger.info(
            page,
            "MANUAL DOWNLOAD BUTTON: Check lower-right corner to skip automation!",
        )

    except Exception as e:
        logger.error(
            f"show_stop_automation_button_async: Failed to inject button: {e}"
        )
        return

    # Wait for DOUBLE-CLICK (no timeout - always available)
    try:
        await page.wait_for_selector(
            "#scitex-manual-button",
            state="attached",
        )

        # Wait for the data-scitex-clicked attribute to be set by double-click
        await page.wait_for_selector(
            "#scitex-manual-button[data-scitex-clicked='true']",
            timeout=0,  # No timeout - wait forever
        )

        # Set the stop event
        stop_event.set()

        # Update button to show monitoring state
        await page.evaluate(
            """
            () => {
                const button = document.getElementById('scitex-manual-button');
                if (button) {
                    button.innerHTML = 'MONITORING<br>DOWNLOADS';
                    button.style.background = 'linear-gradient(135deg, #6b8fb3 0%, #7a9fc3 100%)';
                    button.style.border = '3px solid #506b7a';
                    button.style.cursor = 'default';
                }
            }
        """
        )

    except Exception as e:
        # Button was removed or page closed
        pass


async def show_manual_download_button_async(
    page: Page,
    target_filename: str,
    timeout_sec: float = 300,
) -> bool:
    """
    Show manual download button overlay and wait for user click.

    Args:
        page: Playwright page
        target_filename: Target filename to display
        timeout_sec: How long to wait for user click

    Returns:
        True if button clicked, False if timeout
    """
    # Inject button overlay
    await page.evaluate(
        f"""
        () => {{
            // Create overlay container
            const overlay = document.createElement('div');
            overlay.id = 'manual-download-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 999999;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                color: white;
                max-width: 350px;
            `;

            overlay.innerHTML = `
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                    📥 Manual Download Mode
                </div>
                <div style="font-size: 13px; margin-bottom: 12px; opacity: 0.9;">
                    Target: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">{target_filename}</code>
                </div>
                <div style="font-size: 12px; margin-bottom: 12px; opacity: 0.8;">
                    Please download the PDF manually, then click below to continue.
                </div>
                <button id='manual-download-confirm' style="
                    width: 100%;
                    padding: 12px;
                    background: white;
                    color: #667eea;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">
                    ✓ I've Downloaded the PDF
                </button>
            `;

            document.body.appendChild(overlay);

            // Add hover effect
            const button = overlay.querySelector('#manual-download-confirm');
            button.addEventListener('mouseenter', () => {{
                button.style.background = '#f0f0f0';
                button.style.transform = 'scale(1.02)';
            }});
            button.addEventListener('mouseleave', () => {{
                button.style.background = 'white';
                button.style.transform = 'scale(1)';
            }});
        }}
    """
    )

    # Wait for button click with timeout
    try:
        await page.wait_for_selector(
            "#manual-download-confirm",
            state="attached",
            timeout=timeout_sec * 1000,
        )
        await page.click("#manual-download-confirm")

        # Remove overlay
        await page.evaluate(
            "() => { document.getElementById('manual-download-overlay')?.remove(); }"
        )

        return True
    except Exception:
        # Timeout or error
        await page.evaluate(
            "() => { document.getElementById('manual-download-overlay')?.remove(); }"
        )
        return False


async def complete_manual_download_workflow_async(
    page: Page,
    temp_downloads_dir: Path,
    final_pdfs_dir: Path,
    doi: Optional[str] = None,
    url: Optional[str] = None,
    content_type: str = "main",
    sequence_index: Optional[int] = None,
    button_timeout_sec: float = 300,
    download_timeout_sec: float = 120,
) -> Optional[Path]:
    """
    Complete manual download workflow with monitoring and syncing.

    Workflow:
    1. Show manual download button with target filename
    2. Wait for user to click (button_timeout_sec)
    3. START monitoring temp downloads directory
    4. DETECT new PDF file (download_timeout_sec)
    5. SYNC to final destination with proper naming
    6. CLEANUP and confirm

    Args:
        page: Playwright page
        temp_downloads_dir: Temporary downloads directory (library/downloads/)
        final_pdfs_dir: Final PDFs directory (library/pdfs/)
        doi: DOI of article
        url: URL of article
        content_type: Type of content ("main", "supp", etc.)
        sequence_index: Index for supplements
        button_timeout_sec: How long to wait for button click
        download_timeout_sec: How long to wait for download

    Returns:
        Path to final PDF file, or None if failed
    """
    # Generate target filename for display
    target_filename = FlexibleFilenameGenerator.generate_filename(
        doi=doi,
        url=url,
        content_type=content_type,
        sequence_index=sequence_index,
    )

    # Step 1: Show button and wait for click
    await browser_logger.info(
        page,
        f"Showing manual download button (target: {target_filename})",
        func_name="complete_manual_download_workflow",
    )

    button_clicked = await show_manual_download_button_async(
        page,
        target_filename,
        timeout_sec=button_timeout_sec,
    )

    if not button_clicked:
        await browser_logger.warning(
            page,
            "Manual download button timeout - user did not click",
            func_name="complete_manual_download_workflow",
        )
        return None

    # Step 2: Start monitoring
    await browser_logger.info(
        page,
        "User confirmed download - monitoring temp directory",
        func_name="complete_manual_download_workflow",
    )

    monitor = DownloadMonitorAndSync(temp_downloads_dir, final_pdfs_dir)

    # Step 3: Detect new download
    temp_file = await monitor.monitor_for_new_download_async(
        timeout_sec=download_timeout_sec,
    )

    if not temp_file:
        await browser_logger.error(
            page,
            f"No new PDF detected in {download_timeout_sec}s",
            func_name="complete_manual_download_workflow",
        )
        return None

    await browser_logger.info(
        page,
        f"Detected new PDF: {temp_file.name} ({temp_file.stat().st_size / 1e6:.1f} MB)",
        func_name="complete_manual_download_workflow",
    )

    # Step 4: Sync to final destination
    final_path = monitor.sync_to_final_destination(
        temp_file,
        doi=doi,
        url=url,
        content_type=content_type,
        sequence_index=sequence_index,
    )

    await browser_logger.info(
        page,
        f"Synced to library: {final_path.name}",
        func_name="complete_manual_download_workflow",
    )

    return final_path


def get_manual_button_init_script(target_filename: str) -> str:
    """Get JavaScript init script to inject manual mode button on ALL pages.

    This script runs on EVERY page load (including redirects) to ensure
    the manual mode button is always available.

    Args:
        target_filename: Target filename to display

    Returns:
        JavaScript code as string
    """
    return f"""
(() => {{
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', injectManualButton);
    }} else {{
        injectManualButton();
    }}

    function injectManualButton() {{
        // Remove existing button
        document.getElementById('scitex-manual-button')?.remove();

        // Create button
        const button = document.createElement('button');
        button.id = 'scitex-manual-button';
        button.setAttribute('data-scitex-no-auto-click', 'true');
        button.style.cssText = `
            position: fixed !important;
            top: 50% !important;
            left: 20px !important;
            transform: translateY(-50%) !important;
            z-index: 2147483647 !important;
            background: linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%) !important;
            color: #1a2332 !important;
            padding: 24px 36px !important;
            border: 3px solid #34495e !important;
            border-radius: 8px !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            box-shadow: 0 8px 24px rgba(26, 35, 50, 0.4) !important;
            display: block !important;
            visibility: visible !important;
            text-align: center !important;
            line-height: 1.5 !important;
            min-width: 220px !important;
            text-shadow: 0 1px 2px rgba(255,255,255,0.5) !important;
        `;

        button.innerHTML = `SciTeX<br>Press for Manual Mode`;

        (document.documentElement || document.body).appendChild(button);

        // Click handler - ONLY way to activate
        button.addEventListener('click', (e) => {{
            e.preventDefault();
            e.stopPropagation();

            if (button.getAttribute('data-activated') !== 'true') {{
                console.log('SciTeX: Manual mode activated!');
                button.setAttribute('data-activated', 'true');
                button.innerHTML = 'SciTeX<br>Manual Mode Active';
                button.style.background = 'linear-gradient(135deg, #1a2332 0%, #2d3748 50%, #34495e 100%)';
                button.style.border = '3px solid #8fa4b0';
                button.style.cursor = 'default';

                // Close all browser_logger popups
                const popupContainer = document.getElementById('_scitex_popup_container');
                if (popupContainer) {{
                    popupContainer.remove();
                }}
            }}
        }}, {{ capture: true }});

        // Hover effects
        button.addEventListener('mouseenter', () => {{
            if (button.getAttribute('data-activated') !== 'true') {{
                button.style.background = 'linear-gradient(135deg, #34495e 0%, #506b7a 30%, #6c8ba0 60%, #8fa4b0 100%)';
                button.style.transform = 'translateY(-50%) scale(1.08)';
            }}
        }});
        button.addEventListener('mouseleave', () => {{
            if (button.getAttribute('data-activated') !== 'true') {{
                button.style.background = 'linear-gradient(135deg, #506b7a 0%, #6c8ba0 30%, #8fa4b0 60%, #b5c7d1 100%)';
                button.style.transform = 'translateY(-50%)';
            }}
        }});

        console.log('SciTeX: Manual mode button injected via init script (appears on ALL pages)');
    }}
}})();
"""


async def wait_for_manual_mode_activation_async(
    page: Page,
    stop_event: asyncio.Event,
    timeout_sec: float = 0,  # 0 = wait forever
) -> None:
    """Wait for user to click the manual mode button.

    Monitors the button's data-activated attribute which gets set when
    user clicks the button.

    Args:
        page: Playwright page
        stop_event: Event to set when manual mode is activated
        timeout_sec: Timeout in seconds (0 = wait forever)
    """
    try:
        from scitex import logging

        logger = logging.getLogger(__name__)
        logger.info(
            "wait_for_manual_mode_activation_async: Waiting for button click..."
        )

        # Wait for button to be activated (clicked)
        timeout_ms = timeout_sec * 1000 if timeout_sec > 0 else 0
        await page.wait_for_selector(
            "#scitex-manual-button[data-activated='true']",
            timeout=timeout_ms,
        )

        logger.info(
            "wait_for_manual_mode_activation_async: Button clicked! Setting stop event..."
        )

        # Set stop event
        stop_event.set()

        logger.info(
            f"wait_for_manual_mode_activation_async: stop_event.is_set() = {stop_event.is_set()}"
        )

        # Close all browser_logger popups
        await page.evaluate(
            """
            () => {
                const popupContainer = document.getElementById('_scitex_popup_container');
                if (popupContainer) {
                    popupContainer.remove();
                }
            }
        """
        )

        # Update button to show monitoring
        await page.evaluate(
            """
            () => {
                const button = document.getElementById('scitex-manual-button');
                if (button) {
                    button.innerHTML = 'SciTeX<br>Monitoring Downloads...';
                    button.style.background = 'linear-gradient(135deg, #6b8fb3 0%, #7a9fc3 100%)';
                    button.style.border = '3px solid #506b7a';
                }
            }
        """
        )

    except Exception as e:
        pass

# EOF
