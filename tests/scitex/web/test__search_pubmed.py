#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-08 05:50:57 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/web/test__search_pubmed.py

"""
Tests for PubMed search functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import xml.etree.ElementTree as ET
import json
import asyncio
import aiohttp
from io import StringIO

from scitex.web import (
    _search_pubmed,
    _fetch_details,
    _parse_abstract_xml,
    _get_citation,
    get_crossref_metrics,
    save_bibtex,
    format_bibtex,
    fetch_async,
    batch__fetch_details,
    search_pubmed,
    parse_args,
    run_main
)


class TestSearchPubmed:
    """Test _search_pubmed function."""
    
    def test_search_pubmed_success(self):
        """Test successful PubMed search."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "esearchresult": {
                "idlist": ["12345", "67890"],
                "count": "2"
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = _search_pubmed("test query", retmax=10)
            assert result == mock_response.json.return_value
            assert len(result["esearchresult"]["idlist"]) == 2
    
    def test_search_pubmed_failure(self):
        """Test failed PubMed search."""
        mock_response = Mock()
        mock_response.ok = False
        
        with patch('requests.get', return_value=mock_response):
            with patch('scitex.str.printc') as mock_print:
                result = _search_pubmed("test query")
                assert result == {}
                mock_print.assert_called_once()
    
    def test_search_pubmed_network_error(self):
        """Test network error during search."""
        import requests
        
        with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
            with patch('scitex.str.printc') as mock_print:
                result = _search_pubmed("test query")
                assert result == {}
                mock_print.assert_called_once()
    
    def test_search_pubmed_parameters(self):
        """Test search parameters are correctly passed."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"esearchresult": {}}
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            _search_pubmed("epilepsy", retmax=500)
            
            # Check that correct parameters were passed
            args, kwargs = mock_get.call_args
            assert kwargs['params']['term'] == "epilepsy"
            assert kwargs['params']['retmax'] == 500
            assert kwargs['params']['db'] == "pubmed"


class TestFetchDetails:
    """Test _fetch_details function."""
    
    def test_fetch_details_success(self):
        """Test successful fetch of article details."""
        mock_abstract_response = Mock()
        mock_abstract_response.ok = True
        mock_abstract_response.text = "<xml>abstract data</xml>"
        
        mock_details_response = Mock()
        mock_details_response.ok = True
        mock_details_response.json.return_value = {"result": {"12345": {"title": "Test"}}}
        
        with patch('requests.get', side_effect=[mock_abstract_response, mock_details_response]):
            result = _fetch_details("webenv123", "query_key456", retstart=0, retmax=100)
            assert result["abstracts"] == "<xml>abstract data</xml>"
            assert result["details"] == mock_details_response.json.return_value
    
    def test_fetch_details_failure(self):
        """Test failed fetch of article details."""
        mock_response = Mock()
        mock_response.ok = False
        
        with patch('requests.get', return_value=mock_response):
            result = _fetch_details("webenv123", "query_key456")
            assert result == {}
    
    def test_fetch_details_parameters(self):
        """Test fetch details parameters."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = ""
        mock_response.json.return_value = {}
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            _fetch_details("env123", "key456", retstart=100, retmax=50)
            
            # Verify two calls were made
            assert mock_get.call_count == 2
            
            # Check parameters for abstract fetch
            first_call_params = mock_get.call_args_list[0][1]['params']
            assert first_call_params['WebEnv'] == "env123"
            assert first_call_params['query_key'] == "key456"
            assert first_call_params['retstart'] == 100
            assert first_call_params['retmax'] == 50


class TestParseAbstractXml:
    """Test _parse_abstract_xml function."""
    
    def test_parse_abstract_xml_complete(self):
        """Test parsing complete XML with all fields."""
        xml_text = """
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>12345</PMID>
                    <Article>
                        <Abstract>
                            <AbstractText>This is the abstract text.</AbstractText>
                        </Abstract>
                    </Article>
                </MedlineCitation>
                <PubmedData>
                    <ArticleIdList>
                        <ArticleId IdType="doi">10.1234/test.doi</ArticleId>
                    </ArticleIdList>
                </PubmedData>
                <MeshHeadingList>
                    <MeshHeading>
                        <DescriptorName>Keyword1</DescriptorName>
                    </MeshHeading>
                    <MeshHeading>
                        <DescriptorName>Keyword2</DescriptorName>
                    </MeshHeading>
                </MeshHeadingList>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        result = _parse_abstract_xml(xml_text)
        assert "12345" in result
        assert result["12345"][0] == "This is the abstract text."
        assert result["12345"][1] == ["Keyword1", "Keyword2"]
        assert result["12345"][2] == "10.1234/test.doi"
    
    def test_parse_abstract_xml_missing_fields(self):
        """Test parsing XML with missing fields."""
        xml_text = """
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>67890</PMID>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        result = _parse_abstract_xml(xml_text)
        assert "67890" in result
        assert result["67890"][0] == ""  # No abstract
        assert result["67890"][1] == []  # No keywords
        assert result["67890"][2] == ""  # No DOI
    
    def test_parse_abstract_xml_multiple_articles(self):
        """Test parsing XML with multiple articles."""
        xml_text = """
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>11111</PMID>
                </MedlineCitation>
            </PubmedArticle>
            <PubmedArticle>
                <MedlineCitation>
                    <PMID>22222</PMID>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        """
        
        result = _parse_abstract_xml(xml_text)
        assert len(result) == 2
        assert "11111" in result
        assert "22222" in result


class TestGetCitation:
    """Test _get_citation function."""
    
    def test_get_citation_success(self):
        """Test successful citation retrieval."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "@article{test_citation}"
        
        with patch('requests.get', return_value=mock_response):
            result = _get_citation("12345")
            assert result == "@article{test_citation}"
    
    def test_get_citation_failure(self):
        """Test failed citation retrieval."""
        mock_response = Mock()
        mock_response.ok = False
        
        with patch('requests.get', return_value=mock_response):
            result = _get_citation("12345")
            assert result == ""
    
    def test_get_citation_parameters(self):
        """Test citation parameters."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = ""
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            _get_citation("99999")
            
            args, kwargs = mock_get.call_args
            assert kwargs['params']['db'] == "pubmed"
            assert kwargs['params']['id'] == "99999"
            assert kwargs['params']['rettype'] == "bibtex"


class TestGetCrossrefMetrics:
    """Test get_crossref_metrics function."""
    
    def test_get_crossref_metrics_success(self):
        """Test successful CrossRef metrics retrieval."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "message": {
                "is-referenced-by-count": 42,
                "type": "journal-article",
                "publisher": "Test Publisher",
                "reference": [1, 2, 3],
                "DOI": "10.1234/test"
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = get_crossref_metrics("10.1234/test")
            assert result["citations"] == 42
            assert result["type"] == "journal-article"
            assert result["publisher"] == "Test Publisher"
            assert result["references"] == 3
            assert result["doi"] == "10.1234/test"
    
    def test_get_crossref_metrics_failure(self):
        """Test failed CrossRef metrics retrieval."""
        mock_response = Mock()
        mock_response.ok = False
        
        with patch('requests.get', return_value=mock_response):
            result = get_crossref_metrics("10.1234/test")
            assert result == {}
    
    def test_get_crossref_metrics_missing_fields(self):
        """Test CrossRef metrics with missing fields."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"message": {}}
        
        with patch('requests.get', return_value=mock_response):
            result = get_crossref_metrics("10.1234/test")
            assert result["citations"] == 0
            assert result["type"] == ""
            assert result["publisher"] == ""
            assert result["references"] == 0
            assert result["doi"] == ""


class TestSaveBibtex:
    """Test save_bibtex function."""
    
    def test_save_bibtex_with_citations(self):
        """Test saving BibTeX with official citations."""
        papers = {
            "12345": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}],
                "source": "Test Journal",
                "pubdate": "2023"
            }
        }
        abstracts = {
            "12345": ("Abstract text", ["Keyword1"], "10.1234/test")
        }
        
        mock_citation = "@article{official_citation}"
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('scitex.web._search_pubmed._get_citation', return_value=mock_citation):
                with patch('scitex.str.printc'):
                    save_bibtex(papers, abstracts, "test.bib")
                    
                    # Verify file was written
                    mock_file.assert_called_once_with("test.bib", "w", encoding="utf-8")
                    handle = mock_file()
                    handle.write.assert_called_with(mock_citation)
    
    def test_save_bibtex_without_citations(self):
        """Test saving BibTeX without official citations."""
        papers = {
            "67890": {
                "title": "Test Paper Without Citation",
                "authors": [{"name": "Jane Smith"}],
                "source": "Another Journal",
                "pubdate": "2024"
            }
        }
        abstracts = {}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('scitex.web._search_pubmed._get_citation', return_value=""):
                with patch('scitex.web._search_pubmed.format_bibtex', return_value="@article{formatted}") as mock_format:
                    with patch('scitex.str.printc'):
                        save_bibtex(papers, abstracts, "test.bib")
                        
                        # Verify format_bibtex was called
                        mock_format.assert_called_once()
                        handle = mock_file()
                        handle.write.assert_called_with("@article{formatted}\n")
    
    def test_save_bibtex_skip_uids(self):
        """Test that 'uids' key is skipped."""
        papers = {
            "uids": ["12345"],
            "12345": {"title": "Real Paper"}
        }
        abstracts = {}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('scitex.web._search_pubmed._get_citation', return_value=""):
                with patch('scitex.web._search_pubmed.format_bibtex') as mock_format:
                    with patch('scitex.str.printc'):
                        save_bibtex(papers, abstracts, "test.bib")
                        
                        # Verify format_bibtex was called only once (not for 'uids')
                        assert mock_format.call_count == 1


class TestFormatBibtex:
    """Test format_bibtex function."""
    
    def test_format_bibtex_complete(self):
        """Test formatting complete BibTeX entry."""
        paper = {
            "title": "Machine Learning for Medical Diagnosis",
            "authors": [{"name": "John A. Smith"}, {"name": "Jane B. Doe"}],
            "source": "Nature Medicine",
            "pubdate": "2023 Jul 15"
        }
        pmid = "12345678"
        abstract_data = (
            "This is the abstract text.",
            ["Machine Learning", "Diagnosis"],
            "10.1038/s41591-023-12345"
        )
        
        with patch('scitex.web._search_pubmed.get_crossref_metrics', return_value={
            "publisher": "Nature Publishing",
            "references": 50
        }):
            result = format_bibtex(paper, pmid, abstract_data)
            
            # Check key components
            assert "@article{JohnSmith_2023_machine_learning" in result
            assert "author = {John A. Smith and Jane B. Doe}" in result
            assert "title = {Machine Learning for Medical Diagnosis}" in result
            assert "journal = {Nature Medicine}" in result
            assert "year = {2023}" in result
            assert "pmid = {12345678}" in result
            assert "doi = {10.1038/s41591-023-12345}" in result
            assert "keywords = {Machine Learning, Diagnosis}" in result
            assert "abstract = {This is the abstract text.}" in result
    
    def test_format_bibtex_minimal(self):
        """Test formatting BibTeX with minimal data."""
        paper = {
            "title": "A",
            "authors": [{"name": "X"}],
            "source": "Unknown Journal",
            "pubdate": ""
        }
        pmid = "99999"
        abstract_data = ("", [], "")
        
        with patch('scitex.web._search_pubmed.get_crossref_metrics', return_value={}):
            result = format_bibtex(paper, pmid, abstract_data)
            
            # Check it doesn't crash and produces valid entry
            assert "@article{" in result
            assert "pmid = {99999}" in result
    
    def test_format_bibtex_special_characters(self):
        """Test formatting with special characters in names."""
        paper = {
            "title": "Test-Paper: With Special Characters!",
            "authors": [{"name": "O'Neill-Smith"}],
            "source": "Test Journal",
            "pubdate": "2023"
        }
        pmid = "11111"
        abstract_data = ("", [], "")
        
        with patch('scitex.web._search_pubmed.get_crossref_metrics', return_value={}):
            result = format_bibtex(paper, pmid, abstract_data)
            
            # Check citation key is properly cleaned
            assert "@article{ONeillSmith_2023_testpaper_with" in result


class TestAsyncFunctions:
    """Test async functions."""
    
    @pytest.mark.asyncio
    async def test_fetch_async_json(self):
        """Test async fetch with JSON response."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {"test": "data"})
        
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await fetch_async(mock_session, "http://test.com", {"retmode": "json"})
        assert result == {"test": "data"}
    
    @pytest.mark.asyncio
    async def test_fetch_async_xml(self):
        """Test async fetch with XML response."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = asyncio.coroutine(lambda: "<xml>test</xml>")
        
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await fetch_async(mock_session, "http://test.com", {"retmode": "xml"})
        assert result == "<xml>test</xml>"
    
    @pytest.mark.asyncio
    async def test_fetch_async_failure(self):
        """Test async fetch with failed response."""
        mock_response = MagicMock()
        mock_response.status = 404
        
        mock_session = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        result = await fetch_async(mock_session, "http://test.com", {})
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_batch_fetch_details(self):
        """Test batch fetching details."""
        pmids = ["11111", "22222", "33333"]
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session
            
            with patch('scitex.web._search_pubmed.fetch_async', side_effect=[
                "<xml>1</xml>", {"result": "1"},
                "<xml>2</xml>", {"result": "2"}
            ]):
                results = await batch__fetch_details(pmids, batch_size=2)
                
                assert len(results) == 4  # 2 batches × 2 requests each
                assert results[0] == "<xml>1</xml>"
                assert results[1] == {"result": "1"}


class TestSearchPubmedMain:
    """Test main search_pubmed function."""
    
    def test_search_pubmed_no_results(self):
        """Test search with no results."""
        with patch('scitex.web._search_pubmed._search_pubmed', return_value={}):
            result = search_pubmed("test query", n_entries=10)
            assert result == 1
    
    def test_search_pubmed_success(self):
        """Test successful search and save."""
        search_results = {
            "esearchresult": {
                "idlist": ["12345", "67890"],
                "count": "2"
            }
        }
        
        batch_results = [
            "<PubmedArticleSet></PubmedArticleSet>",  # XML
            {"result": {"12345": {"title": "Test1"}, "67890": {"title": "Test2"}}},  # JSON
        ]
        
        with patch('scitex.web._search_pubmed._search_pubmed', return_value=search_results):
            with patch('asyncio.run', return_value=batch_results):
                with patch('builtins.open', mock_open()) as mock_file:
                    with patch('scitex.web._search_pubmed._parse_abstract_xml', return_value={}):
                        with patch('scitex.web._search_pubmed._get_citation', return_value=""):
                            with patch('scitex.web._search_pubmed.format_bibtex', return_value="@article{}"):
                                result = search_pubmed("test query", n_entries=2)
                                assert result == 0
                                
                                # Verify file operations
                                assert mock_file.call_count == 2  # Two writes
    
    def test_search_pubmed_query_sanitization(self):
        """Test that query is properly sanitized for filename."""
        search_results = {"esearchresult": {"idlist": [], "count": "0"}}
        
        with patch('scitex.web._search_pubmed._search_pubmed', return_value=search_results):
            with patch('asyncio.run', return_value=[]):
                with patch('builtins.open', mock_open()) as mock_file:
                    search_pubmed("test query with spaces", n_entries=0)
                    
                    # Check filename has underscores
                    filename = mock_file.call_args_list[0][0][0]
                    assert filename == "pubmed_test_query_with_spaces.bib"


class TestParseArgs:
    """Test parse_args function."""
    
    def test_parse_args_with_query(self):
        """Test parsing arguments with query."""
        with patch('sys.argv', ['script.py', '--query', 'epilepsy prediction', '--n_entries', '20']):
            with patch('scitex.str.printc'):
                args = parse_args()
                assert args.query == 'epilepsy prediction'
                assert args.n_entries == 20
    
    def test_parse_args_defaults(self):
        """Test parsing arguments with defaults."""
        with patch('sys.argv', ['script.py']):
            with patch('scitex.str.printc'):
                args = parse_args()
                assert args.query is None
                assert args.n_entries == 10
    
    def test_parse_args_short_options(self):
        """Test parsing with short options."""
        with patch('sys.argv', ['script.py', '-q', 'test', '-n', '5']):
            with patch('scitex.str.printc'):
                args = parse_args()
                assert args.query == 'test'
                assert args.n_entries == 5


class TestRunMain:
    """Test run_main function."""
    
    def test_run_main_success(self):
        """Test successful main execution."""
        mock_args = Mock()
        mock_args.query = "test query"
        mock_args.n_entries = 10
        
        with patch('scitex.gen.start', return_value=(None, None, None, None, None)):
            with patch('scitex.web._search_pubmed.parse_args', return_value=mock_args):
                with patch('scitex.web._search_pubmed.search_pubmed', return_value=0) as mock_search:
                    with patch('scitex.gen.close'):
                        run_main()
                        
                        mock_search.assert_called_once_with("test query", 10)
    
    def test_run_main_with_error(self):
        """Test main execution with error."""
        mock_args = Mock()
        mock_args.query = "test"
        mock_args.n_entries = 5
        
        with patch('scitex.gen.start', return_value=(None, None, None, None, None)):
            with patch('scitex.web._search_pubmed.parse_args', return_value=mock_args):
                with patch('scitex.web._search_pubmed.search_pubmed', return_value=1):
                    with patch('scitex.gen.close') as mock_close:
                        run_main()
                        
                        # Verify close was called with exit_status=1
                        assert mock_close.call_args[1]['exit_status'] == 1

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/web/_search_pubmed.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-13 14:30:43 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/web/_search_pubmed.py
# 
# """
# 1. Functionality:
#    - Searches PubMed database for scientific articles
#    - Retrieves detailed information about matched articles
#    - Displays article metadata including title, authors, journal, year, and abstract
# 2. Input:
#    - Search query string (e.g., "epilepsy prediction")
#    - Optional parameters for batch size and result limit
# 3. Output:
#    - Formatted article information displayed to stdout
#    - BibTeX file with official citations
# 4. Prerequisites:
#    - Internet connection
#    - requests package
#    - scitex package
# """
# 
# """Imports"""
# import argparse
# import asyncio
# import xml.etree.ElementTree as ET
# from typing import Any, Dict, List, Optional, Union
# 
# import aiohttp
# import scitex
# import pandas as pd
# import requests
# 
# """Functions & Classes"""
# 
# 
# def _search_pubmed(query: str, retmax: int = 300) -> Dict[str, Any]:
#     try:
#         base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
#         search_url = f"{base_url}esearch.fcgi"
#         params = {
#             "db": "pubmed",
#             "term": query,
#             "retmax": retmax,
#             "retmode": "json",
#             "usehistory": "y",
#         }
# 
#         response = requests.get(search_url, params=params, timeout=10)
#         if not response.ok:
#             scitex.str.printc("PubMed API request failed", c="red")
#             return {}
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         scitex.str.printc(f"Network error: {e}", c="red")
#         return {}
# 
# 
# def _fetch_details(
#     webenv: str, query_key: str, retstart: int = 0, retmax: int = 100
# ) -> Dict[str, Any]:
#     """Fetches detailed information including abstracts for articles.
# 
#     Parameters
#     ----------
#     [Previous parameters remain the same]
# 
#     Returns
#     -------
#     Dict[str, Any]
#         Dictionary containing article details and abstracts
#     """
#     base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
# 
#     # Fetch abstracts
#     efetch_url = f"{base_url}efetch.fcgi"
#     efetch_params = {
#         "db": "pubmed",
#         "query_key": query_key,
#         "WebEnv": webenv,
#         "retstart": retstart,
#         "retmax": retmax,
#         "retmode": "xml",
#         "rettype": "abstract",
#         "field": "abstract,mesh",
#     }
# 
#     abstract_response = requests.get(efetch_url, params=efetch_params)
# 
#     # Fetch metadata
#     fetch_url = f"{base_url}esummary.fcgi"
#     params = {
#         "db": "pubmed",
#         "query_key": query_key,
#         "WebEnv": webenv,
#         "retstart": retstart,
#         "retmax": retmax,
#         "retmode": "json",
#     }
# 
#     details_response = requests.get(fetch_url, params=params)
# 
#     if not all([abstract_response.ok, details_response.ok]):
#         # print(f"Error fetching data")
#         return {}
# 
#     return {
#         "abstracts": abstract_response.text,
#         "details": details_response.json(),
#     }
# 
# 
# def _parse_abstract_xml(xml_text: str) -> Dict[str, tuple]:
#     """Parses XML response to extract abstracts.
# 
#     Parameters
#     ----------
#     xml_text : str
#         XML response from PubMed
# 
#     Returns
#     -------
#     Dict[str, str]
#         Dictionary mapping PMIDs to abstracts
#     """
#     root = ET.fromstring(xml_text)
#     results = {}
# 
#     for article in root.findall(".//PubmedArticle"):
#         pmid = article.find(".//PMID").text
#         abstract_element = article.find(".//Abstract/AbstractText")
#         abstract = abstract_element.text if abstract_element is not None else ""
# 
#         # DOI
#         doi_element = article.find(".//ArticleId[@IdType='doi']")
#         doi = doi_element.text if doi_element is not None else ""
# 
#         # Get MeSH terms
#         keywords = []
#         mesh_terms = article.findall(".//MeshHeading/DescriptorName")
#         keywords = [term.text for term in mesh_terms if term is not None]
# 
#         results[pmid] = (abstract, keywords, doi)
# 
#     return results
# 
# 
# def _get_citation(pmid: str) -> str:
#     """Gets official citation in BibTeX format.
# 
#     Parameters
#     ----------
#     pmid : str
#         PubMed ID
# 
#     Returns
#     -------
#     str
#         Official BibTeX citation
#     """
#     base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
#     cite_url = f"{base_url}efetch.fcgi"
#     params = {
#         "db": "pubmed",
#         "id": pmid,
#         "rettype": "bibtex",
#         "retmode": "text",
#     }
#     response = requests.get(cite_url, params=params)
#     return response.text if response.ok else ""
# 
# 
# def get_crossref_metrics(doi: str, api_key: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
#     """Get article metrics from CrossRef using DOI."""
#     import os
#     base_url = "https://api.crossref.org/works/"
#     
#     # Use provided email or fallback to environment variables
#     if not email:
#         email = os.getenv("SCITEX_CROSSREF_EMAIL", os.getenv("SCITEX_PUBMED_EMAIL", "research@example.com"))
#     headers = {"User-Agent": f"SciTeX/1.0 (mailto:{email})"}
#     
#     # Add API key as query parameter if provided
#     params = {}
#     if api_key:
#         params['key'] = api_key
# 
#     try:
#         response = requests.get(f"{base_url}{doi}", headers=headers, params=params, timeout=10)
#         if response.ok:
#             data = response.json()["message"]
#             return {
#                 "citations": data.get("is-referenced-by-count", 0),
#                 "type": data.get("type", ""),
#                 "publisher": data.get("publisher", ""),
#                 "references": len(data.get("reference", [])),
#                 "doi": data.get("DOI", ""),
#             }
#     except Exception as e:
#         print(f"CrossRef API error for DOI {doi}: {e}")
#     return {}
# 
# 
# async def get_crossref_metrics_async(doi: str, api_key: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
#     """Get article metrics from CrossRef using DOI (async version)."""
#     import os
#     base_url = "https://api.crossref.org/works/"
#     
#     # Use provided email or fallback to environment variables
#     if not email:
#         email = os.getenv("SCITEX_CROSSREF_EMAIL", os.getenv("SCITEX_PUBMED_EMAIL", "research@example.com"))
#     headers = {"User-Agent": f"SciTeX/1.0 (mailto:{email})"}
#     
#     # Add API key as query parameter if provided
#     params = {}
#     if api_key:
#         params['key'] = api_key
# 
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(f"{base_url}{doi}", headers=headers, params=params, timeout=10) as response:
#                 if response.ok:
#                     data = await response.json()
#                     message = data["message"]
#                     return {
#                         "citations": message.get("is-referenced-by-count", 0),
#                         "type": message.get("type", ""),
#                         "publisher": message.get("publisher", ""),
#                         "references": len(message.get("reference", [])),
#                         "doi": message.get("DOI", ""),
#                     }
#     except Exception as e:
#         print(f"CrossRef API error for DOI {doi}: {e}")
#     return {}
# 
# 
# def save_bibtex(
#     papers: Dict[str, Any], abstracts: Dict[str, str], output_file: str
# ) -> None:
#     """Saves paper metadata as BibTeX file with abstracts.
# 
#     Parameters
#     ----------
#     papers : Dict[str, Any]
#         Dictionary of paper metadata
#     abstracts : Dict[str, str]
#         Dictionary of PMIDs to abstracts
#     output_file : str
#         Output file path
#     """
#     with open(output_file, "w", encoding="utf-8") as bibtex_file:
#         for pmid, paper in papers.items():
#             if pmid == "uids":
#                 continue
# 
#             citation = _get_citation(pmid)
#             if citation:
#                 bibtex_file.write(citation)
#             else:
#                 # Use default tuple if pmid not in abstracts
#                 default_data = ("", [], "")  # abstract, keywords, doi
#                 bibtex_entry = format_bibtex(
#                     paper, pmid, abstracts.get(pmid, default_data)
#                 )
#                 bibtex_file.write(bibtex_entry + "\n")
#     scitex.str.printc(f"Saved to: {str(bibtex_file)}", c="yellow")
# 
# 
# def format_bibtex(paper: Dict[str, Any], pmid: str, abstract_data: tuple) -> str:
#     abstract, keywords, doi = abstract_data
# 
#     # Get CrossRef and Scimago metrics
#     crossref_metrics = get_crossref_metrics(doi) if doi else {}
#     journal = paper.get("source", "Unknown Journal")
#     # journal_metrics = get_journal_metrics(journal)
# 
#     authors = paper.get("authors", [{"name": "Unknown"}])
#     author_names = " and ".join(author["name"] for author in authors)
#     year = paper.get("pubdate", "").split()[0]
#     title = paper.get("title", "No Title")
# 
#     # Name formatting
#     first_author = authors[0]["name"]
#     first_name = first_author.split()[0]
#     last_name = first_author.split()[-1]
#     clean_first_name = "".join(c for c in first_name if c.isalnum())
#     clean_last_name = "".join(c for c in last_name if c.isalnum())
# 
#     # Title words
#     title_words = title.split()
#     first_title_word = "".join(c.lower() for c in title_words[0] if c.isalnum())
#     second_title_word = (
#         "".join(c.lower() for c in title_words[1] if c.isalnum())
#         if len(title_words) > 1
#         else ""
#     )
# 
#     citation_key = f"{clean_first_name}.{clean_last_name}_{year}_{first_title_word}_{second_title_word}"
# 
#     entry = f"""@article{{{citation_key},
#     author = {{{author_names}}},
#     title = {{{title}}},
#     journal = {{{journal}}},
#     year = {{{year}}},
#     pmid = {{{pmid}}},
#     doi = {{{doi}}},
#     publisher = {{{crossref_metrics.get('publisher', '')}}},
#     references = {{{crossref_metrics.get('references', 0)}}},
#     keywords = {{{", ".join(keywords)}}},
#     abstract = {{{abstract}}}
# }}
# """
#     return entry
# 
# 
# async def fetch_async(
#     session: aiohttp.ClientSession, url: str, params: Dict
# ) -> Union[Dict, str]:
#     """Asynchronous fetch helper."""
#     async with session.get(url, params=params) as response:
#         if response.status == 200:
#             if params.get("retmode") == "xml":
#                 return await response.text()
#             elif params.get("retmode") == "json":
#                 return await response.json()
#             return await response.text()
#         return {}
# 
# 
# async def batch__fetch_details(pmids: List[str], batch_size: int = 20) -> List[Dict]:
#     """Fetches details for multiple PMIDs concurrently.
# 
#     Parameters
#     ----------
#     pmids : List[str]
#         List of PubMed IDs
#     batch_size : int, optional
#         Size of each batch for concurrent requests
# 
#     Returns
#     -------
#     List[Dict]
#         List of response data
#     """
#     base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
# 
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for i in range(0, len(pmids), batch_size):
#             batch_pmids = pmids[i : i + batch_size]
# 
#             # Fetch both details and citations concurrently
#             efetch_params = {
#                 "db": "pubmed",
#                 "id": ",".join(batch_pmids),
#                 "retmode": "xml",
#                 "rettype": "abstract",
#             }
# 
#             esummary_params = {
#                 "db": "pubmed",
#                 "id": ",".join(batch_pmids),
#                 "retmode": "json",
#             }
# 
#             tasks.append(fetch_async(session, f"{base_url}efetch.fcgi", efetch_params))
#             tasks.append(
#                 fetch_async(session, f"{base_url}esummary.fcgi", esummary_params)
#             )
# 
#         results = await asyncio.gather(*tasks)
#         return results
# 
# 
# def search_pubmed(query: str, n_entries: int = 10) -> int:
#     # query = args.query or "epilepsy prediction"
#     # print(f"Using query: {query}")
# 
#     search_results = _search_pubmed(query)
#     if not search_results:
#         # print("No results found or error occurred")
#         return 1
# 
#     pmids = search_results["esearchresult"]["idlist"]
#     count = len(pmids)
#     # print(f"Found {count:,} results")
# 
#     output_file = f"pubmed_{query.replace(' ', '_')}.bib"
#     # print(f"Saving results to: {output_file}")
# 
#     # Process in larger batches asynchronously
#     results = asyncio.run(batch__fetch_details(pmids[:n_entries]))
#     # here, results seems long string
# 
#     # Process results and save
#     with open(output_file, "w", encoding="utf-8") as f:
#         for i in range(0, len(results), 2):
#             xml_response = results[i]
#             json_response = results[i + 1]
# 
#             if isinstance(xml_response, str):
#                 abstracts = _parse_abstract_xml(xml_response)
#                 if isinstance(json_response, dict) and "result" in json_response:
#                     details = json_response["result"]
#                     save_bibtex(details, abstracts, output_file)
# 
#     # Process results and save
#     temp_bibtex = []
#     for i in range(0, len(results), 2):
#         xml_response = results[i]
#         json_response = results[i + 1]
# 
#         if isinstance(xml_response, str):
#             abstracts = _parse_abstract_xml(xml_response)
#             if isinstance(json_response, dict) and "result" in json_response:
#                 details = json_response["result"]
#                 for pmid in details:
#                     if pmid != "uids":
#                         citation = _get_citation(pmid)
#                         if citation:
#                             temp_bibtex.append(citation)
#                         else:
#                             entry = format_bibtex(
#                                 details[pmid], pmid, abstracts.get(pmid, "")
#                             )
#                             temp_bibtex.append(entry)
# 
#     # Write all entries at once
#     with open(output_file, "w", encoding="utf-8") as f:
#         f.write("\n".join(temp_bibtex))
# 
#     return 0
# 
# 
# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="PubMed article search and retrieval tool"
#     )
#     parser.add_argument(
#         "--query",
#         "-q",
#         type=str,
#         help='Search query (default: "epilepsy prediction")',
#     )
#     parser.add_argument(
#         "--n_entries",
#         "-n",
#         type=int,
#         default=10,
#         help='Search query (default: "epilepsy prediction")',
#     )
#     args = parser.parse_args()
#     scitex.str.printc(args, c="yellow")
#     return args
# 
# 
# def run_main() -> None:
#     global CONFIG
#     import sys
# 
#     import matplotlib.pyplot as plt
#     import scitex
# 
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
#         sys,
#         verbose=False,
#     )
# 
#     args = parse_args()
#     exit_status = search_pubmed(args.query, args.n_entries)
# 
#     scitex.gen.close(
#         CONFIG,
#         verbose=False,
#         notify=False,
#         message="",
#         exit_status=exit_status,
#     )
# 
# 
# if __name__ == "__main__":
#     run_main()
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/web/_search_pubmed.py
# --------------------------------------------------------------------------------
