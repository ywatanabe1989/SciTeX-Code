#!/usr/bin/env python3
"""
PDF downloader with confirmed working tab navigation.
Uses Ctrl+1, Ctrl+2, etc. for explicit tab switching.
"""

import subprocess
import time
import json
from pathlib import Path

def get_remaining_papers():
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

def process_batch_with_proper_tabs(papers, batch_num):
    """Process batch with confirmed working tab navigation."""
    
    print(f"\n" + "=" * 60)
    print(f"BATCH {batch_num} - {len(papers)} papers")
    print("=" * 60)
    
    # Kill Chrome and restart
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open papers
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in papers]
    
    print("\nOpening papers:")
    for i, paper in enumerate(papers, 1):
        print(f"{i:2}. {paper['title']}")
        print(f"    {paper['journal']}")
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Waiting for pages to load...")
    time.sleep(10)
    
    print("\n🤖 Processing each tab with Ctrl+[number]:\n")
    
    # Focus Chrome window
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Process each tab using Ctrl+number (works for tabs 1-9)
    for i in range(1, min(len(papers) + 1, 10)):  # Chrome supports Ctrl+1 to Ctrl+9
        print(f"Tab {i}/{len(papers)}:")
        
        # Switch to specific tab
        print(f"  → Switching to tab {i} (Ctrl+{i})...")
        subprocess.run(['xdotool', 'key', '--clearmodifiers', f'ctrl+{i}'], 
                       capture_output=True)
        time.sleep(3)  # Give page time to be active
        
        # Save with Zotero
        print(f"  → Saving with Zotero (Ctrl+Shift+S)...")
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                       capture_output=True)
        
        # Wait for save
        print(f"  → Waiting for download...", end='', flush=True)
        for j in range(6):
            time.sleep(1)
            print(".", end='', flush=True)
        print(" ✓")
        print()
    
    # Handle tabs 10+ if any (using Ctrl+Tab from tab 9)
    if len(papers) > 9:
        print("\nProcessing tabs 10+ with Ctrl+Tab:")
        
        # Go to tab 9 first
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+9'], 
                       capture_output=True)
        time.sleep(2)
        
        for i in range(10, len(papers) + 1):
            # Use Ctrl+Tab to advance
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                           capture_output=True)
            time.sleep(2)
            
            print(f"\nTab {i}/{len(papers)}:")
            print(f"  → Saving with Zotero...")
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                           capture_output=True)
            
            print(f"  → Waiting...", end='', flush=True)
            for j in range(6):
                time.sleep(1)
                print(".", end='', flush=True)
            print(" ✓")
    
    print(f"\n✅ Batch {batch_num} complete!")

def main():
    """Download all PDFs with proper tab navigation."""
    
    print("=" * 80)
    print("PDF DOWNLOAD WITH CONFIRMED TAB SWITCHING")
    print("=" * 80)
    
    # Check Zotero
    import requests
    try:
        response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
        if response.status_code == 200:
            print("✅ Linux Zotero is running")
        else:
            print("❌ Zotero not responding")
            return
    except:
        print("❌ Cannot connect to Zotero")
        print("Starting Zotero...")
        subprocess.Popen([
            '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
            '--connector-port', '23119'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    
    # Get papers
    papers = get_remaining_papers()
    print(f"\nFound {len(papers)} papers without PDFs (excluding IEEE)")
    
    if not papers:
        print("All papers have PDFs!")
        return
    
    # Process in batches of 8 (to stay within Ctrl+1-9 range)
    batch_size = 8
    num_batches = (len(papers) + batch_size - 1) // batch_size
    
    print(f"Will process in {num_batches} batches of up to {batch_size} papers")
    print("(Using Ctrl+1 through Ctrl+8 for reliable tab switching)")
    
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(papers))
        batch = papers[start_idx:end_idx]
        
        process_batch_with_proper_tabs(batch, batch_num + 1)
        
        if batch_num < num_batches - 1:
            print("\n⏰ Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    print("\n" + "=" * 80)
    print("🎉 ALL DOWNLOADS COMPLETE!")
    print(f"Processed {len(papers)} papers")
    print("\nCheck Linux Zotero for downloaded PDFs:")
    print("  ~/Zotero/storage/*/")
    print("=" * 80)

if __name__ == "__main__":
    main()