#!/usr/bin/env python3
"""DOI-related CLI operations for Scholar."""

from pathlib import Path
from scitex import logging

logger = logging.getLogger(__name__)


async def handle_doi_operations(args, scholar):
    """Handle operations on DOIs."""
    # Collect all DOIs
    dois = []
    if args.doi:
        dois.append(args.doi)
    if args.dois:
        dois.extend(args.dois)

    if not dois:
        logger.error("No DOIs specified")
        return 1

    logger.info(f"Processing {len(dois)} DOIs")

    # Download PDFs if requested
    if args.download:
        results = await scholar.download_pdfs_from_dois_async(dois)
        logger.info(f"Downloaded: {results['downloaded']}, Failed: {results['failed']}")

    # Enrich if requested (create Papers from DOIs first)
    if args.enrich:
        from scitex.scholar.core.Paper import Paper
        from scitex.scholar.core.Papers import Papers

        papers_list = []
        for doi in dois:
            p = Paper()
            p.metadata.id.doi = doi
            papers_list.append(p)
        papers = Papers(papers_list, project=args.project)

        logger.info("Enriching papers from DOIs...")
        papers = scholar.enrich_papers(papers)

        # Save enriched data
        if args.output:
            output_path = Path(args.output)
            scholar.save_papers_as_bibtex(papers, output_path)
            logger.success(f"Saved enriched papers to: {output_path}")

        # Save to library if project specified
        if args.project:
            saved_ids = scholar.save_papers_to_library(papers)
            logger.info(f"Saved {len(saved_ids)} papers to library")

    return 0
