#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-19 14:30:00 (ywatanabe)"
# File: ./src/scitex/io/_load_modules/_pdf.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Enhanced PDF loading module with multiple extraction modes.

This module provides comprehensive PDF text extraction capabilities
for scientific papers, supporting various extraction modes and formats.
"""

from scitex import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib

logger = logging.getLogger(__name__)

# Try to import PDF libraries in order of preference
try:
    import fitz  # PyMuPDF - preferred for better extraction
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


def _load_pdf(lpath: str, **kwargs) -> Any:
    """
    Load PDF file with various extraction modes.
    
    Args:
        lpath: Path to PDF file
        **kwargs: Additional arguments
            - mode: Extraction mode ('text', 'sections', 'metadata', 'full', 'pages')
                - 'text' (default): Plain text extraction
                - 'sections': Section-aware extraction
                - 'metadata': PDF metadata only
                - 'full': All available data
                - 'pages': Page-by-page extraction
            - backend: 'auto' (default), 'fitz', or 'pypdf2'
            - clean_text: Clean extracted text (default: True)
            - extract_images: Extract image descriptions (default: False)
    
    Returns:
        Extracted content based on mode
    """
    mode = kwargs.get('mode', 'text')
    backend = kwargs.get('backend', 'auto')
    clean_text = kwargs.get('clean_text', True)
    extract_images = kwargs.get('extract_images', False)
    
    # Validate file
    if not lpath.endswith('.pdf'):
        raise ValueError("File must have .pdf extension")
    
    if not os.path.exists(lpath):
        raise FileNotFoundError(f"PDF file not found: {lpath}")
    
    # Select backend
    if backend == 'auto':
        if FITZ_AVAILABLE:
            backend = 'fitz'
        elif PYPDF2_AVAILABLE:
            backend = 'pypdf2'
        else:
            raise ImportError(
                "No PDF library available. Install with:\n"
                "  pip install PyMuPDF  # Recommended\n"
                "  pip install PyPDF2   # Alternative"
            )
    
    # Extract based on mode
    if mode == 'text':
        return __extract_text(lpath, backend, clean_text)
    elif mode == 'sections':
        return _extract_sections(lpath, backend, clean_text)
    elif mode == 'metadata':
        return _extract_metadata(lpath, backend)
    elif mode == 'pages':
        return _extract_pages(lpath, backend, clean_text)
    elif mode == 'full':
        return _extract_full(lpath, backend, clean_text, extract_images)
    else:
        raise ValueError(f"Unknown extraction mode: {mode}")


def __extract_text(lpath: str, backend: str, clean: bool) -> str:
    """Extract plain text from PDF."""
    if backend == 'fitz':
        return __extract_text_fitz(lpath, clean)
    else:
        return __extract_text_pypdf2(lpath, clean)


def __extract_text_fitz(lpath: str, clean: bool) -> str:
    """Extract text using PyMuPDF."""
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) not available")
    
    try:
        doc = fitz.open(lpath)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        full_text = '\n'.join(text_parts)
        
        if clean:
            full_text = _clean_pdf_text(full_text)
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text with fitz from {lpath}: {e}")
        raise


def __extract_text_pypdf2(lpath: str, clean: bool) -> str:
    """Extract text using PyPDF2."""
    if not PYPDF2_AVAILABLE:
        raise ImportError("PyPDF2 not available")
    
    try:
        reader = PyPDF2.PdfReader(lpath)
        text_parts = []
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page._extract_text()
            if text.strip():
                text_parts.append(text)
        
        full_text = '\n'.join(text_parts)
        
        if clean:
            full_text = _clean_pdf_text(full_text)
        
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2 from {lpath}: {e}")
        raise


def _extract_sections(lpath: str, backend: str, clean: bool) -> Dict[str, str]:
    """Extract text organized by sections."""
    # Get full text first
    text = __extract_text(lpath, backend, clean=False)
    
    # Parse into sections
    sections = _parse_sections(text)
    
    # Clean section text if requested
    if clean:
        for section, content in sections.items():
            sections[section] = _clean_pdf_text(content)
    
    return sections


def _parse_sections(text: str) -> Dict[str, str]:
    """Parse text into sections based on common patterns."""
    sections = {}
    current_section = "header"
    current_text = []
    
    # Common section patterns in scientific papers
    section_patterns = [
        r'^abstract\s*$',
        r'^introduction\s*$',
        r'^background\s*$',
        r'^related\s+work\s*$',
        r'^methods?\s*$',
        r'^methodology\s*$',
        r'^materials?\s+and\s+methods?\s*$',
        r'^experiments?\s*$',
        r'^results?\s*$',
        r'^results?\s+and\s+discussions?\s*$',
        r'^discussions?\s*$',
        r'^conclusions?\s*$',
        r'^references?\s*$',
        r'^bibliography\s*$',
        r'^acknowledgments?\s*$',
        r'^appendix.*$',
        r'^supplementary.*$',
        r'^\d+\.?\s+\w+',  # Numbered sections
        r'^[A-Z]\.\s+\w+',  # Letter sections
    ]
    
    lines = text.split('\n')
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line is a section header
        is_header = False
        for pattern in section_patterns:
            if re.match(pattern, line_lower, re.IGNORECASE):
                # Save previous section
                if current_text:
                    sections[current_section] = '\n'.join(current_text).strip()
                
                # Start new section
                current_section = line_lower.replace('.', '').strip()
                current_text = []
                is_header = True
                break
        
        if not is_header:
            current_text.append(line)
    
    # Save last section
    if current_text:
        sections[current_section] = '\n'.join(current_text).strip()
    
    return sections


def _extract_metadata(lpath: str, backend: str) -> Dict[str, Any]:
    """Extract PDF metadata."""
    metadata = {
        'file_path': lpath,
        'file_name': os.path.basename(lpath),
        'file_size': os.path.getsize(lpath),
        'backend': backend
    }
    
    if backend == 'fitz' and FITZ_AVAILABLE:
        try:
            doc = fitz.open(lpath)
            pdf_metadata = doc.metadata
            
            metadata.update({
                'title': pdf_metadata.get('title', ''),
                'author': pdf_metadata.get('author', ''),
                'subject': pdf_metadata.get('subject', ''),
                'keywords': pdf_metadata.get('keywords', ''),
                'creator': pdf_metadata.get('creator', ''),
                'producer': pdf_metadata.get('producer', ''),
                'creation_date': str(pdf_metadata.get('creationDate', '')),
                'modification_date': str(pdf_metadata.get('modDate', '')),
                'pages': len(doc),
                'encrypted': doc.is_encrypted,
            })
            
            doc.close()
            
        except Exception as e:
            logger.error(f"Error extracting metadata with fitz: {e}")
    
    elif backend == 'pypdf2' and PYPDF2_AVAILABLE:
        try:
            reader = PyPDF2.PdfReader(lpath)
            
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': str(reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(reader.metadata.get('/ModDate', '')),
                })
            
            metadata['pages'] = len(reader.pages)
            metadata['encrypted'] = reader.is_encrypted
            
        except Exception as e:
            logger.error(f"Error extracting metadata with PyPDF2: {e}")
    
    # Generate file hash
    metadata['md5_hash'] = _calculate_file_hash(lpath)
    
    return metadata


def _extract_pages(lpath: str, backend: str, clean: bool) -> List[Dict[str, Any]]:
    """Extract text page by page."""
    pages = []
    
    if backend == 'fitz' and FITZ_AVAILABLE:
        doc = fitz.open(lpath)
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if clean:
                text = _clean_pdf_text(text)
            
            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'char_count': len(text),
                'word_count': len(text.split())
            })
        
        doc.close()
    
    elif backend == 'pypdf2' and PYPDF2_AVAILABLE:
        reader = PyPDF2.PdfReader(lpath)
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page._extract_text()
            if clean:
                text = _clean_pdf_text(text)
            
            pages.append({
                'page_number': page_num + 1,
                'text': text,
                'char_count': len(text),
                'word_count': len(text.split())
            })
    
    return pages


def _extract_full(lpath: str, backend: str, clean: bool, extract_images: bool) -> Dict[str, Any]:
    """Extract comprehensive data from PDF."""
    result = {
        'pdf_path': lpath,
        'filename': os.path.basename(lpath),
        'backend': backend,
        'extraction_params': {
            'clean_text': clean,
            'extract_images': extract_images
        }
    }
    
    # Extract all components
    try:
        result['full_text'] = __extract_text(lpath, backend, clean)
        result['sections'] = _extract_sections(lpath, backend, clean)
        result['metadata'] = _extract_metadata(lpath, backend)
        result['pages'] = _extract_pages(lpath, backend, clean)
        
        # Calculate statistics
        result['stats'] = {
            'total_chars': len(result['full_text']),
            'total_words': len(result['full_text'].split()),
            'total_pages': len(result['pages']),
            'num_sections': len(result['sections']),
            'avg_words_per_page': len(result['full_text'].split()) / len(result['pages']) if result['pages'] else 0
        }
        
        # Extract images if requested (only with fitz)
        if extract_images and backend == 'fitz' and FITZ_AVAILABLE:
            result['images'] = _extract_image_info(lpath)
        
    except Exception as e:
        logger.error(f"Error in full extraction: {e}")
        result['error'] = str(e)
    
    return result


def _extract_image_info(lpath: str) -> List[Dict[str, Any]]:
    """Extract information about images in PDF (requires fitz)."""
    images = []
    
    try:
        doc = fitz.open(lpath)
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                images.append({
                    'page': page_num + 1,
                    'index': img_index,
                    'width': img[2],
                    'height': img[3],
                    'colorspace': img[4],
                    'bpc': img[5],  # bits per component
                })
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Error extracting image info: {e}")
    
    return images


def _clean_pdf_text(text: str) -> str:
    """Clean extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix hyphenated words at line breaks
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Remove page numbers (common patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    
    # Clean up common PDF artifacts
    text = text.replace('\x00', '')  # Null bytes
    text = re.sub(r'[\x01-\x1f\x7f-\x9f]', '', text)  # Control characters
    
    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('–', '-').replace('—', '-')
    
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def _calculate_file_hash(lpath: str) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(lpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# Convenience function
def load_pdf(filepath: str, mode: str = 'text', **kwargs) -> Any:
    """
    Load PDF file with specified extraction mode.
    
    Args:
        filepath: Path to PDF file
        mode: Extraction mode (text, sections, metadata, pages, full)
        **kwargs: Additional arguments for extraction
    
    Returns:
        Extracted content based on mode
    """
    return _load_pdf(filepath, mode=mode, **kwargs)


# EOF