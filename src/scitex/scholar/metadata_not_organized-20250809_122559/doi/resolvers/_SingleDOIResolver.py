#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 12:21:07 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/resolvers/_SingleDOIResolver.py
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
from typing import Any, Dict, List, Optional

from scitex import logging

from ..core import ConfigurationResolver, ResultCacheManager, SourceManager
from ..sources._SourceRotationManager import SourceRotationManager
from ..strategies import ResolutionOrchestrator
from ..utils._RateLimitHandler import RateLimitHandler

logger = logging.getLogger(__name__)


class SingleDOIResolver:
    """Clean, optimized DOI resolver with configurable sources.

    Now uses focused single-responsibility components:
    - SourceManager: Source instantiation, rotation, and lifecycle management
    - ResultCacheManager: DOI caching, result persistence, and retrieval
    - ConfigurationResolver: Email resolution, source configuration, validation
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
        project: str = "MASTER",
        # Dependency injection for testability and modularity
        config_resolver: Optional[ConfigurationResolver] = None,
        source_manager: Optional[SourceManager] = None,
        cache_manager: Optional[ResultCacheManager] = None,
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
            config_resolver: ConfigurationResolver instance (created if None)
            source_manager: SourceManager instance (created if None)
            cache_manager: ResultCacheManager instance (created if None)
        """
        # Initialize configuration resolver first
        self.config_resolver = config_resolver or ConfigurationResolver(config)
        self.config = self.config_resolver.config

        # Resolve all configuration using the resolver
        resolved_config = self.config_resolver.resolve_all_configuration(
            email_crossref,
            email_pubmed,
            email_openalex,
            email_semantic_scholar,
            email_arxiv,
            sources,
            project,
        )

        # Extract resolved values
        self.email_config = resolved_config["email_config"]
        self.sources = resolved_config["sources"]
        self.project = resolved_config["project"]
        self.api_keys = resolved_config["api_keys"]
        self.rate_limit_config = resolved_config["rate_limit_config"]
        self.enrichment_config = resolved_config["enrichment_config"]

        # Set up backward compatibility properties
        self.email_crossref = self.email_config["crossref"]
        self.email_pubmed = self.email_config["pubmed"]
        self.email_openalex = self.email_config["openalex"]
        self.email_semantic_scholar = self.email_config["semantic_scholar"]
        self.email_arxiv = self.email_config["arxiv"]

        # Initialize rate limit handling
        self.rate_limit_handler = RateLimitHandler(
            state_file=self.rate_limit_config["state_file"]
        )
        self.source_rotation_manager = SourceRotationManager(
            self.rate_limit_handler
        )

        # Initialize source manager
        self.source_manager = source_manager or SourceManager(
            sources=self.sources,
            email_config=self.email_config,
            rate_limit_handler=self.rate_limit_handler,
        )

        # Initialize result cache manager
        self.cache_manager = cache_manager or ResultCacheManager(
            config=self.config, project=self.project
        )

        # Initialize ResolutionOrchestrator with existing components
        self.orchestrator = ResolutionOrchestrator(
            config=self.config,
            project=self.project,
            sources=self.sources,
            rate_limit_handler=self.rate_limit_handler,
            source_rotation_manager=self.source_rotation_manager,
            email_config=self.email_config,
            enrichment_config=self.enrichment_config,
        )

        # Log configuration for debugging
        logger.debug(
            f"SingleDOIResolver initialized with sources: {self.sources}"
        )
        logger.debug(f"Email configuration: {list(self.email_config.keys())}")
        logger.debug(
            f"Rate limit state file: {self.rate_limit_config['state_file']}"
        )
        logger.info(
            "SingleDOIResolver initialized with focused single-responsibility components"
        )

    # Delegate methods to maintain backward compatibility

    def _get_source(self, name: str):
        """Get or create source instance (delegated to source manager)."""
        return self.source_manager.get_source(name)

    def _check_scholar_library(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Check if DOI already exists in master Scholar library (delegated to cache manager)."""
        return self.cache_manager.check_scholar_library(title, year)

    def _save_to_scholar_library(
        self,
        title: str,
        doi: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: str = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
    ):
        """Save resolved DOI to master Scholar library (delegated to cache manager)."""
        return self.cache_manager.save_to_scholar_library(
            title, doi, year, authors, source, metadata, bibtex_source
        )

    def _save_unresolved_entry(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        bibtex_source: Optional[str] = None,
    ):
        """Save unresolved entry to master Scholar library (delegated to cache manager)."""
        return self.cache_manager.save_unresolved_entry(
            title, year, authors, bibtex_source
        )

    def copy_bibtex_to_library(
        self, bibtex_path: str, project_name: Optional[str] = None
    ) -> str:
        """Copy BibTeX file to Scholar library for reference (delegated to cache manager)."""
        return self.cache_manager.copy_bibtex_to_library(
            bibtex_path, project_name
        )

    def get_unresolved_entries(
        self, project_name: Optional[str] = None
    ) -> List[Dict]:
        """Get list of unresolved entries from Scholar library (delegated to cache manager)."""
        return self.cache_manager.get_unresolved_entries(project_name)

    def _create_project_symlink(self, paper_id: str, readable_name: str):
        """Create project symlink to master paper directory (delegated to cache manager)."""
        return self.cache_manager._create_project_symlink(
            paper_id, readable_name
        )

    def _ensure_project_symlink(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ):
        """Ensure project symlink exists for a paper (delegated to cache manager)."""
        return self.cache_manager._ensure_project_symlink(title, year, authors)

    # Core resolution methods (main business logic)

    async def resolve_async(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        skip_cache: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Resolve DOI asynchronously with caching."""
        # Check Scholar library cache first (unless skipping cache)
        if not skip_cache:
            cached_doi = self._check_scholar_library(title, year)
            if cached_doi:
                logger.info(f"DOI found in cache: {cached_doi}")
                return {
                    "doi": cached_doi,
                    "source": "scholar_library_cache",
                    "title": title,
                }

        # Use ResolutionOrchestrator for the actual resolution
        try:
            result = await self.orchestrator.resolve_doi_async(
                title=title,
                year=year,
                authors=authors,
                sources=sources or self.sources,
            )

            if result and result.get("doi"):
                # Save to Scholar library cache
                self._save_to_scholar_library(
                    title=title,
                    doi=result["doi"],
                    year=year,
                    authors=authors,
                    source=result.get("source"),
                    metadata=result.get("metadata"),
                )

                logger.success(f"DOI resolved and cached: {result['doi']}")
                return result
            else:
                # Save as unresolved entry
                self._save_unresolved_entry(title, year, authors)
                logger.warning(f"DOI resolution failed for: {title[:50]}...")
                return None

        except Exception as e:
            logger.error(f"Error during DOI resolution: {e}")
            return None

    def resolve(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
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
                    self.resolve_async(
                        title, year, authors, sources, skip_cache
                    )
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self.resolve_async(title, year, authors, sources, skip_cache)
            )

    def get_abstract(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Get abstract for a paper using ResolutionOrchestrator."""
        try:
            # Use the main resolve_async method to get metadata with abstract
            result = asyncio.run(
                self.orchestrator.resolve_async(
                    title=title,
                    year=year,
                    authors=authors,
                    enable_enrichment=True,
                )
            )
            if result and result.get("metadata"):
                return result["metadata"].get("abstract")
            return None
        except Exception as e:
            logger.error(f"Error getting abstract: {e}")
            return None

    def get_comprehensive_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata using ResolutionOrchestrator."""
        try:
            # Use the main resolve_async method to get complete metadata
            result = asyncio.run(
                self.orchestrator.resolve_async(
                    title=title,
                    year=year,
                    authors=authors,
                    enable_enrichment=True,
                )
            )
            if result:
                # Return the metadata portion, removing orchestrator-specific fields
                metadata = result.get("metadata", {})
                if metadata:
                    return metadata
                # If no separate metadata, return the core fields
                return {
                    "doi": result.get("doi"),
                    "title": title,
                    "year": year,
                    "authors": authors,
                    "source": result.get("source"),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting comprehensive metadata: {e}")
            return None

    # Utility methods

    def extract_dois_from_text(self, text: str) -> List[str]:
        """Extract DOIs from text using URL extractor source."""
        try:
            url_doi_source = self.source_manager.get_source("url_doi_source")
            if url_doi_source and hasattr(
                url_doi_source, "extract_dois_from_text"
            ):
                return url_doi_source.extract_dois_from_text(text)
            return []
        except Exception as e:
            logger.error(f"Error extracting DOIs from text: {e}")
            return []

    def validate_doi(self, doi: str) -> bool:
        """Validate DOI format using URL extractor source."""
        try:
            url_doi_source = self.source_manager.get_source("url_doi_source")
            if url_doi_source and hasattr(url_doi_source, "validate_doi"):
                return url_doi_source.validate_doi(doi)

            # Fallback validation
            import re

            doi_pattern = r"^10\.\d{4,9}/[-._;()/:\w\[\]]+$"
            return bool(re.match(doi_pattern, doi))
        except Exception as e:
            logger.error(f"Error validating DOI: {e}")
            return False

    # Statistics and monitoring

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get comprehensive workflow statistics."""
        try:
            # Get statistics from all components
            source_stats = self.source_manager.get_source_statistics()
            cache_stats = self.cache_manager.get_cache_statistics()
            rate_limit_stats = self.rate_limit_handler.get_statistics()

            # Get orchestrator statistics if available
            orchestrator_stats = {}
            if hasattr(self.orchestrator, "get_statistics"):
                orchestrator_stats = self.orchestrator.get_statistics()

            return {
                "sources": source_stats,
                "cache": cache_stats,
                "rate_limiting": rate_limit_stats,
                "orchestrator": orchestrator_stats,
                "configuration": self.config_resolver.get_configuration_summary(
                    self.email_config,
                    self.sources,
                    self.project,
                    self.api_keys,
                ),
            }
        except Exception as e:
            logger.error(f"Error getting workflow statistics: {e}")
            return {"error": str(e)}

    def reset_statistics(self) -> None:
        """Reset all statistics."""
        try:
            self.rate_limit_handler.reset_statistics()
            if hasattr(self.orchestrator, "reset_statistics"):
                self.orchestrator.reset_statistics()
            logger.info("Statistics reset")
        except Exception as e:
            logger.error(f"Error resetting statistics: {e}")

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate complete resolver configuration."""
        try:
            # Get validation from all components
            config_validation = self.config_resolver.validate_configuration(
                self.email_config, self.sources, self.project
            )
            source_validation = (
                self.source_manager.validate_source_configuration()
            )

            # Combine validations
            combined_validation = {
                "valid": config_validation["valid"]
                and source_validation["valid"],
                "warnings": config_validation["warnings"]
                + source_validation["warnings"],
                "errors": config_validation["errors"]
                + source_validation["errors"],
                "configuration": config_validation,
                "sources": source_validation,
            }

            return combined_validation
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {"valid": False, "errors": [str(e)]}


if __name__ == "__main__":
    import asyncio

    async def main():
        """Example usage of refactored SingleDOIResolver."""

        print("=" * 60)
        print("Refactored SingleDOIResolver Test")
        print("=" * 60)

        # Initialize resolver
        resolver = SingleDOIResolver(
            email_crossref="test@example.com",
            email_pubmed="test@example.com",
            sources=["url_doi_source", "crossref"],
            project="test_project",
        )

        # Validate configuration
        validation = resolver.validate_configuration()
        print(f"Configuration valid: {validation['valid']}")
        if validation["warnings"]:
            print(f"Warnings: {validation['warnings']}")

        # Test resolution (with a simple example)
        print("\nTesting DOI resolution...")
        test_title = "Machine Learning Applications in Bioinformatics"

        try:
            result = await resolver.resolve_async(title=test_title, year=2023)

            if result:
                print(f"✅ DOI found: {result.get('doi', 'None')}")
                print(f"✅ Source: {result.get('source', 'Unknown')}")
            else:
                print("❌ No DOI found")

        except Exception as e:
            print(f"❌ Error during resolution: {e}")

        # Get statistics
        stats = resolver.get_workflow_statistics()
        print(f"\nWorkflow Statistics:")
        print(f"Cache stats: {stats.get('cache', {})}")
        print(f"Sources configured: {len(stats.get('sources', {}))}")

        print("\n✅ Refactored SingleDOIResolver test completed!")

    if __name__ == "__main__":
        asyncio.run(main())

# EOF
