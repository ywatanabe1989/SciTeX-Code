#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 04:10:00 (ywatanabe)"
# File: tests/scitex_scholar/test_literature_review_workflow.py

"""
Test module for literature review workflow functionality.

This module tests the complete workflow from paper discovery
to literature review generation.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import json
import sys
sys.path.insert(0, './src')

from scitex_scholar.literature_review_workflow import LiteratureReviewWorkflow
from scitex_scholar.paper_acquisition import PaperMetadata


class TestLiteratureReviewWorkflow(unittest.TestCase):
    """Test suite for literature review workflow functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.temp_dir = tempfile.mkdtemp()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up for each test."""
        self.workspace_dir = Path(self.temp_dir) / "test_workspace"
        self.workflow = LiteratureReviewWorkflow(
            workspace_dir=self.workspace_dir,
            email="test@example.com"
        )
    
    def test_workflow_initialization(self):
        """Test LiteratureReviewWorkflow initialization."""
        self.assertIsNotNone(self.workflow)
        self.assertTrue(self.workspace_dir.exists())
        self.assertTrue(self.workflow.papers_dir.exists())
        self.assertTrue(self.workflow.index_dir.exists())
        self.assertTrue(self.workflow.vector_db_dir.exists())
        self.assertTrue(self.workflow.metadata_dir.exists())
    
    def test_state_management(self):
        """Test workflow state loading and saving."""
        # Initial state
        self.assertIsInstance(self.workflow.state, dict)
        self.assertIn('searches', self.workflow.state)
        self.assertIn('downloaded_papers', self.workflow.state)
        
        # Modify state
        self.workflow.state['test_key'] = 'test_value'
        self.workflow._save_state()
        
        # Load in new workflow
        new_workflow = LiteratureReviewWorkflow(workspace_dir=self.workspace_dir)
        self.assertEqual(new_workflow.state['test_key'], 'test_value')
    
    @patch.object(LiteratureReviewWorkflow, 'acquisition')
    async def test_discover_papers(self, mock_acquisition):
        """Test paper discovery."""
        # Mock papers
        mock_papers = [
            PaperMetadata(
                title="Test Paper 1",
                authors=["Author 1"],
                year="2023",
                source="pubmed"
            ),
            PaperMetadata(
                title="Test Paper 2",
                authors=["Author 2"],
                year="2024",
                source="arxiv"
            )
        ]
        
        # Mock search method
        self.workflow.acquisition.search = AsyncMock(return_value=mock_papers)
        
        # Discover papers
        papers = await self.workflow.discover_papers(
            query="test query",
            sources=['pubmed', 'arxiv'],
            max_results=10
        )
        
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].title, "Test Paper 1")
        
        # Check state was updated
        self.assertEqual(len(self.workflow.state['searches']), 1)
        self.assertEqual(self.workflow.state['searches'][0]['query'], "test query")
    
    @patch.object(LiteratureReviewWorkflow, 'acquisition')
    async def test_acquire_papers(self, mock_acquisition):
        """Test paper acquisition."""
        # Mock papers
        papers = [
            PaperMetadata(
                title="Paper 1",
                pdf_url="http://example.com/paper1.pdf"
            ),
            PaperMetadata(
                title="Paper 2",
                pdf_url="http://example.com/paper2.pdf"
            )
        ]
        
        # Mock download
        mock_downloaded = {
            "Paper 1": Path(self.workspace_dir) / "paper1.pdf",
            "Paper 2": Path(self.workspace_dir) / "paper2.pdf"
        }
        
        self.workflow.acquisition.batch_download = AsyncMock(return_value=mock_downloaded)
        
        # Acquire papers
        downloaded = await self.workflow.acquire_papers(papers)
        
        self.assertEqual(len(downloaded), 2)
        self.assertIn("Paper 1", downloaded)
        
        # Check state was updated
        self.assertIn("Paper 1", self.workflow.state['downloaded_papers'])
    
    @patch.object(LiteratureReviewWorkflow, 'indexer')
    @patch.object(LiteratureReviewWorkflow, 'vector_engine')
    async def test_index_papers(self, mock_vector_engine, mock_indexer):
        """Test paper indexing."""
        # Mock indexing
        mock_indexer.index_documents = AsyncMock(return_value={'successful': 5})
        
        # Mock documents in search engine
        self.workflow.search_engine.documents = {
            'doc1': {'content': 'test', 'metadata': {}, 'processed': {}},
            'doc2': {'content': 'test2', 'metadata': {}, 'processed': {}}
        }
        
        # Mock vector engine add_document
        mock_vector_engine.add_document = Mock(return_value=True)
        
        # Index papers
        stats = await self.workflow.index_papers()
        
        self.assertEqual(stats['vector_indexed'], 2)
        self.assertEqual(len(self.workflow.state['indexed_papers']), 2)
    
    async def test_search_literature(self):
        """Test literature search."""
        # Mock vector search results
        mock_results = [
            Mock(
                metadata={'title': 'Result 1', 'authors': ['Author 1'], 'year': '2023'},
                score=0.95,
                highlights=['highlight 1'],
                doc_id='doc1'
            )
        ]
        
        self.workflow.vector_engine.search = Mock(return_value=mock_results)
        
        # Search
        results = await self.workflow.search_literature("test query", n_results=5)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Result 1')
        self.assertEqual(results[0]['score'], 0.95)
    
    async def test_find_research_gaps(self):
        """Test research gap analysis."""
        # Mock search results
        mock_papers = [
            {'methods': ['CNN', 'LSTM'], 'datasets': ['MNIST'], 'year': '2023'},
            {'methods': ['CNN'], 'datasets': ['CIFAR'], 'year': '2024'},
            {'methods': ['Transformer'], 'datasets': ['MNIST'], 'year': '2024'}
        ]
        
        self.workflow.search_literature = AsyncMock(return_value=mock_papers)
        
        # Find gaps
        gaps = await self.workflow.find_research_gaps("test topic")
        
        self.assertEqual(gaps['papers_analyzed'], 3)
        self.assertIn('CNN', gaps['methods_used'])
        self.assertIn('MNIST', gaps['datasets_used'])
        self.assertIsInstance(gaps['temporal_trend'], dict)
    
    async def test_generate_review_summary(self):
        """Test review summary generation."""
        # Mock papers
        mock_papers = [
            {
                'title': 'Paper 1',
                'authors': ['Author 1'],
                'year': '2023',
                'methods': ['CNN']
            },
            {
                'title': 'Paper 2',
                'authors': ['Author 2'],
                'year': '2024',
                'methods': ['LSTM']
            }
        ]
        
        # Mock gaps
        mock_gaps = {
            'methods_used': ['CNN', 'LSTM'],
            'datasets_used': ['Dataset1'],
            'potential_unused_methods': ['Transformer'],
            'temporal_trend': {'increasing': True, 'recent_papers': 2}
        }
        
        self.workflow.search_literature = AsyncMock(return_value=mock_papers)
        self.workflow.find_research_gaps = AsyncMock(return_value=mock_gaps)
        
        # Generate summary
        summary = await self.workflow.generate_review_summary("test topic")
        
        self.assertIsInstance(summary, str)
        self.assertIn("test topic", summary)
        self.assertIn("Paper 1", summary)
        self.assertIn("CNN", summary)
        self.assertIn("active area", summary)  # Due to increasing trend
    
    @patch.object(LiteratureReviewWorkflow, 'discover_papers')
    @patch.object(LiteratureReviewWorkflow, 'acquire_papers')
    @patch.object(LiteratureReviewWorkflow, 'index_papers')
    @patch.object(LiteratureReviewWorkflow, 'generate_review_summary')
    @patch.object(LiteratureReviewWorkflow, 'find_research_gaps')
    async def test_full_review_pipeline(self, mock_gaps, mock_summary, 
                                      mock_index, mock_acquire, mock_discover):
        """Test complete review pipeline."""
        # Mock all steps
        mock_discover.return_value = [
            PaperMetadata(title="Paper 1", source="pubmed")
        ]
        mock_acquire.return_value = {"Paper 1": Path("paper1.pdf")}
        mock_index.return_value = {"vector_indexed": 1}
        mock_summary.return_value = "Test summary"
        mock_gaps.return_value = {"methods_used": ["CNN"]}
        
        # Run pipeline
        results = await self.workflow.full_review_pipeline(
            topic="test topic",
            sources=['pubmed'],
            max_papers=10
        )
        
        self.assertEqual(results['topic'], "test topic")
        self.assertEqual(results['papers_found'], 1)
        self.assertEqual(results['papers_downloaded'], 1)
        self.assertEqual(results['papers_indexed'], 1)
        self.assertIn('summary_path', results)
        self.assertIn('research_gaps', results)
    
    def test_extract_snippet(self):
        """Test snippet extraction."""
        content = "This is a long text about machine learning and neural networks. " * 10
        query = "machine learning"
        
        snippet = self.workflow.vector_engine._extract_snippet(content, query)
        
        self.assertIn("machine learning", snippet)
        self.assertIn("...", snippet)  # Should have ellipsis
        self.assertLess(len(snippet), len(content))
    
    async def test_skip_existing_papers(self):
        """Test skipping already downloaded papers."""
        # Add paper to state
        self.workflow.state['downloaded_papers']['Existing Paper'] = str(Path("existing.pdf"))
        
        papers = [
            PaperMetadata(title="Existing Paper"),
            PaperMetadata(title="New Paper")
        ]
        
        # Mock download for new paper only
        self.workflow.acquisition.batch_download = AsyncMock(return_value={
            "New Paper": Path("new.pdf")
        })
        
        # Acquire papers
        downloaded = await self.workflow.acquire_papers(papers, skip_existing=True)
        
        # Should only download new paper
        self.assertEqual(len(downloaded), 1)
        self.assertIn("New Paper", downloaded)
    
    def test_metadata_file_creation(self):
        """Test metadata file creation during discovery."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test_metadata():
            # Mock search
            self.workflow.acquisition.search = AsyncMock(return_value=[
                PaperMetadata(title="Test Paper", year="2024")
            ])
            
            # Discover papers
            await self.workflow.discover_papers("test query")
            
            # Check metadata file was created
            metadata_files = list(self.workflow.metadata_dir.glob("search_*.json"))
            self.assertGreater(len(metadata_files), 0)
            
            # Verify content
            with open(metadata_files[0]) as f:
                data = json.load(f)
                self.assertEqual(data['query'], "test query")
                self.assertEqual(len(data['papers']), 1)
        
        loop.run_until_complete(test_metadata())
        loop.close()


if __name__ == "__main__":
    unittest.main()

# EOF