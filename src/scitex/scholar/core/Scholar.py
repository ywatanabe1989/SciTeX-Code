#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-10 06:55:10 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Scholar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Unified Scholar class for scientific literature management.

This is the main entry point for all scholar functionality, providing:
- Simple, intuitive API
- Smart defaults
- Method chaining
- Progressive disclosure of advanced features
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from copy import deepcopy
from scitex import logging
import shutil

# PDF extraction is now handled by scitex.io
from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig

# Updated imports for current architecture
from scitex.scholar.auth import ScholarAuthManager
from scitex.browser.debugging import browser_logger
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.storage import LibraryManager
from scitex.scholar.storage import ScholarLibrary
from scitex.scholar.engines.ScholarEngine import ScholarEngine
from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader
from scitex.scholar.auth.core.AuthenticationGateway import AuthenticationGateway
from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder

# from scitex.scholar.url.ScholarURLFinderParallel import ScholarURLFinderParallel

import asyncio
import nest_asyncio
from scitex.scholar.engines.JCRImpactFactorEngine import JCRImpactFactorEngine

from .Papers import Papers

logger = logging.getLogger(__name__)


class Scholar:
    """
    Main interface for SciTeX Scholar - scientific literature management made simple.

    By default, papers are automatically enriched with:
    - Journal impact factors from impact_factor package (2024 JCR data)
    - Citation counts from Semantic Scholar (via DOI/title matching)

    Example usage:
        # Basic search with automatic enrichment
        scholar = Scholar()
        papers = scholar.search("deep learning neuroscience")
        # Papers now have impact_factor and citation_count populated
        papers.save("my_pac.bib")

        # Disable automatic enrichment if needed
        config = ScholarConfig(enable_auto_enrich=False)
        scholar = Scholar(config=config)

        # Search specific source
        papers = scholar.search("transformer models", sources='arxiv')

        # Advanced workflow
        papers = scholar.search("transformer models", year_min=2020) \\
                      .filter(min_citations=50) \\
                      .sort_by("impact_factor") \\
                      .save("transformers.bib")

        # Local library
        scholar._index_local_pdfs("./my_papers")
        local_papers = scholar.search_local("attention mechanism")
    """

    @property
    def name(self):
        """Class name for logging."""
        return self.__class__.__name__

    def __init__(
        self,
        config: Optional[Union[ScholarConfig, str, Path]] = None,
        project: Optional[str] = None,
        project_description: Optional[str] = None,
        browser_mode: Optional[str] = None,
    ):
        """
        Initialize Scholar with configuration.

        Args:
            config: Can be:
                   - ScholarConfig instance
                   - Path to YAML config file (str or Path)
                   - None (uses ScholarConfig.load() to find config)
            project: Default project name for operations
            project_description: Optional description for the project
            browser_mode: Browser mode ('stealth', 'interactive', 'manual')
        """

        self.config = self._init_config(config)

        # Store browser mode for later use
        self.browser_mode = browser_mode or "stealth"

        # Set project and workspace
        self.project = self.config.resolve("project", project, "default")
        self.workspace_dir = self.config.path_manager.workspace_dir

        # Auto-create project directory if it doesn't exist
        if project:
            self._ensure_project_exists(project, project_description)

        # Initialize service components (lazy loading for better performance)
        # Use mangled names for private properties
        self._Scholar__scholar_engine = (
            None  # Replaces DOIResolver and LibraryEnricher
        )
        self._Scholar__auth_manager = None
        self._Scholar__browser_manager = None
        self._Scholar__library_manager = None
        self._Scholar__library = (
            None  # ScholarLibrary for high-level operations
        )

        # Show user-friendly initialization message with library location
        library_path = self.config.get_library_dir()
        if project:
            project_path = library_path / project
            logger.info(
                f"Scholar initialized with project '{project}' at {project_path}"
            )
        else:
            logger.info(f"Scholar initialized (library: {library_path})")

    # ----------------------------------------
    # Enrichers
    # ----------------------------------------
    async def enrich_papers_async(self, papers: Papers) -> Papers:
        """Async version of enrich_papers for use in async contexts.

        Args:
            papers: Papers collection to enrich.

        Returns:
            Enriched Papers collection
        """
        enriched_list = []

        for paper in papers:
            try:
                # Use ScholarEngine to search and enrich
                results = await self._scholar_engine.search_async(
                    title=paper.metadata.basic.title,
                    year=paper.metadata.basic.year,
                    authors=(
                        paper.metadata.basic.authors[0]
                        if paper.metadata.basic.authors
                        else None
                    ),
                )

                # Create a copy to avoid modifying original
                enriched_paper = self._merge_enrichment_data(paper, results)
                enriched_list.append(enriched_paper)
                title = paper.metadata.basic.title or "No title"
                logger.info(f"Enriched: {title[:50]}...")

            except Exception as e:
                title = paper.metadata.basic.title or "No title"
                logger.warning(
                    f"Failed to enrich paper '{title[:50]}...': {e}"
                )
                enriched_list.append(
                    paper
                )  # Keep original if enrichment fails

        enriched_papers = Papers(enriched_list, project=self.project)

        # Add impact factors as post-processing step
        if self.config.resolve("enrich_impact_factors", None, True):
            enriched_papers = self._enrich_impact_factors(enriched_papers)

        return enriched_papers

    def enrich_papers(
        self, papers: Optional[Papers] = None
    ) -> Union[Papers, Dict[str, int]]:
        """Enrich papers with metadata from multiple sources.

        Args:
            papers: Papers collection to enrich. If None, enriches all papers in current project.

        Returns:
            - If papers provided: Returns enriched Papers collection
            - If no papers: Returns dict with enrichment statistics for project
        """

        # If no papers provided, enrich entire project
        if papers is None:
            return self._enrich_current_project()

        # Enrich the provided papers collection
        enriched_list = []

        nest_asyncio.apply()  # Allow nested event loops

        for paper in papers:
            try:
                # Use ScholarEngine to search and enrich
                results = asyncio.run(
                    self._scholar_engine.search_async(
                        title=paper.metadata.basic.title,
                        year=paper.metadata.basic.year,
                        authors=(
                            paper.metadata.basic.authors[0]
                            if paper.metadata.basic.authors
                            else None
                        ),
                    )
                )

                # Create a copy to avoid modifying original
                enriched_paper = self._merge_enrichment_data(paper, results)
                enriched_list.append(enriched_paper)
                title = paper.metadata.basic.title or "No title"
                logger.info(f"Enriched: {title[:50]}...")

            except Exception as e:
                title = paper.metadata.basic.title or "No title"
                logger.warning(
                    f"Failed to enrich paper '{title[:50]}...': {e}"
                )
                enriched_list.append(
                    paper
                )  # Keep original if enrichment fails

        enriched_papers = Papers(enriched_list, project=self.project)

        # Add impact factors as post-processing step
        if self.config.resolve("enrich_impact_factors", None, True):
            enriched_papers = self._enrich_impact_factors(enriched_papers)

        return enriched_papers

    def _enrich_impact_factors(self, papers: "Papers") -> "Papers":
        """Add journal impact factors to papers.

        Args:
            papers: Papers collection to enrich with impact factors

        Returns:
            Papers collection with impact factors added where available
        """
        try:
            # Try JCR database first (fast)
            jcr_engine = JCRImpactFactorEngine()
            papers = jcr_engine.enrich_papers(papers)
            return papers
        except Exception as e:
            logger.debug(
                f"JCR engine unavailable: {e}, falling back to calculation method"
            )

        return papers

    def _merge_enrichment_data(self, paper: "Paper", results: Dict) -> "Paper":
        """Merge enrichment results into paper object.

        Creates a new Paper object with merged data to avoid modifying the original.
        """
        # Import here to avoid circular dependency

        enriched = deepcopy(paper)

        # Results from ScholarEngine is already combined metadata, not individual engine results
        if not results:
            return enriched

        # Extract from the combined metadata structure
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
            # Note: corpus_id, semantic_id, ieee_id are in results but not in Paper dataclass

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
            # Try both "count" and "total" fields
            count = results["citation_count"].get("count") or results[
                "citation_count"
            ].get("total")
            if count:
                # Always take the maximum citation count
                current_count = enriched.metadata.citation_count.total or 0
                if not current_count or count > current_count:
                    enriched.metadata.citation_count.total = count
            # Note: influential_citation_count is in results but not in Paper dataclass

        # URL metadata
        if "url" in results:
            if results["url"].get("pdf"):
                # Check if this PDF is not already in the list
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

        # Note: Metrics section (journal_impact_factor, h_index) not stored in Paper dataclass

        return enriched

    def _enrich_current_project(self) -> Dict[str, int]:
        """Enrich all papers in the current project.

        Returns:
            Dictionary with enrichment statistics
        """
        if not self.project:
            raise ValueError(
                "No project specified. Use Scholar(project='name') or provide papers to enrich()."
            )

        # Load papers from project library
        papers = self.load_project(self.project)
        logger.info(
            f"Enriching {len(papers)} papers in project '{self.project}'"
        )

        # Enrich the papers
        enriched_papers = self.enrich_papers(papers)

        # Count successes
        enriched_count = sum(
            1
            for i, p in enumerate(enriched_papers)
            if p.abstract
            and not papers[i].abstract  # Check if abstract was added
        )

        # Save enriched papers back to library
        saved_ids = self.save_papers_to_library(enriched_papers)

        return {
            "enriched": enriched_count,
            "failed": len(papers) - enriched_count,
            "total": len(papers),
            "saved": len(saved_ids),
        }

    # ----------------------------------------
    # URL Finding (Orchestration)
    # ----------------------------------------
    async def _find_urls_for_doi_async(
        self, doi: str, context
    ) -> Dict[str, Any]:
        """Find all URLs for a DOI (orchestration layer).

        Workflow:
            DOI → Publisher URL → PDF URLs → OpenURL (fallback)

        Args:
            doi: DOI string
            context: Authenticated browser context

        Returns:
            Dictionary with URL information: {
                "url_doi": "https://doi.org/...",
                "url_publisher": "https://publisher.com/...",
                "urls_pdf": [{"url": "...", "source": "zotero_translator"}],
                "url_openurl_resolved": "..." (if fallback used)
            }
        """
        from scitex.scholar.auth.gateway import (
            normalize_doi_as_http,
            resolve_publisher_url_by_navigating_to_doi_page,
            OpenURLResolver,
        )

        # Initialize result
        urls = {"url_doi": normalize_doi_as_http(doi)}

        # Step 1: Resolve publisher URL
        page = await context.new_page()
        try:
            url_publisher = await resolve_publisher_url_by_navigating_to_doi_page(
                doi, page
            )
            urls["url_publisher"] = url_publisher
        finally:
            await page.close()

        # Step 2: Find PDF URLs from publisher URL
        url_finder = ScholarURLFinder(context, config=self.config)
        urls_pdf = []

        if url_publisher:
            urls_pdf = await url_finder.find_pdf_urls(url_publisher)

        # Step 3: Try OpenURL fallback if no PDFs found
        if not urls_pdf:
            openurl_resolver = OpenURLResolver(config=self.config)
            page = await context.new_page()
            try:
                url_openurl_resolved = await openurl_resolver.resolve_doi(
                    doi, page
                )
                urls["url_openurl_resolved"] = url_openurl_resolved

                if url_openurl_resolved and url_openurl_resolved != "skipped":
                    urls_pdf = await url_finder.find_pdf_urls(
                        url_openurl_resolved
                    )
            finally:
                await page.close()

        # Deduplicate and store
        urls["urls_pdf"] = (
            self._deduplicate_pdf_urls(urls_pdf) if urls_pdf else []
        )

        return urls

    def _deduplicate_pdf_urls(self, urls_pdf: List[Dict]) -> List[Dict]:
        """Remove duplicate PDF URLs.

        Args:
            urls_pdf: List of PDF URL dicts

        Returns:
            Deduplicated list of PDF URL dicts
        """
        seen = set()
        unique = []
        for pdf in urls_pdf:
            url = pdf.get("url") if isinstance(pdf, dict) else pdf
            if url not in seen:
                seen.add(url)
                unique.append(pdf)
        return unique

    # ----------------------------------------
    # PDF Downloaders
    # ----------------------------------------
    async def download_pdfs_from_dois_async(
        self,
        dois: List[str],
        output_dir: Optional[Path] = None,
        max_concurrent: int = 1,
    ) -> Dict[str, int]:
        """Download PDFs for given DOIs using ScholarPDFDownloader.

        Args:
            dois: List of DOI strings
            output_dir: Output directory (not used - downloads to library MASTER)
            max_concurrent: Maximum concurrent downloads (default: 1 for sequential)

        Returns:
            Dictionary with download statistics
        """
        if not dois:
            return {"downloaded": 0, "failed": 0, "errors": 0}

        # Get authenticated browser context
        browser, context = (
            await self._browser_manager.get_authenticated_browser_and_context_async()
        )

        try:
            # Initialize PDF downloader with browser context
            pdf_downloader = ScholarPDFDownloader(
                context=context,
                config=self.config,
            )

            # Use download_from_dois from ScholarPDFDownloader
            # This handles parallel downloads with semaphore control
            logger.info(
                f"{self.name}: Starting PDF download for {len(dois)} DOIs (max_concurrent={max_concurrent})"
            )

            results = await pdf_downloader.download_from_dois(
                dois=dois,
                output_dir=str(output_dir) if output_dir else "/tmp/",
                max_concurrent=max_concurrent,
            )

            # Process results and organize in library
            stats = {"downloaded": 0, "failed": 0, "errors": 0}
            library_dir = self.config.get_library_dir()
            master_dir = library_dir / "MASTER"
            master_dir.mkdir(parents=True, exist_ok=True)

            for doi, downloaded_paths in zip(dois, results):
                try:
                    if downloaded_paths and len(downloaded_paths) > 0:
                        # PDF was downloaded successfully
                        # Take the first downloaded PDF (if multiple)
                        temp_pdf_path = downloaded_paths[0]

                        # Generate paper ID and create storage
                        paper_id = self.config.path_manager._generate_paper_id(
                            doi=doi
                        )
                        storage_path = master_dir / paper_id
                        storage_path.mkdir(parents=True, exist_ok=True)

                        # Move PDF to MASTER library
                        pdf_filename = (
                            f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
                        )
                        master_pdf_path = storage_path / pdf_filename
                        shutil.move(str(temp_pdf_path), str(master_pdf_path))

                        # Create/update metadata
                        metadata_file = storage_path / "metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)
                        else:
                            metadata = {
                                "doi": doi,
                                "scitex_id": paper_id,
                                "created_at": datetime.now().isoformat(),
                                "created_by": "SciTeX Scholar",
                            }

                        # Update metadata with PDF info
                        metadata["pdf_path"] = str(
                            master_pdf_path.relative_to(library_dir)
                        )
                        metadata["pdf_downloaded_at"] = datetime.now().isoformat()
                        metadata["pdf_size_bytes"] = master_pdf_path.stat().st_size
                        metadata["updated_at"] = datetime.now().isoformat()

                        with open(metadata_file, "w") as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)

                        # Update symlink using LibraryManager
                        if self.project not in ["master", "MASTER"]:
                            self._library_manager.update_symlink(
                                master_storage_path=storage_path,
                                project=self.project,
                            )

                        logger.success(
                            f"Downloaded and organized PDF for {doi}: {master_pdf_path}"
                        )
                        stats["downloaded"] += 1
                    else:
                        logger.warning(f"No PDF downloaded for DOI: {doi}")
                        stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Failed to organize PDF for {doi}: {e}")
                    stats["errors"] += 1
                    stats["failed"] += 1

            return stats

        finally:
            # Always close browser
            await self._browser_manager.close()

    # COMMENTED OUT - Old parallel implementation
    # async def download_pdfs_from_dois_async_OLD(
    #     self,
    #     dois: List[str],
    #     output_dir: Optional[Path] = None,
    #     max_parallel: int = None,
    #     use_parallel: Optional[bool] = None,
    # ) -> Dict[str, int]:
    #     """Download PDFs for given DOIs with optional parallel processing.

    #     Args:
    #         dois: List of DOI strings
    #         output_dir: Output directory (uses config default if None)
    #         use_parallel: Whether to use parallel downloads (None = auto from config)

    #     Returns:
    #         Dictionary with download statistics
    #     """
    #     # Check if parallel download should be used
    #     max_parallel = self.config.resolve(
    #         "max_parallel", max_parallel, default=4
    #     )
    #     # pdf_config = self.config.get("pdf_download") or {}
    #     # use_parallel = (
    #     #     use_parallel
    #     #     if use_parallel is not None
    #     #     else pdf_config.get("use_parallel", True)
    #     # )

    #     if max_parallel and len(dois) > 1:
    #         # Use parallel downloader for multiple DOIs
    #         logger.info(
    #             f"{self.name}: PDF Download: Processing {len(dois)} DOIs in parallel",
    #             sep="=",
    #             n_sep=60,
    #         )

    #         pdf_downloader = ScholarPDFDownloader(self.context)
    #         results = await pdf_downloader.download_from_dois(
    #             dois,
    #             output_dir,
    #         )
    #         for doi, result in zip([dois, results]):
    #             paper_data = {"doi": doi}
    #             paper_id = self.config.path_manager._generate_paper_id(doi=doi)
    #             library_dir = self.config.get_library_dir()
    #             metadata_file = (
    #                 library_dir / "MASTER" / paper_id / "metadata.json"
    #             )

    #             if metadata_file.exists():
    #                 import json

    #                 with open(metadata_file, "r") as f:
    #                     existing_metadata = json.load(f)
    #                     paper_data.update(existing_metadata)
    #                     # Check for existing PDF URLs in metadata
    #                     if (
    #                         "url" in existing_metadata
    #                         and "pdfs" in existing_metadata.get("url", {})
    #                     ):
    #                         existing_pdf_urls = existing_metadata["url"][
    #                             "pdfs"
    #                         ]
    #                     elif "pdf_urls" in existing_metadata:
    #                         existing_pdf_urls = existing_metadata[
    #                             "pdf_urls"
    #                         ]

    #         # Prepare papers - check existing metadata first, only find URLs if needed
    #         papers_with_urls = []
    #         dois_needing_urls = []
    #         doi_to_index = {}  # Map DOI to original index for result matching

    #         for i, doi in enumerate(dois):
    #             try:
    #                 paper_data = {"doi": doi}

    #                 # Check if paper already exists in library
    #                 paper_id = self.config.path_manager._generate_paper_id(
    #                     doi=doi
    #                 )
    #                 library_dir = self.config.get_library_dir()
    #                 metadata_file = (
    #                     library_dir / "MASTER" / paper_id / "metadata.json"
    #                 )

    #                 existing_pdf_urls = []
    #                 if metadata_file.exists():
    #                     import json

    #                     with open(metadata_file, "r") as f:
    #                         existing_metadata = json.load(f)
    #                         paper_data.update(existing_metadata)
    #                         # Check for existing PDF URLs in metadata
    #                         if (
    #                             "url" in existing_metadata
    #                             and "pdfs" in existing_metadata.get("url", {})
    #                         ):
    #                             existing_pdf_urls = existing_metadata["url"][
    #                                 "pdfs"
    #                             ]
    #                         elif "pdf_urls" in existing_metadata:
    #                             existing_pdf_urls = existing_metadata[
    #                                 "pdf_urls"
    #                             ]

    #                 # Only find URLs if we don't have any from metadata
    #                 if existing_pdf_urls:
    #                     logger.info(
    #                         f"{self.name}: Using {len(existing_pdf_urls)} cached PDF URLs for {doi}",
    #                         indent=1,
    #                         c="cyan",
    #                     )
    #                     paper_data["pdf_urls"] = existing_pdf_urls
    #                     papers_with_urls.append(paper_data)
    #                 else:
    #                     # Need to find URLs for this DOI
    #                     dois_needing_urls.append(doi)
    #                     doi_to_index[doi] = i
    #                     papers_with_urls.append(paper_data)  # Add placeholder

    #             except Exception as e:
    #                 logger.warning(f"Failed to load metadata for {doi}: {e}")
    #                 dois_needing_urls.append(doi)
    #                 doi_to_index[doi] = i
    #                 papers_with_urls.append({"doi": doi, "pdf_urls": []})

    #         # Only run URL finder if there are DOIs without URLs
    #         if dois_needing_urls:
    #             logger.info(
    #                 f"URL Finding: Processing {len(dois_needing_urls)}/{len(dois)} DOIs",
    #                 sep="-",
    #                 n_sep=60,
    #                 indent=1,
    #             )

    #             url_finder_parallel = ScholarURLFinderParallel(
    #                 auth_manager=self._auth_manager,
    #                 browser_manager=self._browser_manager,
    #                 config=self.config,
    #             )

    #             url_results = await url_finder_parallel.find_urls_batch(
    #                 dois_needing_urls
    #             )

    #             # Update papers with newly found URLs
    #             for doi, urls in zip(dois_needing_urls, url_results):
    #                 idx = doi_to_index[doi]
    #                 papers_with_urls[idx]["pdf_urls"] = urls.get(
    #                     "urls_pdf", []
    #                 )
    #                 papers_with_urls[idx]["url_info"] = urls
    #         else:
    #             logger.success(
    #                 f"{self.name}: All {len(dois)} DOIs have cached PDF URLs - skipping URL finding",
    #                 indent=1,
    #             )

    #         # Get authenticated browser context for parallel downloads
    #         browser, context = (
    #             await self._browser_manager.get_authenticated_browser_and_context_async()
    #         )

    #         try:
    #             # Initialize simple downloader with built-in parallel support
    #             downloader = ScholarPDFDownloader(
    #                 context=context,
    #                 config=self.config,
    #             )

    #             # Use download_from_dois for parallel downloads (has built-in semaphore)
    #             max_concurrent = pdf_config.get("max_concurrent", 3)
    #             results = await downloader.download_from_dois(
    #                 dois=dois,
    #                 output_dir="/tmp/",
    #                 max_concurrent=max_concurrent,
    #             )

    #             # Convert results to expected format
    #             # results is List[List[Path]] where each inner list is downloads for one DOI
    #             # Count exceptions as errors
    #             errors = sum(1 for r in results if isinstance(r, Exception))
    #             successful = sum(
    #                 1 for r in results if r and not isinstance(r, Exception)
    #             )
    #             failed = len(results) - successful - errors

    #             return {
    #                 "downloaded": successful,
    #                 "failed": failed,
    #                 "errors": errors,
    #             }
    #         finally:
    #             # Always close browser, even on exception
    #             await self._browser_manager.close()
    #     else:
    #         # Use sequential download for single DOI or when parallel disabled
    #         return await self._download_pdfs_sequential(dois, output_dir)

    async def _download_pdfs_sequential(
        self, dois: List[str], output_dir: Optional[Path] = None
    ) -> Dict[str, int]:
        """Sequential PDF download with authentication gateway."""
        results = {"downloaded": 0, "failed": 0, "errors": 0}

        # Get authenticated browser context
        browser, context = (
            await self._browser_manager.get_authenticated_browser_and_context_async()
        )

        # Initialize authentication gateway (NEW)
        auth_gateway = AuthenticationGateway(
            auth_manager=self._auth_manager,
            browser_manager=self._browser_manager,
            config=self.config,
        )

        # Use simple downloader for sequential downloads
        pdf_downloader = ScholarPDFDownloader(
            context=context,
            config=self.config,
        )

        library_dir = self.config.get_library_dir()
        master_dir = library_dir / "MASTER"
        project_dir = library_dir / self.project
        master_dir.mkdir(parents=True, exist_ok=True)
        project_dir.mkdir(parents=True, exist_ok=True)

        for doi in dois:
            try:
                logger.info(f"Processing DOI: {doi}")

                # NEW: Prepare authentication context BEFORE URL finding
                # This establishes publisher-specific cookies if needed
                _url_context = await auth_gateway.prepare_context_async(
                    doi=doi, context=context
                )

                # Step 1: Find URLs for the DOI (orchestration)
                urls = await self._find_urls_for_doi_async(doi, context)

                # Step 2: Get PDF URLs
                pdf_urls = urls.get("urls_pdf", [])

                if not pdf_urls:
                    logger.warning(f"No PDF URLs found for DOI: {doi}")
                    results["failed"] += 1
                    continue

                # Step 3: Try to download from each PDF URL
                downloaded_path = None
                for pdf_entry in pdf_urls:
                    # Handle both dict and string formats
                    pdf_url = (
                        pdf_entry.get("url")
                        if isinstance(pdf_entry, dict)
                        else pdf_entry
                    )

                    if not pdf_url:
                        continue

                    # Download to temp location first
                    temp_output = (
                        Path("/tmp")
                        / f"{doi.replace('/', '_').replace(':', '_')}.pdf"
                    )

                    # Download PDF using simple downloader
                    result = await pdf_downloader.download_from_url(
                        pdf_url=pdf_url, output_path=temp_output
                    )

                    if result and result.exists():
                        downloaded_path = result
                        break

                if downloaded_path:
                    # Step 4: Store PDF in MASTER library with proper organization

                    # Generate unique ID from DOI using PathManager
                    paper_id = self.config.path_manager._generate_paper_id(
                        doi=doi
                    )

                    # Create MASTER storage directory
                    storage_path = master_dir / paper_id
                    storage_path.mkdir(parents=True, exist_ok=True)

                    # Try to get paper metadata to generate readable name
                    readable_name = None
                    temp_paper = None
                    try:
                        # Try to load paper from DOI to get metadata
                        from scitex.scholar.core.Paper import Paper
                        from scitex.scholar.core.Papers import Papers

                        temp_paper = Paper()
                        temp_paper.metadata.id.doi = doi
                        # Try to enrich to get author/year/journal using async method
                        temp_papers = Papers([temp_paper])
                        enriched = await self.enrich_papers_async(temp_papers)
                        if enriched and len(enriched) > 0:
                            temp_paper = enriched[0]

                        # Generate readable name from metadata
                        first_author = "Unknown"
                        authors = temp_paper.metadata.basic.authors
                        if authors and len(authors) > 0:
                            author_parts = authors[0].split()
                            if len(author_parts) > 1:
                                first_author = author_parts[-1]  # Last name
                            else:
                                first_author = author_parts[0]

                        year = temp_paper.metadata.basic.year
                        year_str = str(year) if year else "Unknown"

                        journal_clean = "Unknown"
                        journal = temp_paper.metadata.publication.journal
                        if journal:
                            # Clean journal name - remove special chars, keep alphanumeric
                            journal_clean = "".join(
                                c for c in journal if c.isalnum() or c in " "
                            ).replace(" ", "")
                            if not journal_clean:
                                journal_clean = "Unknown"

                        # Format: Author-Year-Journal
                        readable_name = (
                            f"{first_author}-{year_str}-{journal_clean}"
                        )
                    except:
                        pass

                    # Fallback to DOI if metadata extraction failed
                    if not readable_name:
                        readable_name = (
                            f"DOI_{doi.replace('/', '_').replace(':', '_')}"
                        )

                    # Copy PDF to MASTER storage with ORIGINAL filename to track how downloaded
                    # The PDF filename preserves the DOI format for tracking
                    pdf_filename = (
                        f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
                    )
                    master_pdf_path = storage_path / pdf_filename
                    shutil.copy2(downloaded_path, master_pdf_path)

                    # Load existing metadata or create minimal new metadata
                    metadata_file = storage_path / "metadata.json"
                    if metadata_file.exists():
                        # Load existing rich metadata - DO NOT OVERWRITE IT
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        logger.debug(
                            f"Loaded existing metadata for {paper_id}"
                        )
                    else:
                        # Create new minimal metadata only if none exists
                        metadata = {
                            "doi": doi,
                            "scitex_id": paper_id,
                            "created_at": datetime.now().isoformat(),
                            "created_by": "SciTeX Scholar",
                        }

                        # Add enriched paper metadata for new papers only
                        if temp_paper:
                            # Use Pydantic to_dict() for Paper
                            paper_dict = temp_paper.to_dict()
                            # Merge paper metadata
                            for key, value in paper_dict.items():
                                if value is not None and key not in [
                                    "doi",
                                    "scitex_id",
                                ]:
                                    metadata[key] = value

                    # Add PDF information
                    metadata["pdf_path"] = str(
                        master_pdf_path.relative_to(library_dir)
                    )
                    metadata["pdf_downloaded_at"] = datetime.now().isoformat()
                    metadata["pdf_size_bytes"] = master_pdf_path.stat().st_size
                    metadata["updated_at"] = datetime.now().isoformat()

                    # Save updated metadata
                    with open(metadata_file, "w") as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                    # Update symlink using LibraryManager (generates proper PDF status prefix)
                    if self.project not in ["master", "MASTER"]:
                        self._library_manager.update_symlink(
                            master_storage_path=storage_path,
                            project=self.project,
                        )

                    # Clean up temp file
                    downloaded_path.unlink()

                    logger.success(
                        f"Downloaded PDF for {doi}: MASTER/{paper_id}/{pdf_filename}"
                    )
                    results["downloaded"] += 1
                else:
                    logger.warning(
                        f"Failed to download any PDF for DOI: {doi}"
                    )
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Failed to process {doi}: {e}")
                results["errors"] += 1
                results["failed"] += 1

        await self._browser_manager.close()
        logger.info(f"PDF download complete: {results}")
        return results

    def download_pdfs_from_dois(
        self, dois: List[str], output_dir: Optional[Path] = None
    ) -> Dict[str, int]:
        """Download PDFs for given DOIs.

        Args:
            dois: List of DOI strings
            output_dir: Output directory (uses config default if None)

        Returns:
            Dictionary with download statistics
        """
        import asyncio

        return asyncio.run(
            self.download_pdfs_from_dois_async(dois, output_dir)
        )

    def download_pdfs_from_bibtex(
        self,
        bibtex_input: Union[str, Path, Papers],
        output_dir: Optional[Path] = None,
    ) -> Dict[str, int]:
        """Download PDFs from BibTeX file or Papers collection.

        Args:
            bibtex_input: BibTeX file path, content string, or Papers collection
            output_dir: Output directory (uses config default if None)

        Returns:
            Dictionary with download statistics
        """
        # Load papers if bibtex_input is not already Papers
        if isinstance(bibtex_input, Papers):
            papers = bibtex_input
        else:
            papers = self.load_bibtex(bibtex_input)

        # Extract DOIs from papers
        dois = [
            paper.metadata.id.doi for paper in papers if paper.metadata.id.doi
        ]

        if not dois:
            logger.warning("No papers with DOIs found in BibTeX input")
            return {"downloaded": 0, "failed": 0, "errors": 0}

        logger.info(
            f"Found {len(dois)} papers with DOIs out of {len(papers)} total papers"
        )

        # Download PDFs using DOI method
        return self.download_pdfs_from_dois(dois, output_dir)

    # ----------------------------------------
    # Loaders
    # ----------------------------------------
    def load_project(self, project: Optional[str] = None) -> Papers:
        """Load papers from a project using library manager service.

        Args:
            project: Project name (uses self.project if None)

        Returns:
            Papers collection from the project
        """
        project_name = project or self.project
        if not project_name:
            raise ValueError("No project specified")

        # Load papers from library by reading symlinks in project directory
        from ..core.Papers import Papers
        from ..core.Paper import Paper
        import json

        logger.info(f"Loading papers from project: {project_name}")

        library_dir = self.config.get_library_dir()
        project_dir = library_dir / project_name

        if not project_dir.exists():
            logger.warning(f"Project directory does not exist: {project_dir}")
            return Papers([], project=project_name)

        papers = []
        for item in project_dir.iterdir():
            # Skip info directory and metadata files
            if item.name in ["info", "project_metadata.json", "README.md"]:
                continue

            # Follow symlink to MASTER directory
            if item.is_symlink():
                master_path = item.resolve()
                if master_path.exists():
                    # Load metadata.json from MASTER directory
                    metadata_file = master_path / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, "r") as f:
                                metadata = json.load(f)

                            # Create Paper object using from_dict class method
                            paper = Paper.from_dict(metadata)

                            papers.append(paper)
                        except Exception as e:
                            logger.warning(
                                f"Failed to load metadata from {metadata_file}: {e}"
                            )

        logger.info(
            f"Loaded {len(papers)} papers from project: {project_name}"
        )
        return Papers(papers, project=project_name)

    def load_bibtex(self, bibtex_input: Union[str, Path]) -> Papers:
        """Load Papers collection from BibTeX file or content.

        Args:
            bibtex_input: BibTeX file path or content string

        Returns:
            Papers collection
        """
        # Use the internal library to load papers
        papers = self._library.papers_from_bibtex(bibtex_input)

        # Convert to Papers collection
        from .Papers import Papers

        papers_collection = Papers(
            papers, config=self.config, project=self.project
        )
        papers_collection.library = (
            self._library
        )  # Attach library for save operations

        return papers_collection

    # ----------------------------------------
    # Searchers
    # ----------------------------------------
    def search_library(
        self, query: str, project: Optional[str] = None
    ) -> Papers:
        """
        Search papers in local library.

        For new literature search (not in library), use AI2 Scholar QA:
        https://scholarqa.allen.ai/chat/ then process with:
        papers = scholar.load_bibtex('file.bib') followed by scholar.enrich(papers)

        Args:
            query: Search query
            project: Project filter (uses self.project if None)

        Returns:
            Papers collection matching the query
        """
        # For now, return empty Papers until search is implemented
        from ..core.Papers import Papers

        logger.info(f"Searching library for: {query}")
        return Papers([], project=project or self.project)

    def search_across_projects(
        self, query: str, projects: Optional[List[str]] = None
    ) -> Papers:
        """Search for papers across multiple projects or the entire library.

        Args:
            query: Search query
            projects: List of project names to search (None for all)

        Returns:
            Papers collection with search results
        """
        if projects is None:
            # Search all projects
            all_projects = [p["name"] for p in self.list_projects()]
        else:
            all_projects = projects

        all_papers = []
        for project in all_projects:
            try:
                project_papers = Papers.from_project(project, self.config)
                # Simple text search implementation
                matching_papers = [
                    p
                    for p in project_papers._papers
                    if query.lower() in (p.title or "").lower()
                    or query.lower() in (p.abstract or "").lower()
                    or any(
                        query.lower() in (author or "").lower()
                        for author in (p.authors or [])
                    )
                ]
                all_papers.extend(matching_papers)
            except Exception as e:
                logger.debug(f"Failed to search project {project}: {e}")

        return Papers(all_papers, config=self.config, project="search_results")

    # ----------------------------------------
    # Savers
    # ----------------------------------------
    def save_papers_to_library(self, papers: Papers) -> List[str]:
        """Save papers collection to library.

        Args:
            papers: Papers collection to save

        Returns:
            List of paper IDs saved
        """
        saved_ids = []
        for paper in papers:
            try:
                paper_id = self._library.save_paper(paper)
                saved_ids.append(paper_id)
            except Exception as e:
                logger.warning(f"Failed to save paper: {e}")

        logger.info(f"Saved {len(saved_ids)}/{len(papers)} papers to library")
        return saved_ids

    def save_papers_as_bibtex(
        self, papers: Papers, output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """Save papers to BibTeX format with enrichment metadata.

        Args:
            papers: Papers collection to save
            output_path: Optional path to save the BibTeX file

        Returns:
            BibTeX content as string with enrichment metadata included
        """
        from ..storage.BibTeXHandler import BibTeXHandler

        bibtex_handler = BibTeXHandler(
            project=self.project, config=self.config
        )
        return bibtex_handler.papers_to_bibtex(papers, output_path)

    # ----------------------------------------
    # Project Handlers
    # ----------------------------------------
    def _ensure_project_exists(
        self, project: str, description: Optional[str] = None
    ) -> Path:
        """Ensure project directory exists, create if needed (PRIVATE).

        Args:
            project: Project name
            description: Optional project description

        Returns:
            Path to the project directory
        """
        project_dir = self.config.get_library_dir() / project
        info_dir = project_dir / "info"

        # Create project and info directories
        if not project_dir.exists():
            project_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Auto-created project directory: {project}")

        # Ensure info directory exists
        info_dir.mkdir(parents=True, exist_ok=True)

        # Create/move metadata file to info directory
        old_metadata_file = (
            project_dir / "project_metadata.json"
        )  # Old location
        metadata_file = info_dir / "project_metadata.json"  # New location

        # Move existing metadata file if it exists in old location
        if old_metadata_file.exists() and not metadata_file.exists():
            shutil.move(str(old_metadata_file), str(metadata_file))
            logger.info(f"Moved project metadata to info directory")

        # Create metadata file if it doesn't exist
        if not metadata_file.exists():
            metadata = {
                "name": project,
                "description": description or f"Papers for {project} project",
                "created": datetime.now().isoformat(),
                "created_by": "SciTeX Scholar",
                "auto_created": True,
            }

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(
                f"Created project metadata in info directory: {project}"
            )

        return project_dir

    def _create_project_metadata(
        self, project: str, description: Optional[str] = None
    ) -> Path:
        """Create project directory and metadata (PRIVATE).

        DEPRECATED: Use _ensure_project_exists instead.

        Args:
            project: Project name
            description: Optional project description

        Returns:
            Path to the created project directory
        """
        # Just use the new method that puts metadata in info directory
        return self._ensure_project_exists(project, description)

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in the Scholar library.

        Returns:
            List of project information dictionaries
        """
        library_dir = self.config.get_library_dir()
        projects = []

        for item in library_dir.iterdir():
            if item.is_dir() and item.name != "MASTER":
                project_info = {
                    "name": item.name,
                    "path": str(item),
                    "papers_count": len(list(item.glob("*"))),
                    "created": None,
                    "description": None,
                }

                # Load metadata if exists
                metadata_file = item / "project_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        project_info.update(metadata)
                    except Exception as e:
                        logger.debug(
                            f"Failed to load metadata for {item.name}: {e}"
                        )

                projects.append(project_info)

        return sorted(projects, key=lambda x: x["name"])

    # ----------------------------------------
    # Library Handlers
    # ----------------------------------------
    def get_library_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for the entire Scholar library.

        Returns:
            Dictionary with library-wide statistics
        """
        master_dir = self.config.get_library_master_dir()
        projects = self.list_projects()

        stats = {
            "total_projects": len(projects),
            "total_papers": (
                len(list(master_dir.glob("*"))) if master_dir.exists() else 0
            ),
            "projects": projects,
            "library_path": str(self.config.get_library_dir()),
            "master_path": str(master_dir),
        }

        # Calculate storage usage
        if master_dir.exists():
            total_size = sum(
                f.stat().st_size for f in master_dir.rglob("*") if f.is_file()
            )
            stats["storage_mb"] = total_size / (1024 * 1024)
        else:
            stats["storage_mb"] = 0

        return stats

    def backup_library(self, backup_path: Union[str, Path]) -> Dict[str, Any]:
        """Create a backup of the Scholar library.

        Args:
            backup_path: Path for the backup

        Returns:
            Dictionary with backup information
        """
        backup_path = Path(backup_path)
        library_path = self.config.get_library_dir()

        if not library_path.exists():
            raise ScholarError("Library directory does not exist")

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backup_path / f"scholar_library_backup_{timestamp}"

        logger.info(f"Creating library backup at {backup_dir}")
        shutil.copytree(library_path, backup_dir)

        # Create backup metadata
        backup_info = {
            "timestamp": timestamp,
            "source": str(library_path),
            "backup": str(backup_dir),
            "size_mb": sum(
                f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
            )
            / (1024 * 1024),
        }

        metadata_file = backup_dir / "backup_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(backup_info, f, indent=2)

        logger.info(
            f"Library backup completed: {backup_info['size_mb']:.2f} MB"
        )
        return backup_info

    # =========================================================================
    # PIPELINE METHODS (Phase 2)
    # =========================================================================

    async def process_paper_async(
        self,
        title: Optional[str] = None,
        doi: Optional[str] = None,
        project: Optional[str] = None,
    ) -> "Paper":
        """
        Complete sequential pipeline for processing a single paper.

        Accepts either title OR doi. Uses storage-first approach:
        each stage checks storage before processing.

        Workflow:
          Stage 0: Resolve DOI from title (if needed)
          Stage 1: Load or create Paper from storage
          Stage 2: Find PDF URLs → save to storage
          Stage 3: Download PDF → save to storage
          Stage 4: Update project symlinks

        Args:
            title: Paper title (will resolve DOI using engine)
            doi: DOI of the paper (preferred if available)
            project: Project name (uses self.project if None)

        Returns:
            Fully processed Paper object

        Examples:
            # With DOI (direct)
            paper = await scholar.process_paper_async(doi="10.1038/s41598-017-02626-y")

            # With title (resolves DOI first)
            paper = await scholar.process_paper_async(
                title="Attention Is All You Need"
            )
        """
        from scitex.scholar.core.Paper import Paper

        # Validate input
        if not title and not doi:
            raise ValueError("Must provide either title or doi")

        project = project or self.project

        logger.info(f"{'='*60}")
        logger.info(f"Processing paper")
        if title:
            logger.info(f"Title: {title[:50]}...")
        if doi:
            logger.info(f"DOI: {doi}")
        logger.info(f"{'='*60}")

        # Stage 0: Resolve DOI from title (if needed)
        if not doi and title:
            logger.info(f"Stage 0: Resolving DOI from title...")

            # Use ScholarEngine to search and get DOI
            results = await self._scholar_engine.search_async(title=title)

            if results and results.get("id", {}).get("doi"):
                doi = results["id"]["doi"]
                logger.success(f"Resolved DOI: {doi}")
            else:
                logger.error(f"Could not resolve DOI from title: {title}")
                raise ValueError(f"Could not resolve DOI from title: {title}")

        # Generate paper ID from DOI
        paper_id = self.config.path_manager._generate_paper_id(doi=doi)
        storage_path = self.config.get_library_master_dir() / paper_id

        logger.info(f"Paper ID: {paper_id}")
        logger.info(f"Storage: {storage_path}")

        # Stage 1: Load or create Paper from storage
        logger.info(f"\nStage 1: Loading/creating metadata...")
        if self._library_manager.has_metadata(paper_id):
            # Load existing from storage
            paper = self._library_manager.load_paper_from_id(paper_id)
            logger.info(f"Loaded existing metadata from storage")
        else:
            # Create new Paper
            paper = Paper()
            paper.metadata.set_doi(doi)
            paper.container.scitex_id = paper_id

            # If we have title, save it
            if title:
                paper.metadata.basic.title = title

            # Create storage and save
            self._library_manager.save_paper_incremental(paper_id, paper)
            logger.success(f"Created new paper entry in storage")

        # Stage 2: Check/find URLs
        logger.info(f"\nStage 2: Checking/finding PDF URLs...")
        if not self._library_manager.has_urls(paper_id):
            logger.info(f"Finding PDF URLs for DOI: {doi}")
            browser, context = await self._browser_manager.get_authenticated_browser_and_context_async()
            try:
                url_finder = ScholarURLFinder(context, config=self.config)
                urls = await url_finder.find_pdf_urls(doi)

                paper.metadata.url.pdfs = urls
                self._library_manager.save_paper_incremental(paper_id, paper)
                logger.success(f"Found {len(urls)} PDF URLs, saved to storage")
            finally:
                await self._browser_manager.close()
        else:
            logger.info(f"PDF URLs already in storage ({len(paper.metadata.url.pdfs)} URLs)")

        # Stage 3: Check/download PDF
        logger.info(f"\nStage 3: Checking/downloading PDF...")
        if not self._library_manager.has_pdf(paper_id):
            logger.info(f"Downloading PDF...")
            if paper.metadata.url.pdfs:
                browser, context = await self._browser_manager.get_authenticated_browser_and_context_async()
                try:
                    downloader = ScholarPDFDownloader(context, config=self.config)

                    pdf_url = (
                        paper.metadata.url.pdfs[0]["url"]
                        if isinstance(paper.metadata.url.pdfs[0], dict)
                        else paper.metadata.url.pdfs[0]
                    )
                    temp_path = storage_path / "main.pdf"

                    result = await downloader.download_from_url(pdf_url, temp_path, doi=doi)
                    if result and result.exists():
                        paper.metadata.path.pdfs.append(str(result))
                        self._library_manager.save_paper_incremental(paper_id, paper)
                        logger.success(f"Downloaded PDF, saved to storage")
                    else:
                        logger.warning(f"Failed to download PDF")
                finally:
                    await self._browser_manager.close()
            else:
                logger.warning(f"No PDF URLs available for download")
        else:
            logger.info(f"PDF already in storage")

        # Stage 4: Update project symlinks
        if project and project not in ["master", "MASTER"]:
            logger.info(f"\nStage 4: Updating project symlinks...")
            self._library_manager.update_symlink(
                master_storage_path=storage_path,
                project=project,
            )
            logger.success(f"Updated symlink in project: {project}")

        logger.info(f"\n{'='*60}")
        logger.success(f"Paper processing complete")
        logger.info(f"{'='*60}\n")

        return paper

    def process_paper(
        self,
        title: Optional[str] = None,
        doi: Optional[str] = None,
        project: Optional[str] = None,
    ) -> "Paper":
        """
        Synchronous wrapper for process_paper_async.

        See process_paper_async() for full documentation.
        """
        return asyncio.run(self.process_paper_async(title=title, doi=doi, project=project))

    # =========================================================================
    # PIPELINE METHODS (Phase 3) - Parallel Papers Processing
    # =========================================================================

    async def process_papers_async(
        self,
        papers: Union["Papers", List[str]],
        project: Optional[str] = None,
        max_concurrent: int = 3,
    ) -> "Papers":
        """
        Process multiple papers with controlled parallelism.

        Each paper goes through complete sequential pipeline.
        Semaphore controls how many papers process concurrently.

        Architecture:
          - Parallel papers (max_concurrent at a time)
          - Sequential stages per paper
          - Storage checks before each stage

        Args:
            papers: Papers collection or list of DOIs
            project: Project name (uses self.project if None)
            max_concurrent: Maximum concurrent papers (default: 3)
                           Set to 1 for purely sequential processing

        Returns:
            Papers collection with processed papers

        Examples:
            # Process Papers collection (parallel)
            papers = scholar.load_bibtex("papers.bib")
            processed = await scholar.process_papers_async(papers, max_concurrent=3)

            # Process DOI list (sequential)
            dois = ["10.1038/...", "10.1016/...", "10.1109/..."]
            processed = await scholar.process_papers_async(dois, max_concurrent=1)
        """
        from scitex.scholar.core.Papers import Papers

        project = project or self.project

        # Convert input to Papers collection
        if isinstance(papers, list):
            # List of DOI strings
            papers_list = []
            for doi in papers:
                from scitex.scholar.core.Paper import Paper
                p = Paper()
                p.metadata.set_doi(doi)
                papers_list.append(p)
            papers = Papers(papers_list, project=project, config=self.config)

        total = len(papers)
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {total} papers (max_concurrent={max_concurrent})")
        logger.info(f"Project: {project}")
        logger.info(f"{'='*60}\n")

        # Use semaphore for controlled parallelism
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(paper, index):
            """Process one paper with semaphore control."""
            async with semaphore:
                logger.info(f"\n[{index}/{total}] Starting paper...")
                try:
                    result = await self.process_paper_async(
                        title=paper.metadata.basic.title,
                        doi=paper.metadata.id.doi,
                        project=project,
                    )
                    logger.success(f"[{index}/{total}] Completed")
                    return result
                except Exception as e:
                    logger.error(f"[{index}/{total}] Failed: {e}")
                    return None

        # Create tasks for all papers
        tasks = [
            process_with_semaphore(paper, i + 1)
            for i, paper in enumerate(papers)
        ]

        # Process with controlled parallelism
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        processed_papers = []
        errors = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Paper {i+1} raised exception: {result}")
                errors += 1
            elif result is not None:
                processed_papers.append(result)

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch Processing Complete")
        logger.info(f"  Total: {total}")
        logger.info(f"  Successful: {len(processed_papers)}")
        logger.info(f"  Failed: {total - len(processed_papers)}")
        logger.info(f"  Errors: {errors}")
        logger.info(f"{'='*60}\n")

        return Papers(processed_papers, project=project, config=self.config)

    def process_papers(
        self,
        papers: Union["Papers", List[str]],
        project: Optional[str] = None,
        max_concurrent: int = 3,
    ) -> "Papers":
        """
        Synchronous wrapper for process_papers_async.

        See process_papers_async() for full documentation.
        """
        return asyncio.run(
            self.process_papers_async(
                papers=papers,
                project=project,
                max_concurrent=max_concurrent,
            )
        )

    # =========================================================================
    # INTERNAL SERVICES (PRIVATE - users should not access these directly)
    # =========================================================================
    def _init_config(self, config):
        # Handle different config input types
        if config is None:
            return ScholarConfig.load()  # Auto-detect config
        elif isinstance(config, (str, Path)):
            return ScholarConfig.from_yaml(config)
        elif isinstance(config, ScholarConfig):
            return config
        else:
            raise TypeError(f"Invalid config type: {type(config)}")

    @property
    def _scholar_engine(self) -> ScholarEngine:
        """Get Scholar engine for search and enrichment (PRIVATE)."""
        if (
            not hasattr(self, "__scholar_engine")
            or self.__scholar_engine is None
        ):
            self.__scholar_engine = ScholarEngine(config=self.config)
        return self.__scholar_engine

    @property
    def _auth_manager(self) -> ScholarAuthManager:
        """Get authentication manager service (PRIVATE)."""
        if not hasattr(self, "__auth_manager") or self.__auth_manager is None:
            self.__auth_manager = ScholarAuthManager()
        return self.__auth_manager

    @property
    def _browser_manager(self) -> ScholarBrowserManager:
        """Get browser manager service (PRIVATE)."""
        if (
            not hasattr(self, "__browser_manager")
            or self.__browser_manager is None
        ):
            self.__browser_manager = ScholarBrowserManager(
                auth_manager=self._auth_manager,
                chrome_profile_name="system",
                browser_mode=self.browser_mode,
            )
        return self.__browser_manager

    @property
    def _library_manager(self) -> LibraryManager:
        """Get library manager service - low-level operations (PRIVATE)."""
        if (
            not hasattr(self, "__library_manager")
            or self.__library_manager is None
        ):
            self.__library_manager = LibraryManager(
                project=self.project, config=self.config
            )
        return self.__library_manager

    @property
    def _library(self) -> ScholarLibrary:
        """Get Scholar library service - high-level operations (PRIVATE)."""
        if not hasattr(self, "__library") or self.__library is None:
            self.__library = ScholarLibrary(
                project=self.project, config=self.config
            )
        return self.__library


# Export all classes and functions
__all__ = ["Scholar"]

if __name__ == "__main__":
    from scitex.scholar.core.Paper import Paper
    from scitex.scholar.core.Papers import Papers

    def main():
        """Demonstrate Scholar class usage - Clean API Demo."""
        print("\n" + "=" * 60)
        print("🎓 Scholar Module Demo - Clean API")
        print("=" * 60 + "\n")

        # ----------------------------------------
        # 1. Initialize Scholar
        # ----------------------------------------
        print("1️⃣  Initialize Scholar")
        print("-" * 60)
        scholar = Scholar(
            project="demo_project",
            project_description="Demo project for testing Scholar API",
        )
        print(f"✓ Scholar initialized")
        print(f"  Project: {scholar.project}")
        print(f"  Workspace: {scholar.workspace_dir}")
        print()

        # Demonstrate project management
        print("2. Project Management:")
        try:
            # Create a new project
            project_dir = scholar._create_project_metadata(
                "neural_networks_2024",
                description="Collection of neural network papers from 2024",
            )
            print(f"   ✅ Created project: neural_networks_2024")
            print(f"   📂 Project directory: {project_dir}")

            # List all projects
            projects = scholar.list_projects()
            print(f"   📋 Total projects in library: {len(projects)}")
            for project in projects[:3]:  # Show first 3
                print(
                    f"      - {project['name']}: {project.get('description', 'No description')}"
                )
            if len(projects) > 3:
                print(f"      ... and {len(projects) - 3} more")

        except Exception as e:
            print(f"   ⚠️  Project management demo skipped: {e}")
        print()

        # Demonstrate library statistics
        print("3. Library Statistics:")
        try:
            stats = scholar.get_library_statistics()
            print(f"   📊 Total projects: {stats['total_projects']}")
            print(f"   📚 Total papers: {stats['total_papers']}")
            print(f"   💾 Storage usage: {stats['storage_mb']:.2f} MB")
            print(f"   📁 Library path: {stats['library_path']}")

        except Exception as e:
            print(f"   ⚠️  Library statistics demo skipped: {e}")
        print()

        # Demonstrate paper and project operations
        print("4. Working with Papers:")

        # Create some sample papers with Pydantic structure
        p1 = Paper()
        p1.metadata.basic.title = (
            "Vision Transformer: An Image Is Worth 16x16 Words"
        )
        p1.metadata.basic.authors = ["Dosovitskiy, Alexey", "Beyer, Lucas"]
        p1.metadata.basic.year = 2021
        p1.metadata.basic.keywords = [
            "vision transformer",
            "computer vision",
            "attention",
        ]
        p1.metadata.publication.journal = "ICLR"
        p1.metadata.set_doi("10.48550/arXiv.2010.11929")
        p1.container.projects = ["neural_networks_2024"]

        p2 = Paper()
        p2.metadata.basic.title = "Scaling Laws for Neural Language Models"
        p2.metadata.basic.authors = ["Kaplan, Jared", "McCandlish, Sam"]
        p2.metadata.basic.year = 2020
        p2.metadata.basic.keywords = ["scaling laws", "language models", "GPT"]
        p2.metadata.publication.journal = "arXiv preprint"
        p2.metadata.set_doi("10.48550/arXiv.2001.08361")
        p2.container.projects = ["neural_networks_2024"]

        sample_papers = [p1, p2]

        # Create Papers collection
        papers = Papers(
            sample_papers,
            project="neural_networks_2024",
            config=scholar.config,
        )
        print(f"   📝 Created collection with {len(papers)} papers")

        # Use Scholar to work with the collection
        # Switch project by creating new instance (cleaner pattern)
        scholar = Scholar(project="neural_networks_2024")
        print(f"   🎯 Set Scholar project to: {scholar.project}")
        print()

        # Demonstrate DOI resolution workflow
        print("5. Scholar Workflow Integration:")
        try:
            # Create a sample BibTeX content for demonstration
            sample_bibtex = """
    @article{sample2024,
        title = {Sample Paper for Demo},
        author = {Demo, Author},
        year = {2024},
        journal = {Demo Journal}
    }
            """

            # Demonstrate BibTeX loading
            papers_from_bibtex = scholar.load_bibtex(sample_bibtex.strip())
            print(f"   📄 Loaded {len(papers_from_bibtex)} papers from BibTeX")

            # Demonstrate project loading
            if scholar.project:
                try:
                    project_papers = scholar.load_project()
                    print(
                        f"   📂 Loaded {len(project_papers)} papers from current project"
                    )
                except:
                    print(
                        f"   📂 Current project is empty or doesn't exist yet"
                    )

        except Exception as e:
            print(f"   ⚠️  Workflow demo partially skipped: {e}")
        print()

        # Demonstrate search capabilities
        print("6. Search Capabilities:")
        try:
            # Search across projects
            search_results = scholar.search_across_projects("transformer")
            print(
                f"   🔍 Search for 'transformer': {len(search_results)} results across all projects"
            )

            # Search in current library (existing papers)
            library_search = scholar.search_library("vision")
            print(
                f"   🔍 Library search for 'vision': {len(library_search)} results"
            )

        except Exception as e:
            print(f"   ⚠️  Search demo skipped: {e}")
        print()

        # Demonstrate configuration access
        print("7. Configuration Management:")
        print(f"   ⚙️  Scholar directory: {scholar.config.paths.scholar_dir}")
        print(f"   ⚙️  Library directory: {scholar.config.get_library_dir()}")
        print(
            f"   ⚙️  Debug mode: {scholar.config.resolve('debug_mode', default=False)}"
        )
        print()

        # Demonstrate service access (internal components)
        print("8. Service Components (Internal):")
        print(
            f"   🔧 Scholar Engine: {type(scholar._scholar_engine).__name__}"
        )
        print(f"   🔧 Auth Manager: {type(scholar._auth_manager).__name__}")
        print(
            f"   🔧 Browser Manager: {type(scholar._browser_manager).__name__}"
        )
        print(
            f"   🔧 Library Manager: {type(scholar._library_manager).__name__}"
        )
        print()

        # Demonstrate backup capabilities
        print("9. Backup and Maintenance:")
        try:
            import tempfile
            import os

            # Create a temporary backup location
            backup_dir = Path(tempfile.mkdtemp()) / "scholar_backup"
            backup_info = scholar.backup_library(backup_dir)
            print(f"   💾 Library backup created:")
            print(f"      📁 Location: {backup_info['backup']}")
            print(f"      📊 Size: {backup_info['size_mb']:.2f} MB")
            print(f"      🕐 Timestamp: {backup_info['timestamp']}")

            # Clean up
            import shutil

            shutil.rmtree(backup_dir, ignore_errors=True)

        except Exception as e:
            print(f"   ⚠️  Backup demo skipped: {e}")
        print()

        print("Scholar global management demo completed! ✨")
        print()
        print("💡 Key Scholar Capabilities:")
        print("   • Global library management and statistics")
        print("   • Project creation and organization")
        print("   • Cross-project search and analysis")
        print("   • Integration with Paper and Papers classes")
        print("   • DOI resolution and metadata enrichment")
        print("   • PDF download and browser automation")
        print("   • Backup and maintenance operations")
        print()

    main()

# python -m scitex.scholar.core.Scholar

# EOF
