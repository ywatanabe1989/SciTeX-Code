#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Examples of using typed metadata structures.

This demonstrates how to use the new type-safe metadata system.
"""

from metadata_types import (
    CompletePaperMetadata,
    PaperMetadataStructure,
    IDMetadata,
    BasicMetadata,
    ContainerMetadata,
)
from metadata_converters import (
    dict_to_typed_metadata,
    typed_to_dict_metadata,
    validate_and_normalize_engines,
    add_source_to_engines,
    merge_metadata_sources,
)
import json


def example_1_create_typed_metadata():
    """Example 1: Create typed metadata from scratch."""
    print("=" * 60)
    print("Example 1: Create typed metadata from scratch")
    print("=" * 60)

    # Create a paper with typed metadata
    paper = CompletePaperMetadata()

    # Set ID information
    paper.metadata.id.doi = "10.1234/example.2024"
    paper.metadata.id.doi_engines.append("input")

    # Set basic information
    paper.metadata.basic.title = "Example Paper on Typed Metadata"
    paper.metadata.basic.title_engines.append("input")

    paper.metadata.basic.authors = ["John Doe", "Jane Smith"]
    paper.metadata.basic.authors_engines.append("input")

    paper.metadata.basic.year = 2024
    paper.metadata.basic.year_engines.append("input")

    # Set publication information
    paper.metadata.publication.journal = "Journal of Type Safety"
    paper.metadata.publication.journal_engines.append("input")

    # Set container metadata
    paper.container.scitex_id = "ABC12345"
    paper.container.library_id = "ABC12345"
    paper.container.created_by = "SciTeX Scholar"

    # Convert to dict for JSON
    paper_dict = paper.to_dict()
    print(json.dumps(paper_dict, indent=2))

    return paper


def example_2_load_from_dict():
    """Example 2: Load typed metadata from dictionary."""
    print("\n" + "=" * 60)
    print("Example 2: Load typed metadata from dictionary")
    print("=" * 60)

    # Simulated JSON data from file
    json_data = {
        "metadata": {
            "id": {
                "doi": "10.1234/example.2024",
                "doi_engines": ["input"],
                "arxiv_id": None,
                "arxiv_id_engines": [],
            },
            "basic": {
                "title": "Example Paper",
                "title_engines": ["input", "CrossRef"],
                "authors": ["Alice", "Bob"],
                "authors_engines": ["input"],
            },
        },
        "container": {
            "scitex_id": "ABC12345",
        },
    }

    # Load into typed structure
    paper = dict_to_typed_metadata(json_data)

    # Now you get type safety and IDE autocomplete!
    print(f"DOI: {paper.metadata.id.doi}")
    print(f"Sources: {paper.metadata.id.doi_engines}")
    print(f"Title: {paper.metadata.basic.title}")
    print(f"Sources: {paper.metadata.basic.title_engines}")

    return paper


def example_3_normalize_engines():
    """Example 3: Normalize _engines fields to lists."""
    print("\n" + "=" * 60)
    print("Example 3: Normalize _engines fields to lists")
    print("=" * 60)

    # Metadata with inconsistent _engines format
    messy_metadata = {
        "metadata": {
            "id": {
                "doi": "10.1234/example",
                "doi_engines": "input",  # String instead of list
            },
            "basic": {
                "title": "Example",
                "title_engines": None,  # None instead of list
                "authors": ["Alice"],
                "authors_engines": ["input"],  # Already correct
            },
        }
    }

    print("Before normalization:")
    print(json.dumps(messy_metadata, indent=2))

    # Normalize
    normalized = validate_and_normalize_engines(messy_metadata)

    print("\nAfter normalization:")
    print(json.dumps(normalized, indent=2))

    return normalized


def example_4_add_sources():
    """Example 4: Add sources to existing metadata."""
    print("\n" + "=" * 60)
    print("Example 4: Add sources to existing metadata")
    print("=" * 60)

    # Start with basic metadata
    metadata = {
        "metadata": {
            "basic": {
                "title": "Example Paper",
                "title_engines": ["input"],
            },
            "id": {
                "doi": "10.1234/example",
                "doi_engines": ["input"],
            },
        }
    }

    print("Before adding sources:")
    print(json.dumps(metadata["metadata"]["basic"], indent=2))

    # Add source from CrossRef
    add_source_to_engines(metadata["metadata"], "basic.title", "CrossRef")

    # Try to add duplicate (won't be added)
    add_source_to_engines(metadata["metadata"], "basic.title", "input")

    # Add another source
    add_source_to_engines(metadata["metadata"], "basic.title", "OpenAlex")

    print("\nAfter adding sources:")
    print(json.dumps(metadata["metadata"]["basic"], indent=2))

    return metadata


def example_5_merge_from_multiple_sources():
    """Example 5: Merge metadata from multiple sources."""
    print("\n" + "=" * 60)
    print("Example 5: Merge metadata from multiple sources")
    print("=" * 60)

    # Existing metadata from BibTeX (input)
    existing = {
        "metadata": {
            "basic": {
                "title": "Preliminary Title",
                "title_engines": ["input"],
                "authors": ["John Doe"],
                "authors_engines": ["input"],
            },
            "id": {
                "doi": "10.1234/example",
                "doi_engines": ["input"],
            },
        }
    }

    print("Existing metadata (from BibTeX):")
    print(json.dumps(existing["metadata"]["basic"], indent=2))

    # New metadata from CrossRef
    crossref_data = {
        "metadata": {
            "basic": {
                "title": "Refined Title from CrossRef",
                "abstract": "This is the abstract from CrossRef",
            }
        }
    }

    # Merge title from CrossRef
    merge_metadata_sources(
        existing["metadata"],
        crossref_data["metadata"],
        "basic",
        "title",
        "CrossRef",
    )

    # Merge abstract from CrossRef
    merge_metadata_sources(
        existing["metadata"],
        crossref_data["metadata"],
        "basic",
        "abstract",
        "CrossRef",
    )

    print("\nAfter merging CrossRef data:")
    print(json.dumps(existing["metadata"]["basic"], indent=2))

    # New metadata from OpenAlex
    openalex_data = {
        "metadata": {
            "basic": {
                "title": "Title confirmed by OpenAlex",
            }
        }
    }

    # Merge title from OpenAlex (adds to sources)
    merge_metadata_sources(
        existing["metadata"],
        openalex_data["metadata"],
        "basic",
        "title",
        "OpenAlex",
    )

    print("\nAfter merging OpenAlex data:")
    print(json.dumps(existing["metadata"]["basic"], indent=2))

    return existing


def example_6_type_safety():
    """Example 6: Demonstrate type safety benefits."""
    print("\n" + "=" * 60)
    print("Example 6: Type safety benefits")
    print("=" * 60)

    paper = CompletePaperMetadata()

    # Type checkers and IDEs will catch these errors:
    # paper.metadata.basic.year = "2024"  # Error: Expected int, got str
    # paper.metadata.id.doi_engines = "input"  # Error: Expected List[str], got str

    # Correct usage:
    paper.metadata.basic.year = 2024  # ✓ Correct type
    paper.metadata.id.doi_engines.append("input")  # ✓ Correct type

    # IDE autocomplete works perfectly:
    # paper.metadata.  <- Shows: id, basic, citation_count, publication, url, path, system
    # paper.metadata.basic.  <- Shows: title, authors, year, abstract, etc.

    print("Type-safe assignment successful!")
    print(f"Year: {paper.metadata.basic.year} (type: {type(paper.metadata.basic.year).__name__})")
    print(f"Engines: {paper.metadata.id.doi_engines} (type: {type(paper.metadata.id.doi_engines).__name__})")


if __name__ == "__main__":
    print("\n🔬 TYPED METADATA EXAMPLES\n")

    example_1_create_typed_metadata()
    example_2_load_from_dict()
    example_3_normalize_engines()
    example_4_add_sources()
    example_5_merge_from_multiple_sources()
    example_6_type_safety()

    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60 + "\n")


# EOF
