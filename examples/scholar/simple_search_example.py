#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple example of using scitex.scholar for literature search.

This example shows how to:
1. Search for papers from Semantic Scholar
2. Generate a BibTeX bibliography
3. Display paper metadata
"""

import asyncio
from scitex.scholar import search_papers, Paper

async def main():
    """Run a simple literature search."""
    
    # Search for papers about phase-amplitude coupling
    print("Searching for papers about phase-amplitude coupling...")
    papers = await search_papers(
        query="phase amplitude coupling brain",
        limit=5
    )
    
    if not papers:
        print("No papers found. Check your internet connection.")
        return
    
    print(f"\nFound {len(papers)} papers:\n")
    
    # Display paper information
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}")
        if len(paper.authors) > 3:
            print(f"            et al. ({len(paper.authors)} authors)")
        print(f"   Year: {paper.year}")
        print(f"   Citations: {paper.citation_count}")
        print()
    
    # Generate BibTeX
    print("\nBibTeX entries:")
    print("-" * 60)
    for paper in papers:
        print(paper.to_bibtex(include_enriched=True))
        print()

if __name__ == "__main__":
    asyncio.run(main())