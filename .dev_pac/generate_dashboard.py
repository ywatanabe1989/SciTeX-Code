#!/usr/bin/env python3
"""Generate PAC dashboard with paper status and links."""

import json
from pathlib import Path
import webbrowser

def generate_dashboard_data():
    """Generate JSON data for the dashboard."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers_data = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                # Check for PDFs
                pdfs = list(target.glob('*.pdf'))
                has_pdf = len(pdfs) > 0
                
                # Get metadata
                metadata_file = target / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    paper_info = {
                        'name': item.name,
                        'journal': metadata.get('journal', ''),
                        'doi': metadata.get('doi', ''),
                        'title': metadata.get('title', ''),
                        'year': metadata.get('year', ''),
                        'authors': metadata.get('authors', []),
                        'has_pdf': has_pdf,
                        'pdf_count': len(pdfs)
                    }
                else:
                    paper_info = {
                        'name': item.name,
                        'journal': '',
                        'doi': '',
                        'title': item.name,
                        'year': '',
                        'authors': [],
                        'has_pdf': has_pdf,
                        'pdf_count': len(pdfs)
                    }
                
                papers_data.append(paper_info)
    
    # Save JSON data
    json_file = Path('.dev_pac/pac_papers.json')
    with open(json_file, 'w') as f:
        json.dump(papers_data, f, indent=2)
    
    return papers_data

def generate_summary(papers_data):
    """Generate summary statistics."""
    
    total = len(papers_data)
    with_pdf = sum(1 for p in papers_data if p['has_pdf'])
    ieee = sum(1 for p in papers_data if 'IEEE' in p.get('journal', ''))
    missing = total - with_pdf - ieee
    accessible = total - ieee
    coverage = (with_pdf / accessible * 100) if accessible > 0 else 0
    
    print("="*80)
    print("PAC COLLECTION DASHBOARD GENERATED")
    print("="*80)
    
    print(f"\n📊 Statistics:")
    print(f"  Total papers: {total}")
    print(f"  With PDFs: {with_pdf}")
    print(f"  Missing PDFs: {missing}")
    print(f"  IEEE (no access): {ieee}")
    print(f"  Coverage: {with_pdf}/{accessible} = {coverage:.1f}%")
    
    print(f"\n📁 Files created:")
    print(f"  • pac_dashboard.html - Interactive dashboard")
    print(f"  • pac_papers.json - Paper data")
    
    # Group by journal
    by_journal = {}
    for p in papers_data:
        journal = p.get('journal', 'Unknown')
        if journal not in by_journal:
            by_journal[journal] = {'total': 0, 'with_pdf': 0}
        by_journal[journal]['total'] += 1
        if p['has_pdf']:
            by_journal[journal]['with_pdf'] += 1
    
    print(f"\n📚 Coverage by Publisher:")
    for journal in sorted(by_journal.keys()):
        stats = by_journal[journal]
        if stats['total'] > 0:
            pct = stats['with_pdf'] / stats['total'] * 100
            status = "✅" if pct == 100 else ("⚠️" if pct > 0 else "❌")
            print(f"  {status} {journal}: {stats['with_pdf']}/{stats['total']} ({pct:.0f}%)")
    
    return coverage

def main():
    """Generate dashboard and open it."""
    
    # Generate data
    papers_data = generate_dashboard_data()
    coverage = generate_summary(papers_data)
    
    # Get absolute path to HTML file
    html_file = Path.cwd() / '.dev_pac' / 'pac_dashboard.html'
    
    print(f"\n🌐 Opening dashboard...")
    print(f"   file://{html_file}")
    
    # Open in browser
    webbrowser.open(f'file://{html_file}')
    
    print(f"\n💡 Tips:")
    print(f"  1. Select papers without PDFs")
    print(f"  2. Click 'Open Selected in Tabs' or 'Open in Batches'")
    print(f"  3. Authenticate with OpenAthens if prompted")
    print(f"  4. Save PDFs with Ctrl+S or Zotero Connector")
    print(f"  5. Move downloaded PDFs to appropriate directories")
    
    print(f"\n📂 Download PDFs to:")
    print(f"  ~/.scitex/scholar/library/MASTER/<8-digit-id>/")
    
    # List papers without PDFs for quick reference
    missing_non_ieee = [p for p in papers_data 
                        if not p['has_pdf'] and 'IEEE' not in p.get('journal', '')]
    
    if missing_non_ieee:
        print(f"\n❌ Papers still needing PDFs ({len(missing_non_ieee)}):")
        for p in missing_non_ieee[:5]:
            print(f"  • {p['name']}")
        if len(missing_non_ieee) > 5:
            print(f"  ... and {len(missing_non_ieee) - 5} more")

if __name__ == "__main__":
    main()