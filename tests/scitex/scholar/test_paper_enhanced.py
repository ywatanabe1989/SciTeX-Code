#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 01:40:00"
# File: ./tests/scitex/scholar/test_paper_enhanced.py

"""Test enhanced Paper functionality with enriched metadata."""

import pytest
from scitex.scholar import Paper


def test_paper_with_enhanced_metadata():
    """Test Paper with citation count, impact factor, and URL."""
    paper = Paper(
        title="Test Paper with Enhanced Metadata",
        authors=["Smith, J.", "Doe, A."],
        abstract="A test paper with enriched metadata",
        source="semantic_scholar",
        year=2024,
        journal="Nature",
        doi="10.1038/test",
        citation_count=100,
        impact_factor=49.962,
        journal_quartile="Q1",
        url="https://example.com/paper",
        pdf_url="https://example.com/paper.pdf",
        open_access=True
    )
    
    # Check enhanced fields
    assert paper.citation_count == 100
    assert paper.impact_factor == 49.962
    assert paper.journal_quartile == "Q1"
    assert paper.url == "https://example.com/paper"
    assert paper.pdf_url == "https://example.com/paper.pdf"
    assert paper.open_access is True


def test_bibtex_with_enriched_metadata():
    """Test BibTeX generation with enriched metadata."""
    paper = Paper(
        title="Cross-Frequency Coupling Test",
        authors=["Johnson, B.", "Lee, C."],
        abstract="Test abstract",
        source="pubmed",
        year=2023,
        journal="Science",
        doi="10.1126/science.test123",
        citation_count=250,
        impact_factor=47.728,
        journal_quartile="Q1"
    )
    
    # Generate BibTeX with enriched metadata
    bibtex = paper.to_bibtex(include_enriched=True)
    
    # Check standard fields
    assert "@article{johnson2023," in bibtex
    assert "title = {{Cross-Frequency Coupling Test}}" in bibtex
    assert "author = {Johnson, B. and Lee, C.}" in bibtex
    assert "year = {2023}" in bibtex
    assert "journal = {{Science}}" in bibtex
    assert "doi = {10.1126/science.test123}" in bibtex
    assert "url = {https://doi.org/10.1126/science.test123}" in bibtex
    
    # Check enriched metadata in note field
    assert "note = {" in bibtex
    assert "Citations: 250" in bibtex
    assert "Impact Factor (2024): 47.728" in bibtex
    assert "Journal Quartile: Q1" in bibtex


def test_bibtex_without_enriched_metadata():
    """Test BibTeX generation without enriched metadata."""
    paper = Paper(
        title="Simple Paper",
        authors=["Author, A."],
        abstract="Abstract",
        source="arxiv",
        year=2024,
        arxiv_id="2401.00001"
    )
    
    # Generate standard BibTeX
    bibtex = paper.to_bibtex(include_enriched=False)
    
    # Should not have note field
    assert "note = {" not in bibtex
    assert "@misc{author2024," in bibtex
    assert "eprint = {2401.00001}" in bibtex
    assert "archivePrefix = {arXiv}" in bibtex


def test_bibtex_key_generation():
    """Test standard BibTeX key generation without suffixes."""
    paper1 = Paper(
        title="Test One",
        authors=["Canolty, R.", "Knight, R."],
        abstract="Abstract",
        source="test",
        year=2010
    )
    
    paper2 = Paper(
        title="Test Two",
        authors=["O'Neill, M."],  # Name with apostrophe
        abstract="Abstract",
        source="test",
        year=2022
    )
    
    # Check key generation
    bibtex1 = paper1.to_bibtex()
    bibtex2 = paper2.to_bibtex()
    
    assert "@article{canolty2010," in bibtex1
    assert "@article{oneill2022," in bibtex2  # Special chars removed


def test_paper_to_dict_with_enhanced_fields():
    """Test dictionary conversion includes enhanced fields."""
    paper = Paper(
        title="Test",
        authors=["A"],
        abstract="Abstract",
        source="test",
        citation_count=50,
        impact_factor=10.5,
        url="https://test.com"
    )
    
    paper_dict = paper.to_dict()
    
    # Check enhanced fields in dict
    assert paper_dict["citation_count"] == 50
    assert paper_dict["impact_factor"] == 10.5
    assert paper_dict["url"] == "https://test.com"
    assert paper_dict["journal_quartile"] is None  # Not set
    assert paper_dict["pdf_url"] is None
    assert paper_dict["open_access"] is None


def test_url_generation_from_identifiers():
    """Test URL generation from DOI, PMID, or arXiv ID."""
    # Test DOI URL
    paper_doi = Paper(
        title="DOI Paper",
        authors=["Author"],
        abstract="Abstract",
        source="test",
        doi="10.1234/test"
    )
    bibtex = paper_doi.to_bibtex()
    assert "url = {https://doi.org/10.1234/test}" in bibtex
    
    # Test PMID URL
    paper_pmid = Paper(
        title="PMID Paper",
        authors=["Author"],
        abstract="Abstract",
        source="pubmed",
        pmid="12345678"
    )
    bibtex = paper_pmid.to_bibtex()
    assert "url = {https://pubmed.ncbi.nlm.nih.gov/12345678/}" in bibtex
    
    # Test arXiv URL
    paper_arxiv = Paper(
        title="arXiv Paper",
        authors=["Author"],
        abstract="Abstract",
        source="arxiv",
        arxiv_id="2401.12345"
    )
    bibtex = paper_arxiv.to_bibtex()
    assert "url = {https://arxiv.org/abs/2401.12345}" in bibtex


def test_impact_factor_formatting():
    """Test impact factor formatting handles different types."""
    # Test float IF
    paper1 = Paper(
        title="Test", authors=["A"], abstract="Abstract", source="test",
        impact_factor=12.345
    )
    bibtex1 = paper1.to_bibtex(include_enriched=True)
    assert "Impact Factor (2024): 12.345" in bibtex1
    
    # Test None IF
    paper2 = Paper(
        title="Test", authors=["A"], abstract="Abstract", source="test",
        impact_factor=None
    )
    bibtex2 = paper2.to_bibtex(include_enriched=True)
    assert "Impact Factor" not in bibtex2
    
    # Test string IF (edge case from journal metrics)
    paper3 = Paper(
        title="Test", authors=["A"], abstract="Abstract", source="test",
        impact_factor="Unknown"
    )
    bibtex3 = paper3.to_bibtex(include_enriched=True)
    assert "Impact Factor (2024): Unknown" in bibtex3