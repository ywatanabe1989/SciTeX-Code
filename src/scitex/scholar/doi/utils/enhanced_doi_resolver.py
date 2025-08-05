#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 08:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/utils/enhanced_doi_resolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/utils/enhanced_doi_resolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Enhanced DOI Resolver with Phase 1 utilities integration.

This module extends the existing DOI resolver with immediate recovery utilities:
1. URLDOIExtractor - Extract DOIs from URL fields
2. PubMedConverter - Convert PMIDs to DOIs  
3. TextNormalizer - Improve search accuracy with text normalization

The integration is designed to be backwards compatible and non-disruptive.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path

from scitex import logging
from .url_doi_extractor import URLDOIExtractor
from .pubmed_converter import PubMedConverter
from .text_normalizer import TextNormalizer
from .._SingleDOIResolver import SingleDOIResolver

logger = logging.getLogger(__name__)


class EnhancedSingleDOIResolver:
    """
    Enhanced DOI resolver that integrates Phase 1 utilities for immediate recovery.
    
    Maintains full backward compatibility with existing SingleDOIResolver interface.
    """
    
    def __init__(
        self,
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,  
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        sources: Optional[List[str]] = None,
        config: Optional[Any] = None,
        project: str = "master",
        enable_utilities: bool = True,
        ascii_fallback: bool = False,
    ):
        """
        Initialize enhanced DOI resolver.
        
        Args:
            email_crossref: Email for CrossRef API
            email_pubmed: Email for PubMed API
            email_openalex: Email for OpenAlex API  
            email_semantic_scholar: Email for Semantic Scholar API
            email_arxiv: Email for ArXiv API
            sources: List of source names to use
            config: ScholarConfig object
            project: Project name for Scholar library storage
            enable_utilities: Enable Phase 1 utilities (default: True)
            ascii_fallback: Enable ASCII fallback for text normalization
        """
        # Initialize the base resolver
        self.base_resolver = SingleDOIResolver(
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            email_arxiv=email_arxiv,
            sources=sources,
            config=config,
            project=project,
        )
        
        # Initialize Phase 1 utilities
        self.enable_utilities = enable_utilities
        
        if self.enable_utilities:
            self.url_extractor = URLDOIExtractor()
            self.pubmed_converter = PubMedConverter(
                email=email_pubmed or self.base_resolver.email_pubmed,
                api_key=None  # Could be added to config later
            )
            self.text_normalizer = TextNormalizer(ascii_fallback=ascii_fallback)
            
            logger.debug("Enhanced DOI resolver initialized with Phase 1 utilities")
        else:
            self.url_extractor = None
            self.pubmed_converter = None
            self.text_normalizer = None
            
            logger.debug("Enhanced DOI resolver initialized without utilities (compatibility mode)")
    
    # Delegate properties to base resolver
    @property
    def config(self):
        return self.base_resolver.config
        
    @property
    def project(self):
        return self.base_resolver.project
        
    @property
    def sources(self):
        return self.base_resolver.sources
        
    def _try_utility_extraction(self, entry: Dict) -> Optional[Dict]:
        """
        Try to extract DOI using Phase 1 utilities.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            Dict with 'doi' and 'source' keys if found, None otherwise
        """
        if not self.enable_utilities:
            return None
            
        # Try URL extraction first (fastest)
        doi = self.url_extractor.extract_from_bibtex_entry(entry)
        if doi:
            logger.info(f"Phase 1 recovery via URL extraction: {doi}")
            return {"doi": doi, "source": "url_extraction"}
            
        # Try PubMed conversion (network call but very reliable)
        doi = self.pubmed_converter.extract_from_bibtex_entry(entry)
        if doi:
            logger.info(f"Phase 1 recovery via PubMed conversion: {doi}")
            return {"doi": doi, "source": "pubmed_conversion"}
            
        return None
        
    def _normalize_search_parameters(
        self,
        title: str,
        authors: Optional[List[str]] = None
    ) -> tuple[str, Optional[List[str]]]:
        """
        Normalize search parameters for better accuracy.
        
        Args:
            title: Paper title
            authors: Author list
            
        Returns:
            Tuple of (normalized_title, normalized_authors)
        """
        if not self.enable_utilities or not self.text_normalizer:
            return title, authors
            
        # Normalize title
        normalized_title = self.text_normalizer.normalize_title(title)
        
        # Normalize authors
        normalized_authors = None
        if authors:
            normalized_authors = [
                self.text_normalizer.normalize_author_name(author)
                for author in authors
            ]
            
        # Log if changes were made
        if normalized_title != title:
            logger.debug(f"Title normalized: '{title}' → '{normalized_title}'")
            
        if authors and normalized_authors and normalized_authors != authors:
            logger.debug(f"Authors normalized: {authors} → {normalized_authors}")
            
        return normalized_title, normalized_authors
        
    async def resolve_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,  
        sources: Optional[List[str]] = None,
        entry: Optional[Dict] = None,  # New parameter for utility extraction
    ) -> Optional[Dict]:
        """
        Enhanced resolve with Phase 1 utilities integration.
        
        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)  
            sources: Specific sources to use (optional)
            entry: Full BibTeX entry for utility extraction (optional)
            
        Returns:
            Dict with 'doi' and 'source' keys if found, None otherwise
        """
        # Phase 1: Try utility extraction if entry is provided
        if entry and self.enable_utilities:
            utility_result = self._try_utility_extraction(entry)
            if utility_result:
                # Save to Scholar library for persistence
                self.base_resolver._save_to_scholar_library(
                    title, 
                    utility_result['doi'], 
                    year, 
                    authors, 
                    utility_result['source'],
                    {}  # No additional metadata from utilities
                )
                return utility_result
        
        # Phase 2: Normalize search parameters for better accuracy
        normalized_title, normalized_authors = self._normalize_search_parameters(
            title, authors
        )
        
        # Phase 3: Use base resolver with normalized parameters
        result = await self.base_resolver.resolve_async(
            title=normalized_title,
            year=year,
            authors=normalized_authors,
            sources=sources,
        )
        
        return result
        
    def resolve(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        entry: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Synchronous version of enhanced resolve.
        
        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            sources: Specific sources to use (optional)
            entry: Full BibTeX entry for utility extraction (optional)
            
        Returns:
            DOI string if found, None otherwise
        """
        import asyncio
        
        try:
            # Get the current event loop or create a new one
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        result = loop.run_until_complete(
            self.resolve_async(title, year, authors, sources, entry)
        )
        
        # Return just the DOI string for backward compatibility
        if result and isinstance(result, dict):
            return result.get('doi')
        return result
    
    # Delegate all other methods to base resolver
    def __getattr__(self, name):
        """Delegate unknown attributes to base resolver."""
        return getattr(self.base_resolver, name)
        
    def get_enhancement_stats(self) -> Dict[str, int]:
        """
        Get statistics about Phase 1 utility usage.
        
        Returns:
            Dictionary with utility usage statistics
        """
        if not self.enable_utilities:
            return {"utilities_enabled": False}
            
        # This would need to be implemented with proper tracking
        # For now, return basic info
        return {
            "utilities_enabled": True,
            "url_extractor_ready": self.url_extractor is not None,
            "pubmed_converter_ready": self.pubmed_converter is not None,
            "text_normalizer_ready": self.text_normalizer is not None,
        }


def main():
    """Test and demonstrate EnhancedSingleDOIResolver functionality."""
    print("=" * 60)
    print("EnhancedSingleDOIResolver Test Suite")
    print("=" * 60)
    
    # Test with utilities enabled
    print("\n1. Testing with utilities enabled:")
    enhanced_resolver = EnhancedSingleDOIResolver(
        email_crossref="test@example.com",
        enable_utilities=True,
        ascii_fallback=False
    )
    
    stats = enhanced_resolver.get_enhancement_stats()
    print(f"   Enhancement stats: {stats}")
    
    # Test utility extraction
    print("\n2. Testing utility extraction:")
    test_entries = [
        {
            "title": "Test Paper with URL DOI",
            "url": "https://doi.org/10.1002/hbm.26190",
            "year": "2023"
        },
        {
            "title": "Test Paper with PMID",
            "pmid": "25821343",
            "year": "2015"
        },
        {
            "title": "Test Paper with LaTeX",
            "title": r"Paper by H{\"u}lsemann",
            "author": r"H{\"u}lsemann, Klaus",
            "year": "2020"
        }
    ]
    
    for i, entry in enumerate(test_entries):
        print(f"\n   Entry {i+1}: {entry.get('title', 'No title')}")
        
        # Try utility extraction
        utility_result = enhanced_resolver._try_utility_extraction(entry)
        if utility_result:
            print(f"   ✅ Utility extraction: {utility_result['doi']} (via {utility_result['source']})")
        else:
            print(f"   ❌ Utility extraction: No DOI found")
            
        # Test text normalization
        title = entry.get('title', '')
        authors = [entry.get('author', '')] if entry.get('author') else None
        
        norm_title, norm_authors = enhanced_resolver._normalize_search_parameters(title, authors)
        
        if norm_title != title:
            print(f"   📝 Title normalized: '{title}' → '{norm_title}'")
        if authors and norm_authors and norm_authors != authors:
            print(f"   📝 Authors normalized: {authors} → {norm_authors}")
    
    # Test compatibility mode
    print("\n3. Testing compatibility mode (utilities disabled):")
    compat_resolver = EnhancedSingleDOIResolver(
        email_crossref="test@example.com",
        enable_utilities=False
    )
    
    compat_stats = compat_resolver.get_enhancement_stats()
    print(f"   Compatibility stats: {compat_stats}")
    
    print("\n" + "=" * 60)
    print("✅ EnhancedSingleDOIResolver test completed!")
    print("=" * 60)
    print("\nUsage patterns:")
    print("1. Enhanced mode: EnhancedSingleDOIResolver(enable_utilities=True)")
    print("2. Compatibility mode: EnhancedSingleDOIResolver(enable_utilities=False)")
    print("3. With entry: resolver.resolve_async(title, year, authors, entry=entry)")
    print("4. Standard usage: resolver.resolve_async(title, year, authors)")


if __name__ == "__main__":
    main()


# python -m scitex.scholar.doi.utils.enhanced_doi_resolver

# EOF