#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:07:59 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/pdf/detect_chrome_pdf_viewer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/pdf/detect_chrome_pdf_viewer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

from scitex import logging

logger = logging.getLogger(__name__)


async def detect_chrome_pdf_viewer_async(page, verbose: bool = False):
    """
    Detect if Chrome PDF viewer is present on the page.

    Universal utility for detecting PDF viewer across any browser automation workflow.

    NOTE: Caller should wait for networkidle BEFORE calling this function.
    This function does NOT wait for networkidle to avoid redundant waits.

    Args:
        page: Playwright page object
        verbose: Enable visual feedback via popup system (default False)

    Returns:
        bool: True if PDF viewer detected, False otherwise
    """

    from ..debugging import browser_logger

    if verbose:
        await browser_logger.debug(page, "Detecting Chrome PDF Viewer...")

    # Try multiple detection methods
    detected = await page.evaluate(
        """
    () => {
        // Method 1: Standard PDF embed/iframe/object
        const embedPDF = document.querySelector('embed[type="application/pdf"]');
        const iframePDF = document.querySelector('iframe[src*=".pdf"]');
        const objectPDF = document.querySelector('object[type="application/pdf"]');

        // Method 2: Chrome's built-in PDF viewer
        const chromeViewer = window.PDFViewerApplication;

        // Method 3: Common PDF viewer attributes
        const pdfViewerDiv = document.querySelector('[data-testid="pdf-viewer"]');

        // Method 4: Check if there's a PDF plugin
        const pdfPlugin = navigator.mimeTypes['application/pdf'];

        // Method 5: Check for IEEE-specific PDF viewer elements
        const ieeePDFViewer = document.querySelector('#pdfViewer') ||
                              document.querySelector('.pdf-viewer') ||
                              document.querySelector('[id*="pdf"]') ||
                              document.querySelector('[class*="pdf-viewer"]');

        // Method 6: Check if main frame contains PDF content
        const contentType = document.contentType || document.mimeType;
        const isPDFContent = contentType === 'application/pdf';

        console.log('PDF Detection Results:', {
            embedPDF: !!embedPDF,
            iframePDF: !!iframePDF,
            objectPDF: !!objectPDF,
            chromeViewer: !!chromeViewer,
            pdfViewerDiv: !!pdfViewerDiv,
            pdfPlugin: !!pdfPlugin,
            ieeePDFViewer: !!ieeePDFViewer,
            isPDFContent: isPDFContent
        });

        return !!(
            embedPDF || iframePDF || objectPDF ||
            chromeViewer || pdfViewerDiv || pdfPlugin ||
            ieeePDFViewer || isPDFContent
        );
    }
    """
    )

    if detected:
        logger.debug("PDF viewer detected")
        if verbose:
            await browser_logger.success(page, "✓ PDF viewer elements found!")
        return True
    else:
        logger.debug("PDF viewer not detected")
        if verbose:
            await browser_logger.debug(page, "✗ No PDF viewer elements found")
        return False


def main(args):
    """Demonstrate detect_chrome_pdf_viewer functionality."""
    import asyncio
    from playwright.async_api import async_playwright
    from ..debugging import browser_logger

    async def demo():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            await browser_logger.debug(
                page, "PDF Detection: Starting demo", verbose=True
            )

            # Navigate to a PDF file
            test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
            await page.goto(test_pdf_url, timeout=30000)

            await browser_logger.debug(
                page, "Waiting for page to load...", verbose=True
            )

            await page.wait_for_load_state("networkidle", timeout=10000)

            # Detect PDF viewer
            detected = await detect_chrome_pdf_viewer_async(page, verbose=True)

            if detected:
                logger.success("PDF viewer detected successfully")
            else:
                logger.debug("No PDF viewer detected (this may be expected)")

            await browser_logger.debug(
                page, "✓ Demo complete", verbose=True
            )

            await asyncio.sleep(2)
            await browser.close()

    asyncio.run(demo())
    return 0


def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description="PDF viewer detection demo")
    return parser.parse_args()


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

# python -m scitex.browser.pdf.detect_chrome_pdf_viewer

# EOF
