#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-12 14:11:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/sources/_UnifiedMetadataSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.metadata.doi.sources import (
    CrossRefSource,
    OpenAlexSource,
    PubMedSource,
    SemanticScholarSource,
)

logger = logging.getLogger(__name__)


class UnifiedMetadataSource:
    """Unified source that reuses DOI sources for comprehensive metadata retrieval."""

    # def __init__(self, config: Optional[ScholarConfig] = None):
    #     self.config = config or ScholarConfig()

    #     self.sources = [
    #         SemanticScholarSource(
    #             email=self.config.resolve("semantic_scholar_email", None),
    #             api_key=self.config.resolve("semantic_scholar_api_key", None),
    #         ),
    #         PubMedSource(email=self.config.resolve("pubmed_email", None)),
    #         CrossRefSource(email=self.config.resolve("crossref_email", None)),
    #         OpenAlexSource(email=self.config.resolve("openalex_email", None)),
    #     ]
    def __init__(self, config: Optional[ScholarConfig] = None):
        self.config = config or ScholarConfig()

        # Initialize rate limit handler
        from scitex.scholar.metadata.doi.utils._RateLimitHandler import (
            RateLimitHandler,
        )

        self.rate_limit_handler = RateLimitHandler()

        self.sources = [
            SemanticScholarSource(
                email=self.config.resolve("semantic_scholar_email", None),
                api_key=self.config.resolve("semantic_scholar_api_key", None),
            ),
            PubMedSource(email=self.config.resolve("pubmed_email", None)),
            CrossRefSource(email=self.config.resolve("crossref_email", None)),
            OpenAlexSource(email=self.config.resolve("openalex_email", None)),
        ]

        # Inject rate limit handler into all sources
        for source in self.sources:
            if hasattr(source, "set_rate_limit_handler"):
                source.set_rate_limit_handler(self.rate_limit_handler)

    def get_comprehensive_metadata(self, doi: str) -> Optional[Dict[str, Any]]:
        """Get all metadata fields in minimal API calls."""
        if not doi:
            return None

        # Try sources in priority order
        for source in self.sources:
            try:
                # Use get_metadata_by_doi if available, otherwise get_metadata + search
                if hasattr(source, "get_metadata_by_doi"):
                    metadata = source.get_metadata_by_doi(doi)
                    if metadata:
                        return self._standardize_metadata(
                            metadata, source.name
                        )

                # Fallback: use abstract getter for specific data
                if hasattr(source, "get_abstract"):
                    abstract = source.get_abstract(doi)
                    if abstract:
                        return {
                            "abstract": abstract,
                            "abstract_source": source.name.lower(),
                        }

            except Exception as e:
                logger.debug(f"Metadata fetch failed via {source.name}: {e}")

        return None

    def _standardize_metadata(
        self, metadata: Dict[str, Any], source_name: str
    ) -> Dict[str, Any]:
        """Standardize metadata format across sources."""
        result = {}
        field_map = {
            "title": metadata.get("title"),
            "abstract": metadata.get("abstract"),
            "citation_count": metadata.get("citation_count"),
            "keywords": metadata.get("keywords")
            or metadata.get("fieldsOfStudy"),
            "journal": metadata.get("journal") or metadata.get("venue"),
            "issn": metadata.get("issn"),
            "volume": metadata.get("volume"),
            "issue": metadata.get("issue"),
            "year": metadata.get("year"),
            "authors": metadata.get("authors"),
            "doi": metadata.get("doi"),
            "publisher": metadata.get("publisher"),
        }

        for field, value in field_map.items():
            if value is not None and value != "":
                if field == "title" and value.endswith("."):
                    value = value[:-1]
                result[field] = value
                if field != "doi":
                    result[f"{field}_source"] = source_name.lower()

        return result

# EOF
