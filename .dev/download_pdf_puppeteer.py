#!/usr/bin/env python3
"""
Download PDFs using Puppeteer automation
"""

import requests
import json
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def navigate_to_pdf(url: str) -> dict:
    """Navigate to PDF URL using Puppeteer"""
    response = requests.post(
        "http://localhost:11235/puppeteer_navigate",
        json={"url": url},
        timeout=30
    )
    if response.status_code == 200:
        return response.json()
    return None

def get_pdf_info() -> dict:
    """Get information about the current page"""
    script = """(() => {
        // Check if viewing PDF
        const embedPDF = document.querySelector('embed[type="application/pdf"]');
        const iframePDF = document.querySelector('iframe[src*=".pdf"]');
        const isPDF = embedPDF || iframePDF || window.location.href.endsWith('.pdf');
        
        // For Chrome PDF viewer
        const pdfViewer = document.querySelector('pdf-viewer');
        const downloadButton = document.querySelector('[aria-label="Download"]');
        
        return {
            isPDF: !!isPDF,
            hasPDFViewer: !!pdfViewer,
            hasDownloadButton: !!downloadButton,
            url: window.location.href,
            title: document.title
        };
    })()"""
    
    response = requests.post(
        "http://localhost:11235/puppeteer_evaluate",
        json={"script": script},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        return result.get('result', {})
    return {}

def click_download() -> bool:
    """Click the download button in Chrome PDF viewer"""
    # Try to click download button
    response = requests.post(
        "http://localhost:11235/puppeteer_click",
        json={"selector": '[aria-label="Download"]'},
        timeout=30
    )
    return response.status_code == 200

def take_screenshot(name: str):
    """Take a screenshot for debugging"""
    requests.post(
        "http://localhost:11235/puppeteer_screenshot",
        json={"name": name, "width": 1200, "height": 800},
        timeout=30
    )

# Test with PMC PDF
test_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf"
logger.info(f"Testing PDF download with Puppeteer: {test_url}")

# Navigate to PDF
logger.info("Navigating to PDF...")
nav_result = navigate_to_pdf(test_url)
if nav_result:
    logger.info("Navigation successful")
    
    # Wait a bit for PDF to load
    time.sleep(3)
    
    # Get PDF info
    pdf_info = get_pdf_info()
    logger.info(f"PDF info: {json.dumps(pdf_info, indent=2)}")
    
    # Take screenshot
    take_screenshot("pdf_viewer_state")
    logger.info("Screenshot taken")
    
    if pdf_info.get('hasDownloadButton'):
        logger.info("Download button found, clicking...")
        if click_download():
            logger.info("✅ Download button clicked")
            time.sleep(2)
        else:
            logger.info("❌ Failed to click download button")
    else:
        logger.info("No download button found")
        
        # Alternative: Try to get the PDF URL from the viewer
        script = """(() => {
            // Try to find the actual PDF URL
            const embed = document.querySelector('embed[type="application/pdf"]');
            if (embed && embed.src) {
                return { pdfUrl: embed.src };
            }
            
            // Check Chrome PDF viewer
            const viewer = document.querySelector('pdf-viewer');
            if (viewer) {
                return { 
                    pdfUrl: window.location.href,
                    isChromePDFViewer: true 
                };
            }
            
            return { pdfUrl: null };
        })()"""
        
        response = requests.post(
            "http://localhost:11235/puppeteer_evaluate",
            json={"script": script},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json().get('result', {})
            logger.info(f"PDF URL result: {json.dumps(result, indent=2)}")

# Since browser automation might not work for downloads, let's try a different approach
# Let's check if we can access the parent page and find the real PDF URL
logger.info("\n=== Alternative approach: Check parent PMC page ===")

parent_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/"
logger.info(f"Navigating to parent page: {parent_url}")

nav_result = navigate_to_pdf(parent_url)
if nav_result:
    time.sleep(2)
    
    # Find PDF link on the page
    script = """(() => {
        const links = Array.from(document.querySelectorAll('a'));
        const pdfLinks = links.filter(link => {
            const href = link.href || '';
            const text = link.textContent || '';
            return href.includes('.pdf') || (text.includes('PDF') && text.includes('MB'));
        });
        
        return pdfLinks.map(link => ({
            href: link.href,
            text: link.textContent.trim(),
            download: link.download
        }));
    })()"""
    
    response = requests.post(
        "http://localhost:11235/puppeteer_evaluate", 
        json={"script": script},
        timeout=30
    )
    
    if response.status_code == 200:
        pdf_links = response.json().get('result', [])
        logger.info(f"Found {len(pdf_links)} PDF links:")
        for link in pdf_links:
            logger.info(f"  - {link}")
            
logger.info("\nNote: Browser automation has limitations for file downloads.")
logger.info("Consider using authentication cookies or proxy methods for protected PDFs.")