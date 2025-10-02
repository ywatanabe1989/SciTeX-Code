#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 07:22:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/batch/_MetadataHandlerForBatchDOIResolution.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Metadata processing and enhancement for batch DOI resolution."""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from scitex import logging

logger = logging.getLogger(__name__)


class MetadataHandlerForBatchDOIResolution:
    """Handles paper metadata processing, validation, and enhancement.

    Responsibilities:
    - Title normalization for deduplication
    - Paper similarity detection and grouping
    - BibTeX author string parsing
    - Year parsing and validation
    - Paper key generation for tracking
    """

    def __init__(self, similarity_threshold: float = 0.85):
        """Initialize metadata enhancer.

        Args:
            similarity_threshold: Similarity threshold for duplicate detection (0-1)
        """
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalize title for deduplication.

        Args:
            title: Raw title string

        Returns:
            Normalized title string
        """
        if not title:
            return ""

        # Remove common variations
        normalized = title.lower().strip()
        normalized = re.sub(r"[^\w\s]", "", normalized)  # Remove punctuation
        normalized = re.sub(r"\s+", " ", normalized)  # Normalize whitespace
        return normalized

    def find_similar_papers(
        self, papers: List[Dict[str, Any]]
    ) -> Dict[str, List[int]]:
        """Find potentially duplicate papers based on title similarity.

        Args:
            papers: List of paper dictionaries with 'title' field

        Returns:
            Dictionary mapping group IDs to lists of paper indices
        """
        groups = {}
        processed = set()

        for i, paper1 in enumerate(papers):
            if i in processed:
                continue

            title1 = self.normalize_title(paper1.get("title", ""))
            if not title1:
                continue

            group = [i]
            for j, paper2 in enumerate(papers[i + 1 :], start=i + 1):
                if j in processed:
                    continue

                title2 = self.normalize_title(paper2.get("title", ""))
                if not title2:
                    continue

                # Check similarity
                similarity = SequenceMatcher(None, title1, title2).ratio()
                if similarity > self.similarity_threshold:
                    group.append(j)
                    processed.add(j)

            if len(group) > 1:
                group_key = f"group_{len(groups) + 1}"
                groups[group_key] = group
                logger.warning(
                    f"Found potential duplicates ({len(group)} papers): "
                    f"{[papers[idx].get('title', '')[:50] + '...' for idx in group[:2]]}"
                )

            processed.add(i)

        return groups

    @staticmethod
    def parse_authors(authors_str: str) -> List[str]:
        """Parse BibTeX author string into individual author names.

        Args:
            authors_str: BibTeX format author string (e.g., "Smith, J. and Doe, A.")

        Returns:
            List of individual author names
        """
        if not authors_str:
            return []
        return [a.strip() for a in authors_str.split(" and ") if a.strip()]

    @staticmethod
    def parse_year(year_str: str) -> Optional[int]:
        """Parse year from string, handling various formats.

        Args:
            year_str: Year string (e.g., "2023", "2023-01-01", etc.)

        Returns:
            Parsed year as integer or None if parsing fails
        """
        if not year_str:
            return None

        try:
            # Handle simple year
            if year_str.isdigit():
                return int(year_str)

            # Handle date formats like "2023-01-01"
            year_match = re.search(r"(\d{4})", str(year_str))
            if year_match:
                return int(year_match.group(1))

            return None
        except (ValueError, TypeError):
            return None

    def get_paper_key(self, paper: Dict[str, Any]) -> str:
        """Generate unique key for paper tracking.

        Args:
            paper: Paper dictionary with title and optionally year

        Returns:
            Unique paper key for tracking
        """
        title = self.normalize_title(paper.get("title", ""))
        year = self.parse_year(str(paper.get("year", "")))

        if year:
            return f"{title}_{year}"
        return title

    def validate_paper_metadata(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance paper metadata.

        Args:
            paper: Paper dictionary to validate

        Returns:
            Dictionary with validation results and enhanced metadata
        """
        result = {"valid": True, "warnings": [], "enhanced": {}}

        # Check required fields
        title = paper.get("title", "")
        if not title or not title.strip():
            result["valid"] = False
            result["warnings"].append("Missing or empty title")
        else:
            result["enhanced"]["normalized_title"] = self.normalize_title(
                title
            )

        # Parse and validate year
        year_str = paper.get("year", "")
        if year_str:
            parsed_year = self.parse_year(year_str)
            if parsed_year:
                result["enhanced"]["parsed_year"] = parsed_year
                # Validate year range (reasonable publication years)
                if parsed_year < 1900 or parsed_year > 2030:
                    result["warnings"].append(
                        f"Unusual publication year: {parsed_year}"
                    )
            else:
                result["warnings"].append(f"Could not parse year: {year_str}")

        # Parse authors
        authors_str = paper.get("authors", "") or paper.get("author", "")
        if authors_str:
            parsed_authors = self.parse_authors(authors_str)
            result["enhanced"]["parsed_authors"] = parsed_authors
            result["enhanced"]["author_count"] = len(parsed_authors)
        else:
            result["warnings"].append("Missing author information")

        # Generate paper key
        result["enhanced"]["paper_key"] = self.get_paper_key(paper)

        return result

    def enhance_paper_batch(
        self, papers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance a batch of papers with metadata processing.

        Args:
            papers: List of paper dictionaries to enhance

        Returns:
            Dictionary with enhancement results and statistics
        """
        results = {
            "enhanced_papers": [],
            "duplicate_groups": {},
            "statistics": {
                "total": len(papers),
                "valid": 0,
                "with_warnings": 0,
                "duplicates_found": 0,
            },
        }

        # Enhance individual papers
        for paper in papers:
            validation = self.validate_paper_metadata(paper)
            enhanced_paper = {**paper, **validation["enhanced"]}
            enhanced_paper["_validation"] = validation
            results["enhanced_papers"].append(enhanced_paper)

            if validation["valid"]:
                results["statistics"]["valid"] += 1
            if validation["warnings"]:
                results["statistics"]["with_warnings"] += 1

        # Find duplicates
        duplicate_groups = self.find_similar_papers(papers)
        results["duplicate_groups"] = duplicate_groups
        results["statistics"]["duplicates_found"] = sum(
            len(group) for group in duplicate_groups.values()
        )

        return results


if __name__ == "__main__":
    # Example usage
    enhancer = MetadataHandlerForBatchDOIResolution()

    # Test papers
    test_papers = [
        {
            "title": "Machine Learning for Natural Language Processing",
            "year": "2023",
            "authors": "Smith, J. and Doe, A. and Johnson, B.",
        },
        {
            "title": "Machine learning for natural language processing",  # Similar to first
            "year": "2023",
            "authors": "Smith, John and Doe, Alice",
        },
        {
            "title": "Deep Learning Approaches",
            "year": "invalid_year",
            "authors": "Brown, C.",
        },
        {"title": "", "year": "2022"},  # Invalid title
    ]

    # Enhance papers
    results = enhancer.enhance_paper_batch(test_papers)

    print("Enhancement Results:")
    print(f"Total papers: {results['statistics']['total']}")
    print(f"Valid papers: {results['statistics']['valid']}")
    print(f"Papers with warnings: {results['statistics']['with_warnings']}")
    print(f"Duplicates found: {results['statistics']['duplicates_found']}")

    print("\nDuplicate groups:")
    for group_id, indices in results["duplicate_groups"].items():
        print(f"  {group_id}: {indices}")

    print("\nIndividual paper results:")
    for i, paper in enumerate(results["enhanced_papers"]):
        validation = paper["_validation"]
        print(
            f"  Paper {i}: Valid={validation['valid']}, Warnings={len(validation['warnings'])}"
        )
        if validation["warnings"]:
            print(f"    Warnings: {validation['warnings']}")


# python -m scitex.scholar.metadata.doi.batch._MetadataHandlerForBatchDOIResolution

# EOF
