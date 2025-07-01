#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:25:00"
# Author: Claude
# Filename: _search.py

"""
Unified search interface for SciTeX Scholar.
"""

import os
import asyncio
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Tuple
import logging

from ._paper import Paper
from ._vector_search import VectorSearchEngine
from ._web_sources import search_all_sources
from ._local_search import LocalSearchEngine
from ._pdf_downloader import PDFDownloader


logger = logging.getLogger(__name__)


def get_scholar_dir() -> Path:
    """Get the SciTeX Scholar directory from environment or default."""
    scholar_dir = os.environ.get('SciTeX_SCHOLAR_DIR', '~/.scitex/scholar')
    path = Path(scholar_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


async def search(
    query: str,
    web: bool = True,
    local: Optional[List[Union[str, Path]]] = None,
    max_results: int = 20,
    download_pdfs: bool = False,
    use_vector_search: bool = True,
    web_sources: Optional[List[str]] = None,
) -> List[Paper]:
    """Search for scientific papers from web and local sources.
    
    Parameters
    ----------
    query : str
        Search query
    web : bool
        Whether to search web sources (PubMed, arXiv, etc.)
    local : List[str or Path], optional
        Local directories to search. If None or empty list, no local search.
        If provided, searches these specific paths.
    max_results : int
        Maximum number of results to return
    download_pdfs : bool
        Whether to download PDFs for web results
    use_vector_search : bool
        Whether to use vector similarity search
    web_sources : List[str], optional
        Web sources to search (default: all available)
    
    Returns
    -------
    List[Paper]
        List of papers matching the query
    
    Examples
    --------
    >>> import asyncio
    >>> import scitex.scholar
    >>> 
    >>> # Search web only (no local)
    >>> papers = asyncio.run(scitex.scholar.search("deep learning"))
    >>> 
    >>> # Search specific local directories
    >>> papers = asyncio.run(scitex.scholar.search(
    ...     "neural networks",
    ...     web=False,
    ...     local=["./papers", "~/Documents/papers"]
    ... ))
    >>> 
    >>> # Search both web and local
    >>> papers = asyncio.run(scitex.scholar.search(
    ...     "transformer architecture",
    ...     local=["./my_papers"],
    ...     download_pdfs=True
    ... ))
    """
    all_papers = []
    scholar_dir = get_scholar_dir()
    
    # Search web sources
    if web:
        web_papers = await _search_web_sources(
            query, 
            max_results_per_source=max(5, max_results // 3),
            sources=web_sources
        )
        all_papers.extend(web_papers)
        logger.info(f"Found {len(web_papers)} papers from web sources")
    
    # Search local sources if paths provided
    if local:
        local_paths = [Path(p).expanduser() for p in local]
        local_papers = await _search_local_sources(
            query, 
            local_paths, 
            max_results=max_results
        )
        all_papers.extend(local_papers)
        logger.info(f"Found {len(local_papers)} papers from local sources")
    
    # Remove duplicates based on title similarity
    papers = _deduplicate_papers(all_papers)
    
    # Apply vector search if enabled
    if use_vector_search and papers:
        papers = await _apply_vector_search(query, papers, max_results, scholar_dir)
    else:
        # Simple relevance sorting
        papers = papers[:max_results]
    
    # Download PDFs if requested
    if download_pdfs and web:
        await _download_pdfs(papers, scholar_dir / "pdfs")
    
    return papers


async def _search_web_sources(
    query: str, 
    max_results_per_source: int,
    sources: Optional[List[str]] = None
) -> List[Paper]:
    """Search web sources for papers."""
    try:
        results = await search_all_sources(
            query, 
            max_results_per_source=max_results_per_source,
            sources=sources
        )
        
        papers = []
        for source, source_papers in results.items():
            papers.extend(source_papers)
        
        return papers
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        return []


async def _search_local_sources(
    query: str,
    paths: List[Path],
    max_results: int
) -> List[Paper]:
    """Search local sources for papers."""
    try:
        scholar_dir = get_scholar_dir()
        local_engine = LocalSearchEngine(
            index_path=scholar_dir / "local_index.json",
            cache_metadata=True
        )
        
        results = local_engine.search(
            query,
            paths,
            recursive=True,
            max_results=max_results
        )
        
        papers = [paper for paper, score in results]
        return papers
    except Exception as e:
        logger.error(f"Error in local search: {e}")
        return []


async def _apply_vector_search(
    query: str,
    papers: List[Paper],
    max_results: int,
    scholar_dir: Path
) -> List[Paper]:
    """Apply vector similarity search to rank papers."""
    try:
        vector_engine = VectorSearchEngine(
            index_path=scholar_dir / "vector_index.pkl",
            embedding_dim=384,  # Using smaller model by default
            similarity_metric="cosine"
        )
        
        # Add papers to engine if not already indexed
        for paper in papers:
            vector_engine.add_paper(paper, update_embedding=True)
        
        # Search and re-rank
        results = vector_engine.search(query, top_k=max_results)
        
        # Save updated index
        vector_engine.save_index()
        
        return [paper for paper, score in results]
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        # Fallback to original order
        return papers[:max_results]


async def _download_pdfs(papers: List[Paper], download_dir: Path) -> None:
    """Download PDFs for papers that don't have local copies."""
    try:
        downloader = PDFDownloader(download_dir=download_dir)
        
        # Filter papers that need PDFs
        papers_to_download = [
            p for p in papers 
            if not p.has_pdf() and p.source in ["arxiv", "pubmed"]
        ]
        
        if papers_to_download:
            logger.info(f"Downloading PDFs for {len(papers_to_download)} papers...")
            
            def progress_callback(completed, total):
                if completed % 5 == 0 or completed == total:
                    logger.info(f"Downloaded {completed}/{total} PDFs")
            
            await downloader.download_papers(
                papers_to_download,
                progress_callback=progress_callback
            )
    except Exception as e:
        logger.error(f"Error downloading PDFs: {e}")


def _deduplicate_papers(papers: List[Paper]) -> List[Paper]:
    """Remove duplicate papers based on title similarity."""
    if not papers:
        return papers
    
    unique_papers = []
    seen_identifiers = set()
    
    for paper in papers:
        # Check exact identifier match
        identifier = paper.get_identifier()
        if identifier in seen_identifiers:
            continue
        
        # Check title similarity with existing papers
        is_duplicate = False
        for existing in unique_papers:
            if paper.similarity_score(existing) > 0.8:  # 80% similarity threshold
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_papers.append(paper)
            seen_identifiers.add(identifier)
    
    return unique_papers


def build_index(
    paths: Optional[List[Union[str, Path]]] = None,
    recursive: bool = True,
    build_vector_index: bool = True,
) -> Dict[str, Any]:
    """Build search index for local papers.
    
    Parameters
    ----------
    paths : List[str or Path], optional
        Paths to index (default: current directory)
    recursive : bool
        Whether to search directories recursively
    build_vector_index : bool
        Whether to build vector embeddings
    
    Returns
    -------
    Dict[str, Any]
        Index statistics
    
    Examples
    --------
    >>> import scitex.scholar
    >>> 
    >>> # Index current directory
    >>> stats = scitex.scholar.build_index()
    >>> 
    >>> # Index multiple directories
    >>> stats = scitex.scholar.build_index([
    ...     "./papers",
    ...     "~/Documents/research"
    ... ])
    """
    if paths is None:
        paths = [Path(".")]
    else:
        paths = [Path(p).expanduser() for p in paths]
    
    scholar_dir = get_scholar_dir()
    stats = {}
    
    # Build local search index
    logger.info(f"Building local search index for {len(paths)} paths...")
    local_engine = LocalSearchEngine(
        index_path=scholar_dir / "local_index.json",
        cache_metadata=True
    )
    
    num_files = local_engine.build_index(paths, recursive=recursive)
    stats["local_files_indexed"] = num_files
    
    # Build vector index if requested
    if build_vector_index and num_files > 0:
        logger.info("Building vector embeddings...")
        
        # Get all indexed papers
        all_papers = []
        for path in paths:
            results = local_engine.search("*", [path], max_results=None)
            all_papers.extend([paper for paper, score in results])
        
        # Create vector index
        vector_engine = VectorSearchEngine(
            index_path=scholar_dir / "vector_index.pkl",
            embedding_dim=384,
            similarity_metric="cosine"
        )
        
        # Add papers with progress logging
        for i, paper in enumerate(all_papers):
            vector_engine.add_paper(paper, update_embedding=True)
            if (i + 1) % 10 == 0:
                logger.info(f"Generated embeddings for {i + 1}/{len(all_papers)} papers")
        
        # Save index
        vector_engine.save_index()
        stats["vector_embeddings_created"] = len(all_papers)
        stats.update(vector_engine.get_statistics())
    
    logger.info(f"Index building complete: {stats}")
    return stats


# Synchronous wrapper for convenience
def search_sync(
    query: str,
    web: bool = True,
    local: Optional[List[Union[str, Path]]] = None,
    max_results: int = 20,
    download_pdfs: bool = False,
    use_vector_search: bool = True,
    web_sources: Optional[List[str]] = None,
) -> List[Paper]:
    """Synchronous wrapper for search function.
    
    See `search` for parameter documentation.
    
    Examples
    --------
    >>> import scitex.scholar
    >>> 
    >>> # Simple synchronous search (web only)
    >>> papers = scitex.scholar.search_sync("machine learning")
    >>> 
    >>> # Search with local directories
    >>> papers = scitex.scholar.search_sync(
    ...     "deep learning",
    ...     local=["./papers", "~/Documents/research"]
    ... )
    >>> 
    >>> # Local only search
    >>> papers = scitex.scholar.search_sync(
    ...     "neural networks",
    ...     web=False,
    ...     local=["./my_papers"]
    ... )
    """
    return asyncio.run(search(
        query=query,
        web=web,
        local=local,
        max_results=max_results,
        download_pdfs=download_pdfs,
        use_vector_search=use_vector_search,
        web_sources=web_sources,
    ))