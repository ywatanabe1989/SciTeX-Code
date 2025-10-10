#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manual Download Fallback Strategy"""

from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar import ScholarConfig
from scitex.scholar.browser import browser_logger
from scitex.scholar.download.strategies.manual_download_utils import (
    complete_manual_download_workflow_async,
)

logger = logging.getLogger(__name__)


async def try_download_manual_async(
    context: BrowserContext,
    pdf_url: str,
    output_path: Path,
    downloader_name: str = "ScholarPDFDownloader",
    config: ScholarConfig = None,
) -> Optional[Path]:
    """Manual download fallback - STUB IMPLEMENTATION.

    This is a placeholder that returns None to indicate manual download
    is not supported in the current implementation.

    TODO: Implement manual download workflow when needed.
    """
    logger.info(f"{downloader_name}: Manual download not implemented - returning None")
    return None


# EOF
