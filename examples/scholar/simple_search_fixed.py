#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple example of using scitex.scholar for literature search.
Fixed version with proper field specification.
"""

import asyncio
from scitex.scholar import SemanticScholarClient, Paper

async def main():
    """Run a simple literature search."""
    
    # Create client with limited fields to avoid API errors
    client = SemanticScholarClient()
    
    print("Searching for papers about phase-amplitude coupling...")
    try:
        # Use limited field set that works with the API
        papers = await client.search_papers(
            query="phase amplitude coupling brain",
            limit=5,
            fields="title,authors,year,venue,citationCount"
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
        for paper in papers[:2]:  # Just show first 2
            print(paper.to_bibtex(include_enriched=True))
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying a simpler search...")
        
        # Fallback to even simpler search
        papers = await client.search_papers(
            query="machine learning",
            limit=3,
            fields="title,authors,year"
        )
        
        for paper in papers:
            print(f"- {paper.title} ({paper.year})")

if __name__ == "__main__":
    asyncio.run(main())