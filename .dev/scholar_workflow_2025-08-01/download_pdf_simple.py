#!/usr/bin/env python3
"""Simple PDF download using requests."""

import requests
from pathlib import Path

def download_pdf():
    """Download PDF directly from ScienceDirect."""
    
    # The PDF URL we found
    pdf_url = "https://www.sciencedirect.com/science/article/pii/S0149763420304668/pdfft?md5=ddcdca44eec97eab80e3d3486fe9a855&pid=1-s2.0-S0149763420304668-main.pdf"
    
    # Output path
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "Friston2020_Generative_models.pdf"
    
    print(f"Downloading PDF from: {pdf_url}")
    
    # Headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.sciencedirect.com/',
    }
    
    try:
        # Send GET request
        response = requests.get(pdf_url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            # Check if it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                # Write PDF to file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ PDF downloaded successfully to: {output_path}")
            else:
                print(f"❌ Response is not a PDF. Content-Type: {content_type}")
                print(f"Response preview: {response.text[:500]}")
        else:
            print(f"❌ Failed to download. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")

if __name__ == "__main__":
    download_pdf()