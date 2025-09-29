#!/usr/bin/env python3
"""
Download next batch of papers that don't have PDFs yet.
"""

import json
import subprocess
import time
from pathlib import Path

def get_remaining_papers():
    """Get papers without PDFs (excluding IEEE)."""
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

def open_batch_in_chrome(papers, start_idx=0, batch_size=15):
    """Open a batch of papers in Chrome."""
    
    batch = papers[start_idx:start_idx + batch_size]
    
    if not batch:
        print("No more papers to process!")
        return False
    
    print(f"\nOpening batch {start_idx//batch_size + 1} ({len(batch)} papers)")
    print("=" * 60)
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Prepare URLs
    urls = [p['url'] for p in batch]
    
    # Show what we're opening
    for i, paper in enumerate(batch, 1):
        print(f"{i:2}. {paper['title']}")
        print(f"    {paper['journal']}")
    
    # Launch Chrome
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Waiting for Chrome to load pages...")
    time.sleep(10)
    
    return True

def run_automated_save(num_tabs):
    """Run the automated save process."""
    
    print("\n" + "=" * 60)
    print("STARTING AUTOMATED SAVE")
    print("=" * 60)
    print("\n⚠️  DO NOT TOUCH KEYBOARD/MOUSE!\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    successful = 0
    
    for i in range(num_tabs):
        print(f"Tab {i+1}/{num_tabs}: ", end='', flush=True)
        
        # Wait for page
        time.sleep(3)
        
        # Save with Zotero
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        print("Saving", end='', flush=True)
        
        # Wait for save (longer for PDFs)
        for j in range(6):
            time.sleep(1)
            print(".", end='', flush=True)
        
        print(" ✓")
        successful += 1
        
        # Next tab
        if i < num_tabs - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    return successful

def main():
    """Process all remaining papers in batches."""
    
    print("=" * 80)
    print("DOWNLOAD REMAINING PAPERS - BATCH PROCESSOR")
    print("=" * 80)
    
    # Get remaining papers
    papers = get_remaining_papers()
    total_remaining = len(papers)
    
    print(f"\nFound {total_remaining} papers without PDFs (excluding IEEE)")
    
    if total_remaining == 0:
        print("All accessible papers have PDFs!")
        return
    
    batch_size = 15
    num_batches = (total_remaining + batch_size - 1) // batch_size
    
    print(f"Will process in {num_batches} batches of up to {batch_size} papers each")
    
    # Process each batch
    for batch_num in range(num_batches):
        start_idx = batch_num * batch_size
        
        print(f"\n" + "=" * 80)
        print(f"BATCH {batch_num + 1} of {num_batches}")
        print("=" * 80)
        
        # Open batch in Chrome
        if not open_batch_in_chrome(papers, start_idx, batch_size):
            break
        
        # Wait for user confirmation
        print("\n✅ Chrome opened with papers")
        print("📋 Check that:")
        print("   - Zotero Desktop is running")
        print("   - Zotero WSL Proxy is active")
        print("   - Papers are loaded in Chrome")
        
        response = input("\nReady to start automated save? (y/n/skip): ").lower()
        
        if response == 'y':
            # Run automation
            batch_papers = min(batch_size, total_remaining - start_idx)
            saved = run_automated_save(batch_papers)
            print(f"\n✅ Batch complete! Attempted to save {saved} papers")
            
            # Wait before next batch
            if batch_num < num_batches - 1:
                print("\nWaiting 5 seconds before next batch...")
                time.sleep(5)
        elif response == 'skip':
            print("Skipping this batch...")
            continue
        else:
            print("Stopped by user.")
            break
    
    print("\n" + "=" * 80)
    print("ALL BATCHES COMPLETE!")
    print("Check Zotero library for saved papers and PDFs")
    print("=" * 80)

if __name__ == "__main__":
    main()