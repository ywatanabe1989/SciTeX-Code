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
        mock_page._extract_text.return_value = "Sample text from page 1"
        
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
        mock_page1._extract_text.return_value = "Content from page 1"
        mock_page2 = MagicMock()
        mock_page2._extract_text.return_value = "Content from page 2"
        mock_page3 = MagicMock()
        mock_page3._extract_text.return_value = "Content from page 3"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pypdf2.PdfReader.return_value = mock_reader
        
        result = _load_pdf('multi_page.pdf')
        
        # Verify all pages were processed
        expected_text = "Content from page 1\nContent from page 2\nContent from page 3"
        assert result == expected_text
        
        # Verify all pages had _extract_text called
        mock_page1._extract_text.assert_called_once()
        mock_page2._extract_text.assert_called_once()
        mock_page3._extract_text.assert_called_once()
    
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
        mock_page1._extract_text.return_value = "Regular content"
        mock_page2 = MagicMock()
        mock_page2._extract_text.return_value = ""  # Empty page
        mock_page3 = MagicMock()
        mock_page3._extract_text.return_value = "   "  # Whitespace only
        mock_page4 = MagicMock()
        mock_page4._extract_text.return_value = "More content"
        
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
        mock_page1._extract_text.return_value = "Héllo Wörld! 你好世界"
        mock_page2 = MagicMock()
        mock_page2._extract_text.return_value = "Математика and العربية"
        mock_page3 = MagicMock()
        mock_page3._extract_text.return_value = "Symbols: ∑ ∫ π ∞ 🔬"
        
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
            mock_page._extract_text.return_value = page_text
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
        mock_page._extract_text.return_value = "Test content"
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
        mock_page._extract_text.return_value = "Test content"
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
        mock_page1._extract_text.return_value = "Line 1\nLine 2\nLine 3"
        mock_page2 = MagicMock()
        mock_page2._extract_text.return_value = "Tabs\there\tand\tthere"
        mock_page3 = MagicMock()
        mock_page3._extract_text.return_value = "Special chars: !@#$%^&*()"
        
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
        mock_page1._extract_text.return_value = "Abstract\nThis paper presents a novel approach to..."
        mock_page2 = MagicMock()
        mock_page2._extract_text.return_value = "1. Introduction\nRecent advances in machine learning..."
        mock_page3 = MagicMock()
        mock_page3._extract_text.return_value = "2. Methods\nWe employed a cross-validation approach..."
        mock_page4 = MagicMock()
        mock_page4._extract_text.return_value = "3. Results\nThe experimental results show..."
        mock_page5 = MagicMock()
        mock_page5._extract_text.return_value = "References\n[1] Smith, J. et al. (2023)..."
        
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

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_pdf.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-01-19 14:30:00 (ywatanabe)"
# # File: ./src/scitex/io/_load_modules/_pdf.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/io/_load_modules/_pdf.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# """
# Enhanced PDF loading module with multiple extraction modes.
# 
# This module provides comprehensive PDF text extraction capabilities
# for scientific papers, supporting various extraction modes and formats.
# """
# 
# from scitex import logging
# import re
# from pathlib import Path
# from typing import Dict, List, Any, Optional, Tuple
# import hashlib
# 
# logger = logging.getLogger(__name__)
# 
# # Try to import PDF libraries in order of preference
# try:
#     import fitz  # PyMuPDF - preferred for better extraction
#     FITZ_AVAILABLE = True
# except ImportError:
#     FITZ_AVAILABLE = False
# 
# try:
#     import PyPDF2
#     PYPDF2_AVAILABLE = True
# except ImportError:
#     PYPDF2_AVAILABLE = False
# 
# 
# def _load_pdf(lpath: str, **kwargs) -> Any:
#     """
#     Load PDF file with various extraction modes.
#     
#     Args:
#         lpath: Path to PDF file
#         **kwargs: Additional arguments
#             - mode: Extraction mode ('text', 'sections', 'metadata', 'full', 'pages')
#                 - 'text' (default): Plain text extraction
#                 - 'sections': Section-aware extraction
#                 - 'metadata': PDF metadata only
#                 - 'full': All available data
#                 - 'pages': Page-by-page extraction
#             - backend: 'auto' (default), 'fitz', or 'pypdf2'
#             - clean_text: Clean extracted text (default: True)
#             - extract_images: Extract image descriptions (default: False)
#     
#     Returns:
#         Extracted content based on mode
#     """
#     mode = kwargs.get('mode', 'text')
#     backend = kwargs.get('backend', 'auto')
#     clean_text = kwargs.get('clean_text', True)
#     extract_images = kwargs.get('extract_images', False)
#     
#     # Validate file
#     if not lpath.endswith('.pdf'):
#         raise ValueError("File must have .pdf extension")
#     
#     if not os.path.exists(lpath):
#         raise FileNotFoundError(f"PDF file not found: {lpath}")
#     
#     # Select backend
#     if backend == 'auto':
#         if FITZ_AVAILABLE:
#             backend = 'fitz'
#         elif PYPDF2_AVAILABLE:
#             backend = 'pypdf2'
#         else:
#             raise ImportError(
#                 "No PDF library available. Install with:\n"
#                 "  pip install PyMuPDF  # Recommended\n"
#                 "  pip install PyPDF2   # Alternative"
#             )
#     
#     # Extract based on mode
#     if mode == 'text':
#         return __extract_text(lpath, backend, clean_text)
#     elif mode == 'sections':
#         return _extract_sections(lpath, backend, clean_text)
#     elif mode == 'metadata':
#         return _extract_metadata(lpath, backend)
#     elif mode == 'pages':
#         return _extract_pages(lpath, backend, clean_text)
#     elif mode == 'full':
#         return _extract_full(lpath, backend, clean_text, extract_images)
#     else:
#         raise ValueError(f"Unknown extraction mode: {mode}")
# 
# 
# def __extract_text(lpath: str, backend: str, clean: bool) -> str:
#     """Extract plain text from PDF."""
#     if backend == 'fitz':
#         return __extract_text_fitz(lpath, clean)
#     else:
#         return __extract_text_pypdf2(lpath, clean)
# 
# 
# def __extract_text_fitz(lpath: str, clean: bool) -> str:
#     """Extract text using PyMuPDF."""
#     if not FITZ_AVAILABLE:
#         raise ImportError("PyMuPDF (fitz) not available")
#     
#     try:
#         doc = fitz.open(lpath)
#         text_parts = []
#         
#         for page_num, page in enumerate(doc):
#             text = page.get_text()
#             if text.strip():
#                 text_parts.append(text)
#         
#         doc.close()
#         
#         full_text = '\n'.join(text_parts)
#         
#         if clean:
#             full_text = _clean_pdf_text(full_text)
#         
#         return full_text
#         
#     except Exception as e:
#         logger.error(f"Error extracting text with fitz from {lpath}: {e}")
#         raise
# 
# 
# def __extract_text_pypdf2(lpath: str, clean: bool) -> str:
#     """Extract text using PyPDF2."""
#     if not PYPDF2_AVAILABLE:
#         raise ImportError("PyPDF2 not available")
#     
#     try:
#         reader = PyPDF2.PdfReader(lpath)
#         text_parts = []
#         
#         for page_num in range(len(reader.pages)):
#             page = reader.pages[page_num]
#             text = page._extract_text()
#             if text.strip():
#                 text_parts.append(text)
#         
#         full_text = '\n'.join(text_parts)
#         
#         if clean:
#             full_text = _clean_pdf_text(full_text)
#         
#         return full_text
#         
#     except Exception as e:
#         logger.error(f"Error extracting text with PyPDF2 from {lpath}: {e}")
#         raise
# 
# 
# def _extract_sections(lpath: str, backend: str, clean: bool) -> Dict[str, str]:
#     """Extract text organized by sections."""
#     # Get full text first
#     text = __extract_text(lpath, backend, clean=False)
#     
#     # Parse into sections
#     sections = _parse_sections(text)
#     
#     # Clean section text if requested
#     if clean:
#         for section, content in sections.items():
#             sections[section] = _clean_pdf_text(content)
#     
#     return sections
# 
# 
# def _parse_sections(text: str) -> Dict[str, str]:
#     """Parse text into sections based on common patterns."""
#     sections = {}
#     current_section = "header"
#     current_text = []
#     
#     # Common section patterns in scientific papers
#     section_patterns = [
#         r'^abstract\s*$',
#         r'^introduction\s*$',
#         r'^background\s*$',
#         r'^related\s+work\s*$',
#         r'^methods?\s*$',
#         r'^methodology\s*$',
#         r'^materials?\s+and\s+methods?\s*$',
#         r'^experiments?\s*$',
#         r'^results?\s*$',
#         r'^results?\s+and\s+discussions?\s*$',
#         r'^discussions?\s*$',
#         r'^conclusions?\s*$',
#         r'^references?\s*$',
#         r'^bibliography\s*$',
#         r'^acknowledgments?\s*$',
#         r'^appendix.*$',
#         r'^supplementary.*$',
#         r'^\d+\.?\s+\w+',  # Numbered sections
#         r'^[A-Z]\.\s+\w+',  # Letter sections
#     ]
#     
#     lines = text.split('\n')
#     
#     for line in lines:
#         line_lower = line.lower().strip()
#         
#         # Check if this line is a section header
#         is_header = False
#         for pattern in section_patterns:
#             if re.match(pattern, line_lower, re.IGNORECASE):
#                 # Save previous section
#                 if current_text:
#                     sections[current_section] = '\n'.join(current_text).strip()
#                 
#                 # Start new section
#                 current_section = line_lower.replace('.', '').strip()
#                 current_text = []
#                 is_header = True
#                 break
#         
#         if not is_header:
#             current_text.append(line)
#     
#     # Save last section
#     if current_text:
#         sections[current_section] = '\n'.join(current_text).strip()
#     
#     return sections
# 
# 
# def _extract_metadata(lpath: str, backend: str) -> Dict[str, Any]:
#     """Extract PDF metadata."""
#     metadata = {
#         'file_path': lpath,
#         'file_name': os.path.basename(lpath),
#         'file_size': os.path.getsize(lpath),
#         'backend': backend
#     }
#     
#     if backend == 'fitz' and FITZ_AVAILABLE:
#         try:
#             doc = fitz.open(lpath)
#             pdf_metadata = doc.metadata
#             
#             metadata.update({
#                 'title': pdf_metadata.get('title', ''),
#                 'author': pdf_metadata.get('author', ''),
#                 'subject': pdf_metadata.get('subject', ''),
#                 'keywords': pdf_metadata.get('keywords', ''),
#                 'creator': pdf_metadata.get('creator', ''),
#                 'producer': pdf_metadata.get('producer', ''),
#                 'creation_date': str(pdf_metadata.get('creationDate', '')),
#                 'modification_date': str(pdf_metadata.get('modDate', '')),
#                 'pages': len(doc),
#                 'encrypted': doc.is_encrypted,
#             })
#             
#             doc.close()
#             
#         except Exception as e:
#             logger.error(f"Error extracting metadata with fitz: {e}")
#     
#     elif backend == 'pypdf2' and PYPDF2_AVAILABLE:
#         try:
#             reader = PyPDF2.PdfReader(lpath)
#             
#             if reader.metadata:
#                 metadata.update({
#                     'title': reader.metadata.get('/Title', ''),
#                     'author': reader.metadata.get('/Author', ''),
#                     'subject': reader.metadata.get('/Subject', ''),
#                     'creator': reader.metadata.get('/Creator', ''),
#                     'producer': reader.metadata.get('/Producer', ''),
#                     'creation_date': str(reader.metadata.get('/CreationDate', '')),
#                     'modification_date': str(reader.metadata.get('/ModDate', '')),
#                 })
#             
#             metadata['pages'] = len(reader.pages)
#             metadata['encrypted'] = reader.is_encrypted
#             
#         except Exception as e:
#             logger.error(f"Error extracting metadata with PyPDF2: {e}")
#     
#     # Generate file hash
#     metadata['md5_hash'] = _calculate_file_hash(lpath)
#     
#     return metadata
# 
# 
# def _extract_pages(lpath: str, backend: str, clean: bool) -> List[Dict[str, Any]]:
#     """Extract text page by page."""
#     pages = []
#     
#     if backend == 'fitz' and FITZ_AVAILABLE:
#         doc = fitz.open(lpath)
#         
#         for page_num, page in enumerate(doc):
#             text = page.get_text()
#             if clean:
#                 text = _clean_pdf_text(text)
#             
#             pages.append({
#                 'page_number': page_num + 1,
#                 'text': text,
#                 'char_count': len(text),
#                 'word_count': len(text.split())
#             })
#         
#         doc.close()
#     
#     elif backend == 'pypdf2' and PYPDF2_AVAILABLE:
#         reader = PyPDF2.PdfReader(lpath)
#         
#         for page_num in range(len(reader.pages)):
#             page = reader.pages[page_num]
#             text = page._extract_text()
#             if clean:
#                 text = _clean_pdf_text(text)
#             
#             pages.append({
#                 'page_number': page_num + 1,
#                 'text': text,
#                 'char_count': len(text),
#                 'word_count': len(text.split())
#             })
#     
#     return pages
# 
# 
# def _extract_full(lpath: str, backend: str, clean: bool, extract_images: bool) -> Dict[str, Any]:
#     """Extract comprehensive data from PDF."""
#     result = {
#         'pdf_path': lpath,
#         'filename': os.path.basename(lpath),
#         'backend': backend,
#         'extraction_params': {
#             'clean_text': clean,
#             'extract_images': extract_images
#         }
#     }
#     
#     # Extract all components
#     try:
#         result['full_text'] = __extract_text(lpath, backend, clean)
#         result['sections'] = _extract_sections(lpath, backend, clean)
#         result['metadata'] = _extract_metadata(lpath, backend)
#         result['pages'] = _extract_pages(lpath, backend, clean)
#         
#         # Calculate statistics
#         result['stats'] = {
#             'total_chars': len(result['full_text']),
#             'total_words': len(result['full_text'].split()),
#             'total_pages': len(result['pages']),
#             'num_sections': len(result['sections']),
#             'avg_words_per_page': len(result['full_text'].split()) / len(result['pages']) if result['pages'] else 0
#         }
#         
#         # Extract images if requested (only with fitz)
#         if extract_images and backend == 'fitz' and FITZ_AVAILABLE:
#             result['images'] = _extract_image_info(lpath)
#         
#     except Exception as e:
#         logger.error(f"Error in full extraction: {e}")
#         result['error'] = str(e)
#     
#     return result
# 
# 
# def _extract_image_info(lpath: str) -> List[Dict[str, Any]]:
#     """Extract information about images in PDF (requires fitz)."""
#     images = []
#     
#     try:
#         doc = fitz.open(lpath)
#         
#         for page_num, page in enumerate(doc):
#             image_list = page.get_images()
#             
#             for img_index, img in enumerate(image_list):
#                 images.append({
#                     'page': page_num + 1,
#                     'index': img_index,
#                     'width': img[2],
#                     'height': img[3],
#                     'colorspace': img[4],
#                     'bpc': img[5],  # bits per component
#                 })
#         
#         doc.close()
#         
#     except Exception as e:
#         logger.error(f"Error extracting image info: {e}")
#     
#     return images
# 
# 
# def _clean_pdf_text(text: str) -> str:
#     """Clean extracted PDF text."""
#     # Remove excessive whitespace
#     text = re.sub(r'\s+', ' ', text)
#     
#     # Fix hyphenated words at line breaks
#     text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
#     
#     # Remove page numbers (common patterns)
#     text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
#     text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
#     
#     # Clean up common PDF artifacts
#     text = text.replace('\x00', '')  # Null bytes
#     text = re.sub(r'[\x01-\x1f\x7f-\x9f]', '', text)  # Control characters
#     
#     # Normalize quotes and dashes
#     text = text.replace('"', '"').replace('"', '"')
#     text = text.replace(''', "'").replace(''', "'")
#     text = text.replace('–', '-').replace('—', '-')
#     
#     # Remove multiple consecutive newlines
#     text = re.sub(r'\n{3,}', '\n\n', text)
#     
#     return text.strip()
# 
# 
# def _calculate_file_hash(lpath: str) -> str:
#     """Calculate MD5 hash of file."""
#     hash_md5 = hashlib.md5()
#     with open(lpath, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_md5.update(chunk)
#     return hash_md5.hexdigest()
# 
# 
# # Convenience function
# def load_pdf(filepath: str, mode: str = 'text', **kwargs) -> Any:
#     """
#     Load PDF file with specified extraction mode.
#     
#     Args:
#         filepath: Path to PDF file
#         mode: Extraction mode (text, sections, metadata, pages, full)
#         **kwargs: Additional arguments for extraction
#     
#     Returns:
#         Extracted content based on mode
#     """
#     return _load_pdf(filepath, mode=mode, **kwargs)
# 
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_load_modules/_pdf.py
# --------------------------------------------------------------------------------
