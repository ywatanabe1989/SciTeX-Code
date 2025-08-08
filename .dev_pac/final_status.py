#!/usr/bin/env python3
"""
Final status check for PAC collection PDFs.
"""

import json
from pathlib import Path

def check_final_status():
    """Check final PDF status."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    
    with_pdf = 0
    without_pdf = 0
    ieee = 0
    
    for item in pac_dir.iterdir():
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                pdfs = list(target.glob('*.pdf'))
                metadata_file = target / 'metadata.json'
                
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    journal = metadata.get('journal', '')
                    
                    if pdfs:
                        with_pdf += 1
                    elif 'IEEE' in journal:
                        ieee += 1
                    else:
                        without_pdf += 1
    
    total = with_pdf + without_pdf + ieee
    accessible = total - ieee
    
    print("=" * 60)
    print("FINAL STATUS - PAC COLLECTION")
    print("=" * 60)
    print(f"Total papers: {total}")
    print(f"With PDFs: {with_pdf}")
    print(f"Without PDFs: {without_pdf}")
    print(f"IEEE (no access): {ieee}")
    print("-" * 60)
    print(f"Coverage: {with_pdf}/{accessible} accessible papers")
    print(f"Success rate: {with_pdf/accessible*100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    check_final_status()