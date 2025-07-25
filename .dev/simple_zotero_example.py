#!/usr/bin/env python3
"""
Simple example: Using Zotero translators to get PDF URLs.
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.scitex.scholar._ZoteroTranslatorRunner import ZoteroTranslatorRunner

async def get_pdf_url(paper_url):
    """Get PDF URL for a paper using Zotero translators."""
    
    # Create runner
    runner = ZoteroTranslatorRunner()
    
    # Find the right translator
    translator = runner.find_translator_for_url(paper_url)
    if not translator:
        print(f"No translator found for {paper_url}")
        return None
    
    print(f"Using translator: {translator['label']}")
    
    # Extract PDF URLs
    pdf_urls = await runner.extract_pdf_urls_async(paper_url)
    
    if pdf_urls:
        print(f"Found PDF: {pdf_urls[0]}")
        return pdf_urls[0]
    else:
        print("No PDF found")
        return None

async def main():
    # Test with a Nature paper
    nature_doi = "10.1038/s41586-024-07487-w"
    nature_url = f"https://doi.org/{nature_doi}"
    
    print(f"Getting PDF for: {nature_url}")
    pdf_url = await get_pdf_url(nature_url)
    
    if pdf_url:
        print(f"\nYou can download the PDF from: {pdf_url}")

if __name__ == "__main__":
    asyncio.run(main())