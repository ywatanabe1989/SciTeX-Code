#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:27:00 (ywatanabe)"
# File: ./examples/scholar_simple_example.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scholar_simple_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates the simplified Scholar API
  - Shows common workflows
  - Exports results in multiple formats

Dependencies:
  - scripts:
    - None
  - packages:
    - scitex

Input:
  - Search queries via command line

Output:
  - ./bibliography.bib
  - ./papers_summary.md
  - ./papers.json
"""

"""Imports"""
import argparse
import scitex as stx
from scitex.scholar import Scholar, search, quick_search

"""Functions & Classes"""
def main(args):
    """Demonstrate Scholar functionality."""
    
    # Method 1: Quick search without creating instance
    stx.str.printc("\n=== Quick Search ===", c="blue")
    titles = quick_search("deep learning", top_n=3)
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
    
    # Method 2: Using convenience function
    stx.str.printc("\n=== Convenience Search ===", c="blue")
    papers = search("machine learning", limit=5, year_min=2023)
    print(f"Found {len(papers)} recent papers")
    print(papers.summary())
    
    # Method 3: Full Scholar instance with all features
    stx.str.printc("\n=== Full Scholar Example ===", c="blue")
    
    # Initialize with auto-enrichment
    scholar = Scholar(auto_enrich=True)
    
    # Search with filters
    query = args.query or "neural networks"
    stx.str.printc(f"\nSearching for: '{query}'", c="green")
    
    papers = scholar.search(
        query,
        limit=args.limit,
        year_min=args.year_min,
        sources=['semantic_scholar', 'arxiv']  # Specify sources
    )
    
    print(f"Found {len(papers)} papers")
    
    # Filter results
    if args.min_citations:
        papers = papers.filter(min_citations=args.min_citations)
        print(f"After citation filter: {len(papers)} papers")
    
    # Sort by impact
    papers = papers.sort_by("impact_factor")
    
    # Show top papers
    stx.str.printc("\n=== Top Papers ===", c="blue")
    for i, paper in enumerate(papers[:5], 1):
        metrics = []
        if paper.citation_count:
            metrics.append(f"Citations: {paper.citation_count}")
        if paper.impact_factor:
            metrics.append(f"IF: {paper.impact_factor:.2f}")
        
        metrics_str = f" ({', '.join(metrics)})" if metrics else ""
        print(f"{i}. {paper.title}")
        print(f"   {paper.authors[0] if paper.authors else 'Unknown'} et al., {paper.year}{metrics_str}")
    
    # Analyze trends
    stx.str.printc("\n=== Collection Analysis ===", c="blue")
    trends = papers.analyze_trends()
    
    print(f"Total papers: {trends['total_papers']}")
    if trends['date_range']:
        print(f"Year range: {trends['date_range']['start']}-{trends['date_range']['end']}")
    
    if trends['top_journals']:
        print("\nTop journals:")
        for journal, count in list(trends['top_journals'].items())[:3]:
            print(f"  - {journal}: {count} papers")
    
    if trends['keyword_analysis']:
        print("\nTop keywords:")
        for keyword, count in list(trends['keyword_analysis'].items())[:5]:
            print(f"  - {keyword}: {count}")
    
    # Save in multiple formats
    if args.save and papers:
        stx.str.printc("\n=== Saving Results ===", c="blue")
        
        # BibTeX
        bib_path = papers.save("./bibliography.bib", format="bibtex")
        print(f"Saved BibTeX: {bib_path}")
        
        # Markdown summary
        from scitex.scholar import papers_to_markdown
        md_content = papers_to_markdown(papers.papers, group_by='year')
        md_path = stx.io.save(md_content, "./papers_summary.md", symlink_from_cwd=True)
        print(f"Saved Markdown: {md_path}")
        
        # JSON for further processing
        json_path = papers.save("./papers.json", format="json")
        print(f"Saved JSON: {json_path}")
    
    # Local library example
    if args.index_dir:
        stx.str.printc("\n=== Local Library ===", c="blue")
        stats = scholar.index_local_pdfs(args.index_dir)
        print(f"Indexed {stats['indexed']} PDFs")
        
        # Search local
        local_results = scholar.search_local(query, limit=5)
        print(f"Found {len(local_results)} local matches")
    
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate SciTeX Scholar functionality"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="deep learning",
        help="Search query (default: %(default)s)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=20,
        help="Maximum results (default: %(default)s)",
    )
    parser.add_argument(
        "--year-min",
        "-y",
        type=int,
        default=2020,
        help="Minimum publication year (default: %(default)s)",
    )
    parser.add_argument(
        "--min-citations",
        "-c",
        type=int,
        default=None,
        help="Minimum citation count filter",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        default=True,
        help="Save results to files (default: %(default)s)",
    )
    parser.add_argument(
        "--index-dir",
        "-i",
        type=str,
        help="Directory to index for local search",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF