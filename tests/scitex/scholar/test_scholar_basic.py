#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:40:00"
# Author: Claude
# Filename: test_scholar_basic.py

"""
Basic tests for the SciTeX Scholar module.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

import scitex.scholar


class TestScholarBasic:
    """Basic tests for scholar module."""
    
    def test_import(self):
        """Test that module imports correctly."""
        assert hasattr(scitex.scholar, 'search')
        assert hasattr(scitex.scholar, 'search_sync')
        assert hasattr(scitex.scholar, 'build_index')
        assert hasattr(scitex.scholar, 'Paper')
        assert hasattr(scitex.scholar, 'get_scholar_dir')
    
    def test_paper_creation(self):
        """Test Paper object creation."""
        paper = scitex.scholar.Paper(
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            abstract="This is a test abstract.",
            source="test",
            year=2024
        )
        
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.year == 2024
        assert paper.source == "test"
        
        # Test string representation
        str_repr = str(paper)
        assert "Test Paper" in str_repr
        assert "John Doe" in str_repr
    
    def test_paper_identifier(self):
        """Test paper identifier generation."""
        # With DOI
        paper1 = scitex.scholar.Paper(
            title="Paper 1",
            authors=["Author"],
            abstract="Abstract",
            source="test",
            doi="10.1234/test"
        )
        assert paper1.get_identifier() == "doi:10.1234/test"
        
        # With PMID
        paper2 = scitex.scholar.Paper(
            title="Paper 2",
            authors=["Author"],
            abstract="Abstract",
            source="pubmed",
            pmid="12345678"
        )
        assert paper2.get_identifier() == "pmid:12345678"
        
        # With arXiv ID
        paper3 = scitex.scholar.Paper(
            title="Paper 3",
            authors=["Author"],
            abstract="Abstract",
            source="arxiv",
            arxiv_id="2401.12345"
        )
        assert paper3.get_identifier() == "arxiv:2401.12345"
    
    def test_paper_bibtex(self):
        """Test BibTeX generation."""
        paper = scitex.scholar.Paper(
            title="Deep Learning for Science",
            authors=["John Doe", "Jane Smith"],
            abstract="Abstract text",
            source="arxiv",
            year=2024,
            arxiv_id="2401.12345"
        )
        
        bibtex = paper.to_bibtex()
        assert "@misc{" in bibtex
        assert "title = {{Deep Learning for Science}}" in bibtex
        assert "author = {{John Doe and Jane Smith}}" in bibtex
        assert "year = {{2024}}" in bibtex
        assert "eprint = {{2401.12345}}" in bibtex
    
    def test_paper_similarity(self):
        """Test paper similarity calculation."""
        paper1 = scitex.scholar.Paper(
            title="Deep Learning for Neural Networks",
            authors=["John Doe", "Jane Smith"],
            abstract="This paper explores deep learning applications.",
            source="test"
        )
        
        paper2 = scitex.scholar.Paper(
            title="Deep Learning for Neural Networks",
            authors=["John Doe", "Bob Johnson"],
            abstract="This paper explores deep learning applications.",
            source="test"
        )
        
        paper3 = scitex.scholar.Paper(
            title="Quantum Computing Basics",
            authors=["Alice Cooper"],
            abstract="Introduction to quantum computing.",
            source="test"
        )
        
        # Similar papers should have high score
        score12 = paper1.similarity_score(paper2)
        assert score12 > 0.7
        
        # Different papers should have low score
        score13 = paper1.similarity_score(paper3)
        assert score13 < 0.3
    
    def test_scholar_dir(self):
        """Test scholar directory creation."""
        scholar_dir = scitex.scholar.get_scholar_dir()
        assert isinstance(scholar_dir, Path)
        assert scholar_dir.exists()
        assert scholar_dir.is_dir()
    
    def test_vector_search_engine(self):
        """Test VectorSearchEngine basic functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = scitex.scholar.VectorSearchEngine(
                index_path=Path(tmpdir) / "test_index.pkl",
                embedding_dim=384
            )
            
            # Add papers
            papers = [
                scitex.scholar.Paper(
                    title="Deep Learning Applications",
                    authors=["Author1"],
                    abstract="This paper discusses deep learning.",
                    source="test"
                ),
                scitex.scholar.Paper(
                    title="Machine Learning Basics",
                    authors=["Author2"],
                    abstract="Introduction to machine learning.",
                    source="test"
                ),
            ]
            
            engine.add_papers(papers)
            
            # Search
            results = engine.search("deep learning", top_k=2)
            assert len(results) > 0
            assert results[0][0].title == "Deep Learning Applications"
            
            # Save and load
            engine.save_index()
            assert (Path(tmpdir) / "test_index.pkl").exists()
            
            # Create new engine and load
            engine2 = scitex.scholar.VectorSearchEngine(
                index_path=Path(tmpdir) / "test_index.pkl"
            )
            engine2.load_index()
            assert len(engine2.papers) == 2
    
    def test_local_search_engine(self):
        """Test LocalSearchEngine basic functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = scitex.scholar.LocalSearchEngine(
                index_path=Path(tmpdir) / "local_index.json"
            )
            
            # Create a dummy PDF file
            pdf_path = Path(tmpdir) / "test_paper.pdf"
            pdf_path.write_text("Dummy PDF content")
            
            # Search (should handle non-PDF gracefully)
            results = engine.search("test", [Path(tmpdir)], max_results=10)
            # Results might be empty if no PDF reader is available
            assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_pdf_downloader(self):
        """Test PDFDownloader initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = scitex.scholar.PDFDownloader(
                download_dir=Path(tmpdir)
            )
            
            assert downloader.download_dir.exists()
            assert downloader.timeout == 30
            assert downloader.max_concurrent == 3
    
    def test_search_sync_local_only(self):
        """Test synchronous local-only search."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy files
            (Path(tmpdir) / "paper1.pdf").write_text("dummy")
            (Path(tmpdir) / "paper2.txt").write_text("dummy")
            
            # Search local only
            papers = scitex.scholar.search_sync(
                "test",
                web=False,
                local=True,
                local_paths=[tmpdir],
                max_results=5
            )
            
            # Should return a list (might be empty if no PDF reader)
            assert isinstance(papers, list)
    
    @pytest.mark.asyncio
    async def test_search_async_basic(self):
        """Test basic async search functionality."""
        # Test with minimal parameters
        papers = await scitex.scholar.search(
            "test query",
            web=False,  # Disable web to avoid network calls
            local=True,
            local_paths=["."],
            max_results=1,
            use_vector_search=False  # Disable to avoid model download
        )
        
        assert isinstance(papers, list)
    
    def test_build_index_basic(self):
        """Test index building."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set scholar dir to temp
            import os
            original_env = os.environ.get('SciTeX_SCHOLAR_DIR')
            os.environ['SciTeX_SCHOLAR_DIR'] = tmpdir
            
            try:
                stats = scitex.scholar.build_index(
                    paths=[tmpdir],
                    recursive=False,
                    build_vector_index=False
                )
                
                assert isinstance(stats, dict)
                assert 'local_files_indexed' in stats
            finally:
                # Restore original env
                if original_env:
                    os.environ['SciTeX_SCHOLAR_DIR'] = original_env
                else:
                    os.environ.pop('SciTeX_SCHOLAR_DIR', None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])