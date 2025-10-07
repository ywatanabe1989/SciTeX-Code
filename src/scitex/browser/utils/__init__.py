#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Browser Utilities - Universal Playwright helpers
# ----------------------------------------

from .show_popup_and_capture import show_popup_and_capture
from .detect_chrome_pdf_viewer import detect_chrome_pdf_viewer, detect_chrome_pdf_viewer_async
from .click_download_for_chrome_pdf_viewer import (
    click_download_for_chrome_pdf_viewer,
    click_download_for_chrome_pdf_viewer_async,
)
from .click_center import click_center, click_center_async
from .show_grid import show_grid, show_grid_async
from .click_and_wait import click_and_wait
from .highlight_element import highlight_element
from .click_with_fallbacks import click_with_fallbacks
from .fill_with_fallbacks import fill_with_fallbacks

__all__ = [
    # Visual debugging
    "show_popup_and_capture",
    "show_grid",
    "show_grid_async",  # Backward compatibility
    "highlight_element",

    # PDF viewer utilities
    "detect_chrome_pdf_viewer",
    "detect_chrome_pdf_viewer_async",  # Backward compatibility
    "click_download_for_chrome_pdf_viewer",
    "click_download_for_chrome_pdf_viewer_async",  # Backward compatibility

    # Click/interaction utilities
    "click_center",
    "click_center_async",  # Backward compatibility
    "click_and_wait",
    "click_with_fallbacks",
    "fill_with_fallbacks",
]

# EOF
