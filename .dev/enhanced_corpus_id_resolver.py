#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 09:15:00 (ywatanabe)"
# File: ./.dev/enhanced_corpus_id_resolver.py
# ----------------------------------------
"""
Enhanced CorpusId to DOI resolution with multiple strategies.

This script uses multiple approaches:
1. Semantic Scholar API (with proper rate limiting)
2. CrossRef fuzzy matching
3. arXiv search
4. Direct web scraping of Semantic Scholar pages
"""

import requests
import time
from typing import Optional, Dict, Any, List
import json
import re
from urllib.parse import quote

from scitex.logging import getLogger
logger = getLogger(__name__)

class EnhancedCorpusIdResolver:
    """Enhanced resolver with multiple DOI resolution strategies."""
    
    def __init__(self, email: str = "research@example.com"):
        self.email = email
        self.ss_base_url = "https://api.semanticscholar.org/graph/v1"
        self.crossref_base_url = "https://api.crossref.org/works"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"SciTeX/1.0 (mailto:{self.email})"
        })
    
    def resolve_corpus_id_with_retries(self, corpus_id: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Resolve CorpusId with exponential backoff."""
        
        # Clean the corpus_id
        if "CorpusId:" in corpus_id:
            corpus_id = corpus_id.split("CorpusId:")[-1]
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries} for CorpusId: {corpus_id}")
                
                url = f"{self.ss_base_url}/paper/CorpusId:{corpus_id}"
                params = {
                    "fields": "title,year,externalIds,authors,abstract,venue,citationCount,url"
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully retrieved data for CorpusId: {corpus_id}")
                    
                    # Extract comprehensive information
                    external_ids = data.get("externalIds", {})
                    doi = external_ids.get("DOI")
                    
                    authors = []
                    for author in data.get("authors", []):
                        if author.get("name"):
                            authors.append(author["name"])
                    
                    result = {
                        "corpus_id": corpus_id,
                        "doi": doi,
                        "title": data.get("title"),
                        "year": data.get("year"),
                        "journal": data.get("venue"),
                        "authors": authors,
                        "abstract": data.get("abstract"),
                        "citation_count": data.get("citationCount"),
                        "external_ids": external_ids,
                        "semantic_scholar_url": data.get("url"),
                        "resolution_method": "semantic_scholar_api"
                    }
                    
                    if doi:
                        logger.info(f"Found DOI via Semantic Scholar: {doi}")
                    else:
                        logger.warning(f"No DOI in Semantic Scholar for CorpusId: {corpus_id}")
                        # Log other available external IDs
                        for id_type, id_value in external_ids.items():
                            logger.info(f"  {id_type}: {id_value}")
                    
                    return result
                    
                elif response.status_code == 429:
                    wait_time = 2 ** attempt * 5  # Exponential backoff: 5, 10, 20 seconds
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                elif response.status_code == 404:
                    logger.warning(f"CorpusId not found: {corpus_id}")
                    return None
                    
                else:
                    logger.error(f"HTTP error {response.status_code}: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        logger.error(f"All attempts failed for CorpusId: {corpus_id}")
        return None
    
    def search_crossref(self, title: str, authors: List[str], year: int) -> Optional[str]:
        """Search CrossRef for DOI using title and metadata."""
        logger.info(f"Searching CrossRef for: {title}")
        
        try:
            # Construct search query
            query_parts = [title]
            if authors:
                # Add first author to query
                query_parts.append(authors[0])
            
            query = " ".join(query_parts)
            
            url = f"{self.crossref_base_url}"
            params = {
                "query": query,
                "rows": 10,
                "sort": "score",
                "order": "desc"
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("message", {}).get("items", [])
            
            for item in items:
                item_title = " ".join(item.get("title", []))
                item_year = None
                
                # Extract year from published date
                published = item.get("published-print") or item.get("published-online")
                if published and "date-parts" in published:
                    try:
                        item_year = published["date-parts"][0][0]
                    except (IndexError, TypeError):
                        pass
                
                # Check title similarity and year match
                if (self._title_similarity(title, item_title) > 0.7 and
                    item_year and abs(item_year - year) <= 1):
                    
                    doi = item.get("DOI")
                    if doi:
                        logger.info(f"Found DOI via CrossRef: {doi}")
                        return doi
            
            logger.warning("No matching DOI found in CrossRef")
            return None
            
        except Exception as e:
            logger.error(f"CrossRef search error: {e}")
            return None
    
    def search_arxiv(self, title: str, authors: List[str]) -> Optional[str]:
        """Search arXiv for papers that might have DOIs."""
        logger.info(f"Searching arXiv for: {title}")
        
        try:
            # arXiv API search
            base_url = "http://export.arxiv.org/api/query"
            
            # Clean title for search
            search_title = re.sub(r'[^\w\s-]', ' ', title).strip()
            search_terms = search_title.split()[:10]  # First 10 words
            
            query = f'ti:"{" ".join(search_terms[:5])}"'
            if authors:
                author_query = authors[0].split()[-1]  # Last name
                query += f' AND au:"{author_query}"'
            
            params = {
                "search_query": query,
                "start": 0,
                "max_results": 10,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response (simplified)
            content = response.text
            
            # Look for entries that might match
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                arxiv_title = entry.find(".//{http://www.w3.org/2005/Atom}title")
                if arxiv_title is not None:
                    arxiv_title_text = arxiv_title.text.strip()
                    
                    if self._title_similarity(title, arxiv_title_text) > 0.8:
                        # Get arXiv ID
                        arxiv_id = entry.find(".//{http://www.w3.org/2005/Atom}id")
                        if arxiv_id is not None:
                            arxiv_url = arxiv_id.text
                            logger.info(f"Found potential arXiv match: {arxiv_url}")
                            
                            # For now, return the arXiv URL as a potential identifier
                            # Could be enhanced to check if this arXiv paper has a DOI
                            return f"arXiv:{arxiv_url.split('/')[-1]}"
            
            return None
            
        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return None
    
    def scrape_semantic_scholar_page(self, corpus_id: str) -> Optional[Dict[str, Any]]:
        """Fallback: scrape the Semantic Scholar web page directly."""
        logger.info(f"Attempting web scraping for CorpusId: {corpus_id}")
        
        try:
            # Clean corpus_id
            if "CorpusId:" in corpus_id:
                corpus_id = corpus_id.split("CorpusId:")[-1]
            
            # Try the web page URL
            web_url = f"https://www.semanticscholar.org/paper/{corpus_id}"
            
            # Use a browser-like user agent
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(web_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                content = response.text
                
                # Look for DOI in the page content
                doi_patterns = [
                    r'doi\.org/([^"\'<>\s]+)',
                    r'"doi"\s*:\s*"([^"]+)"',
                    r'DOI:\s*([^<>\s]+)',
                ]
                
                for pattern in doi_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match and len(match) > 5:  # Basic DOI validation
                            logger.info(f"Found DOI via web scraping: {match}")
                            return {"doi": match, "method": "web_scraping"}
                
                logger.info("No DOI found in web page content")
                return None
            else:
                logger.error(f"Web scraping failed with status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return None
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity using word overlap."""
        # Normalize titles
        t1 = re.sub(r'[^\w\s]', ' ', title1.lower()).strip()
        t2 = re.sub(r'[^\w\s]', ' ', title2.lower()).strip() 
        
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def comprehensive_resolve(self, corpus_id: str, title: str, authors: List[str], year: int) -> Dict[str, Any]:
        """Try all resolution methods in sequence."""
        
        result = {
            "corpus_id": corpus_id,
            "title": title,
            "authors": authors,
            "year": year,
            "doi": None,
            "resolution_method": None,
            "attempts": []
        }
        
        # Method 1: Semantic Scholar API
        logger.info("=== Method 1: Semantic Scholar API ===")
        ss_result = self.resolve_corpus_id_with_retries(corpus_id)
        result["attempts"].append("semantic_scholar_api")
        
        if ss_result and ss_result.get("doi"):
            result.update(ss_result)
            return result
        elif ss_result:
            # Update with non-DOI metadata
            result.update({k: v for k, v in ss_result.items() if k not in result or not result[k]})
        
        # Method 2: CrossRef search
        logger.info("=== Method 2: CrossRef Search ===")
        crossref_doi = self.search_crossref(title, authors, year)
        result["attempts"].append("crossref_search")
        
        if crossref_doi:
            result["doi"] = crossref_doi
            result["resolution_method"] = "crossref"
            return result
        
        # Method 3: arXiv search
        logger.info("=== Method 3: arXiv Search ===")
        arxiv_result = self.search_arxiv(title, authors)
        result["attempts"].append("arxiv_search")
        
        if arxiv_result:
            result["arxiv_id"] = arxiv_result
            # Note: arXiv doesn't give us DOI directly, but it's useful info
        
        # Method 4: Web scraping
        logger.info("=== Method 4: Web Scraping ===")
        scrape_result = self.scrape_semantic_scholar_page(corpus_id)
        result["attempts"].append("web_scraping")
        
        if scrape_result and scrape_result.get("doi"):
            result["doi"] = scrape_result["doi"]
            result["resolution_method"] = "web_scraping"
            return result
        
        logger.warning(f"All resolution methods failed for CorpusId: {corpus_id}")
        return result


def main():
    """Test enhanced resolution on target papers."""
    
    resolver = EnhancedCorpusIdResolver()
    
    target_papers = [
        {
            "corpus_id": "263829747",
            "title": "Statistical Inference for Modulation Index in Phase-Amplitude Coupling",
            "authors": ["Marco Pinto-Orellana", "H. Ombao", "Beth A. Lopour"],
            "year": 2023
        },
        {
            "corpus_id": "263786486", 
            "title": "Complex network modelling of EEG band coupling in dyslexia",
            "authors": ["N. Gallego-Molina"],
            "year": 2021
        }
    ]
    
    results = []
    
    for paper in target_papers:
        logger.info(f"\n{'='*80}")
        logger.info(f"PROCESSING: {paper['title']}")
        logger.info(f"CorpusId: {paper['corpus_id']}")
        logger.info(f"{'='*80}")
        
        result = resolver.comprehensive_resolve(
            paper['corpus_id'],
            paper['title'], 
            paper['authors'], 
            paper['year']
        )
        
        results.append(result)
        
        # Add delay between papers to be respectful
        time.sleep(2)
    
    # Final summary
    logger.info(f"\n{'='*80}")
    logger.info("FINAL RESOLUTION SUMMARY")
    logger.info(f"{'='*80}")
    
    success_count = 0
    for result in results:
        corpus_id = result['corpus_id']
        doi = result.get('doi')
        method = result.get('resolution_method')
        
        if doi:
            success_count += 1
            logger.info(f"✓ CorpusId {corpus_id}: SUCCESS")
            logger.info(f"  DOI: {doi}")
            logger.info(f"  Method: {method}")
        else:
            logger.info(f"✗ CorpusId {corpus_id}: FAILED")
            logger.info(f"  Attempts: {', '.join(result['attempts'])}")
        
        # Show additional info if available
        if result.get('arxiv_id'):
            logger.info(f"  arXiv: {result['arxiv_id']}")
        if result.get('journal'):
            logger.info(f"  Journal: {result['journal']}")
        
        logger.info("")
    
    logger.info(f"Success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    # Save detailed results
    output_file = "/home/ywatanabe/proj/SciTeX-Code/.dev/enhanced_corpus_id_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Detailed results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    main()