#!/usr/bin/env python3
"""Open all papers without PDFs in Chrome tabs at once."""

import json
import subprocess
from pathlib import Path

def open_all_missing_papers():
    """Open all papers without PDFs in Chrome."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    urls_to_open = []
    
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
                            print(f"  • {item.name}")
    
    if not urls_to_open:
        print("✅ All papers have PDFs!")
        return
    
    print("="*80)
    print(f"OPENING {len(urls_to_open)} PAPERS WITHOUT PDFs")
    print("="*80)
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    import time
    time.sleep(2)
    
    # Open all URLs at once
    args = [
        'google-chrome',
        '--user-data-dir=/home/ywatanabe/.scitex/scholar/cache/chrome',
        '--profile-directory=Profile 1',
    ] + urls_to_open
    
    print(f"\n🌐 Opening {len(urls_to_open)} tabs in Chrome...")
    print("\n⚠️  This will open ALL missing papers at once!")
    print("   Chrome may take a moment to load all tabs.")
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n✅ All tabs opened!")
    print("\n💡 Next steps:")
    print("  1. Wait for all tabs to load")
    print("  2. Authenticate with OpenAthens if prompted")
    print("  3. Save PDFs with Ctrl+S or Zotero Connector")
    print("  4. Move saved PDFs to ~/.scitex/scholar/library/MASTER/<id>/")

if __name__ == "__main__":
    open_all_missing_papers()