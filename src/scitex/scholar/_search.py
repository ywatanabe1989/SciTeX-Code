#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:10:00 (ywatanabe)"
# File: ./src/scitex/scholar/_search_unified.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_search_unified.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Unified search functionality for SciTeX Scholar.

This module consolidates:
- Web search (Semantic Scholar, PubMed, arXiv)
- Local PDF search
- Vector similarity search
- Search result ranking and merging
"""

import asyncio
import logging
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import aiohttp
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

from ._core import Paper
from ..errors import SearchError

logger = logging.getLogger(__name__)


class SearchEngine:
    """Base class for all search engines."""
    
    def __init__(self, name: str):
        self.name = name
        self.rate_limit = 0.1  # seconds between requests
        self._last_request = 0
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search for papers. Must be implemented by subclasses."""
        raise NotImplementedError
    
    async def _rate_limit(self):
        """Enforce rate limiting."""
        import time
        now = time.time()
        elapsed = now - self._last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request = time.time()


class SemanticScholarEngine(SearchEngine):
    """Semantic Scholar search engine."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("semantic_scholar")
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.rate_limit = 0.1 if api_key else 1.0  # Faster with API key
        
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search Semantic Scholar for papers."""
        await self._rate_limit()
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        params = {
            'query': query,
            'limit': min(limit, 100),
            'fields': 'title,authors,abstract,year,citationCount,journal,paperId,venue,fieldsOfStudy,isOpenAccess,url,tldr'
        }
        
        # Add year filters if provided
        if 'year_min' in kwargs:
            params['year'] = f"{kwargs['year_min']}-"
        if 'year_max' in kwargs:
            if 'year' in params:
                params['year'] = f"{kwargs['year_min']}-{kwargs['year_max']}"
            else:
                params['year'] = f"-{kwargs['year_max']}"
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/paper/search",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('data', []):
                            paper = self._parse_semantic_scholar_paper(item)
                            if paper:
                                papers.append(paper)
                    else:
                        error_msg = await response.text()
                        # Don't print error message directly - just log it
                        logger.debug(f"Semantic Scholar API returned {response.status}: {error_msg}")
                        # Return empty list to let other sources handle the search
                        return []
                        
        except Exception as e:
            logger.debug(f"Semantic Scholar search error: {e}")
            # Return empty list instead of raising to allow fallback to other sources
            return []
        
        return papers
    
    def _parse_semantic_scholar_paper(self, data: Dict[str, Any]) -> Optional[Paper]:
        """Parse Semantic Scholar paper data."""
        if not data or not isinstance(data, dict):
            logger.warning("Received None or non-dict data for Semantic Scholar paper")
            return None
            
        try:
            # Extract authors
            authors = []
            for author_data in data.get('authors', []):
                name = author_data.get('name', '')
                if name:
                    authors.append(name)
            
            # Get PDF URL if available
            pdf_url = None
            if data.get('isOpenAccess'):
                pdf_url = data.get('url')
            
            # Extract journal/venue
            journal_data = data.get('journal')
            journal = ''
            if journal_data and isinstance(journal_data, dict):
                journal = journal_data.get('name', '')
            if not journal:
                journal = data.get('venue', '')
            
            # Create paper
            paper = Paper(
                title=data.get('title', ''),
                authors=authors,
                abstract=data.get('abstract', '') or (data.get('tldr', {}) or {}).get('text', ''),
                source='semantic_scholar',
                year=data.get('year'),
                doi=data.get('doi'),
                journal=journal,
                keywords=data.get('fieldsOfStudy', []),
                citation_count=data.get('citationCount', 0),
                pdf_url=pdf_url,
                metadata={
                    'semantic_scholar_paper_id': data.get('paperId'),
                    'fields_of_study': data.get('fieldsOfStudy', []),
                    'is_open_access': data.get('isOpenAccess', False),
                    'citation_count_source': 'Semantic Scholar' if data.get('citationCount') is not None else None
                }
            )
            
            return paper
            
        except Exception as e:
            logger.warning(f"Failed to parse Semantic Scholar paper: {e}")
            return None


class PubMedEngine(SearchEngine):
    """PubMed search engine using E-utilities."""
    
    def __init__(self, email: Optional[str] = None):
        super().__init__("pubmed")
        self.email = email or "research@example.com"
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.rate_limit = 0.4  # NCBI rate limit
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search PubMed for papers."""
        await self._rate_limit()
        
        # First, search for IDs
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json',
            'email': self.email,
            'sort': 'relevance'  # Sort by relevance instead of date to get diverse years
        }
        
        # Add date filters
        year_min = kwargs.get('year_min')
        year_max = kwargs.get('year_max')
        if year_min is not None or year_max is not None:
            min_date = f"{year_min or 1900}/01/01"
            max_date = f"{year_max or datetime.now().year}/12/31"
            search_params['mindate'] = min_date
            search_params['maxdate'] = max_date
            search_params['datetype'] = 'pdat'  # Publication date
        else:
            # When no date range specified, search last 20 years to avoid only getting current year
            current_year = datetime.now().year
            search_params['mindate'] = f"{current_year - 20}/01/01"
            search_params['maxdate'] = f"{current_year}/12/31"
            search_params['datetype'] = 'pdat'
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Search for IDs
                logger.info(f"PubMed API URL: {self.base_url}/esearch.fcgi")
                logger.info(f"PubMed search params: {search_params}")
                async with session.get(
                    f"{self.base_url}/esearch.fcgi",
                    params=search_params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pmids = data.get('esearchresult', {}).get('idlist', [])
                        logger.info(f"PubMed search returned {len(pmids)} PMIDs")
                        
                        if pmids:
                            # Fetch details
                            papers = await self._fetch_pubmed_details(session, pmids)
                    else:
                        logger.error(f"PubMed search failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"PubMed search error: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return empty list instead of raising to allow other sources
            return []
        
        return papers
    
    async def _fetch_pubmed_details(self, session: aiohttp.ClientSession, pmids: List[str]) -> List[Paper]:
        """Fetch detailed information for PubMed IDs."""
        await self._rate_limit()
        
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email
        }
        
        papers = []
        
        async with session.get(
            f"{self.base_url}/efetch.fcgi",
            params=fetch_params
        ) as response:
            if response.status == 200:
                xml_data = await response.text()
                papers = self._parse_pubmed_xml(xml_data)
            else:
                logger.error(f"PubMed fetch failed: {response.status}")
        
        return papers
    
    def _parse_pubmed_xml(self, xml_data: str) -> List[Paper]:
        """Parse PubMed XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for article_elem in root.findall('.//PubmedArticle'):
                try:
                    # Extract article data
                    medline = article_elem.find('.//MedlineCitation')
                    if medline is None:
                        continue
                    
                    # Title
                    title_elem = medline.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ''
                    
                    # Authors
                    authors = []
                    for author_elem in medline.findall('.//Author'):
                        last_name = author_elem.findtext('LastName', '')
                        first_name = author_elem.findtext('ForeName', '')
                        if last_name:
                            name = f"{last_name}, {first_name}" if first_name else last_name
                            authors.append(name)
                    
                    # Abstract
                    abstract_parts = []
                    for abstract_elem in medline.findall('.//AbstractText'):
                        text = abstract_elem.text or ''
                        abstract_parts.append(text)
                    abstract = ' '.join(abstract_parts)
                    
                    # Year
                    year_elem = medline.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else None
                    
                    # Journal
                    journal_elem = medline.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else ''
                    
                    # PMID
                    pmid_elem = medline.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ''
                    
                    # DOI
                    doi = None
                    for id_elem in article_elem.findall('.//ArticleId'):
                        if id_elem.get('IdType') == 'doi':
                            doi = id_elem.text
                            break
                    
                    # Keywords
                    keywords = []
                    for kw_elem in medline.findall('.//MeshHeading/DescriptorName'):
                        if kw_elem.text:
                            keywords.append(kw_elem.text)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        source='pubmed',
                        year=year,
                        doi=doi,
                        pmid=pmid,
                        journal=journal,
                        keywords=keywords
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse PubMed article: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
        
        return papers


class ArxivEngine(SearchEngine):
    """arXiv search engine."""
    
    def __init__(self):
        super().__init__("arxiv")
        self.base_url = "http://export.arxiv.org/api/query"
        self.rate_limit = 0.5
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search arXiv for papers."""
        await self._rate_limit()
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        papers = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        papers = self._parse_arxiv_xml(xml_data)
                    else:
                        logger.error(f"arXiv search failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            raise SearchError(query, "arXiv", str(e))
        
        return papers
    
    def _parse_arxiv_xml(self, xml_data: str) -> List[Paper]:
        """Parse arXiv XML response."""
        papers = []
        
        try:
            # Parse XML with namespace
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                try:
                    # Title
                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text.strip() if title_elem is not None else ''
                    
                    # Authors
                    authors = []
                    for author_elem in entry.findall('atom:author', ns):
                        name_elem = author_elem.find('atom:name', ns)
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text)
                    
                    # Abstract
                    summary_elem = entry.find('atom:summary', ns)
                    abstract = summary_elem.text.strip() if summary_elem is not None else ''
                    
                    # Year
                    published_elem = entry.find('atom:published', ns)
                    year = None
                    if published_elem is not None and published_elem.text:
                        year = published_elem.text[:4]
                    
                    # arXiv ID
                    id_elem = entry.find('atom:id', ns)
                    arxiv_id = None
                    pdf_url = None
                    if id_elem is not None and id_elem.text:
                        # Extract ID from URL
                        arxiv_id = id_elem.text.split('/')[-1]
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    # Categories (as keywords)
                    keywords = []
                    for cat_elem in entry.findall('atom:category', ns):
                        term = cat_elem.get('term')
                        if term:
                            keywords.append(term)
                    
                    paper = Paper(
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        source='arxiv',
                        year=year,
                        arxiv_id=arxiv_id,
                        keywords=keywords,
                        pdf_url=pdf_url
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse arXiv entry: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to parse arXiv XML: {e}")
        
        return papers


class LocalSearchEngine(SearchEngine):
    """Search engine for local PDF files."""
    
    def __init__(self, index_path: Optional[Path] = None):
        super().__init__("local")
        self.index_path = index_path or get_scholar_dir() / "local_index.json"
        self.index = self._load_index()
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search local PDF collection."""
        # Local search is synchronous, wrap in async
        return await asyncio.to_thread(self._search_sync, query, limit, kwargs)
    
    def _search_sync(self, query: str, limit: int, kwargs: dict) -> List[Paper]:
        """Synchronous local search implementation."""
        if not self.index:
            return []
        
        # Simple keyword matching
        query_terms = query.lower().split()
        scored_papers = []
        
        for paper_data in self.index.values():
            # Calculate relevance score
            score = 0
            searchable_text = f"{paper_data.get('title', '')} {paper_data.get('abstract', '')} {' '.join(paper_data.get('keywords', []))}".lower()
            
            for term in query_terms:
                score += searchable_text.count(term)
            
            if score > 0:
                # Create Paper object
                paper = Paper(
                    title=paper_data.get('title', 'Unknown Title'),
                    authors=paper_data.get('authors', []),
                    abstract=paper_data.get('abstract', ''),
                    source='local',
                    year=paper_data.get('year'),
                    keywords=paper_data.get('keywords', []),
                    pdf_path=Path(paper_data.get('pdf_path', ''))
                )
                scored_papers.append((score, paper))
        
        # Sort by score and return top results
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        return [paper for score, paper in scored_papers[:limit]]
    
    def _load_index(self) -> Dict[str, Any]:
        """Load local search index."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load local index: {e}")
        return {}
    
    def build_index(self, pdf_dirs: List[Path]) -> Dict[str, Any]:
        """Build search index from PDF directories."""
        logger.info(f"Building local index from {len(pdf_dirs)} directories")
        
        index = {}
        stats = {'files_indexed': 0, 'errors': 0}
        
        for pdf_dir in pdf_dirs:
            if not pdf_dir.exists():
                continue
                
            for pdf_path in pdf_dir.rglob("*.pdf"):
                try:
                    # Extract text and metadata
                    paper_data = self._extract_pdf_metadata(pdf_path)
                    if paper_data:
                        index[str(pdf_path)] = paper_data
                        stats['files_indexed'] += 1
                except Exception as e:
                    logger.warning(f"Failed to index {pdf_path}: {e}")
                    stats['errors'] += 1
        
        # Save index
        self.index = index
        self._save_index()
        
        logger.info(f"Indexed {stats['files_indexed']} files with {stats['errors']} errors")
        return stats
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF file."""
        # This is a placeholder - in real implementation would use PyPDF2 or similar
        return {
            'title': pdf_path.stem.replace('_', ' ').title(),
            'authors': [],
            'abstract': '',
            'year': None,
            'keywords': [],
            'pdf_path': str(pdf_path)
        }
    
    def _save_index(self) -> None:
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)


class VectorSearchEngine(SearchEngine):
    """Vector similarity search using sentence embeddings."""
    
    def __init__(self, index_path: Optional[Path] = None, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__("vector")
        self.index_path = index_path or get_scholar_dir() / "vector_index.pkl"
        self.model_name = model_name
        self._model = None
        self._papers = []
        self._embeddings = None
        self._load_index()
    
    async def search(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search using vector similarity."""
        # Vector search is CPU-bound, use thread
        return await asyncio.to_thread(self._search_sync, query, limit)
    
    def _search_sync(self, query: str, limit: int) -> List[Paper]:
        """Synchronous vector search implementation."""
        if not self._embeddings or not self._papers:
            return []
        
        # Lazy load model
        if self._model is None:
            self._load_model()
        
        # Encode query
        query_embedding = self._model.encode([query])[0]
        
        # Calculate similarities
        import numpy as np
        similarities = np.dot(self._embeddings, query_embedding)
        
        # Get top results
        top_indices = np.argsort(similarities)[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self._papers):
                results.append(self._papers[idx])
        
        return results
    
    def add_papers(self, papers: List[Paper]) -> None:
        """Add papers to vector index."""
        if self._model is None:
            self._load_model()
        
        # Create searchable text for each paper
        texts = []
        for paper in papers:
            text = f"{paper.title} {paper.abstract}"
            texts.append(text)
        
        # Encode papers
        new_embeddings = self._model.encode(texts)
        
        # Add to index
        import numpy as np
        if self._embeddings is None:
            self._embeddings = new_embeddings
            self._papers = papers
        else:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])
            self._papers.extend(papers)
        
        # Save index
        self._save_index()
    
    def _load_model(self) -> None:
        """Load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except ImportError:
            logger.warning("sentence-transformers not installed. Vector search disabled.")
            self._model = None
    
    def _load_index(self) -> None:
        """Load vector index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self._papers = data.get('papers', [])
                    self._embeddings = data.get('embeddings')
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")
    
    def _save_index(self) -> None:
        """Save vector index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'papers': self._papers,
            'embeddings': self._embeddings
        }
        with open(self.index_path, 'wb') as f:
            pickle.dump(data, f)


class UnifiedSearcher:
    """
    Unified searcher that combines results from multiple engines.
    """
    
    def __init__(self, 
                 email: Optional[str] = None,
                 semantic_scholar_api_key: Optional[str] = None):
        """Initialize unified searcher with all engines."""
        self.email = email
        self.semantic_scholar_api_key = semantic_scholar_api_key
        self._engines = {}  # Lazy-loaded engines
    
    @property
    def engines(self):
        """Lazy-load engines as needed."""
        return self._engines
    
    def _get_engine(self, source: str):
        """Get or create engine for a source."""
        if source not in self._engines:
            if source == 'semantic_scholar':
                self._engines[source] = SemanticScholarEngine(self.semantic_scholar_api_key)
            elif source == 'pubmed':
                self._engines[source] = PubMedEngine(self.email)
            elif source == 'arxiv':
                self._engines[source] = ArxivEngine()
            elif source == 'local':
                self._engines[source] = LocalSearchEngine()
            elif source == 'vector':
                self._engines[source] = VectorSearchEngine()
            else:
                raise ValueError(f"Unknown source: {source}")
        return self._engines[source]
    
    async def search(self,
                    query: str,
                    sources: List[str] = None,
                    limit: int = 20,
                    deduplicate: bool = True,
                    **kwargs) -> List[Paper]:
        """
        Search across multiple sources and merge results.
        
        Args:
            query: Search query
            sources: List of sources to search (default: all web sources)
            limit: Maximum results per source
            deduplicate: Remove duplicate papers
            **kwargs: Additional parameters for engines
            
        Returns:
            Merged and ranked list of papers
        """
        if sources is None:
            sources = ['pubmed']  # Default to PubMed only
        
        # Filter to valid sources
        valid_sources = ['semantic_scholar', 'pubmed', 'arxiv', 'local', 'vector']
        sources = [s for s in sources if s in valid_sources]
        
        if not sources:
            logger.warning("No valid search sources specified")
            return []
        
        # Search all sources concurrently
        tasks = []
        for source in sources:
            try:
                engine = self._get_engine(source)
                task = engine.search(query, limit, **kwargs)
                tasks.append(task)
            except Exception as e:
                logger.debug(f"Failed to initialize {source} engine: {e}")
        
        logger.debug(f"Searching {len(tasks)} sources: {sources}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        all_papers = []
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                logger.debug(f"Search failed for {source}: {result}")
            else:
                logger.debug(f"{source} returned {len(result)} papers")
                all_papers.extend(result)
        
        # Deduplicate if requested
        if deduplicate:
            all_papers = self._deduplicate_papers(all_papers)
        
        # Sort by relevance (using citation count as proxy)
        all_papers.sort(key=lambda p: p.citation_count or 0, reverse=True)
        
        return all_papers[:limit]
    
    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers based on similarity."""
        if not papers:
            return []
        
        unique_papers = [papers[0]]
        
        for paper in papers[1:]:
            is_duplicate = False
            
            for unique_paper in unique_papers:
                if paper.similarity_score(unique_paper) > 0.85:
                    is_duplicate = True
                    # Keep the one with more information
                    if (paper.citation_count or 0) > (unique_paper.citation_count or 0):
                        unique_papers.remove(unique_paper)
                        unique_papers.append(paper)
                    break
            
            if not is_duplicate:
                unique_papers.append(paper)
        
        return unique_papers
    
    def build_local_index(self, pdf_dirs: List[Union[str, Path]]) -> Dict[str, Any]:
        """Build local search index."""
        pdf_dirs = [Path(d) for d in pdf_dirs]
        return self.engines['local'].build_index(pdf_dirs)
    
    def add_to_vector_index(self, papers: List[Paper]) -> None:
        """Add papers to vector search index."""
        self.engines['vector'].add_papers(papers)


# Convenience functions
def get_scholar_dir() -> Path:
    """Get SciTeX scholar directory."""
    scholar_dir = Path.home() / ".scitex" / "scholar"
    scholar_dir.mkdir(parents=True, exist_ok=True)
    return scholar_dir


async def search(query: str,
                sources: List[str] = None,
                limit: int = 20,
                email: Optional[str] = None,
                semantic_scholar_api_key: Optional[str] = None,
                **kwargs) -> List[Paper]:
    """
    Async convenience function for searching papers.
    """
    searcher = UnifiedSearcher(email=email, semantic_scholar_api_key=semantic_scholar_api_key)
    return await searcher.search(query, sources, limit, **kwargs)


def search_sync(query: str,
               sources: List[str] = None,
               limit: int = 20,
               email: Optional[str] = None,
               semantic_scholar_api_key: Optional[str] = None,
               **kwargs) -> List[Paper]:
    """
    Synchronous convenience function for searching papers.
    """
    return asyncio.run(search(query, sources, limit, email, semantic_scholar_api_key, **kwargs))


def build_index(paths: List[Union[str, Path]],
               vector_index: bool = True) -> Dict[str, Any]:
    """
    Build local search indices.
    
    Args:
        paths: Directories containing PDFs
        vector_index: Also build vector similarity index
        
    Returns:
        Statistics about indexing
    """
    searcher = UnifiedSearcher()
    stats = searcher.build_local_index(paths)
    
    if vector_index:
        # Add papers to vector index
        papers = searcher.engines['local']._search_sync("*", 9999, {})
        if papers:
            searcher.add_to_vector_index(papers)
            stats['vector_indexed'] = len(papers)
    
    return stats


# Export all classes and functions
__all__ = [
    'SearchEngine',
    'SemanticScholarEngine', 
    'PubMedEngine',
    'ArxivEngine',
    'LocalSearchEngine',
    'VectorSearchEngine',
    'UnifiedSearcher',
    'get_scholar_dir',
    'search',
    'search_sync',
    'build_index'
]