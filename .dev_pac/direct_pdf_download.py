#!/usr/bin/env python3
"""Direct PDF download using wget with authentication cookies."""

import subprocess
import json
from pathlib import Path
import time

def get_cookie_header():
    """Get authentication cookies from Chrome profile."""
    # Chrome stores cookies in a SQLite database
    # For now, use the authenticated Chrome profile
    return None

def download_pdf_direct(url, output_path, cookies=None):
    """Download PDF directly using wget."""
    
    args = [
        'wget',
        '--no-check-certificate',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        '--timeout=30',
        '--tries=2',
        '-O', str(output_path)
    ]
    
    if cookies:
        args.extend(['--header', f'Cookie: {cookies}'])
    
    args.append(url)
    
    result = subprocess.run(args, capture_output=True, text=True)
    
    if result.returncode == 0 and output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        if size_mb > 0.05:  # At least 50KB
            return True
    
    # Clean up failed download
    if output_path.exists():
        output_path.unlink()
    
    return False

def try_download_strategies(paper, target_dir):
    """Try multiple download strategies."""
    
    doi = paper['doi']
    journal = paper['journal']
    name = paper['name']
    
    print(f"\n📄 {name}")
    print(f"   Journal: {journal}")
    
    strategies = []
    
    # Strategy 1: Direct PDF URLs for open access
    if 'MDPI' in journal or 'Sensors' in journal or 'Mathematics' in journal or 'Brain Sciences' in journal:
        # MDPI direct PDF
        if '10.3390/' in doi:
            article = doi.split('/')[-1]
            strategies.append({
                'name': 'MDPI Direct',
                'url': f'https://www.mdpi.com/{article}/pdf'
            })
    
    elif 'Frontiers' in journal:
        # Frontiers direct PDF
        article_id = doi.split('.')[-1]
        strategies.append({
            'name': 'Frontiers Direct',
            'url': f'https://www.frontiersin.org/articles/{doi}/pdf'
        })
    
    elif 'BMC' in journal:
        # BMC direct PDF
        article_id = doi.split('/')[-1]
        strategies.append({
            'name': 'BMC Direct',
            'url': f'https://bmcneurosci.biomedcentral.com/counter/pdf/{doi}'
        })
    
    elif 'PeerJ' in journal:
        # PeerJ direct PDF
        if 'peerj-cs' in doi:
            article_id = doi.split('.')[-1]
            strategies.append({
                'name': 'PeerJ Direct',
                'url': f'https://peerj.com/articles/cs-{article_id}.pdf'
            })
        else:
            strategies.append({
                'name': 'PeerJ Direct',
                'url': f'https://peerj.com/articles/{doi.split("/")[-1]}.pdf'
            })
    
    elif 'Nature' in journal or 'Scientific Reports' in journal:
        # Nature/SR direct PDF
        if 'rs.3.rs-' not in doi:  # Skip preprints
            article_id = doi.split('/')[-1]
            strategies.append({
                'name': 'Nature Direct',
                'url': f'https://www.nature.com/articles/{article_id}.pdf'
            })
    
    elif 'Hindawi' in journal or 'Computational Intelligence' in journal or 'Applied Bionics' in journal:
        # Hindawi direct PDF
        if '10.1155/' in doi:
            year = doi.split('/')[-2]
            article_id = doi.split('/')[-1]
            strategies.append({
                'name': 'Hindawi Direct',
                'url': f'https://downloads.hindawi.com/journals/cin/{year}/{article_id}.pdf'
            })
            strategies.append({
                'name': 'Hindawi Alt',
                'url': f'https://downloads.hindawi.com/journals/{year}/{article_id}.pdf'
            })
    
    # Always try DOI as fallback
    strategies.append({
        'name': 'DOI',
        'url': f'https://doi.org/{doi}'
    })
    
    # Try each strategy
    for strategy in strategies:
        print(f"   🎯 Trying {strategy['name']}: {strategy['url']}")
        
        pdf_path = target_dir / f"{name}.pdf"
        
        if download_pdf_direct(strategy['url'], pdf_path):
            print(f"   ✅ SUCCESS! Downloaded {pdf_path.stat().st_size / (1024*1024):.1f} MB")
            return True
        else:
            print(f"   ❌ Failed")
    
    return False

def main():
    """Direct PDF download for missing papers."""
    
    print("="*80)
    print("DIRECT PDF DOWNLOADER")
    print("="*80)
    
    # Load missing papers
    analysis_file = Path('.dev_pac/missing_pdfs_analysis.json')
    with open(analysis_file) as f:
        data = json.load(f)
    
    missing_papers = data['missing_pdfs']
    
    print(f"\n📊 Found {len(missing_papers)} papers without PDFs")
    
    downloaded = 0
    failed = []
    
    for paper in missing_papers:
        # Get target directory
        pac_dir = Path.home() / '.scitex/scholar/library/pac'
        paper_dir = pac_dir / paper['name']
        
        if paper_dir.is_symlink():
            target_dir = paper_dir.resolve()
            
            # Check if PDF already exists
            existing_pdfs = list(target_dir.glob('*.pdf'))
            if existing_pdfs:
                print(f"\n⏭️  Skipping {paper['name']} - already has PDF")
                continue
            
            # Try to download
            if try_download_strategies(paper, target_dir):
                downloaded += 1
            else:
                failed.append(paper)
            
            # Small delay between downloads
            time.sleep(2)
    
    print("\n" + "="*80)
    print("DOWNLOAD RESULTS")
    print("="*80)
    print(f"✅ Successfully downloaded: {downloaded}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print("\nFailed papers:")
        for p in failed[:10]:
            print(f"  • {p['name']} ({p['journal']})")
    
    # Check final status
    print("\n" + "="*80)
    print("FINAL STATUS")
    print("="*80)
    subprocess.run(['python', '.dev_pac/check_pdf_details.py'])

if __name__ == "__main__":
    main()