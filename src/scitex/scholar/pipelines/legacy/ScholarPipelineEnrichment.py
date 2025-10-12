#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-12 01:23:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelineEnrichment.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelineEnrichment.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Enrich papers collection with metadata from multiple sources
  - Queries ScholarEngine for each paper (DOI, PMID, ArXiv ID, etc.)
  - Merges enrichment data (title, authors, abstract, citations, etc.)
  - Optionally adds journal impact factors (JCR database)
  - Preserves original data when enrichment fails

Dependencies:
  - packages:
    - scitex
    - pydantic
  - scripts:
    - ../metadata_engines/ScholarEngine.py
    - ../impact_factor/JCRImpactFactorEngine.py

IO:
  - input-files:
    - Papers collection (in-memory)
  - output-files:
    - Enriched Papers collection (in-memory)
    - Note: Does not save to disk, caller decides where to save
"""

"""Imports"""
from copy import deepcopy
from pathlib import Path
from typing import Dict, Optional

from scitex import logging

from ._ScholarPipelineBase import ScholarPipelineBase

logger = logging.getLogger(__name__)

"""Functions & Classes"""


class ScholarPipelineEnrichment(ScholarPipelineBase):
    """
    Enrich papers with metadata from multiple sources.

    Enriches papers with:
    - DOI, PMID, ArXiv ID
    - Title, authors, year, abstract, keywords
    - Journal, publisher, volume, issue, pages
    - Citation counts
    - PDF URLs
    - Journal impact factors (optional)
    """

    async def run(
        self, papers: "Papers", enrich_impact_factors: bool = True
    ) -> "Papers":
        """
        Enrich papers collection with metadata.

        Args:
            papers: Papers collection to enrich
            enrich_impact_factors: Whether to add journal impact factors

        Returns:
            Enriched Papers collection
        """
        from scitex.scholar.core.Papers import Papers

        enriched_list = []

        for paper in papers:
            try:
                # Use ScholarEngine to search and enrich
                results = await self.scholar_engine.search_async(
                    title=paper.metadata.basic.title,
                    year=paper.metadata.basic.year,
                    authors=(
                        paper.metadata.basic.authors[0]
                        if paper.metadata.basic.authors
                        else None
                    ),
                )

                # Merge enrichment data
                enriched_paper = self._merge_enrichment_data(paper, results)
                enriched_list.append(enriched_paper)
                title = paper.metadata.basic.title or "No title"
                logger.info(f"Enriched: {title[:50]}...")

            except Exception as e:
                title = paper.metadata.basic.title or "No title"
                logger.warning(
                    f"Failed to enrich paper '{title[:50]}...': {e}"
                )
                enriched_list.append(paper)  # Keep original if enrichment fails

        enriched_papers = Papers(enriched_list, project=papers.project)

        # Add impact factors as post-processing step
        if enrich_impact_factors:
            enriched_papers = self._enrich_impact_factors(enriched_papers)

        return enriched_papers

    def _merge_enrichment_data(self, paper: "Paper", results: Dict) -> "Paper":
        """Merge enrichment results into paper object."""
        enriched = deepcopy(paper)

        if not results:
            return enriched

        # ID section
        if "id" in results:
            if results["id"].get("doi") and not enriched.metadata.id.doi:
                enriched.metadata.set_doi(results["id"]["doi"])
            if results["id"].get("pmid") and not enriched.metadata.id.pmid:
                enriched.metadata.id.pmid = results["id"]["pmid"]
            if (
                results["id"].get("arxiv_id")
                and not enriched.metadata.id.arxiv_id
            ):
                enriched.metadata.id.arxiv_id = results["id"]["arxiv_id"]

        # Basic metadata section
        if "basic" in results:
            # Always update abstract if found (key enrichment goal)
            if results["basic"].get("abstract"):
                enriched.metadata.basic.abstract = results["basic"]["abstract"]

            # Update title if more complete
            if results["basic"].get("title"):
                new_title = results["basic"]["title"]
                current_title = enriched.metadata.basic.title or ""
                if not current_title or len(new_title) > len(current_title):
                    enriched.metadata.basic.title = new_title

            # Update authors if found
            if (
                results["basic"].get("authors")
                and not enriched.metadata.basic.authors
            ):
                enriched.metadata.basic.authors = results["basic"]["authors"]

            # Update year if found
            if (
                results["basic"].get("year")
                and not enriched.metadata.basic.year
            ):
                enriched.metadata.basic.year = results["basic"]["year"]

            # Update keywords if found
            if (
                results["basic"].get("keywords")
                and not enriched.metadata.basic.keywords
            ):
                enriched.metadata.basic.keywords = results["basic"]["keywords"]

        # Publication metadata
        if "publication" in results:
            if (
                results["publication"].get("journal")
                and not enriched.metadata.publication.journal
            ):
                enriched.metadata.publication.journal = results["publication"][
                    "journal"
                ]
            if (
                results["publication"].get("publisher")
                and not enriched.metadata.publication.publisher
            ):
                enriched.metadata.publication.publisher = results[
                    "publication"
                ]["publisher"]
            if (
                results["publication"].get("volume")
                and not enriched.metadata.publication.volume
            ):
                enriched.metadata.publication.volume = results["publication"][
                    "volume"
                ]
            if (
                results["publication"].get("issue")
                and not enriched.metadata.publication.issue
            ):
                enriched.metadata.publication.issue = results["publication"][
                    "issue"
                ]
            if (
                results["publication"].get("pages")
                and not enriched.metadata.publication.pages
            ):
                enriched.metadata.publication.pages = results["publication"][
                    "pages"
                ]

        # Citation metadata
        if "citation_count" in results:
            count = results["citation_count"].get("count") or results[
                "citation_count"
            ].get("total")
            if count:
                # Always take the maximum citation count
                current_count = enriched.metadata.citation_count.total or 0
                if not current_count or count > current_count:
                    enriched.metadata.citation_count.total = count

        # URL metadata
        if "url" in results:
            if results["url"].get("pdf"):
                pdf_url = results["url"]["pdf"]
                if not any(
                    p.get("url") == pdf_url for p in enriched.metadata.url.pdfs
                ):
                    enriched.metadata.url.pdfs.append(
                        {"url": pdf_url, "source": "enrichment"}
                    )
            if (
                results["url"].get("url")
                and not enriched.metadata.url.publisher
            ):
                enriched.metadata.url.publisher = results["url"]["url"]

        return enriched

    def _enrich_impact_factors(self, papers: "Papers") -> "Papers":
        """Add journal impact factors to papers."""
        try:
            from scitex.scholar.impact_factor import JCRImpactFactorEngine

            jcr_engine = JCRImpactFactorEngine()
            papers = jcr_engine.enrich_papers(papers)
            return papers
        except Exception as e:
            logger.debug(
                f"JCR engine unavailable: {e}, falling back to calculation method"
            )

        return papers


def main(args):
    """Run enrichment pipeline"""
    import asyncio
    from scitex.scholar.storage import BibTeXHandler

    if not args.bibtex:
        logger.error("No BibTeX file provided. Use --bibtex")
        return 1

    bibtex_path = Path(args.bibtex)
    if not bibtex_path.exists():
        logger.error(f"BibTeX file not found: {bibtex_path}")
        return 1

    logger.info(f"Enriching papers from: {bibtex_path}")
    logger.info(f"  Output: {args.output or 'input_enriched.bib'}")
    logger.info(f"  Impact factors: {args.impact_factors}")

    # Load papers
    handler = BibTeXHandler()
    papers = handler.papers_from_bibtex(bibtex_path)

    from scitex.scholar.core.Papers import Papers
    papers_collection = Papers(papers)

    # Create pipeline
    pipeline = ScholarPipelineEnrichment()

    # Run enrichment
    enriched = asyncio.run(
        pipeline.run(papers_collection, enrich_impact_factors=args.impact_factors)
    )

    # Save enriched BibTeX
    output_path = Path(args.output) if args.output else bibtex_path.parent / f"{bibtex_path.stem}_enriched.bib"
    handler.papers_to_bibtex(enriched, output_path)

    logger.success(f"Enrichment complete: {len(enriched)} papers enriched")
    logger.success(f"Saved to: {output_path}")
    return 0


def parse_args() -> "argparse.Namespace":
    """Parse command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enrich papers with metadata from multiple sources"
    )
    parser.add_argument(
        "--bibtex",
        type=str,
        required=True,
        help="Path to BibTeX file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output BibTeX path (default: {input}_enriched.bib)",
    )
    parser.add_argument(
        "--impact-factors",
        action="store_true",
        default=True,
        help="Include journal impact factors (default: True)",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

"""
Usage Examples:
    # Enrich papers from BibTeX file
    python -m scitex.scholar.pipelines.ScholarPipelineEnrichment \
        --bibtex papers.bib \
        --output papers_enriched.bib

    # Enrich without impact factors
    python -m scitex.scholar.pipelines.ScholarPipelineEnrichment \
        --bibtex papers.bib \
        --no-impact-factors

    # Library usage (recommended)
    from scitex.scholar.pipelines import ScholarPipelineEnrichment
    pipeline = ScholarPipelineEnrichment()
    enriched = await pipeline.run(papers, enrich_impact_factors=True)
"""

# EOF
