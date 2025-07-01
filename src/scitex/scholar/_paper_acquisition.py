#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 00:09:45 (ywatanabe)"
# File: ./src/scitex/scholar/_paper_acquisition.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_paper_acquisition.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Enhanced paper acquisition module for automated literature search and download."""

import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import xml.etree.ElementTree as ET
import json
import re
from urllib.parse import quote_plus
import time

from ._semantic_scholar_client import SemanticScholarClient, S2Paper
from ._journal_metrics import JournalMetrics

logger = logging.getLogger(__name__)


class PaperMetadata:
    """Structured metadata for a scientific paper."""
    
    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.authors = kwargs.get('authors', [])
        self.abstract = kwargs.get('abstract', '')
        self.year = kwargs.get('year', '')
        self.doi = kwargs.get('doi', '')
        self.pmid = kwargs.get('pmid', '')
        self.arxiv_id = kwargs.get('arxiv_id', '')
        self.journal = kwargs.get('journal', '')
        self.keywords = kwargs.get('keywords', [])
        self.pdf_url = kwargs.get('pdf_url', '')
        self.source = kwargs.get('source', '')
        self.citation_count = kwargs.get('citation_count', 0)
        self.influential_citation_count = kwargs.get('influential_citation_count', 0)
        self.s2_paper_id = kwargs.get('s2_paper_id', '')
        self.fields_of_study = kwargs.get('fields_of_study', [])
        self.has_open_access = kwargs.get('has_open_access', False)
        self.impact_factor = kwargs.get('impact_factor', None)
        self.journal_quartile = kwargs.get('journal_quartile', None)
        self.journal_rank = kwargs.get('journal_rank', None)
        self.h_index = kwargs.get('h_index', None)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'year': self.year,
            'doi': self.doi,
            'pmid': self.pmid,
            'arxiv_id': self.arxiv_id,
            'journal': self.journal,
            'keywords': self.keywords,
            'pdf_url': self.pdf_url,
            'source': self.source,
            'citation_count': self.citation_count,
            'influential_citation_count': self.influential_citation_count,
            's2_paper_id': self.s2_paper_id,
            'fields_of_study': self.fields_of_study,
            'has_open_access': self.has_open_access,
            'impact_factor': self.impact_factor,
            'journal_quartile': self.journal_quartile,
            'journal_rank': self.journal_rank,
            'h_index': self.h_index
        }


class PaperAcquisition:
    """Enhanced paper acquisition with Semantic Scholar as primary source and AI integration."""
    
    def __init__(self, 
                 download_dir: Optional[Path] = None, 
                 email: Optional[str] = None, 
                 s2_api_key: Optional[str] = None,
                 ai_provider: Optional[str] = None):
        """
        Initialize enhanced paper acquisition system.
        
        Args:
            download_dir: Directory to save downloaded PDFs
            email: Email for API compliance (required for some services)
            s2_api_key: Semantic Scholar API key for higher rate limits
            ai_provider: AI provider for paper analysis ('anthropic', 'openai', 'google', 'perplexity')
        """
        self.download_dir = download_dir or Path("./downloaded_papers")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.email = email or "research@example.com"
        
        # Initialize Semantic Scholar client and journal metrics
        self.s2_client = SemanticScholarClient(api_key=s2_api_key)
        self.journal_metrics = JournalMetrics()
        
        # Initialize AI client if requested
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
        
        # API endpoints
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.crossref_base = "https://api.crossref.org/works"
        self.unpaywall_base = "https://api.unpaywall.org/v2"
        self.biorxiv_base = "https://api.biorxiv.org/details/biorxiv"
        
        # Rate limiting
        self.rate_limits = {
            'pubmed': 0.34,  # ~3 requests/second
            'arxiv': 0.5,    # 2 requests/second
            'crossref': 0.1, # 10 requests/second
            'unpaywall': 0.1,
            'biorxiv': 0.5,
            'semantic_scholar': 0.1  # handled by S2Client
        }
        self.last_request = {}
    
    async def search(self, 
                    query: str,
                    sources: List[str] = None,
                    max_results: int = 20,
                    start_year: Optional[int] = None,
                    end_year: Optional[int] = None,
                    open_access_only: bool = False) -> List[PaperMetadata]:
        """
        Enhanced search with Semantic Scholar as primary source.
        
        Args:
            query: Search query
            sources: List of sources to search (default: semantic_scholar + others)
            max_results: Maximum results per source
            start_year: Filter by start year
            end_year: Filter by end year
            open_access_only: Only return papers with PDFs
            
        Returns:
            List of paper metadata
        """
        # Semantic Scholar is now the primary source
        sources = sources or ['semantic_scholar', 'pubmed', 'arxiv']
        all_results = []
        
        # Search Semantic Scholar first (primary source)
        if 'semantic_scholar' in sources:
            s2_results = await self._search_semantic_scholar(
                query, max_results, start_year, end_year, open_access_only
            )
            all_results.extend(s2_results)
            logger.info(f"Semantic Scholar found: {len(s2_results)} papers")
        
        # Search other sources
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            if 'pubmed' in sources:
                tasks.append(self._search_pubmed(session, query, max_results, start_year, end_year))
            
            if 'arxiv' in sources:
                tasks.append(self._search_arxiv(session, query, max_results))
            
            if 'biorxiv' in sources:
                tasks.append(self._search_biorxiv(session, query, max_results))
            
            # Execute searches in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Search error: {result}")
                    else:
                        all_results.extend(result)
        
        # Remove duplicates based on title similarity and DOI
        unique_results = self._deduplicate_results(all_results)
        
        logger.info(f"Total unique papers found: {len(unique_results)}")
        return unique_results
    
    async def _search_semantic_scholar(self,
                                     query: str,
                                     max_results: int,
                                     start_year: Optional[int],
                                     end_year: Optional[int],
                                     open_access_only: bool) -> List[PaperMetadata]:
        """Search Semantic Scholar - primary source with 200M+ papers."""
        try:
            # Build year filter
            year_filter = None
            if start_year or end_year:
                start = start_year or 1900
                end = end_year or datetime.now().year
                year_filter = f"{start}-{end}"
            
            async with self.s2_client as client:
                s2_papers = await client.search_papers(
                    query=query,
                    limit=max_results,
                    year_filter=year_filter,
                    open_access_only=open_access_only
                )
                
            # Convert S2Paper to PaperMetadata
            papers = []
            for s2_paper in s2_papers:
                papers.append(self._s2_to_metadata(s2_paper))
                
            return papers
            
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
            return []
    
    def _s2_to_metadata(self, s2_paper: S2Paper) -> PaperMetadata:
        """Convert S2Paper to PaperMetadata with journal metrics."""
        # Get journal metrics if venue is available
        journal_metrics = {}
        if s2_paper.venue:
            journal_metrics = self.journal_metrics.lookup_journal_metrics(s2_paper.venue)
        
        return PaperMetadata(
            title=s2_paper.title,
            authors=s2_paper.author_names,
            abstract=s2_paper.abstract or '',
            year=str(s2_paper.year) if s2_paper.year else '',
            doi=s2_paper.doi or '',
            pmid=s2_paper.pmid or '',
            arxiv_id=s2_paper.arxivId or '',
            journal=s2_paper.venue or '',
            keywords=s2_paper.fieldsOfStudy,
            pdf_url=s2_paper.pdf_url or '',
            source='semantic_scholar',
            citation_count=s2_paper.citationCount,
            influential_citation_count=s2_paper.influentialCitationCount,
            s2_paper_id=s2_paper.paperId,
            fields_of_study=[f['category'] for f in s2_paper.s2FieldsOfStudy],
            has_open_access=s2_paper.has_open_access,
            impact_factor=journal_metrics.get('impact_factor'),
            journal_quartile=journal_metrics.get('quartile'),
            journal_rank=journal_metrics.get('rank'),
            h_index=journal_metrics.get('h_index')
        )
    
    async def _search_pubmed(self, 
                           session: aiohttp.ClientSession,
                           query: str,
                           max_results: int,
                           start_year: Optional[int],
                           end_year: Optional[int]) -> List[PaperMetadata]:
        """Search PubMed/PMC."""
        await self._rate_limit('pubmed')
        
        # Build query with date filters
        date_filter = ""
        if start_year or end_year:
            start = start_year or 1900
            end = end_year or datetime.now().year
            date_filter = f" AND {start}:{end}[pdat]"
        
        search_query = quote_plus(query + date_filter)
        
        # Search for IDs
        search_url = f"{self.pubmed_base}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': search_query,
            'retmax': max_results,
            'retmode': 'json',
            'email': self.email
        }
        
        async with session.get(search_url, params=params) as resp:
            data = await resp.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
        
        if not pmids:
            return []
        
        # Fetch details
        await self._rate_limit('pubmed')
        
        fetch_url = f"{self.pubmed_base}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email
        }
        
        async with session.get(fetch_url, params=params) as resp:
            xml_data = await resp.text()
        
        # Parse results
        papers = []
        root = ET.fromstring(xml_data)
        
        for article in root.findall('.//PubmedArticle'):
            try:
                # Extract metadata
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None else ''
                
                # Authors
                authors = []
                for author in article.findall('.//Author'):
                    lastname = author.find('LastName')
                    forename = author.find('ForeName')
                    if lastname is not None:
                        name = lastname.text
                        if forename is not None:
                            name = f"{forename.text} {name}"
                        authors.append(name)
                
                # Abstract
                abstract_texts = []
                for abstract in article.findall('.//AbstractText'):
                    if abstract.text:
                        abstract_texts.append(abstract.text)
                abstract = ' '.join(abstract_texts)
                
                # Year
                year_elem = article.find('.//PubDate/Year')
                year = year_elem.text if year_elem is not None else ''
                
                # Journal
                journal_elem = article.find('.//Journal/Title')
                journal = journal_elem.text if journal_elem is not None else ''
                
                # PMID
                pmid_elem = article.find('.//PMID')
                pmid = pmid_elem.text if pmid_elem is not None else ''
                
                # DOI
                doi = ''
                for id_elem in article.findall('.//ArticleId'):
                    if id_elem.get('IdType') == 'doi':
                        doi = id_elem.text
                        break
                
                # Keywords
                keywords = []
                for kw in article.findall('.//Keyword'):
                    if kw.text:
                        keywords.append(kw.text)
                
                papers.append(PaperMetadata(
                    title=title,
                    authors=authors[:10],  # Limit authors
                    abstract=abstract,
                    year=year,
                    doi=doi,
                    pmid=pmid,
                    journal=journal,
                    keywords=keywords,
                    source='pubmed'
                ))
                
            except Exception as e:
                logger.error(f"Error parsing PubMed article: {e}")
                continue
        
        return papers
    
    async def _search_arxiv(self,
                          session: aiohttp.ClientSession,
                          query: str,
                          max_results: int) -> List[PaperMetadata]:
        """Search arXiv."""
        await self._rate_limit('arxiv')
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        async with session.get(self.arxiv_base, params=params) as resp:
            xml_data = await resp.text()
        
        # Parse results
        papers = []
        root = ET.fromstring(xml_data)
        
        # Handle namespaces
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            try:
                # Title
                title_elem = entry.find('atom:title', ns)
                title = title_elem.text.strip() if title_elem is not None else ''
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                
                # Abstract
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text.strip() if summary_elem is not None else ''
                
                # Published date
                published_elem = entry.find('atom:published', ns)
                year = ''
                if published_elem is not None:
                    year = published_elem.text[:4]
                
                # arXiv ID
                id_elem = entry.find('atom:id', ns)
                arxiv_id = ''
                pdf_url = ''
                if id_elem is not None:
                    arxiv_id = id_elem.text.split('/')[-1]
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                # Categories as keywords
                keywords = []
                for cat in entry.findall('atom:category', ns):
                    term = cat.get('term')
                    if term:
                        keywords.append(term)
                
                papers.append(PaperMetadata(
                    title=title,
                    authors=authors[:10],
                    abstract=abstract,
                    year=year,
                    arxiv_id=arxiv_id,
                    keywords=keywords,
                    pdf_url=pdf_url,
                    source='arxiv'
                ))
                
            except Exception as e:
                logger.error(f"Error parsing arXiv entry: {e}")
                continue
        
        return papers
    
    async def _search_biorxiv(self,
                            session: aiohttp.ClientSession,
                            query: str,
                            max_results: int) -> List[PaperMetadata]:
        """Search bioRxiv."""
        await self._rate_limit('biorxiv')
        
        # bioRxiv API is limited, using basic search
        papers = []
        logger.info("bioRxiv search is simplified in this implementation")
        
        return papers
    
    async def _rate_limit(self, source: str):
        """Implement rate limiting for API calls."""
        if source in self.last_request:
            elapsed = time.time() - self.last_request[source]
            wait_time = self.rate_limits.get(source, 0.1) - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.last_request[source] = time.time()
    
    def _deduplicate_results(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        """Enhanced deduplication using DOI, title, and arXiv ID."""
        unique_papers = []
        seen_dois = set()
        seen_arxiv_ids = set()
        seen_titles = set()
        
        for paper in papers:
            is_duplicate = False
            
            # Check DOI first (most reliable)
            if paper.doi and paper.doi in seen_dois:
                is_duplicate = True
            elif paper.doi:
                seen_dois.add(paper.doi)
            
            # Check arXiv ID
            if not is_duplicate and paper.arxiv_id and paper.arxiv_id in seen_arxiv_ids:
                is_duplicate = True
            elif paper.arxiv_id:
                seen_arxiv_ids.add(paper.arxiv_id)
            
            # Check title (fallback)
            if not is_duplicate:
                normalized = re.sub(r'[^\w\s]', '', paper.title.lower())
                normalized = ' '.join(normalized.split())
                
                if normalized in seen_titles:
                    is_duplicate = True
                else:
                    seen_titles.add(normalized)
            
            if not is_duplicate:
                unique_papers.append(paper)
            else:
                logger.debug(f"Removed duplicate: {paper.title[:60]}...")
        
        # Sort by source priority (Semantic Scholar first) and citation count
        def sort_key(p):
            source_priority = {
                'semantic_scholar': 0,
                'pubmed': 1,
                'arxiv': 2,
                'biorxiv': 3
            }
            return (source_priority.get(p.source, 99), -p.citation_count)
        
        unique_papers.sort(key=sort_key)
        return unique_papers
    
    # AI-Enhanced Features
    async def analyze_paper_with_ai(self, paper: PaperMetadata) -> Dict[str, str]:
        """Generate AI analysis of a paper."""
        if not self.ai_client:
            return {"error": "AI client not initialized"}
        
        try:
            # Create analysis prompt
            prompt = f"""Analyze this research paper:

Title: {paper.title}
Authors: {', '.join(paper.authors[:5])}
Journal: {paper.journal}
Year: {paper.year}
Citations: {paper.citation_count}

Abstract: {paper.abstract[:1000]}...

Please provide:
1. Key contributions (2-3 bullet points)
2. Methods used
3. Significance in the field
4. Potential limitations
5. Relevance for literature review

Keep response concise and academic."""
            
            response = await self.ai_client.generate_async(prompt)
            
            return {
                "analysis": response,
                "paper_title": paper.title,
                "analyzed_by": self.ai_client.__class__.__name__
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def generate_research_summary(self, papers: List[PaperMetadata], topic: str) -> str:
        """Generate AI summary of research papers on a topic."""
        if not self.ai_client:
            return "AI client not initialized for summarization"
        
        try:
            # Prepare papers summary
            papers_text = ""
            for i, paper in enumerate(papers[:10], 1):  # Limit to top 10 papers
                papers_text += f"\n{i}. {paper.title}\n"
                papers_text += f"   Authors: {', '.join(paper.authors[:3])}\n"
                papers_text += f"   Journal: {paper.journal} ({paper.year})\n"
                papers_text += f"   Citations: {paper.citation_count}\n"
                if paper.abstract:
                    papers_text += f"   Abstract: {paper.abstract[:200]}...\n"
                papers_text += "\n"
            
            prompt = f"""Provide a comprehensive literature review summary for the topic: "{topic}"

Based on these {len(papers)} research papers:
{papers_text}

Please provide:
1. Overview of the research landscape
2. Key methodological approaches
3. Major findings and trends
4. Research gaps identified
5. Future research directions
6. Most influential papers (by citation count)

Format as an academic literature review section."""
            
            summary = await self.ai_client.generate_async(prompt)
            return summary
            
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            return f"AI summarization failed: {str(e)}"
    
    async def find_research_gaps(self, papers: List[PaperMetadata], topic: str) -> List[str]:
        """Use AI to identify research gaps from paper collection."""
        if not self.ai_client:
            return ["AI client not initialized for gap analysis"]
        
        try:
            # Create gap analysis prompt
            methodologies = set()
            recent_papers = []
            
            for paper in papers:
                if paper.year and int(paper.year) >= 2020:
                    recent_papers.append(paper)
                methodologies.update(paper.keywords)
            
            prompt = f"""Analyze research gaps in: "{topic}"

Recent papers ({len(recent_papers)} from 2020+):
{chr(10).join([f"- {p.title} ({p.year})" for p in recent_papers[:15]])}

Common methodologies: {', '.join(list(methodologies)[:10])}

Identify 5-7 specific research gaps or opportunities in this field. Focus on:
1. Methodological limitations
2. Understudied populations/contexts
3. Technical challenges not yet solved
4. Interdisciplinary opportunities
5. Practical applications needed

Return as a numbered list of specific, actionable research gaps."""
            
            gaps_response = await self.ai_client.generate_async(prompt)
            
            # Parse response into list
            gaps = []
            for line in gaps_response.split('\n'):
                if re.match(r'^\d+\.', line.strip()):
                    gaps.append(line.strip())
            
            return gaps if gaps else [gaps_response]
            
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return [f"Gap analysis failed: {str(e)}"]
    
    # Enhanced bibliography generation with AI integration
    def generate_enhanced_bibliography(self, 
                                     papers: List[PaperMetadata],
                                     include_metrics: bool = True,
                                     output_file: Optional[str] = None) -> str:
        """
        Generate enhanced BibTeX bibliography with journal metrics.
        
        Args:
            papers: List of papers to include
            include_metrics: Whether to include impact factors and rankings
            output_file: Optional file path to save the bibliography
            
        Returns:
            BibTeX content as string
        """
        from ._journal_metrics import enhance_bibliography_with_metrics
        
        bib_content = enhance_bibliography_with_metrics(papers, include_metrics)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(bib_content)
            logger.info(f"Enhanced bibliography saved to: {output_file}")
        
        return bib_content


# Enhanced convenience functions with AI support
async def search_papers_with_ai(query: str, ai_provider: str = 'anthropic', **kwargs) -> List[PaperMetadata]:
    """Quick search function with AI analysis."""
    acquisition = PaperAcquisition(ai_provider=ai_provider)
    return await acquisition.search(query, **kwargs)


async def full_literature_review(topic: str, 
                                ai_provider: str = 'anthropic',
                                max_papers: int = 50) -> Dict[str, Any]:
    """Complete AI-enhanced literature review."""
    acquisition = PaperAcquisition(ai_provider=ai_provider)
    
    # Search papers
    papers = await acquisition.search(topic, max_results=max_papers)
    
    # Generate AI analysis
    summary = await acquisition.generate_research_summary(papers, topic)
    gaps = await acquisition.find_research_gaps(papers, topic)
    
    # Generate bibliography
    bibliography = acquisition.generate_enhanced_bibliography(papers)
    
    return {
        'topic': topic,
        'papers_found': len(papers),
        'papers': papers,
        'ai_summary': summary,
        'research_gaps': gaps,
        'bibliography': bibliography,
        'ai_provider': ai_provider
    }


# EOF