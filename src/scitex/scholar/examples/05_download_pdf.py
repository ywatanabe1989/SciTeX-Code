#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 19:59:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging
from scitex.scholar.download import PDFDownloader

logger = logging.getLogger(__name__)


async def main(doi):
    pdf_downloader = PDFDownloader()
    await pdf_downloader.download_from_doi(doi)


import asyncio

asyncio.run(main("10.1523/jneurosci.2929-12.2012"))

# EOF
