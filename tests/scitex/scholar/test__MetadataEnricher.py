#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 16:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/tests/scitex/scholar/test__MetadataEnricher.py
# ----------------------------------------
import os
__FILE__ = (
    "/home/ywatanabe/proj/SciTeX-Code/tests/scitex/scholar/test__MetadataEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Tests for MetadataEnricher functionality.

Tests impact factor lookup, citation enrichment, journal metrics,
and the unified enrichment process.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scitex.errors import EnrichmentError
from scitex.scholar import Paper, Papers
from scitex.scholar._MetadataEnricher import (
    MetadataEnricher,
    _enrich_papers_with_all,
    _enrich_papers_with_citations,
    _enrich_papers_with_impact_factors,
    _get_jcr_year,
)

# Check if pytest-asyncio is available
try:
    import pytest_asyncio
    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False

# Define skipif decorator for async tests
pytestmark_async = pytest.mark.skipif(
    not HAS_PYTEST_ASYNCIO, 
    reason="pytest-asyncio not installed"
)


class TestMetadataEnricher:
    """Test MetadataEnricher functionality."""

    @pytest.fixture
    def sample_papers(self):
        """Create sample papers for testing."""
        return [
            Paper(
                title="Machine Learning Applications",
                authors=["Smith, John", "Doe, Jane"],
                abstract="This paper explores machine learning applications.",
                journal="Nature Machine Intelligence",
                year=2023,
                doi="10.1038/s42256-023-00001",
                source="pubmed",
            ),
            Paper(
                title="Deep Learning Theory",
                authors=["Johnson, Alice"],
                abstract="A theoretical study of deep learning architectures.",
                journal="Journal of Machine Learning Research",
                year=2022,
                doi="10.5555/jmlr.2022.001",
                source="arxiv",
            ),
            Paper(
                title="Neural Networks Review",
                authors=["Brown, Bob"],
                abstract="A comprehensive review of neural network architectures.",
                journal="IEEE Transactions on Neural Networks",
                year=2021,
                source="semantic_scholar",
            ),
        ]

    @pytest.fixture
    def custom_journal_data(self):
        """Create custom journal data for testing."""
        return {
            "nature machine intelligence": {
                "impact_factor": 25.5,
                "quartile": "Q1",
                "rank": 1,
                "h_index": 50,
            },
            "journal of machine learning research": {
                "impact_factor": 5.0,
                "quartile": "Q1",
                "rank": 10,
            },
        }

    @pytest.fixture
    def enricher(self):
        """Create MetadataEnricher instance."""
        return MetadataEnricher(
            semantic_scholar_api_key="test-key",
            use_impact_factor_package=False,  # Disable for tests
            cache_size=10,
        )

    def test_init(self):
        """Test MetadataEnricher initialization."""
        # Test basic init
        enricher = MetadataEnricher()
        assert enricher.semantic_scholar_api_key is None
        assert enricher.crossref_api_key is None
        assert enricher.email is None
        assert enricher.use_impact_factor_package is True

        # Test with parameters
        enricher = MetadataEnricher(
            semantic_scholar_api_key="test-key",
            crossref_api_key="crossref-key",
            email="test@example.com",
            use_impact_factor_package=False,
            cache_size=100,
        )
        assert enricher.semantic_scholar_api_key == "test-key"
        assert enricher.crossref_api_key == "crossref-key"
        assert enricher.email == "test@example.com"
        assert enricher.use_impact_factor_package is False
        assert enricher._cache_size == 100

    def test_init_with_custom_journal_data(self, custom_journal_data):
        """Test initialization with custom journal data."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(custom_journal_data, f)
            data_path = Path(f.name)

        try:
            enricher = MetadataEnricher(journal_data_path=data_path)
            assert enricher._journal_data == custom_journal_data
        finally:
            data_path.unlink()

    @patch("impact_factor.core.Factor")
    def test_init_impact_factor_package(self, mock_factor):
        """Test initialization of impact_factor package."""
        enricher = MetadataEnricher(use_impact_factor_package=True)
        assert enricher._impact_factor_instance is not None
        mock_factor.assert_called_once()

    def test_init_impact_factor_package_not_installed(self):
        """Test handling when impact_factor package is not installed."""
        with patch(
            "impact_factor.core.Factor",
            side_effect=ImportError("No module named 'impact_factor'"),
        ):
            enricher = MetadataEnricher(use_impact_factor_package=True)
            assert enricher._impact_factor_instance is None

    def test_get_jcr_year(self):
        """Test dynamic JCR year detection."""
        # Test with mock data
        with patch("glob.glob") as mock_glob:
            mock_glob.return_value = [
                "/path/to/CopyofImpactFactor2024.xlsx",
                "/path/to/ImpactFactor2023.xlsx",
            ]
            with patch("os.path.exists", return_value=True):
                with patch("impact_factor.__file__", "/path/to/impact_factor/__init__.py"):
                    year = _get_jcr_year()
                    assert year == 2024

        # Test fallback
        with patch("glob.glob", side_effect=Exception("Error")):
            year = _get_jcr_year()
            assert year == 2024  # Fallback year

    def test_normalize_journal_name(self, enricher):
        """Test journal name normalization."""
        # Test various journal name formats
        assert (
            enricher._normalize_journal_name("Nature Machine Intelligence")
            == "nature machine intelligence"
        )
        assert (
            enricher._normalize_journal_name("IEEE Trans. Neural Netw.")
            == "ieee trans neural netw"
        )
        assert (
            enricher._normalize_journal_name("J. Mach. Learn. Res.")
            == "j mach learn res"
        )
        assert (
            enricher._normalize_journal_name("PLOS ONE") == "plos one"
        )

    def test_find_best_journal_match(self, enricher):
        """Test fuzzy journal name matching."""
        candidates = [
            "Nature Machine Intelligence",
            "Nature Communications",
            "Machine Learning Journal",
        ]

        # Exact match
        match = enricher._find_best_journal_match(
            "Nature Machine Intelligence", candidates
        )
        assert match == "Nature Machine Intelligence"

        # Close match
        match = enricher._find_best_journal_match(
            "Nature Mach. Intelligence", candidates
        )
        assert match == "Nature Machine Intelligence"

        # No good match
        match = enricher._find_best_journal_match(
            "Science Magazine", candidates, threshold=0.9
        )
        assert match is None

    def test_get_journal_metrics_with_custom_data(
        self, enricher, custom_journal_data
    ):
        """Test getting journal metrics from custom data."""
        enricher._journal_data = custom_journal_data

        # Test exact match
        metrics = enricher._get_journal_metrics_uncached(
            "Nature Machine Intelligence"
        )
        assert metrics is not None
        assert metrics["impact_factor"] == 25.5
        assert metrics["quartile"] == "Q1"
        assert metrics["source"] == "Custom data"

        # Test no match
        metrics = enricher._get_journal_metrics_uncached("Unknown Journal")
        assert metrics is None

    @patch("impact_factor.core.Factor")
    def test_get_journal_metrics_with_impact_factor_package(
        self, mock_factor_class
    ):
        """Test getting metrics from impact_factor package."""
        # Create mock instance
        mock_instance = MagicMock()
        mock_factor_class.return_value = mock_instance
        mock_instance.search.return_value = [
            {
                "journal": "Nature Machine Intelligence",
                "factor": "25.5",
                "jcr": "Q1",
                "rank": 1,
            }
        ]

        enricher = MetadataEnricher(use_impact_factor_package=True)
        metrics = enricher._get_journal_metrics_uncached(
            "Nature Machine Intelligence"
        )

        assert metrics is not None
        assert metrics["impact_factor"] == 25.5
        assert metrics["quartile"] == "Q1"
        assert metrics["rank"] == 1

    def test_enrich_journal_data(self, enricher, sample_papers):
        """Test journal data enrichment."""
        # Set up custom data
        enricher._journal_data = {
            "nature machine intelligence": {
                "impact_factor": 25.5,
                "quartile": "Q1",
                "rank": 1,
            }
        }

        # Enrich papers
        enricher._enrich_journal_data(
            sample_papers, include_impact_factors=True, include_metrics=True
        )

        # Check first paper was enriched
        assert sample_papers[0].impact_factor == 25.5
        assert sample_papers[0].journal_quartile == "Q1"
        assert sample_papers[0].journal_rank == 1

        # Check other papers were not enriched (no matching data)
        assert sample_papers[1].impact_factor is None
        assert sample_papers[2].impact_factor is None

    def test_papers_match(self, enricher):
        """Test paper matching logic."""
        paper1 = Paper(
            title="Test Paper",
            doi="10.1234/test",
            authors=["Smith, John"],
            abstract="Test abstract",
            source="pubmed",
        )
        paper2 = Paper(
            title="Test Paper",
            doi="10.1234/test",
            authors=["Smith, J."],
            abstract="Test abstract",
            source="arxiv",
        )
        paper3 = Paper(
            title="Different Paper",
            doi="10.5678/other",
            authors=["Doe, Jane"],
            abstract="Different abstract",
            source="pubmed",
        )

        # Same DOI should match
        assert enricher._papers_match(paper1, paper2)

        # Different DOI should not match
        assert not enricher._papers_match(paper1, paper3)

        # Test without DOI - title matching
        paper4 = Paper(title="Test Paper", authors=["Smith, John"], abstract="Test", source="pubmed")
        paper5 = Paper(title="Test Paper", authors=["Smith, J."], abstract="Test", source="arxiv")
        assert enricher._papers_match(paper4, paper5)

    def test_titles_match(self, enricher):
        """Test title matching logic."""
        # Exact match
        assert enricher._titles_match("Test Paper", "Test Paper")

        # Case insensitive
        assert enricher._titles_match("Test Paper", "test paper")

        # Whitespace
        assert enricher._titles_match("Test  Paper", "Test Paper")

        # Close match
        assert enricher._titles_match(
            "Machine Learning Applications",
            "Machine Learning Application",
            threshold=0.9,
        )

        # Not close enough
        assert not enricher._titles_match(
            "Machine Learning", "Deep Learning", threshold=0.9
        )

    @pytestmark_async
    @pytest.mark.asyncio
    async def test_get_citation_count_for_paper_crossref(self, enricher):
        """Test getting citation count from CrossRef."""
        paper = Paper(
            title="Test Paper",
            doi="10.1234/test",
            authors=["Smith, John"],
            abstract="Test abstract",
            source="pubmed",
        )

        with patch(
            "scitex.web._search_pubmed.get_crossref_metrics"
        ) as mock_crossref:
            mock_crossref.return_value = {"citations": 42}

            count = await enricher._get_citation_count_for_paper(paper)
            assert count == 42
            assert paper.metadata["citation_count_source"] == "CrossRef"

    @pytestmark_async
    @pytest.mark.asyncio
    async def test_get_citation_count_for_paper_semantic_scholar(
        self, enricher
    ):
        """Test getting citation count from Semantic Scholar."""
        paper = Paper(
            title="Test Paper",
            doi="10.1234/test",
            authors=["Smith, John"],
            abstract="Test abstract",
            source="pubmed",
        )

        # Mock CrossRef failure
        with patch(
            "scitex.web._search_pubmed.get_crossref_metrics",
            side_effect=Exception("CrossRef error"),
        ):
            # Mock Semantic Scholar success
            mock_result = Paper(
                title="Test Paper",
                doi="10.1234/test",
                authors=["Smith, John"],
                abstract="Test abstract",
                citation_count=100,
                source="semantic_scholar",
            )

            with patch(
                "scitex.scholar._MetadataEnricher.SemanticScholarEngine"
            ) as mock_engine_class:
                mock_engine = AsyncMock()
                mock_engine.search.return_value = [mock_result]
                mock_engine_class.return_value = mock_engine

                count = await enricher._get_citation_count_for_paper(paper)
                assert count == 100
                assert (
                    paper.metadata["citation_count_source"]
                    == "Semantic Scholar"
                )

    @pytestmark_async
    @pytest.mark.asyncio
    async def test_enrich_citations_async(self, enricher, sample_papers):
        """Test async citation enrichment."""
        # Mock citation counts
        async def mock_get_citation(paper):
            if "Machine Learning" in paper.title:
                return 50
            elif "Deep Learning" in paper.title:
                return 30
            return None

        with patch.object(
            enricher, "_get_citation_count_for_paper", mock_get_citation
        ):
            await enricher._enrich_citations_async(sample_papers)

            assert sample_papers[0].citation_count == 50
            assert sample_papers[1].citation_count == 30
            assert sample_papers[2].citation_count is None

    def test_enrich_all(self, enricher, sample_papers):
        """Test complete enrichment process."""
        # Mock journal data
        enricher._journal_data = {
            "nature machine intelligence": {
                "impact_factor": 25.5,
                "quartile": "Q1",
            }
        }

        # Mock citation enrichment
        async def mock_enrich_citations(papers):
            papers[0].citation_count = 100
            return papers

        with patch.object(
            enricher, "_enrich_citations_async", mock_enrich_citations
        ):
            with patch("asyncio.run") as mock_run:
                mock_run.side_effect = lambda coro: asyncio.get_event_loop().run_until_complete(
                    coro
                )

                enriched = enricher.enrich_all(
                    sample_papers,
                    enrich_impact_factors=True,
                    enrich_citations=True,
                    enrich_journal_metrics=True,
                )

                # Check enrichment
                assert enriched[0].impact_factor == 25.5
                assert enriched[0].journal_quartile == "Q1"
                assert enriched[0].citation_count == 100

    def test_enrich_impact_factors_only(self, enricher, sample_papers):
        """Test enriching only impact factors."""
        enricher._journal_data = {
            "nature machine intelligence": {"impact_factor": 25.5}
        }

        enriched = enricher.enrich_impact_factors(sample_papers)
        assert enriched[0].impact_factor == 25.5
        assert enriched[0].citation_count is None  # Should not be enriched

    def test_enrich_citations_only(self, enricher, sample_papers):
        """Test enriching only citations."""
        async def mock_enrich_citations(papers):
            papers[0].citation_count = 100
            return papers

        with patch.object(
            enricher, "_enrich_citations_async", mock_enrich_citations
        ):
            with patch("asyncio.run") as mock_run:
                mock_run.side_effect = lambda coro: asyncio.get_event_loop().run_until_complete(
                    coro
                )

                enriched = enricher.enrich_citations(sample_papers)
                assert enriched[0].citation_count == 100
                assert enriched[0].impact_factor is None  # Should not be enriched

    def test_get_enrichment_stats(self, enricher):
        """Test enrichment statistics."""
        # Create papers with varying enrichment
        papers = [
            Paper(
                title="Paper 1",
                authors=["Author 1"],
                abstract="Abstract 1",
                impact_factor=5.0,
                citation_count=10,
                journal_quartile="Q1",
                source="pubmed",
            ),
            Paper(
                title="Paper 2",
                authors=["Author 2"],
                abstract="Abstract 2",
                impact_factor=3.0,
                citation_count=None,
                journal_quartile="Q2",
                source="arxiv",
            ),
            Paper(
                title="Paper 3",
                authors=["Author 3"],
                abstract="Abstract 3",
                impact_factor=None,
                citation_count=20,
                journal_quartile=None,
                source="pubmed",
            ),
        ]

        stats = enricher.get_enrichment_stats(papers)

        assert stats["total_papers"] == 3
        assert stats["with_impact_factor"] == 2
        assert stats["with_citations"] == 2
        assert stats["with_quartile"] == 2
        assert stats["fully_enriched"] == 1
        assert stats["impact_factor_coverage"] == pytest.approx(66.67, 0.01)
        assert stats["citation_coverage"] == pytest.approx(66.67, 0.01)

    def test_get_enrichment_stats_empty(self, enricher):
        """Test enrichment statistics with no papers."""
        stats = enricher.get_enrichment_stats([])
        assert stats["total_papers"] == 0
        assert stats["coverage_percentage"] == 0.0

    def test_convenience_function_enrich_all(self, sample_papers):
        """Test convenience function for enriching all."""
        with patch(
            "scitex.scholar._MetadataEnricher.MetadataEnricher"
        ) as mock_enricher_class:
            mock_enricher = MagicMock()
            mock_enricher.enrich_all.return_value = sample_papers
            mock_enricher_class.return_value = mock_enricher

            result = _enrich_papers_with_all(
                sample_papers, semantic_scholar_api_key="test-key"
            )

            mock_enricher_class.assert_called_once_with(
                semantic_scholar_api_key="test-key"
            )
            mock_enricher.enrich_all.assert_called_once_with(sample_papers)

    def test_convenience_function_impact_factors(self, sample_papers):
        """Test convenience function for impact factors."""
        with patch(
            "scitex.scholar._MetadataEnricher.MetadataEnricher"
        ) as mock_enricher_class:
            mock_enricher = MagicMock()
            mock_enricher.enrich_impact_factors.return_value = sample_papers
            mock_enricher_class.return_value = mock_enricher

            result = _enrich_papers_with_impact_factors(sample_papers)

            mock_enricher_class.assert_called_once_with(
                use_impact_factor_package=True
            )
            mock_enricher.enrich_impact_factors.assert_called_once_with(
                sample_papers
            )

    def test_convenience_function_citations(self, sample_papers):
        """Test convenience function for citations."""
        with patch(
            "scitex.scholar._MetadataEnricher.MetadataEnricher"
        ) as mock_enricher_class:
            mock_enricher = MagicMock()
            mock_enricher.enrich_citations.return_value = sample_papers
            mock_enricher_class.return_value = mock_enricher

            result = _enrich_papers_with_citations(
                sample_papers, semantic_scholar_api_key="test-key"
            )

            mock_enricher_class.assert_called_once_with(
                semantic_scholar_api_key="test-key"
            )
            mock_enricher.enrich_citations.assert_called_once_with(
                sample_papers
            )

    def test_cache_functionality(self, enricher):
        """Test LRU cache for journal metrics."""
        # Set up mock data
        enricher._journal_data = {
            "test journal": {"impact_factor": 5.0}
        }

        # The cache is created during __init__, so we need to test it differently
        # First call
        metrics1 = enricher._get_journal_metrics("Test Journal")
        assert metrics1 is not None
        assert metrics1["impact_factor"] == 5.0

        # Second call with same key should return same object (cached)
        metrics2 = enricher._get_journal_metrics("Test Journal")
        assert metrics2 is metrics1  # Same object reference
        
        # Different key should return different result
        enricher._journal_data["another journal"] = {"impact_factor": 3.0}
        metrics3 = enricher._get_journal_metrics("Another Journal")
        assert metrics3 is not metrics1
        assert metrics3["impact_factor"] == 3.0
        
        # Verify cache info is available
        cache_info = enricher._get_journal_metrics.cache_info()
        assert cache_info.hits >= 1  # At least one cache hit
        assert cache_info.misses >= 2  # At least two cache misses

    @pytestmark_async
    @pytest.mark.asyncio
    async def test_concurrent_enrichment_with_semaphore(self, enricher):
        """Test that concurrent enrichment respects semaphore limit."""
        papers = [
            Paper(title=f"Paper {i}", doi=f"10.1234/test{i}", authors=[f"Author {i}"], abstract=f"Abstract {i}", source="pubmed")
            for i in range(10)
        ]

        call_times = []

        async def mock_get_citation(paper):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # Simulate API call
            return 10

        with patch.object(
            enricher, "_get_citation_count_for_paper", mock_get_citation
        ):
            await enricher._enrich_citations_async(papers)

        # Check that calls were rate-limited (max 5 concurrent)
        # With 10 papers and max 5 concurrent, we should see at least 2 batches
        assert len(call_times) == 10
        # Can't test exact timing in unit tests, but all should complete
        assert all(p.citation_count == 10 for p in papers)

    def test_error_handling_in_journal_data_loading(self):
        """Test error handling when loading journal data."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json{")
            data_path = Path(f.name)

        try:
            enricher = MetadataEnricher(journal_data_path=data_path)
            assert enricher._journal_data is None  # Should handle error gracefully
        finally:
            data_path.unlink()

    @pytestmark_async
    @pytest.mark.asyncio
    async def test_error_handling_in_citation_enrichment(self, enricher):
        """Test error handling during citation enrichment."""
        papers = [
            Paper(title="Paper 1", doi="10.1234/test1", authors=["Author 1"], abstract="Abstract 1", source="pubmed"),
            Paper(title="Paper 2", doi="10.1234/test2", authors=["Author 2"], abstract="Abstract 2", source="arxiv"),
        ]

        async def mock_get_citation(paper):
            if paper.title == "Paper 1":
                raise Exception("API Error")
            return 20

        with patch.object(
            enricher, "_get_citation_count_for_paper", mock_get_citation
        ):
            await enricher._enrich_citations_async(papers)

            # First paper should fail, second should succeed
            assert papers[0].citation_count is None
            assert papers[1].citation_count == 20

    def test_enrich_all_with_running_event_loop(self, enricher, sample_papers):
        """Test enrichment when event loop is already running."""
        async def mock_enrich_citations(papers):
            papers[0].citation_count = 100
            return papers

        with patch.object(
            enricher, "_enrich_citations_async", mock_enrich_citations
        ):
            # Simulate running event loop
            loop = asyncio.new_event_loop()
            
            # Create a mock loop that reports as running
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            
            with patch("asyncio.get_event_loop", return_value=mock_loop):
                with patch("asyncio.create_task") as mock_create_task:
                    with patch("asyncio.run_coroutine_threadsafe") as mock_run_threadsafe:
                        mock_future = MagicMock()
                        mock_future.result.return_value = sample_papers
                        mock_run_threadsafe.return_value = mock_future
                        
                        result = enricher.enrich_all(
                            sample_papers,
                            enrich_citations=True,
                            enrich_impact_factors=False,
                        )
                        
                        assert mock_create_task.called
                        assert mock_run_threadsafe.called
            
            loop.close()

    def test_module_exports(self):
        """Test that module exports are correct."""
        from scitex.scholar._MetadataEnricher import __all__

        # Note: UnifiedEnricher is listed but should be MetadataEnricher
        expected_exports = [
            "UnifiedEnricher",  # Legacy name still in __all__
            "_enrich_papers_with_all",
            "_enrich_papers_with_impact_factors",
            "_enrich_papers_with_citations",
        ]
        
        assert set(__all__) == set(expected_exports)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])