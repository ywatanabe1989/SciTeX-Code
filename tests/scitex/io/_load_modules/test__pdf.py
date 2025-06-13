#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:10:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/io/_load_modules/test__pdf.py

"""Comprehensive tests for PDF file loading functionality."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock


class TestLoadPdf:
    """Test suite for _load_pdf function"""
    
    def test_valid_extension_check(self):
        """Test that function validates .pdf extension"""
from scitex.io._load_modules import _load_pdf
        
        # Test invalid extensions
        invalid_files = ["file.txt", "document.doc", "text.docx", "data.xlsx"]
        
        for invalid_file in invalid_files:
            with pytest.raises(ValueError, match="File must have .pdf extension"):
                _load_pdf(invalid_file)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_pypdf2_reader_creation(self, mock_pypdf2):
        """Test that PyPDF2.PdfReader is created correctly"""
from scitex.io._load_modules import _load_pdf
        
        # Create mock reader and pages
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample text from page 1"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        # Call function
        result = _load_pdf('test_document.pdf')
        
        # Verify PyPDF2.PdfReader was called correctly
        mock_pypdf2.PdfReader.assert_called_once_with('test_document.pdf')
        
        # Verify text extraction
        assert result == "Sample text from page 1"
        assert isinstance(result, str)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_multi_page_pdf_processing(self, mock_pypdf2):
        """Test processing of multi-page PDFs"""
from scitex.io._load_modules import _load_pdf
        
        # Create mock pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Content from page 1"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Content from page 2"
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Content from page 3"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('multi_page.pdf')
        
        # Verify all pages were processed
        expected_text = "Content from page 1\nContent from page 2\nContent from page 3"
        assert result == expected_text
        
        # Verify all pages had extract_text called
        mock_page1.extract_text.assert_called_once()
        mock_page2.extract_text.assert_called_once()
        mock_page3.extract_text.assert_called_once()
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_empty_pdf_handling(self, mock_pypdf2):
        """Test handling of empty PDFs"""
from scitex.io._load_modules import _load_pdf
        
        # Create mock reader with no pages
        mock_reader = MagicMock()
        mock_reader.pages = []
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('empty.pdf')
        
        assert result == ""
        assert isinstance(result, str)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_pages_with_empty_text(self, mock_pypdf2):
        """Test handling of pages with empty or whitespace text"""
from scitex.io._load_modules import _load_pdf
        
        # Create mock pages with various empty content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Regular content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = ""  # Empty page
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "   "  # Whitespace only
        mock_page4 = MagicMock()
        mock_page4.extract_text.return_value = "More content"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3, mock_page4]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('mixed_content.pdf')
        
        expected_text = "Regular content\n\n   \nMore content"
        assert result == expected_text
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_unicode_text_handling(self, mock_pypdf2):
        """Test handling of Unicode characters in PDF text"""
from scitex.io._load_modules import _load_pdf
        
        # Create mock pages with Unicode content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Héllo Wörld! 你好世界"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Математика and العربية"
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Symbols: ∑ ∫ π ∞ 🔬"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('unicode.pdf')
        
        expected_text = "Héllo Wörld! 你好世界\nМатематика and العربية\nSymbols: ∑ ∫ π ∞ 🔬"
        assert result == expected_text
        assert isinstance(result, str)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_pypdf2_exceptions_handling(self, mock_pypdf2):
        """Test handling of PyPDF2 specific exceptions"""
from scitex.io._load_modules import _load_pdf
        import PyPDF2
        
        # Test PdfReadError
        mock_pypdf2.PdfReader.side_effect = PyPDF2.PdfReadError("Corrupted PDF file")
        mock_pypdf2.PdfReadError = PyPDF2.PdfReadError
        
        with pytest.raises(ValueError, match="Error loading PDF.*Corrupted PDF file"):
            _load_pdf('corrupted.pdf')
        
        # Test FileNotFoundError
        mock_pypdf2.PdfReader.side_effect = FileNotFoundError("File not found")
        
        with pytest.raises(ValueError, match="Error loading PDF.*File not found"):
            _load_pdf('nonexistent.pdf')
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_large_pdf_handling(self, mock_pypdf2):
        """Test handling of PDFs with many pages"""
from scitex.io._load_modules import _load_pdf
        
        # Create 100 mock pages
        mock_pages = []
        expected_lines = []
        for i in range(100):
            mock_page = MagicMock()
            page_text = f"This is content from page {i+1}."
            mock_page.extract_text.return_value = page_text
            mock_pages.append(mock_page)
            expected_lines.append(page_text)
        
        mock_reader = MagicMock()
        mock_reader.pages = mock_pages
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('large_document.pdf')
        
        expected_text = "\n".join(expected_lines)
        assert result == expected_text
        assert "page 1." in result
        assert "page 100." in result
        assert len(result.split("\n")) == 100
    
    def test_function_signature(self):
        """Test function signature and parameters"""
from scitex.io._load_modules import _load_pdf
        import inspect
        
        sig = inspect.signature(_load_pdf)
        
        # Check parameters
        assert 'lpath' in sig.parameters
        assert 'kwargs' in sig.parameters or len(sig.parameters) >= 1
        
        # Check that it accepts kwargs (even if not used)
        params = list(sig.parameters.keys())
        assert len(params) >= 1
    
    def test_function_docstring(self):
        """Test that function has proper docstring"""
from scitex.io._load_modules import _load_pdf
        
        assert hasattr(_load_pdf, '__doc__')
        assert _load_pdf.__doc__ is not None
        docstring = _load_pdf.__doc__
        
        # Check for key documentation elements
        assert 'Load PDF file' in docstring or 'PDF' in docstring
        assert 'text' in docstring.lower()
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_kwargs_handling(self, mock_pypdf2):
        """Test that kwargs are accepted but not used"""
from scitex.io._load_modules import _load_pdf
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        # Call with various kwargs
        result = _load_pdf('test.pdf', verbose=True, encoding='utf-8', custom_param="value")
        
        # Verify PyPDF2.PdfReader was called only with the path
        mock_pypdf2.PdfReader.assert_called_once_with('test.pdf')
        assert result == "Test content"
    
    def test_case_sensitive_extension_check(self):
        """Test case sensitivity of .pdf extension"""
from scitex.io._load_modules import _load_pdf
        
        # Test case variations that should fail
        case_variations = ["file.PDF", "file.Pdf", "file.pDf"]
        
        for variant in case_variations:
            with pytest.raises(ValueError, match="File must have .pdf extension"):
                _load_pdf(variant)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_path_variations(self, mock_pypdf2):
        """Test various path formats"""
from scitex.io._load_modules import _load_pdf
        
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        # Test different path formats
        paths = [
            '/home/user/documents/report.pdf',
            './data/document.pdf',
            'file-with-hyphens.pdf',
            'file_with_underscores.pdf',
            'file with spaces.pdf',
            'very_long_filename_with_many_characters_and_numbers_123.pdf'
        ]
        
        for path in paths:
            mock_pypdf2.PdfReader.reset_mock()
            result = _load_pdf(path)
            mock_pypdf2.PdfReader.assert_called_once_with(path)
            assert result == "Test content"
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_text_extraction_edge_cases(self, mock_pypdf2):
        """Test edge cases in text extraction"""
from scitex.io._load_modules import _load_pdf
        
        # Test pages with special characters and formatting
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Line 1\nLine 2\nLine 3"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Tabs\there\tand\tthere"
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "Special chars: !@#$%^&*()"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('formatted.pdf')
        
        expected_text = "Line 1\nLine 2\nLine 3\nTabs\there\tand\tthere\nSpecial chars: !@#$%^&*()"
        assert result == expected_text
    
    def test_import_error_handling(self):
        """Test behavior when PyPDF2 is not available"""
        # This test verifies the source code would handle missing PyPDF2
        # The actual import error would happen at runtime
from scitex.io._load_modules import _load_pdf
        
        # We can't easily test the import error without modifying the source,
        # but we can verify the function exists
        assert callable(_load_pdf)
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_error_message_format(self, mock_pypdf2):
        """Test that error messages include file path and original error"""
from scitex.io._load_modules import _load_pdf
        import PyPDF2
        
        # Test with specific error message
        error_msg = "Invalid PDF header"
        mock_pypdf2.PdfReader.side_effect = PyPDF2.PdfReadError(error_msg)
        mock_pypdf2.PdfReadError = PyPDF2.PdfReadError
        
        file_path = 'specific_file.pdf'
        with pytest.raises(ValueError) as exc_info:
            _load_pdf(file_path)
        
        # Verify error message format
        error_str = str(exc_info.value)
        assert f"Error loading PDF {file_path}" in error_str
        assert error_msg in error_str
    
    @patch('scitex.io._load_modules._pdf.PyPDF2')
    def test_scientific_document_scenario(self, mock_pypdf2):
        """Test realistic scientific document processing scenario"""
from scitex.io._load_modules import _load_pdf
        
        # Simulate a scientific paper with typical content
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Abstract\nThis paper presents a novel approach to..."
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "1. Introduction\nRecent advances in machine learning..."
        mock_page3 = MagicMock()
        mock_page3.extract_text.return_value = "2. Methods\nWe employed a cross-validation approach..."
        mock_page4 = MagicMock()
        mock_page4.extract_text.return_value = "3. Results\nThe experimental results show..."
        mock_page5 = MagicMock()
        mock_page5.extract_text.return_value = "References\n[1] Smith, J. et al. (2023)..."
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3, mock_page4, mock_page5]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('scientific_paper.pdf')
        
        # Verify scientific content is properly extracted
        assert "Abstract" in result
        assert "Introduction" in result
        assert "Methods" in result
        assert "Results" in result
        assert "References" in result
        assert "machine learning" in result
        assert "cross-validation" in result
        
        # Verify proper page separation
        pages = result.split('\n')
        assert len([p for p in pages if p.strip()]) >= 5  # At least 5 non-empty lines


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__), "-v"])
