#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:40:00 (ywatanabe)"
# File: tests/scitex_scholar/test_paper_acquisition.py

"""
Test module for paper acquisition functionality.

This module tests the automated paper search and download capabilities
from various sources including PubMed and arXiv.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
sys.path.insert(0, './src')

from scitex_scholar.paper_acquisition import PaperAcquisition, PaperMetadata


class TestPaperAcquisition(unittest.TestCase):
    """Test suite for paper acquisition functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.download_dir = Path(cls.temp_dir) / "downloads"
        cls.download_dir.mkdir()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up for each test."""
        self.acquisition = PaperAcquisition(
            download_dir=self.download_dir,
            email="test@example.com"
        )
    
    def test_paper_acquisition_initialization(self):
        """Test PaperAcquisition can be initialized."""
        self.assertIsNotNone(self.acquisition)
        self.assertEqual(self.acquisition.email, "test@example.com")
        self.assertTrue(self.download_dir.exists())
    
    def test_paper_metadata_creation(self):
        """Test PaperMetadata dataclass."""
        metadata = PaperMetadata(
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            abstract="This is a test abstract",
            year="2024",
            doi="10.1234/test",
            pmid="12345678",
            source="test"
        )
        
        self.assertEqual(metadata.title, "Test Paper")
        self.assertEqual(len(metadata.authors), 2)
        self.assertEqual(metadata.year, "2024")
        
        # Test to_dict conversion
        data = metadata.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['title'], "Test Paper")
    
    @patch('aiohttp.ClientSession.get')
    async def test_search_pubmed(self, mock_get):
        """Test PubMed search functionality."""
        # Mock PubMed API responses
        search_response = AsyncMock()
        search_response.json = AsyncMock(return_value={
            'esearchresult': {
                'idlist': ['12345', '67890']
            }
        })
        
        fetch_response = AsyncMock()
        fetch_response.text = AsyncMock(return_value='''
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <ArticleTitle>Test Article</ArticleTitle>
                        <Abstract>
                            <AbstractText>Test abstract text</AbstractText>
                        </Abstract>
                        <AuthorList>
                            <Author>
                                <LastName>Doe</LastName>
                                <ForeName>John</ForeName>
                            </Author>
                        </AuthorList>
                        <Journal>
                            <Title>Test Journal</Title>
                        </Journal>
                        <PubDate>
                            <Year>2024</Year>
                        </PubDate>
                    </Article>
                    <PMID>12345</PMID>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>
        ''')
        
        mock_get.side_effect = [search_response, fetch_response]
        
        # Perform search
        results = await self.acquisition._search_pubmed(
            session=Mock(),
            query="test query",
            max_results=10,
            start_year=None,
            end_year=None
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].title, "Test Article")
        self.assertEqual(results[0].pmid, "12345")
    
    @patch('aiohttp.ClientSession.get')
    async def test_search_arxiv(self, mock_get):
        """Test arXiv search functionality."""
        # Mock arXiv API response
        arxiv_response = AsyncMock()
        arxiv_response.text = AsyncMock(return_value='''
        <?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2401.12345</id>
                <title>Test arXiv Paper</title>
                <summary>Test abstract for arXiv paper</summary>
                <author>
                    <name>John Doe</name>
                </author>
                <published>2024-01-15T00:00:00Z</published>
                <category term="cs.LG"/>
            </entry>
        </feed>
        ''')
        
        mock_get.return_value.__aenter__.return_value = arxiv_response
        
        # Perform search
        results = await self.acquisition._search_arxiv(
            session=Mock(),
            query="machine learning",
            max_results=5
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].title, "Test arXiv Paper")
        self.assertEqual(results[0].arxiv_id, "2401.12345")
        self.assertIn("cs.LG", results[0].keywords)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test_rate_limit():
            # Record time before
            import time
            start = time.time()
            
            # Make two requests
            await self.acquisition._rate_limit('pubmed')
            await self.acquisition._rate_limit('pubmed')
            
            # Should have waited
            elapsed = time.time() - start
            self.assertGreaterEqual(elapsed, self.acquisition.rate_limits['pubmed'])
        
        loop.run_until_complete(test_rate_limit())
        loop.close()
    
    def test_deduplicate_results(self):
        """Test deduplication of search results."""
        papers = [
            PaperMetadata(title="Machine Learning Paper", source="pubmed"),
            PaperMetadata(title="machine learning paper", source="arxiv"),  # Duplicate
            PaperMetadata(title="Deep Learning Paper", source="pubmed"),
            PaperMetadata(title="MACHINE LEARNING PAPER!", source="biorxiv"),  # Duplicate
        ]
        
        unique = self.acquisition._deduplicate_results(papers)
        
        self.assertEqual(len(unique), 2)
        titles = [p.title for p in unique]
        self.assertIn("Machine Learning Paper", titles)
        self.assertIn("Deep Learning Paper", titles)
    
    @patch('aiohttp.ClientSession.get')
    async def test_download_paper(self, mock_get):
        """Test paper download functionality."""
        # Create a paper with PDF URL
        paper = PaperMetadata(
            title="Test Download Paper",
            arxiv_id="2401.12345",
            pdf_url="https://arxiv.org/pdf/2401.12345.pdf"
        )
        
        # Mock PDF download
        pdf_response = AsyncMock()
        pdf_response.status = 200
        pdf_response.read = AsyncMock(return_value=b"PDF content here")
        mock_get.return_value.__aenter__.return_value = pdf_response
        
        # Download paper
        filepath = await self.acquisition.download_paper(paper)
        
        self.assertIsNotNone(filepath)
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.read_bytes(), b"PDF content here")
    
    @patch('aiohttp.ClientSession.get')
    async def test_batch_download(self, mock_get):
        """Test batch download functionality."""
        # Create test papers
        papers = [
            PaperMetadata(
                title=f"Paper {i}",
                arxiv_id=f"2401.{i:05d}",
                pdf_url=f"https://arxiv.org/pdf/2401.{i:05d}.pdf"
            )
            for i in range(3)
        ]
        
        # Mock PDF responses
        pdf_response = AsyncMock()
        pdf_response.status = 200
        pdf_response.read = AsyncMock(return_value=b"PDF content")
        mock_get.return_value.__aenter__.return_value = pdf_response
        
        # Batch download
        downloaded = await self.acquisition.batch_download(papers, max_concurrent=2)
        
        self.assertEqual(len(downloaded), 3)
        for title, path in downloaded.items():
            self.assertTrue(path.exists())
    
    @patch('aiohttp.ClientSession')
    async def test_multi_source_search(self, mock_session):
        """Test searching across multiple sources."""
        # Mock session
        session_instance = AsyncMock()
        mock_session.return_value.__aenter__.return_value = session_instance
        
        # Mock empty responses for simplicity
        self.acquisition._search_pubmed = AsyncMock(return_value=[
            PaperMetadata(title="PubMed Paper", source="pubmed")
        ])
        self.acquisition._search_arxiv = AsyncMock(return_value=[
            PaperMetadata(title="arXiv Paper", source="arxiv")
        ])
        self.acquisition._search_biorxiv = AsyncMock(return_value=[])
        
        # Search multiple sources
        results = await self.acquisition.search(
            query="test",
            sources=['pubmed', 'arxiv', 'biorxiv'],
            max_results=10
        )
        
        self.assertEqual(len(results), 2)
        sources = [p.source for p in results]
        self.assertIn('pubmed', sources)
        self.assertIn('arxiv', sources)
    
    @patch('aiohttp.ClientSession.get')
    async def test_find_open_access_pdf(self, mock_get):
        """Test finding open access PDFs via Unpaywall."""
        paper = PaperMetadata(
            title="Test Paper",
            doi="10.1234/test"
        )
        
        # Mock Unpaywall response
        unpaywall_response = AsyncMock()
        unpaywall_response.status = 200
        unpaywall_response.json = AsyncMock(return_value={
            'best_oa_location': {
                'url_for_pdf': 'https://example.com/paper.pdf'
            }
        })
        mock_get.return_value.__aenter__.return_value = unpaywall_response
        
        # Find open access PDF
        pdf_url = await self.acquisition._find_open_access_pdf(paper)
        
        self.assertEqual(pdf_url, 'https://example.com/paper.pdf')


if __name__ == "__main__":
    # Run async tests
    unittest.main()

# EOF