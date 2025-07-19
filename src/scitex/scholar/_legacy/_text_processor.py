#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:20:00 (ywatanabe)"
# File: src/scitex_scholar/text_processor.py

"""
Text processing module for scientific documents.

This module provides functionality for cleaning, normalizing, and processing
scientific text documents for search and analysis purposes.
"""

import re
from typing import List, Dict, Any, Optional
from ._latex_parser import LaTeXParser


class TextProcessor:
    """
    Text processor for scientific documents.
    
    Provides methods for cleaning, normalizing, and extracting information
    from scientific texts including LaTeX content.
    """
    
    def __init__(self, latex_parser: Optional[LaTeXParser] = None):
        """
        Initialize TextProcessor with default settings.
        
        Args:
            latex_parser: Optional LaTeX parser instance for enhanced LaTeX processing
        """
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        # Initialize LaTeX parser for enhanced document processing
        self.latex_parser = latex_parser or LaTeXParser()
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        return cleaned
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text to lowercase for consistent processing.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        return text.lower()
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text by removing stop words.
        
        Args:
            text: Input text
            min_length: Minimum keyword length
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Normalize and split into words
        normalized = self.normalize_text(text)
        words = re.findall(r'\b[a-zA-Z]+\b', normalized)
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) >= min_length
        ]
        
        return list(set(keywords))  # Remove duplicates
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common sections from scientific documents.
        
        Args:
            text: Input document text
            
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        
        # Common scientific paper sections
        section_patterns = {
            'abstract': r'(?i)abstract\s*\n(.*?)(?=\n\s*(?:introduction|keywords|1\.|$))',
            'introduction': r'(?i)introduction\s*\n(.*?)(?=\n\s*(?:method|related|2\.|$))',
            'conclusion': r'(?i)conclusion\s*\n(.*?)(?=\n\s*(?:reference|acknowledgment|$))'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section_name] = self.clean_text(match.group(1))
        
        return sections
    
    def process_document(self, document: str) -> Dict[str, Any]:
        """
        Process a complete scientific document.
        
        Args:
            document: Full document text
            
        Returns:
            Dictionary containing processed document information
        """
        cleaned_text = self.clean_text(document)
        keywords = self.extract_keywords(cleaned_text)
        sections = self.extract_sections(document)
        
        return {
            'cleaned_text': cleaned_text,
            'keywords': keywords,
            'sections': sections,
            'word_count': len(cleaned_text.split()),
            'char_count': len(cleaned_text)
        }
    
    def process_latex_document(self, latex_text: str) -> Dict[str, Any]:
        """
        Process a LaTeX document with enhanced extraction capabilities.
        
        Args:
            latex_text: LaTeX source document
            
        Returns:
            Dictionary containing comprehensive document analysis
        """
        # Parse LaTeX structure
        latex_parsed = self.latex_parser.parse_document(latex_text)
        
        # Clean LaTeX content for text processing
        cleaned_text = self.latex_parser.clean_latex_content(latex_text)
        
        # Extract keywords from cleaned content
        keywords = self.extract_keywords(cleaned_text)
        
        # Merge LaTeX-specific and general text processing results
        result = {
            'cleaned_text': cleaned_text,
            'keywords': keywords,
            'word_count': len(cleaned_text.split()),
            'char_count': len(cleaned_text),
            
            # LaTeX-specific information
            'latex_metadata': latex_parsed.get('metadata', {}),
            'latex_structure': latex_parsed.get('structure', {}),
            'latex_environments': latex_parsed.get('environments', []),
            'math_expressions': latex_parsed.get('math_expressions', []),
            'citations': latex_parsed.get('citations', []),
            
            # Enhanced analysis
            'document_type': 'latex',
            'has_math': len(latex_parsed.get('math_expressions', [])) > 0,
            'has_citations': len(latex_parsed.get('citations', [])) > 0,
            'section_count': len(latex_parsed.get('structure', {}).get('sections', [])),
        }
        
        # Extract mathematical content as keywords if present
        if result['has_math']:
            math_keywords = self._extract_math_keywords(latex_parsed.get('math_expressions', []))
            result['math_keywords'] = math_keywords
            result['keywords'].extend(math_keywords)
        
        return result
    
    def _extract_math_keywords(self, math_expressions: List[Dict[str, str]]) -> List[str]:
        """
        Extract mathematical keywords from LaTeX math expressions.
        
        Args:
            math_expressions: List of mathematical expressions from LaTeX parser
            
        Returns:
            List of mathematical keywords and concepts
        """
        math_keywords = []
        
        # Common mathematical keywords to extract
        math_patterns = {
            'integral': r'\\int',
            'derivative': r'\\frac\{d\w*\}',
            'summation': r'\\sum',
            'limit': r'\\lim',
            'matrix': r'\\begin\{(matrix|pmatrix|bmatrix)\}',
            'equation': r'=',
            'inequality': r'[<>≤≥]',
            'infinity': r'\\infty',
            'partial_derivative': r'\\partial',
            'square_root': r'\\sqrt',
        }
        
        for expr in math_expressions:
            content = expr.get('content', '')
            for keyword, pattern in math_patterns.items():
                if re.search(pattern, content):
                    math_keywords.append(keyword)
        
        return list(set(math_keywords))  # Remove duplicates
    
    def detect_document_type(self, text: str) -> str:
        """
        Detect the type of document based on content patterns.
        
        Args:
            text: Document text
            
        Returns:
            Detected document type ('latex', 'plain_text', 'scientific')
        """
        # Check for LaTeX patterns
        latex_patterns = [
            r'\\documentclass',
            r'\\begin\{document\}',
            r'\\section\{',
            r'\\cite\{',
            r'\$.*?\$',  # Math expressions
        ]
        
        latex_score = sum(1 for pattern in latex_patterns if re.search(pattern, text))
        
        if latex_score >= 2:
            return 'latex'
        elif any(word in text.lower() for word in ['research', 'study', 'analysis', 'results', 'conclusion']):
            return 'scientific'
        else:
            return 'plain_text'

# EOF