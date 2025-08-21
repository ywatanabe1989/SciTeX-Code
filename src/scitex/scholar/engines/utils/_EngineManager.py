#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 17:32:26 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/utils/_EngineManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/engines/utils/_EngineManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Engine management for DOI resolution."""

from typing import Dict, List, Optional, Type

from scitex import log
from scitex.scholar.config import ScholarConfig

from ._ArXivEngine import ArXivEngine
from ._BaseDOIEngine import BaseDOIEngine
from ._CrossRefEngine import CrossRefEngine
from ._OpenAlexEngine import OpenAlexEngine
from ._PubMedEngine import PubMedEngine
from ._SemanticScholarEngine import SemanticScholarEngine
from ._URLDOIEngine import URLDOIEngine

logger = log.getLogger(__name__)


class EngineManager:
    """Handles engine instantiation, rotation, and lifecycle management.

    Responsibilities:
    - Engine class mapping and registry management
    - Engine instance creation and caching
    - Email configuration per engine
    - Rate limit handler injection
    - Engine-specific configuration
    """

    # Engine registry
    ENGINE_CLASSES: Dict[str, Type[BaseDOIEngine]] = {
        "url_doi_engine": URLDOIEngine,
        "crossref": CrossRefEngine,
        "pubmed": PubMedEngine,
        "openalex": OpenAlexEngine,
        "semantic_scholar": SemanticScholarEngine,
        "arxiv": ArXivEngine,
    }

    def __init__(
        self,
        engines: List[str],
        # Emails
        email_crossref: Optional[str] = None,
        email_pubmed: Optional[str] = None,
        email_openalex: Optional[str] = None,
        email_semantic_scholar: Optional[str] = None,
        email_arxiv: Optional[str] = None,
        rate_limit_handler=None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize engine manager.

        Args:
            engines: List of engine names to manage
            rate_limit_handler: Rate limit handler to inject into engines
        """
        self.config = config or ScholarConfig()
        self.engines = self.config.resolve("engines", engines)
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

        # Initialize engine instances cache
        self._engine_instances: Dict[str, BaseDOIEngine] = {}

        logger.debug(f"EngineManager initialized with engines: {self.engines}")

    def get_engine(self, name: str) -> Optional[BaseDOIEngine]:
        """Get or create engine instance.

        Args:
            name: Engine name

        Returns:
            Engine instance or None if not found
        """
        if name not in self._engine_instances:
            engine_instance = self._create_engine_instance(name)
            if engine_instance:
                self._engine_instances[name] = engine_instance

        return self._engine_instances.get(name)

    def _create_engine_instance(
        self, engine_name: str
    ) -> Optional[BaseDOIEngine]:
        """Create a new engine instance with proper configuration.

        Args:
            engine_name: Engine name

        Returns:
            Configured engine instance or None if engine not found
        """
        engine_class = self.ENGINE_CLASSES.get(engine_name)
        if not engine_class:
            logger.warning(f"Unknown engine: {engine_name}")
            return None

        try:
            # URLDOIEngine doesn't need email parameter
            if engine_name == "url_doi_engine":
                engine_instance = engine_class()
            else:
                email = self._get_email_for_engine(engine_name)
                engine_instance = engine_class(email)

            # Inject rate limit handler into engine
            if self.rate_limit_handler:
                engine_instance.set_rate_limit_handler(self.rate_limit_handler)

            # Configure engine-specific rate limiting parameters
            self._configure_engine_specific_settings(
                engine_instance, engine_name
            )

            logger.debug(f"Created engine instance: {engine_name}")
            return engine_instance

        except Exception as e:
            logger.error(f"Error creating engine {engine_name}: {e}")
            return None

    def _get_email_for_engine(self, engine_name: str) -> str:
        """Get appropriate email for a engine.

        Args:
            engine_name: Engine engine_name

        Returns:
            Email address for the engine
        """
        # Map engine engine_names to email config keys
        email_map = {
            "crossref": self.crossref_email,
            "pubmed": self.pubmed_email,
            "openalex": self.openalex_email,
            "semantic_scholar": self.semantic_scholar_email,
            "arxiv": self.arxiv_email,
        }
        return email_map[engine_name]

    def _configure_engine_specific_settings(
        self, engine_instance: BaseDOIEngine, engine_name: str
    ):
        """Configure engine-specific settings like rate limits.

        Args:
            engine_instance: Engine instance to configure
            engine_name: Engine name for specific configuration
        """
        if not self.rate_limit_handler:
            return

        # Configure engine-specific rate limiting parameters
        if engine_name.lower() == "pubmed":
            # NCBI requires max 3 requests per second (0.35s delay)
            state = self.rate_limit_handler.get_engine_state(
                engine_name.lower()
            )
            state.base_delay = 0.35
            state.adaptive_delay = 0.35
            logger.debug(
                f"Configured PubMed-specific rate limiting: 0.35s delay"
            )

    def get_all_engines(self) -> List[BaseDOIEngine]:
        """Get all configured engine instances.

        Returns:
            List of all configured engine instances
        """
        return [
            self.get_engine(engine_name)
            for engine_name in self.engines
            if self.get_engine(engine_name)
        ]

    def get_available_engine_names(self) -> List[str]:
        """Get list of available engine names.

        Returns:
            List of available engine names
        """
        return list(self.ENGINE_CLASSES.keys())

    def is_engine_available(self, name: str) -> bool:
        """Check if a engine is available.

        Args:
            name: Engine name to check

        Returns:
            True if engine is available, False otherwise
        """
        return name in self.ENGINE_CLASSES

    def reload_engine(self, name: str) -> Optional[BaseDOIEngine]:
        """Reload a engine instance (useful for error recovery).

        Args:
            name: Engine name to reload

        Returns:
            New engine instance or None if creation failed
        """
        if name in self._engine_instances:
            del self._engine_instances[name]

        return self.get_engine(name)

    def clear_engine_cache(self):
        """Clear all cached engine instances."""
        self._engine_instances.clear()
        logger.debug("Cleared engine instance cache")

    def get_engine_statistics(self) -> Dict[str, Dict[str, any]]:
        """Get statistics for all managed engines.

        Returns:
            Dictionary mapping engine names to their statistics
        """
        stats = {}
        for name in self.engines:
            engine = self.get_engine(name)
            if engine and hasattr(engine, "get_statistics"):
                stats[name] = engine.get_statistics()
            else:
                stats[name] = {"status": "unavailable"}

        return stats

    def validate_engine_configuration(self) -> Dict[str, any]:
        """Validate engine configuration and return validation results.

        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "engine_status": {},
        }

        for name in self.engines:
            if not self.is_engine_available(name):
                validation["errors"].append(f"Unknown engine: {name}")
                validation["valid"] = False
                validation["engine_status"][name] = "unknown"
                continue

            try:
                engine = self.get_engine(name)
                if engine:
                    validation["engine_status"][name] = "available"
                else:
                    validation["warnings"].append(
                        f"Could not create engine: {name}"
                    )
                    validation["engine_status"][name] = "creation_failed"
            except Exception as e:
                validation["errors"].append(f"Error with engine {name}: {e}")
                validation["engine_status"][name] = "error"

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

    # # Initialize engine manager
    # manager = EngineManager(
    #     engines=["crossref", "pubmed", "url_doi_engine"],
    #     email_config=email_config,
    # )
    manager = EngineManager(engines=["crossref", "pubmed", "url_doi_engine"])

    print("Engine Manager Test:")
    print(f"Available engines: {manager.get_available_engine_names()}")
    print(f"Configured engines: {manager.engines}")

    # Test engine creation
    crossref_engine = manager.get_engine("crossref")
    print(f"CrossRef engine created: {crossref_engine is not None}")

    # Test validation
    validation = manager.validate_engine_configuration()
    print(f"Configuration valid: {validation['valid']}")
    print(f"Engine status: {validation['engine_status']}")

    # Test engine statistics
    stats = manager.get_engine_statistics()
    print(f"Engine statistics: {stats}")


# python -m scitex.scholar.engines.individual._EngineManager

# EOF
