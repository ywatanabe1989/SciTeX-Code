#!/usr/bin/env python3
"""Download PDFs using OpenURL resolver for institutional access."""

import json
import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex import logging

logger = logging.getLogger(__name__)


async def download_papers_with_dois():
    """Download papers that have DOIs using OpenURL."""
    
    # Load merged data with DOIs
    with open('papers_merged_download_data.json') as f:
        papers = json.load(f)
    
    # Load DOI resolution data if available
    doi_files = list(Path('.').glob('doi_resolution_*.json'))
    doi_map = {}
    
    for doi_file in doi_files:
        try:
            with open(doi_file) as f:
                data = json.load(f)
                if 'papers' in data:
                    for key, info in data['papers'].items():
                        if info.get('status') == 'resolved' and 'doi' in info:
                            doi_map[info['title'].lower()] = info['doi']
        except:
            continue
    
    print(f"Loaded {len(doi_map)} resolved DOIs")
    
    # Find papers to download
    papers_to_download = []
    
    for paper in papers[:20]:  # First 20 papers
        # Check if we need to download
        pdf_path = Path('downloaded_papers') / paper['filename']
        if pdf_path.exists():
            continue
        
        # Try to find DOI
        doi = None
        if paper.get('doi'):
            doi = paper['doi']
        elif paper['title'].lower() in doi_map:
            doi = doi_map[paper['title'].lower()]
        
        if doi:
            papers_to_download.append({
                'title': paper['title'],
                'doi': doi,
                'filename': paper['filename'],
                'index': paper['index']
            })
    
    print(f"\nFound {len(papers_to_download)} papers with DOIs to download")
    
    # Create download URLs using OpenURL
    openurl_base = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    # Create browser script to open tabs
    browser_script = []
    browser_script.append("#!/bin/bash")
    browser_script.append("# Open papers in browser tabs for manual download")
    browser_script.append("")
    
    for paper in papers_to_download[:10]:  # First 10
        print(f"\n{'='*60}")
        print(f"Paper {paper['index']}: {paper['title']}")
        print(f"DOI: {paper['doi']}")
        print(f"Target: {paper['filename']}")
        
        # Create OpenURL
        openurl = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{paper['doi']}&svc_id=fulltext"
        print(f"OpenURL: {openurl}")
        
        browser_script.append(f"# Paper {paper['index']}: {paper['title'][:50]}...")
        browser_script.append(f"xdg-open '{openurl}'")
        browser_script.append("sleep 2  # Wait between tabs")
        browser_script.append("")
    
    # Save browser script
    script_path = Path('.dev/open_papers_in_browser.sh')
    with open(script_path, 'w') as f:
        f.write('\n'.join(browser_script))
    
    script_path.chmod(0o755)
    print(f"\n{'='*60}")
    print(f"Created browser script: {script_path}")
    print("Run this script to open papers in browser tabs:")
    print(f"  ./{script_path}")
    
    # Also create a download status report
    report = {
        'total_papers': len(papers),
        'already_downloaded': len([p for p in papers if (Path('downloaded_papers') / p['filename']).exists()]),
        'papers_with_dois': len([p for p in papers if p.get('doi') or p['title'].lower() in doi_map]),
        'papers_to_download': len(papers_to_download),
        'download_urls': [
            {
                'index': p['index'],
                'title': p['title'],
                'doi': p['doi'],
                'filename': p['filename'],
                'openurl': f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{p['doi']}&svc_id=fulltext"
            }
            for p in papers_to_download[:10]
        ]
    }
    
    with open('.dev/download_status_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nSaved download status report: .dev/download_status_report.json")


if __name__ == "__main__":
    asyncio.run(download_papers_with_dois())