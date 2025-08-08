#!/usr/bin/env python3
"""
Smart parallel PDF downloader:
- Skips already downloaded papers
- Opens multiple tabs for parallel download
- Skips SSO redirect pages
"""

import subprocess
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def get_papers_without_pdfs():
    """Get only papers that don't have PDFs yet."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers_without_pdf = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                # Check if PDF already exists
                pdf_files = list(target_dir.glob('*.pdf'))
                
                if pdf_files:
                    # Skip - already has PDF
                    continue
                
                metadata_file = target_dir / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', '')
                    
                    # Skip IEEE (no subscription)
                    if 'IEEE' in journal:
                        continue
                    
                    doi = metadata.get('doi', '')
                    if doi:
                        papers_without_pdf.append({
                            'name': item.name,
                            'doi': doi,
                            'url': f'https://doi.org/{doi}',
                            'journal': journal,
                            'title': metadata.get('title', '')[:50],
                            'target_dir': target_dir
                        })
    
    return papers_without_pdf

def check_for_sso_redirect():
    """Check if current tab is SSO redirect page."""
    # Use xdotool to get window title
    result = subprocess.run(
        ['xdotool', 'getactivewindow', 'getwindowname'],
        capture_output=True, text=True
    )
    
    title = result.stdout.lower() if result.returncode == 0 else ""
    
    # Common SSO indicators
    sso_indicators = [
        'sign in',
        'login',
        'sso',
        'authentication',
        'openathens',
        'shibboleth',
        'university of melbourne',
        'unimelb'
    ]
    
    return any(indicator in title for indicator in sso_indicators)

def save_current_tab():
    """Try to save current tab with Zotero, skip if SSO."""
    
    # Check if it's SSO page
    if check_for_sso_redirect():
        print("    ⚠️  SSO redirect detected - skipping")
        return False
    
    # Try to save with Zotero
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                   capture_output=True)
    
    return True

def parallel_download_batch(papers):
    """Download papers in parallel by opening all tabs at once."""
    
    if not papers:
        return 0
    
    print(f"\n" + "=" * 60)
    print(f"PARALLEL DOWNLOAD - {len(papers)} papers")
    print("=" * 60)
    
    # Kill Chrome and restart
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open all papers at once
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in papers]
    
    print("\nOpening all papers in parallel:")
    for i, paper in enumerate(papers, 1):
        print(f"{i:2}. {paper['title']}")
        print(f"    {paper['journal']}")
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Waiting for all pages to load (15 seconds)...")
    time.sleep(15)
    
    print("\n🤖 Saving all tabs:\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                   capture_output=True)
    time.sleep(2)
    
    saved_count = 0
    skipped_count = 0
    
    # Process each tab
    for i in range(len(papers)):
        print(f"Tab {i+1}/{len(papers)}: {papers[i]['title'][:30]}...")
        
        # Check and save
        if save_current_tab():
            print("    ✅ Saved to Zotero")
            saved_count += 1
            # Wait for save
            time.sleep(5)
        else:
            skipped_count += 1
        
        # Move to next tab
        if i < len(papers) - 1:
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                           capture_output=True)
            time.sleep(1)
    
    print(f"\n✅ Batch complete: {saved_count} saved, {skipped_count} skipped")
    return saved_count

def sync_zotero_to_scholar():
    """Quick sync from Zotero to Scholar."""
    
    print("\n📁 Syncing Zotero → Scholar library...")
    
    result = subprocess.run(
        ['python', '.dev_pac/sync_zotero_to_scholar.py'],
        capture_output=True, text=True
    )
    
    # Extract sync results
    if "Newly synced:" in result.stdout:
        for line in result.stdout.split('\n'):
            if "Newly synced:" in line:
                print(f"  {line.strip()}")
            elif "PAC papers with PDFs:" in line:
                print(f"  {line.strip()}")

def main():
    """Smart parallel download with deduplication."""
    
    print("=" * 80)
    print("SMART PARALLEL PDF DOWNLOADER")
    print("=" * 80)
    
    # Check Zotero
    import requests
    try:
        response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
        if response.status_code != 200:
            raise Exception("Not running")
        print("✅ Linux Zotero is running")
    except:
        print("Starting Zotero...")
        subprocess.Popen([
            '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
            '--connector-port', '23119'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    
    # Initial sync to avoid duplicates
    sync_zotero_to_scholar()
    
    # Process in batches
    batch_size = 10  # Open 10 tabs at once
    max_iterations = 5
    
    for iteration in range(max_iterations):
        print(f"\n{'=' * 80}")
        print(f"ITERATION {iteration + 1}/{max_iterations}")
        print('=' * 80)
        
        # Get ONLY papers without PDFs
        papers = get_papers_without_pdfs()
        
        if not papers:
            print("✅ All accessible papers have PDFs!")
            break
        
        print(f"Found {len(papers)} papers still needing PDFs")
        
        # Take a batch
        batch = papers[:batch_size]
        
        # Download in parallel
        saved = parallel_download_batch(batch)
        
        if saved > 0:
            # Sync after each batch
            sync_zotero_to_scholar()
        
        # Check if we should continue
        if saved == 0:
            print("\n⚠️  No papers saved in this iteration")
            print("Possible reasons:")
            print("  - All remaining papers require manual authentication")
            print("  - Papers are behind paywall")
            break
        
        if iteration < max_iterations - 1 and len(papers) > batch_size:
            print("\n⏰ Waiting 5 seconds before next batch...")
            time.sleep(5)
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    subprocess.run(['python', '.dev_pac/final_status.py'])

if __name__ == "__main__":
    main()