#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:35:00 (ywatanabe)"
# File: tests/scitex_scholar/test_vector_search_engine.py

"""
Test module for vector search engine functionality.

This module tests the vector-based semantic search capabilities including
embeddings, similarity search, and database operations.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
sys.path.insert(0, './src')

from scitex_scholar.vector_search_engine import VectorSearchEngine, SearchResult


class TestVectorSearchEngine(unittest.TestCase):
    """Test suite for vector search engine functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.temp_dir) / "test_vector_db"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Set up for each test."""
        self.engine = VectorSearchEngine(
            model_name="sentence-transformers/all-MiniLM-L6-v2",  # Smaller model for tests
            chunk_size=256,
            chunk_overlap=64,
            db_path=str(self.db_path)
        )
    
    def test_vector_search_engine_initialization(self):
        """Test VectorSearchEngine can be initialized."""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.chunk_size, 256)
        self.assertEqual(self.engine.chunk_overlap, 64)
        self.assertIsNotNone(self.engine.encoder)
        self.assertIsNotNone(self.engine.chroma_client)
    
    def test_add_document(self):
        """Test adding documents with embeddings."""
        doc_id = "test_doc_1"
        content = "This is a test document about machine learning algorithms."
        metadata = {
            'title': 'Test Document',
            'authors': ['John Doe'],
            'year': '2024'
        }
        
        result = self.engine.add_document(doc_id, content, metadata)
        self.assertTrue(result)
        
        # Verify document was added
        stats = self.engine.get_statistics()
        self.assertGreater(stats['total_documents'], 0)
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        # Add test documents
        docs = [
            {
                'id': 'doc1',
                'content': 'Deep learning neural networks for image classification',
                'metadata': {'title': 'DL for Images', 'year': '2023'}
            },
            {
                'id': 'doc2',
                'content': 'Statistical methods for data analysis in research',
                'metadata': {'title': 'Stats Methods', 'year': '2022'}
            },
            {
                'id': 'doc3',
                'content': 'Convolutional networks for computer vision tasks',
                'metadata': {'title': 'CNN Vision', 'year': '2024'}
            }
        ]
        
        for doc in docs:
            self.engine.add_document(doc['id'], doc['content'], doc['metadata'])
        
        # Test semantic search
        results = self.engine.search(
            query="neural networks for visual recognition",
            search_type="semantic",
            n_results=2
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)
        
        # Check result structure
        if results:
            result = results[0]
            self.assertIsInstance(result, SearchResult)
            self.assertIsNotNone(result.doc_id)
            self.assertIsNotNone(result.score)
            self.assertIsNotNone(result.similarity_score)
    
    def test_chunk_search(self):
        """Test chunk-based search."""
        # Add a longer document
        long_content = """
        Introduction: This paper presents a novel approach to machine learning.
        
        Methods: We used convolutional neural networks with attention mechanisms.
        The accuracy achieved was 95.2% on the test dataset.
        
        Results: Our model outperformed baseline methods significantly.
        
        Conclusion: The proposed method shows promise for practical applications.
        """
        
        self.engine.add_document(
            doc_id="long_doc",
            content=long_content,
            metadata={'title': 'Long Research Paper'}
        )
        
        # Search for specific information
        results = self.engine.search(
            query="accuracy percentage",
            search_type="chunk",
            n_results=1
        )
        
        self.assertGreater(len(results), 0)
        if results:
            self.assertIn("95.2%", results[0].chunk_text or results[0].content)
    
    def test_hybrid_search(self):
        """Test hybrid search combining semantic and keyword matching."""
        # Add documents
        self.engine.add_document(
            "doc_hybrid_1",
            "Phase amplitude coupling in epilepsy seizure detection",
            {'title': 'PAC Epilepsy', 'keywords': ['pac', 'epilepsy']}
        )
        
        self.engine.add_document(
            "doc_hybrid_2",
            "Neural synchronization patterns during sleep stages",
            {'title': 'Sleep Sync', 'keywords': ['sleep', 'synchronization']}
        )
        
        # Hybrid search
        results = self.engine.search(
            query="phase coupling seizure",
            search_type="hybrid",
            n_results=2
        )
        
        self.assertGreater(len(results), 0)
        # First result should be the PAC epilepsy paper
        self.assertIn("phase", results[0].content.lower())
    
    def test_find_similar_documents(self):
        """Test finding similar documents."""
        # Add documents
        doc_ids = []
        for i in range(3):
            doc_id = f"similar_test_{i}"
            content = f"Machine learning approach number {i} for classification"
            self.engine.add_document(doc_id, content, {'index': i})
            doc_ids.append(doc_id)
        
        # Find similar to first document
        similar = self.engine.find_similar_documents(doc_ids[0], n_results=2)
        
        self.assertIsInstance(similar, list)
        # Should find the other documents as similar
        self.assertGreater(len(similar), 0)
    
    def test_query_expansion(self):
        """Test query expansion functionality."""
        original_query = "ml nn cv"
        expanded = self.engine._expand_query(original_query)
        
        self.assertIn("machine learning", expanded.lower())
        self.assertIn("neural network", expanded.lower())
        
    def test_metadata_filtering(self):
        """Test search with metadata filters."""
        # Add documents with different years
        for year in ['2021', '2022', '2023']:
            self.engine.add_document(
                f"doc_year_{year}",
                f"Research paper published in {year}",
                {'year': year, 'title': f'Paper {year}'}
            )
        
        # Search with year filter
        results = self.engine.search(
            query="research paper",
            filters={'year': '2023'},
            n_results=10
        )
        
        # Should only return 2023 paper
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].metadata['year'], '2023')
    
    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.engine.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_documents', stats)
        self.assertIn('total_chunks', stats)
        self.assertIn('embedding_model', stats)
        self.assertIn('chunk_size', stats)
    
    def test_empty_search(self):
        """Test handling of empty search queries."""
        # Add a document first
        self.engine.add_document("test", "test content", {})
        
        # Test with empty query
        results = self.engine.search("", n_results=5)
        self.assertEqual(len(results), 0)
    
    def test_cache_operations(self):
        """Test cache clearing functionality."""
        # Add some documents to populate cache
        for i in range(5):
            self.engine.add_document(
                f"cache_test_{i}",
                f"Document content {i}",
                {'index': i}
            )
        
        # Clear cache
        self.engine.clear_cache()
        
        # Cache should be cleared but documents still searchable
        results = self.engine.search("document content", n_results=5)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()

# EOF