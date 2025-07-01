#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example of creating an enriched bibliography with impact factors.

This example shows how to:
1. Search for papers
2. Enrich them with journal metrics
3. Generate a bibliography with citation counts and impact factors
"""

import asyncio
from pathlib import Path
from scitex.scholar import (
    search_papers, 
    PaperEnrichmentService,
    generate_enriched_bibliography
)

async def main():
    """Create an enriched bibliography."""
    
    # Search for papers
    print("Searching for neuroscience papers...")
    papers = await search_papers(
        query="neural oscillations cognitive neuroscience",
        limit=10
    )
    
    if not papers:
        print("No papers found.")
        return
    
    print(f"Found {len(papers)} papers")
    
    # Enrich papers with journal metrics
    print("\nEnriching papers with journal metrics...")
    enricher = PaperEnrichmentService()
    enriched_papers = enricher.enrich_papers(papers)
    
    # Count papers with impact factors
    with_if = sum(1 for p in enriched_papers if p.impact_factor is not None)
    print(f"Papers with impact factor data: {with_if}/{len(enriched_papers)}")
    
    # Generate bibliography file
    output_path = Path("enriched_bibliography.bib")
    generate_enriched_bibliography(
        enriched_papers,
        output_path,
        enrich=False  # Already enriched
    )
    
    print(f"\nBibliography saved to: {output_path}")
    
    # Show summary statistics
    total_citations = sum(p.citation_count or 0 for p in enriched_papers)
    avg_citations = total_citations / len(enriched_papers) if enriched_papers else 0
    
    print(f"\nSummary Statistics:")
    print(f"- Total papers: {len(enriched_papers)}")
    print(f"- Total citations: {total_citations}")
    print(f"- Average citations: {avg_citations:.1f}")
    print(f"- Papers with impact factor: {with_if}")

if __name__ == "__main__":
    asyncio.run(main())