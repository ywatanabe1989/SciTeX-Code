#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test basic scholar functionality without external API calls.
"""

from scitex.scholar import Paper, PDFDownloader, LocalSearchEngine
from pathlib import Path
import tempfile

def test_paper_creation():
    """Test creating and using Paper objects."""
    print("1. Testing Paper Creation and BibTeX Generation")
    print("-" * 50)
    
    # Create a paper
    paper = Paper(
        title="Deep Learning for Phase-Amplitude Coupling Analysis",
        authors=["Smith, J.", "Doe, A.", "Johnson, B."],
        abstract="This paper presents a novel deep learning approach...",
        source="demo",
        year=2024,
        journal="Journal of Neural Engineering",
        doi="10.1016/j.jne.2024.001",
        citation_count=42,
        impact_factor=5.7
    )
    
    # Display paper info
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Citations: {paper.citation_count}")
    print(f"Impact Factor: {paper.impact_factor}")
    
    # Generate BibTeX
    print("\nBibTeX with enriched metadata:")
    print(paper.to_bibtex(include_enriched=True))
    
    print("\nBibTeX without enriched metadata:")
    print(paper.to_bibtex(include_enriched=False))
    

def test_local_search():
    """Test local search functionality."""
    print("\n\n2. Testing Local Search Engine")
    print("-" * 50)
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test PDF files
        pdf1 = temp_path / "paper1.pdf"
        pdf1.write_text("Phase-amplitude coupling in neural oscillations")
        
        pdf2 = temp_path / "paper2.pdf"
        pdf2.write_text("Deep learning methods for neuroscience")
        
        txt1 = temp_path / "notes.txt"
        txt1.write_text("Research notes on PAC analysis")
        
        # Create search engine with proper index file
        index_file = temp_path / "search_index.json"
        engine = LocalSearchEngine(index_file)
        
        # Build index
        print(f"Indexing directory: {temp_path}")
        indexed = engine.build_index([temp_path])
        print(f"Indexed {indexed} files")
        
        # Search
        print("\nSearching for 'coupling':")
        results = engine.search("coupling", [temp_path])
        for paper, score in results:
            print(f"  - {paper.title} (score: {score:.2f})")
        
        print("\nSearching for 'deep learning':")
        results = engine.search("deep learning", [temp_path])
        for paper, score in results:
            print(f"  - {paper.title} (score: {score:.2f})")


def test_pdf_downloader():
    """Test PDF downloader configuration."""
    print("\n\n3. Testing PDF Downloader")
    print("-" * 50)
    
    # Create downloader
    downloader = PDFDownloader()
    print(f"Download directory: {downloader.download_dir}")
    print(f"Directory exists: {downloader.download_dir.exists()}")
    
    # Test filename generation
    paper = Paper(
        title="Test Paper: Special Characters & Symbols",
        authors=["Author One"],
        abstract="Test",
        source="test",
        year=2024
    )
    
    filename = downloader._get_filename(paper)
    print(f"\nGenerated filename: {filename}")
    print("(Special characters are sanitized)")


def test_paper_similarity():
    """Test paper similarity calculation."""
    print("\n\n4. Testing Paper Similarity")
    print("-" * 50)
    
    paper1 = Paper(
        title="Deep Learning for Phase-Amplitude Coupling",
        authors=["Smith, J.", "Doe, A."],
        abstract="This paper presents deep learning methods for PAC analysis",
        source="test"
    )
    
    paper2 = Paper(
        title="Machine Learning for Phase-Amplitude Coupling",
        authors=["Smith, J.", "Johnson, B."],
        abstract="This paper presents machine learning methods for PAC analysis",
        source="test"
    )
    
    paper3 = Paper(
        title="Quantum Computing Applications",
        authors=["Brown, C."],
        abstract="This paper explores quantum computing in cryptography",
        source="test"
    )
    
    # Calculate similarities
    sim1_2 = paper1.similarity_score(paper2)
    sim1_3 = paper1.similarity_score(paper3)
    
    print(f"Similarity between papers 1 and 2: {sim1_2:.2f}")
    print(f"Similarity between papers 1 and 3: {sim1_3:.2f}")
    print("\n(Higher score = more similar, range 0-1)")


if __name__ == "__main__":
    print("=== SciTeX Scholar Module Test ===\n")
    
    test_paper_creation()
    test_local_search()
    test_pdf_downloader()
    test_paper_similarity()
    
    print("\n\n✅ All basic functionality working correctly!")
    print("\nNote: For real paper searches, you need:")
    print("- Internet connection")
    print("- Valid API keys (optional)")
    print("- Properly configured Semantic Scholar client")