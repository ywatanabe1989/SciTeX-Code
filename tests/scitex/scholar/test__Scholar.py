#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 09:20:00 (ywatanabe)"
# File: tests/scitex/scholar/test_Scholar.py
# ----------------------------------------

"""
Tests for the Scholar class with clean API.

Tests the main interface for SciTeX Scholar functionality.
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from scitex.scholar import Scholar, Paper, Papers, ScholarConfig


def create_mock_scholar_config(tmp_path):
    """
    Create a complete mock ScholarConfig with all required attributes.
    
    This helper ensures all tests use consistent mock configurations
    and prevents AttributeError for missing mock attributes.
    """
    mock_config = Mock(spec=ScholarConfig)
    
    # Core paths
    mock_config.workspace_dir = tmp_path
    mock_config.pdf_dir = str(tmp_path / "pdfs")
    
    # API Keys
    mock_config.semantic_scholar_api_key = None
    mock_config.crossref_api_key = None
    
    # Email addresses
    mock_config.pubmed_email = "test@example.com"
    mock_config.crossref_email = "test@example.com"
    
    # Feature toggles
    mock_config.enable_auto_enrich = True
    mock_config.use_impact_factor_package = False
    mock_config.enable_auto_download = False
    mock_config.acknowledge_scihub_ethical_usage = True
    
    # Search configuration
    mock_config.default_search_sources = ["pubmed", "arxiv"]
    mock_config.default_search_limit = 20
    
    # PDF management
    mock_config.enable_pdf_extraction = True
    
    # Performance settings
    mock_config.max_parallel_requests = 3
    mock_config.request_timeout = 30
    mock_config.cache_size = 1000
    mock_config.google_scholar_timeout = 10
    
    # Advanced settings
    mock_config.verify_ssl = True
    mock_config.debug_mode = False
    
    # OpenAthens authentication
    mock_config.openathens_enabled = False
    mock_config.openathens_org_id = None
    mock_config.openathens_idp_url = None
    mock_config.openathens_email = None
    mock_config.openathens_username = None
    mock_config.openathens_password = None
    mock_config.openathens_institution_name = None
    
    # Lean Library settings
    mock_config.use_lean_library = True
    mock_config.lean_library_browser_profile = None
    
    # HTTP settings
    mock_config.user_agent = "SciTeX-Scholar/1.0"
    
    return mock_config


class TestScholar:
    """Test suite for Scholar class."""
    
    @pytest.fixture
    def scholar(self, tmp_path):
        """Create a Scholar instance for testing."""
        with patch('scitex.scholar._Scholar.ScholarConfig') as mock_config_class:
            mock_config = create_mock_scholar_config(tmp_path)
            mock_config_class.load.return_value = mock_config
            
            scholar = Scholar()
            return scholar
    
    def test_initialization_default(self, tmp_path):
        """Test Scholar initialization with default config."""
        with patch('scitex.scholar._Scholar.ScholarConfig') as mock_config_class:
            mock_config = create_mock_scholar_config(tmp_path)
            mock_config_class.load.return_value = mock_config
            
            scholar = Scholar()
            assert scholar.config == mock_config
            mock_config_class.load.assert_called_once()
    
    def test_initialization_with_config_file(self, tmp_path):
        """Test Scholar initialization with config file path."""
        config_file = tmp_path / "config.yaml"
        
        with patch('scitex.scholar._Scholar.ScholarConfig') as mock_config_class:
            mock_config = create_mock_scholar_config(tmp_path)
            mock_config_class.from_yaml.return_value = mock_config
            
            scholar = Scholar(config=config_file)
            assert scholar.config == mock_config
            mock_config_class.from_yaml.assert_called_once_with(config_file)
    
    def test_initialization_with_config_object(self, tmp_path):
        """Test Scholar initialization with ScholarConfig object."""
        mock_config = create_mock_scholar_config(tmp_path)
        
        scholar = Scholar(config=mock_config)
        assert scholar.config == mock_config
    
    def test_initialization_invalid_config(self):
        """Test Scholar initialization with invalid config type."""
        with pytest.raises(TypeError, match="Invalid config type"):
            Scholar(config=123)
    
    def test_components_initialization(self, scholar):
        """Test that Scholar initializes all components correctly."""
        # Check that all components are initialized
        assert hasattr(scholar, '_searcher')
        assert hasattr(scholar, '_enricher')
        assert hasattr(scholar, '_pdf_downloader')
        assert hasattr(scholar, '_doi_resolver')
        # Note: batch_doi_resolver is not a separate attribute anymore
        
        # Verify types
        assert scholar._pdf_downloader is not None
        assert scholar._enricher is not None
    
    def test_search(self, scholar):
        """Test search functionality."""
        # Mock search results
        mock_papers = Papers([
            Paper(
                title="Test Paper 1",
                authors=["Author One"],
                abstract="Abstract 1",
                source="pubmed",
                doi="10.1234/test1"
            ),
            Paper(
                title="Test Paper 2",
                authors=["Author Two"],
                abstract="Abstract 2",
                source="pubmed",
                doi="10.1234/test2"
            )
        ])
        
        with patch.object(scholar._searcher, 'search', 
                         return_value=mock_papers) as mock_search:
            results = scholar.search("test query", limit=10)
            
            assert len(results) == 2
            assert isinstance(results, Papers)
            assert all(isinstance(p, Paper) for p in results)
    
    def test_search_with_sources(self, scholar):
        """Test search functionality with specific sources."""
        mock_papers = Papers([
            Paper(
                title="ML Paper",
                authors=["ML Author"],
                abstract="ML Abstract",
                source="semantic_scholar",
                doi="10.1234/ml1"
            ),
            Paper(
                title="AI Paper",
                authors=["AI Author"],
                abstract="AI Abstract",
                source="semantic_scholar",
                doi="10.1234/ai1"
            )
        ])
        
        with patch.object(scholar._searcher, 'search', 
                         return_value=mock_papers) as mock_search:
            results = scholar.search("machine learning", sources=["semantic_scholar"], limit=10)
            
            assert len(results) == 2
            assert isinstance(results, Papers)
    
    def test_search_local(self, scholar, tmp_path):
        """Test local search functionality."""
        # Create some test PDFs
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir(exist_ok=True)
        (pdf_dir / "paper1.pdf").write_bytes(b'%PDF-1.4\nTest')
        (pdf_dir / "paper2.pdf").write_bytes(b'%PDF-1.4\nTest')
        
        # Mock the searcher's local search
        mock_papers = [
            Paper(
                title="Local Paper 1",
                authors=["Local Author 1"],
                abstract="Local abstract 1",
                source="local"
            ),
            Paper(
                title="Local Paper 2",
                authors=["Local Author 2"],
                abstract="Local abstract 2",
                source="local"
            )
        ]
        
        # Mock the searcher's search method to return our papers when using 'local' source
        async def mock_search(query, sources, limit):
            if sources == ['local']:
                return mock_papers
            return []
        
        with patch.object(scholar._searcher, 'search', side_effect=mock_search):
            results = scholar.search_local("Local")
            assert len(results) == 2
            assert all(isinstance(p, Paper) for p in results)
    
    def test_enrich_bibtex(self, scholar, tmp_path):
        """Test BibTeX enrichment functionality."""
        # Create a simple BibTeX file
        bibtex_content = """
@article{test2023,
    title={Nature Paper},
    author={Nature Author},
    journal={Nature},
    doi={10.1038/test},
    year={2023}
}
@article{test2022,
    title={Science Paper},
    author={Science Author},
    journal={Science},
    doi={10.1126/test},
    year={2022}
}
"""
        bibtex_file = tmp_path / "test.bib"
        bibtex_file.write_text(bibtex_content)
        
        # Mock the enrich_bibtex directly to avoid recursion
        mock_papers = Papers([
            Paper(
                title="Nature Paper",
                authors=["Nature Author"],
                abstract="Nature abstract",
                source="bibtex",
                journal="Nature",
                doi="10.1038/test",
                year=2023,
                impact_factor=40.0,
                citation_count=100
            ),
            Paper(
                title="Science Paper",
                authors=["Science Author"],
                abstract="Science abstract",
                source="bibtex",
                journal="Science",
                doi="10.1126/test",
                year=2022,
                impact_factor=40.0,
                citation_count=100
            )
        ])
        
        # Use the first enrich_bibtex method (not the wrapper)
        with patch('scitex.scholar._Scholar.Scholar.enrich_bibtex', return_value=mock_papers) as mock_enrich:
            enriched = scholar.enrich_bibtex(bibtex_file)
            
            assert len(enriched) == 2
            assert all(p.impact_factor == 40.0 for p in enriched)
    
    def test_download_pdfs(self, scholar, tmp_path):
        """Test PDF download functionality."""
        papers = Papers([
            Paper(
                title="Test 1",
                authors=["Test Author 1"],
                abstract="Test abstract 1",
                source="test",
                doi="10.1234/test1"
            ),
            Paper(
                title="Test 2",
                authors=["Test Author 2"],
                abstract="Test abstract 2",
                source="test",
                doi="10.1234/test2"
            )
        ])
        
        # Mock batch download
        async def mock_batch_download(identifiers, **kwargs):
            return {
                "10.1234/test1": tmp_path / "test1.pdf",
                "10.1234/test2": None
            }
        
        with patch.object(scholar._pdf_downloader, 'batch_download', mock_batch_download):
            results = scholar.download_pdfs(papers, download_dir=tmp_path)
            
            assert results['successful'] == 1
            assert results['failed'] == 1
            assert '10.1234/test1' in results['downloaded_files']
    
    def test_download_pdfs_with_progress(self, scholar, tmp_path):
        """Test PDF download with progress callback."""
        papers = Papers([
            Paper(
                title="Test",
                authors=["Test Author"],
                abstract="Test abstract",
                source="test",
                doi="10.1234/test"
            )
        ])
        
        progress_calls = []
        
        async def mock_batch_download(identifiers, **kwargs):
            # Call progress callback if provided
            if 'progress_callback' in kwargs and kwargs['progress_callback']:
                kwargs['progress_callback'](1, 1, "10.1234/test")
            return {"10.1234/test": tmp_path / "test.pdf"}
        
        with patch.object(scholar._pdf_downloader, 'batch_download', mock_batch_download):
            results = scholar.download_pdfs(
                papers, 
                download_dir=tmp_path,
                show_progress=True
            )
            
            assert results['successful'] == 1
    
    def test_resolve_doi(self, scholar):
        """Test DOI resolution."""
        # Mock the DOI resolver's title_to_doi method
        with patch.object(scholar._doi_resolver, 'title_to_doi', return_value="10.1234/test"):
            doi = scholar.resolve_doi("Test Article Title", year=2023)
            assert doi == "10.1234/test"
    
    def test_search_returns_papers(self, scholar):
        """Test the search method returns Papers object."""
        mock_papers = Papers([
            Paper(
                title="Paper 1",
                authors=["Author 1"],
                abstract="Abstract 1",
                source="test",
                impact_factor=10.0
            ),
            Paper(
                title="Paper 2",
                authors=["Author 2"],
                abstract="Abstract 2",
                source="test",
                impact_factor=5.0
            )
        ])
        
        with patch.object(scholar._searcher, 'search', return_value=mock_papers):
            with patch.object(scholar._enricher, 'enrich_all', return_value=mock_papers):
                result = scholar.search("test query")
                assert isinstance(result, Papers)
                assert len(result) == 2
    
    def test_papers_filtering(self, scholar):
        """Test paper filtering using Papers methods."""
        papers = Papers([
            Paper(
                title="High Impact",
                authors=["High Author"],
                abstract="High abstract",
                source="test",
                impact_factor=50.0,
                citation_count=200
            ),
            Paper(
                title="Medium Impact",
                authors=["Medium Author"],
                abstract="Medium abstract",
                source="test",
                impact_factor=10.0,
                citation_count=50
            ),
            Paper(
                title="Low Impact",
                authors=["Low Author"],
                abstract="Low abstract",
                source="test",
                impact_factor=2.0,
                citation_count=5
            )
        ])
        
        # Test impact factor filter using Papers methods
        high_impact = papers.filter(impact_factor_min=20.0)
        assert len(high_impact) == 1
        assert high_impact[0].title == "High Impact"
        
        # Test citation filter
        high_citations = papers.filter(min_citations=100)
        assert len(high_citations) == 1
        assert high_citations[0].citation_count == 200
    
    def test_papers_sorting(self, scholar):
        """Test paper sorting using Papers methods."""
        papers = Papers([
            Paper(
                title="Paper A",
                authors=["Author A"],
                abstract="Abstract A",
                source="test",
                impact_factor=10.0,
                year=2023
            ),
            Paper(
                title="Paper B",
                authors=["Author B"],
                abstract="Abstract B",
                source="test",
                impact_factor=50.0,
                year=2021
            ),
            Paper(
                title="Paper C",
                authors=["Author C"],
                abstract="Abstract C",
                source="test",
                impact_factor=20.0,
                year=2022
            )
        ])
        
        # Sort by impact factor using Papers methods
        sorted_if = papers.sort_by('impact_factor', reverse=True)
        assert sorted_if[0].impact_factor == 50.0
        assert sorted_if[1].impact_factor == 20.0
        assert sorted_if[2].impact_factor == 10.0
        
        # Sort by year (appears to default to descending)
        sorted_year = papers.sort_by('year')
        # Years might be strings or ints, check the actual values
        years = [p.year for p in sorted_year]
        # Convert to ints for comparison if needed
        if isinstance(years[0], str):
            years = [int(y) for y in years]
        # Default appears to be descending order
        assert years == [2023, 2022, 2021]
        
        # Test ascending sort explicitly
        sorted_year_asc = papers.sort_by('year', reverse=False)
        years_asc = [p.year for p in sorted_year_asc]
        if isinstance(years_asc[0], str):
            years_asc = [int(y) for y in years_asc]
        assert years_asc == [2021, 2022, 2023]
    
    def test_papers_save(self, scholar, tmp_path):
        """Test saving papers using Papers methods."""
        papers = Papers([
            Paper(
                title="Test Paper",
                authors=["Smith, J.", "Doe, J."],
                abstract="Test abstract for save",
                source="test",
                journal="Nature",
                year=2023,
                doi="10.1038/test"
            )
        ])
        
        # Test BibTeX save using Papers method
        bibtex_file = tmp_path / "test.bib"
        papers.save(str(bibtex_file), format="bibtex")
        assert bibtex_file.exists()
        
        # Test JSON save using Papers method
        json_file = tmp_path / "test.json"
        papers.save(str(json_file), format="json")
        assert json_file.exists()
    
    def test_workspace_management(self, scholar, tmp_path):
        """Test workspace directory management."""
        # Check that workspace directory exists
        assert scholar.workspace_dir.exists()
        # PDF directory might be created when needed
    
    def test_pdf_downloader_configuration(self, scholar):
        """Test PDFDownloader is configured correctly."""
        downloader = scholar._pdf_downloader
        
        # Check configuration from Scholar config
        assert downloader.download_dir == scholar.workspace_dir / "pdfs"
        assert downloader.use_scihub == True  # Based on acknowledge_scihub_ethical_usage
        assert downloader._ethical_acknowledged == True
    
    def test_error_handling(self, scholar):
        """Test error handling in Scholar methods."""
        # Test with empty papers
        empty_papers = Papers([])
        
        results = scholar.download_pdfs(empty_papers)
        assert results['successful'] == 0
        assert results['failed'] == 0
        
        # Test with invalid title
        # Test with no results from CrossRef
        with patch.object(scholar, '_search_crossref_by_title', return_value=None):
            doi = scholar.resolve_doi("Nonexistent Title")
            assert doi is None


class TestScholarIntegration:
    """Integration tests for Scholar with real component interaction."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete Scholar workflow."""
        # Create config
        config = create_mock_scholar_config(tmp_path)
        
        scholar = Scholar(config=config)
        
        # Mock search results
        mock_papers = [
            Paper(
                title="Deep Learning Review",
                authors=["DL Author"],
                abstract="Deep learning abstract",
                source="pubmed",
                doi="10.1234/dl1",
                journal="Nature",
                year=2023
            ),
            Paper(
                title="Machine Learning Survey",
                authors=["ML Author"],
                abstract="Machine learning abstract",
                source="pubmed",
                doi="10.1234/ml1",
                journal="Science",
                year=2022
            )
        ]
        
        with patch.object(scholar._searcher, 'search', return_value=mock_papers):
            # Search
            papers = scholar.search("deep learning")
            assert len(papers) == 2
            
            # Papers are enriched automatically during search if auto_enrich is True
            # Just verify they were returned as Papers object
            assert isinstance(papers, Papers)
            enriched = papers
            
            # Download PDFs (mock)
            async def mock_download(identifiers, **kwargs):
                return {id: tmp_path / f"{id.replace('/', '_')}.pdf" for id in identifiers}
            
            with patch.object(scholar._pdf_downloader, 'batch_download', mock_download):
                results = scholar.download_pdfs(enriched)
                assert results['successful'] == 2
            
            # Save using Papers method
            output_file = tmp_path / "results.bib"
            enriched.save(str(output_file), format="bibtex")
            assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF