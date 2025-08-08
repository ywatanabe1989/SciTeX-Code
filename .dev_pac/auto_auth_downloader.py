#!/usr/bin/env python3
"""Automated authenticated downloader - opens papers and attempts download."""

import subprocess
import json
from pathlib import Path
import time

def main():
    """Automated download with existing auth."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Get papers without PDFs
    papers_to_download = []
    
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
                        
                        # Skip IEEE (no subscription)
                        if 'IEEE' in journal:
                            continue
                        
                        doi = metadata.get('doi', '')
                        if doi:
                            papers_to_download.append({
                                'name': item.name,
                                'journal': journal,
                                'doi': doi,
                                'url': f'https://doi.org/{doi}'
                            })
    
    print("="*80)
    print("AUTOMATED AUTHENTICATED DOWNLOADER")
    print("="*80)
    print(f"\n📊 Found {len(papers_to_download)} papers without PDFs (excluding IEEE)")
    
    if not papers_to_download:
        print("✅ All accessible papers have PDFs!")
        return
    
    # Kill Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Process in small batches
    batch_size = 5
    
    for i in range(0, len(papers_to_download), batch_size):
        batch = papers_to_download[i:i+batch_size]
        
        print(f"\n{'='*60}")
        print(f"BATCH {i//batch_size + 1} - {len(batch)} papers")
        print('='*60)
        
        for p in batch:
            print(f"  • {p['name']}")
        
        urls = [p['url'] for p in batch]
        
        # Open all URLs in Chrome
        args = [
            'google-chrome',
            f'--user-data-dir={profile_dir}',
            '--profile-directory=Profile 1',
        ] + urls
        
        print("\n🌐 Opening in Chrome with authentication...")
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for pages to load
        print("⏳ Waiting 20 seconds for pages to load...")
        time.sleep(20)
        
        # Focus Chrome
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                       capture_output=True)
        time.sleep(1)
        
        # Try to save each tab
        print("\n💾 Attempting to save PDFs...")
        
        # Go to first tab
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                       capture_output=True)
        time.sleep(2)
        
        for j in range(len(batch)):
            print(f"  Tab {j+1}: {batch[j]['name'][:40]}...")
            
            # Try keyboard shortcut for PDF download
            # Ctrl+S to save page
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+s'], 
                           capture_output=True)
            time.sleep(3)
            
            # Press Enter to confirm save dialog
            subprocess.run(['xdotool', 'key', 'Return'], 
                           capture_output=True)
            time.sleep(2)
            
            # Move to next tab
            if j < len(batch) - 1:
                subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                               capture_output=True)
                time.sleep(1)
        
        print("✅ Batch complete")
        
        # Kill Chrome before next batch
        if i + batch_size < len(papers_to_download):
            print("\n⏰ Closing Chrome and waiting before next batch...")
            subprocess.run(['pkill', 'chrome'], capture_output=True)
            time.sleep(5)
    
    print("\n" + "="*80)
    print("DOWNLOAD ATTEMPTS COMPLETE")
    print("="*80)
    
    # Check results
    print("\n📊 Checking results...")
    subprocess.run(['python', '.dev_pac/check_pdf_details.py'])
    
    # Move any downloaded PDFs from Downloads folder
    downloads_dir = Path.home() / 'Downloads'
    pdf_files = list(downloads_dir.glob('*.pdf'))
    
    if pdf_files:
        print(f"\n📁 Found {len(pdf_files)} PDFs in Downloads folder")
        print("You may need to move them to appropriate directories")
        for pdf in pdf_files[:5]:
            print(f"  • {pdf.name}")

if __name__ == "__main__":
    main()