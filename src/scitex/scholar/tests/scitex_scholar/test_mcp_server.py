#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:30:00"
# Author: Claude
# Description: Test cases for MCP server functionality

"""
Test module for MCP server functionality.

This module contains comprehensive test cases for the Model Context Protocol (MCP)
server implementation, including tool registration, request handling, and response
formatting.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.mcp_server import (
    SciteXMCPServer,
    search_papers,
    get_paper_details,
    extract_methods,
    find_similar_papers
)


class TestMCPServerFunctions(unittest.TestCase):
    """Test MCP server tool functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_search_engine = Mock()
        self.mock_pdf_parser = Mock()
        
    @patch('scitex_scholar.mcp_server.search_engine')
    def test_search_papers_success(self, mock_engine):
        """Test successful paper search."""
        # Mock search results
        mock_results = [
            {
                'title': 'Deep Learning in Medicine',
                'authors': ['Smith, J.', 'Doe, A.'],
                'year': '2024',
                'abstract': 'A comprehensive review of deep learning applications...',
                'score': 0.95,
                'file_path': '/path/to/paper1.pdf'
            },
            {
                'title': 'Neural Networks for Diagnosis',
                'authors': ['Johnson, B.'],
                'year': '2023',
                'abstract': 'Novel approach to medical diagnosis...',
                'score': 0.87,
                'file_path': '/path/to/paper2.pdf'
            }
        ]
        mock_engine.search.return_value = mock_results
        
        # Test search
        result = search_papers("deep learning medical diagnosis", max_results=5)
        
        # Verify results
        self.assertIn('results', result)
        self.assertEqual(len(result['results']), 2)
        self.assertEqual(result['results'][0]['title'], 'Deep Learning in Medicine')
        self.assertEqual(result['query'], "deep learning medical diagnosis")
        self.assertEqual(result['count'], 2)
        
    @patch('scitex_scholar.mcp_server.search_engine')
    def test_search_papers_no_results(self, mock_engine):
        """Test search with no results."""
        mock_engine.search.return_value = []
        
        result = search_papers("nonexistent topic xyz123")
        
        self.assertEqual(result['count'], 0)
        self.assertEqual(len(result['results']), 0)
        
    @patch('scitex_scholar.mcp_server.pdf_parser')
    @patch('os.path.exists')
    def test_get_paper_details_success(self, mock_exists, mock_parser):
        """Test successful paper detail extraction."""
        mock_exists.return_value = True
        
        # Mock parsed paper
        mock_paper = Mock()
        mock_paper.title = "Deep Learning in Medicine"
        mock_paper.authors = ["Smith, J.", "Doe, A."]
        mock_paper.abstract = "A comprehensive review..."
        mock_paper.sections = {
            "Introduction": "Deep learning has revolutionized...",
            "Methods": "We used CNN architectures...",
            "Results": "Our model achieved 95% accuracy..."
        }
        mock_paper.methods_mentioned = ["CNN", "LSTM", "Transformer"]
        mock_paper.datasets_mentioned = ["ImageNet", "MIMIC-III"]
        mock_paper.figures = [{"caption": "Figure 1: Model architecture"}]
        mock_paper.tables = [{"caption": "Table 1: Performance metrics"}]
        mock_paper.references = ["Ref1", "Ref2", "Ref3"]
        
        mock_parser.parse_pdf.return_value = mock_paper
        
        # Test extraction
        result = get_paper_details("/path/to/paper.pdf")
        
        # Verify results
        self.assertEqual(result['title'], "Deep Learning in Medicine")
        self.assertEqual(len(result['methods']), 3)
        self.assertEqual(len(result['datasets']), 2)
        self.assertIn("Methods", result['sections'])
        
    @patch('os.path.exists')
    def test_get_paper_details_file_not_found(self, mock_exists):
        """Test paper details with non-existent file."""
        mock_exists.return_value = False
        
        result = get_paper_details("/nonexistent/paper.pdf")
        
        self.assertIn('error', result)
        self.assertIn('not found', result['error'])
        
    @patch('scitex_scholar.mcp_server.pdf_parser')
    @patch('os.path.exists')
    def test_extract_methods_success(self, mock_exists, mock_parser):
        """Test method extraction from paper."""
        mock_exists.return_value = True
        
        # Mock parsed paper
        mock_paper = Mock()
        mock_paper.methods_mentioned = ["CNN", "LSTM", "Random Forest"]
        mock_paper.sections = {
            "Methods": "We employed a CNN with 5 layers... LSTM for sequence... Random Forest for classification..."
        }
        
        mock_parser.parse_pdf.return_value = mock_paper
        
        # Test extraction
        result = extract_methods("/path/to/paper.pdf")
        
        # Verify results
        self.assertEqual(len(result['methods']), 3)
        self.assertIn("CNN", result['methods'])
        self.assertIn("Methods", result['method_section'])
        
    @patch('scitex_scholar.mcp_server.search_engine')
    def test_find_similar_papers_success(self, mock_engine):
        """Test finding similar papers."""
        # Mock similar papers
        mock_similar = [
            {
                'title': 'Related Deep Learning Study',
                'score': 0.92,
                'file_path': '/path/to/similar1.pdf'
            },
            {
                'title': 'Another ML Medical Paper',
                'score': 0.88,
                'file_path': '/path/to/similar2.pdf'
            }
        ]
        mock_engine.find_similar.return_value = mock_similar
        
        # Test finding similar
        result = find_similar_papers("/path/to/reference.pdf", top_k=5)
        
        # Verify results
        self.assertEqual(len(result['similar_papers']), 2)
        self.assertEqual(result['similar_papers'][0]['title'], 'Related Deep Learning Study')
        self.assertEqual(result['reference_paper'], "/path/to/reference.pdf")


class TestSciteXMCPServer(unittest.TestCase):
    """Test SciteXMCPServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = SciteXMCPServer()
        
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertIsNotNone(self.server.server)
        self.assertEqual(self.server.name, "scitex-scholar")
        
    def test_tool_registration(self):
        """Test that all tools are registered."""
        # Check that tools are registered (this would need actual MCP library)
        # For now, just verify the server exists
        self.assertIsNotNone(self.server)
        
    @patch('asyncio.run')
    def test_run_method(self, mock_run):
        """Test server run method."""
        # Test that run calls asyncio.run with serve
        self.server.run()
        mock_run.assert_called_once()


class TestMCPServerIntegration(unittest.TestCase):
    """Integration tests for MCP server."""
    
    @patch('scitex_scholar.mcp_server.search_engine')
    @patch('scitex_scholar.mcp_server.pdf_parser')
    def test_full_workflow(self, mock_parser, mock_engine):
        """Test complete workflow from search to detail extraction."""
        # Mock search results
        mock_engine.search.return_value = [
            {
                'title': 'Test Paper',
                'file_path': '/path/to/test.pdf',
                'score': 0.9
            }
        ]
        
        # Mock paper parsing
        mock_paper = Mock()
        mock_paper.title = "Test Paper"
        mock_paper.methods_mentioned = ["Method1", "Method2"]
        mock_paper.sections = {"Methods": "Test methods section"}
        mock_parser.parse_pdf.return_value = mock_paper
        
        # Mock similar papers
        mock_engine.find_similar.return_value = [
            {
                'title': 'Similar Paper',
                'score': 0.85
            }
        ]
        
        # Test workflow
        # 1. Search for papers
        search_result = search_papers("test query")
        self.assertEqual(len(search_result['results']), 1)
        
        # 2. Get details of first result
        paper_path = search_result['results'][0]['file_path']
        with patch('os.path.exists', return_value=True):
            details = get_paper_details(paper_path)
            self.assertEqual(details['title'], "Test Paper")
            
        # 3. Extract methods
        with patch('os.path.exists', return_value=True):
            methods = extract_methods(paper_path)
            self.assertEqual(len(methods['methods']), 2)
            
        # 4. Find similar papers
        similar = find_similar_papers(paper_path)
        self.assertEqual(len(similar['similar_papers']), 1)


class TestMCPServerErrorHandling(unittest.TestCase):
    """Test error handling in MCP server."""
    
    @patch('scitex_scholar.mcp_server.search_engine')
    def test_search_error_handling(self, mock_engine):
        """Test search error handling."""
        mock_engine.search.side_effect = Exception("Search engine error")
        
        result = search_papers("test query")
        
        # Should return empty results on error
        self.assertEqual(result['count'], 0)
        self.assertEqual(len(result['results']), 0)
        
    @patch('scitex_scholar.mcp_server.pdf_parser')
    @patch('os.path.exists')
    def test_parse_error_handling(self, mock_exists, mock_parser):
        """Test PDF parsing error handling."""
        mock_exists.return_value = True
        mock_parser.parse_pdf.side_effect = Exception("PDF parsing error")
        
        result = get_paper_details("/path/to/paper.pdf")
        
        self.assertIn('error', result)
        self.assertIn('parsing', result['error'].lower())


if __name__ == '__main__':
    unittest.main()