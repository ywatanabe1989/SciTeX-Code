#!/usr/bin/env python3
"""
Comprehensive DOI Resolution with Proper Rate Limiting
Fix the 50% coverage issue with enhanced strategies and proper rate limiting
"""

import sys
import json
import re
import asyncio
import time
import random
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi.utils import URLDOIExtractor, PubMedConverter, TextNormalizer
from scitex.scholar.doi._DOIResolver import DOIResolver
from scitex.scholar.config import ScholarConfig

class ComprehensiveDOIResolver:
    """Comprehensive DOI resolver with proper rate limiting and multiple strategies"""
    
    def __init__(self):
        self.url_extractor = URLDOIExtractor()
        self.pubmed_converter = PubMedConverter(email="research@scitex.ai")
        self.text_normalizer = TextNormalizer()
        self.doi_resolver = DOIResolver(project="pac")
        
        # Rate limiting state
        self.semantic_scholar_delay = 2.0  # Start with 2 seconds
        self.crossref_delay = 1.0
        self.last_api_call = {}
        
    async def rate_limited_request(self, api_name: str, request_func, *args, **kwargs):
        """Make rate-limited API request with exponential backoff"""
        
        # Wait for rate limit
        now = time.time()
        if api_name in self.last_api_call:
            elapsed = now - self.last_api_call[api_name]
            delay = self.semantic_scholar_delay if 'semantic' in api_name else self.crossref_delay
            
            if elapsed < delay:
                wait_time = delay - elapsed + random.uniform(0.1, 0.5)  # Add jitter
                print(f"    ⏳ Rate limiting: waiting {wait_time:.1f}s for {api_name}")
                await asyncio.sleep(wait_time)
        
        # Make request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.last_api_call[api_name] = time.time()
                result = await asyncio.to_thread(request_func, *args, **kwargs)
                
                # Reset delay on success
                if 'semantic' in api_name:
                    self.semantic_scholar_delay = max(1.0, self.semantic_scholar_delay * 0.9)
                
                return result
                
            except Exception as e:
                if '429' in str(e) or 'rate limit' in str(e).lower():
                    # Exponential backoff for rate limits
                    if 'semantic' in api_name:
                        self.semantic_scholar_delay = min(10.0, self.semantic_scholar_delay * 2)
                    
                    wait_time = self.semantic_scholar_delay * (2 ** attempt) + random.uniform(1, 3)
                    print(f"    ⚠️  Rate limited on {api_name}, attempt {attempt+1}/{max_retries}, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    
                    if attempt == max_retries - 1:
                        print(f"    ❌ {api_name} failed after {max_retries} attempts: {e}")
                        return None
                else:
                    print(f"    ❌ {api_name} error: {e}")
                    return None
        
        return None
    
    def extract_corpus_id(self, url: str) -> str:
        """Extract CorpusID from URL"""
        if not url:
            return None
        
        match = re.search(r'CorpusId:(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def semantic_scholar_request(self, corpus_id: str):
        """Make Semantic Scholar API request"""
        import requests
        
        paper_id = f"CorpusId:{corpus_id}"
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        
        params = {
            'fields': 'externalIds,title,authors,year,venue,abstract'
        }
        
        headers = {
            'User-Agent': 'SciTeX Scholar (research@scitex.ai)',
            'X-API-KEY': ''  # Add API key if available
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        data = response.json()
        doi = data.get('externalIds', {}).get('DOI')
        
        if doi:
            print(f"    📄 CorpusID {corpus_id} → DOI: {doi}")
            return doi
        else:
            raise Exception(f"No DOI found for CorpusID {corpus_id}")
    
    def crossref_title_search(self, title: str, year: str = None):
        """Search CrossRef by title"""
        import requests
        
        clean_title = self.text_normalizer.normalize_text(title)
        clean_title = re.sub(r'[^\w\s-]', ' ', clean_title)
        clean_title = ' '.join(clean_title.split())
        
        if len(clean_title) > 100:
            clean_title = clean_title[:100]
        
        url = "https://api.crossref.org/works"
        params = {
            'query.title': clean_title,
            'rows': 3,
            'select': 'DOI,title,published-print,published-online'
        }
        
        if year and year.isdigit():
            params['filter'] = f'published:{year}'
        
        headers = {
            'User-Agent': 'SciTeX Scholar (research@scitex.ai)',
            'mailto': 'research@scitex.ai'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        data = response.json()
        items = data.get('message', {}).get('items', [])
        
        for item in items:
            item_title = item.get('title', [''])[0].lower()
            search_title = clean_title.lower()
            
            # Simple similarity check
            if self._title_similarity(item_title, search_title) > 0.7:
                doi = item.get('DOI')
                if doi:
                    print(f"    📄 Title search → DOI: {doi}")
                    return doi
        
        raise Exception("No matching DOI found")
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity"""
        if not title1 or not title2:
            return 0.0
        
        words1 = set(re.findall(r'\w+', title1.lower()))
        words2 = set(re.findall(r'\w+', title2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

async def comprehensive_resolution():
    """Run comprehensive DOI resolution with proper rate limiting"""
    
    print("🚀 Comprehensive DOI Resolution with Enhanced Rate Limiting")
    print("=" * 70)
    
    resolver = ComprehensiveDOIResolver()
    
    # Load unresolved papers
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    
    if not unresolved_file.exists():
        print(f"❌ Unresolved file not found: {unresolved_file}")
        return
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract BibTeX entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"📊 Processing {len(entries)} unresolved papers")
    
    # Track results
    results = {
        "total_papers": len(entries),
        "url_doi_recovered": 0,
        "pubmed_recovered": 0,
        "corpus_id_recovered": 0,
        "title_search_recovered": 0,
        "actually_processed": 0,
        "processing_errors": 0,
        "rate_limit_errors": 0,
        "successfully_resolved": []
    }
    
    print(f"\n🔍 Enhanced strategies:")
    print(f"   1. URL DOI extraction (immediate)")
    print(f"   2. PubMed ID conversion (with rate limiting)")
    print(f"   3. Semantic Scholar CorpusID (with exponential backoff)")
    print(f"   4. CrossRef title search (with jitter)")
    print(f"   5. Full DOI pipeline processing")
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i:2d}/{len(entries)}. Processing entry...")
        
        # Extract metadata
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1).strip() if title_match else ""
        title_short = title[:50] + "..." if len(title) > 50 else title
        
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        url = url_match.group(1) if url_match else None
        
        year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
        year = year_match.group(1) if year_match else None
        
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
        authors_str = author_match.group(1) if author_match else None
        
        print(f"    📄 {title_short}")
        
        recovered_doi = None
        recovery_method = None
        
        # Strategy 1: URL DOI extraction (fastest, no rate limiting needed)
        if url:
            doi = resolver.url_extractor.extract_doi_from_url(url)
            if doi:
                print(f"    ✅ DOI from URL: {doi}")
                recovered_doi = doi
                recovery_method = "url_extraction"
                results["url_doi_recovered"] += 1
        
        # Strategy 2: PubMed conversion (with rate limiting)
        if not recovered_doi and url and ('pubmed' in url.lower() or 'ncbi.nlm.nih.gov' in url):
            pmid_match = re.search(r'pubmed/(\d+)', url)
            if pmid_match:
                pmid = pmid_match.group(1)
                try:
                    doi = await resolver.rate_limited_request(
                        'pubmed', 
                        resolver.pubmed_converter.pmid_to_doi, 
                        pmid
                    )
                    if doi:
                        print(f"    ✅ DOI from PubMed ID {pmid}: {doi}")
                        recovered_doi = doi
                        recovery_method = "pubmed_conversion"
                        results["pubmed_recovered"] += 1
                except Exception as e:
                    print(f"    ⚠️  PubMed error: {e}")
        
        # Strategy 3: Semantic Scholar CorpusID (with exponential backoff)
        if not recovered_doi and url:
            corpus_id = resolver.extract_corpus_id(url)
            if corpus_id:
                doi = await resolver.rate_limited_request(
                    'semantic_scholar',
                    resolver.semantic_scholar_request,
                    corpus_id
                )
                if doi:
                    recovered_doi = doi
                    recovery_method = "corpus_id_resolution"
                    results["corpus_id_recovered"] += 1
        
        # Strategy 4: CrossRef title search (with jitter)
        if not recovered_doi and title and len(title) > 10:
            doi = await resolver.rate_limited_request(
                'crossref_title',
                resolver.crossref_title_search,
                title, year
            )
            if doi:
                recovered_doi = doi
                recovery_method = "title_search"
                results["title_search_recovered"] += 1
        
        # Strategy 5: Process through DOI pipeline
        if recovered_doi:
            try:
                # Parse authors
                authors = None
                if authors_str:
                    authors = [a.strip() for a in authors_str.split(' and ')]
                    authors = [resolver.text_normalizer.normalize_text(author) for author in authors]
                
                print(f"    🔄 Processing through DOI resolver: {recovered_doi}")
                
                # Process through Scholar pipeline
                result = await resolver.doi_resolver.resolve_async(
                    title=title,
                    year=int(year) if year and year.isdigit() else None,
                    authors=authors,
                    sources=['crossref']
                )
                
                if result and result.get('doi'):
                    print(f"    ✅ Successfully processed: {result['doi']}")
                    results["actually_processed"] += 1
                    results["successfully_resolved"].append({
                        "title": title,
                        "doi": recovered_doi,
                        "recovery_method": recovery_method,
                        "processed": True
                    })
                else:
                    print(f"    ⚠️  DOI resolver failed for: {recovered_doi}")
                    results["processing_errors"] += 1
                    
            except Exception as e:
                print(f"    💥 Processing error: {e}")
                results["processing_errors"] += 1
        else:
            print(f"    ❌ No DOI recovered with all strategies")
        
        # Progress update every 10 papers
        if i % 10 == 0:
            processed = results["actually_processed"]
            rate = (processed / i) * 100
            print(f"\n📊 Progress: {i}/{len(entries)} - Success rate: {rate:.1f}%")
    
    # Final results
    print(f"\n" + "=" * 70)
    print(f"🎯 COMPREHENSIVE RESOLUTION RESULTS")
    print(f"=" * 70)
    print(f"📊 Total papers: {results['total_papers']}")
    print(f"🔗 URL DOI extraction: {results['url_doi_recovered']}")
    print(f"🏥 PubMed conversion: {results['pubmed_recovered']}")
    print(f"📄 CorpusID resolution: {results['corpus_id_recovered']}")
    print(f"🔍 Title search: {results['title_search_recovered']}")
    print(f"✅ Actually processed: {results['actually_processed']}")
    print(f"💥 Processing errors: {results['processing_errors']}")
    
    # Calculate success rate
    total_recovered = (results['url_doi_recovered'] + results['pubmed_recovered'] + 
                      results['corpus_id_recovered'] + results['title_search_recovered'])
    recovery_rate = (results['actually_processed'] / results['total_papers']) * 100
    
    print(f"📈 Total DOIs recovered: {total_recovered}")
    print(f"📈 Processing success rate: {recovery_rate:.1f}%")
    
    # Save results
    results_file = Path(".dev/comprehensive_resolution_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(comprehensive_resolution())