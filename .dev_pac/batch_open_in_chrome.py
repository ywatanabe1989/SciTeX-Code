#!/usr/bin/env python3
"""
Open all PAC paper URLs in Chrome with authenticated Profile 1.
This will use OpenAthens authentication to access paywalled content.
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime


def open_url_in_authenticated_chrome(url: str):
    """Open URL in Chrome with Profile 1 (authenticated)."""
    
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
        print("❌ Chrome/Chromium not found")
        return False
    
    profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'
    
    # Chrome arguments
    args = [
        chrome_cmd,
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
        '--new-tab',
        url
    ]
    
    try:
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Error opening Chrome: {e}")
        return False


def main():
    """Open all PAC papers in Chrome for manual/automatic download."""
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    print("PAC Collection - Batch Open in Authenticated Chrome")
    print("=" * 60)
    print("This will open all paper URLs in Chrome with OpenAthens authentication.")
    print("PDFs should download automatically or be accessible for manual download.")
    print()
    
    # Check Profile 1 exists
    profile_path = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome' / 'Profile 1'
    if not profile_path.exists():
        print("❌ Chrome Profile 1 not found!")
        print("Please login to OpenAthens first using:")
        print("  python -m scitex.scholar.cli.open_chrome")
        return
    
    print(f"✅ Using authenticated profile: {profile_path}")
    print()
    
    # Get papers needing PDFs
    papers_to_open = []
    
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
        
        # Check if PDF already exists
        pdf_files = list(master_path.glob('*.pdf'))
        if pdf_files:
            continue
        
        # Load metadata
        metadata_file = master_path / 'metadata.json'
        if not metadata_file.exists():
            continue
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        doi = metadata.get('doi', '')
        if not doi:
            continue
        
        url = f"https://doi.org/{doi}" if not doi.startswith('http') else doi
        
        papers_to_open.append({
            'name': item.name,
            'journal': metadata.get('journal', 'Unknown'),
            'doi': doi,
            'url': url
        })
    
    print(f"Found {len(papers_to_open)} papers needing PDFs")
    
    # Group by publisher for better organization
    by_publisher = {}
    for paper in papers_to_open:
        journal = paper['journal']
        
        if 'IEEE' in journal:
            publisher = 'IEEE'
        elif 'Elsevier' in journal or any(x in journal.lower() for x in ['epilepsy research', 'progress in neurobiology', 'engineering']):
            publisher = 'Elsevier'
        elif 'Scientific Reports' in journal:
            publisher = 'Nature (Scientific Reports)'
        elif 'Nature' in journal:
            publisher = 'Nature'
        elif 'Frontiers' in journal:
            publisher = 'Frontiers'
        elif any(x in journal.lower() for x in ['sensors', 'mathematics', 'diagnostics', 'brain sciences']):
            publisher = 'MDPI'
        else:
            publisher = 'Other'
        
        if publisher not in by_publisher:
            by_publisher[publisher] = []
        by_publisher[publisher].append(paper)
    
    print("\nPapers by publisher:")
    for publisher, papers in sorted(by_publisher.items()):
        print(f"  {publisher}: {len(papers)} papers")
    
    print("\n" + "=" * 60)
    print("Opening papers in Chrome...")
    print("NOTE: This will open multiple tabs. PDFs may download automatically.")
    print("For papers that don't auto-download, look for PDF links on the page.")
    print("=" * 60)
    print()
    
    # Open papers in batches
    batch_size = 5
    
    for publisher, papers in sorted(by_publisher.items()):
        print(f"\n📚 Opening {publisher} papers ({len(papers)} total)...")
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            
            print(f"\n  Batch {i//batch_size + 1} ({len(batch)} papers):")
            
            for paper in batch:
                print(f"    Opening: {paper['name'][:50]}")
                success = open_url_in_authenticated_chrome(paper['url'])
                if success:
                    time.sleep(2)  # Small delay between tabs
                else:
                    print(f"      ❌ Failed to open")
            
            if i + batch_size < len(papers):
                print(f"\n  ⏸️  Pausing 10 seconds before next batch...")
                print("  (Check Chrome for downloads, close unnecessary tabs if needed)")
                time.sleep(10)
    
    print("\n" + "=" * 60)
    print("✅ All papers opened in Chrome!")
    print()
    print("NEXT STEPS:")
    print("1. Check Chrome for automatic downloads")
    print("2. For papers that didn't auto-download, click PDF links manually")
    print("3. Downloaded PDFs will be in your Downloads folder")
    print("4. Move PDFs to appropriate paper directories in:")
    print(f"   {master_dir}")
    print()
    print("TIP: You can also use Zotero Connector browser extension to capture PDFs")
    print("=" * 60)


if __name__ == "__main__":
    main()