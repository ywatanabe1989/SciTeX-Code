#!/usr/bin/env python3
"""Simple authenticated downloader using Chrome Profile 1 with existing SSO."""

import subprocess
import json
from pathlib import Path
import time

def download_with_auth_session():
    """Use existing authenticated Chrome session."""
    
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
                                'url': f'https://doi.org/{doi}',
                                'target_dir': target
                            })
    
    print("="*80)
    print("SIMPLE AUTHENTICATED DOWNLOADER")
    print("="*80)
    print(f"\n📊 Found {len(papers_to_download)} papers without PDFs (excluding IEEE)")
    
    if not papers_to_download:
        print("✅ All accessible papers have PDFs!")
        return
    
    # Show first 10
    print("\nPapers to download:")
    for i, p in enumerate(papers_to_download[:10], 1):
        print(f"{i:2}. {p['name']}")
        print(f"    {p['journal']}")
    
    if len(papers_to_download) > 10:
        print(f"... and {len(papers_to_download) - 10} more")
    
    print("\n" + "="*80)
    print("OPENING IN AUTHENTICATED CHROME")
    print("="*80)
    print("\n⚠️  Please manually download PDFs using:")
    print("  1. Chrome will open with all papers")
    print("  2. SSO authentication is already active in Profile 1")
    print("  3. Use Ctrl+S to save PDFs manually")
    print("  4. Or use Zotero Connector if it's working")
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open first 10 papers in tabs
    batch_size = 10
    for i in range(0, len(papers_to_download), batch_size):
        batch = papers_to_download[i:i+batch_size]
        
        print(f"\n📂 Opening batch {i//batch_size + 1} ({len(batch)} papers)...")
        
        urls = [p['url'] for p in batch]
        
        args = [
            'google-chrome',
            f'--user-data-dir={profile_dir}',
            '--profile-directory=Profile 1',
        ] + urls
        
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("\n📝 Papers in this batch:")
        for p in batch:
            print(f"  • {p['name']}")
        
        print("\n⏸️  Chrome opened. Please:")
        print("  1. Check if papers load with full text")
        print("  2. Save PDFs manually with Ctrl+S")
        print("  3. Save to: " + str(batch[0]['target_dir'].parent))
        print("\nPress Enter when done with this batch...")
        
        # Wait for user input
        if i + batch_size < len(papers_to_download):
            input()
            subprocess.run(['pkill', 'chrome'], capture_output=True)
            time.sleep(2)
        else:
            print("\n✅ Last batch - no more papers after this")
    
    print("\n" + "="*80)
    print("DOWNLOAD COMPLETE")
    print("="*80)
    print("\nPlease move downloaded PDFs to their respective directories.")
    print("Run this to check status:")
    print("  python .dev_pac/check_pdf_details.py")

def check_auth_status():
    """Check if authentication is working."""
    
    print("\n🔐 Checking authentication status...")
    
    # Check for auth cookies
    profile_dir = Path('/home/ywatanabe/.scitex/scholar/cache/chrome/Profile 1')
    
    if profile_dir.exists():
        print("✅ Chrome Profile 1 exists")
        
        # Check for cookies database
        cookies_db = profile_dir / 'Cookies'
        if cookies_db.exists():
            size_mb = cookies_db.stat().st_size / (1024 * 1024)
            print(f"✅ Cookies database exists ({size_mb:.1f} MB)")
        else:
            print("⚠️  No cookies database found")
    else:
        print("❌ Chrome Profile 1 not found")
    
    print("\n📌 Make sure you've logged in to OpenAthens through Chrome Profile 1")
    print("   Run: python -m scitex.scholar.authenticate openathens")

if __name__ == "__main__":
    check_auth_status()
    download_with_auth_session()