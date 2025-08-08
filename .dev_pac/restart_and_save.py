#!/usr/bin/env python3
"""
Restart Chrome with papers and automate Zotero saves.
Ensures proxy is running and Chrome can detect Zotero.
"""

import subprocess
import time
import json
import requests
from pathlib import Path

def ensure_zotero_proxy():
    """Ensure Zotero WSL Proxy is running."""
    print("Checking Zotero WSL Proxy...")
    
    # Check if proxy is already running
    try:
        response = requests.get("http://ywata-note-win.local:23119/connector/ping", timeout=2)
        if response.status_code == 200:
            print("✅ Zotero proxy already running")
            return True
    except:
        pass
    
    print("❌ Proxy not running. Please start it manually:")
    print("\nIn a separate terminal, run:")
    print("cd /path/to/Zotero-WSL-ProxyServer")
    print("python3 zotero_wsl_proxy.py")
    print("\nOr if installed as a service:")
    print("zotero-wsl-proxy")
    
    input("\nPress Enter when proxy is running...")
    
    # Verify it's running now
    try:
        response = requests.get("http://ywata-note-win.local:23119/connector/ping", timeout=2)
        if response.status_code == 200:
            print("✅ Zotero proxy now running!")
            return True
    except:
        pass
    
    return False

def get_papers_without_pdfs():
    """Get DOI URLs for papers without PDFs."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    urls = []
    
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
                            urls.append(f'https://doi.org/{doi}')
    
    return urls

def restart_chrome_with_papers(urls, limit=15):
    """Restart Chrome with paper URLs."""
    print(f"\nRestarting Chrome with {min(limit, len(urls))} papers...")
    
    # Kill existing Chrome
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Prepare Chrome launch
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Launch Chrome with papers
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + urls[:limit]
    
    # Start Chrome
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("⏳ Waiting for Chrome to start and load pages...")
    time.sleep(10)  # Give Chrome time to start and load
    
    # Verify Zotero Connector can see Zotero
    print("\n✅ Chrome restarted with papers")
    print("✅ Zotero Connector should now detect Zotero Desktop")

def automated_save(num_tabs):
    """Automate Ctrl+Shift+S on each tab."""
    print("\n" + "=" * 80)
    print("STARTING AUTOMATED SAVES")
    print("=" * 80)
    print("\n⚠️  DO NOT TOUCH KEYBOARD/MOUSE!\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    for i in range(num_tabs):
        print(f"Tab {i+1}/{num_tabs}: ", end='', flush=True)
        
        # Wait for page
        time.sleep(2)
        
        # Save with Zotero (Ctrl+Shift+S)
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        print("Saving...", end='', flush=True)
        
        # Wait for save
        time.sleep(5)
        print(" ✓")
        
        # Next tab
        if i < num_tabs - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n✅ COMPLETE! Check Zotero library for saved papers and PDFs")

def main():
    """Main workflow."""
    print("=" * 80)
    print("ZOTERO BATCH SAVE - COMPLETE SOLUTION")
    print("=" * 80)
    
    # Step 1: Ensure proxy is running
    if not ensure_zotero_proxy():
        print("❌ Cannot proceed without Zotero proxy")
        return
    
    # Step 2: Get papers
    urls = get_papers_without_pdfs()
    print(f"\nFound {len(urls)} papers without PDFs (excluding IEEE)")
    
    if not urls:
        print("No papers to process!")
        return
    
    # Step 3: How many to process
    try:
        num_tabs = int(input(f"\nHow many to process (max {len(urls)}, default 15): ") or "15")
        num_tabs = min(num_tabs, len(urls))
    except:
        num_tabs = min(15, len(urls))
    
    # Step 4: Restart Chrome
    print("\n" + "-" * 40)
    print("Will:")
    print("1. Restart Chrome with papers")
    print("2. Wait for pages to load")
    print("3. Automate Zotero saves")
    print("-" * 40)
    
    if input("\nProceed? (y/n): ").lower() != 'y':
        print("Cancelled.")
        return
    
    # Step 5: Restart Chrome with papers
    restart_chrome_with_papers(urls, num_tabs)
    
    # Step 6: Run automation
    print("\nReady to start automation in 5 seconds...")
    print("Make sure Chrome is visible!")
    time.sleep(5)
    
    automated_save(num_tabs)

if __name__ == "__main__":
    main()