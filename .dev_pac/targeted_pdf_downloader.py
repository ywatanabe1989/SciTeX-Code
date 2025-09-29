#!/usr/bin/env python3
"""Targeted downloader for specific missing papers with publisher-specific strategies."""

import subprocess
import time
import json
from pathlib import Path
import requests

def download_nature_paper(paper, profile_dir):
    """Download Nature/Scientific Reports papers."""
    doi = paper['doi']
    
    # Nature papers have specific patterns
    if 'rs.3.rs-' in doi:
        # This is a Research Square preprint DOI, need to get the actual paper
        print(f"  ⚠️  Preprint DOI detected: {doi}")
        # Try opening anyway
        url = f'https://doi.org/{doi}'
    else:
        # Regular Nature paper
        article_id = doi.split('/')[-1]
        if 's41593' in doi:  # Nature Neuroscience
            url = f'https://www.nature.com/articles/{article_id}'
        else:
            url = f'https://doi.org/{doi}'
    
    return url

def download_mdpi_paper(paper, profile_dir):
    """Download MDPI papers - usually open access."""
    doi = paper['doi']
    
    # MDPI pattern: https://www.mdpi.com/journal/volume/issue/article
    # Extract from DOI like 10.3390/brainsci11081066
    if '10.3390/' in doi:
        parts = doi.split('/')[-1]  # e.g., "brainsci11081066"
        
        # Map journal codes
        journal_map = {
            'brainsci': 'brainsci',
            's': 'sensors',
            'math': 'mathematics',
            'diagnostics': 'diagnostics',
            'ijms': 'ijms'
        }
        
        # Try to extract journal from the DOI
        for key in journal_map:
            if parts.startswith(key):
                journal = journal_map[key]
                # Direct PDF URL for MDPI
                pdf_url = f'https://www.mdpi.com/{parts}/pdf'
                print(f"  🎯 MDPI direct PDF: {pdf_url}")
                return pdf_url
    
    # Fallback to DOI
    return f'https://doi.org/{doi}'

def download_frontiers_paper(paper, profile_dir):
    """Download Frontiers papers - usually open access."""
    doi = paper['doi']
    
    # Frontiers pattern is straightforward
    url = f'https://doi.org/{doi}'
    
    # Could also try direct PDF
    # article_id = doi.split('/')[-1]
    # pdf_url = f'https://www.frontiersin.org/articles/{article_id}/pdf'
    
    return url

def download_peerj_paper(paper, profile_dir):
    """Download PeerJ papers - open access."""
    doi = paper['doi']
    
    # PeerJ pattern: https://peerj.com/articles/cs-523.pdf
    if 'peerj-cs' in doi:
        article_id = doi.split('.')[-1]
        pdf_url = f'https://peerj.com/articles/cs-{article_id}.pdf'
        print(f"  🎯 PeerJ direct PDF: {pdf_url}")
        return pdf_url
    
    return f'https://doi.org/{doi}'

def download_hindawi_paper(paper, profile_dir):
    """Download Hindawi papers - usually open access."""
    doi = paper['doi']
    
    # Hindawi pattern: downloads.hindawi.com/journals/...
    if '10.1155/' in doi:
        year_id = doi.split('/')[-2]
        article_id = doi.split('/')[-1]
        # Try direct PDF
        pdf_url = f'https://downloads.hindawi.com/journals/{year_id}/{article_id}.pdf'
        print(f"  🎯 Hindawi direct PDF attempt: {pdf_url}")
        return pdf_url
    
    return f'https://doi.org/{doi}'

def download_elsevier_paper(paper, profile_dir):
    """Download Elsevier papers - needs authentication."""
    doi = paper['doi']
    
    # Elsevier is complex, needs proper auth
    # For now, just open the DOI
    return f'https://doi.org/{doi}'

def get_download_strategy(paper):
    """Determine download strategy based on publisher."""
    journal = paper.get('journal', '')
    
    if 'Nature' in journal or 'Scientific Reports' in journal:
        return 'nature'
    elif 'Frontiers' in journal:
        return 'frontiers'
    elif 'MDPI' in journal or 'Sensors' in journal or 'Mathematics' in journal or 'Brain Sciences' in journal or 'Diagnostics' in journal:
        return 'mdpi'
    elif 'PeerJ' in journal:
        return 'peerj'
    elif 'Hindawi' in journal or 'Applied Bionics' in journal or 'Computational' in journal:
        return 'hindawi'
    elif 'Elsevier' in journal or 'Engineering' in journal or 'Epilepsy' in journal:
        return 'elsevier'
    else:
        return 'generic'

def download_with_chrome_batch(papers, profile_dir):
    """Download papers in batch using Chrome."""
    
    if not papers:
        return 0
    
    print(f"\n{'='*60}")
    print(f"DOWNLOADING {len(papers)} PAPERS")
    print('='*60)
    
    # Prepare URLs with strategies
    urls = []
    for paper in papers:
        strategy = get_download_strategy(paper)
        print(f"\n📄 {paper['name']}")
        print(f"   Journal: {paper['journal']}")
        print(f"   Strategy: {strategy}")
        
        if strategy == 'nature':
            url = download_nature_paper(paper, profile_dir)
        elif strategy == 'mdpi':
            url = download_mdpi_paper(paper, profile_dir)
        elif strategy == 'frontiers':
            url = download_frontiers_paper(paper, profile_dir)
        elif strategy == 'peerj':
            url = download_peerj_paper(paper, profile_dir)
        elif strategy == 'hindawi':
            url = download_hindawi_paper(paper, profile_dir)
        elif strategy == 'elsevier':
            url = download_elsevier_paper(paper, profile_dir)
        else:
            url = f"https://doi.org/{paper['doi']}"
        
        urls.append(url)
        print(f"   URL: {url}")
    
    # Kill Chrome first
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open all URLs
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    print("\n🌐 Opening all URLs in Chrome...")
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("⏳ Waiting for pages to load (20 seconds)...")
    time.sleep(20)
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                   capture_output=True)
    time.sleep(2)
    
    saved = 0
    
    # Try to save each tab
    for i, paper in enumerate(papers):
        print(f"\n📑 Tab {i+1}/{len(papers)}: {paper['name']}")
        
        # Try Zotero save
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                       capture_output=True)
        print("   Attempted Zotero save...")
        time.sleep(5)
        
        # Move to next tab
        if i < len(papers) - 1:
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                           capture_output=True)
            time.sleep(1)
    
    return saved

def main():
    """Main download function."""
    
    print("="*80)
    print("TARGETED PDF DOWNLOADER")
    print("="*80)
    
    # Load missing papers analysis
    analysis_file = Path('.dev_pac/missing_pdfs_analysis.json')
    if not analysis_file.exists():
        print("❌ Run analyze_missing_pdfs.py first!")
        return
    
    with open(analysis_file) as f:
        data = json.load(f)
    
    # Focus on priority papers first
    priority_papers = data['priority_papers']
    
    if not priority_papers:
        print("No priority papers to download")
        return
    
    print(f"\n🎯 Found {len(priority_papers)} priority papers to download")
    
    # Check Zotero
    try:
        response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
        if response.status_code != 200:
            raise Exception("Not running")
        print("✅ Linux Zotero is running")
    except:
        print("Starting Zotero...")
        subprocess.Popen([
            '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
            '--connector-port', '23119'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Process in small batches
    batch_size = 5
    
    for i in range(0, len(priority_papers), batch_size):
        batch = priority_papers[i:i+batch_size]
        download_with_chrome_batch(batch, profile_dir)
        
        if i + batch_size < len(priority_papers):
            print("\n⏰ Waiting before next batch...")
            time.sleep(5)
    
    # Sync Zotero to Scholar
    print("\n📁 Syncing Zotero → Scholar...")
    subprocess.run(['python', '.dev_pac/sync_zotero_to_scholar.py'])
    
    # Final status
    print("\n" + "="*80)
    print("CHECKING RESULTS")
    print("="*80)
    subprocess.run(['python', '.dev_pac/check_pdf_details.py'])

if __name__ == "__main__":
    main()