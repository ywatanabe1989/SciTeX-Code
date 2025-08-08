#!/usr/bin/env python3
"""
Download remaining accessible papers (non-IEEE) using direct download methods.
Focus on open access and journals with known patterns.
"""

import json
import requests
import time
from pathlib import Path

def get_remaining_papers():
    """Get list of papers without PDFs (excluding IEEE)."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers_to_download = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if not pdf_files and metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:  # Skip IEEE
                        papers_to_download.append({
                            'name': item.name,
                            'target_dir': target_dir,
                            'title': metadata.get('title', ''),
                            'doi': metadata.get('doi', ''),
                            'journal': journal,
                            'year': metadata.get('year', '')
                        })
    
    return papers_to_download

def try_download_pdf(paper):
    """Try various methods to download PDF."""
    doi = paper['doi']
    journal = paper['journal'].lower()
    target_dir = paper['target_dir']
    
    if not doi:
        return False
    
    # Headers for requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    pdf_url = None
    
    # Try different patterns based on journal
    if 'peerj' in journal:
        # PeerJ pattern
        article_id = doi.split('/')[-1]
        pdf_url = f'https://peerj.com/articles/cs-{article_id.split("-")[-1]}.pdf'
    
    elif 'nature communications' in journal:
        # Nature Communications (open access)
        article_id = doi.split('/')[-1]
        pdf_url = f'https://www.nature.com/articles/{article_id}.pdf'
    
    elif 'bmc' in journal or 'biomed' in journal:
        # BMC journals
        pdf_url = f'https://doi.org/{doi}/pdf'
    
    elif 'mdpi' in journal or 'sensors' in journal or 'mathematics' in journal or 'diagnostics' in journal:
        # MDPI journals (Sensors, Mathematics, Diagnostics, etc.)
        # These often have complex patterns, try the DOI redirect
        pdf_url = f'https://www.mdpi.com/{doi.split("/")[-1]}/pdf'
    
    elif 'hindawi' in journal or 'computational' in journal or 'applied bionics' in journal:
        # Hindawi journals
        article_id = doi.split('/')[-1]
        pdf_url = f'https://downloads.hindawi.com/journals/{article_id}.pdf'
    
    elif 'eurasip' in journal:
        # EURASIP journals
        pdf_url = f'https://asp-eurasipjournals.springeropen.com/track/pdf/{doi}'
    
    if pdf_url:
        print(f"  Trying: {pdf_url}")
        try:
            response = requests.get(pdf_url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                # Save PDF
                pdf_path = target_dir / f"{paper['name'].split('-')[0]}-{paper['year']}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ Downloaded: {pdf_path.name}")
                return True
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:50]}")
    
    return False

def main():
    print("=" * 80)
    print("DOWNLOADING REMAINING ACCESSIBLE PAPERS")
    print("=" * 80)
    
    papers = get_remaining_papers()
    print(f"Found {len(papers)} papers to download (excluding IEEE)\n")
    
    success_count = 0
    
    # Group by journal for better organization
    journals = {}
    for paper in papers:
        journal = paper['journal']
        if journal not in journals:
            journals[journal] = []
        journals[journal].append(paper)
    
    # Try downloading by journal
    for journal, journal_papers in journals.items():
        print(f"\n{journal} ({len(journal_papers)} papers)")
        print("-" * 40)
        
        for paper in journal_papers:
            print(f"\n{paper['name']}")
            print(f"  DOI: {paper['doi']}")
            
            if try_download_pdf(paper):
                success_count += 1
                time.sleep(1)  # Be polite to servers
    
    print("\n" + "=" * 80)
    print(f"RESULTS: Downloaded {success_count} of {len(papers)} papers")
    print("=" * 80)

if __name__ == "__main__":
    main()