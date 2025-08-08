#!/usr/bin/env python3
"""Generate standalone HTML dashboard with embedded data."""

import json
from pathlib import Path
import webbrowser

def generate_standalone_dashboard():
    """Generate HTML with embedded paper data."""
    
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers_data = []
    
    # Collect paper data
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target = item.resolve()
            if target.exists():
                pdfs = list(target.glob('*.pdf'))
                has_pdf = len(pdfs) > 0
                
                metadata_file = target / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    
                    paper_info = {
                        'name': item.name,
                        'journal': metadata.get('journal', ''),
                        'doi': metadata.get('doi', ''),
                        'title': metadata.get('title', ''),
                        'has_pdf': has_pdf
                    }
                else:
                    paper_info = {
                        'name': item.name,
                        'journal': '',
                        'doi': '',
                        'title': item.name,
                        'has_pdf': has_pdf
                    }
                
                papers_data.append(paper_info)
    
    # Read template
    template_file = Path('.dev_pac/pac_dashboard_standalone.html')
    with open(template_file, 'r') as f:
        html_content = f.read()
    
    # Replace placeholder with actual data
    html_content = html_content.replace(
        'const papers = PAPER_DATA_PLACEHOLDER;',
        f'const papers = {json.dumps(papers_data, indent=2)};'
    )
    
    # Save complete HTML
    output_file = Path('.dev_pac/pac_dashboard_complete.html')
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    # Calculate stats
    total = len(papers_data)
    with_pdf = sum(1 for p in papers_data if p['has_pdf'])
    ieee = sum(1 for p in papers_data if 'IEEE' in p.get('journal', ''))
    missing = total - with_pdf - ieee
    coverage = (with_pdf / (total - ieee) * 100) if (total - ieee) > 0 else 0
    
    print("="*80)
    print("STANDALONE DASHBOARD GENERATED")
    print("="*80)
    print(f"\n📊 Current Status:")
    print(f"  Total: {total} papers")
    print(f"  With PDFs: {with_pdf} ✅")
    print(f"  Missing: {missing} ❌")
    print(f"  IEEE (no access): {ieee} 🚫")
    print(f"  Coverage: {coverage:.1f}%")
    
    print(f"\n📁 Dashboard saved to: {output_file.absolute()}")
    
    # Open in browser
    webbrowser.open(f'file://{output_file.absolute()}')
    
    print(f"\n💡 How to use:")
    print(f"  1. Filter to 'Missing PDFs' tab")
    print(f"  2. Click 'Select All Missing'")
    print(f"  3. Click 'Open in Batches (5)'")
    print(f"  4. Authenticate with OpenAthens when prompted")
    print(f"  5. Save PDFs with Ctrl+S")
    
    return output_file

if __name__ == "__main__":
    dashboard_file = generate_standalone_dashboard()