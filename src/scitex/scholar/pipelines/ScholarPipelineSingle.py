#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-13 07:24:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pipelines/ScholarPipelineSingle.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pipelines/ScholarPipelineSingle.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Orchestrates full paper acquisition pipeline from query to storage
  - Single command: query (DOI/title) + project → complete paper in library
  - Coordinates all workers: metadata, URLs, download, extraction, storage
  - Supports resumable processing (checks existing data at each step)
  - Creates MASTER/{8-digit-ID}/ and project symlinks

Dependencies:
  - packages:
    - playwright
    - pydantic

IO:
  - input-files:
    - None (starts from query string)

  - output-files:
    - library/MASTER/{paper_id}/metadata.json
    - library/MASTER/{paper_id}/main.pdf
    - library/MASTER/{paper_id}/content.txt
    - library/{project}/{paper_id} -> ../MASTER/{paper_id}
"""

"""Imports"""
import argparse
import asyncio
import hashlib
from pathlib import Path
from typing import Optional

from scitex import logging
from scitex.scholar.core import Paper
from scitex.scholar.storage import PaperIO

logger = logging.getLogger(__name__)

"""Functions & Classes"""
class ScholarPipelineSingle:
    """Orchestrates full paper acquisition pipeline"""

    def __init__(
        self, browser_mode: str = "interactive", chrome_profile: str = "system"
    ):
        self.name = self.__class__.__name__
        self.browser_mode = browser_mode
        self.chrome_profile = chrome_profile

    def _link_to_project(
        self, paper: Paper, project: str, io: PaperIO
    ) -> Path:
        """Create human-readable symlink in project directory.

        Uses entry_name template from PathManager (PATH_STRUCTURE):
        PDF-{n_pdfs:02d}_CC-{citation_count:06d}_IF-{impact_factor:03d}_{year:04d}_{first_author}_{journal_name}

        Args:
            paper: Paper object
            project: Project name
            io: PaperIO instance

        Returns:
            Path to created symlink
        """
        from scitex.scholar import ScholarConfig

        config = ScholarConfig()
        project_dir = config.path_manager.get_library_project_dir(project)

        # Gather data for entry name
        pdf_files = list(io.paper_dir.glob("*.pdf"))
        n_pdfs = len(pdf_files)
        citation_count = paper.metadata.citation_count.total or 0
        impact_factor = int(paper.metadata.publication.impact_factor or 0)
        year = paper.metadata.basic.year or 0
        first_author = (
            paper.metadata.basic.authors[0].split()[-1]
            if paper.metadata.basic.authors
            else "Unknown"
        )
        journal_name = (
            paper.metadata.publication.short_journal
            or paper.metadata.publication.journal
            or "Unknown"
        )

        # Use PathManager to generate entry name (single source of truth)
        entry_name = config.path_manager.get_library_project_entry_dirname(
            n_pdfs=n_pdfs,
            citation_count=citation_count,
            impact_factor=impact_factor,
            year=year,
            first_author=first_author,
            journal_name=journal_name,
        )

        # Create symlink using scitex.path.symlink (handles logging)
        import scitex as stx

        symlink_path = project_dir / entry_name
        target_path = Path("../MASTER") / paper.container.library_id

        # Use scitex.path.symlink with overwrite and relative path
        stx.path.symlink(
            src=target_path, dst=symlink_path, overwrite=True, relative=True
        )

        return symlink_path

    def _generate_paper_id(self, doi: str) -> str:
        """Generate 8-digit library ID from DOI

        Args:
            doi: DOI string

        Returns:
            8-character hex ID (e.g., "B58290B2")
        """
        content = f"DOI:{doi}"
        return hashlib.md5(content.encode()).hexdigest()[:8].upper()

    def _merge_metadata_into_paper(
        self, paper: Paper, metadata_dict: dict
    ) -> None:
        """Merge metadata dictionary from ScholarEngine into Paper object.

        Args:
            paper: Paper object to update
            metadata_dict: Dictionary from ScholarEngine.search_async()
        """

        # Helper to safely update field with engine tracking and type conversion
        def update_field(section, field_name, value, engines):
            if value is not None:
                # Convert types to match Paper model expectations
                # IDs should be strings
                if section == "id" and not isinstance(value, str):
                    value = str(value)

                # Year should be integer
                if field_name == "year" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        logger.warning(
                            f"{self.name}: Could not convert year '{value}' to int"
                        )
                        return

                # Citation counts should be integers
                if section == "citation_count" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        logger.warning(
                            f"{self.name}: Could not convert citation count '{value}' to int"
                        )
                        return

                try:
                    section_obj = getattr(paper.metadata, section)
                    setattr(section_obj, field_name, value)
                    setattr(section_obj, f"{field_name}_engines", engines)
                except Exception as e:
                    logger.warning(
                        f"{self.name}: Could not set {section}.{field_name}: {e}"
                    )

        # ID section
        if "id" in metadata_dict:
            id_data = metadata_dict["id"]
            for field in [
                "doi",
                "arxiv_id",
                "pmid",
                "corpus_id",
                "semantic_id",
                "ieee_id",
                "scholar_id",
            ]:
                if field in id_data:
                    update_field(
                        "id",
                        field,
                        id_data[field],
                        id_data.get(f"{field}_engines", []),
                    )

        # Basic section
        if "basic" in metadata_dict:
            basic_data = metadata_dict["basic"]
            for field in [
                "title",
                "authors",
                "year",
                "abstract",
                "keywords",
                "type",
            ]:
                if field in basic_data:
                    update_field(
                        "basic",
                        field,
                        basic_data[field],
                        basic_data.get(f"{field}_engines", []),
                    )

        # Citation count section
        if "citation_count" in metadata_dict:
            cc_data = metadata_dict["citation_count"]
            # Handle total
            if "total" in cc_data:
                update_field(
                    "citation_count",
                    "total",
                    cc_data["total"],
                    cc_data.get("total_engines", []),
                )
            # Handle year-specific counts (convert "2015" → "y2015" for Pydantic model)
            for year in range(2015, 2026):
                year_str = str(year)
                year_field = f"y{year}"
                if year_str in cc_data:
                    update_field(
                        "citation_count",
                        year_field,
                        cc_data[year_str],
                        cc_data.get(f"{year_str}_engines", []),
                    )

        # Publication section
        if "publication" in metadata_dict:
            pub_data = metadata_dict["publication"]
            for field in [
                "journal",
                "short_journal",
                "impact_factor",
                "issn",
                "volume",
                "issue",
                "first_page",
                "last_page",
                "pages",
                "publisher",
            ]:
                if field in pub_data:
                    update_field(
                        "publication",
                        field,
                        pub_data[field],
                        pub_data.get(f"{field}_engines", []),
                    )

        # URL section
        if "url" in metadata_dict:
            url_data = metadata_dict["url"]
            for field in ["doi", "publisher", "arxiv", "corpus_id"]:
                if field in url_data:
                    update_field(
                        "url",
                        field,
                        url_data[field],
                        url_data.get(f"{field}_engines", []),
                    )

        logger.debug(f"{self.name}: Merged metadata into Paper object")

    def _enrich_impact_factor(self, paper: Paper) -> None:
        """Add journal impact factor to paper metadata if not present.

        Args:
            paper: Paper object to enrich
        """
        # Skip if already has impact factor
        if paper.metadata.publication.impact_factor:
            logger.debug(f"{self.name}: Impact factor already present")
            return

        # Need journal name to lookup impact factor
        journal = (
            paper.metadata.publication.short_journal
            or paper.metadata.publication.journal
        )

        if not journal:
            logger.debug(f"{self.name}: No journal name, skipping IF lookup")
            return

        try:
            from scitex.scholar.impact_factor import ImpactFactorEngine

            if_engine = ImpactFactorEngine()
            metrics = if_engine.get_metrics(journal)

            if metrics and metrics.get("impact_factor"):
                paper.metadata.publication.impact_factor = metrics[
                    "impact_factor"
                ]
                paper.metadata.publication.impact_factor_engines = [
                    metrics.get("source", "JCR")
                ]
                logger.info(
                    f"{self.name}: Impact factor added: {metrics['impact_factor']} (from {metrics.get('source', 'JCR')})"
                )
            else:
                logger.debug(
                    f"{self.name}: No impact factor found for journal: {journal}"
                )

        except Exception as e:
            logger.debug(f"{self.name}: Impact factor lookup failed: {e}")

    async def process_single_paper(
        self,
        doi_or_title: str,
        project: Optional[str] = None,
        force: bool = False,
    ) -> Paper:
        """Process single paper from query (DOI or Title) to complete storage.

        Pipeline:
        1. Resolve DOI (if doi_or_title is title)
        2. Create Paper object with 8-digit ID
        3. Resolve metadata (ScholarEngine.search_async)
        4. Enrich impact factor (ImpactFactorEngine)
        5. Find PDF URLs
        6. Download PDF (with manual mode support)
        7. Extract content
        8. Save to MASTER/{8-digit-ID}/
        9. Link to project (if specified)

        Args:
            doi_or_title: DOI or title string
            project: Optional project name for symlinking
            force: If True, ignore existing files and force fresh processing

        Returns:
            Tuple of (Complete Paper object, symlink_path)
        """
        logger.info(f"{self.name}: Processing Query: {doi_or_title}")

        # Step 1: Determine if doi_or_title is DOI or title
        is_doi = doi_or_title.strip().startswith("10.")
        doi = doi_or_title.strip() if is_doi else None

        # Step 2: Create Paper
        paper = Paper()

        if doi:
            logger.info(f"{self.name}: Using DOI: {doi}")
            paper.metadata.id.doi = doi
            paper.metadata.id.doi_engines = ["user_input"]
        else:
            logger.info(f"{self.name}: Title Query: {doi_or_title}")

            # Use ScholarEngine to resolve DOI from title
            from scitex.scholar.metadata_engines import ScholarEngine

            engine = ScholarEngine()
            metadata_dict = await engine.search_async(title=doi_or_title)

            if metadata_dict and metadata_dict.get("id", {}).get("doi"):
                doi = metadata_dict["id"]["doi"]
                paper.metadata.id.doi = doi
                paper.metadata.id.doi_engines = metadata_dict["id"].get(
                    "doi_engines", ["ScholarEngine"]
                )
                logger.success(f"{self.name}: Resolved DOI from title: {doi}")

                # Merge other metadata while we have it
                self._merge_metadata_into_paper(paper, metadata_dict)
            else:
                logger.error(
                    f"{self.name}: Could not resolve DOI from title: {doi_or_title}"
                )
                raise ValueError(f"No DOI found for title: {doi_or_title}")

        # Step 3: Generate 8-digit library ID
        paper_id = self._generate_paper_id(paper.metadata.id.doi)
        paper.container.library_id = paper_id
        logger.info(f"{self.name}: Library ID: {paper_id}")

        # Step 4: Initialize PaperIO
        io = PaperIO(paper)
        logger.info(f"{self.name}: Paper directory: {io.paper_dir}")

        # Step 4.5: Set up per-paper logging
        paper_log_file = io.paper_dir / "logs" / "pipeline.log"

        with logger.to(paper_log_file):
            # Step 5: Metadata resolution (check → process → save)
            if not io.has_metadata() or force:
                logger.info(f"{self.name}: Resolving metadata...")

                # Use ScholarEngine to enrich metadata
                from scitex.scholar.metadata_engines import ScholarEngine

                engine = ScholarEngine()
                metadata_dict = await engine.search_async(
                    doi=paper.metadata.id.doi
                )

                if metadata_dict:
                    # Merge engine results into paper metadata
                    self._merge_metadata_into_paper(paper, metadata_dict)

                    # Add impact factor if not already present
                    self._enrich_impact_factor(paper)

                    io.save_metadata()
                    logger.success(
                        f"{self.name}: Metadata enriched from search engines"
                    )
                else:
                    # Fallback: save basic metadata
                    paper.metadata.basic.title = "Pending metadata resolution"
                    paper.metadata.basic.title_engines = ["pending"]
                    io.save_metadata()
                    logger.warning(
                        f"{self.name}: No metadata found from engines, saved basic metadata"
                    )
            else:
                logger.info(f"{self.name}: Metadata exists, loading...")
                paper = io.load_metadata()

                # Check if metadata needs enrichment (title is "Pending metadata resolution")
                if paper.metadata.basic.title == "Pending metadata resolution":
                    logger.info(f"{self.name}: Enriching existing metadata...")

                    from scitex.scholar.metadata_engines import ScholarEngine

                    engine = ScholarEngine()
                    metadata_dict = await engine.search_async(
                        doi=paper.metadata.id.doi
                    )

                    if metadata_dict:
                        self._merge_metadata_into_paper(paper, metadata_dict)

                        # Add impact factor if not already present
                        self._enrich_impact_factor(paper)

                        io.save_metadata()
                        logger.success(
                            f"{self.name}: Metadata enriched from search engines"
                        )

            # Step 6: Setup browser (needed for both URL finding and downloading)
            browser_manager = None
            context = None

            # Check if we need browser (no URLs OR no PDF)
            needs_browser = not paper.metadata.url.pdfs or not io.has_pdf()

            if needs_browser:
                from scitex.scholar import (
                    ScholarAuthManager,
                    ScholarBrowserManager,
                    ScholarURLFinder,
                )
                from scitex.scholar.auth import AuthenticationGateway

                logger.info(
                    f"{self.name}: Setting up browser (profile: {self.chrome_profile})..."
                )
                auth_manager = ScholarAuthManager()
                browser_manager = ScholarBrowserManager(
                    chrome_profile_name=self.chrome_profile,
                    browser_mode=self.browser_mode,
                    auth_manager=auth_manager,
                )
                browser, context = (
                    await browser_manager.get_authenticated_browser_and_context_async()
                )

            # Step 6a: PDF URL finding (if needed)
            if not paper.metadata.url.pdfs or force:
                logger.info(f"{self.name}: Finding PDF URLs...")

                # TESTING: Re-enable OpenURL with debug logging to find crash cause
                auth_gateway = AuthenticationGateway(
                    auth_manager=auth_manager,
                    browser_manager=browser_manager,
                )
                try:
                    url_context = await auth_gateway.prepare_context_async(
                        doi=paper.metadata.id.doi,
                        context=context,
                    )
                    publisher_url = (
                        url_context.url
                        if url_context
                        else paper.metadata.id.doi
                    )
                except Exception as e:
                    logger.warning(f"{self.name}: Auth gateway failed: {e}")
                    publisher_url = paper.metadata.id.doi

                # Find PDF URLs
                url_finder = ScholarURLFinder(context)
                urls = await url_finder.find_pdf_urls(publisher_url)

                paper.metadata.url.pdfs = urls
                paper.metadata.url.pdfs_engines = ["ScholarURLFinder"]
                io.save_metadata()
                logger.info(f"{self.name}: Found {len(urls)} PDF URL(s)")
            else:
                logger.info(
                    f"{self.name}: PDF URLs exist in metadata ({len(paper.metadata.url.pdfs)} URLs)"
                )

            # Step 7: Download PDF (if URLs exist but no PDF downloaded)
            if (not io.has_pdf() or force) and paper.metadata.url.pdfs:
                logger.info(f"{self.name}: Downloading PDF...")

                from scitex.scholar.pdf_download import ScholarPDFDownloader

                downloader = ScholarPDFDownloader(context)

                # Extract URL from metadata structure
                pdf_url = paper.metadata.url.pdfs[0]
                if isinstance(pdf_url, dict):
                    pdf_url = pdf_url["url"]

                logger.info(f"{self.name}: PDF URL: {pdf_url}")

                # Get authenticated cookies
                auth_gateway = AuthenticationGateway(
                    auth_manager=auth_manager,
                    browser_manager=browser_manager,
                )
                try:
                    # Might not be available in Gateway
                    url_context = await auth_gateway.prepare_context_async(
                        doi=paper.metadata.id.doi,
                        context=context,
                    )
                except Exception as e:
                    logger.warn(str(e))

                # Try downloading to MASTER directory first (Chrome PDF saves directly)
                temp_pdf_path = io.paper_dir / "temp.pdf"
                downloaded_file = await downloader.download_from_url(
                    pdf_url,
                    output_path=temp_pdf_path,
                    doi=paper.metadata.id.doi,
                )

                if downloaded_file:
                    # Check if file was downloaded to MASTER/temp.pdf or downloads/UUID
                    if (
                        downloaded_file == temp_pdf_path
                        and temp_pdf_path.exists()
                    ):
                        # Chrome PDF downloaded directly to MASTER - just rename
                        import shutil

                        main_pdf = io.get_pdf_path()
                        shutil.move(str(temp_pdf_path), str(main_pdf))
                        # Update paper metadata
                        paper.metadata.path.pdfs = [str(main_pdf)]
                        paper.container.pdf_size_bytes = (
                            main_pdf.stat().st_size
                        )
                        io.save_metadata()
                        logger.success(
                            f"{self.name}: PDF downloaded directly to MASTER"
                        )
                    else:
                        # UUID file from downloads directory - use normal flow
                        io.save_pdf(downloaded_file)
                        io.save_metadata()
                    logger.success(f"{self.name}: PDF downloaded and saved")
                    logger.info(f"{self.name}: Updated metadata.path.pdfs")
                else:
                    # Check if PDF was manually downloaded to downloads directory
                    logger.warning(
                        f"{self.name}: Automated download returned None"
                    )
                    logger.info(
                        f"{self.name}: Checking downloads directory for manual downloads..."
                    )

                    from scitex.scholar import ScholarConfig

                    config = ScholarConfig()
                    downloads_dir = config.get_library_downloads_dir()

                    # Find recent PDFs (last 10 minutes)
                    import time

                    current_time = time.time()
                    recent_pdfs = []
                    for pdf_path in downloads_dir.glob("*"):
                        if (
                            pdf_path.is_file()
                            and pdf_path.stat().st_size > 100_000
                        ):
                            age_seconds = (
                                current_time - pdf_path.stat().st_mtime
                            )
                            if age_seconds < 600:
                                recent_pdfs.append((pdf_path, age_seconds))

                    if recent_pdfs:
                        # Use most recent PDF
                        recent_pdfs.sort(key=lambda x: x[1])
                        latest_pdf = recent_pdfs[0][0]
                        logger.info(
                            f"{self.name}: Found recent PDF: {latest_pdf.name} ({latest_pdf.stat().st_size / 1e6:.2f} MB)"
                        )
                        logger.info(
                            f"{self.name}: Assuming this is the manually downloaded PDF"
                        )

                        # Save to MASTER directory
                        io.save_pdf(latest_pdf)
                        io.save_metadata()
                        logger.success(
                            f"{self.name}: Manually downloaded PDF saved to MASTER"
                        )
                        logger.info(f"{self.name}: Updated metadata.path.pdfs")
                    else:
                        logger.warning(
                            f"{self.name}: No recent PDFs found in downloads directory"
                        )
                        logger.warning(
                            f"{self.name}: PDF download incomplete - manual intervention required"
                        )
            elif io.has_pdf():
                logger.info(
                    f"{self.name}: PDF already exists, skipping download"
                )

            # Close browser if it was opened
            if browser_manager:
                await browser_manager.close()

            # Step 8: Content extraction (check → process → save)
            if io.has_pdf() and (not io.has_content() or force):
                logger.info(f"{self.name}: Extracting content...")
                import scitex

                try:
                    # Use scitex.io.load() with ext='pdf' for UUID files
                    pdf_path = io.get_pdf_path()
                    content = scitex.io.load(str(pdf_path), ext="pdf")
                    if hasattr(content, "full_text"):
                        io.save_text(content.full_text)
                        logger.info(f"{self.name}: Content extracted")
                except Exception as e:
                    logger.warning(
                        f"{self.name}: Content extraction failed: {e}"
                    )

            # Step 9: Project linking (if specified)
            if project:
                logger.info(f"{self.name}: Linking to project: {project}")
                symlink_path = self._link_to_project(paper, project, io)
            else:
                symlink_path = None

            # Final status
            logger.info(f"{self.name}: Pipeline complete!")
            status = io.get_all_files()
            for filename, exists in status.items():
                logger.info(f"  {'✓' if exists else '✗'} {filename}")

            # logger.success(f"{self.name}: Paper stored at: {io.paper_dir}")

            # Return both paper and symlink path for main() to display
            return paper, symlink_path


def main(args):
    """Run single paper pipeline"""

    pipeline_single = ScholarPipelineSingle(
        browser_mode=args.browser_mode, chrome_profile=args.chrome_profile
    )

    # Run pipeline (returns tuple of paper and symlink_path)
    paper, symlink_path = asyncio.run(
        pipeline_single.process_single_paper(
            doi_or_title=args.doi_or_title,
            project=args.project,
            force=args.force,
        )
    )

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Orchestrate full paper acquisition pipeline"
    )
    parser.add_argument(
        "--doi-or-title",
        type=str,
        required=True,
        help="DOI or paper title",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Project name for symlinking (optional)",
    )
    parser.add_argument(
        "--browser-mode",
        type=str,
        choices=["stealth", "interactive"],
        default="stealth",
        help="Browser mode (default: interactive)",
    )
    parser.add_argument(
        "--chrome-profile",
        type=str,
        required=True,
        # default="system",
        help="Chrome profile name (default: system, parallel workers: system_worker_0-7)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        default=False,
        help="Force fresh processing, ignore existing files",
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
Usage:


# With Title
python -m scitex.scholar.pipelines.ScholarPipelineSingle \
    --doi-or-title "Epileptic seizure forecasting with long short-term memory (LSTM) neural networks" \
    --project neurovista \
    --chrome-profile system \
    --browser-mode interactive \
    --force

# With DOI; Neurology; Manual Download required
python -m scitex.scholar.pipelines.ScholarPipelineSingle \
    --doi-or-title "10.1212/wnl.0000000000200348" \
    --project neurovista \
    --chrome-profile system \
    --browser-mode interactive
"""

# EOF
