#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 00:09:04 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/engines/ScholarEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/engines/ScholarEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import hashlib
import re
import time
from typing import Dict, List

from tqdm import tqdm

from scitex import logging
from scitex.scholar import ScholarConfig

from .individual import (
    ArXivEngine,
    CrossRefEngine,
    CrossRefLocalEngine,
    OpenAlexEngine,
    PubMedEngine,
    SemanticScholarEngine,
    URLDOIEngine,
)

logger = logging.getLogger(__name__)


class ScholarEngine:
    """Aggregates metadata from multiple engines for enrichment."""

    def __init__(
        self,
        engines: List[str] = None,
        config: ScholarConfig = None,
        use_cache=True,
        clear_cache=False,
    ):
        self.config = config if config else ScholarConfig()
        self.engines = self.config.resolve("engines", engines)
        self.use_cache = self.config.resolve("use_cache_search", use_cache)
        self._engine_instances = {}
        self.rotation_manager = None

        # Initialize cache
        self._setup_cache(clear_cache)

    def _setup_cache(self, clear_cache=False):
        """Setup cache directory and files."""
        self.cache_dir = self.config.get_search_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "search_results.json"

        if clear_cache and self.cache_file.exists():
            self.cache_file.unlink()
            logger.info("Cleared engine search cache")

        self._load_cache()

    def _load_cache(self):
        """Load cache from file."""
        if self.use_cache and self.cache_file.exists():
            try:
                import json

                with open(self.cache_file, "r") as f:
                    self._cache = json.load(f)
            except:
                self._cache = {}
        else:
            self._cache = {}

    def _save_cache(self):
        """Save cache to file."""
        if self.use_cache:
            try:
                import json

                with open(self.cache_file, "w") as f:
                    json.dump(self._cache, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to save engine cache: {e}")

    def _get_cache_key(self, title: str = None, doi: str = None, **kwargs):
        """Generate cache key for search parameters."""
        params = {"title": title, "doi": doi, **kwargs}
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        # Create hash from sorted params
        import json

        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    # # Working but not showing fail message, at least when cache is enabled
    # async def search_async(
    #     self, title: str = None, doi: str = None, **kwargs
    # ) -> Dict[str, Dict]:
    #     """Search all engines and return combined results."""
    #     # Check cache first
    #     cache_key = self._get_cache_key(title, doi, **kwargs)
    #     if self.use_cache and cache_key in self._cache:
    #         logger.debug(f"Using cached search result")
    #         return self._cache[cache_key]

    #     self._last_query_title = title
    #     self._attempted_engines = set()

    #     if self.rotation_manager:
    #         paper_info = {"title": title, **kwargs}
    #         engine_order = self.rotation_manager.get_optimal_engine_order(
    #             paper_info, self.engines, max_engines=len(self.engines)
    #         )
    #     else:
    #         engine_order = self.engines

    #     tasks = []
    #     for engine_name in engine_order:
    #         engine = self._get_engine(engine_name)
    #         if engine:
    #             self._attempted_engines.add(engine_name)
    #             task = self._search_engine_with_timeout(
    #                 engine, engine_name, title, doi, **kwargs
    #             )
    #             tasks.append(task)

    #     results = await asyncio.gather(*tasks, return_exceptions=True)

    #     engine_results = {}
    #     for ii, (engine_name, result) in enumerate(zip(engine_order, results)):
    #         if isinstance(result, Exception):
    #             logger.fail(f"Error from {engine_name}: {result}")
    #             # when cache is enabled this seems not shown
    #             continue
    #         if result:
    #             print(
    #                 f"{engine_name} returned title: {result.get('basic', {}).get('title', 'N/A')}"
    #             )
    #             engine_results[engine_name] = result

    #     combined_result = self._combine_metadata(engine_results)

    #     # Cache result
    #     if self.use_cache and combined_result:
    #         self._cache[cache_key] = combined_result
    #         self._save_cache()

    #     return combined_result

    async def search_async(
        self, title: str = None, doi: str = None, **kwargs
    ) -> Dict[str, Dict]:
        """Search all engines and return combined results."""

        def _build_readable_query_str(title, doi):
            # Log failure if no results found
            query_str = (
                f"title: {title}"
                if title
                else f"doi: {doi}" if doi else "unknown query"
            )
            N_PRINT = 50
            if len(query_str) < N_PRINT:
                return query_str
            else:
                return f"{query_str[:N_PRINT]}..."

        # Check cache first
        cache_key = self._get_cache_key(title, doi, **kwargs)
        if self.use_cache and cache_key in self._cache:
            logger.debug(f"Using cached search result")
            return self._cache[cache_key]

        self._last_query_title = title
        self._attempted_engines = set()

        if self.rotation_manager:
            paper_info = {"title": title, **kwargs}
            engine_order = self.rotation_manager.get_optimal_engine_order(
                paper_info, self.engines, max_engines=len(self.engines)
            )
        else:
            engine_order = self.engines

        tasks = []
        for engine_name in engine_order:
            engine = self._get_engine(engine_name)
            if engine:
                self._attempted_engines.add(engine_name)
                task = self._search_engine_with_timeout(
                    engine, engine_name, title, doi, **kwargs
                )
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        engine_results = {}
        for ii, (engine_name, result) in enumerate(zip(engine_order, results)):
            if isinstance(result, Exception):
                logger.debug(f"Error from {engine_name}: {result}")
                continue
            if result:
                logger.debug(
                    f"{engine_name} returned title: {result.get('basic', {}).get('title', 'N/A')}"
                )
                engine_results[engine_name] = result

        combined_result = self._combine_metadata(engine_results)

        query_str = _build_readable_query_str(title, doi)

        if not combined_result:
            logger.fail(f"No metadata found for {query_str}")

        # Cache result
        if self.use_cache and combined_result:
            self._cache[cache_key] = combined_result
            self._save_cache()

        logger.success(f"Metadata retrieved for this query: {query_str}")

        return combined_result

    async def search_batch_async(
        self,
        titles: List[str] = None,
        dois: List[str] = None,
    ) -> List[Dict[str, Dict]]:
        """Search multiple papers in batch with parallel processing."""

        def _print_stats(queries, results):
            failed_queries = []
            found_count = 0

            for query, result in zip(queries, results):
                if isinstance(result, Exception):
                    failed_queries.append((query, str(result)))
                elif result and result.get("id", {}).get("doi"):
                    found_count += 1
                else:
                    failed_queries.append((query, "No metadata found"))

            n_total = len(queries)
            success_rate = (
                round(100.0 * found_count / n_total, 1) if n_total > 0 else 0.0
            )

            msg = f"Search engines found {found_count}/{n_total} DOIs from publications (= {success_rate}%)"
            if found_count == n_total:
                logger.success(msg)
            else:
                logger.warn(msg)
                for query, error in failed_queries:
                    logger.fail(f"Failed query '{query}': {error}")

        if dois:
            batched_metadata = [
                await self.search_async(doi=doi) for doi in tqdm(dois)
            ]
            _print_stats(dois, batched_metadata)
            return batched_metadata

        if titles:
            batched_metadata = [
                await self.search_async(title=title) for title in tqdm(titles)
            ]
            _print_stats(titles, batched_metadata)
            return batched_metadata

        return []

    def _get_engine(self, name: str):
        if name not in self._engine_instances:
            engine_classes = {
                "URL": URLDOIEngine,
                "CrossRef": CrossRefEngine,
                "CrossRefLocal": CrossRefLocalEngine,
                "OpenAlex": OpenAlexEngine,
                "PubMed": PubMedEngine,
                "Semantic_Scholar": SemanticScholarEngine,
                "arXiv": ArXivEngine,
            }
            if name in engine_classes:
                if name == "url_doi_engine":
                    self._engine_instances[name] = engine_classes[name]()
                else:
                    self._engine_instances[name] = engine_classes[name](
                        "research@example.com"
                    )
        return self._engine_instances.get(name)

    async def _search_engine_with_timeout(
        self,
        engine,
        engine_name: str,
        title: str = None,
        doi: str = None,
        timeout: int = 15,
        **kwargs,
    ):
        """Search single engine with timeout."""
        try:
            # Record attempt if rotation manager available
            if self.rotation_manager:
                start_time = time.time()

            # Create search task
            loop = asyncio.get_event_loop()
            search_task = loop.run_in_executor(
                None, lambda: engine.search(title=title, doi=doi, **kwargs)
            )

            # Wait with timeout
            result = await asyncio.wait_for(search_task, timeout=timeout)

            # Record success
            if self.rotation_manager and result:
                response_time = time.time() - start_time
                self.rotation_manager.record_attempt(
                    engine_name,
                    {"title": title, **kwargs},
                    success=True,
                    response_time=response_time,
                )

            return result

        except asyncio.TimeoutError:
            logger.debug(f"Timeout from {engine_name}")
            if self.rotation_manager:
                self.rotation_manager.record_attempt(
                    engine_name, {"title": title, **kwargs}, success=False
                )
            return None
        except Exception as exc:
            logger.debug(f"Error from {engine_name}: {exc}")
            if self.rotation_manager:
                self.rotation_manager.record_attempt(
                    engine_name, {"title": title, **kwargs}, success=False
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
        first_title = (
            (first.get("basic", {}).get("title") or "").lower().strip()
        )
        first_year = first.get("basic", {}).get("year")
        first_authors = first.get("basic", {}).get("authors", [])
        first_author_surname = (
            first_authors[0].split()[-1].lower() if first_authors else ""
        )

        for metadata in metadata_list[1:]:
            title = (
                (metadata.get("basic", {}).get("title") or "").lower().strip()
            )
            year = metadata.get("basic", {}).get("year")
            authors = metadata.get("basic", {}).get("authors", [])
            first_author = authors[0]
            if first_author:
                author_surname = (
                    authors[0].split()[-1].lower() if authors else ""
                )
            else:
                author_surname = ""

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
            (metadata.get("basic", {}).get("title") or "").lower().strip()
        )
        if not paper_title:
            return False

        query_title = query_title.lower().strip()

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

    def _combine_metadata(self, engine_results: Dict[str, Dict]) -> Dict:
        """Combine metadata with query validation."""
        if not engine_results:
            return None

        query_title = getattr(self, "_last_query_title", None)
        valid_engines = {}
        for engine_name, metadata in engine_results.items():
            if metadata and self._validate_against_query(
                metadata, query_title
            ):
                valid_engines[engine_name] = metadata

        if not valid_engines:
            # Return all engine results without validation if nothing matches
            # This allows partial enrichment even if title validation fails
            logger.warning("No engines returned matching metadata, using all results")
            valid_engines = {k: v for k, v in engine_results.items() if v}

        # If still no valid engines, return empty structure
        if not valid_engines:
            logger.warning("No engine returned any metadata")
            return {}

        # Start with the first valid engine as base
        base_metadata = list(valid_engines.values())[0].copy()

        # Merge all other valid engines
        for engine_name, metadata in list(valid_engines.items())[1:]:
            base_metadata = self._merge_metadata_structures(
                base_metadata, metadata
            )

        # Track all attempted searches
        if "system" not in base_metadata:
            base_metadata["system"] = {}

        for engine_name in self.engines:
            key = f"searched_by_{engine_name}"
            base_metadata["system"][key] = engine_name in valid_engines

        return base_metadata

    def _merge_metadata_structures(self, base: Dict, additional: Dict) -> Dict:
        """Merge two metadata structures with engine priority."""
        merged = base.copy()
        engine_priority = {
            "URL": 5,
            "CrossRef": 4,
            "OpenAlex": 3,
            "Semantic_Scholar": 2,
            "PubMed": 1,
            "arXiv": 1,
        }

        for section, section_data in additional.items():
            if section not in merged:
                merged[section] = section_data.copy()
                continue

            for key, value in section_data.items():
                if key.endswith("_engines") or value is None:
                    continue

                current_value = merged[section].get(key)
                current_engines = merged[section].get(f"{key}_engines")
                new_engines = section_data.get(f"{key}_engines")

                if not isinstance(new_engines, (str, list)) or not new_engines:
                    continue

                # Initialize engine lists if needed
                if not isinstance(current_engines, list):
                    current_engines = (
                        [current_engines] if current_engines else []
                    )
                    merged[section][f"{key}_engines"] = current_engines

                # Convert single engine to list
                if isinstance(new_engines, str):
                    new_engines = [new_engines]

                should_replace = False
                if current_value is None:
                    should_replace = True
                elif engine_priority.get(
                    new_engines[0], 0
                ) > engine_priority.get(
                    current_engines[0] if current_engines else "", 0
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
                    merged[section][f"{key}_engines"] = new_engines
                elif current_value == value:
                    # Add new engines to list if value is the same
                    for new_engine in new_engines:
                        if new_engine not in current_engines:
                            current_engines.append(new_engine)

        return merged


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    from scitex.scholar import ScholarEngine

    async def main_async():
        # Query
        TITLE = "Attention is All You Need"
        DOI = "10.1038/nature14539"

        # Example: Unified Engine
        engine = ScholarEngine(use_cache=False)
        outputs = {}

        # Search by Title
        outputs["metadata_by_title"] = await engine.search_async(
            title=TITLE,
        )

        # Search by DOI
        outputs["metadata_by_doi"] = await engine.search_async(
            doi=DOI,
        )

        for k, v in outputs.items():
            print("----------------------------------------")
            print(k)
            print("----------------------------------------")
            pprint(v)
            time.sleep(1)

    asyncio.run(main_async())

# python -m scitex.scholar.engines.ScholarEngine

# EOF
