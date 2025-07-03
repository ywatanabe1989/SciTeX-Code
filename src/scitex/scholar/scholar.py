#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 09:30:00 (ywatanabe)"
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

This module provides a single, easy-to-use interface for all scholar functionality
including literature search, enrichment, PDF downloads, and bibliography generation.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Iterator
import pandas as pd
from datetime import datetime
import time

# Import existing components
from ._paper_acquisition import PaperAcquisition, PaperMetadata
from ._semantic_scholar_client import SemanticScholarClient, S2Paper
from ._paper_enrichment import PaperEnrichmentService
from ._journal_metrics import JournalMetrics
from ._paper import Paper
from ._local_search import LocalSearchEngine
from ._vector_search import VectorSearchEngine

logger = logging.getLogger(__name__)


class PaperCollection:
    """
    A collection of papers with chainable methods for filtering, analysis, and export.
    
    Supports fluent interface for easy paper management:
    ```python
    papers = scholar.search("deep learning") \
                   .filter(year_min=2020) \
                   .sort_by("citations") \
                   .save("dl_papers.bib")
    ```
    """
    
    def __init__(self, papers: List[Paper], scholar_instance: 'Scholar'):
        """
        Initialize paper collection.
        
        Args:
            papers: List of Paper objects
            scholar_instance: Reference to parent Scholar instance
        """
        self._papers = papers
        self._scholar = scholar_instance
        self._enriched = False
    
    @property
    def papers(self) -> List[Paper]:
        """Get the list of papers."""
        return self._papers
    
    def __len__(self) -> int:
        """Number of papers in collection."""
        return len(self._papers)
    
    def __iter__(self) -> Iterator[Paper]:
        """Iterate over papers."""
        return iter(self._papers)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Paper, 'PaperCollection']:
        """Get paper by index or slice."""
        if isinstance(index, slice):
            return PaperCollection(self._papers[index], self._scholar)
        return self._papers[index]
    
    def filter(self, 
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               min_citations: Optional[int] = None,
               max_citations: Optional[int] = None,
               impact_factor_min: Optional[float] = None,
               open_access_only: bool = False,
               journals: Optional[List[str]] = None,
               authors: Optional[List[str]] = None,
               keywords: Optional[List[str]] = None) -> 'PaperCollection':
        """
        Filter papers by various criteria.
        
        Args:
            year_min: Minimum publication year
            year_max: Maximum publication year
            min_citations: Minimum citation count
            max_citations: Maximum citation count
            impact_factor_min: Minimum journal impact factor
            open_access_only: Only papers with PDFs
            journals: List of journal names to include
            authors: List of author names to include
            keywords: List of keywords to match
            
        Returns:
            New PaperCollection with filtered papers
        """
        filtered = []
        
        for paper in self._papers:
            # Year filters
            if year_min and paper.year and int(paper.year) < year_min:
                continue
            if year_max and paper.year and int(paper.year) > year_max:
                continue
            
            # Citation filters
            if min_citations and paper.citation_count < min_citations:
                continue
            if max_citations and paper.citation_count > max_citations:
                continue
            
            # Impact factor filter
            if impact_factor_min and (not paper.impact_factor or float(paper.impact_factor) < impact_factor_min):
                continue
            
            # Open access filter
            if open_access_only and not paper.pdf_url:
                continue
            
            # Journal filter
            if journals and paper.journal not in journals:
                continue
            
            # Author filter
            if authors:
                author_match = any(
                    any(author_name.lower() in paper_author.lower() for paper_author in paper.authors)
                    for author_name in authors
                )
                if not author_match:
                    continue
            
            # Keyword filter
            if keywords:
                keyword_match = any(
                    any(keyword.lower() in paper_keyword.lower() for paper_keyword in paper.keywords)
                    for keyword in keywords
                )
                if not keyword_match:
                    continue
            
            filtered.append(paper)
        
        logger.info(f"Filtered {len(self._papers)} papers to {len(filtered)} papers")
        return PaperCollection(filtered, self._scholar)
    
    def sort_by(self, field: str = "citations", reverse: bool = True) -> 'PaperCollection':
        """
        Sort papers by specified field.
        
        Args:
            field: Field to sort by ('citations', 'year', 'impact_factor', 'title')
            reverse: Sort in descending order
            
        Returns:
            New PaperCollection with sorted papers
        """
        def get_sort_key(paper):
            if field == "citations":
                return paper.citation_count or 0
            elif field == "year":
                return int(paper.year) if paper.year else 0
            elif field == "impact_factor":
                return float(paper.impact_factor) if paper.impact_factor else 0
            elif field == "title":
                return paper.title.lower()
            else:
                logger.warning(f"Unknown sort field: {field}. Using citations.")
                return paper.citation_count or 0
        
        sorted_papers = sorted(self._papers, key=get_sort_key, reverse=reverse)
        return PaperCollection(sorted_papers, self._scholar)
    
    def enrich(self, force: bool = False) -> 'PaperCollection':
        """
        Enrich papers with journal metrics.
        
        Args:
            force: Force re-enrichment even if already enriched
            
        Returns:
            Self for chaining
        """
        if self._enriched and not force:
            logger.info("Papers already enriched. Use force=True to re-enrich.")
            return self
        
        enricher = PaperEnrichmentService()
        self._papers = enricher.enrich_papers(self._papers)
        self._enriched = True
        
        enriched_count = sum(1 for p in self._papers if p.impact_factor is not None)
        logger.info(f"Enriched {enriched_count}/{len(self._papers)} papers with journal metrics")
        return self
    
    def download_pdfs(self, 
                     force: bool = False, 
                     max_concurrent: int = 3,
                     show_progress: bool = True) -> 'PaperCollection':
        """
        Download PDFs for papers with available URLs.
        
        Args:
            force: Force re-download even if file exists
            max_concurrent: Maximum concurrent downloads
            show_progress: Show download progress
            
        Returns:
            Self for chaining
        """
        if show_progress:
            print(f"Downloading PDFs for {len(self._papers)} papers...")
        
        # Use asyncio to download PDFs
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, create new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self._download_pdfs_async(force, max_concurrent))
                downloaded_paths = future.result()
        else:
            downloaded_paths = asyncio.run(self._download_pdfs_async(force, max_concurrent))
        
        # Update papers with PDF paths
        for paper in self._papers:
            if paper.get_identifier() in downloaded_paths:
                paper.pdf_path = downloaded_paths[paper.get_identifier()]
        
        downloaded_count = len(downloaded_paths)
        if show_progress:
            print(f"Successfully downloaded {downloaded_count} PDFs")
        
        return self
    
    async def _download_pdfs_async(self, force: bool, max_concurrent: int) -> Dict[str, Path]:
        """Internal async PDF download method."""
        from ._pdf_downloader import PDFDownloader
        
        downloader = PDFDownloader(download_dir=self._scholar.download_dir)
        return await downloader.download_papers(self._papers, force=force)
    
    def save(self, 
             filename: Union[str, Path], 
             format: str = "bibtex",
             include_enriched: bool = True) -> Path:
        """
        Save papers to file.
        
        Args:
            filename: Output filename
            format: Output format ('bibtex', 'csv', 'json')
            include_enriched: Include enriched metadata
            
        Returns:
            Path to saved file
        """
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "bibtex":
            self._save_bibtex(output_path, include_enriched)
        elif format.lower() == "csv":
            self._save_csv(output_path)
        elif format.lower() == "json":
            self._save_json(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved {len(self._papers)} papers to {output_path}")
        return output_path
    
    def _save_bibtex(self, path: Path, include_enriched: bool):
        """Save as BibTeX format."""
        content = f"% Bibliography generated by scitex.scholar\n"
        content += f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"% Papers: {len(self._papers)}\n\n"
        
        used_keys = set()
        for paper in self._papers:
            # Generate unique BibTeX key
            base_key = self._generate_bibtex_key(paper)
            key = base_key
            counter = 1
            while key in used_keys:
                key = f"{base_key}{chr(ord('a') + counter - 1)}"
                counter += 1
            used_keys.add(key)
            
            # Get BibTeX entry
            bibtex = paper.to_bibtex(include_enriched=include_enriched)
            # Replace key if modified
            if key != base_key:
                bibtex = bibtex.replace(f"{{{base_key},", f"{{{key},", 1)
            
            content += bibtex + "\n\n"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_csv(self, path: Path):
        """Save as CSV format."""
        df = self.to_dataframe()
        df.to_csv(path, index=False)
    
    def _save_json(self, path: Path):
        """Save as JSON format."""
        import json
        data = []
        for paper in self._papers:
            paper_dict = {
                'title': paper.title,
                'authors': paper.authors,
                'abstract': paper.abstract,
                'year': paper.year,
                'journal': paper.journal,
                'doi': paper.doi,
                'pmid': paper.pmid,
                'citation_count': paper.citation_count,
                'impact_factor': paper.impact_factor,
                'keywords': paper.keywords,
                'source': paper.source
            }
            data.append(paper_dict)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _generate_bibtex_key(self, paper: Paper) -> str:
        """Generate BibTeX key from paper."""
        if paper.authors:
            author = paper.authors[0].split(',')[0].split()[-1].lower()
        else:
            author = "unknown"
        
        year = paper.year or "0000"
        title_words = paper.title.lower().split()[:2]
        title_part = ''.join(word[:3] for word in title_words if word.isalpha())
        
        return f"{author}{year}{title_part}"
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert papers to pandas DataFrame for analysis.
        
        Returns:
            DataFrame with paper data
        """
        data = []
        for paper in self._papers:
            row = {
                'title': paper.title,
                'first_author': paper.authors[0] if paper.authors else '',
                'year': int(paper.year) if paper.year else None,
                'journal': paper.journal,
                'citation_count': paper.citation_count,
                'impact_factor': float(paper.impact_factor) if paper.impact_factor else None,
                'doi': paper.doi,
                'pmid': paper.pmid,
                'source': paper.source,
                'has_pdf': bool(paper.pdf_url),
                'keyword_count': len(paper.keywords),
                'abstract_length': len(paper.abstract) if paper.abstract else 0
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in the paper collection.
        
        Returns:
            Dictionary with trend analysis
        """
        df = self.to_dataframe()
        
        # Year distribution
        year_counts = df['year'].value_counts().sort_index()
        
        # Journal distribution
        journal_counts = df['journal'].value_counts().head(10)
        
        # Citation statistics
        citation_stats = df['citation_count'].describe()
        
        # Impact factor statistics (for papers with IF)
        if_papers = df[df['impact_factor'].notna()]
        if_stats = if_papers['impact_factor'].describe() if not if_papers.empty else None
        
        return {
            'total_papers': len(self._papers),
            'year_range': (int(df['year'].min()), int(df['year'].max())) if not df['year'].isna().all() else None,
            'yearly_distribution': year_counts.to_dict(),
            'top_journals': journal_counts.to_dict(),
            'citation_statistics': citation_stats.to_dict(),
            'impact_factor_statistics': if_stats.to_dict() if if_stats is not None else None,
            'open_access_percentage': (df['has_pdf'].sum() / len(df)) * 100,
            'avg_abstract_length': df['abstract_length'].mean()
        }
    
    async def find_gaps_async(self, topic: str) -> List[str]:
        """
        Use AI to identify research gaps (async version).
        
        Args:
            topic: Research topic for gap analysis
            
        Returns:
            List of identified research gaps
        """
        if not self._scholar.ai_client:
            return ["AI client not available for gap analysis"]
        
        return await self._scholar.acquisition.find_research_gaps(
            [self._to_paper_metadata(p) for p in self._papers], 
            topic
        )
    
    def find_gaps(self, topic: str) -> List[str]:
        """
        Use AI to identify research gaps (sync version).
        
        Args:
            topic: Research topic for gap analysis
            
        Returns:
            List of identified research gaps
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.find_gaps_async(topic))
                    return future.result()
            else:
                return asyncio.run(self.find_gaps_async(topic))
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return [f"Gap analysis failed: {str(e)}"]
    
    def _to_paper_metadata(self, paper: Paper) -> PaperMetadata:
        """Convert Paper to PaperMetadata for compatibility."""
        return PaperMetadata(
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            year=paper.year,
            doi=paper.doi,
            pmid=paper.pmid,
            journal=paper.journal,
            keywords=paper.keywords,
            source=paper.source,
            citation_count=paper.citation_count,
            impact_factor=paper.impact_factor
        )
    
    def summary(self) -> str:
        """
        Generate a summary of the paper collection.
        
        Returns:
            Formatted summary string
        """
        trends = self.analyze_trends()
        
        summary = f"Paper Collection Summary\n"
        summary += f"=" * 50 + "\n"
        summary += f"Total papers: {trends['total_papers']}\n"
        
        if trends['year_range']:
            summary += f"Year range: {trends['year_range'][0]} - {trends['year_range'][1]}\n"
        
        if trends['citation_statistics']:
            avg_citations = trends['citation_statistics']['mean']
            summary += f"Average citations: {avg_citations:.1f}\n"
        
        if trends['impact_factor_statistics']:
            avg_if = trends['impact_factor_statistics']['mean']
            summary += f"Average impact factor: {avg_if:.2f}\n"
        
        summary += f"Open access: {trends['open_access_percentage']:.1f}%\n"
        
        if trends['top_journals']:
            summary += f"\nTop journals:\n"
            for journal, count in list(trends['top_journals'].items())[:5]:
                summary += f"  - {journal}: {count} papers\n"
        
        return summary


class Scholar:
    """
    Unified interface for scientific literature search and management.
    
    Provides a single entry point for all scholar functionality with smart defaults
    and method chaining support.
    
    Example:
    ```python
    # Initialize with defaults
    scholar = Scholar(email="researcher@university.edu")
    
    # Simple search with automatic enrichment
    papers = scholar.search("deep learning neuroscience")
    
    # Chained operations
    recent_papers = scholar.search("machine learning") \
                          .filter(year_min=2020) \
                          .sort_by("citations") \
                          .download_pdfs() \
                          .save("ml_papers.bib")
    
    # Batch operations
    topics = ["AI", "neuroscience", "genomics"]
    all_papers = scholar.search_multiple(topics, papers_per_topic=10)
    ```
    """
    
    def __init__(self,
                 email: Optional[str] = None,
                 api_keys: Optional[Dict[str, str]] = None,
                 enrich_by_default: bool = True,
                 download_dir: Optional[Union[str, Path]] = None,
                 cache_results: bool = True,
                 ai_provider: Optional[str] = None,
                 rate_limit: float = 0.1):
        """
        Initialize Scholar with configuration.
        
        Args:
            email: Email for API compliance (auto-detected from env)
            api_keys: Dict of API keys {'s2': 'key', 'openai': 'key'}
            enrich_by_default: Automatically enrich papers with journal metrics
            download_dir: Directory for PDF downloads
            cache_results: Enable result caching
            ai_provider: AI provider for analysis ('anthropic', 'openai', 'google')
            rate_limit: Rate limit for API requests
        """
        # Auto-detect configuration from environment
        self.email = email or os.getenv('ENTREZ_EMAIL', 'research@example.com')
        
        # Handle API keys
        self.api_keys = api_keys or {}
        if 's2' not in self.api_keys:
            self.api_keys['s2'] = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
        if 'openai' not in self.api_keys and ai_provider == 'openai':
            self.api_keys['openai'] = os.getenv('OPENAI_API_KEY')
        
        # Configuration
        self.enrich_by_default = enrich_by_default
        self.download_dir = Path(download_dir) if download_dir else Path("./downloaded_papers")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.cache_results = cache_results
        self.ai_provider = ai_provider
        
        # Initialize internal components
        self.acquisition = PaperAcquisition(
            download_dir=self.download_dir,
            email=self.email,
            s2_api_key=self.api_keys.get('s2'),
            ai_provider=ai_provider
        )
        
        self.enricher = PaperEnrichmentService(
            pdf_download_dir=self.download_dir
        )
        
        self.journal_metrics = JournalMetrics()
        
        # AI client (if available)
        self.ai_client = None
        if ai_provider:
            try:
                from scitex.ai import genai_factory
                self.ai_client = genai_factory(ai_provider)
                logger.info(f"Initialized AI client: {ai_provider}")
            except ImportError:
                logger.warning("AI functionality not available. Install scitex.ai dependencies.")
            except Exception as e:
                logger.warning(f"Failed to initialize AI client: {e}")
        
        logger.info(f"Scholar initialized with enrichment={'ON' if enrich_by_default else 'OFF'}")
    
    def search(self,
               query: str,
               limit: int = 20,
               sources: Union[str, List[str]] = 'all',
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               open_access_only: bool = False,
               show_progress: bool = True) -> PaperCollection:
        """
        Search for papers with automatic enrichment.
        
        Args:
            query: Search query
            limit: Maximum number of results
            sources: Sources to search ('all', 'semantic_scholar', 'pubmed', 'arxiv')
            year_min: Minimum publication year
            year_max: Maximum publication year
            open_access_only: Only papers with free PDFs
            show_progress: Show search progress
            
        Returns:
            PaperCollection for method chaining
        """
        if show_progress:
            print(f"Searching for: '{query}'...")
        
        # Convert sources
        if sources == 'all':
            sources = ['semantic_scholar', 'pubmed', 'arxiv']
        elif isinstance(sources, str):
            sources = [sources]
        
        # Perform search
        start_time = time.time()
        
        # Use asyncio for search
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self._search_async(
                    query, sources, limit, year_min, year_max, open_access_only
                ))
                paper_metadata_list = future.result()
        else:
            paper_metadata_list = asyncio.run(self._search_async(
                query, sources, limit, year_min, year_max, open_access_only
            ))
        
        # Convert to Paper objects
        papers = [self._metadata_to_paper(pm) for pm in paper_metadata_list]
        
        search_time = time.time() - start_time
        
        if show_progress:
            print(f"Found {len(papers)} papers in {search_time:.1f}s")
        
        # Create collection and auto-enrich if enabled
        collection = PaperCollection(papers, self)
        
        if self.enrich_by_default:
            if show_progress:
                print("Enriching with journal metrics...")
            collection = collection.enrich()
        
        return collection
    
    async def _search_async(self, 
                           query: str, 
                           sources: List[str], 
                           limit: int,
                           year_min: Optional[int],
                           year_max: Optional[int],
                           open_access_only: bool) -> List[PaperMetadata]:
        """Internal async search method."""
        return await self.acquisition.search(
            query=query,
            sources=sources,
            max_results=limit,
            start_year=year_min,
            end_year=year_max,
            open_access_only=open_access_only
        )
    
    def search_multiple(self, 
                       queries: List[str],
                       papers_per_query: int = 10,
                       **kwargs) -> PaperCollection:
        """
        Search multiple topics and combine results.
        
        Args:
            queries: List of search queries
            papers_per_query: Papers to fetch per query
            **kwargs: Additional search parameters
            
        Returns:
            Combined PaperCollection
        """
        print(f"Searching {len(queries)} topics...")
        
        all_papers = []
        for i, query in enumerate(queries, 1):
            print(f"  {i}/{len(queries)}: {query}")
            collection = self.search(query, limit=papers_per_query, show_progress=False, **kwargs)
            all_papers.extend(collection.papers)
        
        # Remove duplicates based on title similarity
        unique_papers = self._deduplicate_papers(all_papers)
        print(f"Combined {len(unique_papers)} unique papers from {len(all_papers)} total")
        
        return PaperCollection(unique_papers, self)
    
    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers based on title and DOI."""
        unique_papers = []
        seen_dois = set()
        seen_titles = set()
        
        for paper in papers:
            is_duplicate = False
            
            # Check DOI first
            if paper.doi and paper.doi in seen_dois:
                is_duplicate = True
            elif paper.doi:
                seen_dois.add(paper.doi)
            
            # Check title
            if not is_duplicate:
                normalized_title = ''.join(paper.title.lower().split())
                if normalized_title in seen_titles:
                    is_duplicate = True
                else:
                    seen_titles.add(normalized_title)
            
            if not is_duplicate:
                unique_papers.append(paper)
        
        return unique_papers
    
    def _metadata_to_paper(self, metadata: PaperMetadata) -> Paper:
        """Convert PaperMetadata to Paper object."""
        return Paper(
            title=metadata.title,
            authors=metadata.authors,
            abstract=metadata.abstract,
            source=metadata.source,
            year=metadata.year,
            doi=metadata.doi,
            pmid=metadata.pmid,
            arxiv_id=metadata.arxiv_id,
            journal=metadata.journal,
            keywords=metadata.keywords,
            citation_count=metadata.citation_count,
            impact_factor=metadata.impact_factor,
            pdf_url=metadata.pdf_url,
            metadata={
                'influential_citation_count': metadata.influential_citation_count,
                's2_paper_id': metadata.s2_paper_id,
                'fields_of_study': metadata.fields_of_study,
                'has_open_access': metadata.has_open_access,
                'journal_quartile': metadata.journal_quartile,
                'journal_rank': metadata.journal_rank,
                'h_index': metadata.h_index
            }
        )
    
    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass
    
    # Quick utility methods
    def quick_search(self, query: str, top_n: int = 5) -> List[str]:
        """
        Quick search returning just paper titles.
        
        Args:
            query: Search query
            top_n: Number of results
            
        Returns:
            List of paper titles
        """
        papers = self.search(query, limit=top_n, show_progress=False)
        return [paper.title for paper in papers]
    
    def build_local_index(self, pdf_directory: Union[str, Path]) -> None:
        """
        Build search index from local PDF collection.
        
        Args:
            pdf_directory: Directory containing PDFs
        """
        from ._search import build_index
        build_index(str(pdf_directory))
        logger.info(f"Built local search index for: {pdf_directory}")
    
    def search_local(self, query: str, limit: int = 10) -> List[Paper]:
        """
        Search local PDF collection.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching papers
        """
        from ._search import search_sync
        local_papers = search_sync(query, local_only=True)
        return local_papers[:limit]
    
    def get_recommendations(self, paper_title: str, limit: int = 10) -> PaperCollection:
        """
        Get paper recommendations based on a paper title.
        
        Args:
            paper_title: Title of reference paper
            limit: Number of recommendations
            
        Returns:
            PaperCollection with recommendations
        """
        # First find the paper ID
        search_results = self.search(paper_title, limit=1, show_progress=False)
        if not search_results:
            logger.warning(f"Could not find paper: {paper_title}")
            return PaperCollection([], self)
        
        # Get S2 paper ID from metadata
        reference_paper = search_results[0]
        s2_id = reference_paper.metadata.get('s2_paper_id')
        
        if not s2_id:
            logger.warning("No Semantic Scholar ID found for recommendations")
            return PaperCollection([], self)
        
        # Get recommendations using Semantic Scholar
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._get_recommendations_async(s2_id, limit))
                    recommendations = future.result()
            else:
                recommendations = asyncio.run(self._get_recommendations_async(s2_id, limit))
            
            # Convert to Papers
            papers = [self._s2_to_paper(s2_paper) for s2_paper in recommendations]
            collection = PaperCollection(papers, self)
            
            if self.enrich_by_default:
                collection = collection.enrich()
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return PaperCollection([], self)
    
    async def _get_recommendations_async(self, s2_id: str, limit: int) -> List[S2Paper]:
        """Get recommendations using Semantic Scholar API."""
        async with SemanticScholarClient(api_key=self.api_keys.get('s2')) as client:
            return await client.get_recommendations(s2_id, limit)
    
    def _s2_to_paper(self, s2_paper: S2Paper) -> Paper:
        """Convert S2Paper to Paper object."""
        return Paper(
            title=s2_paper.title,
            authors=s2_paper.author_names,
            abstract=s2_paper.abstract or '',
            source='semantic_scholar',
            year=str(s2_paper.year) if s2_paper.year else '',
            doi=s2_paper.doi or '',
            pmid=s2_paper.pmid or '',
            arxiv_id=s2_paper.arxivId or '',
            journal=s2_paper.venue or '',
            keywords=s2_paper.fieldsOfStudy,
            citation_count=s2_paper.citationCount,
            pdf_url=s2_paper.pdf_url,
            metadata={
                'influential_citation_count': s2_paper.influentialCitationCount,
                's2_paper_id': s2_paper.paperId,
                'fields_of_study': [f.get('category', '') for f in s2_paper.s2FieldsOfStudy],
                'has_open_access': s2_paper.has_open_access
            }
        )


# EOF