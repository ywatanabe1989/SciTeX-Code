#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:15:00 (ywatanabe)"
# File: tests/test_text_processor.py

"""
Test module for text processing functionality.

This module tests the core text processing capabilities including
text cleaning, normalization, and preprocessing for scientific documents.
"""

import unittest
import sys
sys.path.insert(0, './src')


class TestTextProcessor(unittest.TestCase):
    """Test suite for text processor functionality."""
    
    def test_text_processor_import(self):
        """Test that text processor module can be imported."""
        try:
            from scitex_scholar.text_processor import TextProcessor
        except ImportError:
            self.fail("Failed to import TextProcessor from scitex_scholar.text_processor")

    def test_text_processor_initialization(self):
        """Test TextProcessor can be initialized with default settings."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        self.assertIsNotNone(processor)
        self.assertTrue(hasattr(processor, 'clean_text'))
        self.assertTrue(hasattr(processor, 'normalize_text'))

    def test_clean_text_basic(self):
        """Test basic text cleaning functionality."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        # Test basic cleaning
        input_text = "  Hello   World!  \n\n  "
        expected = "Hello World!"
        result = processor.clean_text(input_text)
        self.assertEqual(result, expected)

    def test_clean_text_scientific_content(self):
        """Test cleaning of scientific text with special characters."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        # Test scientific content cleaning
        input_text = "The equation $E = mc^2$ shows the relationship."
        result = processor.clean_text(input_text)
        self.assertIn("E = mc^2", result)
        self.assertGreater(len(result), 0)

    def test_normalize_text(self):
        """Test text normalization for consistent processing."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        # Test case normalization
        input_text = "UPPERCASE and lowercase TEXT"
        result = processor.normalize_text(input_text)
        self.assertTrue(result.islower())
        self.assertIn("uppercase", result)
        self.assertIn("lowercase", result)

    def test_extract_keywords(self):
        """Test keyword extraction from scientific text."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        input_text = "Machine learning algorithms are used in data science research."
        keywords = processor.extract_keywords(input_text)
        
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        self.assertTrue(any("machine" in kw.lower() for kw in keywords))
        self.assertTrue(any("learning" in kw.lower() for kw in keywords))

    def test_process_scientific_document(self):
        """Test processing a complete scientific document."""
        from scitex_scholar.text_processor import TextProcessor
        
        processor = TextProcessor()
        
        document = """
        Abstract
        
        This paper presents a novel approach to machine learning in scientific research.
        The methodology involves advanced algorithms for data analysis.
        
        Introduction
        
        Recent advances in artificial intelligence have shown promising results.
        """
        
        result = processor.process_document(document)
        
        self.assertIsInstance(result, dict)
        self.assertIn('cleaned_text', result)
        self.assertIn('keywords', result)
        self.assertIn('sections', result)
        self.assertGreater(len(result['cleaned_text']), 0)


if __name__ == "__main__":
    unittest.main()

# EOF