#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:20:00 (ywatanabe)"
# File: ./src/scitex/scholar/scholar.py
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
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import os
from datetime import datetime

from ._core import Paper, PaperCollection, PaperEnricher
from ._search import UnifiedSearcher, get_scholar_dir
from ._download import PDFManager
# PDF extraction is now handled by scitex.io
from ..errors import ConfigurationError, SciTeXWarning
import warnings

logger = logging.getLogger(__name__)


class Scholar:
    """
    Main interface for SciTeX Scholar - scientific literature management made simple.
    
    Example usage:
        # Basic search (uses PubMed by default)
        scholar = Scholar()
        papers = scholar.search("deep learning neuroscience")
        papers.save("my_papers.bib")
        
        # Search specific source
        papers = scholar.search("transformer models", source='arxiv')
        
        # Advanced workflow
        papers = scholar.search("transformer models", year_min=2020) \\
                      .filter(min_citations=50) \\
                      .enrich() \\
                      .download_pdfs() \\
                      .save("transformers.bib")
        
        # Local library
        scholar.index_local_pdfs("./my_papers")
        local_papers = scholar.search_local("attention mechanism")
    """
    
    def __init__(self,
                 email: Optional[str] = None,
                 api_keys: Optional[Dict[str, str]] = None,
                 workspace_dir: Optional[Union[str, Path]] = None,
                 auto_enrich: bool = True,
                 auto_download: bool = False):
        """
        Initialize Scholar with smart defaults.
        
        Args:
            email: Email for API compliance (auto-detected from env)
            api_keys: API keys dict {'s2': 'key'} (auto-detected from env)
            workspace_dir: Directory for downloads and indices
            auto_enrich: Automatically enrich papers with journal metrics
            auto_download: Automatically download open-access PDFs
        """
        # Auto-detect configuration with SCITEX_ prefix
        self.email = email or os.getenv('SCITEX_ENTREZ_EMAIL') or 'ywata1989@gmail.com'
        
        # API keys
        self.api_keys = api_keys or {}
        if 's2' not in self.api_keys:
            self.api_keys['s2'] = os.getenv('SCITEX_SEMANTIC_SCHOLAR_API_KEY')
            if not self.api_keys['s2']:
                warnings.warn(
                    "SCITEX_SEMANTIC_SCHOLAR_API_KEY not found. "
                    "Semantic Scholar searches may be rate-limited. "
                    "Get a free API key at: https://www.semanticscholar.org/product/api",
                    SciTeXWarning,
                    stacklevel=2
                )
        
        # Workspace
        self.workspace_dir = Path(workspace_dir) if workspace_dir else get_scholar_dir()
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Options
        self.auto_enrich = auto_enrich
        self.auto_download = auto_download
        
        # Initialize components
        self._searcher = UnifiedSearcher(
            email=self.email,
            s2_api_key=self.api_keys.get('s2')
        )
        
        self._enricher = PaperEnricher()
        
        self._pdf_manager = PDFManager(self.workspace_dir)
        
        logger.info(f"Scholar initialized (workspace: {self.workspace_dir})")
    
    def search(self,
               query: str,
               limit: int = 20,
               source: str = 'pubmed',
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               **kwargs) -> PaperCollection:
        """
        Search for papers from a specific source.
        
        Args:
            query: Search query
            limit: Maximum results (default 20)
            source: Source to search ('pubmed', 'semantic_scholar', or 'arxiv')
            year_min: Minimum publication year
            year_max: Maximum publication year
            **kwargs: Additional search parameters
            
        Returns:
            PaperCollection with results
        """
        # Run async search in sync context
        coro = self._searcher.search(
            query=query,
            sources=[source],
            limit=limit,
            year_min=year_min,
            year_max=year_max,
            **kwargs
        )
        logger.debug(f"Searching with source: {source}")
        papers = self._run_async(coro)
        logger.debug(f"Search returned {len(papers)} papers")
        
        # Create collection
        collection = PaperCollection(papers)
        
        # Log search results
        if not papers:
            logger.info(f"No results found for query: '{query}'")
            # Suggest alternative sources if default sources were used
            if sources is None or 'semantic_scholar' in sources:
                logger.info("Try searching with different sources or check your internet connection")
        else:
            logger.info(f"Found {len(papers)} papers for query: '{query}'")
        
        # Auto-enrich if enabled
        if self.auto_enrich and papers:
            logger.info("Auto-enriching papers with journal metrics...")
            self._enricher.enrich_papers(papers)
            collection._enriched = True
        
        # Auto-download if enabled
        if self.auto_download and papers:
            open_access = [p for p in papers if p.pdf_url]
            if open_access:
                logger.info(f"Auto-downloading {len(open_access)} open-access PDFs...")
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
    
    def index_local_pdfs(self, 
                        directory: Union[str, Path],
                        recursive: bool = True) -> Dict[str, Any]:
        """
        Index local PDF files for searching.
        
        Args:
            directory: Directory containing PDFs
            recursive: Search subdirectories
            
        Returns:
            Indexing statistics
        """
        return self._pdf_manager.indexer.index_directory(directory, recursive)
    
    def download_pdfs(self, 
                     papers: Union[List[Paper], PaperCollection],
                     force: bool = False) -> Dict[str, Path]:
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
    
    def enrich_papers(self, 
                     papers: Union[List[Paper], PaperCollection]) -> Union[List[Paper], PaperCollection]:
        """
        Enrich papers with journal metrics.
        
        Args:
            papers: Papers to enrich
            
        Returns:
            Enriched papers (same type as input)
        """
        if isinstance(papers, PaperCollection):
            self._enricher.enrich_papers(papers.papers)
            papers._enriched = True
            return papers
        else:
            return self._enricher.enrich_papers(papers)
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics about local PDF library."""
        return self._pdf_manager.get_library_stats()
    
    def quick_search(self, query: str, top_n: int = 5) -> List[str]:
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
    
    def find_similar(self, paper_title: str, limit: int = 10) -> PaperCollection:
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
        
        query = ' '.join(query_parts)
        
        # Search and filter out the reference paper
        similar = self.search(query, limit=limit + 1)
        similar_papers = [p for p in similar.papers if p.get_identifier() != ref_paper.get_identifier()]
        
        return PaperCollection(similar_papers[:limit])
    
    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from PDF file for downstream AI processing.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        # Use scitex.io for PDF text extraction
        from ..io import load
        return load(str(pdf_path), mode='text')
    
    def extract_sections(self, pdf_path: Union[str, Path]) -> Dict[str, str]:
        """
        Extract text organized by sections.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary mapping section names to text
        """
        # Use scitex.io for section extraction
        from ..io import load
        return load(str(pdf_path), mode='sections')
    
    def extract_for_ai(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
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
        return load(str(pdf_path), mode='full')
    
    def extract_from_papers(self, papers: Union[List[Paper], PaperCollection]) -> List[Dict[str, Any]]:
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
                extraction = self.extract_for_ai(paper.pdf_path)
                extraction['paper'] = {
                    'title': paper.title,
                    'authors': paper.authors,
                    'year': paper.year,
                    'doi': paper.doi,
                    'journal': paper.journal
                }
                results.append(extraction)
            else:
                # Include paper even without PDF
                results.append({
                    'paper': {
                        'title': paper.title,
                        'authors': paper.authors,
                        'year': paper.year,
                        'doi': paper.doi,
                        'journal': paper.journal
                    },
                    'full_text': paper.abstract or '',
                    'error': 'No PDF available'
                })
        
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


def quick_search(query: str, top_n: int = 5) -> List[str]:
    """Quick search returning just titles."""
    scholar = Scholar()
    return scholar.quick_search(query, top_n)


# Export main class and convenience functions
__all__ = ['Scholar', 'search', 'quick_search']