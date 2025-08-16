#!/usr/bin/env python3
"""Download PAC papers using scholar module."""

import asyncio
import json
import re
from pathlib import Path
from pprint import pprint
import sys
sys.path.append('/home/ywatanabe/proj/scitex_repo/src')

from scitex.scholar import ScholarAuthManager, ScholarBrowserManager, ScholarURLFinder
from scitex.logging import getLogger

logger = getLogger(__name__)

async def process_paper_async(url_finder, paper_info):
    """Process a single paper to find URLs."""
    try:
        # Extract DOI from URL if available
        doi = None
        if 'doi.org' in paper_info['url']:
            doi = paper_info['url'].split('doi.org/')[-1]
        elif 'doi=' in paper_info['url']:
            doi = paper_info['url'].split('doi=')[-1].split('&')[0]
        
        if not doi:
            logger.warning(f"No DOI found for: {paper_info['title'][:50]}")
            return None
            
        logger.info(f"Processing DOI: {doi} for {paper_info['title'][:50]}")
        
        urls = await url_finder.find_urls(doi=doi)
        return {
            'paper': paper_info,
            'doi': doi,
            'urls': urls
        }
    except Exception as e:
        logger.error(f"Error processing {paper_info['title'][:50]}: {e}")
        return None

async def main_async():
    # Parse bibtex file
    logger.info("Parsing bibtex file...")
    bib_file = '/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/papers.bib'
    with open(bib_file, 'r') as f:
        content = f.read()
    
    # Extract papers
    entries = content.split('@')[1:]
    papers = []
    
    for entry in entries:
        lines = entry.strip().split('\n')
        
        title = ''
        author = ''
        year = ''
        journal = ''
        url = ''
        
        for line in lines[1:]:
            if 'title=' in line:
                match = re.search(r'title=\{([^}]+)\}', line)
                if match:
                    title = match.group(1)
            elif 'author=' in line:
                match = re.search(r'author=\{([^}]+)\}', line)
                if match:
                    author = match.group(1)
            elif 'year=' in line:
                match = re.search(r'year=\{(\d+)\}', line)
                if match:
                    year = match.group(1)
            elif 'journal=' in line:
                match = re.search(r'journal=\{([^}]+)\}', line)
                if match:
                    journal = match.group(1)
            elif 'url=' in line:
                match = re.search(r'url=\{([^}]+)\}', line)
                if match:
                    url = match.group(1)
        
        if title and url:
            papers.append({
                'title': title,
                'author': author,
                'year': year,
                'journal': journal,
                'url': url
            })
    
    logger.info(f"Found {len(papers)} papers in bibtex")
    
    # Initialize browser
    logger.info("Initializing authenticated browser...")
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    
    # Create URL finder
    url_finder = ScholarURLFinder(context)
    
    # Process first 5 papers as test
    results = []
    for paper in papers[:5]:
        logger.info(f"Processing: {paper['title'][:60]}...")
        result = await process_paper_async(url_finder, paper)
        if result:
            results.append(result)
            
            # Save result
            output_file = f"pac_collections/dev/paper_{len(results):03d}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.success(f"Saved to {output_file}")
    
    # Summary
    logger.info(f"Successfully processed {len(results)} papers")
    
    # Close browser
    await context.close()
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main_async())