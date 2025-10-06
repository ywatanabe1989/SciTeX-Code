#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refresh project symlinks based on current MASTER metadata.

This utility regenerates all symlinks in a project directory based on the
current state of metadata in MASTER, without running any downloads or enrichment.

Usage:
    python -m scitex.scholar.utils.refresh_symlinks neurovista
    python -m scitex.scholar.utils.refresh_symlinks --project pac
"""

from pathlib import Path
import argparse
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scitex.scholar.core.Scholar import Scholar
from scitex.logging import getLogger

logger = getLogger(__name__)


def refresh_project_symlinks(project: str) -> dict:
    """Refresh all symlinks in a project based on current MASTER metadata.

    Args:
        project: Project name

    Returns:
        Statistics dict with counts of refreshed, created, removed symlinks
    """
    scholar = Scholar(project=project)
    library_manager = scholar._library_manager

    project_dir = scholar.config.path_manager.get_library_dir(project)
    master_dir = scholar.config.path_manager.get_library_master_dir()

    stats = {
        "refreshed": 0,
        "created": 0,
        "removed": 0,
        "errors": 0,
    }

    # Remove all existing CC_ symlinks
    logger.info(f"Removing old symlinks in {project}...")
    for item in project_dir.iterdir():
        if item.is_symlink() and item.name.startswith("CC_"):
            try:
                item.unlink()
                logger.debug(f"Removed: {item.name}")
            except Exception as e:
                logger.error(f"Failed to remove {item.name}: {e}")
                stats["errors"] += 1

    # Get all paper directories in MASTER
    paper_dirs = [d for d in master_dir.iterdir() if d.is_dir()]
    logger.info(f"Found {len(paper_dirs)} papers in MASTER")

    # Create new symlinks for each paper
    for paper_dir in paper_dirs:
        metadata_file = paper_dir / "metadata.json"
        if not metadata_file.exists():
            continue

        try:
            # Load metadata
            with open(metadata_file) as f:
                metadata = json.load(f)

            # Check if this paper belongs to the project
            projects = metadata.get("container", {}).get("projects", [])
            if project not in projects:
                continue

            # Extract metadata for readable name generation
            meta = metadata.get("metadata", {})
            authors = meta.get("basic", {}).get("authors")
            year = meta.get("basic", {}).get("year")
            journal = meta.get("publication", {}).get("journal")

            # Generate readable name using LibraryManager logic
            readable_name = library_manager._generate_readable_name(
                comprehensive_metadata=meta,
                master_storage_path=paper_dir,
                authors=authors,
                year=year,
                journal=journal
            )

            # Create symlink
            symlink_path = project_dir / readable_name
            relative_path = Path("..") / "MASTER" / paper_dir.name

            if symlink_path.exists():
                logger.warning(f"Symlink already exists (shouldn't happen): {readable_name}")
                stats["errors"] += 1
            else:
                symlink_path.symlink_to(relative_path)
                logger.success(f"Created: {readable_name}")
                stats["created"] += 1

        except Exception as e:
            logger.error(f"Error processing {paper_dir.name}: {e}")
            stats["errors"] += 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Refresh project symlinks from MASTER metadata"
    )
    parser.add_argument(
        "project",
        nargs="?",
        help="Project name (e.g., neurovista, pac)"
    )
    parser.add_argument(
        "--project",
        dest="project_name",
        help="Project name (alternative syntax)"
    )

    args = parser.parse_args()

    project = args.project or args.project_name
    if not project:
        parser.error("Project name is required")

    logger.info(f"Refreshing symlinks for project: {project}")

    stats = refresh_project_symlinks(project)

    logger.info(f"\nResults:")
    logger.info(f"  Created: {stats['created']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info(f"  Total: {stats['created'] + stats['errors']}")


if __name__ == "__main__":
    main()
