#!/usr/bin/env python3
"""Download all papers from papers.bib file using multiple strategies."""

import re
import bibtexparser
from pathlib import Path
from scitex.scholar import Scholar
from scitex import logging
import time

logger = logging.getLogger(__name__)

def parse_bibtex_file(bib_file):
    """Parse BibTeX file and extract paper information."""
    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)
    
    papers = []
    for entry in bib_database.entries:
        paper_info = {
            'id': entry.get('ID', ''),
            'title': entry.get('title', ''),
            'author': entry.get('author', ''),
            'year': entry.get('year', ''),
            'journal': entry.get('journal', ''),
            'url': entry.get('url', ''),
            'doi': None
        }
        
        # Try to extract DOI from URL if present
        url = entry.get('url', '')
        
        # Pattern 1: https://doi.org/...
        doi_match = re.search(r'https?://doi\.org/(.+)$', url)
        if doi_match:
            paper_info['doi'] = doi_match.group(1)
        
        # Pattern 2: DOI in URL parameters
        doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
        if doi_match and not paper_info['doi']:
            paper_info['doi'] = doi_match.group(1)
        
        # Pattern 3: ArXiv IDs
        arxiv_match = re.search(r'arxiv\.org/abs/(.+)$', url, re.IGNORECASE)
        if arxiv_match:
            paper_info['arxiv_id'] = arxiv_match.group(1)
        
        papers.append(paper_info)
    
    return papers

def main():
    """Download all papers from BibTeX file."""
    
    # Configuration
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Parse BibTeX file
    print(f"Parsing BibTeX file: {bib_file}")
    papers = parse_bibtex_file(bib_file)
    print(f"Found {len(papers)} papers in BibTeX file")
    
    # Initialize Scholar
    print("\nInitializing Scholar module...")
    scholar = Scholar()
    
    # Results tracking
    results = []
    successful = 0
    failed = 0
    
    print(f"\nStarting download process...")
    print("="*80)
    
    for i, paper_info in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] Processing: {paper_info['title'][:60]}...")
        print(f"  ID: {paper_info['id']}")
        
        if paper_info['doi']:
            print(f"  DOI: {paper_info['doi']}")
        
        try:
            # Build search query
            if paper_info['doi']:
                # Search by DOI first
                query = f"doi:{paper_info['doi']}"
            else:
                # Search by title
                query = paper_info['title']
            
            # Search for paper
            print("  Searching...")
            found_papers = scholar.search(query, max_results=1)
            
            if found_papers:
                paper = found_papers[0]
                print(f"  Found: {paper.title[:60]}...")
                
                # Try to download PDF
                print("  Attempting download...")
                papers_with_pdf = scholar.download_pdfs(
                    papers=[paper],
                    output_dir=str(output_dir)
                )
                
                if papers_with_pdf and papers_with_pdf[0].pdf_path:
                    print(f"  ✅ Success: {papers_with_pdf[0].pdf_path}")
                    successful += 1
                    results.append({
                        'id': paper_info['id'],
                        'title': paper_info['title'],
                        'success': True,
                        'path': papers_with_pdf[0].pdf_path
                    })
                else:
                    print("  ❌ Failed: PDF not available")
                    failed += 1
                    results.append({
                        'id': paper_info['id'],
                        'title': paper_info['title'],
                        'success': False,
                        'error': 'PDF not available'
                    })
            else:
                print("  ❌ Failed: Paper not found in search")
                failed += 1
                results.append({
                    'id': paper_info['id'],
                    'title': paper_info['title'],
                    'success': False,
                    'error': 'Not found in search'
                })
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
            failed += 1
            results.append({
                'id': paper_info['id'],
                'title': paper_info['title'],
                'success': False,
                'error': str(e)
            })
        
        # Rate limiting
        time.sleep(1)
        
        # Progress summary every 10 papers
        if i % 10 == 0:
            print(f"\n--- Progress: {successful} successful, {failed} failed out of {i} processed ---")
    
    # Final summary
    print("\n" + "="*80)
    print("DOWNLOAD SUMMARY")
    print("="*80)
    print(f"\nTotal papers: {len(papers)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    
    # Save results to file
    results_file = output_dir / "download_results.txt"
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(f"Download Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Successful downloads
        f.write("SUCCESSFUL DOWNLOADS:\n")
        f.write("-"*40 + "\n")
        for r in results:
            if r['success']:
                f.write(f"{r['id']}: {r['title']}\n")
                f.write(f"  Path: {r['path']}\n\n")
        
        # Failed downloads
        f.write("\n\nFAILED DOWNLOADS:\n")
        f.write("-"*40 + "\n")
        for r in results:
            if not r['success']:
                f.write(f"{r['id']}: {r['title']}\n")
                f.write(f"  Error: {r['error']}\n\n")
    
    print(f"\nResults saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise