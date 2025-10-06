#!/usr/bin/env python3
"""CLI utility for deduplicating the Scholar library."""

import argparse
from pathlib import Path

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.storage._DeduplicationManager import DeduplicationManager

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point for library deduplication."""
    parser = argparse.ArgumentParser(
        description="Deduplicate papers in the Scholar MASTER library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be deduplicated
  python -m scitex.scholar.utils.deduplicate_library --dry-run

  # Actually perform deduplication
  python -m scitex.scholar.utils.deduplicate_library

  # Verbose output
  python -m scitex.scholar.utils.deduplicate_library --verbose
"""
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report what would be done without making changes"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    # Initialize config and deduplication manager
    config = ScholarConfig()
    dedup_manager = DeduplicationManager(config=config)

    library_dir = config.get_library_dir()
    master_dir = library_dir / "MASTER"

    logger.info(f"Scholar library: {library_dir}")
    logger.info(f"MASTER directory: {master_dir}")

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    # Run deduplication
    stats = dedup_manager.deduplicate_library(dry_run=args.dry_run)

    # Report results
    logger.info("\nDeduplication Summary:")
    logger.info(f"  Duplicate groups found: {stats['groups_found']}")
    logger.info(f"  Total duplicates: {stats['duplicates_found']}")

    if not args.dry_run:
        logger.info(f"  Duplicates merged: {stats['duplicates_merged']}")
        logger.info(f"  Directories removed: {stats['dirs_removed']}")
        if stats['errors'] > 0:
            logger.warning(f"  Errors encountered: {stats['errors']}")

    if stats['duplicates_found'] == 0:
        logger.success("✓ No duplicates found - library is clean!")
    elif args.dry_run:
        logger.info(f"\nRun without --dry-run to merge {stats['duplicates_found']} duplicates")
    else:
        logger.success(f"✓ Successfully merged {stats['duplicates_merged']} duplicates")


if __name__ == "__main__":
    main()