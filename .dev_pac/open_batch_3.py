#!/usr/bin/env python3
"""
Open batch 3 - final remaining papers.
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

def open_batch_3():
    """Open remaining papers (31+) in Chrome."""
    
    papers = get_remaining_papers()
    
    # Get batch 3 (papers 31+)
    batch_3 = papers[30:]  # Index 30+ (papers 31+)
    
    if not batch_3:
        print("No papers in batch 3!")
        return 0
    
    print("=" * 60)
    print(f"OPENING BATCH 3: Final {len(batch_3)} papers")
    print("=" * 60)
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Show papers being opened
    for i, paper in enumerate(batch_3, 31):
        print(f"{i:2}. {paper['title']}")
        print(f"    {paper['journal']}")
    
    # Prepare Chrome launch
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in batch_3]
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"\n⏳ Chrome opening with final {len(batch_3)} papers...")
    print("Waiting 10 seconds for pages to load...")
    time.sleep(10)
    
    print("\n✅ Batch 3 ready!")
    print(f"Opened {len(batch_3)} papers in Chrome")
    print("\nThis is the FINAL BATCH!")
    
    return len(batch_3)

if __name__ == "__main__":
    num_papers = open_batch_3()
    if num_papers == 0:
        print("\n🎉 ALL PAPERS PROCESSED!")
        print("No more papers to download")