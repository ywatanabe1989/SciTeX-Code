#!/usr/bin/env python3
"""
Extract PDF URLs using Crawl4AI
"""

import requests
import json
import re
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_pdf_urls_from_pubmed(pubmed_url: str) -> dict:
    """Extract PDF URLs from a PubMed page using Crawl4AI"""
    
    # Get the page content as markdown
    md_data = {
        "url": pubmed_url,
        "f": "raw",  # Get raw content to find all links
        "c": "0"
    }
    
    try:
        response = requests.post(
            "http://localhost:11235/md",
            json=md_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch page: {response.status_code}")
            return {}
        
        result = response.json()
        content = result.get('markdown', '')
        
        # Extract links and metadata
        links = result.get('links', {})
        internal_links = links.get('internal', [])
        external_links = links.get('external', [])
        
        # Look for PDF-related links
        pdf_urls = []
        pmc_urls = []
        
        # Check all links
        all_links = internal_links + external_links
        for link in all_links:
            href = link.get('href', '')
            text = link.get('text', '').lower()
            
            # PMC links
            if 'pmc.ncbi.nlm.nih.gov' in href or '/pmc/articles/' in href:
                pmc_urls.append(href)
                logger.info(f"Found PMC link: {href}")
            
            # Direct PDF links
            if href.endswith('.pdf'):
                pdf_urls.append(href)
                logger.info(f"Found PDF link: {href}")
            
            # PDF-related text
            if 'pdf' in text or 'full text' in text or 'free article' in text:
                logger.info(f"Found PDF-related link: {text} -> {href}")
        
        # Extract from content using regex
        pmc_pattern = r'PMC\d+'
        pmc_matches = re.findall(pmc_pattern, content)
        for pmc_id in pmc_matches:
            pmc_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc_id}/"
            if pmc_url not in pmc_urls:
                pmc_urls.append(pmc_url)
                logger.info(f"Found PMC ID in content: {pmc_id}")
        
        return {
            'pmc_urls': pmc_urls,
            'pdf_urls': pdf_urls,
            'all_links': len(all_links)
        }
        
    except Exception as e:
        logger.error(f"Error processing {pubmed_url}: {str(e)}")
        return {}

def process_pmc_page(pmc_url: str) -> dict:
    """Process a PMC page to find PDF download link"""
    
    md_data = {
        "url": pmc_url,
        "f": "fit",
        "c": "0"
    }
    
    try:
        response = requests.post(
            "http://localhost:11235/md",
            json=md_data,
            timeout=30
        )
        
        if response.status_code != 200:
            return {}
        
        result = response.json()
        links = result.get('links', {})
        
        # Look for PDF download links
        pdf_urls = []
        for link in links.get('internal', []) + links.get('external', []):
            href = link.get('href', '')
            if href.endswith('.pdf') or '/pdf/' in href:
                pdf_urls.append(href)
                logger.info(f"Found PDF in PMC: {href}")
        
        return {'pdf_urls': pdf_urls}
        
    except Exception as e:
        logger.error(f"Error processing PMC page: {str(e)}")
        return {}

# Test with sample papers
test_papers = [
    {
        "title": "Quantification of Phase-Amplitude Coupling",
        "pubmed_url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096"
    },
    {
        "title": "Measuring phase-amplitude coupling",
        "pubmed_url": "https://www.ncbi.nlm.nih.gov/pubmed/20463205"
    }
]

logger.info("=== Testing PDF extraction with Crawl4AI ===\n")

for paper in test_papers:
    logger.info(f"Processing: {paper['title']}")
    logger.info(f"PubMed URL: {paper['pubmed_url']}")
    
    # Extract from PubMed page
    result = extract_pdf_urls_from_pubmed(paper['pubmed_url'])
    
    if result.get('pmc_urls'):
        logger.info(f"Found {len(result['pmc_urls'])} PMC links")
        
        # Process first PMC link
        pmc_url = result['pmc_urls'][0]
        logger.info(f"\nProcessing PMC page: {pmc_url}")
        pmc_result = process_pmc_page(pmc_url)
        
        if pmc_result.get('pdf_urls'):
            logger.info(f"✅ Found PDF URLs: {pmc_result['pdf_urls']}")
        else:
            logger.warning("❌ No PDF URLs found in PMC page")
    else:
        logger.warning("No PMC links found")
    
    logger.info("-" * 80 + "\n")

logger.info("Test complete!")