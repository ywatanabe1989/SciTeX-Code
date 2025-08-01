#!/usr/bin/env python3
"""
Download PDF using Crawl4AI execute_js to handle any JavaScript/cookies
"""

import requests
import json
import logging
from pathlib import Path
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_pdf_with_crawl4ai(pdf_url: str, filename: str) -> bool:
    """Download PDF using Crawl4AI to handle JavaScript/auth"""
    
    # Use execute_js to get the PDF content
    js_data = {
        "url": pdf_url,
        "scripts": [
            # Wait for page to load
            "await new Promise(resolve => setTimeout(resolve, 2000))",
            
            # Check if we're on a PDF page
            """
            (() => {
                // Check if we're viewing a PDF
                const isPDF = document.querySelector('embed[type="application/pdf"]') || 
                             document.querySelector('iframe[src*=".pdf"]') ||
                             window.location.href.endsWith('.pdf');
                
                // Get page title and URL
                return {
                    isPDF: isPDF,
                    title: document.title,
                    url: window.location.href,
                    bodyHTML: document.body ? document.body.innerHTML.substring(0, 500) : 'No body'
                };
            })()
            """
        ]
    }
    
    try:
        logger.info(f"Fetching PDF page with Crawl4AI: {pdf_url}")
        
        response = requests.post(
            "http://localhost:11235/execute_js",
            json=js_data,
            timeout=60
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch page: {response.status_code}")
            return False
        
        result = response.json()
        
        # Check if we have the PDF
        if result.get('js_execution_result'):
            js_result = result['js_execution_result']
            logger.info(f"Page info: {json.dumps(js_result, indent=2)}")
            
            # If we're on a PDF page, we need to download it differently
            if js_result.get('isPDF'):
                logger.info("PDF page detected, attempting direct download with session cookies")
                
                # Try regular download now that Crawl4AI has established session
                return download_with_session(pdf_url, filename)
        
        return False
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False

def download_with_session(url: str, filename: str) -> bool:
    """Download with requests after Crawl4AI established session"""
    try:
        # Use a session to maintain cookies
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Save if it's a PDF
        if response.content[:4] == b'%PDF':
            output_path = Path(f"/home/ywatanabe/proj/SciTeX-Code/.dev/{filename}")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Saved PDF to: {output_path}")
            logger.info(f"File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            logger.error(f"Not a PDF. Content-Type: {response.headers.get('Content-Type')}")
            return False
            
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return False

# Alternative: Use Crawl4AI's PDF endpoint
def download_pdf_direct(pdf_url: str, filename: str) -> bool:
    """Use Crawl4AI's PDF endpoint"""
    
    pdf_data = {
        "url": pdf_url,
        "output_path": f"/home/ywatanabe/proj/SciTeX-Code/.dev/{filename}"
    }
    
    try:
        logger.info(f"Using Crawl4AI PDF endpoint for: {pdf_url}")
        
        response = requests.post(
            "http://localhost:11235/pdf",
            json=pdf_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('output_path'):
                logger.info(f"✅ PDF saved to: {result['output_path']}")
                return True
        else:
            logger.error(f"PDF generation failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"PDF download error: {str(e)}")
    
    return False

# Test both methods
test_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf"
test_filename = "Hulsemann-2019-FIN.pdf"

logger.info("=== Testing PDF download methods ===\n")

# Method 1: JavaScript execution
logger.info("Method 1: Using execute_js")
success1 = download_pdf_with_crawl4ai(test_url, test_filename)

# Method 2: Direct PDF endpoint
if not success1:
    logger.info("\nMethod 2: Using PDF endpoint")
    success2 = download_pdf_direct(test_url, test_filename)
else:
    success2 = False

if success1 or success2:
    logger.info("\n✅ PDF download successful!")
else:
    logger.info("\n❌ All methods failed")