#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 01:10:08 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

__FILE__ = __file__
import asyncio
import hashlib
import shutil
import traceback
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar import ScholarConfig
from scitex.scholar.download.strategies import (
    DownloadMonitorAndSync,
    FlexibleFilenameGenerator,
    show_stop_automation_button_async,
    try_download_chrome_pdf_viewer_async,
    try_download_direct_async,
    try_download_manual_async,
    try_download_response_body_async,
)

logger = logging.getLogger(__name__)


class ScholarPDFDownloader:
    """Download PDFs from URLs with multiple fallback strategies.

    This class focuses solely on downloading PDFs from URLs using various strategies:
    - Chrome PDF Viewer
    - Direct Download (ERR_ABORTED)
    - Response Body Extraction
    - Manual Download Fallback

    URL resolution (DOI → URL) should be handled by the caller.

    Logging Strategy:
    - Uses `logger` for terminal-only logs (batch operations, coordination)
    - Uses `await browser_logger` for browser automation logs (visual popups)
    - All messages prefixed with self.name for traceability
    """

    def __init__(
        self,
        context: BrowserContext,
        config: ScholarConfig = None,
    ):
        self.name = self.__class__.__name__
        self.config = config if config else ScholarConfig()
        self.context = context
        self.output_dir = self.config.get_library_downloads_dir()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    # Main entry points
    # ----------------------------------------

    async def download_from_urls(
        self,
        pdf_urls: List[str],
        output_dir: Union[str, Path] = None,
        max_concurrent: int = 3,
    ) -> List[Path]:
        """Download multiple PDFs with parallel processing.

        Args:
            pdf_urls: List of PDF URLs to download
            output_dir: Output directory for downloaded PDFs
            max_concurrent: Maximum number of concurrent downloads (default: 3)

        Returns:
            List of paths to successfully downloaded PDFs
        """
        output_dir = output_dir or self.output_dir

        if not pdf_urls:
            return []

        output_paths = [
            output_dir / f"{ii_pdf:03d}_{os.path.basename(pdf_url)}"
            for ii_pdf, pdf_url in enumerate(pdf_urls)
        ]

        # Use semaphore for controlled parallelization
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(url: str, path: Path, index: int):
            async with semaphore:
                logger.info(
                    f"{self.name}: Downloading PDF {index}/{len(pdf_urls)}: {url}"
                )
                result = await self.download_from_url(url, path)
                if result:
                    logger.success(f"{self.name}: Downloaded to {result}")
                return result

        tasks = [
            download_with_semaphore(url, path, idx + 1)
            for idx, (url, path) in enumerate(zip(pdf_urls, output_paths))
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful downloads
        saved_paths = []
        for result in results:
            if isinstance(result, Exception):
                logger.debug(f"{self.name}: Download error: {result}")
            elif result:
                saved_paths.append(result)

        logger.success(
            f"{self.name}: Downloaded {len(saved_paths)}/{len(pdf_urls)} PDFs successfully"
        )
        return saved_paths

    async def download_from_url(
        self,
        pdf_url: str,
        output_path: Union[str, Path],
        doi: Optional[str] = None,
    ) -> Optional[Path]:
        """Main download method with manual override support."""

        if not pdf_url:
            logger.warning(
                f"{self.name}: PDF URL passed but not valid: {pdf_url}"
            )
            return None

        if isinstance(output_path, str):
            output_path = Path(output_path)
        if not str(output_path).endswith(".pdf"):
            output_path = Path(str(output_path) + ".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate target filename for button display
        target_filename = FlexibleFilenameGenerator.generate_filename(
            doi=doi,
            url=pdf_url,
            content_type="main",
        )

        # Create stop event and show button
        stop_event = asyncio.Event()
        control_page = await self.context.new_page()

        # Start stop automation button task (non-blocking)
        button_task = asyncio.create_task(
            show_stop_automation_button_async(
                control_page,
                stop_event,
                target_filename,
            )
        )

        # Define download strategies with their names
        async def chrome_pdf_wrapper(url, path):
            return await try_download_chrome_pdf_viewer_async(
                self.context, url, path, self.name
            )

        async def direct_download_wrapper(url, path):
            return await try_download_direct_async(
                self.context, url, path, self.name
            )

        async def response_body_wrapper(url, path):
            return await try_download_response_body_async(
                self.context, url, path, self.name
            )

        async def manual_fallback_wrapper(url, path):
            return await try_download_manual_async(
                self.context, url, path, self.name, self.config
            )

        try_download_methods = [
            ("Chrome PDF", chrome_pdf_wrapper),
            ("Direct Download", direct_download_wrapper),
            ("From Response Body", response_body_wrapper),
            ("Manual Download", manual_fallback_wrapper),
        ]

        for method_name, method_func in try_download_methods:
            # Check if user stopped automation
            if stop_event.is_set():
                logger.info(
                    f"{self.name}: Automation stopped by user - switching to manual mode"
                )
                break

            logger.info(f"{self.name}: Trying method: {method_name}")
            try:
                is_downloaded = await method_func(pdf_url, output_path)
                if is_downloaded:
                    # Success! Remove button and close control page
                    await control_page.close()
                    button_task.cancel()

                    logger.success(
                        f"{self.name}: Successfully downloaded via {method_name}"
                    )
                    return output_path
                else:
                    logger.debug(
                        f"{self.name}: {method_name} returned None (failed or not applicable)"
                    )
            except Exception as e:
                logger.warning(
                    f"{self.name}: {method_name} raised exception: {e}"
                )
                logger.debug(
                    f"{self.name}: Traceback: {traceback.format_exc()}"
                )

        # If user stopped automation, handle manual download
        if stop_event.is_set():
            result = await self._handle_manual_download_async(
                control_page,
                pdf_url,
                output_path,
                doi=doi,
            )
            await control_page.close()
            button_task.cancel()
            return result

        # All methods failed
        await control_page.close()
        button_task.cancel()
        logger.fail(f"{self.name}: All download methods failed for {pdf_url}")
        return None

    # Helper functions
    # ----------------------------------------

    async def _handle_manual_download_async(
        self, page, pdf_url: str, output_path: Path, doi: Optional[str] = None
    ) -> Optional[Path]:
        """
        Handle manual download workflow when automation is stopped by user.

        Args:
            page: Playwright page where stop button was clicked
            pdf_url: URL of the PDF
            output_path: Target output path
            doi: Optional DOI for filename generation

        Returns:
            Path to downloaded file, or None if failed
        """

        # Get directories from config
        temp_downloads_dir = self.config.get_library_downloads_dir()
        final_pdfs_dir = self.config.get_library_pdfs_dir()

        # Extract DOI from URL if not provided
        if not doi and "doi.org/" in pdf_url:
            doi = pdf_url.split("doi.org/")[-1].split("?")[0].split("#")[0]

        await browser_logger.info(
            page,
            f"{self.name}: Starting manual download monitoring...",
        )

        # Run complete manual download workflow (without showing button again)
        # The button was already shown and clicked to trigger this
        monitor = DownloadMonitorAndSync(temp_downloads_dir, final_pdfs_dir)

        # Monitor for new download
        temp_file = await monitor.monitor_for_new_download_async(
            timeout_sec=120,  # 2 minutes to download
        )

        if not temp_file:
            await browser_logger.error(
                page,
                f"{self.name}: No new PDF detected in downloads directory",
            )
            return None

        await browser_logger.success(
            page,
            f"{self.name}: Detected new PDF: {temp_file.name} ({temp_file.stat().st_size / 1e6:.1f} MB)",
        )

        # Sync to final destination
        final_path = monitor.sync_to_final_destination(
            temp_file,
            doi=doi,
            url=pdf_url,
            content_type="main",
            sequence_index=None,
        )

        await browser_logger.success(
            page,
            f"{self.name}: Synced to library: {final_path.name}",
        )

        # Copy to requested output path
        if final_path and final_path.exists():
            shutil.copy2(str(final_path), str(output_path))
            await browser_logger.success(
                page,
                f"{self.name}: Manual download complete: {output_path.name}",
            )
            return output_path

        return None


async def main_async(args):
    """Example usage showing decoupled URL resolution and downloading."""
    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarURLFinder,
    )
    from scitex.scholar.auth import AuthenticationGateway

    # ---------------------------------------
    # Context Preparation
    # ---------------------------------------
    # Authenticated Browser and Context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=args.browser_mode,
        auth_manager=auth_manager,
        use_zenrows_proxy=False,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Authentication Gateway
    auth_gateway = AuthenticationGateway(
        auth_manager=auth_manager,
        browser_manager=browser_manager,
    )
    _url_context = await auth_gateway.prepare_context_async(
        doi=args.doi, context=context
    )

    # ---------------------------------------
    # Step 1: URL Resolution (separate from downloading)
    # ---------------------------------------
    url_finder = ScholarURLFinder(context)
    urls = await url_finder.find_pdf_urls(args.doi)  # Returns List[Dict]

    # Extract URL strings from list of dicts
    pdf_urls = []
    for entry in urls:
        if isinstance(entry, dict):
            pdf_urls.append(entry.get("url"))
        elif isinstance(entry, str):
            pdf_urls.append(entry)

    if not pdf_urls:
        logger.error(f"No PDF URLs found for DOI: {args.doi}")
        return

    logger.info(f"Found {len(pdf_urls)} PDF URL(s) for DOI: {args.doi}")

    # ---------------------------------------
    # Step 2: PDF Download (URL-only, decoupled from DOI resolution)
    # ---------------------------------------
    pdf_downloader = ScholarPDFDownloader(context)

    if len(pdf_urls) == 1:
        # Single URL - direct download
        await pdf_downloader.download_from_url(pdf_urls[0], args.output)
    else:
        # Multiple URLs - batch download with parallelization
        output_dir = Path(args.output).parent
        await pdf_downloader.download_from_urls(
            pdf_urls,
            output_dir=output_dir,
            max_concurrent=3,
        )


def main(args):
    import asyncio

    asyncio.run(main_async(args))

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download a PDF using DOI with authentication support"
    )
    parser.add_argument(
        "--doi",
        type=str,
        required=True,
        help="DOI of the paper (e.g., 10.1088/1741-2552/aaf92e)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="~/.scitex/scholar/downloads/downloaded_paper.pdf",
        help="Output path for the PDF (default: ~/.scitex/scholar/downloads/downloaded_paper.pdf)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["stealth", "interactive", "manual"],
        default="stealth",
        help="Browser mode (default: stealth)",
    )

    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

"""
python -m scitex.scholar.download.ScholarPDFDownloader \
    --browser-mode interactive \
    --doi "10.1016/j.clinph.2024.09.017"

    --doi "10.3389/fnins.2024.1417748"
    --doi "10.1016/j.clinph.2024.09.017"

"""

# EOF
