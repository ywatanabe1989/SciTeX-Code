#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 20:08:29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/_Scholar.py"
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

import asyncio
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

# PDF extraction is now handled by scitex.io
from ..errors import (
    BibTeXEnrichmentError,
    ConfigurationError,
    ScholarError,
    SciTeXWarning,
)
from ..io import load
from ._Paper import Paper
from ._Papers import Papers
from .config import ScholarConfig
from .doi._DOIResolver import DOIResolver
from .download._PDFDownloader import PDFDownloader
from .enrichment._MetadataEnricher import MetadataEnricher

# SmartPDFDownloader removed - using PDFDownloader directly
from .search._UnifiedSearcher import UnifiedSearcher
from .utils._paths import get_scholar_dir

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
        papers.save("my_papers.bib")

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
    ):
        """
        Initialize Scholar with configuration.

        Args:
            config: Can be:
                   - ScholarConfig instance
                   - Path to YAML config file (str or Path)
                   - None (uses ScholarConfig.load() to find config)
        """
        # Handle different config input types
        if config is None:
            self.config = ScholarConfig.load()  # Auto-detect config
        elif isinstance(config, (str, Path)):
            self.config = ScholarConfig.from_yaml(config)
        elif isinstance(config, ScholarConfig):
            self.config = config
        else:
            raise TypeError(f"Invalid config type: {type(config)}")

        # Set workspace directory using path manager
        self.workspace_dir = self.config.path_manager.workspace_dir
        
        # Initialize components with config system
        self._searcher = UnifiedSearcher(config=self.config)

        self._enricher = MetadataEnricher(config=self.config)

        # Initialize PDF downloader
        self._initialize_pdf_downloader()

        # Initialize DOI resolver with config
        self._doi_resolver = DOIResolver(config=self.config)

        logger.info(f"Scholar initialized (workspace: {self.workspace_dir})")

        # Print configuration summary
        self._print_config_summary()

    def search(
        self,
        query: str,
        limit: int = 100,
        sources: Union[str, List[str]] = "pubmed",
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs,
    ) -> Papers:
        """
        Search for papers from one or more sources.

        Args:
            query: Search query
            limit: Maximum results (default 100)
            sources: Source(s) to search - can be a string or list of strings
                    ('pubmed', 'semantic_scholar', 'google_scholar', 'arxiv')
            year_min: Minimum publication year
            year_max: Maximum publication year
            search_mode: Search mode - 'strict' (all terms required) or 'flexible' (any terms)
            **kwargs: Additional search parameters

        Returns:
            Papers with results
        """
        print(f"Searching papers...")
        print(f"Query: {query}")
        print(f"  Limit: {limit}")
        print(f"  Sources: {sources}")

        if year_min:
            print(f"  Year min: {year_min}")
        if year_max:
            print(f"  Year max: {year_max}")
        for key, value in kwargs.items():
            print(f"  {key}: {value}")

        # Ensure sources is a list
        if isinstance(sources, str):
            sources = [sources]

        # Run async search in sync context
        coro = self._searcher.search_async(
            query=query,
            sources=sources,
            limit=limit,
            year_min=year_min,
            year_max=year_max,
            **kwargs,
        )
        logger.debug(f"Searching with sources: {sources}")
        papers = self._run_async(coro)
        logger.debug(f"Search returned {len(papers)} papers")

        # Create collection (deduplication is automatic)
        # Pass source priority for intelligent deduplication
        collection = Papers(papers, source_priority=sources)

        # Log search results
        if not papers:
            logger.info(f"No results found for query: '{query}'")
            # Suggest alternative sources if default source was used
            if "semantic_scholar" in sources:
                logger.info(
                    "Try searching with different sources or check your internet connection"
                )
        else:
            logger.info(f"Found {len(papers)} papers for query: '{query}'")

        # Auto-enrich if enabled
        if self.config.enable_auto_enrich and papers:
            logger.info("Auto-enriching papers...")
            # Only try Semantic Scholar for citations if it was in the search sources
            use_semantic_scholar = "semantic_scholar" in (sources or [])
            self._enricher.enrich_all(
                papers,
                enrich_impact_factors=True,  # Always enrich with impact factors
                enrich_citations=True,
                enrich_journal_metrics=True,  # Always enrich with journal metrics
                use_semantic_scholar_for_citations=use_semantic_scholar,
            )
            collection._enriched = True

        # Auto-download if enabled
        if self.config.enable_auto_download and papers:
            open_access = [p for p in papers if p.pdf_url]
            if open_access:
                logger.info(
                    f"Auto-downloading {len(open_access)} open-access PDFs..."
                )
                # Download PDFs for open access papers
                dois = [p.doi for p in open_access if p.doi]
                if dois:
                    self.download_pdfs(dois, show_progress=False)

        print(f"\nFound:")
        print(collection.to_dataframe())

        return collection

    def search_local(self, query: str, limit: int = 20) -> Papers:
        """
        Search local PDF library.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Papers with local results
        """
        # Use the UnifiedSearcher with 'local' source
        papers = self._run_async(
            self._searcher.search_async(query, sources=["local"], limit=limit)
        )
        return Papers(papers)

    def _index_local_pdfs(
        self, directory: Union[str, Path], recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Index local PDF files for searching.

        Args:
            directory: Directory containing PDFs
            recursive: Search subdirectories

        Returns:
            Indexing statistics
        """
        # Build local index using the searcher
        return self._searcher.build_local_index([directory])

    def download_pdfs(
        self,
        items: Union[List[str], List[Paper], Papers, str, Paper],
        download_dir: Optional[Union[str, Path]] = None,
        force: bool = False,
        max_workers: int = 4,
        show_progress: bool = True,
        acknowledge_ethical_usage: Optional[bool] = None,
        verify_auth_live: bool = True,
        auto_authenticate: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Download PDFs for DOIs or papers.

        This is the main entry point for downloading PDFs. It accepts various input types
        and delegates to the appropriate downloader.

        Args:
            items: Can be:
                - List of DOI strings
                - Single DOI string
                - List of Paper objects
                - Single Paper object
                - Papers collection
            download_dir: Directory to save PDFs (default: workspace_dir/pdfs)
            force: Force re-download even if files exist
            max_workers: Maximum concurrent downloads
            show_progress: Show download progress
            acknowledge_ethical_usage: Acknowledge ethical usage terms for Sci-Hub (default: from config)
            verify_auth_live: If True, performs live verification of OpenAthens authentication
                            (adds ~2-3s but ensures session is valid). Default: True.
            auto_authenticate: If True, automatically opens browser for authentication without prompting.
                             If False, prompts user before opening browser. Default: False.
            **kwargs: Additional arguments passed to downloader

        Returns:
            Dictionary with download results:
                - 'successful': Number of successful downloads
                - 'failed': Number of failed downloads
                - 'results': List of detailed results
                - 'downloaded_files': Dict mapping DOIs to file paths

        Examples:
            >>> # Download from DOIs
            >>> scholar.download_pdfs(["10.1234/doi1", "10.5678/doi2"])

            >>> # Download from Papers collection
            >>> papers = scholar.search("deep learning")
            >>> scholar.download_pdfs(papers)

            >>> # Download single DOI
            >>> scholar.download_pdfs("10.1234/example")
        """
        # Use the integrated PDFDownloader instead of standalone SciHubDownloader

        # Set default download directory
        if download_dir is None:
            download_dir = self.workspace_dir / "pdfs"

        # Normalize input to list
        if isinstance(items, str):
            # Single DOI string
            items = [items]
        elif isinstance(items, Paper):
            # Single Paper object
            items = [items]
        elif isinstance(items, Papers):
            # Papers collection
            items = items.papers

        # Determine if we have DOIs or Papers
        if items and isinstance(items[0], str):
            # List of DOI strings
            dois = items
        else:
            # List of Paper objects - extract DOIs
            dois = []
            for paper in items:
                if paper.doi:
                    dois.append(paper)
                else:
                    logger.warning(
                        f"Paper '{paper.title}' has no DOI, skipping download"
                    )

        if not dois:
            return {
                "successful": 0,
                "failed": 0,
                "results": [],
                "downloaded_files": {},
            }

        # Update PDFDownloader settings
        self._pdf_downloader.acknowledge_ethical_usage = (
            acknowledge_ethical_usage
        )
        self._pdf_downloader.max_concurrent = max_workers

        # Check OpenAthens authentication first if enabled
        if self.config.openathens_enabled:
            logger.info("Checking OpenAthens authentication status...")
            try:
                # First try a quick local check
                is_authenticated = self._run_async(
                    self._pdf_downloader.openathens_authenticator.is_authenticated(
                        verify_live=False
                    )
                )

                if is_authenticated:
                    logger.info("Using existing OpenAthens session")
                else:
                    # If not authenticated locally, try to authenticate
                    # This will load cached sessions if available
                    auth_success = self.authenticate_openathens(force=False)

                    if not auth_success:
                        # Only show the authentication UI if we really need to authenticate
                        print("\n" + "=" * 60)
                        print("🔒 OpenAthens Authentication Required")
                        print("=" * 60)
                        print(
                            "\nAuthentication is required to download PDFs from your institution."
                        )
                        print("Opening browser for login...")
                        print("\n• You'll need your institutional credentials")
                        print("• You may need to complete 2FA")
                        print("\n🌐 Opening browser for authentication...")

                        # Now try with UI
                        auth_success = self.authenticate_openathens(
                            force=False
                        )

                        if auth_success:
                            print(
                                "\n✅ Authentication successful! Proceeding with downloads...\n"
                            )
                            # Continue with download after successful auth
                        else:
                            print(
                                "\n❌ Authentication failed or was cancelled."
                            )
                            return {
                                "successful": 0,
                                "failed": len(dois),
                                "results": [
                                    {
                                        "doi": (
                                            doi
                                            if isinstance(doi, str)
                                            else doi.doi
                                        ),
                                        "success": False,
                                        "error": "OpenAthens authentication failed",
                                        "method": None,
                                    }
                                    for doi in dois
                                ],
                                "summary": {"auth_failed": True},
                            }
            except KeyboardInterrupt:
                print("\n\n❌ Authentication cancelled by user.")
                return {
                    "successful": 0,
                    "failed": len(dois),
                    "results": [
                        {
                            "doi": doi if isinstance(doi, str) else doi.doi,
                            "success": False,
                            "error": "Authentication cancelled by user",
                            "method": None,
                        }
                        for doi in dois
                    ],
                    "summary": {"cancelled": True},
                }
            except Exception as e:
                logger.warning(f"OpenAthens authentication check failed: {e}")
                # Continue anyway - maybe cookies work even if check fails

        # Download PDFs using the integrated downloader
        async def download_batch_async():
            # Extract DOIs and metadata
            identifiers = []
            metadata_list = []

            for item in dois:
                if isinstance(item, str):
                    identifiers.append(item)
                    metadata_list.append(None)
                elif isinstance(item, Paper):
                    identifiers.append(item.doi)
                    metadata_list.append(
                        {
                            "title": item.title,
                            "authors": item.authors,
                            "year": item.year,
                        }
                    )

            return await self._pdf_downloader.batch_download_async(
                identifiers=identifiers,
                output_dir=download_dir,
                metadata_list=metadata_list,
                show_progress=show_progress,
                return_detailed=True,  # Get method information
            )

        # Run async function
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, download_batch_async()
                    )
                    results = future.result()
            else:
                results = loop.run_until_complete(download_batch_async())
        except RuntimeError:
            # No event loop
            results = asyncio.run(download_batch_async())

        # Create Papers instance with successfully downloaded papers
        downloaded_papers = []

        # Map identifiers back to papers
        identifier_to_paper = {}
        for item in items:
            if isinstance(item, Paper):
                identifier = item.doi or item.get_identifier()
                if identifier:
                    identifier_to_paper[identifier] = item

        # If we have DOI strings, we need to create Paper objects for successful downloads
        if not identifier_to_paper:
            # We were given DOI strings, not Paper objects
            for identifier, result in results.items():
                if result:
                    # Extract path and method from detailed result
                    path = result["path"]
                    method = result["method"]

                    # Create a minimal Paper object with the DOI and PDF path
                    paper = Paper(
                        title=f"Paper with DOI: {identifier}",
                        authors=[],
                        abstract="",  # Empty abstract for DOI-only downloads
                        year=None,
                        journal=None,
                        doi=identifier,
                    )
                    paper.pdf_path = path
                    paper.pdf_source = method  # Actual method used
                    downloaded_papers.append(paper)
        else:
            # Collect successfully downloaded papers from existing Paper objects
            for identifier, result in results.items():
                if result and identifier in identifier_to_paper:
                    # Extract path and method from detailed result
                    path = result["path"]
                    method = result["method"]

                    paper = identifier_to_paper[identifier]
                    paper.pdf_path = path  # Update PDF path
                    paper.pdf_source = method  # Actual method used
                    downloaded_papers.append(paper)

        # Create Papers instance
        return Papers(downloaded_papers)

    def _enrich_papers(
        self,
        papers: Union[List[Paper], Papers],
        impact_factors: bool = True,
        citations: bool = True,
        journal_metrics: bool = True,
    ) -> Union[List[Paper], Papers]:
        """
        Enrich papers with all available metadata.

        Args:
            papers: Papers to enrich
            impact_factors: Add journal impact factors
            citations: Add citation counts
            journal_metrics: Add quartiles, rankings

        Returns:
            Enriched papers (same type as input)
        """
        if isinstance(papers, Papers):
            self._enricher.enrich_all(
                papers.papers,
                enrich_impact_factors=impact_factors,
                enrich_citations=citations,
                enrich_journal_metrics=journal_metrics,
            )
            papers._enriched = True
            return papers
        else:
            return self._enricher.enrich_all(
                papers,
                enrich_impact_factors=impact_factors,
                enrich_citations=citations,
                enrich_journal_metrics=journal_metrics,
            )

    def enrich_bibtex(
        self,
        bibtex_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        backup: bool = True,
        preserve_original_fields: bool = True,
        add_missing_abstracts: bool = True,
        add_missing_urls: bool = True,
    ) -> Papers:
        """
        Enrich an existing BibTeX file with impact factors, citations, and missing fields.

        Args:
            bibtex_path: Path to input BibTeX file
            output_path: Path for enriched output (defaults to input path)
            backup: Create backup of original file before overwriting
            preserve_original_fields: Keep all original BibTeX fields
            add_missing_abstracts: Fetch abstracts for entries without them
            add_missing_urls: Fetch URLs for entries without them

        Returns:
            Papers with enriched papers
        """
        bibtex_path = Path(bibtex_path)
        if not bibtex_path.exists():
            from ..errors import PathNotFoundError

            raise PathNotFoundError(str(bibtex_path))

        # Set output path
        if output_path is None:
            output_path = bibtex_path
        else:
            output_path = Path(output_path)

        # Create backup if needed
        if backup and output_path == bibtex_path:
            backup_path = bibtex_path.with_suffix(".bib.bak")
            import shutil

            shutil.copy2(bibtex_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Load existing BibTeX entries
        logger.info(f"Loading BibTeX file: {bibtex_path}")
        try:
            entries = load(str(bibtex_path))
        except Exception as e:
            raise BibTeXEnrichmentError(
                str(bibtex_path), f"Failed to load BibTeX file: {str(e)}"
            )

        # Convert BibTeX entries to Paper objects
        papers = []
        original_fields_map = {}

        for entry in entries:
            paper = self._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)
                # Store original fields for preservation
                if preserve_original_fields:
                    original_fields_map[paper.get_identifier()] = entry[
                        "fields"
                    ]

        logger.info(f"Parsed {len(papers)} papers from BibTeX file")

        # Create collection
        collection = Papers(papers)

        # Enrich papers with impact factors and citations
        if papers:
            logger.info(
                "Enriching papers with impact factors and citations..."
            )
            self._enricher.enrich_all(
                papers,
                enrich_impact_factors=True,  # Always enrich with impact factors
                enrich_citations=True,
                enrich_journal_metrics=True,  # Always enrich with journal metrics
            )

            # Always fetch missing DOIs, and optionally abstracts/URLs
            logger.info(
                "Fetching missing DOIs and other information from online sources..."
            )
            self._fetch_missing_fields(
                papers, add_missing_abstracts, add_missing_urls
            )

        # Merge original fields if preserving
        if preserve_original_fields:
            for paper in papers:
                paper_id = paper.get_identifier()
                if paper_id in original_fields_map:
                    paper._original_bibtex_fields = original_fields_map[
                        paper_id
                    ]

        # Save enriched BibTeX
        collection.save(str(output_path))
        logger.info(f"Saved enriched BibTeX to: {output_path}")

        return collection

    def _bibtex_entry_to_paper(self, entry: Dict[str, Any]) -> Optional[Paper]:
        """
        Convert a parsed BibTeX entry to a Paper object.

        Args:
            entry: Parsed BibTeX entry dictionary

        Returns:
            Paper object or None if conversion fails
        """
        try:
            fields = entry.get("fields", {})

            # Extract authors
            authors_str = fields.get("author", "")
            authors = self._parse_bibtex_authors(authors_str)

            # Extract Semantic Scholar Corpus ID if URL is from api.semanticscholar.org
            url = fields.get("url", "")
            semantic_scholar_id = None
            if "api.semanticscholar.org/CorpusId:" in url:
                # Extract corpus ID from URL
                match = re.search(r"CorpusId:(\d+)", url)
                if match:
                    semantic_scholar_id = match.group(1)

            # Create Paper object with available fields
            paper = Paper(
                title=fields.get("title", "").strip(),
                authors=authors,
                year=(
                    int(fields.get("year", 0))
                    if fields.get("year", "").isdigit()
                    else None
                ),
                journal=fields.get("journal", fields.get("booktitle", "")),
                doi=fields.get("doi", ""),
                pmid=fields.get("pmid", ""),
                arxiv_id=fields.get("arxiv", ""),
                abstract=fields.get("abstract", ""),
                pdf_url=fields.get("url", ""),
                keywords=self._parse_bibtex_keywords(
                    fields.get("keywords", "")
                ),
                source=f"bibtex:{entry.get('key', 'unknown')}",
            )

            # Store Semantic Scholar ID for later use
            if semantic_scholar_id:
                paper._semantic_scholar_corpus_id = semantic_scholar_id

            # Add volume, pages if available
            if "volume" in fields:
                paper.volume = fields["volume"]
            if "pages" in fields:
                paper.pages = fields["pages"]

            # Store entry type and key
            paper._bibtex_entry_type = entry.get("entry_type", "article")
            paper._bibtex_key = entry.get("key", "")

            return paper

        except Exception as e:
            logger.warning(f"Failed to convert BibTeX entry: {e}")
            return None

    def _parse_bibtex_authors(self, authors_str: str) -> List[str]:
        """Parse BibTeX author string into list of author names."""
        if not authors_str:
            return []

        # Split by 'and'
        authors = []
        for author in authors_str.split(" and "):
            author = author.strip()
            if author:
                # Handle "Last, First" format
                if "," in author:
                    parts = author.split(",", 1)
                    author = f"{parts[1].strip()} {parts[0].strip()}"
                authors.append(author)

        return authors

    def _parse_bibtex_keywords(self, keywords_str: str) -> List[str]:
        """Parse BibTeX keywords string into list."""
        if not keywords_str:
            return []

        # Split by comma or semicolon
        keywords = []
        for kw in re.split(r"[,;]", keywords_str):
            kw = kw.strip()
            if kw:
                keywords.append(kw)

        return keywords

    def _fetch_missing_fields(
        self, papers: List[Paper], fetch_abstracts: bool, fetch_urls: bool
    ):
        """
        Fetch missing DOIs, abstracts and URLs from online sources.
        Uses batch processing for efficiency when handling multiple papers.

        Args:
            papers: List of Paper objects
            fetch_abstracts: Whether to fetch missing abstracts
            fetch_urls: Whether to fetch missing URLs
        """
        papers_to_update = []

        for paper in papers:
            needs_update = False

            # Always try to get DOI if missing
            if not paper.doi:
                needs_update = True
            if fetch_abstracts and not paper.abstract:
                needs_update = True
            if fetch_urls and not paper.pdf_url:
                needs_update = True

            if needs_update:
                papers_to_update.append(paper)

        if not papers_to_update:
            return

        logger.info(
            f"Fetching missing fields for {len(papers_to_update)} papers..."
        )

        # Use batch processing for efficiency
        if len(papers_to_update) > 1:
            logger.info(
                "Using batch processing for efficient DOI resolution..."
            )

            # Extract titles and years for batch resolution
            titles = []
            years = []
            for paper in papers_to_update:
                if not paper.doi:  # Only resolve if DOI is missing
                    titles.append(paper.title)
                    years.append(paper.year)

            # Batch resolve DOIs
            if titles:
                doi_results = self._doi_resolver.batch_resolve(
                    titles=titles, years=years, show_progress=True
                )

                # Update papers with resolved DOIs
                for paper in papers_to_update:
                    if not paper.doi and paper.title in doi_results:
                        resolved_doi = doi_results[paper.title]
                        if resolved_doi:
                            paper.doi = resolved_doi
                            logger.info(
                                f"  ✓ Found DOI for: {paper.title[:50]}... -> {resolved_doi}"
                            )

            # Update URLs if needed
            for paper in papers_to_update:
                if (
                    paper.doi
                    and fetch_urls
                    and "api.semanticscholar.org" in (paper.pdf_url or "")
                ):
                    paper.pdf_url = f"https://doi.org/{paper.doi}"
                    logger.info(
                        f"  ✓ Updated URL to DOI link for: {paper.title[:50]}..."
                    )

                # Fetch abstracts if needed
                if paper.doi and fetch_abstracts and not paper.abstract:
                    abstract = self._doi_resolver.get_abstract(paper.doi)
                    if abstract:
                        paper.abstract = abstract
                        logger.info(
                            f"  ✓ Found abstract for: {paper.title[:50]}..."
                        )

        else:
            # Single paper - use regular resolver
            paper = papers_to_update[0]
            logger.debug(f"Processing single paper: {paper.title[:50]}...")

            # Try to get DOI
            if not paper.doi:
                # First try URL resolution if available
                if paper.pdf_url:
                    doi = self._doi_resolver.resolve_from_url(paper.pdf_url)
                    if doi:
                        paper.doi = doi
                        logger.info(f"  ✓ Found DOI from URL: {doi}")

                # If still no DOI, try title-based search
                if not paper.doi:
                    authors_tuple = (
                        tuple(paper.authors) if paper.authors else None
                    )

                    doi = self._doi_resolver.title_to_doi(
                        title=paper.title,
                        year=paper.year,
                        authors=authors_tuple,
                    )

                    if doi:
                        paper.doi = doi
                        logger.info(f"  ✓ Found DOI from title: {doi}")

                # Update URL if needed
                if (
                    paper.doi
                    and fetch_urls
                    and "api.semanticscholar.org" in (paper.pdf_url or "")
                ):
                    paper.pdf_url = f"https://doi.org/{paper.doi}"
                    logger.info(f"  ✓ Updated URL to DOI link")

            # Get abstract if needed
            if paper.doi and fetch_abstracts and not paper.abstract:
                abstract = self._doi_resolver.get_abstract(paper.doi)
                if abstract:
                    paper.abstract = abstract
                    logger.info(f"  ✓ Found abstract")

    def resolve_doi(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Resolve DOI from paper title using multiple sources.

        This method uses CrossRef, PubMed, and OpenAlex to find DOIs,
        avoiding rate-limited services like Semantic Scholar.

        Args:
            title: Paper title
            year: Publication year (optional but improves accuracy)
            authors: List of author names (optional but improves accuracy)

        Returns:
            DOI string if found, None otherwise

        Example:
            doi = scholar.resolve_doi(
                "The functional role of cross-frequency coupling",
                year=2010
            )
            # Returns: "10.1016/j.tins.2010.09.001"
        """
        # Convert authors to tuple for caching if provided
        authors_tuple = tuple(authors) if authors else None
        return self._doi_resolver.title_to_doi(title, year, authors_tuple)

    def _search_crossref_by_title(
        self, title: str, authors: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search CrossRef API by title to find DOI.

        Args:
            title: Paper title
            authors: List of author names (optional)

        Returns:
            List of matching papers from CrossRef
        """
        try:
            from urllib.parse import quote

            import requests

            # Build query
            query = quote(title)

            # Add author to query if available
            if authors and len(authors) > 0:
                first_author = authors[0]
                # Extract last name
                last_name = first_author.split()[-1] if first_author else ""
                if last_name:
                    query += f"+{quote(last_name)}"

            # CrossRef API URL
            url = f"https://api.crossref.org/works"
            params = {
                "query": title,  # Use unquoted title for query parameter
                "rows": 5,
                "select": "DOI,title,author,abstract,published-print,type",
            }

            # Add email if configured for polite access
            if self._email_crossref:
                params["mailto"] = self._email_crossref

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                items = data.get("message", {}).get("items", [])

                # Filter results by title similarity
                results = []
                for item in items:
                    crossref_title = item.get("title", [""])[0]
                    # Simple similarity check
                    if (
                        crossref_title
                        and self._title_similarity(title, crossref_title) > 0.8
                    ):
                        results.append(item)

                return results
            else:
                logger.debug(f"CrossRef API returned {response.status_code}")
                return []

        except Exception as e:
            logger.debug(f"CrossRef search error: {e}")
            return []

    def _title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles (simple approach).

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity score between 0 and 1
        """
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()

        # Remove punctuation
        import string

        translator = str.maketrans("", "", string.punctuation)
        t1 = t1.translate(translator)
        t2 = t2.translate(translator)

        # Split into words
        words1 = set(t1.split())
        words2 = set(t2.split())

        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def configure_openathens(
        self, email: Optional[str] = None, save_to_env: bool = False
    ):
        """
        Configure OpenAthens authentication.

        Args:
            email: Institutional email address (e.g., 'user@institution.edu')
            save_to_env: Save configuration to environment variables

        Note:
            Uses the unified MyAthens interface. Authentication is done
            manually in the browser when you call authenticate_openathens().
        """
        import getpass

        # Update configuration
        self.config.openathens_enabled = True
        if email:
            self.config.openathens_email = email

        # Save to environment if requested
        if save_to_env:
            import os

            os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
            if email:
                os.environ["SCITEX_SCHOLAR_OPENATHENS_EMAIL"] = email

        # Reinitialize PDF downloader with OpenAthens
        openathens_config = {
            "email": self.config.openathens_email,
            "debug_mode": (
                self.config.debug_mode
                if hasattr(self.config, "debug_mode")
                else False
            ),
        }

        # Update to use PDFDownloader with new configuration
        self._pdf_downloader = PDFDownloader(
            download_dir=(
                Path(self.config.pdf_dir).expanduser()
                if self.config.pdf_dir
                else None
            ),
            use_translators=True,
            use_playwright=True,
            use_openathens=True,  # OpenAthens is now configured
            openathens_config=openathens_config,
            use_lean_library=self.config.use_lean_library,
            timeout=30,
            max_retries=3,
            max_concurrent=self.config.max_parallel_requests,
            debug_mode=self.config.debug_mode,
        )

        logger.info("OpenAthens configured")

    def authenticate_openathens(self, force: bool = False) -> bool:
        """
        Manually trigger OpenAthens authentication (sync version).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        return self._run_async(self.authenticate_openathens_async(force))

    async def authenticate_openathens_async(self, force: bool = False) -> bool:
        """
        Manually trigger OpenAthens authentication (async version).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        if not self.config.openathens_enabled:
            raise ScholarError(
                "OpenAthens not configured. Call configure_openathens() first."
            )

        if not self._pdf_downloader.openathens_authenticator:
            raise ScholarError("OpenAthens authenticator not initialized")

        return (
            await self._pdf_downloader.openathens_authenticator.authenticate(
                force=force
            )
        )

    def is_openathens_authenticated(self) -> bool:
        """
        Check if OpenAthens is authenticated (sync version).

        Returns:
            True if authenticated and session is valid
        """
        return self._run_async(self.is_openathens_authenticated_async())

    async def is_openathens_authenticated_async(self) -> bool:
        """
        Check if OpenAthens is authenticated (async version).

        Returns:
            True if authenticated and session is valid
        """
        if not self.config.openathens_enabled:
            return False

        if not self._pdf_downloader.openathens_authenticator:
            return False

        return (
            await self._pdf_downloader.openathens_authenticator.is_authenticated_async()
        )

    def ensure_authenticated(self, force: bool = False) -> bool:
        """
        Ensure OpenAthens is authenticated, opening browser if needed.

        This is a convenience method that:
        1. Checks if already authenticated
        2. If not, automatically opens browser for authentication
        3. Returns True if authenticated (either already or after login)

        Args:
            force: Force re-authentication even if already logged in

        Returns:
            True if authenticated successfully

        Example:
            >>> scholar = Scholar(openathens_enabled=True)
            >>> if scholar.ensure_authenticated():
            ...     papers = scholar.search("quantum")
            ...     scholar.download_pdfs(papers)
        """
        if not self.config.openathens_enabled:
            return True  # No auth needed

        # Check current status
        if not force and self.is_openathens_authenticated():
            logger.info("Already authenticated with OpenAthens")
            return True

        # Need to authenticate
        print("\n" + "=" * 60)
        print("🔐 OpenAthens Authentication Required")
        print("=" * 60)
        print("\nOpening browser for authentication...")
        print("Please log in with your institutional credentials.\n")

        # Authenticate
        success = self.authenticate_openathens(force=force)

        if success:
            print("\n✅ Authentication successful!")
        else:
            print("\n❌ Authentication failed!")

        return success

    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about local PDF library."""
        # Get stats from the local search engine
        pdf_dir = self.workspace_dir / "pdfs"
        if not pdf_dir.exists():
            return {"total_pdfs": 0, "indexed": 0}

        # Count PDF files
        pdf_files = list(pdf_dir.rglob("*.pdf"))
        return {
            "total_pdfs": len(pdf_files),
            "pdf_directory": str(pdf_dir),
            "indexed": len(pdf_files),  # Assume all PDFs are indexed
        }

    def search_quick(self, query: str, top_n: int = 5) -> List[str]:
        """
        Quick search returning just paper titles.

        Args:
            query: Search query
            top_n: Number of results

        Returns:
            List of paper titles
        """
        papers = self.search(query, limit=top_n)
        return [p.title for p in papers]

    def find_similar(self, paper_title: str, limit: int = 10) -> Papers:
        """
        Find papers similar to a given paper.

        Args:
            paper_title: Title of reference paper
            limit: Number of similar papers

        Returns:
            Papers with similar papers
        """
        # First find the paper
        reference = self.search(paper_title, limit=1)
        if not reference:
            logger.warning(f"Could not find paper: {paper_title}")
            return Papers([])

        # Search for similar topics
        ref_paper = reference[0]

        # Build query from title and keywords
        query_parts = [ref_paper.title]
        if ref_paper.keywords:
            query_parts.extend(ref_paper.keywords[:3])

        query = " ".join(query_parts)

        # Search and filter out the reference paper
        similar = self.search(query, limit=limit + 1)
        similar_papers = [
            p
            for p in similar.papers
            if p.get_identifier() != ref_paper.get_identifier()
        ]

        return Papers(similar_papers[:limit])

    def _extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF file for downstream AI processing.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        # Use scitex.io for PDF text extraction
        from ..io import load

        return load(str(pdf_path), mode="text")

    def _extract_sections(self, pdf_path: Union[str, Path]) -> Dict[str, str]:
        """
        Extract text organized by sections.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary mapping section names to text
        """
        # Use scitex.io for section extraction
        from ..io import load

        return load(str(pdf_path), mode="sections")

    def _extract_for_ai(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Extract comprehensive data from PDF for AI processing.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with:
            - full_text: Complete text
            - sections: Text by section
            - metadata: PDF metadata
            - stats: Word count, page count, etc.
        """
        # Use scitex.io for comprehensive extraction
        from ..io import load

        return load(str(pdf_path), mode="full")

    def extract_text_from_papers(
        self, papers: Union[List[Paper], Papers]
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple papers for AI processing.

        Args:
            papers: Papers to extract text from

        Returns:
            List of extraction results with paper metadata
        """
        if isinstance(papers, Papers):
            papers = papers.papers

        results = []
        for paper in papers:
            if paper.pdf_path and paper.pdf_path.exists():
                extraction = self._extract_for_ai(paper.pdf_path)
                extraction["paper"] = {
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.year,
                    "doi": paper.doi,
                    "journal": paper.journal,
                }
                results.append(extraction)
            else:
                # Include paper even without PDF
                results.append(
                    {
                        "paper": {
                            "title": paper.title,
                            "authors": paper.authors,
                            "year": paper.year,
                            "doi": paper.doi,
                            "journal": paper.journal,
                        },
                        "full_text": paper.abstract or "",
                        "error": "No PDF available",
                    }
                )

        return results

    def _initialize_pdf_downloader(self):
        """Initialize or reinitialize the PDF downloader with current configuration."""
        # Prepare OpenAthens config if enabled
        openathens_config = None
        if self.config.openathens_enabled:
            openathens_config = {
                "email": self.config.openathens_email,
                "debug_mode": (
                    self.config.debug_mode
                    if hasattr(self.config, "debug_mode")
                    else False
                ),
            }

        # Initialize PDFDownloader with config
        self._pdf_downloader = PDFDownloader(
            download_dir=(
                Path(self.config.pdf_dir).expanduser()
                if self.config.pdf_dir
                else None
            ),
            use_translators=True,
            use_playwright=True,
            use_openathens=self.config.openathens_enabled,
            openathens_config=openathens_config,
            use_lean_library=self.config.use_lean_library,
            zenrows_api_key=self.config.zenrows_api_key,  # Auto-enables if present
            timeout=30,
            max_retries=3,
            max_concurrent=self.config.max_parallel_requests,
            debug_mode=self.config.debug_mode,
        )

        # Pass config to downloader for EZProxy support
        self._pdf_downloader.config = self.config

    def _print_config_summary(self):
        """Print configuration summary on initialization."""
        print("\n" + "=" * 60)
        print("SciTeX Scholar - Configuration Summary")
        print("=" * 60)

        # Helper function to mask sensitive data
        def mask_sensitive(value, show_first=4):
            """Mask sensitive data showing only first few characters."""
            if not value:
                return None
            if len(str(value)) > show_first + 3:
                return f"{str(value)[:show_first]}{'*' * (len(str(value)) - show_first)}"
            else:
                return "*" * len(str(value))

        # API Keys status
        print("\n📚 API Keys:")
        if self.config.semantic_scholar_api_key:
            masked_key = mask_sensitive(self.config.semantic_scholar_api_key)
            print(f"  • Semantic Scholar: ✓ Configured ({masked_key})")
        else:
            print(
                f"  • Semantic Scholar: ✗ Not set (citations via CrossRef only)"
            )

        if self.config.crossref_api_key:
            masked_key = mask_sensitive(self.config.crossref_api_key)
            print(f"  • CrossRef: ✓ Configured ({masked_key})")
        else:
            print(f"  • CrossRef: ✗ Not set (works without key)")

        if self.config.pubmed_email:
            # Mask email but show domain
            parts = self.config.pubmed_email.split("@")
            if len(parts) == 2:
                masked_email = f"{mask_sensitive(parts[0], 2)}@{parts[1]}"
            else:
                masked_email = mask_sensitive(self.config.pubmed_email)
            print(f"  • PubMed Email: ✓ Set ({masked_email})")
        else:
            print(f"  • PubMed Email: ✗ Not set (required for PubMed)")

        # Features
        print("\n⚙️  Features:")
        print(
            f"  • Auto-enrichment: {'✓ Enabled' if self.config.enable_auto_enrich else '✗ Disabled'}"
        )
        print(f"  • Impact factors: ✓ Using JCR package (2024 data)")
        print(
            f"  • Auto-download PDFs: {'✓ Enabled' if self.config.enable_auto_download else '✗ Disabled'}"
        )

        # OpenAthens status
        if self.config.openathens_enabled:
            print(
                f"  • OpenAthens: ✓ Enabled ({self.config.openathens_org_id})"
            )
            if self.config.openathens_username:
                masked_user = mask_sensitive(
                    self.config.openathens_username, 3
                )
                print(f"    - Username: {masked_user}")
            if self.config.openathens_idp_url:
                print(f"    - IdP URL: {self.config.openathens_idp_url}")
        else:
            print(f"  • OpenAthens: ✗ Disabled")

        # Shibboleth status
        if self.config.shibboleth_enabled:
            print(
                f"  • Shibboleth: ✓ Enabled ({self.config.shibboleth_institution or 'No institution set'})"
            )
            if self.config.shibboleth_username:
                masked_user = mask_sensitive(
                    self.config.shibboleth_username, 3
                )
                print(f"    - Username: {masked_user}")
            if self.config.shibboleth_idp_url:
                print(f"    - IdP URL: {self.config.shibboleth_idp_url}")
        else:
            print(f"  • Shibboleth: ✗ Disabled")

        # Settings
        print("\n📁 Settings:")
        print(f"  • Workspace: {self.workspace_dir}")
        print(f"  • Default search limit: {self.config.default_search_limit}")
        print(
            f"  • Default sources: {', '.join(self.config.default_search_sources)}"
        )

        print("\n💡 Tip: Configure with environment variables or YAML file")
        print("  See: stx.scholar.ScholarConfig.show_env_vars()")
        print("=" * 60 + "\n")

    def configure_ezproxy(
        self,
        proxy_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        institution: Optional[str] = None,
        save_to_env: bool = False,
    ):
        """
        Configure EZProxy authentication.

        Args:
            proxy_url: EZProxy server URL (e.g., 'https://ezproxy.library.edu')
            username: Username for authentication
            password: Password for authentication
            institution: Institution name
            save_to_env: Save configuration to environment variables

        Example:
            scholar.configure_ezproxy(
                proxy_url="https://ezproxy.myuni.edu",
                username="johndoe",
                institution="My University"
            )
        """
        import getpass

        # Update configuration
        self.config.ezproxy_enabled = True

        if proxy_url:
            self.config.ezproxy_url = proxy_url
        elif not self.config.ezproxy_url:
            self.config.ezproxy_url = input("EZProxy URL: ")

        if username:
            self.config.ezproxy_username = username
        elif not self.config.ezproxy_username:
            self.config.ezproxy_username = input("EZProxy username: ")

        if password:
            self.config.ezproxy_password = password

        if institution:
            self.config.ezproxy_institution = institution

        # Save to environment if requested
        if save_to_env:
            env_vars = {
                "SCITEX_SCHOLAR_EZPROXY_ENABLED": "true",
                "SCITEX_SCHOLAR_EZPROXY_URL": self.config.ezproxy_url,
                "SCITEX_SCHOLAR_EZPROXY_USERNAME": self.config.ezproxy_username,
            }
            if self.config.ezproxy_institution:
                env_vars["SCITEX_SCHOLAR_EZPROXY_INSTITUTION"] = (
                    self.config.ezproxy_institution
                )

            print("\nAdd these to your environment:")
            for key, value in env_vars.items():
                if value:
                    print(f'export {key}="{value}"')

        # Reinitialize PDF downloader with EZProxy
        self._initialize_pdf_downloader()

        logger.info(f"EZProxy configured for {self.config.ezproxy_url}")

    async def authenticate_ezproxy_async(self, force: bool = False) -> bool:
        """
        Authenticate with EZProxy (async).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        if not self.config.ezproxy_enabled:
            raise ScholarError(
                "EZProxy not configured. Call configure_ezproxy() first."
            )

        if not self._pdf_downloader.ezproxy_authenticator:
            raise ScholarError("EZProxy authenticator not initialized")

        result = await self._pdf_downloader.ezproxy_authenticator.authenticate(
            force=force
        )
        return bool(result)

    def authenticate_ezproxy(self, force: bool = False) -> bool:
        """
        Authenticate with EZProxy (sync).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        return self._run_async(self.authenticate_ezproxy_async(force))

    async def is_ezproxy_authenticated_async(self) -> bool:
        """
        Check if EZProxy is authenticated (async).

        Returns:
            True if authenticated and session is valid
        """
        if not self._pdf_downloader.ezproxy_authenticator:
            return False
        return (
            await self._pdf_downloader.ezproxy_authenticator.is_authenticated()
        )

    def is_ezproxy_authenticated(self) -> bool:
        """
        Check if EZProxy is authenticated (sync).

        Returns:
            True if authenticated and session is valid
        """
        return self._run_async(self.is_ezproxy_authenticated_async())

    def configure_shibboleth(
        self,
        institution: Optional[str] = None,
        idp_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> None:
        """
        Configure Shibboleth authentication.

        Args:
            institution: Institution name (e.g., 'University of Example')
            idp_url: Identity Provider URL
            username: Username for authentication
            password: Password for authentication
            entity_id: Entity ID for the institution
        """
        # Update config with provided values
        if institution:
            self.config.shibboleth_institution = institution
        if idp_url:
            self.config.shibboleth_idp_url = idp_url
        if username:
            self.config.shibboleth_username = username
        if password:
            self.config.shibboleth_password = password
        if entity_id:
            self.config.shibboleth_entity_id = entity_id

        # Enable Shibboleth
        self.config.shibboleth_enabled = True

        # Reinitialize downloader with new config
        self._initialize_pdf_downloader()

        # Initialize Shibboleth in downloader
        if hasattr(self._pdf_downloader, "_init_shibboleth"):
            self._pdf_downloader._init_shibboleth()

    async def authenticate_shibboleth_async(self, force: bool = False) -> bool:
        """
        Authenticate with Shibboleth (async).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        if not self._pdf_downloader.shibboleth_authenticator:
            # Initialize Shibboleth if not already done
            if hasattr(self._pdf_downloader, "_init_shibboleth"):
                self._pdf_downloader._init_shibboleth()

        if not self._pdf_downloader.shibboleth_authenticator:
            raise ValueError(
                "Shibboleth not configured. Call configure_shibboleth() first."
            )

        result = (
            await self._pdf_downloader.shibboleth_authenticator.authenticate(
                force=force
            )
        )
        return bool(result.get("cookies"))

    def authenticate_shibboleth(self, force: bool = False) -> bool:
        """
        Authenticate with Shibboleth (sync).

        Args:
            force: Force re-authentication even if session exists

        Returns:
            True if authentication successful
        """
        return self._run_async(self.authenticate_shibboleth_async(force))

    async def is_shibboleth_authenticated_async(self) -> bool:
        """
        Check if Shibboleth is authenticated (async).

        Returns:
            True if authenticated and session is valid
        """
        if not self._pdf_downloader.shibboleth_authenticator:
            return False
        return (
            await self._pdf_downloader.shibboleth_authenticator.is_authenticated()
        )

    def is_shibboleth_authenticated(self) -> bool:
        """
        Check if Shibboleth is authenticated (sync).

        Returns:
            True if authenticated and session is valid
        """
        return self._run_async(self.is_shibboleth_authenticated_async())

    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            # Check if we're already in an async context
            loop = asyncio.get_running_loop()
            # We're in an async context, create a task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(coro)

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    # Async context manager support
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# Convenience functions for quick use
def search(query: str, **kwargs) -> Papers:
    """Quick search without creating Scholar instance."""
    scholar = Scholar()
    return scholar.search(query, **kwargs)


def search_quick(query: str, top_n: int = 5) -> List[str]:
    """Quick search returning just titles."""
    scholar = Scholar()
    return scholar.search_quick(query, top_n)


def enrich_bibtex(
    bibtex_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> Papers:
    """
    Quick function to enrich a BibTeX file with impact factors and citations.

    This is the easiest way to enrich your bibliography with:
    - Journal impact factors (2024 JCR data)
    - Citation counts from CrossRef and Semantic Scholar
    - Missing DOIs

    Args:
        bibtex_path: Path to BibTeX file to enrich
        output_path: Optional output path (defaults to overwriting input with backup)

    Returns:
        Papers collection with enriched data

    Example:
        >>> from scitex.scholar import enrich_bibtex
        >>> enrich_bibtex("my_papers.bib")
        >>> # Or save to new file:
        >>> enrich_bibtex("my_papers.bib", "my_papers_enriched.bib")
    """
    scholar = Scholar()
    return scholar.enrich_bibtex(bibtex_path, output_path)


# Export main class and convenience functions
__all__ = ["Scholar", "search", "search_quick", "enrich_bibtex"]

# EOF
