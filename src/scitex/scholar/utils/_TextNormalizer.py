#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 18:30:00 (ywatanabe)"
# File: ./src/scitex/scholar/utils/_TextNormalizer.py
# ----------------------------------------
from __future__ import annotations

"""Text normalization utilities for improved DOI resolution.

This module provides utilities to normalize text for better matching
in DOI resolution, handling Unicode, LaTeX, and encoding issues.
"""

import re
import unicodedata
from typing import Dict, List


class TextNormalizer:
    """Normalize text for better matching in academic paper searches."""
    
    # LaTeX to Unicode mappings
    LATEX_UNICODE_MAP = {
        # Common accented characters
        r'\{\\\"u\}': 'ü', r'\{\\\"U\}': 'Ü',
        r'\{\\\"o\}': 'ö', r'\{\\\"O\}': 'Ö', 
        r'\{\\\"a\}': 'ä', r'\{\\\"A\}': 'Ä',
        r'\{\\\"e\}': 'ë', r'\{\\\"E\}': 'Ë',
        r'\{\\\"i\}': 'ï', r'\{\\\"I\}': 'Ï',
        
        # Circumflex
        r'\{\\^e\}': 'ê', r'\{\\^E\}': 'Ê',
        r'\{\\^a\}': 'â', r'\{\\^A\}': 'Â',
        r'\{\\^o\}': 'ô', r'\{\\^O\}': 'Ô',
        r'\{\\^u\}': 'û', r'\{\\^U\}': 'Û',
        r'\{\\^i\}': 'î', r'\{\\^I\}': 'Î',
        
        # Grave accent
        r'\{\\`e\}': 'è', r'\{\\`E\}': 'È',
        r'\{\\`a\}': 'à', r'\{\\`A\}': 'À',
        r'\{\\`o\}': 'ò', r'\{\\`O\}': 'Ò',
        r'\{\\`u\}': 'ù', r'\{\\`U\}': 'Ù',
        r'\{\\`i\}': 'ì', r'\{\\`I\}': 'Ì',
        
        # Acute accent
        r'\{\\\'e\}': 'é', r'\{\\\'E\}': 'É',
        r'\{\\\'a\}': 'á', r'\{\\\'A\}': 'Á',
        r'\{\\\'o\}': 'ó', r'\{\\\'O\}': 'Ó',
        r'\{\\\'u\}': 'ú', r'\{\\\'U\}': 'Ú',
        r'\{\\\'i\}': 'í', r'\{\\\'I\}': 'Í',
        
        # Tilde
        r'\{\\~n\}': 'ñ', r'\{\\~N\}': 'Ñ',
        r'\{\\~a\}': 'ã', r'\{\\~A\}': 'Ã',
        r'\{\\~o\}': 'õ', r'\{\\~O\}': 'Õ',
        
        # Cedilla
        r'\{\\c c\}': 'ç', r'\{\\c C\}': 'Ç',
        
        # Ring
        r'\{\\aa\}': 'å', r'\{\\AA\}': 'Å',
        
        # Slash
        r'\{\\o\}': 'ø', r'\{\\O\}': 'Ø',
        
        # Special characters
        r'\{ss\}': 'ß',
        r'\{ae\}': 'æ', r'\{AE\}': 'Æ',
        r'\{oe\}': 'œ', r'\{OE\}': 'Œ',
        
        # Czech/Slovak
        r'\{\\v c\}': 'č', r'\{\\v C\}': 'Č',
        r'\{\\v r\}': 'ř', r'\{\\v R\}': 'Ř',
        r'\{\\v s\}': 'š', r'\{\\v S\}': 'Š',
        r'\{\\v z\}': 'ž', r'\{\\v Z\}': 'Ž',
        r'\{\\v n\}': 'ň', r'\{\\v N\}': 'Ň',
        r'\{\\v t\}': 'ť', r'\{\\v T\}': 'Ť',
        r'\{\\v d\}': 'ď', r'\{\\v D\}': 'Ď',
        r'\{\\v l\}': 'ľ', r'\{\\v L\}': 'Ľ',
        
        # Polish
        r'\{\\\\l\}': 'ł', r'\{\\\\L\}': 'Ł',
        
        # Hungarian
        r'\{\\\\H\{o\}\}': 'ő', r'\{\\\\H\{O\}\}': 'Ő',
        r'\{\\\\H\{u\}\}': 'ű', r'\{\\\\H\{U\}\}': 'Ű',
    }
    
    @classmethod
    def normalize_for_search(cls, text: str, preserve_case: bool = False) -> str:
        """Normalize text for academic paper search matching.
        
        Args:
            text: Input text to normalize
            preserve_case: Whether to preserve original case
            
        Returns:
            Normalized text suitable for fuzzy matching
        """
        if not text:
            return ""
        
        # Convert LaTeX sequences to Unicode
        normalized = cls._convert_latex_to_unicode(text)
        
        # Unicode normalization (decompose accented characters)
        normalized = unicodedata.normalize('NFKD', normalized)
        
        # Convert to lowercase unless preserving case
        if not preserve_case:
            normalized = normalized.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    @classmethod
    def normalize_for_fuzzy_matching(cls, text: str) -> str:
        """Aggressive normalization for fuzzy title matching.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Heavily normalized text for fuzzy matching
        """
        if not text:
            return ""
        
        # Start with search normalization
        normalized = cls.normalize_for_search(text, preserve_case=False)
        
        # Remove punctuation and special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove common stopwords that don't affect meaning
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 
            'through', 'during', 'before', 'after', 'above', 'below', 
            'between', 'among', 'since'
        }
        
        words = [w for w in normalized.split() if w not in stopwords and len(w) > 1]
        
        return ' '.join(words)
    
    @classmethod
    def normalize_author_name(cls, name: str) -> str:
        """Normalize author names for better matching.
        
        Args:
            name: Author name to normalize
            
        Returns:
            Normalized author name
        """
        if not name:
            return ""
        
        # Convert LaTeX to Unicode
        normalized = cls._convert_latex_to_unicode(name)
        
        # Unicode normalization
        normalized = unicodedata.normalize('NFKD', normalized)
        
        # Handle common name formats
        # "Last, First Middle" -> "First Middle Last"
        if ',' in normalized:
            parts = normalized.split(',', 1)
            if len(parts) == 2:
                last_name = parts[0].strip()
                first_names = parts[1].strip()
                normalized = f"{first_names} {last_name}"
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    @classmethod  
    def _convert_latex_to_unicode(cls, text: str) -> str:
        """Convert LaTeX sequences to Unicode characters.
        
        Args:
            text: Text containing LaTeX sequences
            
        Returns:
            Text with LaTeX converted to Unicode
        """
        result = text
        
        # Handle common patterns from academic papers first
        common_patterns = [
            # Handle H{"u}lsemann style (without escaping)
            (r'H\{\"u\}', 'Hü'),
            (r'H\{\"o\}', 'Hö'),
            (r'H\{\"a\}', 'Hä'),
            # Handle with braces
            (r'\{\"u\}', 'ü'), (r'\{\"U\}', 'Ü'),
            (r'\{\"o\}', 'ö'), (r'\{\"O\}', 'Ö'), 
            (r'\{\"a\}', 'ä'), (r'\{\"A\}', 'Ä'),
            (r'\{\"e\}', 'ë'), (r'\{\"E\}', 'Ë'),
            (r'\{\"i\}', 'ï'), (r'\{\"I\}', 'Ï'),
            # Circumflex
            (r'\{\^e\}', 'ê'), (r'\{\^E\}', 'Ê'),
            (r'\{\^a\}', 'â'), (r'\{\^A\}', 'Â'),
            (r'\{\^o\}', 'ô'), (r'\{\^O\}', 'Ô'),
            (r'\{\^u\}', 'û'), (r'\{\^U\}', 'Û'),
            (r'\{\^i\}', 'î'), (r'\{\^I\}', 'Î'),
            # Grave accent
            (r'\{\`e\}', 'è'), (r'\{\`E\}', 'È'),
            (r'\{\`a\}', 'à'), (r'\{\`A\}', 'À'),
            (r'\{\`o\}', 'ò'), (r'\{\`O\}', 'Ò'),
            (r'\{\`u\}', 'ù'), (r'\{\`U\}', 'Ù'),
            (r'\{\`i\}', 'ì'), (r'\{\`I\}', 'Ì'),
            # Acute accent
            (r'\{\'e\}', 'é'), (r'\{\'E\}', 'É'),
            (r'\{\'a\}', 'á'), (r'\{\'A\}', 'Á'),
            (r'\{\'o\}', 'ó'), (r'\{\'O\}', 'Ó'),
            (r'\{\'u\}', 'ú'), (r'\{\'U\}', 'Ú'),
            (r'\{\'i\}', 'í'), (r'\{\'I\}', 'Í'),
        ]
        
        # Apply common patterns first
        for pattern, replacement in common_patterns:
            result = re.sub(pattern, replacement, result)
        
        # Then apply the full mapping with proper escaping
        for latex_seq, unicode_char in cls.LATEX_UNICODE_MAP.items():
            result = re.sub(latex_seq, unicode_char, result)
        
        return result
    
    @classmethod
    def calculate_title_similarity(cls, title1: str, title2: str) -> float:
        """Calculate similarity between two academic paper titles.
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            Similarity score between 0 and 1
        """
        if not title1 or not title2:
            return 0.0
        
        # Normalize both titles for comparison
        norm1 = cls.normalize_for_fuzzy_matching(title1)
        norm2 = cls.normalize_for_fuzzy_matching(title2)
        
        if norm1 == norm2:
            return 1.0
        
        # Calculate word-based Jaccard similarity
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    @classmethod
    def is_likely_same_title(cls, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles likely refer to the same paper.
        
        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if titles are likely the same paper
        """
        similarity = cls.calculate_title_similarity(title1, title2)
        return similarity >= threshold

    @classmethod
    def normalize_title(cls, title: str, remove_trailing_period: bool = True) -> str:
        """Normalize paper title for storage and comparison.
        
        This method provides consistent title normalization across the Scholar system:
        - Removes BibTeX braces: {Title} -> Title
        - Converts LaTeX sequences to Unicode
        - Normalizes whitespace
        - Optionally removes trailing periods
        
        Args:
            title: Paper title to normalize
            remove_trailing_period: Whether to remove trailing period (default: True)
            
        Returns:
            Normalized title string
            
        Examples:
            >>> TextNormalizer.normalize_title("{Deep Learning in Neural Networks.}")
            "Deep Learning in Neural Networks"
            >>> TextNormalizer.normalize_title("Title.", remove_trailing_period=False)
            "Title."
        """
        if not title:
            return ""
        
        # Remove BibTeX braces
        normalized = title.strip('{}')
        
        # Convert LaTeX sequences to Unicode
        normalized = cls._convert_latex_to_unicode(normalized)
        
        # Unicode normalization
        normalized = unicodedata.normalize('NFKD', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove trailing period if requested
        if remove_trailing_period and normalized.endswith('.'):
            normalized = normalized.rstrip('.')
        
        return normalized

    @classmethod
    def strip_html_tags(cls, text: str) -> str:
        """Strip HTML/XML tags from text.
        
        This method removes HTML and XML tags commonly found in academic metadata
        such as abstracts and titles retrieved from APIs.
        
        Args:
            text: Text containing HTML/XML tags
            
        Returns:
            Text with HTML/XML tags removed
            
        Examples:
            >>> TextNormalizer.strip_html_tags("<p>Abstract <i>text</i> here.</p>")
            "Abstract text here."
            >>> TextNormalizer.strip_html_tags("Title with <sup>superscript</sup>")
            "Title with superscript"
        """
        if not text:
            return ""
        
        # Remove HTML/XML tags using regex
        # This pattern matches opening and closing tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up any HTML entities that might remain
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&#39;': "'",
            '&#34;': '"',
        }
        
        for entity, replacement in html_entities.items():
            clean_text = clean_text.replace(entity, replacement)
        
        # Normalize whitespace after tag removal
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    @classmethod
    def clean_metadata_text(cls, text: str) -> str:
        """Comprehensive cleaning for metadata text fields.
        
        This combines HTML tag stripping, LaTeX conversion, and normalization
        specifically for metadata fields like titles and abstracts.
        
        Args:
            text: Raw metadata text
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # First strip HTML/XML tags
        cleaned = cls.strip_html_tags(text)
        
        # Convert LaTeX sequences to Unicode (needed before normalization)
        cleaned = cls._convert_latex_to_unicode(cleaned)
        
        # Then apply Unicode normalization and whitespace cleanup
        # Use NFC to keep composed characters like ü together
        cleaned = unicodedata.normalize('NFC', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned


# Export
__all__ = ["TextNormalizer"]

# EOF