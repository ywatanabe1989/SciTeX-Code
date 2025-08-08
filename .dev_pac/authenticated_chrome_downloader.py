#!/usr/bin/env python3
"""
Download ALL PDFs from PAC collection using authenticated Chrome Profile 1.
This uses the manually created browser profile with OpenAthens authentication.
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import os
import tempfile


def launch_chrome_with_profile(url: str, profile_path: Path) -> subprocess.Popen:
    """Launch Chrome with authenticated profile."""
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
    ]
    
    chrome_binary = None
    for path in chrome_paths:
        if Path(path).exists():
            chrome_binary = path
            break
    
    if not chrome_binary:
        raise Exception("Chrome/Chromium not found")
    
    # Chrome arguments for automation
    args = [
        chrome_binary,
        f'--user-data-dir={profile_path.parent}',
        f'--profile-directory={profile_path.name}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--no-sandbox',
        '--window-size=1920,1080',
        url
    ]
    
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def download_with_authenticated_browser():
    """Download all PAC PDFs using authenticated browser."""
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    # Use Profile 1 with authentication
    profile_path = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome' / 'Profile 1'
    
    if not profile_path.exists():
        print(f"❌ Profile not found: {profile_path}")
        return
    
    print("PAC Collection Authenticated PDF Downloader")
    print("=" * 60)
    print(f"Using Chrome Profile: {profile_path}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get papers needing PDFs
    papers_to_download = []
    
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
        
        papers_to_download.append({
            'name': item.name,
            'unique_id': unique_id,
            'master_path': master_path,
            'metadata': metadata,
            'doi': doi,
            'url': f"https://doi.org/{doi}" if not doi.startswith('http') else doi
        })
    
    print(f"Found {len(papers_to_download)} papers needing PDFs")
    
    # Create download script using Chrome DevTools Protocol
    download_script = '''
    // Wait for page to load and look for PDF links
    setTimeout(() => {
        // Try to find and click PDF download links
        const pdfLinks = Array.from(document.querySelectorAll('a')).filter(a => 
            a.href && (
                a.href.includes('.pdf') || 
                a.textContent.toLowerCase().includes('pdf') ||
                a.textContent.toLowerCase().includes('download')
            )
        );
        
        if (pdfLinks.length > 0) {
            // Click the first PDF link
            pdfLinks[0].click();
        } else {
            // Try to trigger print dialog which often provides PDF
            window.print();
        }
    }, 5000);
    '''
    
    # Process papers in batches
    batch_size = 5
    for i in range(0, len(papers_to_download), batch_size):
        batch = papers_to_download[i:i+batch_size]
        
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} papers)")
        
        for paper in batch:
            print(f"\n[{i+1}/{len(papers_to_download)}] {paper['name'][:50]}")
            print(f"  DOI: {paper['doi']}")
            print(f"  URL: {paper['url']}")
            
            # Launch Chrome with the URL
            try:
                process = launch_chrome_with_profile(paper['url'], profile_path)
                
                # Wait for page to load and potential download
                time.sleep(10)
                
                # Check if PDF was downloaded to Downloads folder
                downloads_dir = Path.home() / 'Downloads'
                recent_pdfs = sorted(
                    downloads_dir.glob('*.pdf'),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                
                # Check if a new PDF appeared in the last 15 seconds
                if recent_pdfs:
                    latest_pdf = recent_pdfs[0]
                    if time.time() - latest_pdf.stat().st_mtime < 15:
                        # Move PDF to paper directory
                        authors = paper['metadata'].get('authors', [])
                        year = paper['metadata'].get('year', '')
                        if authors and year:
                            first_author = str(authors[0]).split(',')[0].split()[-1]
                            filename = f"{first_author}-{year}.pdf"
                        else:
                            filename = f"{paper['name']}.pdf"
                        
                        target_path = paper['master_path'] / filename
                        latest_pdf.rename(target_path)
                        
                        print(f"  ✅ Downloaded: {filename} ({target_path.stat().st_size / 1024 / 1024:.1f} MB)")
                        
                        # Update metadata
                        with open(paper['master_path'] / 'metadata.json', 'r') as f:
                            metadata = json.load(f)
                        metadata['pdf_downloaded'] = True
                        metadata['pdf_filename'] = filename
                        metadata['pdf_download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        with open(paper['master_path'] / 'metadata.json', 'w') as f:
                            json.dump(metadata, f, indent=2)
                    else:
                        print(f"  ⚠️  No recent PDF found in Downloads")
                
                # Kill Chrome process
                process.terminate()
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Download session completed")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main function."""
    
    # First, let's test if we can use Chrome with the profile
    profile_path = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome' / 'Profile 1'
    
    if not profile_path.exists():
        print("❌ Chrome Profile 1 not found!")
        print(f"Expected at: {profile_path}")
        print("\nPlease ensure you have logged into OpenAthens using:")
        print("  python -m scitex.scholar.cli.open_chrome")
        return
    
    print("✅ Found Chrome Profile 1 with authentication")
    
    # Check for Chrome binary
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if Path(path).exists():
            print(f"✅ Found Chrome at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("❌ Chrome/Chromium not found in standard locations")
        return
    
    # Run the downloader
    download_with_authenticated_browser()


if __name__ == "__main__":
    main()