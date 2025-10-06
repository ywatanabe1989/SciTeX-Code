#!/usr/bin/env python3
"""Deduplication manager for handling duplicate papers in the library."""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class DeduplicationManager:
    """Manages deduplication of papers in the MASTER library."""

    def __init__(self, config: ScholarConfig = None):
        self.config = config or ScholarConfig()
        self.library_dir = self.config.get_library_dir()
        self.master_dir = self.library_dir / "MASTER"

    def find_duplicate_papers(self) -> Dict[str, List[Path]]:
        """Find all duplicate papers in MASTER library.

        Returns:
            Dictionary mapping paper fingerprint to list of duplicate paths
        """
        logger.info("Scanning MASTER library for duplicates...")

        paper_groups = {}  # fingerprint -> list of paths
        papers_by_title = {}  # normalized_title -> list of (path, metadata)

        if not self.master_dir.exists():
            return paper_groups

        # First pass: collect all papers
        all_papers = []
        for paper_dir in self.master_dir.iterdir():
            if not paper_dir.is_dir():
                continue

            metadata_file = paper_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                all_papers.append((paper_dir, metadata))
            except Exception as e:
                logger.debug(f"Error reading {metadata_file}: {e}")

        # Second pass: group by fingerprint AND by normalized title
        for paper_dir, metadata in all_papers:
            # Group by fingerprint (existing logic)
            fingerprint = self._generate_paper_fingerprint(metadata)
            if fingerprint:
                if fingerprint not in paper_groups:
                    paper_groups[fingerprint] = []
                paper_groups[fingerprint].append(paper_dir)

            # Also group by normalized title for cross-DOI duplicate detection
            title = metadata.get("title")
            if title:
                title_norm = self._normalize_title(title)
                if title_norm:
                    if title_norm not in papers_by_title:
                        papers_by_title[title_norm] = []
                    papers_by_title[title_norm].append((paper_dir, metadata))

        # Find duplicates by title (papers with same title but different fingerprints)
        for title_norm, papers in papers_by_title.items():
            if len(papers) > 1:
                # Check if these are truly duplicates (same title, similar year)
                groups_to_merge = {}  # fingerprint -> paths

                for paper_dir, metadata in papers:
                    fp = self._generate_paper_fingerprint(metadata)
                    if fp not in groups_to_merge:
                        groups_to_merge[fp] = []
                    groups_to_merge[fp].append(paper_dir)

                # If we have multiple fingerprints for same title, merge them
                if len(groups_to_merge) > 1:
                    # Use the fingerprint with DOI if available, otherwise first one
                    main_fp = None
                    for fp in groups_to_merge:
                        if fp.startswith("DOI:"):
                            main_fp = fp
                            break
                    if not main_fp:
                        main_fp = list(groups_to_merge.keys())[0]

                    # Merge all papers into the main fingerprint group
                    if main_fp not in paper_groups:
                        paper_groups[main_fp] = []

                    for fp, paths in groups_to_merge.items():
                        for path in paths:
                            if path not in paper_groups[main_fp]:
                                paper_groups[main_fp].append(path)

        # Filter to only groups with duplicates
        duplicates = {
            fp: paths for fp, paths in paper_groups.items()
            if len(paths) > 1
        }

        if duplicates:
            total_dups = sum(len(paths) - 1 for paths in duplicates.values())
            logger.warning(f"Found {len(duplicates)} groups with {total_dups} duplicate papers")
        else:
            logger.info("No duplicates found")

        return duplicates

    def _generate_paper_fingerprint(self, metadata: Dict) -> Optional[str]:
        """Generate a fingerprint for paper comparison.

        Uses DOI if available, otherwise title+author+year.
        """
        # Prefer DOI as unique identifier
        doi = metadata.get("doi")
        if doi:
            return f"DOI:{self._normalize_doi(doi)}"

        # Fallback to title+author+year
        title = metadata.get("title")
        if not title:
            return None

        # Normalize title
        title_norm = self._normalize_title(title)

        # Get first author
        authors = metadata.get("authors", [])
        first_author = ""
        if authors:
            if isinstance(authors[0], str):
                first_author = self._normalize_author(authors[0])
            elif isinstance(authors[0], dict):
                name = authors[0].get("name", "")
                first_author = self._normalize_author(name)

        # Get year
        year = str(metadata.get("year", ""))

        return f"META:{title_norm}:{first_author}:{year}"

    def _normalize_doi(self, doi: str) -> str:
        """Normalize DOI for comparison."""
        if not doi:
            return ""
        # Remove URL prefixes
        doi = doi.replace("https://doi.org/", "")
        doi = doi.replace("http://dx.doi.org/", "")
        doi = doi.replace("doi:", "")
        return doi.lower().strip()

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        if not title:
            return ""
        # Remove special characters and normalize whitespace
        title = re.sub(r'[^\w\s]', '', title.lower())
        title = ' '.join(title.split())
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = [w for w in title.split() if w not in stop_words]
        return ' '.join(words)

    def _normalize_author(self, author: str) -> str:
        """Normalize author name for comparison."""
        if not author:
            return ""
        # Extract last name
        author = author.strip()
        if ',' in author:
            # Last, First format
            return author.split(',')[0].strip().lower()
        else:
            # First Last format
            parts = author.split()
            return parts[-1].lower() if parts else ""

    def merge_duplicate_papers(
        self,
        paper_dirs: List[Path],
        strategy: str = "best_metadata"
    ) -> Tuple[Path, List[Path]]:
        """Merge duplicate papers into one canonical entry.

        Args:
            paper_dirs: List of duplicate paper directories
            strategy: Merge strategy ('best_metadata', 'newest', 'oldest')

        Returns:
            Tuple of (kept_dir, removed_dirs)
        """
        if len(paper_dirs) < 2:
            return paper_dirs[0] if paper_dirs else None, []

        # Score each paper to determine which to keep
        scored_papers = []
        for paper_dir in paper_dirs:
            metadata_file = paper_dir / "metadata.json"
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                score = self._score_paper_metadata(metadata, paper_dir)
                scored_papers.append((score, paper_dir, metadata))

            except Exception as e:
                logger.debug(f"Error scoring {paper_dir}: {e}")
                scored_papers.append((0, paper_dir, {}))

        # Sort by score (highest first)
        scored_papers.sort(key=lambda x: x[0], reverse=True)

        # Keep the best one
        best_score, keep_dir, keep_metadata = scored_papers[0]
        remove_dirs = [p[1] for p in scored_papers[1:]]

        logger.info(f"Keeping {keep_dir.name} (score: {best_score})")
        logger.info(f"Will merge/remove: {[d.name for d in remove_dirs]}")

        # Merge metadata from all duplicates
        merged_metadata = self._merge_metadata(scored_papers)

        # Save merged metadata
        metadata_file = keep_dir / "metadata.json"
        metadata_backup = keep_dir / f"metadata.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Backup original
        shutil.copy2(metadata_file, metadata_backup)

        # Write merged metadata
        with open(metadata_file, 'w') as f:
            json.dump(merged_metadata, f, indent=2)

        # Merge any PDFs or other files
        self._merge_files(keep_dir, remove_dirs)

        return keep_dir, remove_dirs

    def _score_paper_metadata(self, metadata: Dict, paper_dir: Path) -> int:
        """Score paper metadata quality for deduplication priority.

        Higher score = better metadata = should be kept
        """
        score = 0

        # DOI is most important
        if metadata.get("doi"):
            score += 1000

        # Citation count (log scale to avoid extreme dominance)
        citation_count = metadata.get("citation_count", 0)
        if citation_count:
            import math
            score += min(int(math.log10(citation_count + 1) * 100), 500)

        # Impact factor
        impact_factor = metadata.get("impact_factor", 0)
        if impact_factor:
            score += min(int(impact_factor * 10), 200)

        # Abstract
        if metadata.get("abstract"):
            score += 50

        # PDF exists
        pdf_files = list(paper_dir.glob("*.pdf"))
        if pdf_files:
            score += 100

        # Complete author list
        authors = metadata.get("authors", [])
        if len(authors) > 1:
            score += 20

        # Journal name
        if metadata.get("journal"):
            score += 30

        # URL
        if metadata.get("url"):
            score += 10

        # PDF URL
        if metadata.get("pdf_url"):
            score += 20

        # Publisher
        if metadata.get("publisher"):
            score += 10

        return score

    def _merge_metadata(self, scored_papers: List[Tuple[int, Path, Dict]]) -> Dict:
        """Merge metadata from multiple papers, keeping best values."""
        if not scored_papers:
            return {}

        # Start with best paper's metadata
        _, _, merged = scored_papers[0]
        merged = merged.copy()

        # Track sources for transparency
        merged["_deduplication"] = {
            "merged_from": [str(p[1].name) for p in scored_papers],
            "merge_timestamp": datetime.now().isoformat(),
            "scores": {str(p[1].name): p[0] for p in scored_papers}
        }

        # Merge from other papers
        for _, paper_dir, metadata in scored_papers[1:]:
            # Add missing fields
            for key, value in metadata.items():
                if key not in merged and value:
                    merged[key] = value

            # Update with better values for specific fields

            # Take highest citation count
            new_cc = metadata.get("citation_count", 0) or 0
            old_cc = merged.get("citation_count", 0) or 0
            if new_cc > old_cc:
                merged["citation_count"] = metadata["citation_count"]
                merged["citation_count_source"] = metadata.get("citation_count_source", "merged")

            # Take highest impact factor
            new_if = metadata.get("impact_factor", 0) or 0
            old_if = merged.get("impact_factor", 0) or 0
            if new_if > old_if:
                merged["impact_factor"] = metadata["impact_factor"]
                merged["impact_factor_source"] = metadata.get("impact_factor_source", "merged")

            # Take DOI if missing
            if not merged.get("doi") and metadata.get("doi"):
                merged["doi"] = metadata["doi"]
                merged["doi_source"] = metadata.get("doi_source", "merged")

            # Take abstract if missing
            if not merged.get("abstract") and metadata.get("abstract"):
                merged["abstract"] = metadata["abstract"]
                merged["abstract_source"] = metadata.get("abstract_source", "merged")

        return merged

    def _merge_files(self, keep_dir: Path, remove_dirs: List[Path]):
        """Merge files from duplicate directories."""
        for remove_dir in remove_dirs:
            # Copy PDFs if not already present
            for pdf_file in remove_dir.glob("*.pdf"):
                target_pdf = keep_dir / pdf_file.name
                if not target_pdf.exists():
                    logger.info(f"Copying PDF: {pdf_file.name}")
                    shutil.copy2(pdf_file, target_pdf)

            # Merge screenshots directory
            remove_screenshots = remove_dir / "screenshots"
            if remove_screenshots.exists():
                keep_screenshots = keep_dir / "screenshots"
                keep_screenshots.mkdir(exist_ok=True)

                for screenshot in remove_screenshots.glob("*"):
                    target = keep_screenshots / screenshot.name
                    if not target.exists():
                        shutil.copy2(screenshot, target)

            # Merge logs directory
            remove_logs = remove_dir / "logs"
            if remove_logs.exists():
                keep_logs = keep_dir / "logs"
                keep_logs.mkdir(exist_ok=True)

                for log in remove_logs.glob("*"):
                    target = keep_logs / log.name
                    if not target.exists():
                        shutil.copy2(log, target)

    def deduplicate_library(self, dry_run: bool = True) -> Dict[str, int]:
        """Deduplicate entire MASTER library.

        Args:
            dry_run: If True, only report what would be done

        Returns:
            Statistics about deduplication
        """
        stats = {
            "groups_found": 0,
            "duplicates_found": 0,
            "duplicates_merged": 0,
            "dirs_removed": 0,
            "broken_symlinks_removed": 0,
            "errors": 0
        }

        # Find all duplicates
        duplicates = self.find_duplicate_papers()
        stats["groups_found"] = len(duplicates)
        stats["duplicates_found"] = sum(len(paths) - 1 for paths in duplicates.values())

        if not duplicates:
            logger.info("No duplicates to process")
            return stats

        if dry_run:
            logger.info("DRY RUN - no changes will be made")
            for fingerprint, paper_dirs in duplicates.items():
                logger.info(f"\nDuplicate group: {fingerprint}")
                for paper_dir in paper_dirs:
                    metadata_file = paper_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        cc = metadata.get("citation_count", 0)
                        doi = metadata.get("doi", "No DOI")
                        logger.info(f"  - {paper_dir.name}: CC={cc}, DOI={doi}")
        else:
            # Actually merge duplicates
            for fingerprint, paper_dirs in duplicates.items():
                try:
                    logger.info(f"\nProcessing duplicate group: {fingerprint}")
                    keep_dir, remove_dirs = self.merge_duplicate_papers(paper_dirs)

                    # Remove duplicate directories
                    for remove_dir in remove_dirs:
                        # Move to .deduplicated directory instead of deleting
                        dedup_dir = self.master_dir / ".deduplicated" / datetime.now().strftime("%Y%m%d_%H%M%S")
                        dedup_dir.mkdir(parents=True, exist_ok=True)

                        target = dedup_dir / remove_dir.name
                        logger.info(f"Moving {remove_dir.name} to {target}")
                        shutil.move(str(remove_dir), str(target))
                        stats["dirs_removed"] += 1

                    stats["duplicates_merged"] += len(remove_dirs)

                    # Update project symlinks
                    self._update_project_symlinks(fingerprint, keep_dir, remove_dirs)

                except Exception as e:
                    logger.error(f"Error processing group {fingerprint}: {e}")
                    stats["errors"] += 1

        # Clean up broken symlinks after deduplication
        if not dry_run:
            broken_count = self._cleanup_broken_symlinks()
            stats["broken_symlinks_removed"] = broken_count
            if broken_count > 0:
                logger.info(f"Removed {broken_count} broken symlinks")

        logger.info(f"\nDeduplication complete: {stats}")
        return stats

    def _cleanup_broken_symlinks(self) -> int:
        """Remove broken symlinks from all project directories.

        Returns:
            Number of broken symlinks removed
        """
        removed_count = 0

        # Check all project directories
        for project_dir in self.library_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name == "MASTER":
                continue

            # Check each symlink in the project
            for item in project_dir.iterdir():
                if item.is_symlink():
                    # Check if symlink target exists
                    try:
                        target = item.resolve(strict=True)
                    except (OSError, RuntimeError):
                        # Symlink is broken
                        logger.info(f"Removing broken symlink: {project_dir.name}/{item.name}")
                        item.unlink()
                        removed_count += 1

        return removed_count

    def _update_project_symlinks(self, fingerprint: str, keep_dir: Path, remove_dirs: List[Path]):
        """Update project symlinks after deduplication."""
        removed_ids = {d.name for d in remove_dirs}

        # Check all project directories
        for project_dir in self.library_dir.iterdir():
            if not project_dir.is_dir() or project_dir.name == "MASTER":
                continue

            # Find symlinks pointing to removed directories
            for symlink in project_dir.iterdir():
                if symlink.is_symlink():
                    target = symlink.resolve()
                    if target.name in removed_ids:
                        # Update to point to kept directory
                        logger.info(f"Updating symlink: {symlink} -> {keep_dir}")
                        symlink.unlink()
                        symlink.symlink_to(Path("..") / "MASTER" / keep_dir.name)

    def check_for_existing_paper(self, metadata: Dict) -> Optional[Path]:
        """Check if a paper already exists in MASTER library.

        Args:
            metadata: Paper metadata to check

        Returns:
            Path to existing paper directory if found, None otherwise
        """
        if not self.master_dir.exists():
            return None

        # Generate fingerprint for the paper
        fingerprint = self._generate_paper_fingerprint(metadata)
        if not fingerprint:
            return None

        # Check all papers in MASTER
        for paper_dir in self.master_dir.iterdir():
            if not paper_dir.is_dir():
                continue

            metadata_file = paper_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    existing_metadata = json.load(f)

                existing_fingerprint = self._generate_paper_fingerprint(existing_metadata)

                if fingerprint == existing_fingerprint:
                    return paper_dir

            except Exception:
                continue

        return None