#!/usr/bin/env python3
"""
Phase 2: Enhanced DOI Resolution for Remaining Papers
Advanced strategies for the 49 remaining unresolved papers
"""

import sys
import json
import re
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi.utils import URLDOIExtractor, PubMedConverter, TextNormalizer
from scitex.scholar.doi._DOIResolver import DOIResolver
from scitex.scholar.config import ScholarConfig

class EnhancedDOIResolver:
    """Enhanced DOI resolution with multiple strategies"""
    
    def __init__(self):
        self.url_extractor = URLDOIExtractor()
        self.pubmed_converter = PubMedConverter(email="research@scitex.ai")
        self.text_normalizer = TextNormalizer()
        self.doi_resolver = DOIResolver(project="pac")
        
    def extract_arxiv_id(self, url: str) -> str:
        """Extract arXiv ID from URL"""
        if not url or 'arxiv' not in url.lower():
            return None
        
        # Pattern: https://arxiv.org/pdf/2012.04217.pdf or https://arxiv.org/abs/2012.04217
        match = re.search(r'arxiv\.org/(?:pdf|abs)/(\d{4}\.\d{4,5})', url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    async def arxiv_to_doi(self, arxiv_id: str) -> str:
        """Convert arXiv ID to DOI via arXiv API"""
        if not arxiv_id:
            return None
        
        try:
            import requests
            import xml.etree.ElementTree as ET
            
            # arXiv API
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            
            headers = {
                'User-Agent': 'SciTeX Scholar (research@scitex.ai)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)
                
                # Look for DOI in the entry
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('.//atom:entry', ns)
                
                if entries:
                    entry = entries[0]
                    # Check for DOI link
                    links = entry.findall('.//atom:link', ns)
                    for link in links:
                        href = link.get('href', '')
                        if 'doi.org' in href:
                            doi_match = re.search(r'doi\.org/(.+)', href)
                            if doi_match:
                                doi = doi_match.group(1)
                                print(f"    📄 arXiv {arxiv_id} → DOI: {doi}")
                                return doi
                
                print(f"    ❌ arXiv {arxiv_id}: No DOI found")
            else:
                print(f"    ⚠️  arXiv {arxiv_id}: API error {response.status_code}")
                
        except Exception as e:
            print(f"    💥 Error resolving arXiv {arxiv_id}: {e}")
        
        return None
    
    def extract_semantic_scholar_url_doi(self, url: str) -> str:
        """Try to extract DOI from Semantic Scholar URL patterns"""
        if not url or 'semanticscholar' not in url.lower():
            return None
        
        try:
            import requests
            
            # Follow redirects to see if it leads to a publisher URL with DOI
            headers = {
                'User-Agent': 'SciTeX Scholar (research@scitex.ai)'
            }
            
            response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            final_url = response.url
            
            # Check if final URL contains DOI
            doi = self.url_extractor.extract_doi_from_url(final_url)
            if doi:
                print(f"    📄 Semantic Scholar redirect → DOI: {doi}")
                return doi
                
        except Exception as e:
            print(f"    ⚠️  Error following Semantic Scholar URL: {e}")
        
        return None
    
    async def title_year_search(self, title: str, year: str = None, authors: str = None) -> str:
        """Search for DOI using title and year via CrossRef"""
        if not title or len(title) < 10:
            return None
        
        try:
            import requests
            
            # Clean title for search
            clean_title = self.text_normalizer.normalize_text(title)
            clean_title = re.sub(r'[^\w\s-]', ' ', clean_title)  # Remove special chars
            clean_title = ' '.join(clean_title.split())  # Normalize whitespace
            
            # Limit to reasonable length
            if len(clean_title) > 100:
                clean_title = clean_title[:100]
            
            # CrossRef search API
            url = "https://api.crossref.org/works"
            params = {
                'query.title': clean_title,
                'rows': 5
            }
            
            if year and year.isdigit():
                params['filter'] = f'published:{year}'
            
            headers = {
                'User-Agent': 'SciTeX Scholar (research@scitex.ai)',
                'mailto': 'research@scitex.ai'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('message', {}).get('items', [])
                
                for item in items:
                    item_title = item.get('title', [''])[0].lower()
                    search_title = clean_title.lower()
                    
                    # Simple title similarity check
                    if self._title_similarity(item_title, search_title) > 0.7:
                        doi = item.get('DOI')
                        if doi:
                            print(f"    📄 Title search → DOI: {doi}")
                            return doi
                
                print(f"    ❌ Title search: No matching DOI found")
            else:
                print(f"    ⚠️  Title search: API error {response.status_code}")
                
        except Exception as e:
            print(f"    💥 Error in title search: {e}")
        
        return None
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Simple title similarity using word overlap"""
        if not title1 or not title2:
            return 0.0
        
        words1 = set(re.findall(r'\w+', title1.lower()))
        words2 = set(re.findall(r'\w+', title2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

async def phase2_enhanced_resolution():
    """Enhanced DOI resolution for remaining unresolved papers"""
    
    print("🚀 Phase 2: Enhanced DOI Resolution")
    print("=" * 70)
    
    resolver = EnhancedDOIResolver()
    
    # Load unresolved papers
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    
    if not unresolved_file.exists():
        print(f"❌ Unresolved file not found: {unresolved_file}")
        return
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract BibTeX entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"📊 Remaining unresolved papers: {len(entries)}")
    
    # Track results
    results = {
        "total_papers": len(entries),
        "arxiv_recovered": 0,
        "semantic_scholar_redirect_recovered": 0,
        "title_search_recovered": 0,
        "rate_limited": 0,
        "actually_processed": 0,
        "processing_errors": 0,
        "still_unresolved": [],
        "successfully_resolved": []
    }
    
    print(f"\n🔍 Enhanced resolution strategies:")
    print(f"   1. arXiv ID extraction and conversion")
    print(f"   2. Semantic Scholar URL redirect following")
    print(f"   3. CrossRef title+year search")
    print(f"   4. Rate limiting with delays")
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i:2d}/{len(entries)}. Processing entry...")
        
        # Extract basic info
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1).strip() if title_match else ""
        title_short = title[:60] + "..." if len(title) > 60 else title
        
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        url = url_match.group(1) if url_match else None
        
        year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
        year = year_match.group(1) if year_match else None
        
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
        authors_str = author_match.group(1) if author_match else None
        
        print(f"    📄 {title_short}")
        
        recovered_doi = None
        recovery_method = None
        
        # Strategy 1: arXiv ID extraction
        if url and not recovered_doi:
            arxiv_id = resolver.extract_arxiv_id(url)
            if arxiv_id:
                try:
                    doi = await resolver.arxiv_to_doi(arxiv_id)
                    if doi:
                        recovered_doi = doi
                        recovery_method = "arxiv_conversion"
                        results["arxiv_recovered"] += 1
                except Exception as e:
                    print(f"    ⚠️  arXiv error: {e}")
        
        # Strategy 2: Semantic Scholar redirect following
        if url and not recovered_doi and 'semanticscholar' in url.lower():
            try:
                doi = resolver.extract_semantic_scholar_url_doi(url)
                if doi:
                    recovered_doi = doi
                    recovery_method = "semantic_scholar_redirect"
                    results["semantic_scholar_redirect_recovered"] += 1
            except Exception as e:
                print(f"    ⚠️  Semantic Scholar redirect error: {e}")
        
        # Strategy 3: Title+year search (with rate limiting)
        if not recovered_doi and title:
            try:
                doi = await resolver.title_year_search(title, year, authors_str)
                if doi:
                    recovered_doi = doi
                    recovery_method = "title_search"
                    results["title_search_recovered"] += 1
                
                # Rate limiting for CrossRef
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    ⚠️  Title search error: {e}")
        
        # Process through DOI resolver if recovered
        if recovered_doi:
            try:
                # Parse authors
                authors = None
                if authors_str:
                    authors = [a.strip() for a in authors_str.split(' and ')] if authors_str else None
                    if authors:
                        authors = [resolver.text_normalizer.normalize_text(author) for author in authors]
                
                print(f"    🔄 Processing through DOI resolver: {recovered_doi}")
                
                # Actually resolve through the pipeline
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
            print(f"    ❌ No DOI recovered with enhanced methods")
            results["still_unresolved"].append({
                "title": title,
                "url": url
            })
        
        # Progress update
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{len(entries)} - Processed: {results['actually_processed']}")
    
    # Final results
    print(f"\n" + "=" * 70)
    print(f"🎯 PHASE 2 ENHANCED RESOLUTION RESULTS")
    print(f"=" * 70)
    print(f"📊 Total papers: {results['total_papers']}")
    print(f"📄 arXiv conversion: {results['arxiv_recovered']}")
    print(f"🔗 Semantic Scholar redirects: {results['semantic_scholar_redirect_recovered']}")
    print(f"🔍 Title search: {results['title_search_recovered']}")
    print(f"✅ Actually processed through Scholar: {results['actually_processed']}")
    print(f"💥 Processing errors: {results['processing_errors']}")
    print(f"❌ Still unresolved: {len(results['still_unresolved'])}")
    
    recovery_rate = (results['actually_processed'] / results['total_papers']) * 100
    print(f"📈 Phase 2 Recovery Rate: {recovery_rate:.1f}%")
    
    # Save results
    results_file = Path(".dev/phase2_enhanced_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(phase2_enhanced_resolution())