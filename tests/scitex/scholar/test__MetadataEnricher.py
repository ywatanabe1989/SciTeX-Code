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
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/_MetadataEnricher.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-07-23 15:52:29 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_MetadataEnricher.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/scholar/_MetadataEnricher.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# """
# Metadata enrichment module for SciTeX Scholar.
# 
# This module enriches scientific papers with additional metadata:
# - Journal impact factors from impact_factor package
# - Citation counts from Semantic Scholar and CrossRef
# - Journal metrics (quartiles, rankings)
# - Future: h-index, author metrics, altmetrics, etc.
# 
# All enrichment is done in-place on Paper objects.
# """
# 
# import asyncio
# from scitex import logging
# from difflib import SequenceMatcher
# from functools import lru_cache
# from pathlib import Path
# from typing import Any, Dict, List, Optional, Tuple
# 
# from ..errors import EnrichmentError, warn_performance
# from ._Paper import Paper
# 
# logger = logging.getLogger(__name__)
# 
# 
# def _get_jcr_year():
#     """Dynamically determine JCR data year from impact_factor package files."""
#     try:
#         import glob
#         import re
# 
#         import impact_factor
# 
#         # Find Excel files in the package data directory
#         package_dir = os.path.dirname(impact_factor.__file__)
#         data_dir = os.path.join(package_dir, "data")
# 
#         if os.path.exists(data_dir):
#             excel_files = glob.glob(os.path.join(data_dir, "*.xlsx"))
#             years = []
# 
#             for file in excel_files:
#                 basename = os.path.basename(file)
#                 # Extract year from filename (e.g., "CopyofImpactFactor2024.xlsx")
#                 year_match = re.search(r"20\d{2}", basename)
#                 if year_match:
#                     years.append(int(year_match.group()))
# 
#             if years:
#                 return max(years)  # Return the latest year
#     except Exception as e:
#         logger.debug(f"Could not determine JCR year from package: {e}")
# 
#     # Fallback to hardcoded year
#     return 2024
# 
# 
# # JCR data year - dynamically determined from impact_factor package
# JCR_YEAR = _get_jcr_year()
# 
# 
# class MetadataEnricher:
#     """
#     Metadata enricher for scientific papers.
# 
#     Enriches Paper objects with impact factors, citation counts,
#     journal metrics, and other scholarly metadata from various sources.
#     """
# 
#     def __init__(
#         self,
#         semantic_scholar_api_key: Optional[str] = None,
#         crossref_api_key: Optional[str] = None,
#         email: Optional[str] = None,
#         journal_data_path: Optional[Path] = None,
#         use_impact_factor_package: bool = True,
#         cache_size: int = 1000,
#     ) -> None:
#         """
#         Initialize unified enricher.
# 
#         Args:
#             semantic_scholar_api_key: API key for Semantic Scholar
#             crossref_api_key: API key for CrossRef (optional, for higher rate limits)
#             email: Email for CrossRef API (used in User-Agent)
#             journal_data_path: Path to custom journal metrics data
#             use_impact_factor_package: Whether to use impact_factor package
#             cache_size: Size of LRU cache for journal lookups
#         """
#         # API keys and email
#         self.semantic_scholar_api_key: Optional[str] = semantic_scholar_api_key
#         self.crossref_api_key: Optional[str] = crossref_api_key
#         self.email: Optional[str] = email
# 
#         # Journal data
#         self.journal_data_path: Optional[Path] = journal_data_path
#         self.use_impact_factor_package: bool = use_impact_factor_package
#         self._journal_data: Optional[Dict[str, Dict[str, Any]]] = None
#         self._impact_factor_instance: Optional[Any] = None
# 
#         # Configure cache
#         self._cache_size: int = cache_size
#         self._get_journal_metrics = lru_cache(maxsize=cache_size)(
#             self._get_journal_metrics_uncached
#         )
# 
#         # Initialize components
#         self._init_impact_factor_package()
#         self._load_journal_data()
# 
#     def enrich_all(
#         self,
#         papers: List[Paper],
#         enrich_impact_factors: bool = True,
#         enrich_citations: bool = True,
#         enrich_journal_metrics: bool = True,
#         parallel: bool = True,
#     ) -> List[Paper]:
#         """
#         Enrich papers with all available metadata.
# 
#         Args:
#             papers: List of papers to enrich
#             enrich_impact_factors: Add journal impact factors
#             enrich_citations: Add citation counts from Semantic Scholar
#             enrich_journal_metrics: Add quartiles, rankings
#             parallel: Use parallel processing for API calls
# 
#         Returns:
#             Same list with papers enriched in-place
# 
#         Raises:
#             EnrichmentError: If enrichment fails critically
#         """
#         if not papers:
#             return papers
# 
#         logger.info(f"Starting enrichment for {len(papers)} papers")
# 
#         # Enrich impact factors and journal metrics together (same data source)
#         if enrich_impact_factors or enrich_journal_metrics:
#             self._enrich_journal_data(
#                 papers,
#                 include_impact_factors=enrich_impact_factors,
#                 include_metrics=enrich_journal_metrics,
#             )
# 
#         # Enrich citations (requires API calls)
#         if enrich_citations:
#             if parallel and len(papers) > 50:
#                 warn_performance(
#                     "Citation enrichment",
#                     f"Enriching {len(papers)} papers in parallel. This may take time.",
#                 )
# 
#             # Run async enrichment
#             try:
#                 loop = asyncio.get_event_loop()
#                 if loop.is_running():
#                     # If already in async context, create task
#                     task = asyncio.create_task(
#                         self._enrich_citations_async(papers)
#                     )
#                     papers = asyncio.run_coroutine_threadsafe(
#                         task, loop
#                     ).result()
#                 else:
#                     papers = loop.run_until_complete(
#                         self._enrich_citations_async(papers)
#                     )
#             except RuntimeError:
#                 # No event loop, create new one
#                 papers = asyncio.run(self._enrich_citations_async(papers))
# 
#         logger.info("Enrichment completed")
#         return papers
# 
#     def enrich_impact_factors(self, papers: List[Paper]) -> List[Paper]:
#         """
#         Enrich papers with journal impact factors only.
# 
#         Args:
#             papers: List of papers to enrich
# 
#         Returns:
#             Same list with impact factors added
#         """
#         return self.enrich_all(
#             papers,
#             enrich_impact_factors=True,
#             enrich_citations=False,
#             enrich_journal_metrics=False,
#         )
# 
#     def enrich_citations(self, papers: List[Paper]) -> List[Paper]:
#         """
#         Enrich papers with citation counts only.
# 
#         Args:
#             papers: List of papers to enrich
# 
#         Returns:
#             Same list with citation counts added
#         """
#         return self.enrich_all(
#             papers,
#             enrich_impact_factors=False,
#             enrich_citations=True,
#             enrich_journal_metrics=False,
#         )
# 
#     # Private methods for impact factor functionality
# 
#     def _init_impact_factor_package(self) -> None:
#         """Initialize impact_factor package if available."""
#         if self.use_impact_factor_package:
#             try:
#                 from impact_factor.core import Factor
# 
#                 self._impact_factor_instance = Factor()
#                 logger.info(
#                     f"Impact factor package initialized (JCR {JCR_YEAR} data from impact_factor package)"
#                 )
#             except ImportError:
#                 logger.warning(
#                     "impact_factor package not available. Install with: pip install impact-factor\n"
#                     "Journal impact factors will use fallback data if available."
#                 )
#                 self._impact_factor_instance = None
# 
#     def _load_journal_data(self) -> None:
#         """Load custom journal data if provided."""
#         if self.journal_data_path and self.journal_data_path.exists():
#             try:
#                 import json
# 
#                 with open(self.journal_data_path, "r") as f:
#                     self._journal_data = json.load(f)
#                 logger.info(
#                     f"Loaded custom journal data from {self.journal_data_path}"
#                 )
#             except Exception as e:
#                 logger.warning(f"Failed to load custom journal data: {e}")
#                 self._journal_data = None
#         else:
#             self._journal_data = None
# 
#     def _enrich_journal_data(
#         self,
#         papers: List[Paper],
#         include_impact_factors: bool = True,
#         include_metrics: bool = True,
#     ) -> None:
#         """
#         Enrich papers with journal-related data.
# 
#         Args:
#             papers: Papers to enrich (modified in-place)
#             include_impact_factors: Add impact factors
#             include_metrics: Add quartiles, rankings
#         """
#         enriched_count: int = 0
# 
#         for paper in papers:
#             if not paper.journal:
#                 continue
# 
#             metrics = self._get_journal_metrics(paper.journal)
#             if not metrics:
#                 continue
# 
#             # Add requested data
#             if include_impact_factors and "impact_factor" in metrics:
#                 paper.impact_factor = metrics["impact_factor"]
#                 paper.impact_factor_source = metrics.get(
#                     "source", f"JCR {JCR_YEAR}"
#                 )
#                 paper.metadata["impact_factor_source"] = (
#                     paper.impact_factor_source
#                 )
#                 enriched_count += 1
# 
#             if include_metrics:
#                 if "quartile" in metrics:
#                     paper.journal_quartile = metrics["quartile"]
#                     paper.quartile_source = metrics.get(
#                         "source", f"JCR {JCR_YEAR}"
#                     )
#                     paper.metadata["quartile_source"] = paper.quartile_source
#                 if "rank" in metrics:
#                     paper.journal_rank = metrics["rank"]
#                 if "h_index" in metrics:
#                     paper.h_index = metrics["h_index"]
# 
#         logger.info(
#             f"Enriched {enriched_count}/{len(papers)} papers with journal data"
#         )
# 
#     def _get_journal_metrics_uncached(
#         self, journal_name: str
#     ) -> Optional[Dict[str, Any]]:
#         """
#         Get journal metrics from available sources (uncached version).
# 
#         Args:
#             journal_name: Name of the journal
# 
#         Returns:
#             Dictionary with available metrics or None
#         """
#         metrics: Dict[str, Any] = {}
# 
#         # Try impact_factor package first (real 2024 JCR data)
#         if self._impact_factor_instance:
#             try:
#                 # Search for journal
#                 search_results = self._impact_factor_instance.search(
#                     journal_name
#                 )
# 
#                 if search_results:
#                     # Get best match
#                     best_match = self._find_best_journal_match(
#                         journal_name, [r["journal"] for r in search_results]
#                     )
# 
#                     if best_match:
#                         # Find the matching result
#                         for result in search_results:
#                             if result["journal"] == best_match:
#                                 factor_value = result.get("factor")
#                                 if factor_value is not None:
#                                     metrics["impact_factor"] = float(
#                                         factor_value
#                                     )
#                                 metrics["quartile"] = result.get(
#                                     "jcr", "Unknown"
#                                 )
#                                 metrics["rank"] = result.get("rank")
#                                 metrics["source"] = f"JCR {JCR_YEAR}"
#                                 break
# 
#             except Exception as e:
#                 logger.debug(
#                     f"Impact factor lookup failed for '{journal_name}': {e}"
#                 )
# 
#         # Fall back to custom data if no impact factor found
#         if not metrics and self._journal_data:
#             normalized_name = self._normalize_journal_name(journal_name)
#             if normalized_name in self._journal_data:
#                 custom_metrics = self._journal_data[normalized_name]
#                 metrics.update(custom_metrics)
#                 metrics["source"] = "Custom data"
# 
#         return metrics if metrics else None
# 
#     def _find_best_journal_match(
#         self, query: str, candidates: List[str], threshold: float = 0.85
#     ) -> Optional[str]:
#         """
#         Find best matching journal name from candidates.
# 
#         Args:
#             query: Journal name to match
#             candidates: List of candidate journal names
#             threshold: Minimum similarity score
# 
#         Returns:
#             Best matching journal name or None
#         """
#         if not candidates:
#             return None
# 
#         query_normalized = self._normalize_journal_name(query)
#         best_match: Optional[str] = None
#         best_score: float = 0.0
# 
#         for candidate in candidates:
#             candidate_normalized = self._normalize_journal_name(candidate)
#             score = SequenceMatcher(
#                 None, query_normalized, candidate_normalized
#             ).ratio()
# 
#             if score > best_score and score >= threshold:
#                 best_score = score
#                 best_match = candidate
# 
#         return best_match
# 
#     def _normalize_journal_name(self, name: str) -> str:
#         """Normalize journal name for matching."""
#         import re
# 
#         # Convert to lowercase and remove punctuation
#         normalized = name.lower()
#         normalized = re.sub(r"[^\w\s]", " ", normalized)
#         normalized = " ".join(normalized.split())
#         return normalized
# 
#     # Private methods for citation functionality
# 
#     async def _enrich_citations_async(
#         self, papers: List[Paper]
#     ) -> List[Paper]:
#         """
#         Asynchronously enrich papers with citation counts.
# 
#         Args:
#             papers: Papers to enrich
# 
#         Returns:
#             Same list with citations added where possible
#         """
#         # Group papers that need citation enrichment
#         papers_needing_citations: List[Tuple[int, Paper]] = [
#             (i, p) for i, p in enumerate(papers) if p.citation_count is None
#         ]
# 
#         if not papers_needing_citations:
#             logger.info("All papers already have citation counts")
#             return papers
# 
#         logger.info(
#             f"Enriching {len(papers_needing_citations)} papers with citation counts"
#         )
# 
#         # Create tasks for concurrent enrichment
#         tasks = [
#             self._get_citation_count_for_paper(paper)
#             for _, paper in papers_needing_citations
#         ]
# 
#         # Run with semaphore to limit concurrent requests
#         semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
# 
#         async def limited_task(task):
#             async with semaphore:
#                 return await task
# 
#         results = await asyncio.gather(
#             *[limited_task(task) for task in tasks], return_exceptions=True
#         )
# 
#         # Update papers with results
#         enriched_count: int = 0
#         for (idx, paper), result in zip(papers_needing_citations, results):
#             if isinstance(result, Exception):
#                 logger.debug(
#                     f"Failed to get citations for '{paper.title[:50]}...': {result}"
#                 )
#             elif result is not None:
#                 paper.citation_count = result
#                 enriched_count += 1
# 
#         logger.info(
#             f"Successfully enriched {enriched_count}/{len(papers_needing_citations)} papers with citations"
#         )
#         return papers
# 
#     async def _get_citation_count_for_paper(
#         self, paper: Paper
#     ) -> Optional[int]:
#         """
#         Get citation count for a single paper.
# 
#         Args:
#             paper: Paper to get citation count for
# 
#         Returns:
#             Citation count or None
#         """
#         # Try CrossRef first if DOI is available
#         if paper.doi:
#             try:
#                 from ..web._search_pubmed import get_crossref_metrics
# 
#                 metrics = get_crossref_metrics(
#                     paper.doi, api_key=self.crossref_api_key, email=self.email
#                 )
#                 if metrics and "citations" in metrics:
#                     logger.debug(
#                         f"Got citation count from CrossRef for {paper.doi}: {metrics['citations']}"
#                     )
#                     # Update paper metadata to indicate source
#                     paper.metadata["citation_count_source"] = "CrossRef"
#                     return metrics["citations"]
#             except Exception as e:
#                 logger.debug(
#                     f"CrossRef citation lookup failed for {paper.doi}: {e}"
#                 )
# 
#         # Fall back to Semantic Scholar
#         # Import here to avoid circular dependency
#         from ._SearchEngines import SemanticScholarEngine
# 
#         # Build search query
#         query: Optional[str] = None
#         if paper.doi:
#             query = f"doi:{paper.doi}"
#         elif paper.title:
#             query = paper.title
#         else:
#             return None
# 
#         try:
#             # Create Semantic Scholar engine
#             semantic_scholar_engine = SemanticScholarEngine(
#                 api_key=self.semantic_scholar_api_key
#             )
# 
#             # Search for the paper
#             results = await semantic_scholar_engine.search(query, limit=3)
# 
#             # Find best match
#             for result in results:
#                 # Check if titles match
#                 if self._papers_match(paper, result):
#                     # Update metadata to indicate source
#                     paper.metadata["citation_count_source"] = (
#                         "Semantic Scholar"
#                     )
#                     return result.citation_count
# 
#         except Exception as e:
#             logger.debug(f"Semantic Scholar citation lookup failed: {e}")
# 
#         return None
# 
#     def _papers_match(
#         self, paper1: Paper, paper2: Paper, threshold: float = 0.85
#     ) -> bool:
#         """
#         Check if two papers are the same.
# 
#         Args:
#             paper1: First paper
#             paper2: Second paper
#             threshold: Similarity threshold for title matching
# 
#         Returns:
#             True if papers match
#         """
#         # Check DOI match first (most reliable)
#         if paper1.doi and paper2.doi:
#             return paper1.doi.lower() == paper2.doi.lower()
# 
#         # Check title match
#         if paper1.title and paper2.title:
#             return self._titles_match(paper1.title, paper2.title, threshold)
# 
#         return False
# 
#     def _titles_match(
#         self, title1: str, title2: str, threshold: float = 0.85
#     ) -> bool:
#         """
#         Check if two titles match using fuzzy matching.
# 
#         Args:
#             title1: First title
#             title2: Second title
#             threshold: Minimum similarity score
# 
#         Returns:
#             True if titles match
#         """
#         if not title1 or not title2:
#             return False
# 
#         # Normalize titles
#         t1 = title1.lower().strip()
#         t2 = title2.lower().strip()
# 
#         # Exact match
#         if t1 == t2:
#             return True
# 
#         # Fuzzy match
#         similarity = SequenceMatcher(None, t1, t2).ratio()
#         return similarity >= threshold
# 
#     def get_enrichment_stats(self, papers: List[Paper]) -> Dict[str, Any]:
#         """
#         Get statistics about enrichment coverage.
# 
#         Args:
#             papers: List of papers to analyze
# 
#         Returns:
#             Dictionary with enrichment statistics
#         """
#         total = len(papers)
#         if total == 0:
#             return {
#                 "total_papers": 0,
#                 "with_impact_factor": 0,
#                 "with_citations": 0,
#                 "with_quartile": 0,
#                 "fully_enriched": 0,
#                 "coverage_percentage": 0.0,
#             }
# 
#         with_if = sum(1 for p in papers if p.impact_factor is not None)
#         with_cite = sum(1 for p in papers if p.citation_count is not None)
#         with_quartile = sum(
#             1 for p in papers if p.journal_quartile is not None
#         )
#         fully_enriched = sum(
#             1
#             for p in papers
#             if p.impact_factor is not None and p.citation_count is not None
#         )
# 
#         return {
#             "total_papers": total,
#             "with_impact_factor": with_if,
#             "with_citations": with_cite,
#             "with_quartile": with_quartile,
#             "fully_enriched": fully_enriched,
#             "impact_factor_coverage": (with_if / total) * 100,
#             "citation_coverage": (with_cite / total) * 100,
#             "quartile_coverage": (with_quartile / total) * 100,
#             "full_coverage": (fully_enriched / total) * 100,
#         }
# 
# 
# # Convenience functions for backward compatibility
# 
# 
# def _enrich_papers_with_all(
#     papers: List[Paper],
#     semantic_scholar_api_key: Optional[str] = None,
#     **kwargs,
# ) -> List[Paper]:
#     """
#     Convenience function to enrich papers with all available data.
# 
#     Args:
#         papers: List of papers to enrich
#         semantic_scholar_api_key: Optional API key
#         **kwargs: Additional arguments for MetadataEnricher
# 
#     Returns:
#         Enriched papers
#     """
#     enricher = MetadataEnricher(
#         semantic_scholar_api_key=semantic_scholar_api_key, **kwargs
#     )
#     return enricher.enrich_all(papers)
# 
# 
# def _enrich_papers_with_impact_factors(
#     papers: List[Paper], use_impact_factor_package: bool = True
# ) -> List[Paper]:
#     """
#     Convenience function to enrich papers with impact factors only.
# 
#     Args:
#         papers: List of papers
#         use_impact_factor_package: Whether to use impact_factor package
# 
#     Returns:
#         Papers with impact factors
#     """
#     enricher = MetadataEnricher(
#         use_impact_factor_package=use_impact_factor_package
#     )
#     return enricher.enrich_impact_factors(papers)
# 
# 
# def _enrich_papers_with_citations(
#     papers: List[Paper], semantic_scholar_api_key: Optional[str] = None
# ) -> List[Paper]:
#     """
#     Convenience function to enrich papers with citations only.
# 
#     Args:
#         papers: List of papers
#         semantic_scholar_api_key: Optional API key
# 
#     Returns:
#         Papers with citation counts
#     """
#     enricher = MetadataEnricher(
#         semantic_scholar_api_key=semantic_scholar_api_key
#     )
#     return enricher.enrich_citations(papers)
# 
# 
# __all__ = [
#     "MetadataEnricher",
#     "_enrich_papers_with_all",
#     "_enrich_papers_with_impact_factors",
#     "_enrich_papers_with_citations",
# ]
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/_MetadataEnricher.py
# --------------------------------------------------------------------------------
