#!/usr/bin/env python3
"""Check current processing status."""

import json
from pathlib import Path
from datetime import datetime

def check_status():
    """Check and display current processing status."""
    progress_file = Path(".dev/processing_progress.json")
    
    if not progress_file.exists():
        print("No progress file found.")
        return
    
    with open(progress_file, 'r') as f:
        progress = json.load(f)
    
    total_papers = 75  # From BibTeX file
    processed = len(progress["processed_keys"])
    results = progress["results"]
    
    # Count statistics
    doi_found = sum(1 for r in results if r.get("doi"))
    pdf_found = sum(1 for r in results if r.get("pdf_stored"))
    errors = sum(1 for r in results if r.get("error"))
    
    print("=" * 60)
    print("SCHOLAR PIPELINE PROCESSING STATUS")
    print("=" * 60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nProgress: {processed}/{total_papers} papers ({processed/total_papers*100:.1f}%)")
    print(f"Last processed index: {progress['last_processed_index']}")
    
    print(f"\nStatistics:")
    print(f"  DOIs found: {doi_found}/{processed} ({doi_found/processed*100:.1f}%)")
    print(f"  PDFs stored: {pdf_found}/{processed} ({pdf_found/processed*100:.1f}%)")
    print(f"  Errors: {errors}")
    
    # Show last 5 processed papers
    print(f"\nLast 5 processed papers:")
    for key in progress["processed_keys"][-5:]:
        # Find result for this key
        result = next((r for r in results if any(key in str(v) for v in r.values())), None)
        if result:
            status = "PDF" if result.get("pdf_stored") else "DOI" if result.get("doi") else "No DOI"
            print(f"  - {key}: {status}")
    
    # Count papers by status
    print(f"\nPapers by status:")
    pdf_papers = [r for r in results if r.get("pdf_stored")]
    doi_only_papers = [r for r in results if r.get("doi") and not r.get("pdf_stored")]
    no_doi_papers = [r for r in results if not r.get("doi") and not r.get("error")]
    
    print(f"  With PDF: {len(pdf_papers)}")
    print(f"  DOI only (need PDF): {len(doi_only_papers)}")
    print(f"  No DOI found: {len(no_doi_papers)}")
    print(f"  Errors: {errors}")
    
    # Estimate remaining time
    if processed > 0:
        # Rough estimate: 2 seconds per paper
        remaining = total_papers - processed
        est_minutes = (remaining * 2) / 60
        print(f"\nEstimated time remaining: {est_minutes:.1f} minutes")
    
    # Check if still running
    import subprocess
    try:
        result = subprocess.run(['pgrep', '-f', 'process_all_papers_sequential.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n✓ Processing is currently RUNNING (PID: {result.stdout.strip()})")
        else:
            print(f"\n✗ Processing is NOT running")
    except:
        pass

if __name__ == "__main__":
    check_status()