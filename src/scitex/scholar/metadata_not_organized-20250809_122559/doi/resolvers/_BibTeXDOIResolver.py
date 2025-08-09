#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 02:29:26 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/_BibTeXDOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/_BibTeXDOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from pathlib import Path

"""
Resolve DOIs from BibTeX file in a resumable manner with progress tracking.

This module implements the critical task #4 from CLAUDE.md:
- Resolve DOIs from BibTeX entries
- Resumable processing with progress tracking
- Progress and ETA display like rsync
- Performance optimization
"""

import argparse
import asyncio
import json
import time
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode

from scitex import logging

from ._SingleDOIResolver import SingleDOIResolver
from ._EnhancedSingleDOIResolver import EnhancedSingleDOIResolver

logger = logging.getLogger(__name__)


class BibTeXDOIResolver:
    """Resolve DOIs for all entries in a BibTeX file with resumable processing."""

    def __init__(
        self,
        bibtex_path: Path,
        output_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        project_name: Optional[str] = None,
    ):
        """
        Initialize BibTeX DOI resolver.

        Args:
            bibtex_path: Path to input BibTeX file
            output_path: Path for output (defaults to input path)
            cache_dir: Directory for progress cache
            project_name: Project name (auto-detected from path if not provided)
        """
        self.bibtex_path = Path(bibtex_path)
        self.output_path = output_path or self.bibtex_path

        # Set up cache directory
        self.cache_dir = (
            cache_dir or Path.home() / ".scitex" / "scholar" / "doi_cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Progress tracking
        self.progress_file = (
            self.cache_dir / f"{self.bibtex_path.stem}_progress.json"
        )
        self.progress = self._load_progress()

        # Determine project name
        self.project_name = project_name
        if not self.project_name:
            # Extract from path (e.g., "pac" from "/path/to/pac/papers.bib")
            path_parts = self.bibtex_path.parts
            for part in reversed(path_parts[:-1]):  # Exclude filename
                if part.lower() not in [
                    "src",
                    "docs",
                    "papers",
                    "references",
                    "bib",
                ]:
                    self.project_name = part
                    break
            if not self.project_name:
                self.project_name = "imported"

        # Initialize enhanced resolver with project context and Phase 1 utilities
        self.resolver = EnhancedSingleDOIResolver(
            project=self.project_name,
            enable_utilities=True,
            ascii_fallback=False,
        )

        # Copy bibtex to library for tracking
        self.library_bibtex_path = None
        try:
            self.library_bibtex_path = self.resolver.copy_bibtex_to_library(
                str(self.bibtex_path), self.project_name
            )
            logger.info(
                f"Copied bibtex to library: {self.library_bibtex_path}"
            )
        except Exception as e:
            logger.warning(f"Could not copy bibtex to library: {e}")

        # Timing
        self.start_time = None
        self.processed_count = 0

        # Results tracking for summary
        self.results = {
            "resolved": [],
            "not_found": [],
            "failed": [],
            "existing": [],
        }

    def _load_progress(self) -> Dict[str, any]:
        """Load progress from cache file."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load progress: {e}")

        return {
            "processed": {},  # entry_id -> doi or 'not_found'
            "failed": {},  # entry_id -> error_message
            "started_at": None,
            "last_updated": None,
        }

    def _save_progress(self):
        """Save progress to cache file."""
        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, "w") as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def _load_bibtex(self) -> List[Dict]:
        """Load and parse BibTeX file."""
        parser = BibTexParser()
        parser.customization = convert_to_unicode

        with open(self.bibtex_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f, parser=parser)

        return bib_db.entries

    def _save_bibtex(self, entries: List[Dict]):
        """Save updated BibTeX entries."""
        # Create backup if overwriting
        if self.output_path == self.bibtex_path:
            backup_path = self.bibtex_path.with_suffix(".bib.bak")
            if not backup_path.exists():
                import shutil

                shutil.copy2(self.bibtex_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

        # Write BibTeX
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = entries

        writer = BibTexWriter()
        writer.indent = "  "
        writer.align_values = True

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(writer.write(db))

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

    def _print_progress(self, current: int, total: int, entry_title: str = ""):
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

        # Build progress bar
        bar_width = 40
        filled = int(bar_width * current / total) if total > 0 else 0
        bar = "=" * filled + ">" + " " * (bar_width - filled - 1)

        # Truncate title if too long
        if len(entry_title) > 50:
            entry_title = entry_title[:47] + "..."

        # Print rsync-style progress
        print(
            f"\r[{bar}] {percent:3.0f}% | "
            f"{current}/{total} | "
            f"Rate: {rate:.1f}/s | "
            f"ETA: {self._format_time(eta)} | "
            f"Current: {entry_title:<50}",
            end="",
            flush=True,
        )

    async def resolve_all_async(self) -> Tuple[int, int, int]:
        """
        Resolve DOIs for all entries in BibTeX file.

        Returns:
            Tuple of (total_entries, resolved_count, failed_count)
        """
        # Load BibTeX entries
        entries = self._load_bibtex()
        total = len(entries)

        logger.info(f"Loaded {total} entries from {self.bibtex_path}")

        # Filter out already processed entries
        pending_entries = []
        for entry in entries:
            entry_id = entry.get("ID", "")

            # Skip if already has DOI
            if "doi" in entry and entry["doi"]:
                if entry_id not in self.progress["processed"]:
                    self.progress["processed"][entry_id] = entry["doi"]

                # Track for summary
                self.results["existing"].append(
                    {
                        "entry_id": entry_id,
                        "title": entry.get("title", "").strip("{}"),
                        "doi": entry["doi"],
                        "year": entry.get("year", ""),
                        "journal": entry.get("journal", ""),
                    }
                )
                continue

            # Skip if already processed
            if entry_id in self.progress["processed"]:
                # Update entry with resolved DOI if found
                if self.progress["processed"][entry_id] != "not_found":
                    entry["doi"] = self.progress["processed"][entry_id]
                    entry["doi_source"] = "cache"
                continue

            # Skip if failed too many times
            if entry_id in self.progress["failed"]:
                if self.progress["failed"][entry_id].get("attempts", 0) >= 3:
                    continue

            pending_entries.append(entry)

        # Update progress tracking
        if not self.progress["started_at"]:
            self.progress["started_at"] = datetime.now().isoformat()

        self.start_time = time.time()
        self.processed_count = len(self.progress["processed"])

        logger.info(
            f"Progress: {self.processed_count}/{total} already processed, "
            f"{len(pending_entries)} remaining"
        )

        # Process pending entries
        for i, entry in enumerate(pending_entries):
            entry_id = entry.get("ID", "")
            title = entry.get("title", "").strip("{}")

            # Update progress display
            current = self.processed_count + i + 1
            self._print_progress(current, total, title)

            try:
                # Extract metadata for DOI resolution
                authors_str = entry.get("author", "")
                authors = (
                    [a.strip() for a in authors_str.split(" and ")]
                    if authors_str
                    else []
                )

                # Convert "Last, First" format to "First Last" format
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

                year = entry.get("year", "")
                journal = entry.get("journal", "")

                # Try to resolve DOI with Phase 1 utilities and bibtex source tracking
                result = await self.resolver.resolve_async(
                    title=title,
                    year=int(year) if year and year.isdigit() else None,
                    authors=normalized_authors if normalized_authors else None,
                    entry=entry,  # Pass full entry for utility extraction
                )

                if result and result.get("doi"):
                    doi = result["doi"]
                    source = result.get("source", "unknown")

                    entry["doi"] = doi
                    entry["doi_source"] = source
                    self.progress["processed"][entry_id] = doi

                    # Track for summary
                    self.results["resolved"].append(
                        {
                            "entry_id": entry_id,
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
                    self.progress["processed"][entry_id] = "not_found"

                    # Track for summary
                    self.results["not_found"].append(
                        {
                            "entry_id": entry_id,
                            "title": title,
                            "year": year,
                            "journal": journal,
                        }
                    )

                    logger.debug(f"No DOI found for '{title}'")

            except Exception as e:
                logger.error(f"Error resolving DOI for '{title}': {e}")

                # Track failures
                if entry_id not in self.progress["failed"]:
                    self.progress["failed"][entry_id] = {
                        "attempts": 0,
                        "errors": [],
                    }

                self.progress["failed"][entry_id]["attempts"] += 1
                self.progress["failed"][entry_id]["errors"].append(
                    {"timestamp": datetime.now().isoformat(), "error": str(e)}
                )

                # Track for summary
                self.results["failed"].append(
                    {
                        "entry_id": entry_id,
                        "title": title,
                        "error": str(e),
                        "year": year,
                        "journal": journal,
                    }
                )

            # Save progress periodically
            if (current % 10) == 0:
                self._save_progress()
                self._save_bibtex(entries)

        # Final progress update
        self._print_progress(total, total, "Complete!")
        print()  # New line after progress bar

        # Save final results
        self._save_progress()
        self._save_bibtex(entries)

        # Generate summary CSV
        summary_path = self.generate_summary_csv()
        if summary_path:
            logger.success(f"Summary CSV generated: {summary_path}")

        # Calculate statistics
        resolved_count = sum(
            1 for v in self.progress["processed"].values() if v != "not_found"
        )
        failed_count = len(self.progress["failed"])

        return total, resolved_count, failed_count

    def generate_summary_csv(self) -> str:
        """Generate CSV summary of bibtex resolution results."""
        try:
            import csv
            from pathlib import Path

            # Create info directory in project library
            info_dir = (
                self.resolver.config.path_manager.library_dir
                / self.project_name
                / "info"
                / "files-bib"
            )
            info_dir.mkdir(parents=True, exist_ok=True)

            # Generate summary filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bibtex_name = self.bibtex_path.stem
            summary_filename = f"{bibtex_name}_{timestamp}_summary.csv"
            summary_path = info_dir / summary_filename

            # Prepare CSV data
            all_entries = []

            # Add existing entries
            for entry in self.results["existing"]:
                all_entries.append(
                    {
                        "entry_id": entry["entry_id"],
                        "title": entry["title"],
                        "status": "existing_doi",
                        "doi": entry["doi"],
                        "source": "existing",
                        "year": entry["year"],
                        "journal": entry["journal"],
                        "error": "",
                    }
                )

            # Add resolved entries
            for entry in self.results["resolved"]:
                all_entries.append(
                    {
                        "entry_id": entry["entry_id"],
                        "title": entry["title"],
                        "status": "resolved",
                        "doi": entry["doi"],
                        "source": entry["source"],
                        "year": entry["year"],
                        "journal": entry["journal"],
                        "error": "",
                    }
                )

            # Add not found entries
            for entry in self.results["not_found"]:
                all_entries.append(
                    {
                        "entry_id": entry["entry_id"],
                        "title": entry["title"],
                        "status": "not_found",
                        "doi": "",
                        "source": "",
                        "year": entry["year"],
                        "journal": entry["journal"],
                        "error": "",
                    }
                )

            # Add failed entries
            for entry in self.results["failed"]:
                all_entries.append(
                    {
                        "entry_id": entry["entry_id"],
                        "title": entry["title"],
                        "status": "failed",
                        "doi": "",
                        "source": "",
                        "year": entry["year"],
                        "journal": entry["journal"],
                        "error": entry["error"],
                    }
                )

            # Write CSV
            with open(
                summary_path, "w", newline="", encoding="utf-8"
            ) as csvfile:
                fieldnames = [
                    "entry_id",
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
                for entry in all_entries:
                    writer.writerow(entry)

            logger.info(f"Generated summary CSV: {summary_path}")
            return str(summary_path)

        except Exception as e:
            logger.error(f"Error generating summary CSV: {e}")
            return ""

    def print_summary(self):
        """Print summary of resolution results."""
        total = len(self.progress["processed"]) + len(self.progress["failed"])
        resolved = sum(
            1 for v in self.progress["processed"].values() if v != "not_found"
        )
        not_found = sum(
            1 for v in self.progress["processed"].values() if v == "not_found"
        )
        failed = len(self.progress["failed"])

        print("\n" + "=" * 60)
        print("DOI Resolution Summary")
        print("=" * 60)
        print(f"Total entries:    {total}")
        print(f"DOIs resolved:    {resolved} ({resolved/total*100:.1f}%)")
        print(f"DOIs not found:   {not_found} ({not_found/total*100:.1f}%)")
        print(f"Failed entries:   {failed} ({failed/total*100:.1f}%)")

        if self.progress["started_at"]:
            started = datetime.fromisoformat(self.progress["started_at"])
            duration = datetime.now() - started
            print(f"\nProcessing time:  {duration}")

        print(f"\nOutput file:      {self.output_path}")
        print(f"Progress cache:   {self.progress_file}")

        # Show failed entries
        if failed > 0:
            print("\nFailed entries:")
            for entry_id, info in self.progress["failed"].items():
                print(f"  - {entry_id}: {info['attempts']} attempts")


if __name__ == "__main__":

    async def main():
        """Main entry point for command-line usage."""
        parser = argparse.ArgumentParser(
            description="Resolve DOIs from BibTeX file in a resumable manner",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
    Examples:
      # Resolve DOIs from BibTeX file
      python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib

      # Resume interrupted processing
      python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib

      # Save to different file
      python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib --output papers-with-dois.bib

      # Use more worker_asyncs for faster processing
      python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib --worker_asyncs 5
            """,
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
            "--worker_asyncs",
            "-w",
            type=int,
            default=3,
            help="Maximum concurrent worker_asyncs (default: 3)",
        )

        parser.add_argument(
            "--cache-dir",
            type=str,
            help="Directory for progress cache (default: ~/.scitex/scholar/doi_cache)",
        )

        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset progress and start from scratch",
        )

        parser.add_argument(
            "--project",
            "-p",
            type=str,
            help="Project name (defaults to auto-detection from path)",
        )

        args = parser.parse_args()

        # Initialize resolver
        resolver = BibTeXDOIResolver(
            bibtex_path=Path(args.bibtex),
            output_path=Path(args.output) if args.output else None,
            cache_dir=Path(args.cache_dir) if args.cache_dir else None,
            project_name=args.project,
        )

        # Reset progress if requested
        if args.reset and resolver.progress_file.exists():
            resolver.progress_file.unlink()
            resolver.progress = resolver._load_progress()
            print("Progress reset.")

        # Resolve DOIs
        try:
            total, resolved, failed = await resolver.resolve_all_async()
            resolver.print_summary()

        except KeyboardInterrupt:
            print("\n\nInterrupted! Progress has been saved.")
            print(
                f"Resume with: python -m scitex.scholar.resolve_doi_asyncs --bibtex {args.bibtex}"
            )
            return 1

        except Exception as e:
            logger.error(f"Error: {e}")
            return 1

        return 0

    import sys

    sys.exit(asyncio.run(main()))

# EOF
