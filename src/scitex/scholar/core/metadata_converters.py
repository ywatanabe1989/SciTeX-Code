#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converters between typed metadata structures and dict/DotDict formats.

Provides bidirectional conversion to maintain backward compatibility
while enabling type-safe operations.
"""

from __future__ import annotations
from typing import Dict, Any, Union

try:
    from .metadata_types import (
        CompletePaperMetadata,
        PaperMetadataStructure,
        IDMetadata,
        BasicMetadata,
        CitationCountMetadata,
        PublicationMetadata,
        URLMetadata,
        PathMetadata,
        SystemMetadata,
        ContainerMetadata,
    )
except ImportError:
    from metadata_types import (
        CompletePaperMetadata,
        PaperMetadataStructure,
        IDMetadata,
        BasicMetadata,
        CitationCountMetadata,
        PublicationMetadata,
        URLMetadata,
        PathMetadata,
        SystemMetadata,
        ContainerMetadata,
    )


def dict_to_typed_metadata(data: Dict[str, Any]) -> CompletePaperMetadata:
    """
    Convert dictionary to typed metadata structure.

    Args:
        data: Dictionary containing metadata and container sections

    Returns:
        CompletePaperMetadata: Typed metadata structure
    """
    return CompletePaperMetadata.from_dict(data)


def typed_to_dict_metadata(typed_metadata: CompletePaperMetadata) -> Dict[str, Any]:
    """
    Convert typed metadata structure to dictionary.

    Args:
        typed_metadata: Typed metadata structure

    Returns:
        Dict: Dictionary representation suitable for JSON serialization
    """
    return typed_metadata.to_dict()


def validate_and_normalize_engines(
    metadata_dict: Dict[str, Any], section_path: str = ""
) -> Dict[str, Any]:
    """
    Validate and normalize _engines fields to be lists.

    Recursively processes nested dictionaries and converts:
    - None -> []
    - "string" -> ["string"]
    - ["string"] -> ["string"] (unchanged)

    Args:
        metadata_dict: Dictionary to normalize
        section_path: Current path for error messages (used in recursion)

    Returns:
        Dict: Normalized dictionary with _engines as lists
    """
    if not isinstance(metadata_dict, dict):
        return metadata_dict

    result = {}
    for key, value in metadata_dict.items():
        if key.endswith("_engines"):
            # Normalize _engines fields
            if value is None:
                result[key] = []
            elif isinstance(value, str):
                result[key] = [value] if value else []
            elif isinstance(value, list):
                result[key] = value
            else:
                # Unexpected type - convert to string then list
                result[key] = [str(value)]
        elif isinstance(value, dict):
            # Recursively process nested dicts
            new_path = f"{section_path}.{key}" if section_path else key
            result[key] = validate_and_normalize_engines(value, new_path)
        else:
            result[key] = value

    return result


def add_source_to_engines(
    metadata_dict: Dict[str, Any], field_path: str, source: str
) -> None:
    """
    Add a source to the _engines list for a specific field.

    Args:
        metadata_dict: Dictionary containing metadata
        field_path: Dot-notation path to field (e.g., "basic.title" or "id.doi")
        source: Source identifier to add (e.g., "input", "CrossRef", "OpenAlex")

    Example:
        >>> metadata = {"basic": {"title": "Example", "title_engines": []}}
        >>> add_source_to_engines(metadata, "basic.title", "input")
        >>> metadata
        {"basic": {"title": "Example", "title_engines": ["input"]}}
    """
    if not source:
        return

    # Parse path
    parts = field_path.split(".")
    if len(parts) < 2:
        raise ValueError(f"Invalid field path: {field_path}. Must be section.field format.")

    section = parts[0]
    field = parts[1]
    engines_field = f"{field}_engines"

    # Navigate to section
    if section not in metadata_dict:
        metadata_dict[section] = {}

    section_dict = metadata_dict[section]

    # Ensure _engines field exists and is a list
    if engines_field not in section_dict:
        section_dict[engines_field] = []
    elif not isinstance(section_dict[engines_field], list):
        # Normalize if not already a list
        if section_dict[engines_field] is None:
            section_dict[engines_field] = []
        elif isinstance(section_dict[engines_field], str):
            section_dict[engines_field] = [section_dict[engines_field]]

    # Add source if not already present
    if source not in section_dict[engines_field]:
        section_dict[engines_field].append(source)


def merge_metadata_sources(
    existing: Dict[str, Any], new: Dict[str, Any], section: str, field: str, new_source: str
) -> None:
    """
    Merge metadata from new source into existing, tracking sources.

    Args:
        existing: Existing metadata dictionary
        new: New metadata to merge in
        section: Section name (e.g., "basic", "id")
        field: Field name (e.g., "title", "doi")
        new_source: Source of new data (e.g., "CrossRef")

    Example:
        >>> existing = {"basic": {"title": "Old Title", "title_engines": ["input"]}}
        >>> new = {"basic": {"title": "New Title"}}
        >>> merge_metadata_sources(existing, new, "basic", "title", "CrossRef")
        >>> existing
        {"basic": {"title": "New Title", "title_engines": ["input", "CrossRef"]}}
    """
    # Ensure section exists
    if section not in existing:
        existing[section] = {}
    if section not in new:
        return

    # Get values
    new_value = new[section].get(field)
    if new_value is None:
        return

    # Update value
    existing[section][field] = new_value

    # Add source
    add_source_to_engines(existing, f"{section}.{field}", new_source)


def get_field_sources(metadata_dict: Dict[str, Any], field_path: str) -> list[str]:
    """
    Get list of sources that provided data for a field.

    Args:
        metadata_dict: Dictionary containing metadata
        field_path: Dot-notation path to field (e.g., "basic.title")

    Returns:
        List of source identifiers

    Example:
        >>> metadata = {"basic": {"title": "Example", "title_engines": ["input", "CrossRef"]}}
        >>> get_field_sources(metadata, "basic.title")
        ["input", "CrossRef"]
    """
    parts = field_path.split(".")
    if len(parts) < 2:
        return []

    section = parts[0]
    field = parts[1]
    engines_field = f"{field}_engines"

    if section not in metadata_dict:
        return []

    section_dict = metadata_dict[section]
    engines = section_dict.get(engines_field, [])

    # Ensure it's a list
    if isinstance(engines, str):
        return [engines] if engines else []
    elif isinstance(engines, list):
        return engines
    else:
        return []


# EOF
