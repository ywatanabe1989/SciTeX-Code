#!/usr/bin/env python3
"""
Deploy Phase 1 Enhanced DOI Resolver on Actual Unresolved PAC Papers
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi.utils import URLDOIExtractor, PubMedConverter, TextNormalizer
from scitex.scholar.config import ScholarConfig

def process_unresolved_papers():
    """Process unresolved papers with Phase 1 enhanced DOI resolver"""
    
    print("🚀 Deploying Phase 1 Enhanced DOI Resolver")
    print("=" * 60)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize utilities  
    url_extractor = URLDOIExtractor()
    pubmed_converter = PubMedConverter(email="research@scitex.ai")
    text_normalizer = TextNormalizer()
    
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
        "url_doi_extracted": 0,
        "pubmed_converted": 0,
        "text_normalized": 0,
        "total_recovered": 0,
        "recovered_papers": [],
        "failed_papers": [],
        "start_time": datetime.now().isoformat(),
    }
    
    print(f"\n🔄 Processing papers with Phase 1 utilities...")
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i:2d}/{len(entries)}. Processing entry...")
        
        # Extract basic info
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1) if title_match else "Unknown Title"
        title_short = title[:50] + "..." if len(title) > 50 else title
        
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        url = url_match.group(1) if url_match else None
        
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
        authors = author_match.group(1) if author_match else None
        
        print(f"    📄 {title_short}")
        if url:
            print(f"    🔗 {url[:60] + '...' if len(url) > 60 else url}")
        
        recovered_doi = None
        recovery_method = None
        
        # 1. Try URL DOI extraction
        if url:
            doi = url_extractor.extract_doi_from_url(url)
            if doi:
                print(f"    ✅ DOI extracted from URL: {doi}")
                recovered_doi = doi
                recovery_method = "url_extraction"
                results["url_doi_extracted"] += 1
        
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
                        results["pubmed_converted"] += 1
                except Exception as e:
                    print(f"    ⚠️  PubMed conversion error for PMID {pmid}: {e}")
        
        # 3. Text normalization (for better future searches)
        normalized_authors = None
        if authors:
            normalized = text_normalizer.normalize_text(authors)
            if normalized != authors:
                print(f"    🔧 Authors normalized: {authors[:30]}... → {normalized[:30]}...")
                normalized_authors = normalized
                results["text_normalized"] += 1
        
        # Record results
        paper_result = {
            "index": i,
            "title": title,
            "original_url": url,
            "original_authors": authors,
            "normalized_authors": normalized_authors,
            "recovered_doi": recovered_doi,
            "recovery_method": recovery_method,
        }
        
        if recovered_doi:
            results["recovered_papers"].append(paper_result)
            results["total_recovered"] += 1
            print(f"    🎉 Paper recovered via {recovery_method}")
        else:
            results["failed_papers"].append(paper_result)
            print(f"    ❌ No DOI recovered")
        
        # Rate limiting
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{len(entries)} papers processed, {results['total_recovered']} recovered")
    
    # Final results
    results["end_time"] = datetime.now().isoformat()
    recovery_rate = (results["total_recovered"] / results["total_papers"]) * 100
    
    print(f"\n" + "=" * 60)
    print(f"🎯 PHASE 1 DEPLOYMENT RESULTS")
    print(f"=" * 60)
    print(f"📊 Total papers processed: {results['total_papers']}")
    print(f"✅ Papers recovered: {results['total_recovered']} ({recovery_rate:.1f}%)")
    print(f"🔗 URL DOI extraction: {results['url_doi_extracted']} papers")
    print(f"🏥 PubMed conversion: {results['pubmed_converted']} papers")
    print(f"🔧 Text normalization: {results['text_normalized']} papers")
    print(f"❌ Still unresolved: {len(results['failed_papers'])} papers")
    
    # Save detailed results
    results_file = Path(".dev/phase1_deployment_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Performance vs projection
    projected_rate = 28  # Our original projection
    if recovery_rate >= projected_rate * 0.8:  # Within 80% of projection
        print(f"✅ SUCCESS: Recovery rate {recovery_rate:.1f}% meets projection ({projected_rate}%)")
    else:
        print(f"⚠️  REVIEW: Recovery rate {recovery_rate:.1f}% below projection ({projected_rate}%)")
    
    return results

if __name__ == "__main__":
    results = process_unresolved_papers()