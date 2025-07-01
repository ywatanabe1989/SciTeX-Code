#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:30:00 (ywatanabe)"
# File: examples/scitex_scholar/paper_acquisition_example.py

"""
Example: Automated paper discovery and download.

This example demonstrates:
- Searching papers from multiple sources
- Filtering by year and metadata
- Downloading available PDFs
- Working with paper metadata
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, './src')

from scitex_scholar.paper_acquisition import PaperAcquisition


async def main():
    """Demonstrate paper acquisition capabilities."""
    
    print("=== Paper Acquisition Example ===\n")
    
    # Initialize acquisition system
    acquisition = PaperAcquisition(
        download_dir=Path("./example_downloads"),
        email="research@example.com"  # Use your email
    )
    
    # Example 1: Search PubMed
    print("1. Search PubMed for Recent Papers")
    print("-" * 40)
    
    pubmed_papers = await acquisition.search(
        query="deep learning EEG analysis",
        sources=['pubmed'],
        max_results=5,
        start_year=2022,
        end_year=2024
    )
    
    print(f"Found {len(pubmed_papers)} papers from PubMed:")
    for i, paper in enumerate(pubmed_papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Year: {paper.year} | Journal: {paper.journal}")
        print(f"   PMID: {paper.pmid}")
    
    # Example 2: Search arXiv
    print("\n\n2. Search arXiv for Preprints")
    print("-" * 40)
    
    arxiv_papers = await acquisition.search(
        query="transformer medical imaging",
        sources=['arxiv'],
        max_results=5
    )
    
    print(f"Found {len(arxiv_papers)} papers from arXiv:")
    for i, paper in enumerate(arxiv_papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   arXiv ID: {paper.arxiv_id}")
        print(f"   Categories: {', '.join(paper.keywords[:3])}")
    
    # Example 3: Multi-source Search
    print("\n\n3. Multi-source Search")
    print("-" * 40)
    
    all_papers = await acquisition.search(
        query="seizure prediction machine learning",
        sources=['pubmed', 'arxiv'],
        max_results=10
    )
    
    # Group by source
    by_source = {}
    for paper in all_papers:
        by_source.setdefault(paper.source, []).append(paper)
    
    print(f"Total papers found: {len(all_papers)}")
    for source, papers in by_source.items():
        print(f"  - {source}: {len(papers)} papers")
    
    # Example 4: Download Papers
    print("\n\n4. Download Available Papers")
    print("-" * 40)
    
    # Download first 3 arXiv papers (they're freely available)
    to_download = [p for p in arxiv_papers if p.pdf_url][:3]
    
    if to_download:
        print(f"Downloading {len(to_download)} papers...")
        
        downloaded = await acquisition.batch_download(to_download)
        
        print(f"\nSuccessfully downloaded {len(downloaded)} papers:")
        for title, path in downloaded.items():
            print(f"  ✓ {path.name}")
    else:
        print("No downloadable papers found.")
    
    # Example 5: Extract Metadata
    print("\n\n5. Paper Metadata Analysis")
    print("-" * 40)
    
    # Analyze keywords across all papers
    all_keywords = []
    for paper in all_papers[:10]:
        all_keywords.extend(paper.keywords)
    
    # Count keyword frequency
    keyword_counts = {}
    for kw in all_keywords:
        keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
    
    # Show top keywords
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top keywords in search results:")
    for keyword, count in top_keywords:
        print(f"  - {keyword}: {count} papers")


if __name__ == "__main__":
    print("Note: This example requires internet connection")
    print("and will create an 'example_downloads' directory.\n")
    
    asyncio.run(main())

# EOF