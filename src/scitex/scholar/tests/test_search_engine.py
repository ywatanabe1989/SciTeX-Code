#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:15:00 (ywatanabe)"
# File: tests/test_search_engine.py

"""
Test module for search engine functionality.

This module tests the core search capabilities including
keyword search, phrase matching, and document ranking.
"""

import unittest
import sys
sys.path.insert(0, './src')


class TestSearchEngine(unittest.TestCase):
    """Test suite for search engine functionality."""
    
    def test_search_engine_import(self):
        """Test that search engine module can be imported."""
        try:
            from scitex_scholar.search_engine import SearchEngine
        except ImportError:
            self.fail("Failed to import SearchEngine from scitex_scholar.search_engine")

    def test_search_engine_initialization(self):
        """Test SearchEngine can be initialized."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        self.assertIsNotNone(engine)
        self.assertTrue(hasattr(engine, 'search'))
        self.assertTrue(hasattr(engine, 'add_document'))

    def test_add_document(self):
        """Test adding documents to search index."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        
        doc_id = "doc1"
        content = "This is a sample scientific document about machine learning."
        
        result = engine.add_document(doc_id, content)
        self.assertTrue(result)
        self.assertIn(doc_id, engine.documents)

    def test_keyword_search(self):
        """Test basic keyword search functionality."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        
        # Add test documents
        engine.add_document("doc1", "Machine learning algorithms for data analysis")
        engine.add_document("doc2", "Deep learning neural networks in AI research")
        engine.add_document("doc3", "Statistical methods in scientific computing")
        
        # Search for keywords
        results = engine.search("machine learning")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertTrue(any(result['doc_id'] == "doc1" for result in results))

    def test_phrase_search(self):
        """Test exact phrase search functionality."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        
        # Add test documents
        engine.add_document("doc1", "machine learning algorithms")
        engine.add_document("doc2", "learning machine algorithms")
        
        # Search for exact phrase
        results = engine.search("machine learning", exact_phrase=True)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['doc_id'], "doc1")

    def test_search_scoring(self):
        """Test search result scoring and ranking."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        
        # Add documents with different relevance
        engine.add_document("doc1", "machine learning machine learning algorithms")
        engine.add_document("doc2", "machine learning in science")
        engine.add_document("doc3", "algorithms and methods")
        
        results = engine.search("machine learning")
        
        self.assertGreaterEqual(len(results), 2)
        # Check that results are scored
        self.assertTrue(all('score' in result for result in results))
        # Check that more relevant document scores higher
        self.assertGreaterEqual(results[0]['score'], results[1]['score'])

    def test_search_with_filters(self):
        """Test search with document type filters."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        
        # Add documents with metadata
        engine.add_document("doc1", "machine learning paper", metadata={"type": "paper"})
        engine.add_document("doc2", "machine learning book", metadata={"type": "book"})
        
        # Search with filter
        results = engine.search("machine learning", filters={"type": "paper"})
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['doc_id'], "doc1")

    def test_empty_search(self):
        """Test handling of empty search queries."""
        from scitex_scholar.search_engine import SearchEngine
        
        engine = SearchEngine()
        engine.add_document("doc1", "sample content")
        
        # Test empty query
        results = engine.search("")
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
        
        # Test None query
        results = engine.search(None)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()

# EOF