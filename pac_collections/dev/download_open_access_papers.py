#!/usr/bin/env python3
"""Download open access PAC papers from various sources."""

import json
import time
import os
from pathlib import Path
import subprocess

def download_frontiers_paper(url, title, output_dir):
    """Download paper from Frontiers (usually open access)."""
    # Frontiers papers typically have direct PDF links
    if 'frontiersin.org' in url:
        # Try to construct PDF URL
        if '/articles/' in url:
            pdf_url = url.replace('/articles/', '/files/') + '/pdf'
        else:
            pdf_url = url
        
        filename = f"{title[:50].replace(' ', '_').replace('/', '_')}.pdf"
        output_path = output_dir / filename
        
        cmd = [
            'wget', '-q', 
            '-O', str(output_path),
            '--user-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            pdf_url
        ]
        
        try:
            subprocess.run(cmd, check=True, timeout=30)
            if output_path.exists() and output_path.stat().st_size > 1000:
                return True, output_path
        except:
            pass
    
    return False, None

def download_arxiv_paper(url, title, output_dir):
    """Download paper from arXiv."""
    if 'arxiv.org' in url:
        # Extract arXiv ID
        arxiv_id = url.split('/')[-1]
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        filename = f"{title[:50].replace(' ', '_').replace('/', '_')}.pdf"
        output_path = output_dir / filename
        
        cmd = [
            'wget', '-q',
            '-O', str(output_path),
            pdf_url
        ]
        
        try:
            subprocess.run(cmd, check=True, timeout=30)
            if output_path.exists() and output_path.stat().st_size > 1000:
                return True, output_path
        except:
            pass
    
    return False, None

def main():
    # Load categorized papers
    with open('pac_collections/dev/pac_papers_categorized.json') as f:
        data = json.load(f)
    
    output_dir = Path('pac_collections/dev/downloaded_pdfs')
    output_dir.mkdir(exist_ok=True)
    
    results = {
        'downloaded': [],
        'failed': [],
        'skipped': []
    }
    
    # Try downloading papers from different sources
    all_papers = []
    for category, papers in data['categories'].items():
        for paper in papers:
            paper['category'] = category
            all_papers.append(paper)
    
    print(f"Processing {len(all_papers)} papers...")
    
    for i, paper in enumerate(all_papers[:10], 1):  # Test with first 10
        title = paper['title']
        url = paper['url']
        category = paper['category']
        
        print(f"\n[{i}/10] Processing: {title[:60]}...")
        print(f"  Category: {category}")
        print(f"  URL: {url[:80]}...")
        
        success = False
        output_path = None
        
        # Try different download methods based on source
        if category == 'other' and 'arxiv' in url:
            success, output_path = download_arxiv_paper(url, title, output_dir)
        elif category == 'frontiers':
            success, output_path = download_frontiers_paper(url, title, output_dir)
        else:
            # Skip papers that need authentication
            results['skipped'].append({
                'title': title,
                'category': category,
                'reason': 'Requires authentication or manual download'
            })
            print("  Status: Skipped (requires auth)")
            continue
        
        if success:
            results['downloaded'].append({
                'title': title,
                'category': category,
                'path': str(output_path)
            })
            print(f"  Status: ✅ Downloaded to {output_path.name}")
        else:
            results['failed'].append({
                'title': title,
                'category': category,
                'url': url
            })
            print("  Status: ❌ Failed")
        
        # Rate limiting
        time.sleep(1)
    
    # Save results
    results_file = output_dir / 'download_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Downloaded: {len(results['downloaded'])} papers")
    print(f"Failed: {len(results['failed'])} papers")
    print(f"Skipped: {len(results['skipped'])} papers")
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()