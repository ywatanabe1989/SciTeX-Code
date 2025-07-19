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

logger = logging.getLogger(__name__)


class Scholar:
    """
    Main interface for SciTeX Scholar - scientific literature management made simple.
    
    Example usage:
        # Basic search
        scholar = Scholar()
        papers = scholar.search("deep learning neuroscience")
        papers.save("my_papers.bib")
        
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
        # Auto-detect configuration
        self.email = email or os.getenv('SCHOLAR_EMAIL') or os.getenv('ENTREZ_EMAIL')
        if not self.email:
            logger.info("No email provided. Some sources may have limited functionality.")
        
        # API keys
        self.api_keys = api_keys or {}
        if 's2' not in self.api_keys:
            self.api_keys['s2'] = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        
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
               sources: Optional[List[str]] = None,
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               **kwargs) -> PaperCollection:
        """
        Search for papers across multiple sources.
        
        Args:
            query: Search query
            limit: Maximum results (default 20)
            sources: Sources to search (default: ['semantic_scholar', 'pubmed', 'arxiv'])
            year_min: Minimum publication year
            year_max: Maximum publication year
            **kwargs: Additional search parameters
            
        Returns:
            PaperCollection with results
        """
        # Run async search in sync context
        papers = self._run_async(
            self._searcher.search(
                query=query,
                sources=sources,
                limit=limit,
                year_min=year_min,
                year_max=year_max,
                **kwargs
            )
        )
        
        # Create collection
        collection = PaperCollection(papers)
        
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
    
    def _run_async(self, coro):
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create new one
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