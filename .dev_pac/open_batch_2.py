#!/usr/bin/env python3
"""
Open batch 2 of remaining papers (papers 16-30).
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

def open_batch_2():
    """Open papers 16-30 in Chrome."""
    
    papers = get_remaining_papers()
    
    # Get batch 2 (papers 16-30)
    batch_2 = papers[15:30]  # Index 15-29 (papers 16-30)
    
    if not batch_2:
        print("No papers in batch 2!")
        return
    
    print("=" * 60)
    print(f"OPENING BATCH 2: Papers 16-{min(30, 15+len(batch_2))}")
    print("=" * 60)
    print(f"Opening {len(batch_2)} papers\n")
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Show papers being opened
    for i, paper in enumerate(batch_2, 16):
        print(f"{i:2}. {paper['title']}")
        print(f"    {paper['journal']}")
    
    # Prepare Chrome launch
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in batch_2]
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Chrome opening with batch 2...")
    print("Waiting 10 seconds for pages to load...")
    time.sleep(10)
    
    print("\n✅ Batch 2 ready!")
    print(f"Opened {len(batch_2)} papers in Chrome")
    print("\nReady for automated save with Ctrl+Shift+S")

if __name__ == "__main__":
    open_batch_2()