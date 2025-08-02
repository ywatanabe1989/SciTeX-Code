<!-- ---
!-- Timestamp: 2025-07-01 22:22:52
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Scholar/docs/from_user/suggestions_by_other_LLMs_v02.md
!-- --- -->

SciTeX-Scholar Enhancement: Semantic Scholar Integration
To: SciTeX Development Team
From: AI Architecture Consultant
Date: January 2025
Re: Semantic Scholar API Integration for Enhanced Paper Access

Executive Summary
I've analyzed your SciTeX-Scholar implementation and identified Semantic Scholar (S2) as a critical integration that solves your subscription paper access challenge while significantly enhancing your system's capabilities.
Technical Integration Plan
1. Core API Integration
Create src/scitex_scholar/semantic_scholar_client.py:
pythonimport asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from scitex import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@dataclass
class S2Paper:
    """Semantic Scholar paper representation"""
    paperId: str
    title: str
    authors: List[Dict[str, str]]
    year: Optional[int]
    abstract: Optional[str]
    openAccessPdf: Optional[Dict[str, str]]
    citationCount: int
    influentialCitationCount: int
    references: List[str]
    citations: List[str]
    venue: Optional[str]
    doi: Optional[str]
    arxivId: Optional[str]
    pmid: Optional[str]
    fieldsOfStudy: List[str]
    s2FieldsOfStudy: List[Dict[str, str]]
    
    @property
    def has_open_access(self) -> bool:
        return self.openAccessPdf is not None
    
    @property
    def pdf_url(self) -> Optional[str]:
        return self.openAccessPdf['url'] if self.openAccessPdf else None


class SemanticScholarClient:
    """Client for Semantic Scholar Academic Graph API"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RATE_LIMIT = 100  # requests per 5 minutes
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_times = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement S2 rate limiting (100 requests per 5 min)"""
        now = time.time()
        # Remove requests older than 5 minutes
        self._request_times = [t for t in self._request_times if now - t < 300]
        
        if len(self._request_times) >= self.RATE_LIMIT:
            sleep_time = 300 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(now)
    
    async def search_papers(self, 
                          query: str,
                          limit: int = 20,
                          fields: Optional[List[str]] = None,
                          year_filter: Optional[str] = None,
                          open_access_only: bool = False) -> List[S2Paper]:
        """
        Search for papers using Semantic Scholar
        
        Args:
            query: Search query
            limit: Maximum results
            fields: Fields to return
            year_filter: Year range (e.g., "2020-2025")
            open_access_only: Only return papers with PDFs
        """
        await self._rate_limit()
        
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year',
                'openAccessPdf', 'citationCount', 'influentialCitationCount',
                'venue', 'doi', 'arxivId', 'pmid', 'fieldsOfStudy',
                's2FieldsOfStudy'
            ]
        
        params = {
            'query': query,
            'limit': limit,
            'fields': ','.join(fields)
        }
        
        if year_filter:
            params['year'] = year_filter
        
        if open_access_only:
            params['openAccessPdf'] = ''
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        url = f"{self.BASE_URL}/paper/search"
        
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            
        papers = [S2Paper(**paper) for paper in data.get('data', [])]
        return papers
    
    async def get_paper(self,
                       paper_id: str,
                       fields: Optional[List[str]] = None) -> Optional[S2Paper]:
        """Get details for a specific paper by ID, DOI, arxiv ID, etc."""
        await self._rate_limit()
        
        if fields is None:
            fields = [
                'paperId', 'title', 'abstract', 'authors', 'year',
                'openAccessPdf', 'citationCount', 'influentialCitationCount',
                'references', 'citations', 'venue', 'doi', 'arxivId', 'pmid',
                'fieldsOfStudy', 's2FieldsOfStudy'
            ]
        
        params = {'fields': ','.join(fields)}
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/paper/{paper_id}"
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return S2Paper(**data) if data else None
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                return None
            raise
    
    async def get_paper_citations(self,
                                 paper_id: str,
                                 limit: int = 100,
                                 fields: Optional[List[str]] = None) -> List[S2Paper]:
        """Get papers that cite this paper"""
        await self._rate_limit()
        
        if fields is None:
            fields = ['paperId', 'title', 'authors', 'year', 'openAccessPdf']
        
        params = {
            'fields': ','.join(fields),
            'limit': limit
        }
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/paper/{paper_id}/citations"
        
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            
        citations = [S2Paper(**cite['citingPaper']) for cite in data.get('data', [])]
        return citations
    
    async def get_recommendations(self,
                                paper_id: str,
                                limit: int = 20) -> List[S2Paper]:
        """Get recommended papers based on a paper"""
        await self._rate_limit()
        
        params = {
            'fields': 'paperId,title,abstract,authors,year,openAccessPdf',
            'limit': limit
        }
        headers = {'x-api-key': self.api_key} if self.api_key else {}
        
        url = f"{self.BASE_URL}/recommendations/v1/papers/forpaper/{paper_id}"
        
        async with self.session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            
        papers = [S2Paper(**paper) for paper in data.get('recommendedPapers', [])]
        return papers
2. Enhance Paper Acquisition
Update src/scitex_scholar/paper_acquisition.py:
pythonclass EnhancedPaperAcquisition(PaperAcquisition):
    """Enhanced paper acquisition with Semantic Scholar"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s2_client = SemanticScholarClient()
    
    async def search(self, 
                    query: str,
                    sources: List[str] = None,
                    **kwargs) -> List[PaperMetadata]:
        """Enhanced search including Semantic Scholar"""
        sources = sources or ['pubmed', 'arxiv', 'semantic_scholar']
        
        # Get results from parent class
        results = await super().search(query, sources, **kwargs)
        
        # Add Semantic Scholar results
        if 'semantic_scholar' in sources:
            async with self.s2_client as client:
                s2_papers = await client.search_papers(
                    query=query,
                    limit=kwargs.get('max_results', 20),
                    open_access_only=kwargs.get('open_access_only', False)
                )
                
                # Convert to PaperMetadata
                for s2_paper in s2_papers:
                    results.append(self._s2_to_metadata(s2_paper))
        
        return self._deduplicate_results(results)
    
    async def find_open_access_version(self, paper: PaperMetadata) -> Optional[str]:
        """Enhanced OA finder using multiple sources"""
        # Try existing methods first
        pdf_url = await super()._find_open_access_pdf(paper)
        
        if not pdf_url:
            # Try Semantic Scholar
            async with self.s2_client as client:
                # Search by multiple identifiers
                paper_id = None
                if paper.doi:
                    paper_id = paper.doi
                elif paper.arxiv_id:
                    paper_id = f"arXiv:{paper.arxiv_id}"
                elif paper.pmid:
                    paper_id = f"PMID:{paper.pmid}"
                
                if paper_id:
                    s2_paper = await client.get_paper(paper_id)
                    if s2_paper and s2_paper.has_open_access:
                        pdf_url = s2_paper.pdf_url
        
        return pdf_url
    
    def _s2_to_metadata(self, s2_paper: S2Paper) -> PaperMetadata:
        """Convert S2Paper to PaperMetadata"""
        return PaperMetadata(
            title=s2_paper.title,
            authors=[a['name'] for a in s2_paper.authors],
            abstract=s2_paper.abstract or '',
            year=str(s2_paper.year) if s2_paper.year else '',
            doi=s2_paper.doi or '',
            pmid=s2_paper.pmid or '',
            arxiv_id=s2_paper.arxivId or '',
            journal=s2_paper.venue or '',
            keywords=[f['category'] for f in s2_paper.s2FieldsOfStudy],
            pdf_url=s2_paper.pdf_url or '',
            source='semantic_scholar',
            citation_count=s2_paper.citationCount
        )
3. Add Citation Network Analysis
Create src/scitex_scholar/citation_network.py:
pythonclass CitationNetworkAnalyzer:
    """Analyze citation networks using Semantic Scholar"""
    
    def __init__(self, s2_client: SemanticScholarClient):
        self.s2_client = s2_client
    
    async def build_citation_network(self,
                                   seed_papers: List[str],
                                   depth: int = 2,
                                   max_papers: int = 100) -> Dict[str, Any]:
        """Build citation network from seed papers"""
        network = {
            'nodes': {},  # paper_id: paper_data
            'edges': []   # [(citing_id, cited_id), ...]
        }
        
        to_process = seed_papers.copy()
        processed = set()
        
        for level in range(depth):
            next_level = []
            
            for paper_id in to_process:
                if paper_id in processed or len(network['nodes']) >= max_papers:
                    continue
                
                # Get paper details
                paper = await self.s2_client.get_paper(paper_id)
                if not paper:
                    continue
                
                network['nodes'][paper_id] = {
                    'title': paper.title,
                    'year': paper.year,
                    'citations': paper.citationCount,
                    'level': level
                }
                
                # Get citations
                citations = await self.s2_client.get_paper_citations(
                    paper_id, limit=10
                )
                
                for citation in citations:
                    network['edges'].append((citation.paperId, paper_id))
                    if citation.paperId not in processed:
                        next_level.append(citation.paperId)
                
                processed.add(paper_id)
            
            to_process = next_level
        
        return network
    
    async def find_research_trends(self,
                                 topic: str,
                                 years: int = 5) -> Dict[str, Any]:
        """Analyze research trends in a topic"""
        current_year = datetime.now().year
        trends = {}
        
        for year in range(current_year - years, current_year + 1):
            papers = await self.s2_client.search_papers(
                query=topic,
                year_filter=f"{year}-{year}",
                limit=100
            )
            
            trends[year] = {
                'count': len(papers),
                'avg_citations': sum(p.citationCount for p in papers) / len(papers) if papers else 0,
                'top_venues': self._get_top_venues(papers),
                'emerging_keywords': self._get_emerging_keywords(papers)
            }
        
        return trends
4. Update Vector Search Engine
Enhance src/scitex_scholar/vector_search_engine.py:
pythonclass EnhancedVectorSearchEngine(VectorSearchEngine):
    """Vector search with Semantic Scholar enrichment"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s2_client = SemanticScholarClient()
    
    async def add_document_with_enrichment(self,
                                         doc_id: str,
                                         content: str,
                                         metadata: Dict[str, Any]) -> bool:
        """Add document with S2 enrichment"""
        # Try to find paper in Semantic Scholar
        enriched_metadata = metadata.copy()
        
        if metadata.get('doi') or metadata.get('arxiv_id'):
            async with self.s2_client as client:
                paper_id = metadata.get('doi') or f"arXiv:{metadata.get('arxiv_id')}"
                s2_paper = await client.get_paper(paper_id)
                
                if s2_paper:
                    enriched_metadata.update({
                        'citation_count': s2_paper.citationCount,
                        'influential_citations': s2_paper.influentialCitationCount,
                        'fields_of_study': [f['category'] for f in s2_paper.s2FieldsOfStudy],
                        's2_paper_id': s2_paper.paperId,
                        'has_open_access': s2_paper.has_open_access
                    })
        
        return await super().add_document(doc_id, content, enriched_metadata)
5. Update MCP Server
Add to src/scitex_scholar/mcp_vector_server.py:
python@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """Extended tools with S2 capabilities"""
    return existing_tools + [
        types.Tool(
            name="find_open_access",
            description="Find free, legal versions of papers",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Paper title"},
                    "doi": {"type": "string", "description": "DOI (optional)"},
                    "arxiv_id": {"type": "string", "description": "arXiv ID (optional)"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="analyze_citations",
            description="Analyze citation network for a paper",
            inputSchema={
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string", "description": "Paper ID, DOI, or arXiv ID"},
                    "depth": {"type": "integer", "default": 2, "description": "Network depth"}
                },
                "required": ["paper_id"]
            }
        ),
        types.Tool(
            name="research_trends",
            description="Analyze research trends in a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                    "years": {"type": "integer", "default": 5, "description": "Years to analyze"}
                },
                "required": ["topic"]
            }
        )
    ]
Key Benefits
1. Massive Open Access Coverage

200M+ papers in Semantic Scholar
~50M with open access PDFs
Continuously updated

2. Rich Metadata

Citation counts and influential citations
Fields of study classification
Author networks
Venue information

3. Advanced Features

Citation network analysis
Research trend detection
Paper recommendations
Author disambiguation

4. Ethical & Legal

All data legally obtained
Respects copyright
No scraping needed

Implementation Timeline
Week 1: Basic S2 client integration
Week 2: Enhanced paper acquisition
Week 3: Citation network features
Week 4: MCP tool integration
Performance Considerations

Rate Limiting: 100 requests/5min (or 10k/day with API key)
Caching: Cache S2 responses for 24-48 hours
Batch Operations: Use bulk endpoints where available
Async Processing: All operations are async-ready

Next Steps

Register for free S2 API key at https://api.semanticscholar.org
Test integration with your existing corpus
Consider adding S2's SPECTER embeddings for better vector search
Implement citation-based paper recommendations

This integration transforms SciTeX-Scholar from a local search tool to a comprehensive research platform with access to millions of papers while remaining completely legal and ethical.

<!-- EOF -->