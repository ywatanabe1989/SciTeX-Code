#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:10:00"
# Author: Claude
# Filename: _web_sources.py

"""
Web source search functions for scientific papers.
"""

import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import logging
from urllib.parse import quote

from ._paper import Paper


logger = logging.getLogger(__name__)


async def search_pubmed(
    query: str,
    max_results: int = 10,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[Paper]:
    """Search PubMed for papers.
    
    Parameters
    ----------
    query : str
        Search query
    max_results : int
        Maximum number of results
    session : aiohttp.ClientSession, optional
        Aiohttp session for connection pooling
    
    Returns
    -------
    List[Paper]
        List of papers from PubMed
    """
    papers = []
    close_session = False
    
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        # Search for PMIDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        
        async with session.get(search_url, params=search_params) as response:
            data = await response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
        
        if not pmids:
            logger.info(f"No results found for query: {query}")
            return papers
        
        # Fetch details for PMIDs
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        
        async with session.get(fetch_url, params=fetch_params) as response:
            xml_data = await response.text()
        
        # Parse XML
        root = ET.fromstring(xml_data)
        
        for article in root.findall(".//PubmedArticle"):
            try:
                # Extract metadata
                medline = article.find(".//MedlineCitation")
                if medline is None:
                    continue
                
                # Title
                title_elem = medline.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else "No title"
                
                # Authors
                authors = []
                for author in medline.findall(".//Author"):
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None:
                        name = last_name.text
                        if fore_name is not None:
                            name = f"{fore_name.text} {name}"
                        authors.append(name)
                
                # Abstract
                abstract_parts = []
                for abstract_elem in medline.findall(".//AbstractText"):
                    if abstract_elem.text:
                        abstract_parts.append(abstract_elem.text)
                abstract = " ".join(abstract_parts) if abstract_parts else "No abstract available"
                
                # Year
                year = None
                pub_date = medline.find(".//PubDate")
                if pub_date is not None:
                    year_elem = pub_date.find("Year")
                    if year_elem is not None:
                        year = int(year_elem.text)
                
                # Journal
                journal_elem = medline.find(".//Journal/Title")
                journal = journal_elem.text if journal_elem is not None else None
                
                # PMID
                pmid_elem = medline.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else None
                
                # DOI
                doi = None
                for id_elem in article.findall(".//ArticleId"):
                    if id_elem.get("IdType") == "doi":
                        doi = id_elem.text
                        break
                
                # Keywords
                keywords = []
                for kw in medline.findall(".//Keyword"):
                    if kw.text:
                        keywords.append(kw.text)
                
                # Create Paper object
                paper = Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    source="pubmed",
                    year=year,
                    doi=doi,
                    pmid=pmid,
                    journal=journal,
                    keywords=keywords,
                )
                
                papers.append(paper)
                
            except Exception as e:
                logger.error(f"Error parsing PubMed article: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error searching PubMed: {e}")
    finally:
        if close_session:
            await session.close()
    
    return papers


async def search_arxiv(
    query: str,
    max_results: int = 10,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[Paper]:
    """Search arXiv for papers.
    
    Parameters
    ----------
    query : str
        Search query
    max_results : int
        Maximum number of results
    session : aiohttp.ClientSession, optional
        Aiohttp session for connection pooling
    
    Returns
    -------
    List[Paper]
        List of papers from arXiv
    """
    papers = []
    close_session = False
    
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        # arXiv API URL
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        
        async with session.get(url, params=params) as response:
            xml_data = await response.text()
        
        # Parse XML with namespace
        root = ET.fromstring(xml_data)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        
        for entry in root.findall("atom:entry", namespace):
            try:
                # Title
                title_elem = entry.find("atom:title", namespace)
                title = title_elem.text.strip() if title_elem is not None else "No title"
                
                # Authors
                authors = []
                for author_elem in entry.findall("atom:author", namespace):
                    name_elem = author_elem.find("atom:name", namespace)
                    if name_elem is not None:
                        authors.append(name_elem.text.strip())
                
                # Abstract
                summary_elem = entry.find("atom:summary", namespace)
                abstract = summary_elem.text.strip() if summary_elem is not None else "No abstract"
                
                # arXiv ID
                id_elem = entry.find("atom:id", namespace)
                arxiv_id = None
                if id_elem is not None:
                    # Extract ID from URL
                    match = re.search(r"arxiv.org/abs/(.+)", id_elem.text)
                    if match:
                        arxiv_id = match.group(1)
                
                # Published date (year)
                year = None
                published_elem = entry.find("atom:published", namespace)
                if published_elem is not None:
                    try:
                        year = int(published_elem.text[:4])
                    except:
                        pass
                
                # DOI (if available)
                doi = None
                for link_elem in entry.findall("atom:link", namespace):
                    if link_elem.get("title") == "doi":
                        doi = link_elem.get("href", "").replace("http://dx.doi.org/", "")
                        break
                
                # Categories as keywords
                keywords = []
                for cat_elem in entry.findall("atom:category", namespace):
                    term = cat_elem.get("term")
                    if term:
                        keywords.append(term)
                
                # PDF link
                pdf_url = None
                for link_elem in entry.findall("atom:link", namespace):
                    if link_elem.get("type") == "application/pdf":
                        pdf_url = link_elem.get("href")
                        break
                
                # Create Paper object
                paper = Paper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    source="arxiv",
                    year=year,
                    doi=doi,
                    arxiv_id=arxiv_id,
                    keywords=keywords,
                    metadata={"pdf_url": pdf_url} if pdf_url else {},
                )
                
                papers.append(paper)
                
            except Exception as e:
                logger.error(f"Error parsing arXiv entry: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Error searching arXiv: {e}")
    finally:
        if close_session:
            await session.close()
    
    return papers


async def search_semantic_scholar(
    query: str,
    max_results: int = 10,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[Paper]:
    """Search Semantic Scholar for papers.
    
    Parameters
    ----------
    query : str
        Search query
    max_results : int
        Maximum number of results
    session : aiohttp.ClientSession, optional
        Aiohttp session for connection pooling
    
    Returns
    -------
    List[Paper]
        List of papers from Semantic Scholar
    """
    papers = []
    close_session = False
    
    if session is None:
        session = aiohttp.ClientSession()
        close_session = True
    
    try:
        # Semantic Scholar API
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,abstract,authors,year,doi,arxivId,publicationTypes,journal",
        }
        
        headers = {
            "User-Agent": "SciTeX Scholar Library",
        }
        
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                for item in data.get("data", []):
                    try:
                        # Extract authors
                        authors = []
                        for author_data in item.get("authors", []):
                            name = author_data.get("name")
                            if name:
                                authors.append(name)
                        
                        # Create Paper object
                        paper = Paper(
                            title=item.get("title", "No title"),
                            authors=authors,
                            abstract=item.get("abstract", "No abstract available"),
                            source="semantic_scholar",
                            year=item.get("year"),
                            doi=item.get("doi"),
                            arxiv_id=item.get("arxivId"),
                            journal=item.get("journal", {}).get("name"),
                            keywords=item.get("publicationTypes", []),
                            metadata={"ss_id": item.get("paperId")},
                        )
                        
                        papers.append(paper)
                        
                    except Exception as e:
                        logger.error(f"Error parsing Semantic Scholar paper: {e}")
                        continue
            else:
                logger.warning(f"Semantic Scholar API returned status {response.status}")
    
    except Exception as e:
        logger.error(f"Error searching Semantic Scholar: {e}")
    finally:
        if close_session:
            await session.close()
    
    return papers


async def search_all_sources(
    query: str,
    max_results_per_source: int = 5,
    sources: Optional[List[str]] = None,
) -> Dict[str, List[Paper]]:
    """Search multiple sources concurrently.
    
    Parameters
    ----------
    query : str
        Search query
    max_results_per_source : int
        Maximum results per source
    sources : List[str], optional
        Sources to search (default: all available)
    
    Returns
    -------
    Dict[str, List[Paper]]
        Dictionary mapping source names to paper lists
    """
    if sources is None:
        sources = ["pubmed", "arxiv", "semantic_scholar"]
    
    # Create session for connection pooling
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        if "pubmed" in sources:
            tasks.append(("pubmed", search_pubmed(query, max_results_per_source, session)))
        
        if "arxiv" in sources:
            tasks.append(("arxiv", search_arxiv(query, max_results_per_source, session)))
        
        if "semantic_scholar" in sources:
            tasks.append(("semantic_scholar", search_semantic_scholar(query, max_results_per_source, session)))
        
        # Run searches concurrently
        results = {}
        for source_name, task in tasks:
            try:
                papers = await task
                results[source_name] = papers
                logger.info(f"Found {len(papers)} papers from {source_name}")
            except Exception as e:
                logger.error(f"Error searching {source_name}: {e}")
                results[source_name] = []
    
    return results


# Example usage
if __name__ == "__main__":
    async def main():
        # Search individual sources
        print("Searching PubMed...")
        pubmed_papers = await search_pubmed("machine learning cancer", max_results=3)
        for paper in pubmed_papers:
            print(f"- {paper.title}")
        
        print("\nSearching arXiv...")
        arxiv_papers = await search_arxiv("neural networks", max_results=3)
        for paper in arxiv_papers:
            print(f"- {paper.title}")
        
        print("\nSearching all sources...")
        all_results = await search_all_sources("deep learning", max_results_per_source=2)
        for source, papers in all_results.items():
            print(f"\n{source}: {len(papers)} papers")
            for paper in papers:
                print(f"  - {paper.title}")