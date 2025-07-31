#!/usr/bin/env python3
"""Simple paper download using requests and institutional access."""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import quote

# Set up session with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
})

# Papers to download (from your BibTeX)
papers = [
    {
        'id': 'Hlsemann2019QuantificationOPA',
        'title': 'Quantification of Phase-Amplitude Coupling',
        'doi': '10.3389/fnins.2019.00573',
        'pmid': '31275096'
    },
    {
        'id': 'Friston2020GenerativeMLB', 
        'title': 'Generative models, linguistic communication',
        'doi': '10.1016/j.neubiorev.2020.07.005'
    },
    {
        'id': 'Canolty2010TheFRC',
        'title': 'The functional role of cross-frequency coupling',
        'doi': '10.1016/j.tics.2010.09.001'
    }
]

def try_download_urls(paper, output_dir):
    """Try different URL patterns to download the paper."""
    
    urls_to_try = []
    
    # 1. Try Sci-Hub (if available)
    if paper.get('doi'):
        urls_to_try.extend([
            f"https://sci-hub.se/{paper['doi']}",
            f"https://sci-hub.st/{paper['doi']}",
            f"https://sci-hub.ru/{paper['doi']}"
        ])
    
    # 2. Try PubMed Central
    if paper.get('pmid'):
        urls_to_try.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/pmid/{paper['pmid']}/pdf/")
    
    # 3. Try direct publisher links
    if paper.get('doi'):
        if paper['doi'].startswith('10.3389/'):
            # Frontiers journals
            urls_to_try.append(f"https://www.frontiersin.org/articles/{paper['doi']}/pdf")
        elif paper['doi'].startswith('10.1016/'):
            # Elsevier
            pii = paper['doi'].split('/')[-1]
            urls_to_try.append(f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft")
    
    # 4. Try institutional OpenURL resolver
    if paper.get('doi'):
        openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{paper['doi']}&svc_id=fulltext"
        urls_to_try.append(openurl)
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        print(f"  Already exists: {output_path}")
        return str(output_path)
    
    for url in urls_to_try:
        print(f"  Trying: {url[:80]}...")
        try:
            response = session.get(url, timeout=30, allow_redirects=True)
            
            # Check if we got a PDF
            content_type = response.headers.get('content-type', '')
            if response.status_code == 200 and ('pdf' in content_type or response.content.startswith(b'%PDF')):
                # Save the PDF
                output_path.write_bytes(response.content)
                print(f"  ✅ Downloaded: {output_path}")
                return str(output_path)
            else:
                print(f"  Not a PDF (status: {response.status_code}, type: {content_type})")
                
        except Exception as e:
            print(f"  Failed: {str(e)[:50]}")
        
        time.sleep(1)  # Be polite
    
    return None

def main():
    """Download papers."""
    
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("Simple Paper Downloader")
    print("="*60)
    
    results = []
    
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] {paper['title']}")
        print(f"  DOI: {paper.get('doi', 'N/A')}")
        
        pdf_path = try_download_urls(paper, output_dir)
        
        if pdf_path:
            results.append({'paper': paper['id'], 'success': True, 'path': pdf_path})
        else:
            results.append({'paper': paper['id'], 'success': False})
            print(f"  ❌ Failed to download")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\nTotal: {success_count}/{len(papers)} downloaded successfully")
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['paper']}")
        if r['success']:
            print(f"   Path: {r.get('path')}")

if __name__ == "__main__":
    main()