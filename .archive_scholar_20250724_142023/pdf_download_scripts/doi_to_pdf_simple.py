#!/usr/bin/env python3
"""
Simple DOI to PDF downloader that clearly indicates when user action is needed.
"""

import webbrowser
import time
import json
from pathlib import Path
from datetime import datetime
import sys


def download_pdfs_with_zotero(doi_list, output_tracking_file="pdf_download_progress.json"):
    """
    Semi-automated PDF download using Zotero.
    
    This script will:
    1. Open each DOI in your browser
    2. Wait for you to save it to Zotero (Ctrl+Shift+S)
    3. Track your progress
    """
    
    # Load progress if exists
    progress_file = Path(output_tracking_file)
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            progress = json.load(f)
    else:
        progress = {"completed": [], "failed": [], "remaining": doi_list.copy()}
    
    print("=" * 70)
    print("DOI TO PDF DOWNLOADER (via Zotero)")
    print("=" * 70)
    print(f"Total DOIs: {len(doi_list)}")
    print(f"Already completed: {len(progress['completed'])}")
    print(f"Remaining: {len(progress['remaining'])}")
    print("=" * 70)
    
    # Check prerequisites
    print("\n⚠️  BEFORE WE START - Please ensure:")
    print("   1. Zotero desktop app is running")
    print("   2. You are logged into your institutional accounts in your browser")
    print("   3. Zotero Connector extension is installed in your browser")
    
    input("\nPress Enter when ready to start...")
    
    # Process remaining DOIs
    remaining = progress['remaining'].copy()
    
    for i, doi in enumerate(remaining):
        print(f"\n{'='*70}")
        print(f"[{i+1}/{len(remaining)}] DOI: {doi}")
        print(f"{'='*70}")
        
        # Open in browser
        url = f"https://doi.org/{doi}"
        print(f"\n🌐 Opening in browser: {url}")
        webbrowser.open(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Instruct user
        print("\n👉 YOUR ACTION REQUIRED:")
        print("   1. Wait for the page to fully load")
        print("   2. Press Ctrl+Shift+S (or click Zotero connector icon)")
        print("   3. Zotero will save the paper AND download the PDF")
        print("   4. Come back here and report the result")
        
        print("\nWhat happened?")
        print("  [s] Successfully saved to Zotero")
        print("  [f] Failed (no access/error)")
        print("  [p] Paused (I need a break)")
        print("  [q] Quit")
        
        while True:
            response = input("\nYour choice (s/f/p/q): ").strip().lower()
            
            if response == 's':
                progress['completed'].append(doi)
                progress['remaining'].remove(doi)
                print("✅ Great! Moving to next paper...")
                break
                
            elif response == 'f':
                progress['failed'].append(doi)
                progress['remaining'].remove(doi)
                reason = input("Brief reason for failure (optional): ").strip()
                if reason:
                    progress.setdefault('failure_reasons', {})[doi] = reason
                print("❌ Noted. Moving to next paper...")
                break
                
            elif response == 'p':
                print("\n⏸️  Progress saved. You can resume later by running this script again.")
                save_progress(progress, progress_file)
                return
                
            elif response == 'q':
                print("\n🛑 Quitting...")
                save_progress(progress, progress_file)
                return
                
            else:
                print("Invalid choice. Please enter s, f, p, or q.")
        
        # Save progress after each DOI
        save_progress(progress, progress_file)
        
        # Small delay before next
        if i < len(remaining) - 1:
            time.sleep(2)
    
    # Final summary
    print(f"\n{'='*70}")
    print("DOWNLOAD COMPLETE!")
    print(f"{'='*70}")
    print(f"✅ Successfully downloaded: {len(progress['completed'])}")
    print(f"❌ Failed: {len(progress['failed'])}")
    
    if progress['failed']:
        print("\nFailed DOIs:")
        for doi in progress['failed']:
            reason = progress.get('failure_reasons', {}).get(doi, "No reason given")
            print(f"  - {doi} ({reason})")
    
    print(f"\n📊 Progress saved to: {progress_file}")
    print("\n💡 Your PDFs are now in your Zotero library!")
    print("   Default location: ~/Zotero/storage/")


def save_progress(progress, filepath):
    """Save progress to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(progress, f, indent=2)


def load_dois_from_bibtex(bibtex_file):
    """Extract DOIs from enhanced BibTeX file."""
    # Import at runtime to avoid dependency issues
    from scitex.io import load
    
    entries = load(bibtex_file)
    dois = []
    
    for entry in entries:
        fields = entry.get('fields', {})
        if fields.get('doi'):
            dois.append(fields['doi'])
    
    return dois


if __name__ == "__main__":
    # Example usage
    print("DOI to PDF Downloader")
    print("=" * 70)
    
    # You can either provide DOIs directly...
    example_dois = [
        "10.1371/journal.pone.0159279",
        "10.3389/fnins.2019.00573",
        "10.1016/j.tics.2010.09.001"
    ]
    
    # Or load from your enhanced BibTeX file
    if len(sys.argv) > 1:
        bibtex_file = sys.argv[1]
        print(f"Loading DOIs from: {bibtex_file}")
        dois = load_dois_from_bibtex(bibtex_file)
        print(f"Found {len(dois)} DOIs")
    else:
        print("Using example DOIs (pass BibTeX file as argument to use your own)")
        dois = example_dois
    
    # Start the download process
    download_pdfs_with_zotero(dois)