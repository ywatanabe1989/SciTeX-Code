#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 18:33:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_SourceManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_SourceManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Source management for DOI resolution."""

from typing import Dict, List, Optional, Type

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._ArXivSource import ArXivSource
from ._BaseDOISource import BaseDOISource
from ._CrossRefSource import CrossRefSource
from ._OpenAlexSource import OpenAlexSource
from ._PubMedSource import PubMedSource
from ._SemanticScholarSource import SemanticScholarSource
from ._URLDOISource import URLDOISource

logger = logging.getLogger(__name__)


class SourceManager:
    """Handles source instantiation, rotation, and lifecycle management.

    Responsibilities:
    - Source class mapping and registry management
    - Source instance creation and caching
    - Email configuration per source
    - Rate limit handler injection
    - Source-specific configuration
    """

    # Source registry
    SOURCE_CLASSES: Dict[str, Type[BaseDOISource]] = {
        "url_doi_source": URLDOISource,
        "crossref": CrossRefSource,
        "pubmed": PubMedSource,
        "openalex": OpenAlexSource,
        "semantic_scholar": SemanticScholarSource,
        "arxiv": ArXivSource,
    }

    def __init__(
        self,
        sources: List[str],
        # Emails
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        rate_limit_handler=None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize source manager.

        Args:
            sources: List of source names to manage
            rate_limit_handler: Rate limit handler to inject into sources
        """
        self.config = config or ScholarConfig()
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

        self.rate_limit_handler = rate_limit_handler

        # Initialize source instances cache
        self._source_instances: Dict[str, BaseDOISource] = {}

        logger.debug(f"SourceManager initialized with sources: {self.sources}")

    def get_source(self, name: str) -> Optional[BaseDOISource]:
        """Get or create source instance.

        Args:
            name: Source name

        Returns:
            Source instance or None if not found
        """
        if name not in self._source_instances:
            source_instance = self._create_source_instance(name)
            if source_instance:
                self._source_instances[name] = source_instance

        return self._source_instances.get(name)

    def _create_source_instance(
        self, source_name: str
    ) -> Optional[BaseDOISource]:
        """Create a new source instance with proper configuration.

        Args:
            source_name: Source name

        Returns:
            Configured source instance or None if source not found
        """
        source_class = self.SOURCE_CLASSES.get(source_name)
        if not source_class:
            logger.warning(f"Unknown source: {source_name}")
            return None

        try:
            # URLDOISource doesn't need email parameter
            if source_name == "url_doi_source":
                source_instance = source_class()
            else:
                email = self._get_email_for_source(source_name)
                source_instance = source_class(email)

            # Inject rate limit handler into source
            if self.rate_limit_handler:
                source_instance.set_rate_limit_handler(self.rate_limit_handler)

            # Configure source-specific rate limiting parameters
            self._configure_source_specific_settings(
                source_instance, source_name
            )

            logger.debug(f"Created source instance: {source_name}")
            return source_instance

        except Exception as e:
            logger.error(f"Error creating source {source_name}: {e}")
            return None

    def _get_email_for_source(self, source_name: str) -> str:
        """Get appropriate email for a source.

        Args:
            source_name: Source source_name

        Returns:
            Email address for the source
        """
        # Map source source_names to email config keys
        email_map = {
            "crossref": self.crossref_email,
            "pubmed": self.pubmed_email,
            "openalex": self.openalex_email,
            "semantic_scholar": self.semantic_scholar_email,
            "arxiv": self.arxiv_email,
        }
        return email_map[source_name]

    def _configure_source_specific_settings(
        self, source_instance: BaseDOISource, source_name: str
    ):
        """Configure source-specific settings like rate limits.

        Args:
            source_instance: Source instance to configure
            source_name: Source name for specific configuration
        """
        if not self.rate_limit_handler:
            return

        # Configure source-specific rate limiting parameters
        if source_name.lower() == "pubmed":
            # NCBI requires max 3 requests per second (0.35s delay)
            state = self.rate_limit_handler.get_source_state(
                source_name.lower()
            )
            state.base_delay = 0.35
            state.adaptive_delay = 0.35
            logger.debug(
                f"Configured PubMed-specific rate limiting: 0.35s delay"
            )

    def get_all_sources(self) -> List[BaseDOISource]:
        """Get all configured source instances.

        Returns:
            List of all configured source instances
        """
        return [
            self.get_source(source_name)
            for source_name in self.sources
            if self.get_source(source_name)
        ]

    def get_available_source_names(self) -> List[str]:
        """Get list of available source names.

        Returns:
            List of available source names
        """
        return list(self.SOURCE_CLASSES.keys())

    def is_source_available(self, name: str) -> bool:
        """Check if a source is available.

        Args:
            name: Source name to check

        Returns:
            True if source is available, False otherwise
        """
        return name in self.SOURCE_CLASSES

    def reload_source(self, name: str) -> Optional[BaseDOISource]:
        """Reload a source instance (useful for error recovery).

        Args:
            name: Source name to reload

        Returns:
            New source instance or None if creation failed
        """
        if name in self._source_instances:
            del self._source_instances[name]

        return self.get_source(name)

    def clear_source_cache(self):
        """Clear all cached source instances."""
        self._source_instances.clear()
        logger.debug("Cleared source instance cache")

    def get_source_statistics(self) -> Dict[str, Dict[str, any]]:
        """Get statistics for all managed sources.

        Returns:
            Dictionary mapping source names to their statistics
        """
        stats = {}
        for name in self.sources:
            source = self.get_source(name)
            if source and hasattr(source, "get_statistics"):
                stats[name] = source.get_statistics()
            else:
                stats[name] = {"status": "unavailable"}

        return stats

    def validate_source_configuration(self) -> Dict[str, any]:
        """Validate source configuration and return validation results.

        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "source_status": {},
        }

        for name in self.sources:
            if not self.is_source_available(name):
                validation["errors"].append(f"Unknown source: {name}")
                validation["valid"] = False
                validation["source_status"][name] = "unknown"
                continue

            try:
                source = self.get_source(name)
                if source:
                    validation["source_status"][name] = "available"
                else:
                    validation["warnings"].append(
                        f"Could not create source: {name}"
                    )
                    validation["source_status"][name] = "creation_failed"
            except Exception as e:
                validation["errors"].append(f"Error with source {name}: {e}")
                validation["source_status"][name] = "error"

        return validation


if __name__ == "__main__":
    # # Test email configuration
    # email_config = {
    #     "crossref": "test@example.com",
    #     "pubmed": "test@example.com",
    #     "openalex": "test@example.com",
    #     "semantic_scholar": "test@example.com",
    #     "arxiv": "test@example.com",
    # }

    # # Initialize source manager
    # manager = SourceManager(
    #     sources=["crossref", "pubmed", "url_doi_source"],
    #     email_config=email_config,
    # )
    manager = SourceManager(sources=["crossref", "pubmed", "url_doi_source"])

    print("Source Manager Test:")
    print(f"Available sources: {manager.get_available_source_names()}")
    print(f"Configured sources: {manager.sources}")

    # Test source creation
    crossref_source = manager.get_source("crossref")
    print(f"CrossRef source created: {crossref_source is not None}")

    # Test validation
    validation = manager.validate_source_configuration()
    print(f"Configuration valid: {validation['valid']}")
    print(f"Source status: {validation['source_status']}")

    # Test source statistics
    stats = manager.get_source_statistics()
    print(f"Source statistics: {stats}")


# python -m scitex.scholar.metadata.doi.sources._SourceManager

# EOF
