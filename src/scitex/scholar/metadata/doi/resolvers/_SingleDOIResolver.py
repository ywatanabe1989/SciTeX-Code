#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 09:56:56 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/resolvers/_SingleDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/resolvers/_SingleDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Clean, optimized DOI resolver with focused single-responsibility components."""

import asyncio
import re
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._LibraryCacheManager import LibraryCacheManager

from ..sources._SourceManager import SourceManager
from ..sources._SourceResolutionStrategy import SourceResolutionStrategy
from ..sources._SourceRotationManager import SourceRotationManager
from ..utils import PubMedConverter, RateLimitHandler, TextNormalizer, URLDOIExtractor

# from ..utils._RateLimitHandler import RateLimitHandler

logger = logging.getLogger(__name__)


class SingleDOIResolver:
    """Clean, optimized DOI resolver with configurable sources.

    Now uses focused single-responsibility components:
    - SourceManager: Source instantiation, rotation, and lifecycle management
    - LibraryCacheManager: DOI caching, result persistence, and retrieval
    - ConfigurationResolver: Email resolution, source configuration, validation
    """

    def __init__(
        self,
        sources: Optional[List[str]] = None,
        project: str = None,
        # Emails
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        # API Keys
        semantic_scholar_api_key: str = None,
        crossref_api_key: str = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize resolver with specified sources and dependency injection.

        Args:
            email_crossref: Email for CrossRef API (None to use config)
            email_pubmed: Email for PubMed API (None to use config)
            email_openalex: Email for OpenAlex API (None to use config)
            email_semantic_scholar: Email for Semantic Scholar API (None to use config)
            email_arxiv: Email for ArXiv API (None to use config)
            sources: List of source names to use (None for default sources)
            config: ScholarConfig object (None to create default)
            project: Project name for Scholar library storage (default: "master")
            # config_resolver: ConfigurationResolver instance (created if None)
            source_manager: SourceManager instance (created if None)
            cache_manager: LibraryCacheManager instance (created if None)
        """
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self.sources = self.config.resolve("sources", sources)

        # Emails
        self.crossref_email = self.config.resolve(
            "crossref_email", email_crossref
        )
        self.pubmed_email = self.config.resolve("pubmed_email", email_pubmed)
        self.openalex_email = self.config.resolve(
            "openalex_email", email_openalex
        )
        self.semantic_scholar_email = self.config.resolve(
            "semantic_scholar_email",
            email_semantic_scholar,
        )
        self.arxiv_email = self.config.resolve("arxiv_email", email_arxiv)

        # API Keys
        self.semantic_scholar_api_key = self.config.resolve(
            "semantic_scholar_api_key", semantic_scholar_api_key
        )
        self.crossref_api_key = self.config.resolve(
            "crossref_api_key", crossref_api_key
        )

        # Utilities
        self.url_doi_extractor = URLDOIExtractor()
        self.pubmed_converter = PubMedConverter(email=self.pubmed_email)
        self.text_normalizer = TextNormalizer()

        # Initialize classes
        self._rate_limit_handler = RateLimitHandler()
        self._source_rotation_manager = SourceRotationManager(
            self._rate_limit_handler
        )
        self._source_manager = SourceManager(
            sources=self.sources,
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            email_arxiv=email_arxiv,
            rate_limit_handler=self._rate_limit_handler,
        )

        self._source_strategy = SourceResolutionStrategy(
            sources=self.sources,
            rate_limit_handler=self._rate_limit_handler,
            email_crossref=email_crossref,
            email_pubmed=email_pubmed,
            email_openalex=email_openalex,
            email_semantic_scholar=email_semantic_scholar,
            email_arxiv=email_arxiv,
        )

        self._library_cache_manager = LibraryCacheManager(
            project=self.project, config=self.config
        )

    async def metadata2doi_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_entry: Optional[Dict] = None,
        skip_cache: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve DOI asynchronously with caching.

        Args:
            title: Paper title
            year: Publication year (optional)
            authors: Author list (optional)
            sources: Specific sources to use (optional)
            bibtex_entry: Full BibTeX bibtex_entry for utility extraction (optional)

        Returns:
            Dict with 'doi' and 'source' keys if found, None otherwise
        """

        # Phase 0: Normalize search parameters for better accuracy
        title, authors = self._normalize_search_parameters(title, authors)

        # Check cache first unless explicitly skipped
        if not skip_cache:
            cached_doi = self._library_cache_manager.is_doi_stored(
                title,
                year,
            )
            if cached_doi:
                logger.info(f"DOI found in cache: {cached_doi}")
                return {"doi": cached_doi, "source": "cache", "title": title}

        # Phase 1: Try utility extraction if bibtex_entry is provided
        if bibtex_entry:
            utility_result = self._try_utility_extraction(bibtex_entry)
            if utility_result:
                # Save to Scholar library for persistence
                self._library_cache_manager.save_entry(
                    title=title,
                    doi=utility_result["doi"],
                    year=year,
                    authors=authors,
                    source=utility_result["source"],
                    metadata=None,  # No additional metadata from utilities
                    bibtex_source=None,
                )
                return utility_result

        # Phase 2: Resolve from sources
        result = await self._source_strategy.metadata2metadata_async(
            title=title, year=year, authors=authors
        )

        # Cache successful or failed resolution
        self._library_cache_manager.save_entry(
            title=title,
            doi=result.get("doi") if result else None,
            year=year,
            authors=authors,
            source=result.get("source") if result else None,
            metadata=result.get("metadata") if result else None,
            bibtex_source=result.get("bibtex_source") if result else None,
        )

        return result

    def metadata2doi(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_entry: Optional[Dict] = None,
        skip_cache: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Synchronous wrapper for resolve_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Cannot use asyncio.run() in running loop
                logger.warning(
                    "Cannot run synchronous resolve in async context. Use resolve_async() instead."
                )
                return None
            else:
                return loop.run_until_complete(
                    self.metadata2doi_async(
                        title, year, authors, bibtex_entry, skip_cache
                    )
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self.metadata2doi_async(
                    title, year, authors, bibtex_entry, skip_cache
                )
            )

    def text2dois(self, text: str) -> List[str]:
        """Extract DOIs from text using URL extractor source."""
        try:
            url_doi_source = self._source_manager.get_source("url_doi_source")
            if url_doi_source and hasattr(
                url_doi_source, "extract_dois_from_text"
            ):
                return url_doi_source.extract_dois_from_text(text)
            return []
        except Exception as e:
            logger.error(f"Error extracting DOIs from text: {e}")
            return []

    def _validate_doi(self, input_str: str) -> bool:
        """Check if input string is a DOI."""
        return bool(re.match(r"^10\.\d{4,}/[^\s]+$", input_str))

    def _try_utility_extraction(self, bibtex_entry: Dict) -> Optional[Dict]:
        """
        Try to extract DOI using Phase 1 utilities.

        Args:
            bibtex_entry: BibTeX bibtex_entry dictionary

        Returns:
            Dict with 'doi' and 'source' keys if found, None otherwise
        """
        # Try URL extraction first (fastest)
        doi = self.url_doi_extractor.bibtex_entry2doi(bibtex_entry)
        if doi:
            logger.info(f"Phase 1 recovery via URL extraction: {doi}")
            return {"doi": doi, "source": "url_extraction"}

        # Try PubMed conversion (network call but very reliable)
        doi = self.pubmed_converter.bibtex_entry2doi(bibtex_entry)
        if doi:
            logger.info(f"Phase 1 recovery via PubMed conversion: {doi}")
            return {"doi": doi, "source": "pubmed_conversion"}

        return None

    def _normalize_search_parameters(
        self, title: str, authors: Optional[List[str]] = None
    ) -> tuple[str, Optional[List[str]]]:
        """
        Normalize search parameters for better accuracy.

        Args:
            title: Paper title
            authors: Author list

        Returns:
            Tuple of (normalized_title, normalized_authors)
        """

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
            logger.debug(
                f"Authors normalized: {authors} → {normalized_authors}"
            )

        return normalized_title, normalized_authors

    # def _get_workflow_statistics(self) -> Dict[str, Any]:
    #     """Get comprehensive workflow statistics."""
    #     try:
    #         # Get statistics from all components
    #         source_stats = self._source_manager.get_source_statistics()
    #         cache_stats = self._library_cache_manager.get_cache_statistics()
    #         rate_limit_stats = self._rate_limit_handler.get_statistics()

    #         # Get orchestrator statistics if available
    #         orchestrator_stats = {}
    #         if hasattr(self.orchestrator, "get_statistics"):
    #             orchestrator_stats = self.orchestrator.get_statistics()

    #         return {
    #             "sources": source_stats,
    #             "cache": cache_stats,
    #             "rate_limiting": rate_limit_stats,
    #             "orchestrator": orchestrator_stats,
    #             "configuration": self.config_resolver.get_configuration_summary(
    #                 self.email_config,
    #                 self.sources,
    #                 self.project,
    #                 self.api_keys,
    #             ),
    #         }
    #     except Exception as e:
    #         logger.error(f"Error getting workflow statistics: {e}")
    #         return {"error": str(e)}

    # def reset_statistics(self) -> None:
    #     """Reset all statistics."""
    #     try:
    #         self._rate_limit_handler.reset_statistics()
    #         if hasattr(self.orchestrator, "reset_statistics"):
    #             self.orchestrator.reset_statistics()
    #         logger.info("Statistics reset")
    #     except Exception as e:
    #         logger.error(f"Error resetting statistics: {e}")

    # def _validate_configuration(self) -> Dict[str, Any]:
    #     """Validate complete resolver configuration."""
    #     try:
    #         # Get validation from all components
    #         config_validation = self.config_resolver.validate_configuration(
    #             self.email_config, self.sources, self.project
    #         )
    #         source_validation = (
    #             self._source_manager.validate_source_configuration()
    #         )

    #         # Combine validations
    #         combined_validation = {
    #             "valid": config_validation["valid"]
    #             and source_validation["valid"],
    #             "warnings": config_validation["warnings"]
    #             + source_validation["warnings"],
    #             "errors": config_validation["errors"]
    #             + source_validation["errors"],
    #             "configuration": config_validation,
    #             "sources": source_validation,
    #         }

    #         return combined_validation
    #     except Exception as e:
    #         logger.error(f"Error validating configuration: {e}")
    #         return {"valid": False, "errors": [str(e)]}


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage of refactored SingleDOIResolver."""

        single_doi_resolver = SingleDOIResolver()
        found_doi = await single_doi_resolver.metadata2doi_async(
            title="Direct modulation index: A measure of phase amplitude coupling for neurophysiology data",
            year=None,
        )
        dir(single_doi_resolver)
        __import__("ipdb").set_trace()

    if __name__ == "__main__":
        asyncio.run(main())

# python -m scitex.scholar.metadata.doi.resolvers._SingleDOIResolver

# EOF
