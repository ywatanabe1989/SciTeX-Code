#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 10:05:53 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_detect_pdf_viewer_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_detect_pdf_viewer_async.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import log

logger = log.getLogger(__name__)


async def detect_pdf_viewer_async(page):
    from . import show_popup_message_async

    await page.wait_for_load_state("networkidle")
    await show_popup_message_async(page, "Detecting Chrome PDF Viewer...")
    detected = await page.evaluate(
        """
    () => {
        return !!(
            document.querySelector('embed[type="application/pdf"]') ||
            document.querySelector('iframe[src*=".pdf"]') ||
            document.querySelector('object[type="application/pdf"]') ||
            window.PDFViewerApplication ||
            document.querySelector('[data-testid="pdf-viewer"]')
        );
    }
    """
    )
    if detected:
        logger.debug("PDF viewer detected")
        return True
    else:
        logger.debug("PDF viewer not detected")
        return False

# EOF
