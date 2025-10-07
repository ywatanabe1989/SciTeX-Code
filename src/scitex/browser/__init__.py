#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Browser Utilities - Universal Playwright helpers organized by category
# ----------------------------------------

# Debugging utilities
from .debugging import (
    show_popup_and_capture,
    show_grid,
    show_grid_async,
    highlight_element,
)

# PDF utilities
from .pdf import (
    detect_chrome_pdf_viewer,
    detect_chrome_pdf_viewer_async,
    click_download_for_chrome_pdf_viewer,
    click_download_for_chrome_pdf_viewer_async,
)

# Interaction utilities
from .interaction import (
    click_center,
    click_center_async,
    click_and_wait,
    click_with_fallbacks,
    fill_with_fallbacks,
)

__all__ = [
    # Debugging
    "show_popup_and_capture",
    "show_grid",
    "show_grid_async",
    "highlight_element",

    # PDF
    "detect_chrome_pdf_viewer",
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer",
    "click_download_for_chrome_pdf_viewer_async",

    # Interaction
    "click_center",
    "click_center_async",
    "click_and_wait",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]

# EOF
