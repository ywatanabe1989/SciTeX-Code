#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:19:00 (ywatanabe)"
# File: ./tests/scitex/scholar/test_paper.py

"""Test Paper class functionality."""

import pytest
from scitex.scholar import Paper


def test_paper_creation():
    """Test creating a Paper instance."""
    paper = Paper(
        title="Test Paper",
        authors=["Author One", "Author Two"],
        abstract="Test abstract",
        source="test",
        year=2025,
        journal="Test Journal"
    )
    
    assert paper.title == "Test Paper"
    assert paper.authors == ["Author One", "Author Two"]
    assert paper.abstract == "Test abstract"
    assert paper.source == "test"
    assert paper.year == 2025
    assert paper.journal == "Test Journal"


def test_paper_str_representation():
    """Test string representation of Paper."""
    paper = Paper(
        title="Test Paper",
        authors=["Author One"],
        abstract="Test abstract",
        source="test",
        year=2025
    )
    
    str_repr = str(paper)
    assert "Test Paper" in str_repr
    assert "Author One" in str_repr
    assert "2025" in str_repr


def test_paper_equality():
    """Test Paper equality comparison using similarity."""
    paper1 = Paper(title="Test", authors=["A"], abstract="Abstract", source="test", year=2025)
    paper2 = Paper(title="Test", authors=["A"], abstract="Abstract", source="test", year=2025)
    paper3 = Paper(title="Different", authors=["A"], abstract="Abstract", source="test", year=2025)
    
    # Use similarity score instead of equality
    similarity = paper1.similarity_score(paper2)
    assert similarity > 0.8  # High similarity
    
    different_similarity = paper1.similarity_score(paper3)
    assert different_similarity < similarity  # Lower similarity


if __name__ == "__main__":
    pytest.main([__file__])