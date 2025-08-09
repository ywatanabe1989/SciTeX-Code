#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 02:54:43 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/core/_SourceManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/core/_SourceManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Source management for DOI resolution."""

from typing import Dict, List, Optional, Type

from scitex import logging

from ..sources import (
    ArXivSource,
    BaseDOISource,
    CrossRefSource,
    OpenAlexSource,
    PubMedSource,
    SemanticScholarSource,
    URLDOISource,
)

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

    # Default source order (URL extractor first for immediate recovery)
    DEFAULT_SOURCES = [
        "url_doi_source",
        "crossref",
        "semantic_scholar",
        "pubmed",
        "openalex",
    ]

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
        email_config: Dict[str, str],
        rate_limit_handler=None,
    ):
        """Initialize source manager.

        Args:
            sources: List of source names to manage
            email_config: Dictionary mapping source names to email addresses
            rate_limit_handler: Rate limit handler to inject into sources
        """
        self.sources = sources or self.DEFAULT_SOURCES
        self.email_config = email_config or {}
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

    def _create_source_instance(self, name: str) -> Optional[BaseDOISource]:
        """Create a new source instance with proper configuration.

        Args:
            name: Source name

        Returns:
            Configured source instance or None if source not found
        """
        source_class = self.SOURCE_CLASSES.get(name)
        if not source_class:
            logger.warning(f"Unknown source: {name}")
            return None

        try:
            # URLDOISource doesn't need email parameter
            if name == "url_doi_source":
                source_instance = source_class()
            else:
                email = self._get_email_for_source(name)
                source_instance = source_class(email)

            # Inject rate limit handler into source
            if self.rate_limit_handler:
                source_instance.set_rate_limit_handler(self.rate_limit_handler)

            # Configure source-specific rate limiting parameters
            self._configure_source_specific_settings(source_instance, name)

            logger.debug(f"Created source instance: {name}")
            return source_instance

        except Exception as e:
            logger.error(f"Error creating source {name}: {e}")
            return None

    def _get_email_for_source(self, name: str) -> str:
        """Get appropriate email for a source.

        Args:
            name: Source name

        Returns:
            Email address for the source
        """
        # Map source names to email config keys
        email_map = {
            "crossref": "crossref",
            "pubmed": "pubmed",
            "openalex": "openalex",
            "semantic_scholar": "semantic_scholar",
            "arxiv": "arxiv",
        }

        config_key = email_map.get(name)
        if config_key and config_key in self.email_config:
            return self.email_config[config_key]

        # Fallback email
        return "research@example.com"

    def _configure_source_specific_settings(
        self, source_instance: BaseDOISource, name: str
    ):
        """Configure source-specific settings like rate limits.

        Args:
            source_instance: Source instance to configure
            name: Source name for specific configuration
        """
        if not self.rate_limit_handler:
            return

        # Configure source-specific rate limiting parameters
        if name.lower() == "pubmed":
            # NCBI requires max 3 requests per second (0.35s delay)
            state = self.rate_limit_handler.get_source_state(name.lower())
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
            self.get_source(name)
            for name in self.sources
            if self.get_source(name)
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

    def update_email_config(self, email_config: Dict[str, str]):
        """Update email configuration and reload affected sources.

        Args:
            email_config: New email configuration dictionary
        """
        self.email_config.update(email_config)

        # Reload sources that use email configuration
        email_dependent_sources = [
            name
            for name in self.sources
            if name not in ["url_doi_source"] and name in self._source_instances
        ]

        for name in email_dependent_sources:
            self.reload_source(name)

        logger.info(
            f"Updated email configuration and reloaded {len(email_dependent_sources)} sources"
        )


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    # Test email configuration
    email_config = {
        "crossref": "test@example.com",
        "pubmed": "test@example.com",
        "openalex": "test@example.com",
        "semantic_scholar": "test@example.com",
        "arxiv": "test@example.com",
    }

    # Initialize source manager
    manager = SourceManager(
        sources=["crossref", "pubmed", "url_doi_source"],
        email_config=email_config,
    )

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

# EOF
