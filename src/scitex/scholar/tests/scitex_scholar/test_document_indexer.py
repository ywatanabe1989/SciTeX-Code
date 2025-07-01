#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:50:00 (ywatanabe)"
# File: tests/scitex_scholar/test_document_indexer.py

"""
Test module for document indexer functionality.

This module tests the document discovery, parsing, and indexing
capabilities for building searchable document collections.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
sys.path.insert(0, './src')

from scitex_scholar.document_indexer import DocumentIndexer
from scitex_scholar.search_engine import SearchEngine
from scitex_scholar.scientific_pdf_parser import ScientificPaper


class TestDocumentIndexer(unittest.TestCase):
    """Test suite for document indexer functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_docs_dir = Path(cls.temp_dir) / "test_docs"
        cls.test_docs_dir.mkdir()
        
        # Create test files
        (cls.test_docs_dir / "test1.pdf").write_text("PDF content 1")
        (cls.test_docs_dir / "test2.pdf").write_text("PDF content 2")
        (cls.test_docs_dir / "test.txt").write_text("Text content")
        (cls.test_docs_dir / "test.md").write_text("# Markdown content")
        
        # Create subdirectory with more files
        sub_dir = cls.test_docs_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "test3.pdf").write_text("PDF content 3")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up for each test."""
        self.search_engine = SearchEngine()
        self.indexer = DocumentIndexer(self.search_engine)
    
    def test_document_indexer_initialization(self):
        """Test DocumentIndexer can be initialized."""
        self.assertIsNotNone(self.indexer)
        self.assertIsNotNone(self.indexer.search_engine)
        self.assertIsNotNone(self.indexer.pdf_parser)
        self.assertIsInstance(self.indexer.indexed_files, set)
        self.assertIsInstance(self.indexer.index_stats, dict)
    
    def test_get_file_id(self):
        """Test file ID generation."""
        file_path = Path("/home/user/doc.pdf")
        file_id = self.indexer._get_file_id(file_path)
        
        self.assertIsInstance(file_id, str)
        self.assertEqual(file_id, str(file_path.absolute()))
    
    async def test_index_documents_discovery(self):
        """Test document discovery in directories."""
        # Test file discovery
        stats = await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.pdf', '*.txt', '*.md']
        )
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_files'], 5)  # 3 PDFs + 1 txt + 1 md
    
    @patch.object(DocumentIndexer, '_process_pdf')
    async def test_index_documents_pdf_processing(self, mock_process_pdf):
        """Test PDF processing during indexing."""
        mock_process_pdf.return_value = True
        
        stats = await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.pdf']
        )
        
        # Should process 3 PDF files
        self.assertEqual(mock_process_pdf.call_count, 3)
        self.assertEqual(stats['successful'], 3)
    
    def test_process_text_file(self):
        """Test text file processing."""
        text_file = self.test_docs_dir / "test.txt"
        result = self.indexer._process_text_file(text_file)
        
        self.assertTrue(result)
        
        # Check document was added to search engine
        doc_id = self.indexer._get_file_id(text_file)
        self.assertIn(doc_id, self.search_engine.documents)
        
        # Check metadata
        doc = self.search_engine.documents[doc_id]
        self.assertEqual(doc['metadata']['file_type'], 'txt')
        self.assertEqual(doc['content'], "Text content")
    
    @patch('scitex_scholar.scientific_pdf_parser.ScientificPDFParser.parse_pdf')
    def test_process_pdf_success(self, mock_parse_pdf):
        """Test successful PDF processing."""
        # Mock parsed paper
        mock_paper = ScientificPaper(
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
            sections={},
            keywords=["test"],
            references=[],
            figures=[],
            tables=[],
            equations=[],
            metadata={'file_path': 'test.pdf'},
            citations_in_text=[],
            methods_mentioned=[],
            datasets_mentioned=[],
            metrics_reported={}
        )
        mock_parse_pdf.return_value = mock_paper
        
        # Mock to_search_document
        self.indexer.pdf_parser.to_search_document = Mock(return_value={
            'content': 'Test content',
            'metadata': {'title': 'Test Paper'}
        })
        
        pdf_file = self.test_docs_dir / "test1.pdf"
        result = self.indexer._process_pdf(pdf_file)
        
        self.assertTrue(result)
        
        # Check document was added
        doc_id = self.indexer._get_file_id(pdf_file)
        self.assertIn(doc_id, self.search_engine.documents)
        self.assertIn(doc_id, self.indexer.indexed_files)
    
    @patch('scitex_scholar.scientific_pdf_parser.ScientificPDFParser.parse_pdf')
    def test_process_pdf_failure(self, mock_parse_pdf):
        """Test PDF processing failure handling."""
        mock_parse_pdf.side_effect = Exception("Parse error")
        
        pdf_file = self.test_docs_dir / "test1.pdf"
        result = self.indexer._process_pdf(pdf_file)
        
        self.assertFalse(result)
    
    async def test_force_reindex(self):
        """Test force reindexing of already indexed files."""
        # First indexing
        stats1 = await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.txt']
        )
        
        # Second indexing without force - should skip
        stats2 = await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.txt'],
            force_reindex=False
        )
        
        self.assertEqual(stats2['skipped'], 1)
        
        # Third indexing with force - should reprocess
        stats3 = await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.txt'],
            force_reindex=True
        )
        
        self.assertEqual(stats3['skipped'], 0)
    
    async def test_parse_document(self):
        """Test single document parsing."""
        text_file = self.test_docs_dir / "test.txt"
        content, metadata = await self.indexer.parse_document(text_file)
        
        self.assertEqual(content, "Text content")
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['file_type'], 'txt')
        self.assertEqual(metadata['file_name'], 'test.txt')
    
    @patch('scitex_scholar.scientific_pdf_parser.ScientificPDFParser.parse_pdf')
    async def test_parse_pdf_document(self, mock_parse_pdf):
        """Test PDF document parsing."""
        mock_paper = ScientificPaper(
            title="Test PDF",
            authors=["Author"],
            abstract="Abstract",
            sections={},
            keywords=[],
            references=[],
            figures=[],
            tables=[],
            equations=[],
            metadata={},
            citations_in_text=[],
            methods_mentioned=[],
            datasets_mentioned=[],
            metrics_reported={}
        )
        mock_parse_pdf.return_value = mock_paper
        
        self.indexer.pdf_parser.to_search_document = Mock(return_value={
            'content': 'PDF content',
            'metadata': {'title': 'Test PDF'}
        })
        
        pdf_file = self.test_docs_dir / "test1.pdf"
        content, metadata = await self.indexer.parse_document(pdf_file)
        
        self.assertEqual(content, 'PDF content')
        self.assertEqual(metadata['title'], 'Test PDF')
    
    async def test_save_and_load_index(self):
        """Test saving and loading index state."""
        # Index some files
        await self.indexer.index_documents(
            paths=[self.test_docs_dir],
            patterns=['*.txt']
        )
        
        # Save index
        cache_path = Path(self.temp_dir) / "test_index.json"
        await self.indexer.save_index(cache_path)
        
        self.assertTrue(cache_path.exists())
        
        # Create new indexer and load
        new_indexer = DocumentIndexer(SearchEngine())
        await new_indexer.load_index(cache_path)
        
        # Check state was restored
        self.assertEqual(len(new_indexer.indexed_files), len(self.indexer.indexed_files))
        self.assertEqual(new_indexer.index_stats['total_files'], self.indexer.index_stats['total_files'])
    
    def test_concurrent_processing(self):
        """Test concurrent file processing."""
        # This is tested implicitly in index_documents with ThreadPoolExecutor
        # Here we just verify the indexer can handle multiple files
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test_concurrent():
            stats = await self.indexer.index_documents(
                paths=[self.test_docs_dir],
                patterns=['*.pdf', '*.txt', '*.md']
            )
            
            # Should process all files
            self.assertGreater(stats['total_files'], 0)
            self.assertGreaterEqual(stats['successful'] + stats['failed'] + stats['skipped'], 
                                   stats['total_files'])
        
        loop.run_until_complete(test_concurrent())
        loop.close()
    
    def test_process_file_unsupported_type(self):
        """Test handling of unsupported file types."""
        # Create unsupported file
        unsupported_file = self.test_docs_dir / "test.xyz"
        unsupported_file.write_text("Unsupported content")
        
        result = self.indexer._process_file(unsupported_file)
        
        self.assertFalse(result)
    
    def test_index_stats_tracking(self):
        """Test index statistics tracking."""
        # Initial stats
        self.assertEqual(self.indexer.index_stats['total_files'], 0)
        self.assertEqual(self.indexer.index_stats['successful'], 0)
        self.assertEqual(self.indexer.index_stats['failed'], 0)
        self.assertEqual(self.indexer.index_stats['skipped'], 0)
        
        # Process a file
        text_file = self.test_docs_dir / "test.txt"
        self.indexer._process_file(text_file)
        
        # Stats should be updated (in real async context)
        # This is handled in index_documents method


if __name__ == "__main__":
    unittest.main()

# EOF