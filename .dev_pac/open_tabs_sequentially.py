#!/usr/bin/env python3
"""Open tabs sequentially in already-running Chrome."""

import subprocess
import time
from pathlib import Path
import json

def open_tabs_sequentially():
    """Open each URL as a new tab in existing Chrome window."""
    
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
    print(f"OPENING {len(urls_to_open)} PAPERS SEQUENTIALLY")
    print("="*80)
    
    # First, open Chrome with first URL
    print("\n🌐 Opening Chrome with first paper...")
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open Chrome with first URL
    subprocess.Popen([
        'google-chrome',
        '--user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome',
        '--profile-directory=Profile 1',
        urls_to_open[0]
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"1/{len(urls_to_open)}: {papers_list[0]}")
    time.sleep(5)  # Wait for Chrome to start
    
    # Focus Chrome window
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Open remaining URLs as new tabs using Ctrl+T and typing URL
    for i, (url, name) in enumerate(zip(urls_to_open[1:], papers_list[1:]), 2):
        print(f"{i}/{len(urls_to_open)}: {name}")
        
        # Open new tab with Ctrl+T
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+t'], 
                       capture_output=True)
        time.sleep(0.5)
        
        # Type the URL
        subprocess.run(['xdotool', 'type', url], capture_output=True)
        time.sleep(0.2)
        
        # Press Enter to navigate
        subprocess.run(['xdotool', 'key', 'Return'], capture_output=True)
        time.sleep(0.3)  # Small delay between tabs
    
    print(f"\n✅ All {len(urls_to_open)} tabs opened!")
    print("\n💡 Next steps:")
    print("  1. Tabs are loading in background")
    print("  2. Authenticate with OpenAthens when needed")
    print("  3. Save PDFs with Ctrl+S")
    
    # Go back to first tab
    print("\n🔄 Returning to first tab...")
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                   capture_output=True)

if __name__ == "__main__":
    open_tabs_sequentially()