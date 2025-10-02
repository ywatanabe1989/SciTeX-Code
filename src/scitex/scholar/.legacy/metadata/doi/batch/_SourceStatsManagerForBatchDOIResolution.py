#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 05:40:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/batch/_SourceStatsManagerForBatchDOIResolution.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from pathlib import Path

from typing import Union

"""Configuration management for batch DOI resolution."""

import json
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class SourceStatsManagerForBatchDOIResolution:
    """Handles configuration resolution and validation for batch DOI processing.

    Responsibilities:
    - Configuration parameter resolution with proper defaults
    - Source performance statistics management
    - Workspace directory management
    - Batch-specific configuration validation
    """

    def __init__(
        self,
        progress_path: Optional[Union[str, Path]] = None,
        max_worker: Optional[int] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize configuration manager.

        Args:
            config: ScholarConfig instance, creates default if None
        """
        self.config = config or ScholarConfig()
        self.max_worker = self.config.resolve("max_worker", max_worker)
        self.progress_path = self.config.get_doi_resolution_progress_path(
            progress_path
        )
        self._source_success_rates: Dict[str, Dict[str, float]] = {}
        self._load_source_stats()

    def get_doi_resolution_progress_path(
        self, provided_path: Optional[Path] = None
    ) -> Path:
        """Resolve progress file path with automatic generation if needed."""
        return self.config.get_doi_resolution_progress_path(provided_path)

    def get_workspace_logs_dir(self) -> Path:
        """Get workspace logs directory from configuration."""
        return self.config.path_manager.get_workspace_logs_dir()

    def get_library_dir(self) -> Path:
        """Get Scholar library directory from configuration."""
        return self.config.path_manager.library_dir

    def resolve_sources(
        self, provided_sources: Optional[List[str]] = None
    ) -> List[str]:
        """Resolve DOI sources with configuration fallbacks."""
        if provided_sources:
            return provided_sources

        # Use configuration or default sources
        return self.config.resolve(
            "sources",
            None,
            ["pubmed", "crossref", "semantic_scholar"],
            list,
        )

    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return {
            "default_delay": self.config.resolve(
                "rate_limit_default_delay", None, 1.0, float
            ),
            "adaptive_enabled": self.config.resolve(
                "rate_limit_adaptive", None, True, bool
            ),
            "max_retries": self.config.resolve(
                "rate_limit_max_retries", None, 3, int
            ),
        }

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate batch configuration and return validation results.

        Returns:
            Dictionary with validation results and any issues found
        """
        validation = {"valid": True, "warnings": [], "errors": []}

        try:
            # Check workspace directory access
            workspace_dir = self.get_workspace_logs_dir()
            if not workspace_dir.exists():
                try:
                    workspace_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    validation["errors"].append(
                        f"Cannot create workspace directory: {e}"
                    )
                    validation["valid"] = False
            elif not workspace_dir.is_dir():
                validation["errors"].append(
                    f"Workspace path is not a directory: {workspace_dir}"
                )
                validation["valid"] = False

            # Check library directory access
            library_dir = self.get_library_dir()
            if not library_dir.exists():
                validation["warnings"].append(
                    f"Library directory does not exist: {library_dir}"
                )
            elif not library_dir.is_dir():
                validation["errors"].append(
                    f"Library path is not a directory: {library_dir}"
                )
                validation["valid"] = False

            # Validate max worker_asyncs
            if self.max_worker <= 0:
                validation["errors"].append(
                    f"Invalid self.max_worker value: {self.max_worker}"
                )
                validation["valid"] = False
            elif self.max_worker > 20:
                validation["warnings"].append(
                    f"High self.max_worker value may cause rate limiting: {self.max_worker}"
                )

            # Validate sources
            sources = self.resolve_sources()
            if not sources:
                validation["errors"].append("No DOI sources configured")
                validation["valid"] = False

        except Exception as e:
            validation["errors"].append(f"Configuration validation error: {e}")
            validation["valid"] = False

        return validation

    def _load_source_stats(self):
        """Load historical source performance stats from workspace directory."""
        try:
            workspace_dir = self.get_workspace_logs_dir()
            stats_file = workspace_dir / "source_stats.json"

            if stats_file.exists():
                with open(stats_file, "r") as f:
                    self._source_success_rates = json.load(f)
                logger.debug(f"Loaded source statistics from {stats_file}")
            else:
                self._source_success_rates = {}
                logger.debug("No existing source statistics found")

        except Exception as e:
            logger.warning(f"Could not load source statistics: {e}")
            self._source_success_rates = {}

    def save_source_stats(self):
        """Save source performance stats to workspace directory."""
        try:
            workspace_dir = self.get_workspace_logs_dir()
            workspace_dir.mkdir(parents=True, exist_ok=True)

            stats_file = workspace_dir / "source_stats.json"
            with open(stats_file, "w") as f:
                json.dump(self._source_success_rates, f, indent=2)

            logger.debug(f"Saved source statistics to {stats_file}")

        except Exception as e:
            logger.warning(f"Could not save source statistics: {e}")

    def get_source_success_rate(self, source: str) -> float:
        """Get historical success rate for a source.

        Args:
            source: Source name

        Returns:
            Success rate (0.0 to 1.0)
        """
        return self._source_success_rates.get(source, {}).get(
            "success_rate", 0.0
        )

    def update_source_stats(self, source: str, success: bool):
        """Update source performance statistics.

        Args:
            source: Source name
            success: Whether the request was successful
        """
        if source not in self._source_success_rates:
            self._source_success_rates[source] = {
                "attempts": 0,
                "successes": 0,
                "success_rate": 0.0,
                "last_updated": datetime.now().isoformat(),
            }

        stats = self._source_success_rates[source]
        stats["attempts"] += 1
        if success:
            stats["successes"] += 1

        stats["success_rate"] = stats["successes"] / stats["attempts"]
        stats["last_updated"] = datetime.now().isoformat()

    def get_all_source_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get all source performance statistics.

        Returns:
            Dictionary mapping source names to their statistics
        """
        return self._source_success_rates.copy()

    def reset_source_stats(self):
        """Reset all source performance statistics."""
        self._source_success_rates = {}
        self.save_source_stats()

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration.

        Returns:
            Dictionary with configuration summary
        """
        return {
            "max_worker": self.max_worker,
            "sources": self.resolve_sources(),
            "workspace_dir": str(self.get_workspace_logs_dir()),
            "library_dir": str(self.get_library_dir()),
            "rate_limit_config": self.get_rate_limit_config(),
            "source_stats_count": len(self._source_success_rates),
        }


if __name__ == "__main__":

    def main():
        # Example usage
        from pathlib import Path

        # Initialize configuration manager
        source_stats_manager = SourceStatsManagerForBatchDOIResolution()

        # Test configuration resolution
        print("Configuration Summary:")
        summary = source_stats_manager.get_configuration_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")

        # Test validation
        print("\nConfiguration Validation:")
        validation = source_stats_manager.validate_configuration()
        print(f"  Valid: {validation['valid']}")
        if validation["warnings"]:
            print(f"  Warnings: {validation['warnings']}")
        if validation["errors"]:
            print(f"  Errors: {validation['errors']}")

        # Test source statistics
        print("\nTesting source statistics:")
        source_stats_manager.update_source_stats("pubmed", True)
        source_stats_manager.update_source_stats("pubmed", False)
        source_stats_manager.update_source_stats("crossref", True)

        stats = source_stats_manager.get_all_source_stats()
        for source, stat in stats.items():
            print(
                f"  {source}: {stat['successes']}/{stat['attempts']} = {stat['success_rate']:.2%}"
            )

        # Test progress file path generation
        progress_path = source_stats_manager.progress_path
        print(f"\nGenerated progress file path: {progress_path}")

    main()

# python -m scitex.scholar.metadata.doi.batch._SourceStatsManagerForBatchDOIResolution

# EOF
