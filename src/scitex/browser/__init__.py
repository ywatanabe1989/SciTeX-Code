#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Browser Utilities - Universal Playwright helpers organized by category
# ----------------------------------------

# Debugging utilities
from .debugging import (
    show_popup_and_capture_async,
    show_grid_async,
    highlight_element_async,
)

# PDF utilities
from .pdf import (
    detect_chrome_pdf_viewer_async,
    click_download_for_chrome_pdf_viewer_async,
)

# Interaction utilities
from .interaction import (
    click_center_async,
    click_with_fallbacks_async,
    fill_with_fallbacks_async,
)

__all__ = [
    # Debugging
    "show_popup_and_capture_async",
    "show_grid_async",
    "highlight_element_async",

    # PDF
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer_async",

    # Interaction
    "click_center_async",
    "click_with_fallbacks_async",
    "fill_with_fallbacks_async",
]

# EOF
