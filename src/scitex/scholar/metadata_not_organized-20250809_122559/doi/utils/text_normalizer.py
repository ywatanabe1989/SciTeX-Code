#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 08:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/text_normalizer.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/utils/text_normalizer.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
TextNormalizer: Fix LaTeX encoding and Unicode issues for better search accuracy.

This utility normalizes text to improve matching accuracy when searching
academic databases that may have different encoding representations.

Examples:
    H{\"u}lsemann → Hülsemann
    Dvořák → Dvorak (optional ASCII fallback)
    García-López → Garcia-Lopez (optional ASCII fallback)
    {\\textquoteright} → '
"""

import re
import unicodedata
from typing import Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


class TextNormalizer:
    """Normalize text by fixing LaTeX encoding and Unicode issues."""
    
    # LaTeX to Unicode mappings
    LATEX_TO_UNICODE = {
        # Accented characters
        r'\{\\\"a\}': 'ä', r'\{\\\"A\}': 'Ä',
        r'\{\\\"e\}': 'ë', r'\{\\\"E\}': 'Ë', 
        r'\{\\\"i\}': 'ï', r'\{\\\"I\}': 'Ï',
        r'\{\\\"o\}': 'ö', r'\{\\\"O\}': 'Ö',
        r'\{\\\"u\}': 'ü', r'\{\\\"U\}': 'Ü',
        r'\{\\\"y\}': 'ÿ', r'\{\\\"Y\}': 'Ÿ',
        
        # Acute accents
        r"\\'{a}": 'á', r"\\'{A}": 'Á',
        r"\\'{e}": 'é', r"\\'{E}": 'É',
        r"\\'{i}": 'í', r"\\'{I}": 'Í',
        r"\\'{o}": 'ó', r"\\'{O}": 'Ó',
        r"\\'{u}": 'ú', r"\\'{U}": 'Ú',
        r"\\'{y}": 'ý', r"\\'{Y}": 'Ý',
        
        # Grave accents
        r'\\`{a}': 'à', r'\\`{A}': 'À',
        r'\\`{e}': 'è', r'\\`{E}': 'È',
        r'\\`{i}': 'ì', r'\\`{I}': 'Ì',
        r'\\`{o}': 'ò', r'\\`{O}': 'Ò',
        r'\\`{u}': 'ù', r'\\`{U}': 'Ù',
        
        # Circumflex accents
        r'\\^{a}': 'â', r'\\^{A}': 'Â',
        r'\\^{e}': 'ê', r'\\^{E}': 'Ê',
        r'\\^{i}': 'î', r'\\^{I}': 'Î',
        r'\\^{o}': 'ô', r'\\^{O}': 'Ô',
        r'\\^{u}': 'û', r'\\^{U}': 'Û',
        
        # Tilde accents
        r'\\~{a}': 'ã', r'\\~{A}': 'Ã',
        r'\\~{n}': 'ñ', r'\\~{N}': 'Ñ',
        r'\\~{o}': 'õ', r'\\~{O}': 'Õ',
        
        # Ring and cedilla
        r'\\r{a}': 'å', r'\\r{A}': 'Å',
        r'\\c{c}': 'ç', r'\\c{C}': 'Ç',
        
        # Slash and stroke
        r'\\o': 'ø', r'\\O': 'Ø',
        r'\\l': 'ł', r'\\L': 'Ł',
        
        # Special characters
        r'\\ae': 'æ', r'\\AE': 'Æ',
        r'\\oe': 'œ', r'\\OE': 'Œ',
        r'\\ss': 'ß',
        
        # Quotation marks
        r'\\textquoteright': "'",
        r'\\textquoteleft': "'",
        r'\\textquotedblleft': '"',
        r'\\textquotedblright': '"',
        
        # Dashes
        r'\\textemdash': '—',
        r'\\textendash': '–',
        
        # Common patterns with braces
        r'\{([aeiouAEIOU])\}': r'\1',  # Remove braces around vowels
    }
    
    def __init__(self, ascii_fallback: bool = False):
        """
        Initialize text normalizer.
        
        Args:
            ascii_fallback: If True, also convert Unicode to ASCII approximations
        """
        self.ascii_fallback = ascii_fallback
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {
            pattern: re.compile(pattern) 
            for pattern in self.LATEX_TO_UNICODE.keys()
        }
        
    def normalize_latex(self, text: str) -> str:
        """
        Convert LaTeX encoding to Unicode characters.
        
        Args:
            text: Text with potential LaTeX encoding
            
        Returns:
            Text with LaTeX converted to Unicode
        """
        if not text or not isinstance(text, str):
            return text
            
        normalized = text
        
        # Apply LaTeX to Unicode conversions
        for latex_pattern, unicode_char in self.LATEX_TO_UNICODE.items():
            if latex_pattern in self.compiled_patterns:
                normalized = self.compiled_patterns[latex_pattern].sub(
                    unicode_char, normalized
                )
            else:
                # Simple string replacement for non-regex patterns
                normalized = normalized.replace(latex_pattern, unicode_char)
                
        # Clean up remaining braces around single characters
        normalized = re.sub(r'\{([a-zA-Z])\}', r'\1', normalized)
        
        # Clean up excessive whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
        
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters using NFD normalization.
        
        Args:
            text: Text with potential Unicode issues
            
        Returns:
            Unicode-normalized text
        """
        if not text or not isinstance(text, str):
            return text
            
        # Normalize using NFD (decomposed form)
        normalized = unicodedata.normalize('NFD', text)
        
        # Optionally convert to ASCII approximations
        if self.ascii_fallback:
            # Remove combining characters (accents)
            normalized = ''.join(
                char for char in normalized 
                if unicodedata.category(char) != 'Mn'
            )
            
        return normalized
        
    def normalize_text(self, text: str) -> str:
        """
        Apply complete text normalization (LaTeX + Unicode).
        
        Args:
            text: Text to normalize
            
        Returns:
            Fully normalized text
        """
        if not text or not isinstance(text, str):
            return text
            
        # First convert LaTeX to Unicode
        normalized = self.normalize_latex(text)
        
        # Then normalize Unicode
        normalized = self.normalize_unicode(normalized)
        
        return normalized
        
    def normalize_author_name(self, author: str) -> str:
        """
        Normalize author name with special handling for academic formats.
        
        Args:
            author: Author name to normalize
            
        Returns:
            Normalized author name
        """
        if not author or not isinstance(author, str):
            return author
            
        # Apply standard normalization
        normalized = self.normalize_text(author)
        
        # Handle common academic name formats
        # Remove excessive commas and spaces
        normalized = re.sub(r',\s*,', ',', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Handle "LastName, FirstName" format
        if ',' in normalized:
            parts = [part.strip() for part in normalized.split(',')]
            if len(parts) == 2:
                # Ensure proper spacing
                normalized = f"{parts[0]}, {parts[1]}"
                
        return normalized
        
    def normalize_title(self, title: str) -> str:
        """
        Normalize paper title with special handling for academic formats.
        
        Args:
            title: Paper title to normalize
            
        Returns:
            Normalized title
        """
        if not title or not isinstance(title, str):
            return title
            
        # Apply standard normalization
        normalized = self.normalize_text(title)
        
        # Handle title-specific issues
        # Remove excessive punctuation
        normalized = re.sub(r'[.]{2,}', '.', normalized)
        normalized = re.sub(r'[?]{2,}', '?', normalized)
        normalized = re.sub(r'[!]{2,}', '!', normalized)
        
        # Clean up spacing around punctuation
        normalized = re.sub(r'\s+([.!?:;,])', r'\1', normalized)
        normalized = re.sub(r'([.!?:;,])\s+', r'\1 ', normalized)
        
        # Remove trailing punctuation that might cause issues
        normalized = normalized.rstrip('.')
        
        return normalized
        
    def normalize_bibtex_entry(self, entry: Dict) -> Dict:
        """
        Normalize all text fields in a BibTeX entry.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Entry with normalized text fields
        """
        if not entry or not isinstance(entry, dict):
            return entry
            
        normalized_entry = entry.copy()
        
        # Fields that should be normalized
        text_fields = [
            'title', 'author', 'journal', 'booktitle', 'publisher',
            'institution', 'organization', 'school', 'address',
            'note', 'abstract', 'keywords'
        ]
        
        for field in text_fields:
            if field in normalized_entry and normalized_entry[field]:
                if field == 'author':
                    # Special handling for author field
                    if isinstance(normalized_entry[field], list):
                        normalized_entry[field] = [
                            self.normalize_author_name(author) 
                            for author in normalized_entry[field]
                        ]
                    else:
                        normalized_entry[field] = self.normalize_author_name(
                            normalized_entry[field]
                        )
                elif field == 'title':
                    normalized_entry[field] = self.normalize_title(
                        normalized_entry[field]
                    )
                else:
                    normalized_entry[field] = self.normalize_text(
                        normalized_entry[field]
                    )
                    
        return normalized_entry
        
    def normalize_bibtex_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Normalize all text fields in multiple BibTeX entries.
        
        Args:
            entries: List of BibTeX entry dictionaries
            
        Returns:
            List of entries with normalized text fields
        """
        if not entries:
            return entries
            
        normalized_entries = [
            self.normalize_bibtex_entry(entry) 
            for entry in entries
        ]
        
        logger.info(f"TextNormalizer: Normalized {len(normalized_entries)} entries")
        
        return normalized_entries
        
    def create_search_variants(self, text: str) -> List[str]:
        """
        Create multiple search variants of text for better matching.
        
        Args:
            text: Original text
            
        Returns:
            List of text variants for searching
        """
        if not text or not isinstance(text, str):
            return [text] if text else []
            
        variants = set()
        
        # Original text
        variants.add(text)
        
        # LaTeX normalized
        latex_normalized = self.normalize_latex(text)
        variants.add(latex_normalized)
        
        # Unicode normalized
        unicode_normalized = self.normalize_unicode(latex_normalized)
        variants.add(unicode_normalized)
        
        # ASCII fallback (if enabled)
        if self.ascii_fallback:
            ascii_normalizer = TextNormalizer(ascii_fallback=True)
            ascii_normalized = ascii_normalizer.normalize_unicode(unicode_normalized)
            variants.add(ascii_normalized)
            
        # Remove duplicates and empty strings
        variants = [v for v in variants if v and v.strip()]
        
        return sorted(list(set(variants)))
        
    def is_title_match(self, title1: str, title2: str, threshold: float = 0.6) -> bool:
        """
        Check if two titles match using advanced normalization and similarity.
        
        This method is significantly more robust than simple string matching,
        handling LaTeX encoding, Unicode issues, and academic title variations.
        
        Args:
            title1: First title to compare
            title2: Second title to compare  
            threshold: Similarity threshold (0.0-1.0, default 0.6)
            
        Returns:
            True if titles match above threshold
        """
        if not title1 or not title2:
            return False
            
        # Normalize both titles
        norm_title1 = self.normalize_title(title1)
        norm_title2 = self.normalize_title(title2)
        
        # Check for exact match after normalization
        if norm_title1.lower() == norm_title2.lower():
            return True
            
        # Advanced normalization for comparison
        def normalize_for_comparison(title: str) -> str:
            import string
            title = title.lower()
            # Remove punctuation
            translator = str.maketrans('', '', string.punctuation)
            title = title.translate(translator)
            # Remove extra whitespace
            title = ' '.join(title.split())
            return title
        
        comp_title1 = normalize_for_comparison(norm_title1)
        comp_title2 = normalize_for_comparison(norm_title2)
        
        # Exact match after aggressive normalization
        if comp_title1 == comp_title2:
            return True
        
        # Remove common stop words that don't contribute to matching
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
            'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may'
        }
        
        def remove_stop_words(text: str) -> str:
            words = text.split()
            return ' '.join([w for w in words if w not in stop_words])
        
        filtered_title1 = remove_stop_words(comp_title1)
        filtered_title2 = remove_stop_words(comp_title2)
        
        # Try without stop words
        if filtered_title1 == filtered_title2:
            return True
            
        # Calculate Jaccard similarity on filtered words
        words1 = set(filtered_title1.split())
        words2 = set(filtered_title2.split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return False
        
        jaccard = len(intersection) / len(union)
        
        # Apply threshold
        is_match = jaccard >= threshold
        
        if is_match:
            logger.debug(
                f"Title match found (Jaccard={jaccard:.3f}): "
                f"'{title1[:50]}...' ≈ '{title2[:50]}...'"
            )
        
        return is_match


def main():
    """Test and demonstrate TextNormalizer functionality."""
    print("=" * 60)
    print("TextNormalizer Test Suite")
    print("=" * 60)
    
    # Test with and without ASCII fallback
    normalizers = [
        ("Unicode", TextNormalizer(ascii_fallback=False)),
        ("ASCII", TextNormalizer(ascii_fallback=True))
    ]
    
    # Test cases
    test_texts = [
        r'H{\"u}lsemann',  # LaTeX umlaut
        r'Dvořák',         # Unicode characters
        r'García-López',   # Multiple accents
        r'{\\textquoteright}Connor',  # LaTeX quotes
        r'Müller, J{\"o}rg',  # Mixed LaTeX and Unicode
        r'{\AA}ngstr{\"o}m',  # LaTeX special characters
        r'Normal Text',    # No encoding issues
    ]
    
    print("\n1. Testing text normalization:")
    for normalizer_name, normalizer in normalizers:
        print(f"\n   --- {normalizer_name} Mode ---")
        for text in test_texts:
            result = normalizer.normalize_text(text)
            print(f"   {text} → {result}")
            
    # Test BibTeX entry normalization
    print("\n2. Testing BibTeX entry normalization:")
    test_entry = {
        'title': r'Deep Learning with H{\"u}lsemann Networks',
        'author': r'García-López, José and M{\"u}ller, Hans',
        'journal': r'Journal of Dvořák Studies',
        'year': '2023',
        'doi': '10.1234/example'
    }
    
    normalizer = TextNormalizer(ascii_fallback=False)
    normalized_entry = normalizer.normalize_bibtex_entry(test_entry)
    
    print("   Original entry:")
    for key, value in test_entry.items():
        print(f"     {key}: {value}")
        
    print("   Normalized entry:")
    for key, value in normalized_entry.items():
        print(f"     {key}: {value}")
        
    # Test search variants
    print("\n3. Testing search variants:")
    test_names = [
        r'H{\"u}lsemann',
        r'García-López',
        r'Dvořák'
    ]
    
    for name in test_names:
        variants = normalizer.create_search_variants(name)
        print(f"   {name}:")
        for i, variant in enumerate(variants):
            print(f"     {i+1}. {variant}")
            
    print("\n" + "=" * 60)
    print("✅ TextNormalizer test completed!")
    print("=" * 60)
    print("\nUsage patterns:")
    print("1. LaTeX only: normalizer.normalize_latex(text)")
    print("2. Unicode only: normalizer.normalize_unicode(text)")
    print("3. Full normalization: normalizer.normalize_text(text)")
    print("4. BibTeX entry: normalizer.normalize_bibtex_entry(entry)")
    print("5. Search variants: normalizer.create_search_variants(text)")


if __name__ == "__main__":
    main()


# python -m scitex.scholar.doi.utils.text_normalizer

# EOF