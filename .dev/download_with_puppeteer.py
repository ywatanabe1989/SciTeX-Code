#!/usr/bin/env python3
"""
Download paper using MCP Puppeteer for browser automation
"""

import asyncio
import time
from pathlib import Path

async def download_ai_epilepsy_with_browser():
    """Use MCP Puppeteer to download the paper."""
    
    print("=" * 80)
    print("DOWNLOADING WITH MCP PUPPETEER")
    print("=" * 80)
    
    # Paper details
    paper_title = "Artificial intelligence in epilepsy — applications and pathways to the clinic"
    paper_doi = "10.1038/s41582-024-00965-9"
    paper_url = f"https://doi.org/{paper_doi}"
    
    print(f"\nTarget paper: {paper_title}")
    print(f"DOI: {paper_doi}")
    print(f"URL: {paper_url}")
    
    # Note: This would use the MCP puppeteer tool to:
    # 1. Navigate to the paper URL
    # 2. Handle any redirects
    # 3. Look for PDF download buttons
    # 4. Click to download
    
    print("\nTo download using browser automation:")
    print("1. Navigate to:", paper_url)
    print("2. Look for 'Download PDF' or 'Access' buttons")
    print("3. Handle institutional login if needed")
    print("4. Download the PDF")
    
    return paper_url

if __name__ == "__main__":
    url = asyncio.run(download_ai_epilepsy_with_browser())
    print(f"\nReady to navigate to: {url}")