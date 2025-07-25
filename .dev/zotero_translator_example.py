#!/usr/bin/env python3
"""
Example showing how to use Zotero JavaScript translators from Python.

Zotero translators are JavaScript files that know how to extract bibliographic
data and PDF URLs from academic websites. This example shows how to run them
in a controlled browser environment using Playwright.
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.scitex.scholar._ZoteroTranslatorRunner import ZoteroTranslatorRunner

async def demo_zotero_translator():
    """Demonstrate using Zotero translators to extract PDF URLs."""
    
    print("=" * 80)
    print("ZOTERO TRANSLATOR EXAMPLE")
    print("=" * 80)
    
    # Initialize the translator runner
    runner = ZoteroTranslatorRunner()
    
    # Example 1: Nature paper
    nature_url = "https://www.nature.com/articles/s41586-024-07487-w"
    print(f"\n1. Testing Nature paper: {nature_url}")
    
    # Find the right translator for this URL
    translator = runner.find_translator_for_url(nature_url)
    if translator:
        print(f"   Found translator: {translator['label']}")
        
        # Extract PDF URLs using the translator
        pdf_urls = await runner.extract_pdf_urls_async(nature_url)
        print(f"   Found {len(pdf_urls)} PDF URLs:")
        for url in pdf_urls:
            print(f"   - {url}")
    else:
        print("   No translator found for this URL")
    
    # Example 2: arXiv paper
    arxiv_url = "https://arxiv.org/abs/2401.00001"
    print(f"\n2. Testing arXiv paper: {arxiv_url}")
    
    translator = runner.find_translator_for_url(arxiv_url)
    if translator:
        print(f"   Found translator: {translator['label']}")
        
        # Extract full metadata (not just PDFs)
        metadata = await runner.run_translator_async(arxiv_url, translator)
        if metadata:
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Authors: {', '.join(metadata.get('authors', []))}")
            print(f"   Abstract: {metadata.get('abstract', '')[:100]}...")
            
            # Get PDF URLs from metadata
            pdf_urls = await runner.extract_pdf_urls_async(arxiv_url)
            print(f"   PDF URLs: {pdf_urls}")
    
    # Example 3: PubMed paper
    pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/38592456/"
    print(f"\n3. Testing PubMed paper: {pubmed_url}")
    
    translator = runner.find_translator_for_url(pubmed_url)
    if translator:
        print(f"   Found translator: {translator['label']}")
        pdf_urls = await runner.extract_pdf_urls_async(pubmed_url)
        print(f"   Found {len(pdf_urls)} PDF URLs")
    
    print("\n" + "=" * 80)
    print("HOW IT WORKS:")
    print("=" * 80)
    print("""
1. TRANSLATOR SELECTION:
   - Each website has a specific translator (e.g., Nature.js, arXiv.js)
   - Translators define URL patterns they can handle
   - Runner finds the right translator based on the URL

2. BROWSER ENVIRONMENT:
   - Uses Playwright to create a headless Chromium browser
   - Injects a "Zotero shim" - fake Zotero object that translators expect
   - Navigates to the paper URL in the browser

3. JAVASCRIPT EXECUTION:
   - Loads the translator JavaScript code
   - Executes it in the browser context
   - Translator interacts with the page DOM to find data

4. DATA EXTRACTION:
   - Translator populates window._zoteroItems with results
   - Python retrieves this data from the browser
   - Extracts PDF URLs from attachment items

5. KEY COMPONENTS IN SCITEX:
   - _ZoteroTranslatorRunner.py: Main runner class
   - _create_zotero_shim(): Creates fake Zotero environment
   - find_translator_for_url(): Selects appropriate translator
   - run_translator(): Executes translator in browser
   - extract_pdf_urls(): Gets PDF URLs from results
    """)

if __name__ == "__main__":
    asyncio.run(demo_zotero_translator())