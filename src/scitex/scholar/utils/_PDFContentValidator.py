#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 14:00:00"
# Author: Claude
# File: _PDFContentValidator.py

"""
Validate PDF content to ensure it contains the main paper.

This module implements Critical Task #8: Confirm downloaded PDFs are main contents
by analyzing PDF structure, text content, and metadata.
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz

from scitex import logging
from .._Paper import Paper

logger = logging.getLogger(__name__)


class PDFContentValidator:
    """Validate PDF content to ensure it's the main paper."""
    
    def __init__(self):
        """Initialize PDF content validator."""
        # Common indicators of non-main content
        self.abstract_only_indicators = [
            "abstract only",
            "summary only",
            "preview",
            "excerpt",
            "sample pages",
            "table of contents"
        ]
        
        self.supplementary_indicators = [
            "supplementary",
            "supporting information",
            "appendix",
            "supplemental",
            "additional file",
            "extended data"
        ]
        
        self.error_indicators = [
            "access denied",
            "subscription required",
            "please log in",
            "purchase",
            "not found",
            "404",
            "403",
            "unauthorized"
        ]
        
        # Expected sections in a full paper
        self.expected_sections = [
            "abstract",
            "introduction",
            "method",
            "result",
            "discussion",
            "conclusion",
            "reference"
        ]
        
        # Minimum thresholds
        self.min_pages = 3  # Most papers have at least 3 pages
        self.min_words = 1000  # Reasonable minimum for a paper
        self.min_sections = 3  # Should have multiple sections
        
    def validate_pdf(self, pdf_path: Path, paper: Optional[Paper] = None) -> Dict[str, Any]:
        """
        Validate a PDF file to ensure it contains the main paper.
        
        Args:
            pdf_path: Path to PDF file
            paper: Optional Paper object with metadata
            
        Returns:
            Dict with validation results
        """
        if not pdf_path.exists():
            return {
                'valid': False,
                'reason': 'File does not exist',
                'confidence': 1.0
            }
            
        try:
            # Open PDF
            doc = fitz.open(str(pdf_path))
            
            # Basic checks
            page_count = len(doc)
            
            # Extract text from first few pages
            text_samples = []
            full_text = ""
            
            for i in range(min(5, page_count)):
                page = doc[i]
                text = page.get_text()
                text_samples.append(text)
                full_text += text + "\n"
                
            doc.close()
            
            # Run validation checks
            validation_results = {
                'page_count': page_count,
                'file_size': pdf_path.stat().st_size,
                'checks': {}
            }
            
            # 1. Check page count
            validation_results['checks']['page_count'] = self._check_page_count(page_count)
            
            # 2. Check for error pages
            validation_results['checks']['error_page'] = self._check_error_indicators(full_text)
            
            # 3. Check for abstract-only
            validation_results['checks']['abstract_only'] = self._check_abstract_only(full_text)
            
            # 4. Check for supplementary material
            validation_results['checks']['supplementary'] = self._check_supplementary(full_text)
            
            # 5. Check word count
            validation_results['checks']['word_count'] = self._check_word_count(full_text)
            
            # 6. Check for expected sections
            validation_results['checks']['sections'] = self._check_sections(full_text)
            
            # 7. Check title match (if paper metadata provided)
            if paper and paper.title:
                validation_results['checks']['title_match'] = self._check_title_match(
                    text_samples[0] if text_samples else "",
                    paper.title
                )
            
            # 8. Check for references section
            validation_results['checks']['references'] = self._check_references(full_text)
            
            # Calculate overall validity
            checks = validation_results['checks']
            
            # Critical failures
            if not checks['page_count']['valid'] or checks['error_page']['detected']:
                validation_results['valid'] = False
                validation_results['reason'] = checks['error_page']['reason'] if checks['error_page']['detected'] else 'Too few pages'
                validation_results['confidence'] = 0.9
                
            # Likely not main content
            elif checks['abstract_only']['detected'] or checks['supplementary']['detected']:
                validation_results['valid'] = False
                validation_results['reason'] = 'Not main paper content'
                validation_results['confidence'] = 0.8
                
            # Suspicious content
            elif not checks['word_count']['valid'] or not checks['sections']['valid']:
                validation_results['valid'] = False
                validation_results['reason'] = 'Content too short or missing sections'
                validation_results['confidence'] = 0.7
                
            # Title mismatch (if checked)
            elif 'title_match' in checks and not checks['title_match']['matches']:
                validation_results['valid'] = False
                validation_results['reason'] = 'Title does not match'
                validation_results['confidence'] = 0.6
                
            # Likely valid
            else:
                validation_results['valid'] = True
                validation_results['reason'] = 'Appears to be main paper'
                validation_results['confidence'] = 0.9
                
                # Boost confidence if references found
                if checks['references']['found']:
                    validation_results['confidence'] = 0.95
                    
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'confidence': 0.5
            }
            
    def _check_page_count(self, page_count: int) -> Dict[str, Any]:
        """Check if page count is reasonable."""
        return {
            'valid': page_count >= self.min_pages,
            'page_count': page_count,
            'min_expected': self.min_pages
        }
        
    def _check_error_indicators(self, text: str) -> Dict[str, Any]:
        """Check for error page indicators."""
        text_lower = text.lower()
        
        for indicator in self.error_indicators:
            if indicator in text_lower:
                return {
                    'detected': True,
                    'indicator': indicator,
                    'reason': f'Error indicator found: {indicator}'
                }
                
        return {'detected': False}
        
    def _check_abstract_only(self, text: str) -> Dict[str, Any]:
        """Check if PDF contains only abstract."""
        text_lower = text.lower()
        
        for indicator in self.abstract_only_indicators:
            if indicator in text_lower:
                return {
                    'detected': True,
                    'indicator': indicator
                }
                
        # Also check if text is suspiciously short after abstract
        if "abstract" in text_lower:
            abstract_pos = text_lower.find("abstract")
            remaining_text = text[abstract_pos + 1000:]  # Text after abstract + buffer
            
            if len(remaining_text.split()) < 500:  # Very little content after abstract
                return {
                    'detected': True,
                    'indicator': 'short_content_after_abstract'
                }
                
        return {'detected': False}
        
    def _check_supplementary(self, text: str) -> Dict[str, Any]:
        """Check if PDF is supplementary material."""
        text_lower = text.lower()
        first_page = text_lower[:2000]  # Check first part heavily
        
        for indicator in self.supplementary_indicators:
            # Strong indicator if in first page
            if indicator in first_page:
                return {
                    'detected': True,
                    'indicator': indicator,
                    'location': 'first_page'
                }
            # Weaker indicator if elsewhere
            elif text_lower.count(indicator) > 3:  # Mentioned multiple times
                return {
                    'detected': True,
                    'indicator': indicator,
                    'location': 'multiple_mentions'
                }
                
        return {'detected': False}
        
    def _check_word_count(self, text: str) -> Dict[str, Any]:
        """Check if word count is reasonable."""
        words = text.split()
        word_count = len(words)
        
        return {
            'valid': word_count >= self.min_words,
            'word_count': word_count,
            'min_expected': self.min_words
        }
        
    def _check_sections(self, text: str) -> Dict[str, Any]:
        """Check for expected paper sections."""
        text_lower = text.lower()
        found_sections = []
        
        for section in self.expected_sections:
            # Look for section headers
            patterns = [
                f"\n{section}\n",
                f"\n{section}:\n",
                f"\n\\d+\\.?\\s*{section}",
                f"{section}\n[=-]+\n"  # Underlined headers
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    found_sections.append(section)
                    break
                    
        return {
            'valid': len(found_sections) >= self.min_sections,
            'found_sections': found_sections,
            'count': len(found_sections),
            'min_expected': self.min_sections
        }
        
    def _check_title_match(self, first_page_text: str, expected_title: str) -> Dict[str, Any]:
        """Check if paper title matches expected."""
        # Clean title
        expected_clean = re.sub(r'[^\w\s]', '', expected_title.lower())
        expected_words = expected_clean.split()
        
        # Look for title in first page
        first_page_lower = first_page_text.lower()
        
        # Check exact match
        if expected_title.lower() in first_page_lower:
            return {
                'matches': True,
                'match_type': 'exact'
            }
            
        # Check word match (at least 80% of words)
        found_words = sum(1 for word in expected_words if word in first_page_lower)
        match_ratio = found_words / len(expected_words) if expected_words else 0
        
        return {
            'matches': match_ratio >= 0.8,
            'match_type': 'partial',
            'match_ratio': match_ratio
        }
        
    def _check_references(self, text: str) -> Dict[str, Any]:
        """Check for references section."""
        text_lower = text.lower()
        
        # Common reference section headers
        reference_headers = [
            "references",
            "bibliography",
            "works cited",
            "literature cited"
        ]
        
        for header in reference_headers:
            if header in text_lower:
                # Check if it's near the end
                position = text_lower.rfind(header)
                relative_position = position / len(text_lower)
                
                if relative_position > 0.7:  # In last 30% of document
                    return {
                        'found': True,
                        'header': header,
                        'position': 'end'
                    }
                    
        return {'found': False}
        
    def validate_batch(
        self,
        pdf_paths: List[Path],
        papers: Optional[List[Paper]] = None
    ) -> Dict[Path, Dict[str, Any]]:
        """
        Validate multiple PDFs.
        
        Args:
            pdf_paths: List of PDF paths
            papers: Optional list of Paper objects
            
        Returns:
            Dict mapping paths to validation results
        """
        results = {}
        
        for i, pdf_path in enumerate(pdf_paths):
            paper = papers[i] if papers and i < len(papers) else None
            results[pdf_path] = self.validate_pdf(pdf_path, paper)
            
        return results
        
    def get_content_summary(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Get a summary of PDF content for debugging.
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Dict with content summary
        """
        try:
            doc = fitz.open(str(pdf_path))
            
            # Extract metadata
            metadata = doc.metadata
            
            # Extract outline (table of contents)
            outline = []
            toc = doc.get_toc()
            for level, title, page in toc:
                outline.append({
                    'level': level,
                    'title': title,
                    'page': page
                })
                
            # Extract text statistics
            total_chars = 0
            total_words = 0
            page_stats = []
            
            for i, page in enumerate(doc):
                text = page.get_text()
                chars = len(text)
                words = len(text.split())
                
                total_chars += chars
                total_words += words
                
                page_stats.append({
                    'page': i + 1,
                    'chars': chars,
                    'words': words
                })
                
            # Find potential section headers
            full_text = ""
            for page in doc:
                full_text += page.get_text() + "\n"
                
            headers = self._extract_headers(full_text)
            
            doc.close()
            
            return {
                'metadata': metadata,
                'page_count': len(page_stats),
                'total_words': total_words,
                'total_chars': total_chars,
                'outline': outline,
                'page_stats': page_stats[:5],  # First 5 pages
                'detected_headers': headers[:10]  # First 10 headers
            }
            
        except Exception as e:
            logger.error(f"Error getting content summary: {e}")
            return {'error': str(e)}
            
    def _extract_headers(self, text: str) -> List[str]:
        """Extract potential section headers from text."""
        headers = []
        
        # Pattern for headers (lines with specific formatting)
        patterns = [
            r'^\d+\.?\s+[A-Z][A-Za-z\s]+$',  # Numbered headers
            r'^[A-Z][A-Z\s]+$',  # All caps headers
            r'^[A-Z][A-Za-z\s]+:$'  # Headers with colon
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line) < 100:  # Reasonable header length
                for pattern in patterns:
                    if re.match(pattern, line):
                        headers.append(line)
                        break
                        
        return headers


def validate_pdf_quality(pdf_path: Path, paper: Optional[Paper] = None) -> Tuple[bool, str]:
    """
    Quick validation function for PDF quality.
    
    Args:
        pdf_path: Path to PDF
        paper: Optional Paper object
        
    Returns:
        Tuple of (is_valid, reason)
    """
    validator = PDFContentValidator()
    result = validator.validate_pdf(pdf_path, paper)
    
    return result['valid'], result['reason']