#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:37:27 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_UnifiedSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_UnifiedSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import hashlib
import time
from typing import Dict, List

from scitex import logging

from ._ArXivSource import ArXivSource
from ._CrossRefSource import CrossRefSource
from ._OpenAlexSource import OpenAlexSource
from ._PubMedSource import PubMedSource
from ._SemanticScholarSource import SemanticScholarSource
from ._URLDOISource import URLDOISource

logger = logging.getLogger(__name__)


class UnifiedSource:
    """Aggregates metadata from multiple sources for enrichment."""

    def __init__(self, sources: List[str] = None):
        self.sources = sources or [
            "Semantic_Scholar",
            "CrossRef",
            "OpenAlex",
            "PubMed",
            "arXiv",
            "URL",
        ]
        self._source_instances = {}
        self.rotation_manager = None

    def _get_source(self, name: str):
        if name not in self._source_instances:
            source_classes = {
                "CrossRef": CrossRefSource,
                "OpenAlex": OpenAlexSource,
                "PubMed": PubMedSource,
                "Semantic_Scholar": SemanticScholarSource,
                "arXiv": ArXivSource,
                "URL": URLDOISource,
            }
            if name in source_classes:
                if name == "url_doi_source":
                    self._source_instances[name] = source_classes[name]()
                else:
                    self._source_instances[name] = source_classes[name](
                        "research@example.com"
                    )
        return self._source_instances.get(name)

    async def search_all_sources_async(
        self, title: str = None, doi: str = None, **kwargs
    ) -> Dict[str, Dict]:
        """Search all sources and return combined results."""
        self._last_query_title = title
        self._attempted_sources = set()  # Track all attempted sources

        if self.rotation_manager:
            paper_info = {"title": title, **kwargs}
            source_order = self.rotation_manager.get_optimal_source_order(
                paper_info, self.sources, max_sources=len(self.sources)
            )
        else:
            source_order = self.sources

        tasks = []
        for source_name in source_order:
            source = self._get_source(source_name)
            if source:
                self._attempted_sources.add(source_name)
                task = self._search_source_with_timeout(
                    source, source_name, title, doi, **kwargs
                )
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        source_results = {}
        for ii, (source_name, result) in enumerate(zip(source_order, results)):
            if isinstance(result, Exception):
                logger.debug(f"Error from {source_name}: {result}")
                continue
            if result:
                print(
                    f"{source_name} returned title: {result.get('basic', {}).get('title', 'N/A')}"
                )
                source_results[source_name] = result

        return source_results

    async def _search_source_with_timeout(
        self,
        source,
        source_name: str,
        title: str = None,
        doi: str = None,
        timeout: int = 15,
        **kwargs,
    ):
        """Search single source with timeout."""
        try:
            # Record attempt if rotation manager available
            if self.rotation_manager:
                start_time = time.time()

            # Create search task
            loop = asyncio.get_event_loop()
            search_task = loop.run_in_executor(
                None, lambda: source.search(title=title, doi=doi, **kwargs)
            )

            # Wait with timeout
            result = await asyncio.wait_for(search_task, timeout=timeout)

            # Record success
            if self.rotation_manager and result:
                response_time = time.time() - start_time
                self.rotation_manager.record_attempt(
                    source_name,
                    {"title": title, **kwargs},
                    success=True,
                    response_time=response_time,
                )

            return result

        except asyncio.TimeoutError:
            logger.debug(f"Timeout from {source_name}")
            if self.rotation_manager:
                self.rotation_manager.record_attempt(
                    source_name, {"title": title, **kwargs}, success=False
                )
            return None
        except Exception as exc:
            logger.debug(f"Error from {source_name}: {exc}")
            if self.rotation_manager:
                self.rotation_manager.record_attempt(
                    source_name, {"title": title, **kwargs}, success=False
                )
            return None

    def _extract_identifiers(self, metadata: Dict) -> Dict:
        """Extract all identifiers from metadata."""
        ids = metadata.get("id", {})
        identifiers = {}

        # Clean and normalize identifiers
        if ids.get("doi"):
            doi = str(ids["doi"]).lower().strip()
            if doi.startswith("http"):
                doi = doi.split("/")[-2] + "/" + doi.split("/")[-1]
            identifiers["doi"] = doi

        if ids.get("pmid"):
            identifiers["pmid"] = str(ids["pmid"])

        if ids.get("arxiv_id"):
            identifiers["arxiv_id"] = str(ids["arxiv_id"]).lower()

        if ids.get("corpus_id"):
            identifiers["corpus_id"] = str(ids["corpus_id"])

        if ids.get("scholar_id"):
            identifiers["scholar_id"] = str(ids["scholar_id"])

        return identifiers

    def _identifiers_match(self, ids1: Dict, ids2: Dict) -> bool:
        """Check if any identifiers match between two papers."""
        if not ids1 or not ids2:
            return False

        # Check each identifier type
        for id_type in ["doi", "pmid", "arxiv_id", "corpus_id", "scholar_id"]:
            val1 = ids1.get(id_type)
            val2 = ids2.get(id_type)
            if val1 and val2 and val1 == val2:
                return True

        return False

    def _validate_paper_consistency(self, metadata_list: List[Dict]) -> bool:
        """Check if all metadata refers to same paper by title, exact year, and first author."""
        if not metadata_list or len(metadata_list) < 2:
            return True

        first = metadata_list[0]
        first_title = first.get("basic", {}).get("title", "").lower().strip()
        first_year = first.get("basic", {}).get("year")
        first_authors = first.get("basic", {}).get("authors", [])
        first_author_surname = (
            first_authors[0].split()[-1].lower() if first_authors else ""
        )

        for metadata in metadata_list[1:]:
            title = metadata.get("basic", {}).get("title", "").lower().strip()
            year = metadata.get("basic", {}).get("year")
            authors = metadata.get("basic", {}).get("authors", [])
            author_surname = authors[0].split()[-1].lower() if authors else ""

            # Year must be exactly the same
            if first_year != year:
                return False

            # First author surname must match
            if first_author_surname and author_surname:
                if first_author_surname != author_surname:
                    return False

            # Title similarity check
            if first_title and title:
                first_words = set(first_title.split())
                title_words = set(title.split())
                overlap = len(first_words & title_words)
                min_len = min(len(first_words), len(title_words))
                if overlap < min_len * 0.7:
                    return False

        return True

    def _validate_against_query(
        self, metadata: Dict, query_title: str
    ) -> bool:
        """Validate metadata matches the original query with strict title matching."""
        if not query_title or not metadata:
            return True

        paper_title = (
            metadata.get("basic", {}).get("title", "").lower().strip()
        )
        query_title = query_title.lower().strip()

        if not paper_title:
            return False

        import re

        def normalize_title(text):
            text = re.sub(r"[^\w\s]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            return text

        norm_query = normalize_title(query_title)
        norm_paper = normalize_title(paper_title)

        # Check if normalized query is substring of paper title or vice versa
        if norm_query in norm_paper or norm_paper in norm_query:
            return True

        # Check word-by-word exact match (order matters)
        query_words = norm_query.split()
        paper_words = norm_paper.split()

        # Find longest common subsequence
        common_seq_len = 0
        for ii in range(len(paper_words)):
            match_len = 0
            for jj in range(min(len(query_words), len(paper_words) - ii)):
                if (
                    ii + jj < len(paper_words)
                    and paper_words[ii + jj] == query_words[jj]
                ):
                    match_len += 1
                else:
                    break
            common_seq_len = max(common_seq_len, match_len)

        # Require at least 80% of query words in sequence
        return common_seq_len >= len(query_words) * 0.8

    def combine_metadata(self, source_results: Dict[str, Dict]) -> Dict:
        """Combine metadata with query validation."""
        if not source_results:
            return None

        query_title = getattr(self, "_last_query_title", None)
        valid_sources = {}
        for source_name, metadata in source_results.items():
            if metadata and self._validate_against_query(
                metadata, query_title
            ):
                valid_sources[source_name] = metadata

        if not valid_sources:
            return None

        # Start with the first valid source as base
        base_metadata = list(valid_sources.values())[0].copy()

        # Merge all other valid sources
        for source_name, metadata in list(valid_sources.items())[1:]:
            base_metadata = self.merge_metadata_structures(
                base_metadata, metadata
            )

        # Track all attempted searches
        if "system" not in base_metadata:
            base_metadata["system"] = {}

        for source_name in self.sources:
            key = f"searched_by_{source_name}"
            base_metadata["system"][key] = source_name in valid_sources

        return base_metadata

    def merge_metadata_structures(self, base: Dict, additional: Dict) -> Dict:
        """Merge two metadata structures with source priority."""
        merged = base.copy()
        source_priority = {
            "CrossRef": 4,
            "OpenAlex": 3,
            "Semantic_Scholar": 2,
            "PubMed": 1,
            "arXiv": 1,
            "URL": 1,
        }

        for section, section_data in additional.items():
            if section not in merged:
                merged[section] = section_data.copy()
                continue

            for key, value in section_data.items():
                if key.endswith("_sources") or value is None:
                    continue

                current_value = merged[section].get(key)
                current_sources = merged[section].get(f"{key}_sources")
                new_sources = section_data.get(f"{key}_sources")

                if not isinstance(new_sources, (str, list)) or not new_sources:
                    continue

                # Initialize source lists if needed
                if not isinstance(current_sources, list):
                    current_sources = (
                        [current_sources] if current_sources else []
                    )
                    merged[section][f"{key}_sources"] = current_sources

                # Convert single source to list
                if isinstance(new_sources, str):
                    new_sources = [new_sources]

                should_replace = False
                if current_value is None:
                    should_replace = True
                elif source_priority.get(
                    new_sources[0], 0
                ) > source_priority.get(
                    current_sources[0] if current_sources else "", 0
                ):
                    should_replace = True
                elif isinstance(value, list) and isinstance(
                    current_value, list
                ):
                    if len(value) > len(current_value):
                        should_replace = True
                elif isinstance(value, str) and isinstance(current_value, str):
                    if len(value) > len(current_value):
                        should_replace = True

                if should_replace:
                    merged[section][key] = value
                    merged[section][f"{key}_sources"] = new_sources
                elif current_value == value:
                    # Add new sources to list if value is the same
                    for new_source in new_sources:
                        if new_source not in current_sources:
                            current_sources.append(new_source)

        return merged


if __name__ == "__main__":
    from pprint import pprint

    async def main_async():

        TITLE = "Attention is All You Need"
        DOI = "10.1038/nature14539"
        # DOI = "https://doi.org/10.48550/arXiv.1706.03762"
        # DOI = "10.1007/978-3-031-84300-6_13"

        # Example: Unified Source
        source = UnifiedSource()
        outputs = {}

        # Search by Title
        source_results = await source.search_all_sources_async(
            title=TITLE,
        )
        enriched_metadata = source.combine_metadata(source_results)
        outputs["metadata_by_title"] = enriched_metadata

        # Search by DOI
        source_results = await source.search_all_sources_async(
            doi=DOI,
        )
        enriched_metadata = source.combine_metadata(source_results)
        outputs["metadata_by_doi"] = enriched_metadata

        for k, v in outputs.items():
            print("----------------------------------------")
            print(k)
            print("----------------------------------------")
            pprint(v)
            time.sleep(1)

    asyncio.run(main_async())

# python -m scitex.scholar.metadata.doi.sources._UnifiedSource

# EOF
