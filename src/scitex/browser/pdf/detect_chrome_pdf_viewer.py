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


async def detect_chrome_pdf_viewer_async(page):
    """
    Detect if Chrome PDF viewer is present on the page.

    Universal utility for detecting PDF viewer across any browser automation workflow.

    NOTE: Caller should wait for networkidle BEFORE calling this function.
    This function does NOT wait for networkidle to avoid redundant waits.
    """

    from ..debugging import show_popup_and_capture

    await show_popup_and_capture(page, "Detecting Chrome PDF Viewer...")

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
        await show_popup_and_capture(page, "✓ PDF viewer elements found!")
        return True
    else:
        logger.debug("PDF viewer not detected")
        await show_popup_and_capture(page, "✗ No PDF viewer elements found")
        return False


# Backward compatibility alias
detect_chrome_pdf_viewer_async = detect_chrome_pdf_viewer

# EOF
