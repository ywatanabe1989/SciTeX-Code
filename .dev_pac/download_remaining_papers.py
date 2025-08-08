#!/usr/bin/env python3
"""Download remaining 17 papers using all available methods."""

import subprocess
import json
from pathlib import Path
import time

def download_with_authenticated_chrome(papers):
    """Use authenticated Chrome for harder papers."""
    
    if not papers:
        return
    
    print(f"\n{'='*60}")
    print(f"AUTHENTICATED CHROME DOWNLOAD - {len(papers)} papers")
    print('='*60)
    
    # Kill Chrome first
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    for paper in papers:
        print(f"\n📄 {paper['name']}")
        print(f"   Journal: {paper['journal']}")
        print(f"   DOI: {paper['doi']}")
        
        url = f"https://doi.org/{paper['doi']}"
        
        # Open in Chrome with auth
        args = [
            'google-chrome',
            f'--user-data-dir={profile_dir}',
            '--profile-directory=Profile 1',
            url
        ]
        
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("   ⏳ Waiting for page to load...")
        time.sleep(15)
        
        # Focus Chrome
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                       capture_output=True)
        time.sleep(1)
        
        # Try Zotero save
        print("   💾 Attempting Zotero save...")
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                       capture_output=True)
        time.sleep(8)
        
        # Close tab
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+w'], 
                       capture_output=True)
        time.sleep(2)

def try_hindawi_variations(paper, target_dir):
    """Try multiple Hindawi journal codes."""
    
    doi = paper['doi']
    if '10.1155/' not in doi:
        return False
    
    year = doi.split('/')[-2]
    article_id = doi.split('/')[-1]
    
    # Common Hindawi journal codes
    journal_codes = [
        'cin',  # Computational Intelligence and Neuroscience
        'abb',  # Applied Bionics and Biomechanics
        'cmmm', # Computational and Mathematical Methods in Medicine
        'bmri', # BioMed Research International
        'np',   # Neural Plasticity
    ]
    
    for code in journal_codes:
        url = f'https://downloads.hindawi.com/journals/{code}/{year}/{article_id}.pdf'
        print(f"   🎯 Trying Hindawi {code}: {url}")
        
        pdf_path = target_dir / f"{paper['name']}.pdf"
        
        args = [
            'wget',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0',
            '--timeout=15',
            '--tries=1',
            '-O', str(pdf_path),
            url
        ]
        
        result = subprocess.run(args, capture_output=True, text=True)
        
        if result.returncode == 0 and pdf_path.exists():
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            if size_mb > 0.05:
                print(f"   ✅ SUCCESS with {code}! Downloaded {size_mb:.1f} MB")
                return True
        
        # Clean up failed download
        if pdf_path.exists():
            pdf_path.unlink()
    
    return False

def main():
    """Download remaining papers."""
    
    print("="*80)
    print("DOWNLOADING REMAINING PAPERS")
    print("="*80)
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    
    # Get remaining papers
    remaining = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                pdfs = list(target.glob('*.pdf'))
                
                if not pdfs:
                    metadata_file = target / 'metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        journal = metadata.get('journal', '')
                        
                        # Skip IEEE
                        if 'IEEE' in journal:
                            continue
                        
                        doi = metadata.get('doi', '')
                        if doi:
                            remaining.append({
                                'name': item.name,
                                'journal': journal,
                                'doi': doi,
                                'target_dir': target
                            })
    
    print(f"\n📊 Found {len(remaining)} papers still without PDFs (excluding IEEE)")
    
    # Categorize
    hindawi_papers = []
    elsevier_papers = []
    other_papers = []
    
    for paper in remaining:
        journal = paper['journal']
        
        if 'Hindawi' in journal or 'Computational Intelligence' in journal or 'Applied Bionics' in journal or 'Computational and Mathematical' in journal:
            hindawi_papers.append(paper)
        elif 'Elsevier' in journal or 'Engineering' in journal or 'Epilepsy' in journal or 'Progress' in journal or 'Neural Engineering' in journal:
            elsevier_papers.append(paper)
        else:
            other_papers.append(paper)
    
    print(f"\n  Hindawi: {len(hindawi_papers)}")
    print(f"  Elsevier: {len(elsevier_papers)}")
    print(f"  Other: {len(other_papers)}")
    
    downloaded = 0
    
    # Try Hindawi papers with variations
    print(f"\n{'='*60}")
    print("HINDAWI PAPERS")
    print('='*60)
    
    for paper in hindawi_papers:
        print(f"\n📄 {paper['name']}")
        if try_hindawi_variations(paper, paper['target_dir']):
            downloaded += 1
    
    # Try authenticated Chrome for Elsevier and others
    print(f"\n{'='*60}")
    print("ELSEVIER & OTHER PAPERS")
    print('='*60)
    
    # Check Zotero
    try:
        import requests
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
    
    # Process Elsevier and others with authenticated Chrome
    all_hard_papers = elsevier_papers + other_papers
    download_with_authenticated_chrome(all_hard_papers)
    
    # Sync Zotero
    print("\n📁 Syncing Zotero → Scholar...")
    subprocess.run(['python', '.dev_pac/sync_zotero_to_scholar.py'])
    
    # Final status
    print("\n" + "="*80)
    print("FINAL STATUS")
    print("="*80)
    subprocess.run(['python', '.dev_pac/check_pdf_details.py'])

if __name__ == "__main__":
    main()