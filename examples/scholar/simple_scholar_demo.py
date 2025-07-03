#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 09:35:00 (ywatanabe)"
# File: ./examples/scholar/simple_scholar_demo.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scholar/simple_scholar_demo.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Simple demonstration of the new unified Scholar class.

This script shows how the Scholar class simplifies literature management
with a single entry point and method chaining.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scitex.scholar import Scholar


def main():
    """Demonstrate the new Scholar class interface."""
    
    print("🔬 SciTeX Scholar - Unified Interface Demo")
    print("=" * 50)
    
    # Initialize Scholar with smart defaults
    print("\n1. Initializing Scholar...")
    scholar = Scholar(
        email="demo@example.com",
        enrich_by_default=True,  # Automatic journal metrics
        download_dir="./demo_pdfs"
    )
    print("✅ Scholar initialized with automatic enrichment")
    
    # Simple search
    print("\n2. Simple literature search...")
    papers = scholar.search("deep learning", limit=5)
    print(f"✅ Found {len(papers)} papers")
    
    if papers:
        print(f"\nFirst paper:")
        print(f"   Title: {papers[0].title}")
        print(f"   Journal: {papers[0].journal}")
        print(f"   Year: {papers[0].year}")
        print(f"   Citations: {papers[0].citation_count}")
        if papers[0].impact_factor:
            print(f"   Impact Factor: {papers[0].impact_factor}")
    
    # Method chaining demonstration
    print("\n3. Method chaining for advanced workflow...")
    try:
        filtered_papers = papers.filter(year_min=2020) \
                                .sort_by("citations") \
                                .save("demo_papers.bib")
        
        print(f"✅ Filtered to {len(filtered_papers)} recent papers")
        print("✅ Saved bibliography to demo_papers.bib")
        
        # Show collection summary
        print("\n4. Collection analysis...")
        trends = filtered_papers.analyze_trends()
        print(f"   Year range: {trends.get('year_range', 'N/A')}")
        print(f"   Average citations: {trends.get('citation_statistics', {}).get('mean', 0):.1f}")
        print(f"   Open access: {trends.get('open_access_percentage', 0):.1f}%")
        
        if trends.get('top_journals'):
            top_journal = list(trends['top_journals'].keys())[0]
            print(f"   Top journal: {top_journal}")
        
    except Exception as e:
        print(f"⚠️  Advanced workflow failed: {e}")
    
    # Multiple topic search
    print("\n5. Multi-topic search...")
    try:
        topics = ["machine learning", "neural networks"]
        multi_papers = scholar.search_multiple(topics, papers_per_query=3)
        print(f"✅ Combined search found {len(multi_papers)} unique papers")
        
        # Quick search demo
        print("\n6. Quick utilities...")
        quick_titles = scholar.quick_search("BERT", top_n=3)
        print("Quick search results:")
        for i, title in enumerate(quick_titles, 1):
            print(f"   {i}. {title[:60]}...")
        
    except Exception as e:
        print(f"⚠️  Multi-topic search failed: {e}")
    
    # Context manager usage
    print("\n7. Context manager usage...")
    try:
        with Scholar() as s:
            ctx_papers = s.search("quantum computing", limit=3)
            print(f"✅ Context manager found {len(ctx_papers)} papers")
    except Exception as e:
        print(f"⚠️  Context manager failed: {e}")
    
    print("\n🎉 Demo completed!")
    print("\nThe Scholar class provides:")
    print("• Single entry point for all literature management")
    print("• Automatic enrichment with journal metrics")
    print("• Method chaining for fluent workflows")
    print("• Multiple export formats (BibTeX, CSV, JSON)")
    print("• Built-in analysis and filtering tools")
    print("• Progress feedback for long operations")
    
    print(f"\nExample usage:")
    print("scholar.search('topic').filter(year_min=2020).save('papers.bib')")


if __name__ == "__main__":
    main()