#!/usr/bin/env python3
"""
PDF downloader using Ctrl+Tab for sequential tab navigation.
Continues until coverage increases.
"""

import subprocess
import time
import json
from pathlib import Path

def check_current_coverage():
    """Check current PDF coverage."""
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
    coverage = with_pdf / accessible * 100 if accessible > 0 else 0
    
    return with_pdf, without_pdf, ieee, coverage

def get_remaining_papers():
    """Get papers without PDFs."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if not pdf_files and metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:  # Skip IEEE
                        doi = metadata.get('doi', '')
                        if doi:
                            papers.append({
                                'name': item.name,
                                'doi': doi,
                                'url': f'https://doi.org/{doi}',
                                'journal': journal,
                                'title': metadata.get('title', '')[:50]
                            })
    
    return papers

def process_batch_with_ctrl_tab(papers, batch_num):
    """Process batch using Ctrl+Tab navigation."""
    
    print(f"\n" + "=" * 60)
    print(f"BATCH {batch_num} - {len(papers)} papers")
    print("=" * 60)
    
    # Kill Chrome and restart
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open papers
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in papers]
    
    print("\nOpening papers:")
    for i, paper in enumerate(papers, 1):
        print(f"{i:2}. {paper['title']}")
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Waiting for pages to load...")
    time.sleep(12)
    
    print("\n🤖 Processing with Ctrl+Tab navigation:\n")
    
    # Focus Chrome window
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Start from first tab
    print("Going to first tab (Ctrl+1)...")
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                   capture_output=True)
    time.sleep(2)
    
    # Process each tab using Ctrl+Tab
    for i in range(len(papers)):
        print(f"Tab {i+1}/{len(papers)}:")
        
        # Save with Zotero
        print(f"  → Saving with Zotero (Ctrl+Shift+S)...")
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                       capture_output=True)
        
        # Wait for save
        print(f"  → Waiting for download...", end='', flush=True)
        for j in range(7):  # Slightly longer wait
            time.sleep(1)
            print(".", end='', flush=True)
        print(" ✓")
        
        # Move to next tab (except for last)
        if i < len(papers) - 1:
            print(f"  → Next tab (Ctrl+Tab)")
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                           capture_output=True)
            time.sleep(2)
        
        print()
    
    print(f"✅ Batch {batch_num} complete!")

def main():
    """Download until coverage improves."""
    
    print("=" * 80)
    print("PDF DOWNLOAD WITH CTRL+TAB - CONTINUOUS")
    print("=" * 80)
    
    # Check initial coverage
    with_pdf, without_pdf, ieee, initial_coverage = check_current_coverage()
    print(f"\nInitial status:")
    print(f"  With PDFs: {with_pdf}")
    print(f"  Without PDFs: {without_pdf}")
    print(f"  IEEE (no access): {ieee}")
    print(f"  Coverage: {initial_coverage:.1f}%")
    
    # Check Zotero
    import requests
    try:
        response = requests.get("http://127.0.0.1:23119/connector/ping", timeout=2)
        if response.status_code == 200:
            print("✅ Linux Zotero is running")
        else:
            print("Starting Zotero...")
            subprocess.Popen([
                '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
                '--connector-port', '23119'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
    except:
        print("Starting Zotero...")
        subprocess.Popen([
            '/home/ywatanabe/opt/Zotero_linux-x86_64/zotero',
            '--connector-port', '23119'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)
    
    # Process in smaller batches for better success rate
    batch_size = 6
    max_iterations = 5  # Limit iterations
    
    for iteration in range(max_iterations):
        print(f"\n{'=' * 80}")
        print(f"ITERATION {iteration + 1}/{max_iterations}")
        print('=' * 80)
        
        # Get remaining papers
        papers = get_remaining_papers()
        
        if not papers:
            print("All accessible papers have PDFs!")
            break
        
        print(f"Found {len(papers)} papers without PDFs")
        
        # Process one batch
        batch = papers[:batch_size]
        process_batch_with_ctrl_tab(batch, iteration + 1)
        
        # Sync Zotero to Scholar
        print("\nSyncing Zotero PDFs to Scholar library...")
        subprocess.run(['python', '.dev_pac/sync_zotero_to_scholar.py'], 
                       capture_output=True)
        
        # Check new coverage
        with_pdf_new, without_pdf_new, _, new_coverage = check_current_coverage()
        
        print(f"\nCoverage update:")
        print(f"  Before: {initial_coverage:.1f}%")
        print(f"  After: {new_coverage:.1f}%")
        print(f"  PDFs added: {with_pdf_new - with_pdf}")
        
        if new_coverage > initial_coverage + 5:  # Significant improvement
            print(f"✅ Significant improvement! Coverage increased by {new_coverage - initial_coverage:.1f}%")
            initial_coverage = new_coverage
            with_pdf = with_pdf_new
        
        # Wait before next iteration
        if iteration < max_iterations - 1:
            print("\n⏰ Waiting 5 seconds before next iteration...")
            time.sleep(5)
    
    print("\n" + "=" * 80)
    print("DOWNLOAD SESSION COMPLETE")
    print("=" * 80)
    
    # Final status
    with_pdf_final, without_pdf_final, ieee_final, final_coverage = check_current_coverage()
    print(f"\nFinal status:")
    print(f"  With PDFs: {with_pdf_final}")
    print(f"  Without PDFs: {without_pdf_final}")
    print(f"  IEEE (no access): {ieee_final}")
    print(f"  Coverage: {final_coverage:.1f}%")
    print(f"\nImprovement: {final_coverage - initial_coverage:.1f}%")

if __name__ == "__main__":
    main()