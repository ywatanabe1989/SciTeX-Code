#!/usr/bin/env python3
"""
Batch download remaining PDFs using Linux Zotero.
Direct connection without Windows proxy!
"""

import subprocess
import time
import json
from pathlib import Path

def check_zotero_running():
    """Ensure Linux Zotero is running with connector."""
    import requests
    
    try:
        response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    
    # Start Zotero if not running
    print("Starting Linux Zotero...")
    subprocess.Popen([
        '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
        '--connector-port', '23119'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for startup
    for i in range(10):
        time.sleep(2)
        try:
            response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
            if response.status_code == 200:
                print("✅ Zotero started successfully")
                return True
        except:
            continue
    
    return False

def get_all_remaining_papers():
    """Get all papers without PDFs."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers = []
    
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
                        doi = metadata.get('doi', '')
                        if doi:
                            papers.append({
                                'name': item.name,
                                'doi': doi,
                                'url': f'https://doi.org/{doi}',
                                'journal': journal,
                                'title': metadata.get('title', '')[:50]
                            })
    
    return papers

def process_batch(papers, batch_num, batch_size=10):
    """Process a batch of papers."""
    
    print(f"\n" + "=" * 60)
    print(f"BATCH {batch_num}")
    print("=" * 60)
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open papers in Chrome
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in papers]
    
    print(f"Opening {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"{i:2}. {paper['title']}")
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Loading pages...")
    time.sleep(10)
    
    # Automated save
    print("\n🤖 Starting automated save...")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    # Process each tab
    for i in range(len(papers)):
        print(f"Paper {i+1}/{len(papers)}: ", end='', flush=True)
        
        # Wait for page
        time.sleep(2)
        
        # Save with Zotero
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        print("Saving", end='', flush=True)
        
        # Wait for save
        for j in range(5):
            time.sleep(1)
            print(".", end='', flush=True)
        
        print(" ✓")
        
        # Next tab
        if i < len(papers) - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print(f"\n✅ Batch {batch_num} complete!")

def main():
    """Process all remaining papers."""
    
    print("=" * 80)
    print("BATCH PDF DOWNLOAD WITH LINUX ZOTERO")
    print("=" * 80)
    
    # Check Zotero
    if not check_zotero_running():
        print("❌ Cannot start Zotero!")
        return
    
    print("✅ Linux Zotero is running")
    print("✅ No Windows proxy needed!")
    print("✅ Direct connection: Chrome → Linux Zotero")
    
    # Get papers
    papers = get_all_remaining_papers()
    print(f"\nFound {len(papers)} papers without PDFs (excluding IEEE)")
    
    if not papers:
        print("All papers have PDFs!")
        return
    
    # Process in batches
    batch_size = 10
    num_batches = (len(papers) + batch_size - 1) // batch_size
    
    print(f"Will process in {num_batches} batches of up to {batch_size} papers")
    
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(papers))
        batch = papers[start_idx:end_idx]
        
        process_batch(batch, batch_num + 1, batch_size)
        
        if batch_num < num_batches - 1:
            print("\nWaiting 5 seconds before next batch...")
            time.sleep(5)
    
    print("\n" + "=" * 80)
    print("🎉 ALL BATCHES COMPLETE!")
    print(f"Processed {len(papers)} papers")
    print("\nCheck Linux Zotero library for downloaded PDFs")
    print("=" * 80)

if __name__ == "__main__":
    main()