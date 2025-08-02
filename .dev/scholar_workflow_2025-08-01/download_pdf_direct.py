#!/usr/bin/env python3
"""
Direct PDF download script
"""

import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_pdf(url: str, output_path: Path) -> bool:
    """Download PDF from URL"""
    try:
        logger.info(f"Downloading from: {url}")
        logger.info(f"Saving to: {output_path}")
        
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Successfully downloaded: {output_path.name}")
            return True
        else:
            logger.error(f"Failed to download. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error downloading: {str(e)}")
        return False

# Download the first paper
pdf_url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf"
output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/downloaded_papers")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "Hulsemann-2019-FIN.pdf"

success = download_pdf(pdf_url, output_path)
print(f"Download successful: {success}")