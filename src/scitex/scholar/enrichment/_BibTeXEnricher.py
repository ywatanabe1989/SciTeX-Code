#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 20:09:22 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_BibTeXEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_BibTeXEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Time-stamp: "2025-08-01 13:25:00"
# Author: Claude

"""
Enrich BibTeX entries with additional metadata.

This module implements Critical Task #6: Enrich BibTeX with metadata
including abstracts, keywords, journal metrics, citations, and more.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

from scitex import logging

from ..config import ScholarConfig
from ..doi import DOIResolver
from ..search_engine import (
    CrossRefSearchEngine,
    PubMedSearchEngine,
    SemanticScholarSearchEngine,
)

logger = logging.getLogger(__name__)


class BibTeXEnricher:
    """Enrich BibTeX entries with comprehensive metadata."""

    def __init__(self, config: Optional[ScholarConfig] = None):
        """
        Initialize BibTeX enricher.

        Args:
            config: Scholar configuration
        """
        self.config = config or ScholarConfig()

        # Initialize search engines with config
        self.crossref = CrossRefSearchEngine(config=self.config)
        self.pubmed = PubMedSearchEngine(config=self.config)
        self.semantic_scholar = SemanticScholarSearchEngine(config=self.config)

        # DOI resolver for entries without DOI
        self.doi_resolver = DOIResolver(config=self.config)

        # Cache directory using path manager
        self.cache_dir = self.config.path_manager.get_cache_dir("enrichment")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Progress tracking
        self.progress_file = None
        self.progress = {}

    def _load_bibtex(
        self, bibtex_path: Path
    ) -> Tuple[bibtexparser.bibdatabase.BibDatabase, List[Dict]]:
        """Load and parse BibTeX file."""
        parser = BibTexParser()
        parser.customization = convert_to_unicode

        with open(bibtex_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f, parser=parser)

        return bib_db, bib_db.entries

    def _save_bibtex(
        self, bib_db: bibtexparser.bibdatabase.BibDatabase, output_path: Path
    ):
        """Save enriched BibTeX."""
        # Create backup if overwriting
        if output_path.exists():
            backup_path = output_path.with_suffix(".bib.bak")
            if not backup_path.exists():
                import shutil

                shutil.copy2(output_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

        # Write BibTeX
        writer = BibTexWriter()
        writer.indent = "  "
        writer.align_values = True

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(writer.write(bib_db))

    def _load_progress(self) -> Dict[str, Any]:
        """Load enrichment progress."""
        if self.progress_file and self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load progress: {e}")

        return {
            "enriched": {},
            "failed": {},
            "started_at": None,
            "last_updated": None,
        }

    def _save_progress(self):
        """Save enrichment progress."""
        if not self.progress_file:
            return

        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, "w") as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    async def _fetch_crossref_metadata(self, doi: str) -> Dict[str, Any]:
        """Fetch metadata from CrossRef."""
        try:
            # Search by DOI
            results = await self.crossref.search_async(f"doi:{doi}", limit=1)

            if results:
                paper = results[0]
                return {
                    "abstract": paper.get("abstract"),
                    "keywords": paper.get("keywords", []),
                    "cited_by_count": paper.get("is-referenced-by-count", 0),
                    "references_count": paper.get("reference-count", 0),
                    "publisher": paper.get("publisher"),
                    "issn": paper.get("ISSN", []),
                    "subject": paper.get("subject", []),
                    "funder": paper.get("funder", []),
                    "license": paper.get("license", []),
                }
        except Exception as e:
            logger.debug(f"CrossRef fetch failed for {doi}: {e}")

        return {}

    async def _fetch_pubmed_metadata(
        self, doi: str, title: str
    ) -> Dict[str, Any]:
        """Fetch metadata from PubMed."""
        try:
            # Try DOI first, then title
            query = f"{doi}[DOI]" if doi else title
            results = await self.pubmed.search_async(query, limit=1)

            if results:
                paper = results[0]
                return {
                    "pmid": paper.get("pmid"),
                    "abstract": paper.get("abstract"),
                    "mesh_terms": paper.get("mesh_terms", []),
                    "keywords": paper.get("keywords", []),
                    "publication_types": paper.get("publication_types", []),
                }
        except Exception as e:
            logger.debug(f"PubMed fetch failed: {e}")

        return {}

    async def _fetch_semantic_scholar_metadata(
        self, doi: str, title: str
    ) -> Dict[str, Any]:
        """Fetch metadata from Semantic Scholar."""
        try:
            # Search by DOI or title
            query = doi if doi else title
            results = await self.semantic_scholar.search_async(query, limit=1)

            if results:
                paper = results[0]
                return {
                    "semantic_scholar_id": paper.get("paperId"),
                    "abstract": paper.get("abstract"),
                    "tldr": paper.get("tldr", {}).get("text"),
                    "citation_count": paper.get("citationCount", 0),
                    "influential_citation_count": paper.get(
                        "influentialCitationCount", 0
                    ),
                    "fields_of_study": paper.get("fieldsOfStudy", []),
                    "authors": [
                        {
                            "name": author.get("name"),
                            "author_id": author.get("authorId"),
                        }
                        for author in paper.get("authors", [])
                    ],
                    "venue": paper.get("venue"),
                    "year": paper.get("year"),
                }
        except Exception as e:
            logger.debug(f"Semantic Scholar fetch failed: {e}")

        return {}

    async def _enrich_single_entry(
        self, entry: Dict[str, str]
    ) -> Dict[str, str]:
        """Enrich a single BibTeX entry."""
        entry_id = entry.get("ID", "")
        title = entry.get("title", "").strip("{}")
        doi = entry.get("doi", "")

        # Skip if already enriched
        if entry_id in self.progress.get("enriched", {}):
            logger.debug(f"Skipping already enriched entry: {entry_id}")
            return entry

        logger.info(f"Enriching: {title[:50]}...")

        # Resolve DOI if missing
        if not doi:
            try:
                doi = await self.doi_resolver.title_to_doi_async(title)
                if doi:
                    entry["doi"] = doi
                    logger.debug(f"Resolved DOI: {doi}")
            except Exception as e:
                logger.debug(f"DOI resolution failed: {e}")

        # Fetch metadata from all sources concurrently
        metadata_tasks = []

        if doi:
            metadata_tasks.append(self._fetch_crossref_metadata(doi))

        metadata_tasks.extend(
            [
                self._fetch_pubmed_metadata(doi, title),
                self._fetch_semantic_scholar_metadata(doi, title),
            ]
        )

        # Gather all metadata
        all_metadata = await asyncio.gather(
            *metadata_tasks, return_exceptions=True
        )

        # Merge metadata
        merged = {}
        for metadata in all_metadata:
            if isinstance(metadata, dict):
                merged.update(metadata)

        # Update entry with enriched data
        if merged.get("abstract") and "abstract" not in entry:
            entry["abstract"] = merged["abstract"]

        if merged.get("keywords"):
            keywords = entry.get("keywords", "").split(";")
            keywords = [k.strip() for k in keywords if k.strip()]

            # Add new keywords
            for kw in merged["keywords"]:
                if isinstance(kw, str) and kw not in keywords:
                    keywords.append(kw)

            if keywords:
                entry["keywords"] = "; ".join(keywords)

        # Add citation metrics
        if merged.get("citation_count"):
            entry["citation_count"] = str(merged["citation_count"])
        elif merged.get("cited_by_count"):
            entry["citation_count"] = str(merged["cited_by_count"])

        # Add identifiers
        if merged.get("pmid"):
            entry["pmid"] = str(merged["pmid"])

        if merged.get("semantic_scholar_id"):
            entry["semantic_scholar_id"] = merged["semantic_scholar_id"]

        # Add metadata source
        sources = []
        if merged.get("publisher"):
            sources.append("crossref")
        if merged.get("pmid"):
            sources.append("pubmed")
        if merged.get("semantic_scholar_id"):
            sources.append("semantic_scholar")

        if sources:
            entry["metadata_sources"] = "; ".join(sources)

        # Add enrichment timestamp
        entry["enriched_date"] = datetime.now().strftime("%Y-%m-%d")

        # Track progress
        self.progress["enriched"][entry_id] = {
            "timestamp": datetime.now().isoformat(),
            "sources": sources,
        }

        return entry

    async def enrich_bibtex_async(
        self,
        bibtex_path: Path,
        output_path: Optional[Path] = None,
        resume: bool = True,
        max_concurrent: int = 3,
    ) -> Tuple[int, int, int]:
        """
        Enrich all entries in a BibTeX file.

        Args:
            bibtex_path: Path to input BibTeX
            output_path: Output path (defaults to input)
            resume: Whether to resume from previous progress
            max_concurrent: Maximum concurrent enrichments

        Returns:
            Tuple of (total, enriched, failed) counts
        """
        # Setup paths
        bibtex_path = Path(bibtex_path)
        output_path = output_path or bibtex_path

        # Setup progress tracking using workspace logs
        self.progress_file = (
            self.config.path_manager.get_workspace_logs_dir() / f"enrichment_{bibtex_path.stem}_progress.json"
        )
        if resume:
            self.progress = self._load_progress()
        else:
            self.progress = {
                "enriched": {},
                "failed": {},
                "started_at": datetime.now().isoformat(),
                "last_updated": None,
            }

        # Load BibTeX
        bib_db, entries = self._load_bibtex(bibtex_path)
        total = len(entries)

        logger.info(f"Loaded {total} entries from {bibtex_path}")

        # Filter entries to process
        entries_to_process = []
        for entry in entries:
            entry_id = entry.get("ID", "")

            # Skip if already enriched
            if entry_id in self.progress.get("enriched", {}):
                continue

            # Skip if failed too many times
            if entry_id in self.progress.get("failed", {}):
                if self.progress["failed"][entry_id].get("attempts", 0) >= 3:
                    continue

            entries_to_process.append(entry)

        logger.info(
            f"Progress: {len(self.progress.get('enriched', {}))} enriched, "
            f"{len(entries_to_process)} remaining"
        )

        # Process entries with semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)

        async def enrich_with_limit(entry: Dict, index: int):
            async with semaphore:
                try:
                    enriched = await self._enrich_single_entry(entry)

                    # Update progress periodically
                    if (index + 1) % 5 == 0:
                        self._save_progress()
                        self._save_bibtex(bib_db, output_path)

                    return True

                except Exception as e:
                    entry_id = entry.get("ID", "")
                    logger.error(f"Failed to enrich {entry_id}: {e}")

                    # Track failure
                    if entry_id not in self.progress["failed"]:
                        self.progress["failed"][entry_id] = {
                            "attempts": 0,
                            "errors": [],
                        }

                    self.progress["failed"][entry_id]["attempts"] += 1
                    self.progress["failed"][entry_id]["errors"].append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "error": str(e),
                        }
                    )

                    return False

        # Process all entries
        tasks = [
            enrich_with_limit(entry, i)
            for i, entry in enumerate(entries_to_process)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count results
        enriched_count = sum(1 for r in results if r is True)
        failed_count = sum(1 for r in results if r is False)

        # Save final results
        self._save_progress()
        self._save_bibtex(bib_db, output_path)

        # Total enriched includes previous progress
        total_enriched = len(self.progress.get("enriched", {}))
        total_failed = len(self.progress.get("failed", {}))

        logger.info(
            f"Enrichment complete: {total_enriched}/{total} enriched, "
            f"{total_failed} failed"
        )

        return total, total_enriched, total_failed

    def enrich_bibtex(
        self,
        bibtex_path: Path,
        output_path: Optional[Path] = None,
        resume: bool = True,
    ) -> Tuple[int, int, int]:
        """Synchronous wrapper for enrich_bibtex_async."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.enrich_bibtex_async(bibtex_path, output_path, resume)
            )
        finally:
            loop.close()


async def main():
    """Command-line interface for BibTeX enrichment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enrich BibTeX entries with additional metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enrich BibTeX file
  python -m scitex.scholar.enrichment.enrich --bibtex papers.bib

  # Save to different file
  python -m scitex.scholar.enrichment.enrich --bibtex papers.bib --output enriched.bib

  # Start fresh (don't resume)
  python -m scitex.scholar.enrichment.enrich --bibtex papers.bib --no-resume

  # Use more concurrent workers
  python -m scitex.scholar.enrichment.enrich --bibtex papers.bib --workers 5
        """,
    )

    parser.add_argument(
        "--bibtex", "-b", type=str, required=True, help="Path to BibTeX file"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output BibTeX file (defaults to input file)",
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Don't resume from previous progress",
    )

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=3,
        help="Maximum concurrent workers (default: 3)",
    )

    args = parser.parse_args()

    # Initialize enricher
    enricher = BibTeXEnricher()

    # Enrich BibTeX
    try:
        total, enriched, failed = await enricher.enrich_bibtex_async(
            Path(args.bibtex),
            Path(args.output) if args.output else None,
            resume=not args.no_resume,
            max_concurrent=args.workers,
        )

        print(f"\nEnrichment Summary:")
        print(f"  Total entries: {total}")
        print(f"  Enriched: {enriched}")
        print(f"  Failed: {failed}")

        if args.output:
            print(f"\nOutput saved to: {args.output}")

    except KeyboardInterrupt:
        print("\nInterrupted! Progress has been saved.")
        print(
            f"Resume with: python -m scitex.scholar.enrichment.enrich --bibtex {args.bibtex}"
        )
        return 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))

# EOF
