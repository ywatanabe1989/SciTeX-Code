#!/usr/bin/env python3
"""
Fixed tab navigation - use Ctrl+1, Ctrl+2, etc. instead of Ctrl+Tab
"""

import subprocess
import time
import json
from pathlib import Path

def test_tab_switching():
    """Test that tab switching actually works."""
    
    print("=" * 60)
    print("TESTING TAB NAVIGATION")
    print("=" * 60)
    
    # Open 5 test URLs
    print("\nOpening 5 test tabs...")
    
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    test_urls = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.wikipedia.org',
        'https://www.nature.com',
        'https://www.science.org'
    ]
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + test_urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)
    
    print("\nTesting tab navigation...")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Test switching to specific tabs
    for i in range(1, 6):
        print(f"\nSwitching to tab {i} (Ctrl+{i})...")
        subprocess.run(['xdotool', 'key', f'ctrl+{i}'], capture_output=True)
        time.sleep(2)
        print(f"  Now on tab {i}")
    
    print("\n✅ Tab switching test complete!")
    print("Did you see the tabs change?")

def process_papers_with_fixed_navigation():
    """Process papers with proper tab navigation."""
    
    # Get papers
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers = []
    
    for item in sorted(pac_dir.iterdir())[:5]:  # Just 5 for testing
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if not pdf_files and metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:
                        doi = metadata.get('doi', '')
                        if doi:
                            papers.append({
                                'url': f'https://doi.org/{doi}',
                                'title': metadata.get('title', '')[:30]
                            })
                            if len(papers) >= 5:
                                break
    
    if not papers:
        print("No papers to test!")
        return
    
    print("\n" + "=" * 60)
    print("PROCESSING PAPERS WITH FIXED NAVIGATION")
    print("=" * 60)
    
    # Open papers
    print(f"\nOpening {len(papers)} papers...")
    
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    urls = [p['url'] for p in papers]
    
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}...")
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n⏳ Waiting for pages to load...")
    time.sleep(10)
    
    # Process each tab with explicit navigation
    print("\n🤖 Processing with explicit tab numbers...\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    for i in range(1, len(papers) + 1):
        print(f"Tab {i}:")
        
        # Switch to specific tab number
        print(f"  Switching to tab {i} (Ctrl+{i})...")
        subprocess.run(['xdotool', 'key', f'ctrl+{i}'], capture_output=True)
        time.sleep(2)
        
        # Save with Zotero
        print(f"  Saving with Zotero (Ctrl+Shift+S)...")
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        
        # Wait for save
        print(f"  Waiting for save...")
        time.sleep(5)
        
        print(f"  ✓ Tab {i} complete")
    
    print("\n✅ All tabs processed with explicit navigation!")
    print("\nCheck Zotero - each paper should be saved separately")

def main():
    """Run tests."""
    
    print("Testing tab navigation fix...")
    
    # First test basic tab switching
    test_tab_switching()
    
    time.sleep(3)
    
    # Then test with actual papers
    process_papers_with_fixed_navigation()

if __name__ == "__main__":
    main()