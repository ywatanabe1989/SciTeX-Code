#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual Download Utilities

This module provides shared utilities for manual download workflows:
1. FlexibleFilenameGenerator - DOI-based filename generation
2. DownloadMonitorAndSync - Monitor downloads directory and sync to library
3. UI button functions - Show buttons in browser for manual interaction
"""

import asyncio
import re
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import Page

from scitex.browser.debugging import browser_logger


class FlexibleFilenameGenerator:
    """Generate flexible filenames for PDFs with DOI-based naming."""

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
            base = f"{parsed.netloc}_{parsed.path}".replace("/", "_").replace(".", "_")
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
    ) -> Optional[Path]:
        """
        Monitor temp directory for new PDF files.

        Args:
            timeout_sec: Maximum time to wait for download
            check_interval_sec: How often to check for new files

        Returns:
            Path to new PDF file, or None if timeout
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout_sec:
                return None

            # Get current files
            current_files = self._get_current_files()
            new_files = current_files - self.baseline_files

            # Check each new file
            for filename in new_files:
                file_path = self.temp_dir / filename

                # Check if it's a stable PDF
                if self._is_file_stable(file_path) and self._is_pdf_file(file_path):
                    return file_path

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


async def show_stop_automation_button_async(
    page: Page,
    stop_event: "asyncio.Event",
    target_filename: str,
) -> None:
    """
    Show 'Stop Automation' button that user can click anytime to take over manually.

    This button is shown from the start and allows users to bypass automation.
    When clicked, it sets stop_event and updates to monitoring state.

    Args:
        page: Playwright page
        stop_event: Event to signal automation stop
        target_filename: Target filename to display
    """
    # Inject button overlay
    await page.evaluate(f"""
        () => {{
            // Create overlay container
            const overlay = document.createElement('div');
            overlay.id = 'stop-automation-overlay';
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
                    🤖 SciTeX Download Helper
                </div>
                <div style="font-size: 13px; margin-bottom: 12px; opacity: 0.9;">
                    Target: <code style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px;">{target_filename}</code>
                </div>
                <div style="font-size: 12px; margin-bottom: 12px; opacity: 0.8;">
                    Automation is running. Click below to take over manually anytime.
                </div>
                <button id='stop-automation-btn' style="
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
                    ⏹ Stop Automation & Download Manually
                </button>
            `;

            document.body.appendChild(overlay);

            // Add hover effect
            const button = overlay.querySelector('#stop-automation-btn');
            button.addEventListener('mouseenter', () => {{
                button.style.background = '#f0f0f0';
                button.style.transform = 'scale(1.02)';
            }});
            button.addEventListener('mouseleave', () => {{
                button.style.background = 'white';
                button.style.transform = 'scale(1)';
            }});
        }}
    """)

    # Wait for button click (no timeout - always available)
    try:
        await page.wait_for_selector(
            "#stop-automation-btn",
            state="attached",
        )
        await page.click("#stop-automation-btn")

        # Set the stop event
        stop_event.set()

        # Update button to show monitoring state
        await page.evaluate("""
            () => {
                const overlay = document.getElementById('stop-automation-overlay');
                if (overlay) {
                    overlay.innerHTML = `
                        <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                            📥 Manual Download Mode
                        </div>
                        <div style="font-size: 13px; margin-bottom: 12px; opacity: 0.9;">
                            Automation stopped - monitoring downloads...
                        </div>
                        <div style="font-size: 12px; opacity: 0.8;">
                            Please download the PDF manually.
                        </div>
                    `;
                }
            }
        """)

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
    await page.evaluate(f"""
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
    """)

    # Wait for button click with timeout
    try:
        await page.wait_for_selector(
            "#manual-download-confirm",
            state="attached",
            timeout=timeout_sec * 1000,
        )
        await page.click("#manual-download-confirm")

        # Remove overlay
        await page.evaluate("() => { document.getElementById('manual-download-overlay')?.remove(); }")

        return True
    except Exception:
        # Timeout or error
        await page.evaluate("() => { document.getElementById('manual-download-overlay')?.remove(); }")
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

    await browser_logger.success(
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

    await browser_logger.success(
        page,
        f"Synced to library: {final_path.name}",
        func_name="complete_manual_download_workflow",
    )

    return final_path


# EOF
