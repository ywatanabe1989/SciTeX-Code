#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 17:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/utils/enrich_and_fix_library.py
# ----------------------------------------
"""
Enrich library metadata and fix symlinks using existing Scholar modules.

This properly reuses existing components:
- Scholar.load_bibtex() for loading BibTeX
- Scholar.enrich_papers() for enrichment
- Scholar.save_papers_as_bibtex() for saving
- JCRImpactFactorEngine for impact factors
- Library structure from ScholarLibrary

Usage:
    python -m scitex.scholar.utils.enrich_and_fix_library --project neurovista
    python -m scitex.scholar.utils.enrich_and_fix_library --bibtex data/neurovista_enriched.bib --project neurovista
"""

import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import asyncio
import sys
import os

# Add parent directory to path to import standardize_metadata
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scitex.scholar.engines.utils._standardize_metadata import standardize_metadata

from scitex import logging
from scitex.scholar.core.Scholar import Scholar
from scitex.scholar.core.Paper import Paper
from scitex.scholar.core.Papers import Papers

logger = logging.getLogger(__name__)


async def enrich_and_fix_library(
    project_name: str,
    bibtex_file: Optional[Path] = None,
    dry_run: bool = False
):
    """Enrich library metadata and fix symlinks.

    Args:
        project_name: Project to enrich and fix
        bibtex_file: Optional enriched BibTeX file to use as source
        dry_run: If True, show what would be done
    """
    library_dir = Path.home() / ".scitex/scholar/library"
    project_dir = library_dir / project_name
    master_dir = library_dir / "MASTER"

    # Check both possible library locations
    if not project_dir.exists():
        # Try alternative location
        library_dir = Path("/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/library")
        project_dir = library_dir / project_name
        master_dir = library_dir / "MASTER"

    if not project_dir.exists():
        logger.error(f"Project directory not found: {project_name}")
        return

    logger.info(f"Enriching and fixing library for project: {project_name}")
    if dry_run:
        logger.warning("DRY RUN - No changes will be made")

    # Initialize Scholar
    scholar = Scholar(project=project_name)

    # If BibTeX file provided, load enriched data from it
    enriched_papers = None
    enriched_lookup = {}

    if bibtex_file and Path(bibtex_file).exists():
        logger.info(f"Loading enriched data from: {bibtex_file}")
        enriched_papers = scholar.load_bibtex(bibtex_file)

        # Create lookup by DOI
        for paper in enriched_papers:
            if paper.doi:
                enriched_lookup[paper.doi] = paper

        logger.success(f"Loaded {len(enriched_lookup)} enriched papers")

    # Process each symlink in project
    symlinks = [f for f in project_dir.iterdir() if f.is_symlink()]
    logger.info(f"Found {len(symlinks)} symlinks to process")

    for i, symlink in enumerate(symlinks, 1):
        logger.info(f"\n[{i}/{len(symlinks)}] Processing: {symlink.name}")

        # Get target MASTER directory
        target = symlink.readlink()
        paper_id = target.name if target.name else str(target).split("/")[-1]
        master_path = master_dir / paper_id

        if not master_path.exists():
            logger.warning(f"  Master path not found: {master_path}")
            continue

        # Load existing metadata
        metadata_file = master_path / "metadata.json"
        if not metadata_file.exists():
            logger.warning(f"  No metadata.json found")
            continue

        with open(metadata_file) as f:
            existing_metadata = json.load(f)

        # Check for DOI in both flat and structured formats
        doi = None
        if isinstance(existing_metadata.get("id"), dict):
            doi = existing_metadata["id"].get("doi")
        else:
            doi = existing_metadata.get("doi")

        if not doi:
            logger.warning(f"  No DOI in metadata")
            continue

        # Get enriched data for this DOI
        enriched_paper = None

        if doi in enriched_lookup:
            # Use data from provided BibTeX file
            enriched_paper = enriched_lookup[doi]
            logger.info(f"  Found in enriched BibTeX")
        else:
            # Try to enrich using Scholar
            logger.info(f"  Enriching DOI: {doi}")
            try:
                paper = Paper(doi=doi)
                papers = Papers([paper])
                enriched = await scholar.enrich_papers_async(papers)
                if enriched and len(enriched) > 0:
                    enriched_paper = enriched[0]
            except Exception as e:
                logger.error(f"  Enrichment failed: {e}")

        if not enriched_paper:
            logger.warning(f"  Could not get enriched data")
            continue

        # Generate readable name
        first_author = "Unknown"
        if enriched_paper.authors and len(enriched_paper.authors) > 0:
            # Handle author format (might be list or string)
            author = enriched_paper.authors[0]
            if isinstance(author, str):
                author_parts = author.split()
                if len(author_parts) > 1:
                    # Try to get last name
                    first_author = author_parts[-1]
                else:
                    first_author = author_parts[0]

        year_str = str(enriched_paper.year) if enriched_paper.year else "Unknown"

        journal_clean = "Unknown"
        if enriched_paper.journal:
            # Clean journal name for filesystem
            journal_clean = "".join(
                c for c in enriched_paper.journal
                if c.isalnum() or c in " "
            ).replace(" ", "")
            if not journal_clean:
                journal_clean = "Unknown"

        readable_name = f"{first_author}-{year_str}-{journal_clean}"
        logger.info(f"  Generated name: {readable_name}")

        # Show enriched metrics
        if enriched_paper.citation_count is not None:
            logger.success(f"  Citations: {enriched_paper.citation_count}")
        if enriched_paper.journal_impact_factor is not None:
            logger.success(f"  Impact Factor: {enriched_paper.journal_impact_factor}")

        if not dry_run:
            # Convert existing flat metadata to structured format if needed
            if "id" not in existing_metadata or not isinstance(existing_metadata.get("id"), dict):
                # It's flat format, convert to structured
                structured = {
                    "id": {
                        "doi": existing_metadata.get("doi"),
                        "pmid": existing_metadata.get("pmid"),
                        "arxiv_id": existing_metadata.get("arxiv_id"),
                    },
                    "basic": {
                        "title": existing_metadata.get("title"),
                        "authors": existing_metadata.get("authors"),
                        "year": existing_metadata.get("year"),
                        "abstract": existing_metadata.get("abstract"),
                        "keywords": existing_metadata.get("keywords"),
                    },
                    "publication": {
                        "journal": existing_metadata.get("journal"),
                        "publisher": existing_metadata.get("publisher"),
                        "volume": existing_metadata.get("volume"),
                        "issue": existing_metadata.get("issue"),
                    },
                    "citation_count": {
                        "total": existing_metadata.get("citation_count"),
                    },
                    "url": {
                        "doi": f"https://doi.org/{doi}" if doi else None,
                        "publisher": existing_metadata.get("url"),
                    },
                    "path": {
                        "pdfs": [existing_metadata.get("pdf_path")] if existing_metadata.get("pdf_path") else [],
                    },
                    "system": {
                        "scitex_id": existing_metadata.get("scitex_id"),
                        "created_at": existing_metadata.get("created_at"),
                        "created_by": existing_metadata.get("created_by"),
                        "pdf_downloaded_at": existing_metadata.get("pdf_downloaded_at"),
                        "pdf_size_bytes": existing_metadata.get("pdf_size_bytes"),
                        "updated_at": existing_metadata.get("updated_at"),
                        "enriched_at": existing_metadata.get("enriched_at"),
                    }
                }
                # Use standardize_metadata to ensure all fields exist
                existing_metadata = standardize_metadata(structured)
            else:
                # Already structured, just standardize
                existing_metadata = standardize_metadata(existing_metadata)

            # Update with enriched data
            updated = False
            enrichment_source = "BibTeX enrichment" if bibtex_file else "Scholar API"

            # Basic fields
            if enriched_paper.title and not existing_metadata["basic"]["title"]:
                existing_metadata["basic"]["title"] = enriched_paper.title
                existing_metadata["basic"]["title_engines"] = enrichment_source
                updated = True

            if enriched_paper.authors and not existing_metadata["basic"]["authors"]:
                existing_metadata["basic"]["authors"] = enriched_paper.authors
                existing_metadata["basic"]["authors_engines"] = enrichment_source
                updated = True

            if enriched_paper.year and not existing_metadata["basic"]["year"]:
                existing_metadata["basic"]["year"] = enriched_paper.year
                existing_metadata["basic"]["year_engines"] = enrichment_source
                updated = True

            if enriched_paper.abstract and not existing_metadata["basic"]["abstract"]:
                existing_metadata["basic"]["abstract"] = enriched_paper.abstract
                existing_metadata["basic"]["abstract_engines"] = enrichment_source
                updated = True

            if enriched_paper.keywords and not existing_metadata["basic"]["keywords"]:
                existing_metadata["basic"]["keywords"] = enriched_paper.keywords
                existing_metadata["basic"]["keywords_engines"] = enrichment_source
                updated = True

            # Publication fields
            if enriched_paper.journal and not existing_metadata["publication"]["journal"]:
                existing_metadata["publication"]["journal"] = enriched_paper.journal
                existing_metadata["publication"]["journal_engines"] = enrichment_source
                updated = True

            if hasattr(enriched_paper, 'publisher') and enriched_paper.publisher and not existing_metadata["publication"]["publisher"]:
                existing_metadata["publication"]["publisher"] = enriched_paper.publisher
                existing_metadata["publication"]["publisher_engines"] = enrichment_source
                updated = True

            # Citation count
            if enriched_paper.citation_count is not None:
                existing_metadata["citation_count"]["total"] = enriched_paper.citation_count
                existing_metadata["citation_count"]["total_engines"] = enrichment_source
                updated = True

            # Impact factor
            if enriched_paper.journal_impact_factor is not None:
                existing_metadata["publication"]["impact_factor"] = enriched_paper.journal_impact_factor
                existing_metadata["publication"]["impact_factor_engines"] = "JCR 2024 database"
                updated = True

            # URLs
            if enriched_paper.url and not existing_metadata["url"]["publisher"]:
                existing_metadata["url"]["publisher"] = enriched_paper.url
                existing_metadata["url"]["publisher_engines"] = enrichment_source
                updated = True

            if updated:
                # Update system metadata
                existing_metadata["system"]["updated_at"] = datetime.now().isoformat()
                existing_metadata["system"]["enriched_at"] = datetime.now().isoformat()
                existing_metadata["system"]["enrichment_source"] = enrichment_source

                # Save updated metadata
                with open(metadata_file, 'w') as f:
                    json.dump(existing_metadata, f, indent=2, ensure_ascii=False)
                logger.success(f"  ✓ Updated metadata.json")

            # Fix symlink if needed
            if symlink.name != readable_name and readable_name != "Unknown-Unknown-Unknown":
                symlink.unlink()
                logger.info(f"  Removed old symlink: {symlink.name}")

                new_symlink = project_dir / readable_name
                if not new_symlink.exists():
                    new_symlink.symlink_to(f"../MASTER/{paper_id}")
                    logger.success(f"  ✓ Created new symlink: {readable_name}")
                else:
                    logger.warning(f"  Symlink already exists: {readable_name}")

    if dry_run:
        logger.info("\nDry run complete. Run without --dry-run to apply changes")
    else:
        logger.success(f"\n✓ Enrichment and fixing complete for project: {project_name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enrich library metadata and fix symlinks using Scholar modules"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project name to enrich and fix"
    )
    parser.add_argument(
        "--bibtex",
        help="Enriched BibTeX file to use as source (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    if args.debug:
        logging.set_level(logging.DEBUG)

    asyncio.run(
        enrich_and_fix_library(
            args.project,
            args.bibtex,
            args.dry_run
        )
    )


if __name__ == "__main__":
    main()

# EOF