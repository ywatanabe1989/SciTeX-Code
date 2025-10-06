#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-04 10:10:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Scholar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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

from scitex import logging

# PDF extraction is now handled by scitex.io
from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig

# Updated imports for current architecture
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.storage import LibraryManager
from scitex.scholar.storage import ScholarLibrary
from scitex.scholar.engines.ScholarEngine import ScholarEngine

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

    def __init__(
        self,
        config: Optional[Union[ScholarConfig, str, Path]] = None,
        project: Optional[str] = None,
        project_description: Optional[str] = None,
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
        """

        self.config = self._init_config(config)

        # Set project and workspace
        self.project = self.config.resolve("project", project, "default")
        self.workspace_dir = self.config.path_manager.workspace_dir

        # Create project directory with description if provided
        if project and project_description:
            self._create_project_metadata(project, project_description)

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

        logger.info(
            f"Scholar initialized (project: {project}, workspace: {self.workspace_dir})"
        )

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
                    title=paper.title,
                    year=paper.year,
                    authors=paper.authors[0] if paper.authors else None,
                )

                # Create a copy to avoid modifying original
                enriched_paper = self._merge_enrichment_data(paper, results)
                enriched_list.append(enriched_paper)
                logger.info(f"Enriched: {paper.title[:50]}...")

            except Exception as e:
                logger.warning(
                    f"Failed to enrich paper '{paper.title[:50]}...': {e}"
                )
                enriched_list.append(paper)  # Keep original if enrichment fails

        from ..core.Papers import Papers
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
        import asyncio

        # If no papers provided, enrich entire project
        if papers is None:
            return self._enrich_current_project()

        # Enrich the provided papers collection
        enriched_list = []

        for paper in papers:
            try:
                # Use ScholarEngine to search and enrich
                results = asyncio.run(
                    self._scholar_engine.search_async(
                        title=paper.title,
                        year=paper.year,
                        authors=paper.authors[0] if paper.authors else None,
                    )
                )

                # Create a copy to avoid modifying original
                enriched_paper = self._merge_enrichment_data(paper, results)
                enriched_list.append(enriched_paper)
                logger.info(f"Enriched: {paper.title[:50]}...")

            except Exception as e:
                logger.warning(
                    f"Failed to enrich paper '{paper.title[:50]}...': {e}"
                )
                enriched_list.append(
                    paper
                )  # Keep original if enrichment fails

        from ..core.Papers import Papers

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
        # Try JCR database first (fast)
        try:
            from scitex.scholar.engines.JCRImpactFactorEngine import (
                JCRImpactFactorEngine,
            )

            jcr_engine = JCRImpactFactorEngine()
            papers = jcr_engine.enrich_papers(papers)
            return papers
        except Exception as e:
            logger.debug(
                f"JCR engine unavailable: {e}, falling back to calculation method"
            )

        # Fallback to calculation method (slower but always available)
        import sys
        from pathlib import Path

        # Add impact_factor module to path if needed
        impact_factor_path = (
            Path(__file__).parent.parent / "externals/impact_factor/src"
        )
        if (
            impact_factor_path.exists()
            and str(impact_factor_path) not in sys.path
        ):
            sys.path.insert(0, str(impact_factor_path))

        try:
            from impact_factor import ImpactFactorCalculator

            calculator = ImpactFactorCalculator()
            journals_cache = {}  # Cache to avoid repeated lookups

            enriched_count = 0

            for paper in papers:
                if paper.journal and paper.journal not in journals_cache:
                    try:
                        # Calculate impact factor for the journal
                        result = calculator.calculate_impact_factor(
                            paper.journal
                        )
                        if result and "impact_factors" in result:
                            # Store the 2-year impact factor
                            journals_cache[paper.journal] = result[
                                "impact_factors"
                            ].get("classical_2year")
                        else:
                            journals_cache[paper.journal] = None
                    except Exception as e:
                        logger.debug(
                            f"Could not get impact factor for {paper.journal}: {e}"
                        )
                        journals_cache[paper.journal] = None

                # Add journal impact factor to paper if available
                if (
                    paper.journal in journals_cache
                    and journals_cache[paper.journal]
                ):
                    if (
                        not hasattr(paper, "journal_impact_factor")
                        or not paper.journal_impact_factor
                    ):
                        paper.journal_impact_factor = journals_cache[
                            paper.journal
                        ]
                        enriched_count += 1

            if enriched_count > 0:
                logger.info(f"Added impact factors to {enriched_count} papers")

        except ImportError as e:
            logger.warning(f"Impact factor module not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to enrich impact factors: {e}")

        return papers

    def _merge_enrichment_data(self, paper: "Paper", results: Dict) -> "Paper":
        """Merge enrichment results into paper object.

        Creates a new Paper object with merged data to avoid modifying the original.
        """
        # Import here to avoid circular dependency
        from copy import deepcopy

        enriched = deepcopy(paper)

        # Results from ScholarEngine is already combined metadata, not individual engine results
        if not results:
            return enriched

        # Extract from the combined metadata structure
        # ID section
        if "id" in results:
            if results["id"].get("doi") and not enriched.doi:
                enriched.doi = results["id"]["doi"]
            if results["id"].get("pmid") and not enriched.pmid:
                enriched.pmid = results["id"]["pmid"]
            if results["id"].get("arxiv_id") and not enriched.arxiv_id:
                enriched.arxiv_id = results["id"]["arxiv_id"]
            # Note: corpus_id, semantic_id, ieee_id are in results but not in Paper dataclass

        # Basic metadata section
        if "basic" in results:
            # Always update abstract if found (key enrichment goal)
            if results["basic"].get("abstract"):
                enriched.abstract = results["basic"]["abstract"]

            # Update title if more complete
            if results["basic"].get("title"):
                new_title = results["basic"]["title"]
                if not enriched.title or len(new_title) > len(enriched.title):
                    enriched.title = new_title

            # Update authors if found
            if results["basic"].get("authors") and not enriched.authors:
                enriched.authors = results["basic"]["authors"]

            # Update year if found
            if results["basic"].get("year") and not enriched.year:
                enriched.year = results["basic"]["year"]

            # Update keywords if found
            if results["basic"].get("keywords") and not enriched.keywords:
                enriched.keywords = results["basic"]["keywords"]

        # Publication metadata
        if "publication" in results:
            if results["publication"].get("journal") and not enriched.journal:
                enriched.journal = results["publication"]["journal"]
            if (
                results["publication"].get("publisher")
                and not enriched.publisher
            ):
                enriched.publisher = results["publication"]["publisher"]
            if results["publication"].get("volume") and not enriched.volume:
                enriched.volume = results["publication"]["volume"]
            if results["publication"].get("issue") and not enriched.issue:
                enriched.issue = results["publication"]["issue"]
            if results["publication"].get("pages") and not enriched.pages:
                enriched.pages = results["publication"]["pages"]

        # Citation metadata
        if "citation_count" in results:
            # Try both "count" and "total" fields
            count = results["citation_count"].get("count") or results[
                "citation_count"
            ].get("total")
            if count:
                # Always take the maximum citation count
                if (
                    not enriched.citation_count
                    or count > enriched.citation_count
                ):
                    enriched.citation_count = count
            # Note: influential_citation_count is in results but not in Paper dataclass

        # URL metadata
        if "url" in results:
            if results["url"].get("pdf") and not enriched.pdf_url:
                enriched.pdf_url = results["url"]["pdf"]
            if results["url"].get("url") and not enriched.url:
                enriched.url = results["url"]["url"]

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
    # PDF Downloaders
    # ----------------------------------------
    async def download_pdfs_from_dois_async(
        self, dois: List[str], output_dir: Optional[Path] = None
    ) -> Dict[str, int]:
        """Download PDFs for given DOIs using ScholarURLFinder and ScholarPDFDownloader.

        Args:
            dois: List of DOI strings
            output_dir: Output directory (uses config default if None)

        Returns:
            Dictionary with download statistics
        """
        from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder
        from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader

        results = {"downloaded": 0, "failed": 0, "errors": 0}

        # Get authenticated browser context
        browser, context = (
            await self._browser_manager.get_authenticated_browser_and_context_async()
        )

        # Initialize URL finder and PDF downloader
        url_finder = ScholarURLFinder(
            context=context,
            config=self.config,
            use_cache=True
        )
        pdf_downloader = ScholarPDFDownloader(
            context=context,
            config=self.config,
            use_cache=True
        )

        # Get library paths
        import json
        import shutil
        import hashlib
        from datetime import datetime

        library_dir = self.config.get_library_dir()
        master_dir = library_dir / "MASTER"
        project_dir = library_dir / self.project
        master_dir.mkdir(parents=True, exist_ok=True)
        project_dir.mkdir(parents=True, exist_ok=True)

        for doi in dois:
            try:
                logger.info(f"Processing DOI: {doi}")

                # Step 1: Find URLs for the DOI
                urls = await url_finder.find_urls(doi)

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
                    pdf_url = pdf_entry.get("url") if isinstance(pdf_entry, dict) else pdf_entry

                    if not pdf_url:
                        continue

                    # Download to temp location first
                    temp_output = Path("/tmp") / f"{doi.replace('/', '_').replace(':', '_')}.pdf"

                    # Try to download
                    result = await pdf_downloader.download_from_url(
                        pdf_url=pdf_url,
                        output_path=temp_output
                    )

                    if result and result.exists():
                        downloaded_path = result
                        break

                if downloaded_path:
                    # Step 4: Store PDF in MASTER library with proper organization

                    # Generate unique ID from DOI
                    paper_id = hashlib.md5(doi.encode()).hexdigest()[:8].upper()

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
                        temp_paper = Paper(doi=doi)
                        # Try to enrich to get author/year/journal using async method
                        temp_papers = Papers([temp_paper])
                        enriched = await self.enrich_papers_async(temp_papers)
                        if enriched and len(enriched) > 0:
                            temp_paper = enriched[0]

                        # Generate readable name from metadata
                        first_author = "Unknown"
                        if temp_paper.authors and len(temp_paper.authors) > 0:
                            author_parts = temp_paper.authors[0].split()
                            if len(author_parts) > 1:
                                first_author = author_parts[-1]  # Last name
                            else:
                                first_author = author_parts[0]

                        year_str = str(temp_paper.year) if temp_paper.year else "Unknown"

                        journal_clean = "Unknown"
                        if temp_paper.journal:
                            # Clean journal name - remove special chars, keep alphanumeric
                            journal_clean = "".join(
                                c for c in temp_paper.journal
                                if c.isalnum() or c in " "
                            ).replace(" ", "")
                            if not journal_clean:
                                journal_clean = "Unknown"

                        # Format: Author-Year-Journal
                        readable_name = f"{first_author}-{year_str}-{journal_clean}"
                    except:
                        pass

                    # Fallback to DOI if metadata extraction failed
                    if not readable_name:
                        readable_name = f"DOI_{doi.replace('/', '_').replace(':', '_')}"

                    # Copy PDF to MASTER storage with ORIGINAL filename to track how downloaded
                    # The PDF filename preserves the DOI format for tracking
                    pdf_filename = f"DOI_{doi.replace('/', '_').replace(':', '_')}.pdf"
                    master_pdf_path = storage_path / pdf_filename
                    shutil.copy2(downloaded_path, master_pdf_path)

                    # Create or update metadata with full enriched data
                    metadata_file = storage_path / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    else:
                        metadata = {
                            "doi": doi,
                            "scitex_id": paper_id,
                            "created_at": datetime.now().isoformat(),
                            "created_by": "SciTeX Scholar"
                        }

                    # Add enriched paper metadata if available
                    if temp_paper:
                        # Add all paper fields to metadata
                        paper_dict = temp_paper.to_dict() if hasattr(temp_paper, 'to_dict') else {
                            "title": temp_paper.title,
                            "authors": temp_paper.authors,
                            "year": temp_paper.year,
                            "journal": temp_paper.journal,
                            "abstract": temp_paper.abstract,
                            "citation_count": temp_paper.citation_count,
                            "journal_impact_factor": temp_paper.journal_impact_factor,
                            "keywords": temp_paper.keywords,
                            "url": temp_paper.url,
                            "pdf_url": temp_paper.pdf_url,
                            "publisher": temp_paper.publisher,
                        }
                        # Merge paper metadata
                        for key, value in paper_dict.items():
                            if value is not None and key not in ["doi", "scitex_id"]:
                                metadata[key] = value

                    # Add PDF information
                    metadata["pdf_path"] = str(master_pdf_path.relative_to(library_dir))
                    metadata["pdf_downloaded_at"] = datetime.now().isoformat()
                    metadata["pdf_size_bytes"] = master_pdf_path.stat().st_size
                    metadata["updated_at"] = datetime.now().isoformat()

                    # Save updated metadata
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)

                    # Create symlink in project directory with readable name
                    if self.project not in ["master", "MASTER"]:
                        project_link = project_dir / readable_name
                        if not project_link.exists():
                            project_link.symlink_to(f"../MASTER/{paper_id}")

                    # Clean up temp file
                    downloaded_path.unlink()

                    logger.success(f"Downloaded PDF for {doi}: MASTER/{paper_id}/{pdf_filename}")
                    results["downloaded"] += 1
                else:
                    logger.warning(f"Failed to download any PDF for DOI: {doi}")
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
        dois = [paper.doi for paper in papers if paper.doi]

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

        # Load papers from library
        # For now, return empty Papers until this is implemented
        from ..core.Papers import Papers

        logger.info(f"Loading papers from project: {project_name}")
        return Papers([], project=project_name)

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
    def _create_project_metadata(
        self, project: str, description: Optional[str] = None
    ) -> Path:
        """Create project directory and metadata (PRIVATE).

        Args:
            project: Project name
            description: Optional project description

        Returns:
            Path to the created project directory
        """
        project_dir = self.config.get_library_dir() / project
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create project metadata
        metadata = {
            "name": project,
            "description": description,
            "created": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
        }

        metadata_file = project_dir / "project_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Project created: {project} at {project_dir}")
        return project_dir

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
        import shutil
        from datetime import datetime

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
                browser_mode="stealth",
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

    # ----------------------------------------
    # Deprecated Aliases (Backward Compatibility)
    # ----------------------------------------
    def from_bibtex(self, bibtex_input: Union[str, Path]) -> Papers:
        """DEPRECATED: Use load_bibtex() instead."""
        logger.warning(
            "from_bibtex() is deprecated. Use load_bibtex() instead."
        )
        return self.load_bibtex(bibtex_input)

    def enrich(
        self, papers: Optional[Papers] = None
    ) -> Union[Papers, Dict[str, int]]:
        """DEPRECATED: Use enrich_papers() instead."""
        logger.warning("enrich() is deprecated. Use enrich_papers() instead.")
        return self.enrich_papers(papers)

    def save_papers(self, papers: Papers) -> List[str]:
        """DEPRECATED: Use save_papers_to_library() instead."""
        logger.warning(
            "save_papers() is deprecated. Use save_papers_to_library() instead."
        )
        return self.save_papers_to_library(papers)

    def save_as_bibtex(
        self, papers: Papers, output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """DEPRECATED: Use save_papers_as_bibtex() instead."""
        logger.warning(
            "save_as_bibtex() is deprecated. Use save_papers_as_bibtex() instead."
        )
        return self.save_papers_as_bibtex(papers, output_path)

    def to_bibtex(
        self, papers: Papers, output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """DEPRECATED: Use save_papers_as_bibtex() instead."""
        logger.warning(
            "to_bibtex() is deprecated. Use save_papers_as_bibtex() instead."
        )
        return self.save_papers_as_bibtex(papers, output_path)


# Export all classes and functions
__all__ = ["Scholar"]

if __name__ == "__main__":

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

        # Create some sample papers
        sample_papers = [
            Paper(
                title="Vision Transformer: An Image Is Worth 16x16 Words",
                authors=["Dosovitskiy, Alexey", "Beyer, Lucas"],
                journal="ICLR",
                year=2021,
                doi="10.48550/arXiv.2010.11929",
                keywords=[
                    "vision transformer",
                    "computer vision",
                    "attention",
                ],
                project="neural_networks_2024",
            ),
            Paper(
                title="Scaling Laws for Neural Language Models",
                authors=["Kaplan, Jared", "McCandlish, Sam"],
                journal="arXiv preprint",
                year=2020,
                doi="10.48550/arXiv.2001.08361",
                keywords=["scaling laws", "language models", "GPT"],
                project="neural_networks_2024",
            ),
        ]

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
            papers_from_bibtex = scholar.from_bibtex(sample_bibtex.strip())
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
            f"   ⚙️  Debug mode: {config.resolve('debug_mode', default=False)}"
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
