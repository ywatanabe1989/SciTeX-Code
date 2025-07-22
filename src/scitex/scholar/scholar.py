#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 13:58:32 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/scholar.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/scholar.py"
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
import logging
import re
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# PDF extraction is now handled by scitex.io
from ..errors import ConfigurationError, SciTeXWarning
from ._core import Paper, PaperCollection
from ._download import PDFManager
from ._search import UnifiedSearcher, get_scholar_dir
from .enrichment import UnifiedEnricher
from ..io import load

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
        scholar = Scholar(impact_factors=False, citations=False)

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
        email_pubmed: Optional[str] = None,
        email_crossref: Optional[str] = None,
        api_key_semantic_scholar: Optional[str] = None,
        api_key_crossref: Optional[str] = None,
        workspace_dir: Optional[Union[str, Path]] = None,
        impact_factors: bool = True,
        citations: bool = True,
        auto_download: bool = False,
    ):
        """
        Initialize Scholar with smart defaults.

        Args:
            email_pubmed: Email for PubMed API. If None, uses os.getenv("SCITEX_PUBMED_EMAIL")
            email_crossref: Email for CrossRef API. If None, uses os.getenv("SCITEX_CROSSREF_EMAIL")
            api_key_semantic_scholar: Semantic Scholar API key. If None, uses os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY")
            api_key_crossref: CrossRef API key for higher rate limits (optional). If None, uses os.getenv("SCITEX_CROSSREF_API_KEY")
            workspace_dir: Directory for downloads and indices (default: ~/.scitex/scholar)
            impact_factors: Automatically add journal impact factors from impact_factor package
                          (2024 JCR data). Install with: pip install impact-factor (default: True)
            citations: Automatically add citation counts from CrossRef (primary) and Semantic Scholar (fallback).
                      CrossRef works without key but has higher rate limits with one. (default: True)
            auto_download: Automatically download open-access PDFs (default: False)
        """
        # PubMed email configuration
        self._email_pubmed = email_pubmed or os.getenv("SCITEX_PUBMED_EMAIL")
        
        # CrossRef email configuration
        self._email_crossref = email_crossref or os.getenv("SCITEX_CROSSREF_EMAIL")

        # API key for Semantic Scholar
        self._api_key_semantic_scholar = api_key_semantic_scholar or os.getenv(
            "SCITEX_SEMANTIC_SCHOLAR_API_KEY"
        )
        
        # API key for CrossRef (optional - for higher rate limits)
        self._api_key_crossref = api_key_crossref or os.getenv(
            "SCITEX_CROSSREF_API_KEY"
        )
        
        if citations and not self._api_key_semantic_scholar:
            warnings.warn(
                "SCITEX_SEMANTIC_SCHOLAR_API_KEY not found. "
                "Citation counts will use CrossRef (works without key). "
                "For additional citation sources, get a free API key at: "
                "https://www.semanticscholar.org/product/api",
                SciTeXWarning,
                stacklevel=2,
            )

        # Workspace
        self.workspace_dir = (
            Path(workspace_dir) if workspace_dir else get_scholar_dir()
        )
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Options
        self._flag_impact_factors = impact_factors
        self._flag_citations = citations
        self._flag_auto_download = auto_download

        # Initialize components
        self._searcher = UnifiedSearcher(
            email=self._email_pubmed,
            semantic_scholar_api_key=self._api_key_semantic_scholar,
        )

        self._enricher = UnifiedEnricher(
            semantic_scholar_api_key=self._api_key_semantic_scholar,
            crossref_api_key=self._api_key_crossref,
            email=self._email_crossref,
            use_impact_factor_package=True,
        )

        self._pdf_manager = PDFManager(self.workspace_dir)

        logger.info(f"Scholar initialized (workspace: {self.workspace_dir})")

    def search(
        self,
        query: str,
        limit: int = 100,
        sources: Union[str, List[str]] = "pubmed",
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs,
    ) -> PaperCollection:
        """
        Search for papers from one or more sources.

        Args:
            query: Search query
            limit: Maximum results (default 100)
            sources: Source(s) to search - can be a string or list of strings
                    ('pubmed', 'semantic_scholar', 'arxiv')
            year_min: Minimum publication year
            year_max: Maximum publication year
            search_mode: Search mode - 'strict' (all terms required) or 'flexible' (any terms)
            **kwargs: Additional search parameters

        Returns:
            PaperCollection with results
        """
        # Ensure sources is a list
        if isinstance(sources, str):
            sources = [sources]

        # Run async search in sync context
        coro = self._searcher.search(
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
        collection = PaperCollection(papers, source_priority=sources)

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
        if (self._flag_impact_factors or self._flag_citations) and papers:
            logger.info("Auto-enriching papers...")
            self._enricher.enrich_all(
                papers,
                enrich_impact_factors=self._flag_impact_factors,
                enrich_citations=self._flag_citations,
                enrich_journal_metrics=self._flag_impact_factors,
            )
            collection._enriched = True

        # Auto-download if enabled
        if self._flag_auto_download and papers:
            open_access = [p for p in papers if p.pdf_url]
            if open_access:
                logger.info(
                    f"Auto-downloading {len(open_access)} open-access PDFs..."
                )
                self._run_async(
                    self._pdf_manager.download_and_index(open_access)
                )

        return collection

    def search_local(self, query: str, limit: int = 20) -> PaperCollection:
        """
        Search local PDF library.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            PaperCollection with local results
        """
        papers = self._pdf_manager.search_library(query, limit)
        return PaperCollection(papers)

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
        return self._pdf_manager.indexer.index_directory(directory, recursive)

    def download_pdfs(
        self, papers: Union[List[Paper], PaperCollection], force: bool = False
    ) -> Dict[str, Path]:
        """
        Download PDFs for papers.

        Args:
            papers: Papers to download
            force: Force re-download

        Returns:
            Dictionary mapping paper IDs to downloaded paths
        """
        if isinstance(papers, PaperCollection):
            papers = papers.papers

        result = self._run_async(
            self._pdf_manager.download_and_index(papers, force)
        )

        return result

    def _enrich_papers(
        self,
        papers: Union[List[Paper], PaperCollection],
        impact_factors: bool = True,
        citations: bool = True,
        journal_metrics: bool = True,
    ) -> Union[List[Paper], PaperCollection]:
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
        if isinstance(papers, PaperCollection):
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

    def enhance_bibtex(
        self,
        bibtex_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        backup: bool = True,
        preserve_original_fields: bool = True,
        add_missing_abstracts: bool = True,
        add_missing_urls: bool = True,
    ) -> PaperCollection:
        """
        Enhance an existing BibTeX file with impact factors, citations, and missing fields.
        
        Args:
            bibtex_path: Path to input BibTeX file
            output_path: Path for enhanced output (defaults to input path)
            backup: Create backup of original file before overwriting
            preserve_original_fields: Keep all original BibTeX fields
            add_missing_abstracts: Fetch abstracts for entries without them
            add_missing_urls: Fetch URLs for entries without them
        
        Returns:
            PaperCollection with enhanced papers
        """
        bibtex_path = Path(bibtex_path)
        if not bibtex_path.exists():
            raise FileNotFoundError(f"BibTeX file not found: {bibtex_path}")
        
        # Set output path
        if output_path is None:
            output_path = bibtex_path
        else:
            output_path = Path(output_path)
        
        # Create backup if needed
        if backup and output_path == bibtex_path:
            backup_path = bibtex_path.with_suffix('.bib.bak')
            import shutil
            shutil.copy2(bibtex_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Load existing BibTeX entries
        logger.info(f"Loading BibTeX file: {bibtex_path}")
        entries = load(str(bibtex_path))
        
        # Convert BibTeX entries to Paper objects
        papers = []
        original_fields_map = {}
        
        for entry in entries:
            paper = self._bibtex_entry_to_paper(entry)
            if paper:
                papers.append(paper)
                # Store original fields for preservation
                if preserve_original_fields:
                    original_fields_map[paper.get_identifier()] = entry['fields']
        
        logger.info(f"Parsed {len(papers)} papers from BibTeX file")
        
        # Create collection
        collection = PaperCollection(papers)
        
        # Enrich papers with impact factors and citations
        if papers:
            logger.info("Enriching papers with impact factors and citations...")
            self._enricher.enrich_all(
                papers,
                enrich_impact_factors=self._flag_impact_factors,
                enrich_citations=self._flag_citations,
                enrich_journal_metrics=self._flag_impact_factors,
            )
            
            # Fetch missing abstracts and URLs if requested
            if add_missing_abstracts or add_missing_urls:
                logger.info("Fetching missing information from online sources...")
                self._fetch_missing_fields(papers, add_missing_abstracts, add_missing_urls)
        
        # Merge original fields if preserving
        if preserve_original_fields:
            for paper in papers:
                paper_id = paper.get_identifier()
                if paper_id in original_fields_map:
                    paper._original_bibtex_fields = original_fields_map[paper_id]
        
        # Save enhanced BibTeX
        collection.save(str(output_path))
        logger.info(f"Saved enhanced BibTeX to: {output_path}")
        
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
            fields = entry.get('fields', {})
            
            # Extract authors
            authors_str = fields.get('author', '')
            authors = self._parse_bibtex_authors(authors_str)
            
            # Create Paper object with available fields
            paper = Paper(
                title=fields.get('title', '').strip(),
                authors=authors,
                year=int(fields.get('year', 0)) if fields.get('year', '').isdigit() else None,
                journal=fields.get('journal', fields.get('booktitle', '')),
                doi=fields.get('doi', ''),
                pmid=fields.get('pmid', ''),
                arxiv_id=fields.get('arxiv', ''),
                abstract=fields.get('abstract', ''),
                pdf_url=fields.get('url', ''),
                keywords=self._parse_bibtex_keywords(fields.get('keywords', '')),
                source=f"bibtex:{entry.get('key', 'unknown')}",
            )
            
            # Add volume, pages if available
            if 'volume' in fields:
                paper.volume = fields['volume']
            if 'pages' in fields:
                paper.pages = fields['pages']
            
            # Store entry type and key
            paper._bibtex_entry_type = entry.get('entry_type', 'article')
            paper._bibtex_key = entry.get('key', '')
            
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
        for author in authors_str.split(' and '):
            author = author.strip()
            if author:
                # Handle "Last, First" format
                if ',' in author:
                    parts = author.split(',', 1)
                    author = f"{parts[1].strip()} {parts[0].strip()}"
                authors.append(author)
        
        return authors
    
    def _parse_bibtex_keywords(self, keywords_str: str) -> List[str]:
        """Parse BibTeX keywords string into list."""
        if not keywords_str:
            return []
        
        # Split by comma or semicolon
        keywords = []
        for kw in re.split(r'[,;]', keywords_str):
            kw = kw.strip()
            if kw:
                keywords.append(kw)
        
        return keywords
    
    def _fetch_missing_fields(
        self, 
        papers: List[Paper], 
        fetch_abstracts: bool, 
        fetch_urls: bool
    ):
        """
        Fetch missing abstracts and URLs from online sources.
        
        Args:
            papers: List of Paper objects
            fetch_abstracts: Whether to fetch missing abstracts
            fetch_urls: Whether to fetch missing URLs
        """
        papers_to_update = []
        
        for paper in papers:
            needs_update = False
            
            if fetch_abstracts and not paper.abstract:
                needs_update = True
            if fetch_urls and not paper.pdf_url:
                needs_update = True
            
            if needs_update:
                papers_to_update.append(paper)
        
        if not papers_to_update:
            return
        
        logger.info(f"Fetching missing fields for {len(papers_to_update)} papers...")
        
        # Try to find papers with missing fields
        for paper in papers_to_update:
            # Build search query from title and first author
            query_parts = [paper.title]
            if paper.authors:
                # Add first author's last name
                first_author = paper.authors[0]
                last_name = first_author.split()[-1] if first_author else ""
                if last_name:
                    query_parts.append(last_name)
            
            query = " ".join(query_parts)
            
            # Search for the paper
            try:
                results = self.search(
                    query, 
                    limit=3,
                    sources=['semantic_scholar', 'pubmed'],
                    year_min=paper.year - 1 if paper.year else None,
                    year_max=paper.year + 1 if paper.year else None,
                )
                
                # Find best match by title similarity
                best_match = None
                best_score = 0
                
                for result in results:
                    score = result.similarity_score(paper)
                    if score > best_score and score > 0.8:  # 80% similarity threshold
                        best_score = score
                        best_match = result
                
                if best_match:
                    # Update missing fields
                    if fetch_abstracts and not paper.abstract and best_match.abstract:
                        paper.abstract = best_match.abstract
                        logger.debug(f"Added abstract for: {paper.title[:50]}...")
                    
                    if fetch_urls and not paper.pdf_url and best_match.pdf_url:
                        paper.pdf_url = best_match.pdf_url
                        logger.debug(f"Added URL for: {paper.title[:50]}...")
                    
                    # Also update DOI if missing
                    if not paper.doi and best_match.doi:
                        paper.doi = best_match.doi
                        
            except Exception as e:
                logger.debug(f"Could not fetch missing fields for '{paper.title[:50]}...': {e}")

    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about local PDF library."""
        return self._pdf_manager.get_library_stats()

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

    def find_similar(
        self, paper_title: str, limit: int = 10
    ) -> PaperCollection:
        """
        Find papers similar to a given paper.

        Args:
            paper_title: Title of reference paper
            limit: Number of similar papers

        Returns:
            PaperCollection with similar papers
        """
        # First find the paper
        reference = self.search(paper_title, limit=1)
        if not reference:
            logger.warning(f"Could not find paper: {paper_title}")
            return PaperCollection([])

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

        return PaperCollection(similar_papers[:limit])

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
        self, papers: Union[List[Paper], PaperCollection]
    ) -> List[Dict[str, Any]]:
        """
        Extract text from multiple papers for AI processing.

        Args:
            papers: Papers to extract text from

        Returns:
            List of extraction results with paper metadata
        """
        if isinstance(papers, PaperCollection):
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

    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        # Simplified approach - always create new event loop
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
def search(query: str, **kwargs) -> PaperCollection:
    """Quick search without creating Scholar instance."""
    scholar = Scholar()
    return scholar.search(query, **kwargs)


def search_quick(query: str, top_n: int = 5) -> List[str]:
    """Quick search returning just titles."""
    scholar = Scholar()
    return scholar.search_quick(query, top_n)


# Export main class and convenience functions
__all__ = ["Scholar", "search", "search_quick"]

# EOF
