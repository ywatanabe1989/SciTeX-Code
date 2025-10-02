#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 06:25:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/utils/_URLDOIExtractor.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URLDOISource: Extract DOIs directly from URL fields in BibTeX entries.

This utility provides immediate DOI recovery for papers that have
DOI URLs in their URL field but no explicit DOI field.

Examples:
    https://doi.org/10.1002/hbm.26190 → 10.1002/hbm.26190
    http://dx.doi.org/10.1038/nature12373 → 10.1038/nature12373
    https://www.doi.org/10.1126/science.aao0702 → 10.1126/science.aao0702
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from scitex import logging

logger = logging.getLogger(__name__)


class URLDOIExtractor:
    """Extract DOIs from URL fields with comprehensive pattern matching."""

    # DOI patterns for different URL formats
    DOI_URL_PATTERNS = [
        # Standard DOI URLs
        r"https?://(?:www\.)?doi\.org/(.+)",
        r"https?://dx\.doi\.org/(.+)",
        r"https?://(?:www\.)?dx\.doi\.org/(.+)",
        # Publisher-specific DOI URLs
        r"https?://doi\.wiley\.com/(.+)",
        r"https?://doi\.nature\.com/(.+)",
        r"https?://doi\.apa\.org/(.+)",
        # General DOI pattern in URLs (more permissive)
        r"(?:doi[\.:/]|DOI[\.:/])([0-9]{2}\.[0-9]{4,}/[^\s\?&#]+)",
    ]

    # Valid DOI pattern for validation
    DOI_PATTERN = re.compile(r"^10\.\d{4,}/[^\s]+$")

    def __init__(self):
        """Initialize the URL DOI extractor."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.DOI_URL_PATTERNS
        ]

    def extract_doi_from_url(self, url: str) -> Optional[str]:
        """
        Extract DOI from a single URL string.

        Args:
            url: URL string to extract DOI from

        Returns:
            DOI string if found and valid, None otherwise
        """
        if not url or not isinstance(url, str):
            return None

        url = url.strip()
        if not url:
            return None

        # Try each pattern
        for pattern in self.compiled_patterns:
            match = pattern.search(url)
            if match:
                potential_doi = match.group(1).strip()

                # Clean up common URL artifacts
                potential_doi = self._clean_doi(potential_doi)

                # Validate DOI format
                if self._is_valid_doi(potential_doi):
                    logger.debug(
                        f"Extracted DOI '{potential_doi}' from URL: {url}"
                    )
                    return potential_doi

        return None

    def _clean_doi(self, doi: str) -> str:
        """Clean extracted DOI from URL artifacts."""
        # Remove common URL suffixes
        doi = re.sub(r"[?&#].*$", "", doi)  # Remove query params and fragments
        doi = re.sub(r"/$", "", doi)  # Remove trailing slash
        doi = doi.strip()

        # Handle URL encoding
        doi = doi.replace("%2F", "/")
        doi = doi.replace("%3A", ":")
        doi = doi.replace("%20", " ")

        return doi

    def _is_valid_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        if not doi:
            return False

        # Basic DOI pattern validation
        return bool(self.DOI_PATTERN.match(doi))

    def bibtex_entry2doi(self, entry: Dict) -> Optional[str]:
        """
        Extract DOI from a BibTeX entry's URL field.

        Args:
            entry: BibTeX entry dictionary

        Returns:
            DOI string if found, None otherwise
        """
        # Check if DOI already exists
        if entry.get("doi"):
            return None  # Already has DOI

        # Try to extract from URL field
        url = entry.get("url")
        if url:
            extracted_doi = self.extract_doi_from_url(url)
            if extracted_doi:
                logger.info(
                    f"Extracted DOI from URL for '{entry.get('title', 'Unknown')}': {extracted_doi}"
                )
                return extracted_doi

        return None

    def bibtex_entries2dois(self, entries: List[Dict]) -> Dict[str, str]:
        """
        Extract DOIs from multiple BibTeX entries.

        Args:
            entries: List of BibTeX entry dictionaries

        Returns:
            Dictionary mapping entry indices to extracted DOIs
        """
        results = {}

        for i, entry in enumerate(entries):
            extracted_doi = self.bibtex_entry2doi(entry)
            if extracted_doi:
                results[str(i)] = extracted_doi

        if results:
            logger.info(
                f"URLDOIExtractor: Extracted DOIs from {len(results)} entries"
            )

        return results

    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract all DOIs from arbitrary text.

        Args:
            text: Text to search for DOI URLs

        Returns:
            List of unique valid DOIs found
        """
        dois = set()

        # Find all potential URLs in text
        url_pattern = re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE)
        urls = url_pattern.findall(text)

        # Extract DOIs from each URL
        for url in urls:
            doi = self.extract_doi_from_url(url)
            if doi:
                dois.add(doi)

        return sorted(list(dois))


def main():
    """Test and demonstrate URLDOIExtractor functionality."""
    print("=" * 60)
    print("URLDOIExtractor Test Suite")
    print("=" * 60)

    extractor = URLDOIExtractor()

    # Test cases
    test_urls = [
        "https://doi.org/10.1002/hbm.26190",
        "http://dx.doi.org/10.1038/nature12373",
        "https://www.doi.org/10.1126/science.aao0702",
        "https://doi.wiley.com/10.1002/advs.202101329",
        "https://example.com/paper.html",  # No DOI
        "not-a-url",  # Invalid input
        "",  # Empty input
    ]

    print("\n1. Testing individual URL extraction:")
    for url in test_urls:
        result = extractor.extract_doi_from_url(url)
        status = "✅" if result else "❌"
        print(f"   {status} {url} → {result}")

    # Test BibTeX entry extraction
    print("\n2. Testing BibTeX entry extraction:")
    test_entries = [
        {
            "title": "Paper with DOI URL",
            "url": "https://doi.org/10.1002/hbm.26190",
            "year": "2023",
        },
        {
            "title": "Paper with existing DOI",
            "doi": "10.1038/existing",
            "url": "https://doi.org/10.1002/should-not-extract",
            "year": "2023",
        },
        {
            "title": "Paper with no DOI URL",
            "url": "https://example.com/paper.html",
            "year": "2023",
        },
    ]

    for i, entry in enumerate(test_entries):
        result = extractor.bibtex_entry2doi(entry)
        status = "✅" if result else "❌"
        print(f"   {status} Entry {i}: '{entry['title']}' → {result}")

    # Test batch extraction
    print("\n3. Testing batch extraction:")
    batch_results = extractor.bibtex_entries2dois(test_entries)
    print(
        f"   📊 Extracted DOIs from {len(batch_results)} out of {len(test_entries)} entries"
    )
    for entry_idx, doi in batch_results.items():
        print(f"     Entry {entry_idx}: {doi}")

    # Test text extraction
    print("\n4. Testing text extraction:")
    sample_text = """
    This paper references several works:
    https://doi.org/10.1126/science.aao0702 and
    http://dx.doi.org/10.1038/nature12373.
    Also see https://doi.org/10.1016/j.cell.2020.01.021 for details.
    """

    text_dois = extractor.extract_from_text(sample_text)
    print(f"   📄 Found {len(text_dois)} DOIs in text:")
    for doi in text_dois:
        print(f"     - {doi}")

    print("\n" + "=" * 60)
    print("✅ URLDOIExtractor test completed!")
    print("=" * 60)
    print("\nUsage patterns:")
    print("1. Single URL: extractor.extract_doi_from_url(url)")
    print("2. BibTeX entry: extractor.bibtex_entry2doi(entry)")
    print("3. Batch entries: extractor.bibtex_entries2dois(entries)")
    print("4. Text search: extractor.extract_from_text(text)")


if __name__ == "__main__":
    main()


# python -m scitex.scholar.doi.utils.url_doi_extractor

# EOF
