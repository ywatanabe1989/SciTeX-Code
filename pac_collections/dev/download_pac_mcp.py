#!/usr/bin/env python3
"""Download PAC papers using MCP browser - simplified version."""

import json
import re
from pathlib import Path
import time

def parse_bibtex():
    """Parse bibtex file to extract papers."""
    bib_file = '/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/papers.bib'
    with open(bib_file, 'r') as f:
        content = f.read()
    
    entries = content.split('@')[1:]
    papers = []
    
    for entry in entries:
        lines = entry.strip().split('\n')
        
        title = author = year = journal = url = ''
        
        for line in lines[1:]:
            if 'title=' in line:
                match = re.search(r'title=\{([^}]+)\}', line)
                if match:
                    title = match.group(1)
            elif 'author=' in line:
                match = re.search(r'author=\{([^}]+)\}', line)
                if match:
                    author = match.group(1)
            elif 'year=' in line:
                match = re.search(r'year=\{(\d+)\}', line)
                if match:
                    year = match.group(1)
            elif 'journal=' in line:
                match = re.search(r'journal=\{([^}]+)\}', line)
                if match:
                    journal = match.group(1)
            elif 'url=' in line:
                match = re.search(r'url=\{([^}]+)\}', line)
                if match:
                    url = match.group(1)
        
        if title and url:
            papers.append({
                'title': title,
                'author': author,
                'year': year,
                'journal': journal,
                'url': url
            })
    
    return papers

def categorize_papers(papers):
    """Categorize papers by source."""
    categories = {
        'pubmed': [],
        'frontiers': [],
        'nature': [],
        'science': [],
        'sciencedirect': [],
        'ieee': [],
        'other': []
    }
    
    for paper in papers:
        url = paper['url'].lower()
        if 'ncbi.nlm.nih.gov' in url or 'pubmed' in url:
            categories['pubmed'].append(paper)
        elif 'frontiersin.org' in url:
            categories['frontiers'].append(paper)
        elif 'nature.com' in url:
            categories['nature'].append(paper)
        elif 'science.org' in url:
            categories['science'].append(paper)
        elif 'sciencedirect.com' in url:
            categories['sciencedirect'].append(paper)
        elif 'ieee.org' in url:
            categories['ieee'].append(paper)
        else:
            categories['other'].append(paper)
    
    return categories

def main():
    print("Parsing PAC papers from bibtex...")
    papers = parse_bibtex()
    print(f"Found {len(papers)} papers")
    
    categories = categorize_papers(papers)
    
    print("\nPapers by source:")
    for source, papers in categories.items():
        if papers:
            print(f"  {source}: {len(papers)} papers")
    
    # Save categorized papers
    output_file = Path('pac_collections/dev/pac_papers_categorized.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'total': len(papers),
            'categories': {k: v for k, v in categories.items() if v},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, indent=2)
    
    print(f"\nSaved categorized papers to {output_file}")
    
    # Show first paper from each category for testing
    print("\nSample papers from each category:")
    for source, papers in categories.items():
        if papers:
            p = papers[0]
            print(f"\n{source.upper()}:")
            print(f"  Title: {p['title'][:60]}...")
            print(f"  URL: {p['url'][:80]}...")

if __name__ == "__main__":
    main()