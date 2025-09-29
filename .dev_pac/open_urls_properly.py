#!/usr/bin/env python3
"""Open URLs properly in Chrome - workaround for multiple URL issue."""

import json
import subprocess
import time
from pathlib import Path

def open_all_at_once():
    """Open all missing papers using proper Chrome syntax."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    urls_to_open = []
    papers_list = []
    
    # Collect papers without PDFs
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                pdfs = list(target.glob('*.pdf'))
                
                if not pdfs:  # No PDF exists
                    metadata_file = target / 'metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        doi = metadata.get('doi', '')
                        if doi and doi != 'None':
                            urls_to_open.append(f'https://doi.org/{doi}')
                            papers_list.append(item.name)
    
    if not urls_to_open:
        print("✅ All papers have PDFs!")
        return
    
    print("="*80)
    print(f"OPENING {len(urls_to_open)} PAPERS")
    print("="*80)
    
    for i, name in enumerate(papers_list[:10], 1):
        print(f"{i:2}. {name}")
    if len(papers_list) > 10:
        print(f"... and {len(papers_list) - 10} more")
    
    # Method 1: Try using bash to expand all URLs
    print("\n🌐 Opening all tabs...")
    
    # Kill Chrome first
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Build command with all URLs as separate arguments
    chrome_cmd = [
        'google-chrome',
        '--user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome',
        '--profile-directory=Profile 1',
        '--new-window'  # Force new window
    ]
    
    # Add each URL as a separate argument
    for url in urls_to_open:
        chrome_cmd.append(url)
    
    # Execute with shell=False to ensure each URL is a separate argument
    proc = subprocess.Popen(chrome_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"\n✅ Chrome launched with {len(urls_to_open)} URLs")
    
    # Alternative: If that doesn't work, open Chrome first then add tabs
    time.sleep(5)
    
    # Check if all tabs opened
    print("\n⚠️  If only one tab opened:")
    print("  1. Chrome may have a limit on command-line URLs")
    print("  2. Try the alternative script: open_tabs_sequentially.py")
    
    return urls_to_open

if __name__ == "__main__":
    urls = open_all_at_once()
    
    # Save URLs to file for alternative method
    if urls:
        with open('.dev_pac/urls_to_open.txt', 'w') as f:
            for url in urls:
                f.write(url + '\n')
        print(f"\n📁 URLs saved to: .dev_pac/urls_to_open.txt")