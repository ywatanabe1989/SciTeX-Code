#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 07:16:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdf_download/ScholarPDFDownloader.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdf_download/ScholarPDFDownloader.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

__FILE__ = __file__
import asyncio
import hashlib
import traceback
from pathlib import Path
from typing import List, Optional, Union

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.browser.debugging import browser_logger
from scitex.scholar import ScholarConfig
from scitex.scholar.pdf_download.strategies import (
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
        """Main download method with manual override support.

        Shows manual download button immediately - if clicked, switches to manual mode.
        Otherwise tries automated download strategies.
        """

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

        # Create stop event for manual mode
        stop_event = asyncio.Event()

        # Add manual mode flag to context (shared across all strategies)
        self.context._scitex_is_manual_mode = (
            False  # Flag strategies can check
        )
        self.context._scitex_manual_mode_event = (
            stop_event  # Event for internal monitoring
        )

        # Inject manual mode button script into ALL pages in this context
        # This ensures button appears on every page, even after redirects
        from scitex.scholar.pdf_download.strategies.manual_download_utils import (
            get_manual_button_init_script,
        )

        button_script = get_manual_button_init_script(target_filename)
        await self.context.add_init_script(button_script)
        logger.info(
            f"{self.name}: Manual mode button injected into browser context (appears on ALL pages)"
        )

        # Create manual mode monitoring (will be used if user presses 'M')
        button_task = None
        pdf_page = None

        # Define download strategies with their names
        async def chrome_pdf_wrapper(url, path):
            # Chrome PDF strategy creates its own page
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
            # Don't run manual download in the loop - it's handled separately after
            # if stop_event is set
            return None

        try_download_methods = [
            ("Chrome PDF", chrome_pdf_wrapper),
            ("Direct Download", direct_download_wrapper),
            ("From Response Body", response_body_wrapper),
            ("Manual Download", manual_fallback_wrapper),
        ]

        for method_name, method_func in try_download_methods:
            # Check if user activated manual mode - STOP ALL AUTOMATION IMMEDIATELY
            if stop_event.is_set():
                logger.info(
                    f"{self.name}: User activated manual mode - stopping all automation"
                )
                break

            logger.info(f"{self.name}: Trying method: {method_name}")

            # Pass stop_event to strategies so they can check it periodically
            try:
                # Check before starting
                if stop_event.is_set():
                    logger.info(
                        f"{self.name}: Manual mode activated, skipping {method_name}"
                    )
                    break

                # Run the method - it should check stop_event periodically
                is_downloaded = await method_func(pdf_url, output_path)

                # Check after completing
                if stop_event.is_set():
                    logger.info(
                        f"{self.name}: Manual mode activated during {method_name}"
                    )
                    break

                if is_downloaded:
                    # Success! Clean up
                    if button_task:
                        button_task.cancel()
                    if pdf_page:
                        await pdf_page.close()
                    logger.success(
                        f"{self.name}: Successfully downloaded via {method_name}"
                    )
                    return is_downloaded  # Return the actual path from the strategy
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

        # If user chose manual download or all automation failed
        if stop_event.is_set():
            # Set context flag so all strategies know we're in manual mode
            self.context._scitex_is_manual_mode = True

            logger.info(
                f"{self.name}: User chose manual download - starting monitoring"
            )
            # Cancel button task
            if button_task:
                button_task.cancel()

            # Open page for manual download if not already open
            if not pdf_page:
                pdf_page = await self.context.new_page()
                await pdf_page.goto(
                    pdf_url, timeout=30000, wait_until="domcontentloaded"
                )

            result = await self._handle_manual_download_async(
                pdf_page,
                pdf_url,
                output_path,
                doi=doi,
            )
            await pdf_page.close()
            return result

        # All methods failed - clean up
        if button_task:
            button_task.cancel()
        if pdf_page:
            await pdf_page.close()
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
        # IMPORTANT: Manual download should ONLY save to downloads dir
        # MASTER organization (8-digit IDs) is handled by storage module
        temp_downloads_dir = self.config.get_library_downloads_dir()
        final_pdfs_dir = self.config.get_library_downloads_dir()  # NOT MASTER!

        # Extract DOI from URL if not provided
        if not doi and "doi.org/" in pdf_url:
            doi = pdf_url.split("doi.org/")[-1].split("?")[0].split("#")[0]

        await browser_logger.info(
            page,
            f"{self.name}: Manual download mode activated",
        )

        # Page is already navigated to PDF URL (done in download_from_url)
        # Just show instructions
        await browser_logger.info(
            page,
            f"{self.name}: Please download the PDF manually from this page",
        )

        # Run complete manual download workflow (without showing button again)
        # The button was already shown and clicked to trigger this
        monitor = DownloadMonitorAndSync(temp_downloads_dir, final_pdfs_dir)

        # Create logger function for progress reporting (must be sync, not async)
        def log_progress(msg: str):
            logger.info(f"{self.name}: {msg}")

        # Monitor for new download with progress reporting (2 minutes)
        # Long timeouts cause process accumulation - keep it short
        temp_file = await monitor.monitor_for_new_download_async(
            timeout_sec=120,  # 2 minutes to download
            logger_func=log_progress,
        )

        if not temp_file:
            await browser_logger.error(
                page,
                f"{self.name}: No new PDF detected in downloads directory",
            )
            return None

        await browser_logger.success(
            page,
            f"{self.name}: Detected PDF: {temp_file.name} ({temp_file.stat().st_size / 1e6:.1f} MB)",
        )

        # Keep UUID filename as-is in downloads directory
        # Orchestration layer will handle metadata extraction and MASTER organization

        # Save minimal metadata header (DOI only - no PDF parsing)
        if doi:
            import json

            metadata_file = temp_file.parent / f"{temp_file.name}.meta.json"
            metadata = {
                "doi": doi,
                "pdf_url": pdf_url,
                "pdf_file": temp_file.name,
            }
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

        await browser_logger.success(
            page,
            f"{self.name}: Manual download complete - saved in downloads/",
        )

        logger.info(f"{self.name}: PDF: {temp_file}")
        if doi:
            logger.info(
                f"{self.name}: DOI: {doi} (saved in {temp_file.name}.meta.json)"
            )

        # Return the UUID file path (in downloads directory)
        return temp_file


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
    url_context = await auth_gateway.prepare_context_async(
        doi=args.doi, context=context
    )

    # ---------------------------------------
    # Step 1: URL Resolution (separate from downloading)
    # ---------------------------------------
    url_finder = ScholarURLFinder(context)

    # Use the resolved URL from auth_gateway to avoid duplicate OpenURL resolution
    resolved_url = url_context.url if url_context else None
    if resolved_url:
        logger.info(
            f"{__name__}: Using resolved URL from auth_gateway: {resolved_url}"
        )
        urls = await url_finder.find_pdf_urls(resolved_url)
    else:
        logger.info(f"{__name__}: No resolved URL, using DOI: {args.doi}")
        urls = await url_finder.find_pdf_urls(
            args.doi
        )  # Will resolve DOI internally

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
        default="~/.scitex/scholar/library/downloads/downloaded_paper.pdf",
        help="Output path for the PDF (default: ~/.scitex/scholar/library/downloads/downloaded_paper.pdf)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["stealth", "interactive"],
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

python -m scitex.scholar.download.ScholarPDFDownloader \
    --browser-mode interactive \
    --doi "10.1212/wnl.0000000000200348"


# This seems calling URL Resolution on OpenURL twice

    --doi "10.3389/fnins.2024.1417748"
    --doi "10.1016/j.clinph.2024.09.017"

"""

# EOF
