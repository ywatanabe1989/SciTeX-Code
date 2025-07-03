#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:35:00"
# Author: ywatanabe
# Filename: basic_search_example.py

"""
Basic example of using SciTeX Scholar for scientific literature search.

This example demonstrates:
1. Simple web search
2. Local PDF search
3. Combined search with vector similarity
4. Building local index
"""

import scitex
import asyncio
from pathlib import Path


def demo_simple_search():
    """Demonstrate simple synchronous search."""
    print("=== Simple Web Search ===")
    
    # Search for papers about deep learning (web only by default)
    papers = scitex.scholar.search_sync(
        "deep learning transformer architecture",
        max_results=5
    )
    
    print(f"Found {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}")
        if len(paper.authors) > 3:
            print(f"            ... and {len(paper.authors) - 3} more")
        print(f"   Year: {paper.year}")
        print(f"   Source: {paper.source}")
        if paper.doi:
            print(f"   DOI: {paper.doi}")


def demo_local_search():
    """Demonstrate local PDF search."""
    print("\n=== Local PDF Search ===")
    
    # Search in current directory for PDFs
    papers = scitex.scholar.search_sync(
        "neural networks",
        web=False,
        local=["."],  # Current directory
        max_results=5
    )
    
    if papers:
        print(f"Found {len(papers)} local papers:")
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Path: {paper.pdf_path}")
    else:
        print("No local papers found in current directory")


def demo_combined_search():
    """Demonstrate combined web and local search."""
    print("\n=== Combined Search (Web + Local) ===")
    
    # Search both web and local sources
    papers = scitex.scholar.search_sync(
        "machine learning applications",
        web=True,
        local=[".", "./papers"],  # Search current dir and papers dir
        max_results=10,
        use_vector_search=True  # Use semantic similarity
    )
    
    print(f"Found {len(papers)} papers total:")
    
    # Group by source
    by_source = {}
    for paper in papers:
        by_source.setdefault(paper.source, []).append(paper)
    
    for source, source_papers in by_source.items():
        print(f"\n{source}: {len(source_papers)} papers")
        for paper in source_papers[:3]:  # Show first 3 from each source
            print(f"  - {paper.title[:80]}...")


async def demo_async_search_with_download():
    """Demonstrate async search with PDF download."""
    print("\n=== Async Search with PDF Download ===")
    
    # Search and download PDFs
    papers = await scitex.scholar.search(
        "attention mechanism deep learning",
        web=True,
        local=[],  # No local search
        max_results=3,
        download_pdfs=True,  # Download available PDFs
        web_sources=["arxiv"]  # Only search arXiv for downloadable papers
    )
    
    print(f"Found and downloaded {len(papers)} papers:")
    for paper in papers:
        print(f"\n- {paper.title}")
        if paper.has_pdf():
            print(f"  PDF saved to: {paper.pdf_path}")
        else:
            print("  PDF not available")


def demo_build_index():
    """Demonstrate building a local index."""
    print("\n=== Building Local Index ===")
    
    # Build index for faster future searches
    stats = scitex.scholar.build_index(
        paths=["."],  # Index current directory
        recursive=True,
        build_vector_index=False  # Skip vector embeddings for speed
    )
    
    print("Index statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def demo_paper_object():
    """Demonstrate working with Paper objects."""
    print("\n=== Working with Paper Objects ===")
    
    # Create a paper manually
    paper = scitex.scholar.Paper(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        abstract="The dominant sequence transduction models...",
        source="arxiv",
        year=2017,
        arxiv_id="1706.03762",
        keywords=["transformer", "attention", "deep learning"]
    )
    
    print("Paper details:")
    print(paper)
    
    print("\nBibTeX entry:")
    print(paper.to_bibtex())
    
    print(f"\nUnique identifier: {paper.get_identifier()}")


def demo_environment_setup():
    """Show how to configure the scholar directory."""
    print("\n=== Environment Configuration ===")
    
    # Get current scholar directory
    scholar_dir = scitex.scholar.get_scholar_dir()
    print(f"Scholar directory: {scholar_dir}")
    
    # You can set SciTeX_SCHOLAR_DIR environment variable to change it
    print("\nTo change the default directory, set:")
    print("export SciTeX_SCHOLAR_DIR='~/my_papers'")


def main():
    """Run all demonstrations."""
    print("SciTeX Scholar - Scientific Literature Search Demo")
    print("=" * 50)
    
    # 1. Simple search
    demo_simple_search()
    
    # 2. Local search
    demo_local_search()
    
    # 3. Combined search
    demo_combined_search()
    
    # 4. Async search with download
    print("\n(Running async example...)")
    asyncio.run(demo_async_search_with_download())
    
    # 5. Build index
    demo_build_index()
    
    # 6. Paper object
    demo_paper_object()
    
    # 7. Environment setup
    demo_environment_setup()
    
    print("\n" + "=" * 50)
    print("Demo completed!")


if __name__ == "__main__":
    main()