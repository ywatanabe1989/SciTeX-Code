#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetadataIOManager - Handle all metadata.json file I/O operations.

This module centralizes metadata file I/O operations for the Scholar system.
All metadata files follow the structure:
    {
        "doi": "10.1234/...",
        "scitex_id": "ABCD1234",
        "urls": {...},
        "basic": {...},
        ...
    }
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class MetadataIOManager:
    """Centralized metadata file I/O operations for Scholar system.

    This class handles all metadata.json file I/O, ensuring consistent
    access patterns across the codebase.

    Example:
        >>> handler = MetadataIOManager()
        >>> metadata = handler.read("/path/to/MASTER/12345678/metadata.json")
        >>> handler.update_urls(metadata_path, {"url_doi": "...", "urls_pdf": [...]})
    """

    def __init__(self, name: str = "MetadataIOManager"):
        """Initialize metadata manager.

        Args:
            name: Name for logging (typically the calling class name)
        """
        self.name = name

    # ==========================================================================
    # Core Read/Write Operations
    # ==========================================================================

    def read(self, metadata_path: Path) -> Dict[str, Any]:
        """Read metadata from JSON file.

        Args:
            metadata_path: Path to metadata.json file

        Returns:
            Dictionary containing metadata, or empty dict if file doesn't exist

        Example:
            >>> metadata = manager.read(Path("/path/to/metadata.json"))
            >>> doi = metadata.get("doi")
        """
        try:
            if not metadata_path.exists():
                logger.debug(f"{self.name}: Metadata file not found: {metadata_path}")
                return {}

            content = metadata_path.read_text(encoding="utf-8")
            metadata = json.loads(content)

            logger.debug(f"{self.name}: Read metadata from {metadata_path.name}")
            return metadata

        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: Invalid JSON in {metadata_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"{self.name}: Failed to read {metadata_path}: {e}")
            return {}

    def write(
        self,
        metadata_path: Path,
        metadata: Dict[str, Any],
        create_dirs: bool = True
    ) -> bool:
        """Write metadata to JSON file.

        Args:
            metadata_path: Path to metadata.json file
            metadata: Dictionary to write
            create_dirs: Whether to create parent directories if they don't exist

        Returns:
            True if successful, False otherwise

        Example:
            >>> metadata = {"doi": "10.1234/test", "scitex_id": "ABCD1234"}
            >>> manager.write(Path("/path/to/metadata.json"), metadata)
        """
        try:
            # Create parent directories if requested
            if create_dirs:
                metadata_path.parent.mkdir(parents=True, exist_ok=True)

            # Write with proper formatting
            content = json.dumps(metadata, indent=2, ensure_ascii=False, default=str)
            metadata_path.write_text(content, encoding="utf-8")

            logger.success(f"{self.name}: Wrote metadata to {metadata_path.parent.name}/{metadata_path.name}")
            return True

        except Exception as e:
            logger.error(f"{self.name}: Failed to write {metadata_path}: {e}")
            return False

    # ==========================================================================
    # Specialized Update Operations
    # ==========================================================================

    def update_urls(
        self,
        metadata_path: Path,
        urls: Dict[str, Any],
        create_if_missing: bool = True
    ) -> bool:
        """Update URLs section in metadata file.

        This is commonly used after URL finding to store resolved URLs.

        Args:
            metadata_path: Path to metadata.json file
            urls: Dictionary containing URL data to merge into metadata["urls"]
            create_if_missing: Whether to create file if it doesn't exist

        Returns:
            True if successful, False otherwise

        Example:
            >>> urls = {
            ...     "url_doi": "https://doi.org/10.1234/test",
            ...     "url_publisher": "https://publisher.com/article",
            ...     "urls_pdf": [
            ...         {"url": "https://pdf.com/file.pdf", "source": "zotero"}
            ...     ]
            ... }
            >>> manager.update_urls(metadata_path, urls)
        """
        try:
            # Read existing metadata or start fresh
            if metadata_path.exists():
                metadata = self.read(metadata_path)
            elif create_if_missing:
                metadata = {}
                logger.info(f"{self.name}: Creating new metadata file")
            else:
                logger.warning(f"{self.name}: Metadata file not found: {metadata_path}")
                return False

            # Update URLs section
            metadata.setdefault("urls", {}).update(urls)

            # Write back
            return self.write(metadata_path, metadata)

        except Exception as e:
            logger.error(f"{self.name}: Failed to update URLs in {metadata_path}: {e}")
            return False

    def get_urls(self, metadata_path: Path) -> Dict[str, Any]:
        """Get URLs section from metadata file.

        Args:
            metadata_path: Path to metadata.json file

        Returns:
            Dictionary containing URLs, or empty dict if not found

        Example:
            >>> urls = manager.get_urls(metadata_path)
            >>> pdf_urls = urls.get("urls_pdf", [])
        """
        metadata = self.read(metadata_path)
        return metadata.get("urls", {})

    def update_field(
        self,
        metadata_path: Path,
        field_path: str,
        value: Any,
        create_if_missing: bool = True
    ) -> bool:
        """Update a specific field in metadata using dot notation.

        Args:
            metadata_path: Path to metadata.json file
            field_path: Field path in dot notation (e.g., "basic.title", "urls.url_doi")
            value: Value to set
            create_if_missing: Whether to create file if it doesn't exist

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager.update_field(path, "basic.title", "New Title")
            >>> manager.update_field(path, "urls.url_doi", "https://doi.org/...")
        """
        try:
            # Read existing metadata
            if metadata_path.exists():
                metadata = self.read(metadata_path)
            elif create_if_missing:
                metadata = {}
            else:
                logger.warning(f"{self.name}: Metadata file not found: {metadata_path}")
                return False

            # Navigate to nested field
            parts = field_path.split(".")
            current = metadata

            # Create nested structure if needed
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set value
            current[parts[-1]] = value

            # Write back
            return self.write(metadata_path, metadata)

        except Exception as e:
            logger.error(f"{self.name}: Failed to update field '{field_path}' in {metadata_path}: {e}")
            return False

    def get_field(self, metadata_path: Path, field_path: str, default: Any = None) -> Any:
        """Get a specific field from metadata using dot notation.

        Args:
            metadata_path: Path to metadata.json file
            field_path: Field path in dot notation (e.g., "basic.title")
            default: Default value if field not found

        Returns:
            Field value, or default if not found

        Example:
            >>> title = manager.get_field(path, "basic.title", default="Unknown")
            >>> doi = manager.get_field(path, "doi")
        """
        metadata = self.read(metadata_path)

        # Navigate to nested field
        parts = field_path.split(".")
        current = metadata

        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            return default

    # ==========================================================================
    # Utility Operations
    # ==========================================================================

    def exists(self, metadata_path: Path) -> bool:
        """Check if metadata file exists and is valid JSON.

        Args:
            metadata_path: Path to metadata.json file

        Returns:
            True if file exists and contains valid JSON
        """
        if not metadata_path.exists():
            return False

        try:
            json.loads(metadata_path.read_text())
            return True
        except:
            return False

    def merge(
        self,
        metadata_path: Path,
        updates: Dict[str, Any],
        overwrite: bool = False
    ) -> bool:
        """Merge updates into existing metadata.

        Args:
            metadata_path: Path to metadata.json file
            updates: Dictionary to merge
            overwrite: If True, overwrite existing values; if False, only add new keys

        Returns:
            True if successful, False otherwise

        Example:
            >>> updates = {"basic": {"abstract": "New abstract"}}
            >>> manager.merge(path, updates, overwrite=False)  # Only if abstract missing
        """
        try:
            metadata = self.read(metadata_path)

            if overwrite:
                # Deep merge with overwrite
                self._deep_merge(metadata, updates, overwrite=True)
            else:
                # Only add missing keys
                self._deep_merge(metadata, updates, overwrite=False)

            return self.write(metadata_path, metadata)

        except Exception as e:
            logger.error(f"{self.name}: Failed to merge metadata: {e}")
            return False

    def _deep_merge(self, target: dict, source: dict, overwrite: bool = False):
        """Recursively merge source into target.

        Args:
            target: Target dictionary (modified in place)
            source: Source dictionary
            overwrite: Whether to overwrite existing values
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                # Recursive merge for nested dicts
                self._deep_merge(target[key], value, overwrite)
            elif overwrite or key not in target:
                # Set value if overwrite=True or key doesn't exist
                target[key] = value


# ==========================================================================
# Convenience Functions
# ==========================================================================

def update_metadata_urls(metadata_path: Path, urls: Dict[str, Any]) -> bool:
    """Convenience function to update URLs in metadata.

    Args:
        metadata_path: Path to metadata.json file
        urls: Dictionary containing URL data

    Returns:
        True if successful, False otherwise

    Example:
        >>> from scitex.scholar.storage import update_metadata_urls
        >>> update_metadata_urls(path, {"url_doi": "https://doi.org/..."})
    """
    handler = MetadataIOManager()
    return handler.update_urls(metadata_path, urls)


def get_metadata_urls(metadata_path: Path) -> Dict[str, Any]:
    """Convenience function to get URLs from metadata.

    Args:
        metadata_path: Path to metadata.json file

    Returns:
        Dictionary containing URLs

    Example:
        >>> from scitex.scholar.storage import get_metadata_urls
        >>> urls = get_metadata_urls(path)
        >>> pdfs = urls.get("urls_pdf", [])
    """
    handler = MetadataIOManager()
    return handler.get_urls(metadata_path)


# ==========================================================================
# Module Exports
# ==========================================================================

__all__ = [
    "MetadataIOManager",
    "update_metadata_urls",
    "get_metadata_urls",
]


# EOF
