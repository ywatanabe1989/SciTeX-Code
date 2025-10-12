#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF Download Strategies

This module contains different strategies for downloading PDFs from academic publishers.
Each strategy is tried in sequence until one succeeds.
"""

# Download strategies
from .chrome_pdf_viewer import try_download_chrome_pdf_viewer_async
from .direct_download import try_download_direct_async
from .response_body import try_download_response_body_async
from .manual_download_fallback import try_download_manual_async

# Manual download utilities
from .manual_download_utils import (
    DownloadMonitorAndSync,
    FlexibleFilenameGenerator,
    show_stop_automation_button_async,
    show_manual_download_button_async,
    complete_manual_download_workflow_async,
)

__all__ = [
    # Download strategies
    "try_download_chrome_pdf_viewer_async",
    "try_download_direct_async",
    "try_download_response_body_async",
    "try_download_manual_async",
    # Manual download utilities
    "DownloadMonitorAndSync",
    "FlexibleFilenameGenerator",
    "show_stop_automation_button_async",
    "show_manual_download_button_async",
    "complete_manual_download_workflow_async",
]

# EOF
