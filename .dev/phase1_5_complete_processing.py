#!/usr/bin/env python3
"""
Phase 1.5: Complete DOI Processing with CorpusID Support
Actually process recovered DOIs through the Scholar pipeline
"""

import sys
import json
import re
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi.utils import URLDOIExtractor, PubMedConverter, TextNormalizer
from scitex.scholar.doi._DOIResolver import DOIResolver
from scitex.scholar.config import ScholarConfig

class SemanticScholarCorpusResolver:
    """Resolve DOIs from Semantic Scholar CorpusID"""
    
    def __init__(self):
        self.api_base = "https://api.semanticscholar.org/graph/v1/paper"
    
    def extract_corpus_id(self, url: str) -> str:
        """Extract CorpusID from Semantic Scholar URL"""
        if not url:
            return None
        
        # Pattern: https://api.semanticscholar.org/CorpusId:123456
        match = re.search(r'CorpusId:(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def corpus_id_to_doi(self, corpus_id: str) -> str:
        """Convert CorpusID to DOI via Semantic Scholar API"""
        if not corpus_id:
            return None
        
        try:
            import requests
            
            # Use CorpusID format for API
            paper_id = f"CorpusId:{corpus_id}"
            url = f"{self.api_base}/{paper_id}"
            
            params = {
                'fields': 'externalIds,title,authors,year,venue,abstract'
            }
            
            headers = {
                'User-Agent': 'SciTeX Scholar (research@scitex.ai)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                external_ids = data.get('externalIds', {})
                doi = external_ids.get('DOI')
                
                if doi:
                    print(f"    📄 CorpusID {corpus_id} → DOI: {doi}")
                    return doi
                else:
                    print(f"    ❌ CorpusID {corpus_id}: No DOI found in Semantic Scholar")
            else:
                print(f"    ⚠️  CorpusID {corpus_id}: API error {response.status_code}")
                
        except Exception as e:
            print(f"    💥 Error resolving CorpusID {corpus_id}: {e}")
        
        return None

async def process_recovered_papers():
    """Actually process recovered papers through DOI resolution pipeline"""
    
    print("🔄 Phase 1.5: Complete DOI Processing with CorpusID Support")
    print("=" * 70)
    
    # Initialize all utilities
    url_extractor = URLDOIExtractor()
    pubmed_converter = PubMedConverter(email="research@scitex.ai")
    text_normalizer = TextNormalizer()
    corpus_resolver = SemanticScholarCorpusResolver()
    
    # Initialize DOI resolver for actual processing
    doi_resolver = DOIResolver(project="pac")
    
    # Load unresolved papers
    config = ScholarConfig()
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    
    if not unresolved_file.exists():
        print(f"❌ Unresolved file not found: {unresolved_file}")
        return
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract BibTeX entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"📊 Total unresolved papers: {len(entries)}")
    
    # Track results
    results = {
        "total_papers": len(entries),
        "url_doi_recovered": 0,
        "pubmed_recovered": 0,
        "corpus_id_recovered": 0,
        "actually_processed": 0,
        "processing_errors": 0,
        "still_unresolved": [],
        "successfully_resolved": []
    }
    
    print(f"\\n🚀 Processing papers through full DOI resolution pipeline...")
    
    for i, entry in enumerate(entries, 1):
        print(f"\\n{i:2d}/{len(entries)}. Processing entry...")
        
        # Extract basic info
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1) if title_match else "Unknown Title"
        title_short = title[:50] + "..." if len(title) > 50 else title
        
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        url = url_match.group(1) if url_match else None
        
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
        authors_str = author_match.group(1) if author_match else None
        
        year_match = re.search(r'year\s*=\s*\{([^}]+)\}', entry)
        year_str = year_match.group(1) if year_match else None
        year = int(year_str) if year_str and year_str.isdigit() else None
        
        print(f"    📄 {title_short}")
        
        recovered_doi = None
        recovery_method = None
        
        # 1. Try URL DOI extraction  
        if url:
            doi = url_extractor.extract_doi_from_url(url)
            if doi:
                print(f"    ✅ DOI from URL: {doi}")
                recovered_doi = doi
                recovery_method = "url_extraction"
                results["url_doi_recovered"] += 1
        
        # 2. Try PubMed ID conversion
        if not recovered_doi and url and ('pubmed' in url.lower() or 'ncbi.nlm.nih.gov' in url):
            pmid_match = re.search(r'pubmed/(\d+)', url)
            if pmid_match:
                pmid = pmid_match.group(1)
                try:
                    doi = pubmed_converter.pmid_to_doi(pmid)
                    if doi:
                        print(f"    ✅ DOI from PubMed ID {pmid}: {doi}")
                        recovered_doi = doi
                        recovery_method = "pubmed_conversion"
                        results["pubmed_recovered"] += 1
                except Exception as e:
                    print(f"    ⚠️  PubMed error for PMID {pmid}: {e}")
        
        # 3. NEW: Try CorpusID resolution
        if not recovered_doi and url and 'CorpusId:' in url:
            corpus_id = corpus_resolver.extract_corpus_id(url)
            if corpus_id:
                try:
                    doi = corpus_resolver.corpus_id_to_doi(corpus_id)
                    if doi:
                        print(f"    ✅ DOI from CorpusID {corpus_id}: {doi}")
                        recovered_doi = doi
                        recovery_method = "corpus_id_resolution"
                        results["corpus_id_recovered"] += 1
                        # Rate limiting for Semantic Scholar
                        await asyncio.sleep(1)
                except Exception as e:
                    print(f"    ⚠️  CorpusID error for {corpus_id}: {e}")
        
        # 4. If DOI recovered, process through actual DOI resolver
        if recovered_doi:
            try:
                # Parse authors
                authors = None
                if authors_str:
                    authors = [a.strip() for a in authors_str.split(' and ')] if authors_str else None
                    # Normalize author names
                    if authors:
                        authors = [text_normalizer.normalize_text(author) for author in authors]
                
                print(f"    🔄 Processing through DOI resolver: {recovered_doi}")
                
                # Actually resolve through the pipeline to create Scholar library entry
                result = await doi_resolver.resolve_async(
                    title=title,
                    year=year,
                    authors=authors,
                    sources=['crossref']  # Use CrossRef to get full metadata
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
            print(f"    ❌ No DOI recovered - remains unresolved")
            results["still_unresolved"].append({
                "title": title,
                "url": url
            })
        
        # Progress update
        if i % 10 == 0:
            print(f"\\n📊 Progress: {i}/{len(entries)} - Processed: {results['actually_processed']}")
    
    # Final results
    print(f"\\n" + "=" * 70)
    print(f"🎯 PHASE 1.5 COMPLETE PROCESSING RESULTS")
    print(f"=" * 70)
    print(f"📊 Total papers: {results['total_papers']}")
    print(f"🔗 URL DOI extraction: {results['url_doi_recovered']}")
    print(f"🏥 PubMed conversion: {results['pubmed_recovered']}")
    print(f"📄 CorpusID resolution: {results['corpus_id_recovered']}")
    print(f"✅ Actually processed through Scholar: {results['actually_processed']}")
    print(f"💥 Processing errors: {results['processing_errors']}")
    print(f"❌ Still unresolved: {len(results['still_unresolved'])}")
    
    # Save results
    results_file = Path(".dev/phase1_5_complete_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\\n💾 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(process_recovered_papers())