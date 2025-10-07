#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SciTeX Browser PDF Utilities
# ----------------------------------------

from .detect_chrome_pdf_viewer import detect_chrome_pdf_viewer_async
from .click_download_for_chrome_pdf_viewer import click_download_for_chrome_pdf_viewer_async

__all__ = [
    "detect_chrome_pdf_viewer_async",
    "click_download_for_chrome_pdf_viewer_async",
]

# EOF
