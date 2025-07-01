#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:28:00 (ywatanabe)"
# File: ./examples/scholar/basic_scholar_example.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/scholar/basic_scholar_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic scholar module usage
  - Shows how to create and search papers
  - Illustrates PDF downloader functionality
  - Examples of building search index

Dependencies:
  - packages: scitex
Input:
  - None (example script)
Output:
  - Console output showing scholar functionality
"""

"""Imports"""
import sys
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scitex.scholar import (
    Paper,
    PDFDownloader,
    LocalSearchEngine,
    build_index,
    get_scholar_dir,
    search_sync
)

"""Functions"""
def demo_paper_creation():
    """Demonstrate creating Paper objects."""
    print("=== Paper Creation Demo ===")
    
    # Create a paper instance
    paper = Paper(
        title="Deep Learning for Scientific Computing",
        authors=["John Doe", "Jane Smith"],
        year=2025,
        journal="Journal of Computational Science",
        abstract="This paper explores deep learning applications in scientific computing...",
        doi="10.1234/example.2025.001"
    )
    
    print(f"Created paper: {paper}")
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Journal: {paper.journal}")
    print()
    

def demo_pdf_downloader():
    """Demonstrate PDF downloader functionality."""
    print("=== PDF Downloader Demo ===")
    
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as tmpdir:
        downloader = PDFDownloader(download_dir=tmpdir)
        print(f"Download directory: {downloader.download_dir}")
        
        # Note: Actual download would require a real PDF URL
        print("PDFDownloader initialized successfully")
    print()


def demo_local_search():
    """Demonstrate local search functionality."""
    print("=== Local Search Demo ===")
    
    # Get scholar directory
    scholar_dir = get_scholar_dir()
    print(f"Scholar directory: {scholar_dir}")
    
    # Create search engine
    search_engine = LocalSearchEngine()
    print("LocalSearchEngine initialized successfully")
    
    # Note: Actual search would require indexed documents
    print("Search functionality available")
    print()


def demo_search_index():
    """Demonstrate building search index."""
    print("=== Search Index Demo ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some sample files
        sample_file = Path(tmpdir) / "sample_paper.txt"
        sample_file.write_text(
            "This is a sample paper about machine learning and neural networks. "
            "It discusses various architectures and applications."
        )
        
        # Build index
        print(f"Building index for: {tmpdir}")
        try:
            build_index(tmpdir)
            print("Index built successfully")
        except Exception as e:
            print(f"Index building example (may require additional setup): {type(e).__name__}")
    print()


def main():
    """Main function demonstrating scholar module capabilities."""
    print("SciTeX Scholar Module - Basic Examples")
    print("=" * 40)
    print()
    
    # Run demonstrations
    demo_paper_creation()
    demo_pdf_downloader()
    demo_local_search()
    demo_search_index()
    
    print("All demonstrations completed!")
    return 0


if __name__ == "__main__":
    main()

# EOF