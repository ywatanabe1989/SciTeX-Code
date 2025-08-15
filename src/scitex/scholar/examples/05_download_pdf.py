#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 19:54:24 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/05_download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar import ScholarPDFDownloader


async def main_async():
    # Parameters
    DOI = "10.1523/jneurosci.2929-12.2012"
    OUTPUT_DIR = "/tmp/"

    async with ScholarPDFDownloader() as downloader:
        await downloader.download_from_doi(DOI, output_dir=OUTPUT_DIR)


import asyncio

asyncio.run(main_async())

# EOF
