#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 09:30:00 (ywatanabe)"
# File: ./src/scitex/scholar/_scholar.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_scholar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Main Scholar class providing unified interface for scientific literature management.

Features:
  - Unified search across multiple sources (Semantic Scholar, PubMed, etc.)
  - Automatic paper enrichment with impact factors by default
  - PDF downloads and local indexing
  - Simple sync/async API that auto-detects context
  - Progress feedback for long operations
  - Chainable methods for workflow construction
"""

import asyncio
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

from ._paper import Paper
from ._search import search_sync, build_index, get_scholar_dir
from ._pdf_downloader import PDFDownloader


class PaperCollection:
    """Container for paper search results with utility methods."""
    
    def __init__(self, papers: List[Paper]):
        self.papers = papers
        self._enriched = False
    
    def __len__(self) -> int:
        return len(self.papers)
    
    def __iter__(self):
        return iter(self.papers)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return PaperCollection(self.papers[index])
        return self.papers[index]
    
    def filter(self, 
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               min_citations: Optional[int] = None,
               impact_factor_min: Optional[float] = None,
               open_access_only: bool = False) -> 'PaperCollection':
        """Filter papers based on criteria."""
        filtered = []
        for paper in self.papers:
            # Year filter
            if year_min and paper.year and paper.year < year_min:
                continue
            if year_max and paper.year and paper.year > year_max:
                continue
            
            # Citation filter
            if min_citations and paper.citation_count and paper.citation_count < min_citations:
                continue
            
            # Impact factor filter
            if impact_factor_min and hasattr(paper, 'impact_factor') and paper.impact_factor:
                if paper.impact_factor < impact_factor_min:
                    continue
            
            # Open access filter
            if open_access_only and not getattr(paper, 'is_open_access', False):
                continue
            
            filtered.append(paper)
        
        return PaperCollection(filtered)
    
    def sort_by(self, criteria: str = "citations", reverse: bool = True) -> 'PaperCollection':
        """Sort papers by specified criteria."""
        if criteria == "citations":
            key_func = lambda p: p.citation_count or 0
        elif criteria == "year":
            key_func = lambda p: p.year or 0
        elif criteria == "impact_factor":
            key_func = lambda p: getattr(p, 'impact_factor', 0) or 0
        else:
            raise ValueError(f"Unknown sort criteria: {criteria}")
        
        sorted_papers = sorted(self.papers, key=key_func, reverse=reverse)
        return PaperCollection(sorted_papers)
    
    def save_bibliography(self, output_path: Union[str, Path], format: str = "bibtex") -> str:
        """Save papers as bibliography file."""
        output_path = Path(output_path)
        
        if format.lower() == "bibtex":
            bibtex_entries = []
            for paper in self.papers:
                try:
                    bibtex = paper.to_bibtex(include_enriched=self._enriched)
                    bibtex_entries.append(bibtex)
                except Exception as e:
                    warnings.warn(f"Failed to generate BibTeX for paper {paper.title}: {e}")
            
            content = "\n\n".join(bibtex_entries)
            output_path.write_text(content, encoding='utf-8')
            return str(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert papers to list of dictionaries."""
        return [paper.__dict__ for paper in self.papers]


class Scholar:
    """
    Main entry point for SciTeX Scholar - scientific literature management.
    
    This class provides a unified, user-friendly interface for:
    - Searching scientific literature across multiple sources
    - Automatic paper enrichment with journal metrics
    - PDF downloads and local indexing
    - Bibliography generation and management
    
    Example usage:
        # Simple search with default enrichment
        scholar = Scholar()
        papers = scholar.search("deep learning neuroscience", limit=10)
        
        # Save enriched bibliography
        papers.save_bibliography("my_papers.bib")
        
        # Filter and chain operations
        high_impact = scholar.search("neural networks") \\
                           .filter(year_min=2020, min_citations=50) \\
                           .sort_by("impact_factor")
    """
    
    def __init__(self, 
                 email: Optional[str] = None,
                 workspace_dir: Optional[Union[str, Path]] = None,
                 enrich_by_default: bool = True,
                 cache_results: bool = True,
                 api_keys: Optional[Dict[str, str]] = None,
                 progress_callback: Optional[callable] = None):
        """
        Initialize Scholar instance.
        
        Parameters
        ----------
        email : str, optional
            Email for API access (required for some sources like PubMed)
        workspace_dir : str or Path, optional
            Directory for storing downloads, cache, and indices
            Defaults to ~/.scitex/scholar/
        enrich_by_default : bool, default True
            Whether to automatically enrich papers with journal metrics
        cache_results : bool, default True
            Whether to cache search results
        api_keys : dict, optional
            API keys for various services (auto-detected from environment if not provided)
        progress_callback : callable, optional
            Function to call for progress updates during long operations
        """
        self.email = email
        self.enrich_by_default = enrich_by_default
        self.cache_results = cache_results
        self.progress_callback = progress_callback or self._default_progress
        
        # Set up workspace directory
        if workspace_dir:
            self.workspace_dir = Path(workspace_dir)
        else:
            self.workspace_dir = Path(get_scholar_dir())
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._init_components(api_keys)
    
    def _init_components(self, api_keys: Optional[Dict[str, str]]):
        """Initialize internal components."""
        # Initialize search clients
        try:
            from ._semantic_scholar_client import SemanticScholarClient
            self._semantic_scholar = SemanticScholarClient()
        except ImportError:
            self._semantic_scholar = None
            warnings.warn("Semantic Scholar client not available")
        
        # Initialize enrichment service
        if self.enrich_by_default:
            try:
                from ._paper_enrichment import PaperEnrichmentService
                self._enrichment_service = PaperEnrichmentService()
            except ImportError:
                self._enrichment_service = None
                warnings.warn("Paper enrichment service not available")
        else:
            self._enrichment_service = None
        
        # Initialize PDF downloader
        try:
            self._pdf_downloader = PDFDownloader(
                download_dir=self.workspace_dir / "pdfs"
            )
        except Exception:
            self._pdf_downloader = None
            warnings.warn("PDF downloader not available")
        
        # Initialize advanced features if available
        try:
            from ._paper_acquisition import PaperAcquisition
            ai_provider = None
            if api_keys:
                if api_keys.get('OPENAI_API_KEY'):
                    ai_provider = 'openai'
                elif api_keys.get('ANTHROPIC_API_KEY'):
                    ai_provider = 'anthropic'
            
            self._paper_acquisition = PaperAcquisition(
                download_dir=self.workspace_dir / "pdfs",
                email=self.email,
                s2_api_key=api_keys.get('SEMANTIC_SCHOLAR_API_KEY') if api_keys else None,
                ai_provider=ai_provider
            )
        except ImportError:
            self._paper_acquisition = None
        except Exception as e:
            # If PaperAcquisition fails to initialize, continue without it
            self._paper_acquisition = None
            warnings.warn(f"PaperAcquisition initialization failed: {e}")
    
    def _default_progress(self, message: str, progress: float = None):
        """Default progress callback that prints to console."""
        if progress is not None:
            print(f"\r{message} [{progress:.1%}]", end="", flush=True)
        else:
            print(f"{message}")
    
    def _is_async_context(self) -> bool:
        """Check if we're in an async context."""
        try:
            loop = asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
    
    def search(self, 
               query: str, 
               limit: int = 20,
               sources: Union[str, List[str]] = "semantic_scholar",
               start_year: Optional[int] = None,
               end_year: Optional[int] = None,
               enrich: Optional[bool] = None,
               show_progress: bool = True) -> PaperCollection:
        """
        Search for scientific papers with automatic enrichment.
        
        This method automatically detects sync/async context and handles
        enrichment based on default settings.
        
        Parameters
        ----------
        query : str
            Search query (e.g., "deep learning neuroscience")
        limit : int, default 20
            Maximum number of papers to return
        sources : str or list, default "semantic_scholar"
            Sources to search. Options: "semantic_scholar", "pubmed", "all"
        start_year : int, optional
            Earliest publication year to include
        end_year : int, optional
            Latest publication year to include
        enrich : bool, optional
            Whether to enrich papers with journal metrics
            If None, uses the instance default (enrich_by_default)
        show_progress : bool, default True
            Whether to show progress during search and enrichment
        
        Returns
        -------
        PaperCollection
            Collection of papers with utility methods for filtering, sorting, etc.
        """
        # Determine enrichment setting
        should_enrich = enrich if enrich is not None else self.enrich_by_default
        
        if show_progress:
            self.progress_callback(f"Searching for papers: '{query}'")
        
        # Perform search based on context
        if self._is_async_context():
            # We're in async context, but search() should be sync
            # Use asyncio.create_task if needed, but for now keep it simple
            papers = self._search_sync(query, limit, sources, start_year, end_year)
        else:
            papers = self._search_sync(query, limit, sources, start_year, end_year)
        
        if show_progress:
            self.progress_callback(f"Found {len(papers)} papers")
        
        # Convert to Paper objects if needed
        paper_objects = []
        for paper in papers:
            if isinstance(paper, Paper):
                paper_objects.append(paper)
            else:
                # Convert from dict or other format
                paper_obj = Paper.from_dict(paper) if hasattr(Paper, 'from_dict') else Paper(**paper)
                paper_objects.append(paper_obj)
        
        # Create collection
        collection = PaperCollection(paper_objects)
        
        # Enrich if requested
        if should_enrich and self._enrichment_service and paper_objects:
            if show_progress:
                self.progress_callback("Enriching papers with journal metrics")
            
            try:
                enriched_papers = self._enrichment_service.enrich_papers(paper_objects)
                collection = PaperCollection(enriched_papers)
                collection._enriched = True
                
                if show_progress:
                    enriched_count = sum(1 for p in enriched_papers if hasattr(p, 'impact_factor') and p.impact_factor)
                    self.progress_callback(f"Enriched {enriched_count}/{len(enriched_papers)} papers with metrics")
            except Exception as e:
                warnings.warn(f"Enrichment failed: {e}")
        
        if show_progress:
            self.progress_callback("Search complete\n")
        
        return collection
    
    def _search_sync(self, query: str, limit: int, sources, start_year: Optional[int], end_year: Optional[int]) -> List:
        """Synchronous search implementation."""
        if self._semantic_scholar and (sources == "semantic_scholar" or sources == "all"):
            try:
                from ._semantic_scholar_client import search_papers
                # Handle async function in sync context
                import asyncio
                try:
                    # Try to get existing event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, but we need sync behavior
                        # Fall back to local search
                        raise RuntimeError("Cannot run async in async context")
                    else:
                        papers = loop.run_until_complete(search_papers(query, limit=limit))
                except RuntimeError:
                    # No loop or loop is running, try new loop
                    try:
                        papers = asyncio.run(search_papers(query, limit=limit))
                    except RuntimeError:
                        # Fall back to local search
                        raise RuntimeError("Cannot create async loop")
                        
                # Convert S2Paper objects to Paper objects
                converted_papers = []
                for s2_paper in papers:
                    try:
                        paper = Paper(
                            title=s2_paper.title,
                            authors=[author.get('name', '') for author in s2_paper.authors] if s2_paper.authors else [],
                            abstract=s2_paper.abstract or "",
                            year=s2_paper.year,
                            doi=s2_paper.doi,
                            source="semantic_scholar"
                        )
                        paper.citation_count = s2_paper.citationCount
                        paper.venue = s2_paper.venue
                        converted_papers.append(paper)
                    except Exception as e:
                        warnings.warn(f"Failed to convert paper: {e}")
                        continue
                
                return converted_papers
            except Exception as e:
                warnings.warn(f"Semantic Scholar search failed: {e}")
        
        # Fallback to local search
        try:
            papers = search_sync(query, limit=limit)
            return papers if papers else []
        except Exception as e:
            warnings.warn(f"Local search failed: {e}")
            return []
    
    async def search_async(self, 
                          query: str, 
                          limit: int = 20,
                          sources: Union[str, List[str]] = "semantic_scholar",
                          **kwargs) -> PaperCollection:
        """
        Asynchronous version of search for advanced users.
        
        Useful for bulk operations or when integrating with async code.
        """
        if self._paper_acquisition:
            papers = await self._paper_acquisition.search(
                query=query,
                max_results=limit,
                sources=sources if isinstance(sources, list) else [sources],
                **kwargs
            )
            return PaperCollection(papers)
        else:
            # Fallback to sync search
            papers = self._search_sync(query, limit, sources, kwargs.get('start_year'), kwargs.get('end_year'))
            return PaperCollection(papers)
    
    def search_multiple(self, 
                       queries: List[str], 
                       papers_per_query: int = 10,
                       combine_results: bool = True,
                       **kwargs) -> Union[PaperCollection, List[PaperCollection]]:
        """
        Search multiple queries efficiently.
        
        Parameters
        ----------
        queries : list of str
            List of search queries
        papers_per_query : int, default 10
            Maximum papers per query
        combine_results : bool, default True
            Whether to combine all results into one collection
        **kwargs
            Additional arguments passed to search()
        
        Returns
        -------
        PaperCollection or list of PaperCollection
            Combined results or list of individual results
        """
        results = []
        total_queries = len(queries)
        
        for i, query in enumerate(queries):
            self.progress_callback(f"Searching query {i+1}/{total_queries}: '{query}'")
            
            try:
                papers = self.search(query, limit=papers_per_query, show_progress=False, **kwargs)
                results.append(papers)
            except Exception as e:
                warnings.warn(f"Search failed for query '{query}': {e}")
                results.append(PaperCollection([]))
        
        if combine_results:
            all_papers = []
            for collection in results:
                all_papers.extend(collection.papers)
            
            # Remove duplicates based on DOI or title
            unique_papers = []
            seen_dois = set()
            seen_titles = set()
            
            for paper in all_papers:
                # Check DOI first
                if hasattr(paper, 'doi') and paper.doi:
                    if paper.doi in seen_dois:
                        continue
                    seen_dois.add(paper.doi)
                # Fallback to title
                elif hasattr(paper, 'title') and paper.title:
                    title_normalized = paper.title.lower().strip()
                    if title_normalized in seen_titles:
                        continue
                    seen_titles.add(title_normalized)
                
                unique_papers.append(paper)
            
            combined = PaperCollection(unique_papers)
            # Mark as enriched if any individual collection was enriched
            combined._enriched = any(getattr(r, '_enriched', False) for r in results)
            
            self.progress_callback(f"Combined {len(all_papers)} papers into {len(unique_papers)} unique papers")
            return combined
        
        return results
    
    def download_pdfs(self, 
                     papers: Union[PaperCollection, List[Paper]], 
                     output_dir: Optional[Union[str, Path]] = None,
                     max_downloads: int = 10) -> Dict[str, Path]:
        """
        Download PDFs for papers.
        
        Parameters
        ----------
        papers : PaperCollection or list of Paper
            Papers to download PDFs for
        output_dir : str or Path, optional
            Directory to save PDFs (defaults to workspace/pdfs)
        max_downloads : int, default 10
            Maximum number of PDFs to download
        
        Returns
        -------
        dict
            Mapping of paper titles to downloaded file paths
        """
        if not self._pdf_downloader:
            raise RuntimeError("PDF downloader not available")
        
        if isinstance(papers, PaperCollection):
            paper_list = papers.papers
        else:
            paper_list = papers
        
        if output_dir:
            download_dir = Path(output_dir)
        else:
            download_dir = self.workspace_dir / "pdfs"
        
        download_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded = {}
        count = 0
        
        for paper in paper_list[:max_downloads]:
            if count >= max_downloads:
                break
            
            self.progress_callback(f"Downloading PDF {count+1}/{min(len(paper_list), max_downloads)}: {paper.title[:50]}...")
            
            try:
                # Try to download PDF
                pdf_path = self._pdf_downloader.download_paper_pdf(paper, str(download_dir))
                if pdf_path:
                    downloaded[paper.title] = Path(pdf_path)
                    count += 1
            except Exception as e:
                warnings.warn(f"Failed to download PDF for '{paper.title}': {e}")
        
        self.progress_callback(f"Downloaded {count} PDFs to {download_dir}")
        return downloaded
    
    def build_local_index(self, 
                         pdf_directory: Union[str, Path],
                         rebuild: bool = False) -> str:
        """
        Build searchable index from local PDF collection.
        
        Parameters
        ----------
        pdf_directory : str or Path
            Directory containing PDF files
        rebuild : bool, default False
            Whether to rebuild existing index
        
        Returns
        -------
        str
            Path to created index
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise ValueError(f"PDF directory does not exist: {pdf_dir}")
        
        self.progress_callback(f"Building search index from {pdf_dir}")
        
        try:
            index_path = build_index(str(pdf_dir))
            self.progress_callback(f"Index created: {index_path}")
            return index_path
        except Exception as e:
            raise RuntimeError(f"Failed to build index: {e}")
    
    def search_local(self, 
                    query: str, 
                    limit: int = 10) -> PaperCollection:
        """
        Search local PDF collection.
        
        Parameters
        ----------
        query : str
            Search query
        limit : int, default 10
            Maximum number of results
        
        Returns
        -------
        PaperCollection
            Search results from local collection
        """
        self.progress_callback(f"Searching local collection for: '{query}'")
        
        try:
            papers = search_sync(query, local_only=True, limit=limit)
            collection = PaperCollection(papers if papers else [])
            
            self.progress_callback(f"Found {len(collection)} papers in local collection")
            return collection
        except Exception as e:
            warnings.warn(f"Local search failed: {e}")
            return PaperCollection([])
    
    def analyze_with_ai(self, 
                       papers: Union[PaperCollection, List[Paper]], 
                       topic: Optional[str] = None,
                       analysis_type: str = "summary") -> Dict[str, Any]:
        """
        AI analysis of paper collection.
        
        Parameters
        ----------
        papers : PaperCollection or list of Paper
            Papers to analyze
        topic : str, optional
            Specific topic to focus analysis on
        analysis_type : str, default "summary"
            Type of analysis: "summary", "trends", "gaps"
        
        Returns
        -------
        dict
            Analysis results
        """
        if not self._paper_acquisition or not hasattr(self._paper_acquisition, 'analyze_papers'):
            raise RuntimeError("AI analysis not available. Requires PaperAcquisition with AI support.")
        
        if isinstance(papers, PaperCollection):
            paper_list = papers.papers
        else:
            paper_list = papers
        
        self.progress_callback(f"Running AI analysis on {len(paper_list)} papers")
        
        try:
            # This would need to be implemented in PaperAcquisition
            analysis = {"message": "AI analysis not yet implemented", "papers_analyzed": len(paper_list)}
            return analysis
        except Exception as e:
            warnings.warn(f"AI analysis failed: {e}")
            return {"error": str(e)}
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about the Scholar workspace."""
        info = {
            "workspace_dir": str(self.workspace_dir),
            "enrich_by_default": self.enrich_by_default,
            "components": {
                "semantic_scholar": self._semantic_scholar is not None,
                "enrichment_service": self._enrichment_service is not None,
                "pdf_downloader": self._pdf_downloader is not None,
                "paper_acquisition": self._paper_acquisition is not None,
            }
        }
        
        # Add directory stats
        if self.workspace_dir.exists():
            pdf_dir = self.workspace_dir / "pdfs"
            info["pdf_count"] = len(list(pdf_dir.glob("*.pdf"))) if pdf_dir.exists() else 0
        
        return info


# Convenience functions for backward compatibility and quick usage
def search_papers_simple(query: str, limit: int = 20, enrich: bool = True) -> PaperCollection:
    """
    Quick search function for simple use cases.
    
    Parameters
    ----------
    query : str
        Search query
    limit : int, default 20
        Maximum number of papers
    enrich : bool, default True
        Whether to enrich with journal metrics
    
    Returns
    -------
    PaperCollection
        Search results
    """
    scholar = Scholar(enrich_by_default=enrich)
    return scholar.search(query, limit=limit)


# EOF