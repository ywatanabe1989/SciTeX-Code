#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 13:32:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/resolvers/_BibTeXDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/resolvers/_BibTeXDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio
import csv
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._LibraryCacheManager import LibraryCacheManager

# from ._SingleDOIResolverForBibTeXDOIResolver import (
#     SingleDOIResolverForBibTeXDOIResolver,
# )
from ._SingleDOIResolver import SingleDOIResolver

logger = logging.getLogger(__name__)


class BibTeXDOIResolver:
    """Resolve DOIs for all entries in a BibTeX file with resumable processing."""

    def __init__(
        self,
        project: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize BibTeX DOI resolver."""
        self.config = config or ScholarConfig()
        self.cache_dir = self.config.get_doi_resolution_cache_dir()
        self.project = self.config.resolve("project", project)

        self.single_doi_resolver = SingleDOIResolver(
            project=self.project,
        )

        self._library_cache_manager = LibraryCacheManager(
            project=self.project, config=self.config
        )

        self.start_time = None
        self.processed_count = 0
        self.results = {
            "resolved": [],
            "not_found": [],
            "failed": [],
            "existing": [],
        }

    async def bibtex_file2dois_async(
        self,
        bibtex_input_path,
        project_name: Optional[str] = None,
    ) -> Tuple[int, int, int]:
        """Resolve DOIs for all entries in BibTeX file."""

        bibtex_input_path = Path(str(bibtex_input_path))

        self.progress = self._load_progress(bibtex_input_path)
        bibtex_entries = self._load_bibtex(bibtex_input_path)
        total = len(bibtex_entries)
        logger.info(f"Loaded {total} bibtex_entries from {bibtex_input_path}")

        # Copy to library for future reference
        self._library_cache_manager.copy_bibtex_to_library(
            bibtex_input_path, project_name
        )

        pending_bibtex_entries = []
        for bibtex_entry in bibtex_entries:
            bibtex_entry_id = bibtex_entry.get("ID", "")

            if "doi" in bibtex_entry and bibtex_entry["doi"]:
                if bibtex_entry_id not in self.progress["processed"]:
                    self.progress["processed"][bibtex_entry_id] = bibtex_entry[
                        "doi"
                    ]
                self.results["existing"].append(
                    {
                        "bibtex_entry_id": bibtex_entry_id,
                        "title": bibtex_entry.get("title", "").strip("{}"),
                        "doi": bibtex_entry["doi"],
                        "year": bibtex_entry.get("year", ""),
                        "journal": bibtex_entry.get("journal", ""),
                    }
                )
                # Create symlink for existing DOIs
                title = bibtex_entry.get("title", "").strip("{}")
                year = bibtex_entry.get("year", "")
                authors_str = bibtex_entry.get("author", "")
                authors = (
                    [auth_.strip() for auth_ in authors_str.split(" and ")]
                    if authors_str
                    else []
                )

                self._library_cache_manager._ensure_project_symlink(
                    title=title,
                    year=int(year) if year and year.isdigit() else None,
                    authors=authors if authors else None,
                )
                continue

            if bibtex_entry_id in self.progress["processed"]:
                if self.progress["processed"][bibtex_entry_id] != "not_found":
                    bibtex_entry["doi"] = self.progress["processed"][
                        bibtex_entry_id
                    ]
                    bibtex_entry["doi_source"] = "cache"
                continue

            if bibtex_entry_id in self.progress["failed"]:
                if (
                    self.progress["failed"][bibtex_entry_id].get("attempts", 0)
                    >= 3
                ):
                    continue

            pending_bibtex_entries.append(bibtex_entry)

        pending_count = len(pending_bibtex_entries)

        if not self.progress["started_at"]:
            self.progress["started_at"] = datetime.now().isoformat()
        self.start_time = time.time()
        self.processed_count = len(self.progress["processed"])

        logger.info(
            f"Progress: {self.processed_count}/{total} already processed, {len(pending_bibtex_entries)} remaining"
        )

        for ii_, bibtex_entry in enumerate(pending_bibtex_entries):
            bibtex_entry_id = bibtex_entry.get("ID", "")
            title = bibtex_entry.get("title", "").strip("{}")
            current = self.processed_count + ii_ + 1
            self._print_progress(current, total, title)

            try:
                authors_str = bibtex_entry.get("author", "")
                authors = (
                    [auth_.strip() for auth_ in authors_str.split(" and ")]
                    if authors_str
                    else []
                )

                normalized_authors = []
                for author in authors:
                    if "," in author:
                        parts = author.split(",", 1)
                        if len(parts) == 2:
                            last, first = parts[0].strip(), parts[1].strip()
                            normalized_authors.append(f"{first} {last}")
                        else:
                            normalized_authors.append(author)
                    else:
                        normalized_authors.append(author)

                year = bibtex_entry.get("year", "")
                journal = bibtex_entry.get("journal", "")

                result = await self.single_doi_resolver.metadata2doi_async(
                    title=title,
                    year=int(year) if year and year.isdigit() else None,
                    authors=normalized_authors if normalized_authors else None,
                    bibtex_entry=bibtex_entry,
                )

                if result and result.get("doi"):
                    doi = result["doi"]
                    source = result.get("source", "unknown")

                    # Ensure symlink creation even for cache hits
                    if source == "cache":
                        self.single_doi_resolver._library_cache_manager._ensure_project_symlink(
                            title=title,
                            year=(
                                int(year) if year and year.isdigit() else None
                            ),
                            authors=(
                                normalized_authors
                                if normalized_authors
                                else None
                            ),
                        )

                    bibtex_entry["doi"] = doi
                    bibtex_entry["doi_source"] = source
                    self.progress["processed"][bibtex_entry_id] = doi

                    self.results["resolved"].append(
                        {
                            "bibtex_entry_id": bibtex_entry_id,
                            "title": title,
                            "doi": doi,
                            "source": source,
                            "year": year,
                            "journal": journal,
                        }
                    )
                    logger.debug(
                        f"Resolved DOI for '{title}': {doi} (via {source})"
                    )
                else:
                    self.progress["processed"][bibtex_entry_id] = "not_found"
                    self.results["not_found"].append(
                        {
                            "bibtex_entry_id": bibtex_entry_id,
                            "title": title,
                            "year": year,
                            "journal": journal,
                        }
                    )
                    logger.debug(f"No DOI found for '{title}'")

            except Exception as exc_:
                logger.error(f"Error resolving DOI for '{title}': {exc_}")
                if bibtex_entry_id not in self.progress["failed"]:
                    self.progress["failed"][bibtex_entry_id] = {
                        "attempts": 0,
                        "errors": [],
                    }

                self.progress["failed"][bibtex_entry_id]["attempts"] += 1
                self.progress["failed"][bibtex_entry_id]["errors"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "error": str(exc_),
                    }
                )

                self.results["failed"].append(
                    {
                        "bibtex_entry_id": bibtex_entry_id,
                        "title": title,
                        "error": str(exc_),
                        "year": year,
                        "journal": journal,
                    }
                )

            if (current % 10) == 0:
                self._save_progress(bibtex_input_path)
                self._save_bibtex(bibtex_entries, bibtex_input_path)

        self._print_progress(total, total, "Complete!")
        print()

        self._save_progress(bibtex_input_path)
        self._save_bibtex(bibtex_entries, bibtex_input_path)

        summary_path = self.generate_summary_csv(bibtex_input_path)
        if summary_path:
            logger.success(f"Summary CSV generated: {summary_path}")

        resolved_count = sum(
            1
            for val_ in self.progress["processed"].values()
            if val_ != "not_found"
        )
        failed_count = len(self.progress["failed"])

        resolved_count += total - pending_count
        success_rate = 1.0 * 100 * resolved_count / total
        logger.success(
            f"{resolved_count}/{total} papers resolved ({success_rate:.1f}%)"
        )
        return total, resolved_count, failed_count

    def generate_summary_csv(self, bibtex_input_path) -> str:
        """Generate CSV summary of bibtex resolution results."""
        try:
            info_dir = (
                self.single_doi_resolver.config.path_manager.library_dir
                / self.project
                / "info"
                / os.path.basename(bibtex_input_path).replace(".bib", "-bib")
            )
            info_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bibtex_name = bibtex_input_path.stem
            summary_filename = f"{bibtex_name}_{timestamp}_summary.csv"
            summary_path = info_dir / summary_filename

            all_bibtex_entries = []

            for bibtex_entry in self.results["existing"]:
                all_bibtex_entries.append(
                    {
                        "bibtex_entry_id": bibtex_entry["bibtex_entry_id"],
                        "title": bibtex_entry["title"],
                        "status": "existing_doi",
                        "doi": bibtex_entry["doi"],
                        "source": "existing",
                        "year": bibtex_entry["year"],
                        "journal": bibtex_entry["journal"],
                        "error": "",
                    }
                )

            for bibtex_entry in self.results["resolved"]:
                all_bibtex_entries.append(
                    {
                        "bibtex_entry_id": bibtex_entry["bibtex_entry_id"],
                        "title": bibtex_entry["title"],
                        "status": "resolved",
                        "doi": bibtex_entry["doi"],
                        "source": bibtex_entry["source"],
                        "year": bibtex_entry["year"],
                        "journal": bibtex_entry["journal"],
                        "error": "",
                    }
                )

            for bibtex_entry in self.results["not_found"]:
                all_bibtex_entries.append(
                    {
                        "bibtex_entry_id": bibtex_entry["bibtex_entry_id"],
                        "title": bibtex_entry["title"],
                        "status": "not_found",
                        "doi": "",
                        "source": "",
                        "year": bibtex_entry["year"],
                        "journal": bibtex_entry["journal"],
                        "error": "",
                    }
                )

            for bibtex_entry in self.results["failed"]:
                all_bibtex_entries.append(
                    {
                        "bibtex_entry_id": bibtex_entry["bibtex_entry_id"],
                        "title": bibtex_entry["title"],
                        "status": "failed",
                        "doi": "",
                        "source": "",
                        "year": bibtex_entry["year"],
                        "journal": bibtex_entry["journal"],
                        "error": bibtex_entry["error"],
                    }
                )

            with open(
                summary_path, "w", newline="", encoding="utf-8"
            ) as csvfile:
                fieldnames = [
                    "bibtex_entry_id",
                    "title",
                    "status",
                    "doi",
                    "source",
                    "year",
                    "journal",
                    "error",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for bibtex_entry in all_bibtex_entries:
                    writer.writerow(bibtex_entry)

            logger.info(f"Generated summary CSV: {summary_path}")
            return str(summary_path)
        except Exception as exc_:
            logger.error(f"Error generating summary CSV: {exc_}")
            return ""

    def print_summary(self, bibtex_input_path, bibtex_output_path):
        """Print summary of resolution results."""
        self.progress_file = (
            self.cache_dir / f"{bibtex_input_path.stem}_progress.json"
        )
        self.progress = self._load_progress(bibtex_input_path)
        total = len(self.progress["processed"]) + len(self.progress["failed"])
        resolved = sum(
            1
            for val_ in self.progress["processed"].values()
            if val_ != "not_found"
        )
        not_found = sum(
            1
            for val_ in self.progress["processed"].values()
            if val_ == "not_found"
        )
        failed = len(self.progress["failed"])

        print("\n" + "=" * 60)
        print("DOI Resolution Summary")
        print("=" * 60)
        print(f"Total bibtex_entries:    {total}")
        print(f"DOIs resolved:    {resolved} ({resolved/total*100:.1f}%)")
        print(f"DOIs not found:   {not_found} ({not_found/total*100:.1f}%)")
        print(f"Failed bibtex_entries:   {failed} ({failed/total*100:.1f}%)")

        if self.progress["started_at"]:
            started = datetime.fromisoformat(self.progress["started_at"])
            duration = datetime.now() - started
            print(f"\nProcessing time:  {duration}")

        print(f"\nOutput file:      {bibtex_output_path}")
        print(f"Progress cache:   {self.progress_file}")

        if failed > 0:
            print("\nFailed bibtex_entries:")
            for bibtex_entry_id, info in self.progress["failed"].items():
                print(f"  - {bibtex_entry_id}: {info['attempts']} attempts")

    def _load_progress(self, bibtex_input_path) -> Dict[str, any]:
        """Load progress from cache file."""
        self.progress_file = (
            self.cache_dir / f"{bibtex_input_path.stem}_progress.json"
        )
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as file_:
                    return json.load(file_)
            except Exception as exc_:
                logger.warning(f"Failed to load progress: {exc_}")
        return {
            "processed": {},
            "failed": {},
            "started_at": None,
            "last_updated": None,
        }

    def _save_progress(self, bibtex_input_path):
        """Save progress to cache file."""
        self.progress_file = (
            self.cache_dir / f"{bibtex_input_path.stem}_progress.json"
        )
        self.progress = self._load_progress(bibtex_input_path)
        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, "w") as file_:
                json.dump(self.progress, file_, indent=2)
        except Exception as exc_:
            logger.error(f"Failed to save progress: {exc_}")

    def _load_bibtex(self, bibtex_input_path) -> List[Dict]:
        """Load and parse BibTeX file."""
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        with open(bibtex_input_path, "r", encoding="utf-8") as file_:
            bib_db = bibtexparser.load(file_, parser=parser)
        return bib_db.entries

    def _save_bibtex(
        self,
        bibtex_entries: List[Dict],
        bibtex_input_path: str,
        bibtex_output_path: Optional[str] = None,
    ):
        """Save updated BibTeX bibtex_entries."""
        if (bibtex_output_path is not None) and (
            bibtex_output_path == bibtex_input_path
        ):
            backup_path = bibtex_input_path.with_suffix(".bib.bak")
            if not backup_path.exists():
                shutil.copy2(bibtex_input_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

        db_ = bibtexparser.bibdatabase.BibDatabase()
        db_.entries = bibtex_entries
        writer = BibTexWriter()
        writer.indent = "  "
        writer.align_values = True

        if bibtex_output_path is None:
            bibtex_output_path = bibtex_input_path

        with open(bibtex_output_path, "w", encoding="utf-8") as file_:
            file_.write(writer.write(db_))

    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{mins:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def _print_progress(
        self, current: int, total: int, bibtex_entry_title: str = ""
    ):
        """Print progress with ETA like rsync."""
        if self.start_time is None:
            return

        elapsed = time.time() - self.start_time
        if current > 0:
            rate = current / elapsed
            eta = (total - current) / rate if rate > 0 else 0
        else:
            rate = 0
            eta = 0

        percent = (current / total) * 100 if total > 0 else 0
        bar_width = 40
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "=" * filled + ">" + " " * (bar_width - filled - 1)

        if len(bibtex_entry_title) > 50:
            bibtex_entry_title = bibtex_entry_title[:47] + "..."

        print(
            f"\r[{bar}] {percent:3.0f}% | "
            f"{current}/{total} | "
            f"Rate: {rate:.1f}/s | "
            f"ETA: {self._format_time(eta)} | "
            f"Current: {bibtex_entry_title:<50}",
            end="",
            flush=True,
        )


if __name__ == "__main__":

    async def main():
        """Main bibtex_entry point for command-line usage."""
        parser = argparse.ArgumentParser(
            description="Resolve DOIs from BibTeX file in a resumable manner",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "--bibtex",
            "-b",
            type=str,
            required=True,
            help="Path to BibTeX file",
        )
        parser.add_argument(
            "--output",
            "-o",
            type=str,
            help="Output BibTeX file (defaults to input file)",
        )
        parser.add_argument(
            "--workers",
            "-w",
            type=int,
            default=3,
            help="Maximum concurrent workers (default: 3)",
        )
        parser.add_argument(
            "--cache-dir", type=str, help="Directory for progress cache"
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset progress and start from scratch",
        )
        parser.add_argument("--project", "-p", type=str, help="Project name")

        args = parser.parse_args()

        resolver = BibTeXDOIResolver(project=args.project)

        if args.reset and resolver.progress_file.exists():
            resolver.progress_file.unlink()
            resolver.progress = resolver._load_progress()
            print("Progress reset.")

        try:
            total, resolved, failed = await resolver.bibtex_file2dois_async(
                Path(args.bibtex)
            )
            resolver.print_summary(
                Path(args.bibtex),
                Path(args.output) if args.output else Path(args.bibtex),
            )
        except KeyboardInterrupt:
            print("\n\nInterrupted! Progress has been saved.")
            return 1
        except Exception as exc_:
            logger.error(f"Error: {exc_}")
            return 1
        return 0

    import sys

    sys.exit(asyncio.run(main()))

# python -m scitex.scholar.metadata.doi.resolvers._BibTeXDOIResolver --bibtex /home/ywatanabe/win/downloads/papers.bib --project pac

# EOF
