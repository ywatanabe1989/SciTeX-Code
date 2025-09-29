#!/usr/bin/env python3
"""
Use Chrome with Zotero Connector to capture PAC papers.
This opens papers in Chrome where Zotero Connector can save them directly.

Since Chrome in WSL has Zotero Connector installed, it should be able to:
1. Detect papers on publisher pages
2. Save metadata to Zotero
3. Attempt PDF downloads with institutional access
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime


def open_in_chrome_for_zotero(urls: list, batch_size: int = 5):
    """Open URLs in Chrome with Profile 1 for Zotero Connector capture."""
    
    chrome_paths = [
        'google-chrome',
        'google-chrome-stable', 
        'chromium',
        'chromium-browser',
    ]
    
    chrome_cmd = None
    for cmd in chrome_paths:
        try:
            subprocess.run(['which', cmd], capture_output=True, check=True)
            chrome_cmd = cmd
            break
        except:
            continue
    
    if not chrome_cmd:
        print("❌ Chrome not found")
        return
    
    profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'
    
    print("Opening papers in Chrome with Zotero Connector...")
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("1. Chrome will open with multiple tabs")
    print("2. Zotero Connector icon should appear in toolbar")
    print("3. Click Zotero icon to save each paper")
    print("4. Connector will detect paper metadata automatically")
    print("5. PDFs may download if accessible with your institutional login")
    print("=" * 60)
    print()
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        
        print(f"Opening batch {i//batch_size + 1} ({len(batch)} papers)...")
        
        # Open all URLs in batch
        for url_data in batch:
            url = url_data['url']
            name = url_data['name']
            
            args = [
                chrome_cmd,
                f'--user-data-dir={profile_dir}',
                '--profile-directory=Profile 1',
                '--new-tab',
                url
            ]
            
            try:
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  Opened: {name[:50]}")
                time.sleep(2)  # Small delay between tabs
            except Exception as e:
                print(f"  Failed: {name[:50]} - {e}")
        
        if i + batch_size < len(urls):
            print(f"\n⏸️  Batch complete. Save papers to Zotero using the Connector icon.")
            print("Press Enter to continue with next batch...")
            input()
        print()


def main():
    """Main function to facilitate Zotero Connector capture."""
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    print("PAC Collection → Zotero via Chrome Connector")
    print("=" * 60)
    print()
    
    # Check Chrome Profile
    profile_path = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome' / 'Profile 1'
    if not profile_path.exists():
        print("❌ Chrome Profile 1 not found!")
        return
    
    print("✅ Using authenticated Chrome Profile 1")
    print("✅ Zotero Connector should be installed in Chrome")
    print()
    
    # Get papers
    papers = []
    
    for item in sorted(pac_dir.iterdir()):
        if not item.is_symlink() or item.name.startswith('.') or item.name == 'info':
            continue
        
        target = item.readlink()
        if target.parts[0] != '..':
            continue
            
        unique_id = target.parts[-1]
        master_path = master_dir / unique_id
        
        if not master_path.exists():
            continue
        
        metadata_file = master_path / 'metadata.json'
        if not metadata_file.exists():
            continue
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        doi = metadata.get('doi', '')
        if not doi:
            continue
        
        # Check if already has PDF
        pdf_files = list(master_path.glob('*.pdf'))
        
        papers.append({
            'name': item.name,
            'journal': metadata.get('journal', 'Unknown'),
            'year': metadata.get('year', ''),
            'has_pdf': len(pdf_files) > 0,
            'doi': doi,
            'url': f"https://doi.org/{doi}" if not doi.startswith('http') else doi
        })
    
    print(f"Found {len(papers)} papers with DOIs")
    
    # Filter options
    without_pdf = [p for p in papers if not p['has_pdf']]
    print(f"Papers without PDFs: {len(without_pdf)}")
    print()
    
    print("Options:")
    print("1. Open ALL papers for Zotero capture")
    print("2. Open only papers WITHOUT PDFs")
    print("3. Open specific publishers (IEEE, Elsevier, etc.)")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == '2':
        papers = without_pdf
        print(f"\nWill open {len(papers)} papers without PDFs")
    elif choice == '3':
        print("\nSelect publisher:")
        print("1. IEEE papers")
        print("2. Elsevier papers")
        print("3. Nature/Scientific Reports")
        print("4. Frontiers")
        print("5. MDPI")
        print("6. All paywalled (IEEE + Elsevier)")
        
        pub_choice = input("\nSelect publisher (1-6): ").strip()
        
        if pub_choice == '1':
            papers = [p for p in papers if 'IEEE' in p['journal']]
        elif pub_choice == '2':
            papers = [p for p in papers if any(x in p['journal'].lower() for x in ['elsevier', 'epilepsy research', 'progress in neurobiology'])]
        elif pub_choice == '3':
            papers = [p for p in papers if 'Nature' in p['journal'] or 'Scientific Reports' in p['journal']]
        elif pub_choice == '4':
            papers = [p for p in papers if 'Frontiers' in p['journal']]
        elif pub_choice == '5':
            papers = [p for p in papers if any(x in p['journal'].lower() for x in ['sensors', 'mathematics', 'diagnostics', 'brain sciences'])]
        elif pub_choice == '6':
            papers = [p for p in papers if 'IEEE' in p['journal'] or any(x in p['journal'].lower() for x in ['elsevier', 'epilepsy research', 'progress in neurobiology'])]
        
        print(f"\nWill open {len(papers)} papers from selected publisher(s)")
    
    if not papers:
        print("No papers to process")
        return
    
    print()
    print("Papers to open:")
    for i, p in enumerate(papers[:10], 1):
        pdf_status = "✅ Has PDF" if p['has_pdf'] else "❌ No PDF"
        print(f"  {i}. {p['name'][:40]:<40} [{p['journal'][:20]:<20}] {pdf_status}")
    
    if len(papers) > 10:
        print(f"  ... and {len(papers) - 10} more")
    
    print()
    confirm = input("Proceed? (y/n): ").strip().lower()
    
    if confirm == 'y':
        print()
        open_in_chrome_for_zotero(papers, batch_size=5)
        
        print("\n" + "=" * 60)
        print("✅ All papers opened!")
        print()
        print("NEXT STEPS:")
        print("1. Go to Chrome")
        print("2. Click the Zotero Connector icon in each tab")
        print("3. Zotero will save the paper with metadata")
        print("4. If you have access, PDFs will download automatically")
        print()
        print("TIP: You can save all open tabs at once:")
        print("  - Right-click Zotero icon → 'Save to Zotero' → 'Save All Tabs'")
        print()
        print("Your institutional access (OpenAthens) should allow PDF downloads for:")
        print("  - IEEE papers")
        print("  - Elsevier papers")
        print("  - Nature papers")
        print("  - Most university subscribed content")


if __name__ == "__main__":
    main()