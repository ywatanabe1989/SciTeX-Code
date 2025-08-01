#!/usr/bin/env python3
"""
Simple test to download papers using Scholar module.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Test import
try:
    from scitex.scholar._Scholar import Scholar
    from scitex.scholar._Papers import Papers
    print("✓ Scholar module imported successfully")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Load papers from BibTeX
bibtex_file = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/from_user/papers.bib"
print(f"\nLoading papers from: {bibtex_file}")

try:
    papers = Papers.from_bibtex(bibtex_file)
    print(f"✓ Loaded {len(papers)} papers")
    
    # Show first 3 papers
    print("\nFirst 3 papers:")
    for i, paper in enumerate(papers[:3]):
        print(f"\n{i+1}. {paper.title[:80]}...")
        print(f"   DOI: {paper.doi}")
        print(f"   Authors: {', '.join(paper.authors[:3]) if paper.authors else 'N/A'}")
        print(f"   Year: {paper.year}")
        
except Exception as e:
    print(f"✗ Error loading papers: {e}")
    import traceback
    traceback.print_exc()