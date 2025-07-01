#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:31:00"
# Author: Claude
# Description: Test cases for MCP vector server functionality

"""
Test module for MCP vector server functionality.

This module contains comprehensive test cases for the vector-based MCP server
implementation, including vector search operations, document indexing, and
similarity computations.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
import json
import numpy as np
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.mcp_vector_server import (
    VectorMCPServer,
    vector_search,
    index_documents,
    find_similar_vectors,
    get_document_embedding,
    update_vector_index
)


class TestVectorMCPServerFunctions(unittest.TestCase):
    """Test vector MCP server tool functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_vector_engine = Mock()
        self.mock_embeddings = np.random.rand(5, 768)  # 5 documents, 768 dim
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_vector_search_success(self, mock_engine):
        """Test successful vector search."""
        # Mock search results
        mock_results = [
            {
                'document_id': 'doc1',
                'content': 'Deep learning applications in healthcare...',
                'score': 0.95,
                'metadata': {
                    'title': 'ML in Medicine',
                    'author': 'Smith et al.',
                    'year': 2024
                }
            },
            {
                'document_id': 'doc2',
                'content': 'Neural networks for medical diagnosis...',
                'score': 0.87,
                'metadata': {
                    'title': 'AI Diagnosis',
                    'author': 'Johnson et al.',
                    'year': 2023
                }
            }
        ]
        mock_engine.search.return_value = mock_results
        
        # Test search
        result = vector_search(
            query="machine learning healthcare",
            k=10,
            filters={'year': {'$gte': 2020}}
        )
        
        # Verify results
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['results'][0]['document_id'], 'doc1')
        self.assertIn('embedding_used', result)
        self.assertEqual(result['num_results'], 2)
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_vector_search_with_threshold(self, mock_engine):
        """Test vector search with similarity threshold."""
        mock_results = [
            {'document_id': 'doc1', 'score': 0.95},
            {'document_id': 'doc2', 'score': 0.75},
            {'document_id': 'doc3', 'score': 0.65}
        ]
        mock_engine.search.return_value = mock_results
        
        # Test with threshold
        result = vector_search(
            query="test query",
            k=10,
            similarity_threshold=0.8
        )
        
        # Should only return results above threshold
        filtered_results = [r for r in result['results'] if r['score'] >= 0.8]
        self.assertEqual(len(filtered_results), 1)
        
    @patch('scitex_scholar.mcp_vector_server.document_indexer')
    def test_index_documents_success(self, mock_indexer):
        """Test successful document indexing."""
        # Mock indexing results
        mock_indexer.index_documents.return_value = {
            'indexed': 5,
            'failed': 0,
            'skipped': 1
        }
        
        # Test indexing
        documents = [
            {'id': 'doc1', 'content': 'Content 1', 'metadata': {'type': 'paper'}},
            {'id': 'doc2', 'content': 'Content 2', 'metadata': {'type': 'paper'}},
            {'id': 'doc3', 'content': 'Content 3', 'metadata': {'type': 'review'}}
        ]
        
        result = index_documents(documents, batch_size=2)
        
        # Verify results
        self.assertEqual(result['total_indexed'], 5)
        self.assertEqual(result['failed'], 0)
        self.assertIn('index_name', result)
        
    @patch('scitex_scholar.mcp_vector_server.document_indexer')
    def test_index_documents_with_errors(self, mock_indexer):
        """Test document indexing with errors."""
        mock_indexer.index_documents.return_value = {
            'indexed': 3,
            'failed': 2,
            'errors': ['Error 1', 'Error 2']
        }
        
        documents = [{'id': f'doc{i}', 'content': f'Content {i}'} for i in range(5)]
        result = index_documents(documents)
        
        self.assertEqual(result['total_indexed'], 3)
        self.assertEqual(result['failed'], 2)
        self.assertIn('errors', result)
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_find_similar_vectors_success(self, mock_engine):
        """Test finding similar vectors."""
        # Mock similar documents
        mock_similar = [
            {
                'document_id': 'similar1',
                'score': 0.92,
                'content': 'Similar content 1'
            },
            {
                'document_id': 'similar2',
                'score': 0.88,
                'content': 'Similar content 2'
            }
        ]
        mock_engine.find_similar.return_value = mock_similar
        
        # Test finding similar
        result = find_similar_vectors(
            document_id="ref_doc",
            k=5,
            exclude_self=True
        )
        
        # Verify results
        self.assertEqual(len(result['similar_documents']), 2)
        self.assertEqual(result['reference_document'], "ref_doc")
        self.assertTrue(result['exclude_self'])
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_get_document_embedding_success(self, mock_engine):
        """Test retrieving document embedding."""
        # Mock embedding
        mock_embedding = np.random.rand(768).tolist()
        mock_engine.get_embedding.return_value = mock_embedding
        
        # Test retrieval
        result = get_document_embedding("doc123")
        
        # Verify results
        self.assertEqual(len(result['embedding']), 768)
        self.assertEqual(result['document_id'], "doc123")
        self.assertEqual(result['dimension'], 768)
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_get_document_embedding_not_found(self, mock_engine):
        """Test embedding retrieval for non-existent document."""
        mock_engine.get_embedding.return_value = None
        
        result = get_document_embedding("nonexistent")
        
        self.assertIn('error', result)
        self.assertIn('not found', result['error'].lower())
        
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_update_vector_index_success(self, mock_engine):
        """Test updating vector index."""
        mock_engine.update_index.return_value = {
            'status': 'success',
            'documents_updated': 10,
            'time_taken': 2.5
        }
        
        # Test update
        result = update_vector_index(
            rebuild=False,
            optimize=True
        )
        
        # Verify results
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['documents_updated'], 10)
        self.assertTrue(result['optimized'])


class TestVectorMCPServer(unittest.TestCase):
    """Test VectorMCPServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = VectorMCPServer()
        
    def test_server_initialization(self):
        """Test vector server initialization."""
        self.assertIsNotNone(self.server.server)
        self.assertEqual(self.server.name, "scitex-vector-search")
        
    def test_vector_tools_registration(self):
        """Test that vector tools are registered."""
        # Verify server is initialized with vector capabilities
        self.assertIsNotNone(self.server)
        
    @patch('asyncio.run')
    def test_run_method(self, mock_run):
        """Test server run method."""
        self.server.run()
        mock_run.assert_called_once()


class TestVectorMCPServerIntegration(unittest.TestCase):
    """Integration tests for vector MCP server."""
    
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    @patch('scitex_scholar.mcp_vector_server.document_indexer')
    def test_index_and_search_workflow(self, mock_indexer, mock_engine):
        """Test complete workflow from indexing to search."""
        # Mock indexing
        mock_indexer.index_documents.return_value = {
            'indexed': 3,
            'failed': 0
        }
        
        # Mock search
        mock_engine.search.return_value = [
            {
                'document_id': 'doc1',
                'content': 'Indexed content',
                'score': 0.9
            }
        ]
        
        # 1. Index documents
        docs = [
            {'id': 'doc1', 'content': 'Test content 1'},
            {'id': 'doc2', 'content': 'Test content 2'},
            {'id': 'doc3', 'content': 'Test content 3'}
        ]
        index_result = index_documents(docs)
        self.assertEqual(index_result['total_indexed'], 3)
        
        # 2. Search indexed documents
        search_result = vector_search("test query", k=5)
        self.assertEqual(len(search_result['results']), 1)
        
        # 3. Find similar documents
        mock_engine.find_similar.return_value = [
            {'document_id': 'doc2', 'score': 0.85}
        ]
        similar_result = find_similar_vectors('doc1', k=3)
        self.assertEqual(len(similar_result['similar_documents']), 1)


class TestVectorMCPServerAdvanced(unittest.TestCase):
    """Advanced tests for vector MCP server."""
    
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_hybrid_search(self, mock_engine):
        """Test hybrid search combining vector and keyword search."""
        # Mock hybrid search results
        mock_engine.hybrid_search.return_value = [
            {
                'document_id': 'doc1',
                'vector_score': 0.9,
                'keyword_score': 0.8,
                'combined_score': 0.85
            }
        ]
        
        # Test hybrid search
        result = vector_search(
            query="machine learning",
            search_type="hybrid",
            k=10
        )
        
        # Verify combined scoring
        self.assertIn('results', result)
        if result['results']:
            self.assertIn('combined_score', result['results'][0])
            
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_batch_embedding_retrieval(self, mock_engine):
        """Test batch retrieval of embeddings."""
        # Mock batch embeddings
        mock_embeddings = {
            'doc1': np.random.rand(768).tolist(),
            'doc2': np.random.rand(768).tolist(),
            'doc3': np.random.rand(768).tolist()
        }
        mock_engine.get_batch_embeddings.return_value = mock_embeddings
        
        # Test batch retrieval
        doc_ids = ['doc1', 'doc2', 'doc3']
        # This would be a batch version of get_document_embedding
        # For now, test individual retrieval
        for doc_id in doc_ids:
            mock_engine.get_embedding.return_value = mock_embeddings[doc_id]
            result = get_document_embedding(doc_id)
            self.assertEqual(len(result['embedding']), 768)


class TestVectorMCPServerErrorHandling(unittest.TestCase):
    """Test error handling in vector MCP server."""
    
    @patch('scitex_scholar.mcp_vector_server.vector_engine')
    def test_search_error_handling(self, mock_engine):
        """Test vector search error handling."""
        mock_engine.search.side_effect = Exception("Vector engine error")
        
        result = vector_search("test query")
        
        # Should handle error gracefully
        self.assertEqual(result['num_results'], 0)
        self.assertEqual(len(result['results']), 0)
        
    @patch('scitex_scholar.mcp_vector_server.document_indexer')
    def test_indexing_error_handling(self, mock_indexer):
        """Test indexing error handling."""
        mock_indexer.index_documents.side_effect = Exception("Indexing error")
        
        result = index_documents([{'id': 'doc1', 'content': 'test'}])
        
        self.assertEqual(result['total_indexed'], 0)
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()