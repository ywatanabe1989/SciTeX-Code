#!/usr/bin/env python3
"""
Detailed status check for PAC collection PDFs.
Shows exactly which papers have PDFs and which don't.
"""

import json
from pathlib import Path
from collections import defaultdict

def check_detailed_status():
    """Check detailed PDF status for PAC collection."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    
    stats = defaultdict(list)
    
    # Iterate through all symlinks in pac directory
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            # Follow symlink to actual directory in MASTER
            target_dir = item.resolve()
            if target_dir.exists():
                # Check for PDF in the actual MASTER directory
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', 'Unknown')
                    title = metadata.get('title', 'Unknown')
                    doi = metadata.get('doi', '')
                    
                    status = 'has_pdf' if pdf_files else 'no_pdf'
                    
                    # Categorize by journal
                    if 'IEEE' in journal:
                        status = 'ieee_no_subscription'
                    elif pdf_files:
                        pdf_names = [p.name for p in pdf_files]
                        status = 'has_pdf'
                    
                    stats[status].append({
                        'name': item.name,
                        'journal': journal,
                        'title': title[:60],
                        'doi': doi,
                        'pdfs': [p.name for p in pdf_files] if pdf_files else []
                    })
    
    return stats

def print_report(stats):
    """Print detailed status report."""
    print("=" * 80)
    print("PAC COLLECTION - DETAILED PDF STATUS REPORT")
    print("=" * 80)
    
    # Papers with PDFs
    if stats['has_pdf']:
        print(f"\n✅ PAPERS WITH PDFs ({len(stats['has_pdf'])})")
        print("-" * 40)
        for paper in stats['has_pdf']:
            print(f"• {paper['name']}")
            print(f"  Journal: {paper['journal']}")
            print(f"  PDFs: {', '.join(paper['pdfs'])}")
    
    # Papers without PDFs (excluding IEEE)
    accessible_no_pdf = [p for p in stats['no_pdf'] if 'IEEE' not in p['journal']]
    if accessible_no_pdf:
        print(f"\n⚠️ ACCESSIBLE PAPERS WITHOUT PDFs ({len(accessible_no_pdf)})")
        print("-" * 40)
        for paper in accessible_no_pdf:
            print(f"• {paper['name']}")
            print(f"  Journal: {paper['journal']}")
            print(f"  DOI: {paper['doi']}")
    
    # IEEE papers (no subscription)
    ieee_papers = stats['ieee_no_subscription']
    if ieee_papers:
        print(f"\n❌ IEEE PAPERS - NO SUBSCRIPTION ({len(ieee_papers)})")
        print("-" * 40)
        for paper in ieee_papers[:5]:  # Show first 5 as example
            print(f"• {paper['name']}")
        if len(ieee_papers) > 5:
            print(f"  ... and {len(ieee_papers) - 5} more")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("-" * 40)
    total = sum(len(papers) for papers in stats.values())
    print(f"Total papers: {total}")
    print(f"With PDFs: {len(stats['has_pdf'])}")
    print(f"Without PDFs (accessible): {len(accessible_no_pdf)}")
    print(f"IEEE (no subscription): {len(ieee_papers)}")
    print(f"Coverage: {len(stats['has_pdf'])}/{total - len(ieee_papers)} accessible papers")
    
    # Next steps
    if accessible_no_pdf:
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("-" * 40)
        print("1. Chrome with papers is open")
        print("2. Zotero WSL Proxy is running")
        print("3. Click Zotero Connector icon to save papers")
        print("4. PDFs will download with institutional access")

def main():
    stats = check_detailed_status()
    print_report(stats)

if __name__ == "__main__":
    main()