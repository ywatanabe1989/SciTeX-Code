#!/usr/bin/env python3
"""
Enrich metadata for all resolved PAC papers
Ensure all papers have complete abstracts and metadata
"""

import json
import re
import asyncio
from pathlib import Path
from datetime import datetime

def enrich_all_metadata():
    """Enrich metadata for all resolved PAC papers"""
    
    print("📚 Enriching Metadata for All Resolved PAC Papers")
    print("=" * 60)
    
    # Find all resolved papers
    pac_dir = Path("~/.scitex/scholar/library/pac").expanduser()
    resolved_papers = []
    
    for item in pac_dir.iterdir():
        if item.is_symlink() and item.name != "info":
            resolved_papers.append(item)
    
    print(f"📊 Found {len(resolved_papers)} resolved papers")
    
    # Track enrichment stats
    stats = {
        "total_papers": len(resolved_papers),
        "papers_with_abstracts": 0,
        "papers_missing_abstracts": 0,
        "papers_enriched": 0,
        "enrichment_errors": 0
    }
    
    for i, paper_link in enumerate(resolved_papers, 1):
        paper_name = paper_link.name
        print(f"\n{i:2d}/{len(resolved_papers)}. {paper_name}")
        
        # Get metadata file path
        master_path = paper_link.resolve()
        metadata_file = master_path / "metadata.json"
        
        if not metadata_file.exists():
            print(f"    ❌ No metadata file found")
            stats["enrichment_errors"] += 1
            continue
        
        # Load current metadata
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"    ❌ Error reading metadata: {e}")
            stats["enrichment_errors"] += 1
            continue
        
        # Check if abstract exists
        has_abstract = metadata.get('abstract') and len(metadata.get('abstract', '')) > 20
        
        if has_abstract:
            print(f"    ✅ Has abstract ({len(metadata['abstract'])} chars)")
            stats["papers_with_abstracts"] += 1
        else:
            print(f"    ❌ Missing abstract")
            stats["papers_missing_abstracts"] += 1
            
            # Try to enrich from DOI
            doi = metadata.get('doi')
            if doi:
                try:
                    enriched = enrich_from_crossref(doi)
                    if enriched.get('abstract'):
                        metadata.update(enriched)
                        metadata['updated_at'] = datetime.now().isoformat()
                        
                        # Save enriched metadata
                        with open(metadata_file, 'w') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                        
                        print(f"    ✅ Enriched with abstract ({len(enriched['abstract'])} chars)")
                        stats["papers_enriched"] += 1
                    else:
                        print(f"    ⚠️  No abstract available from CrossRef")
                        
                except Exception as e:
                    print(f"    ❌ Enrichment error: {e}")
                    stats["enrichment_errors"] += 1
            else:
                print(f"    ⚠️  No DOI available for enrichment")
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📊 METADATA ENRICHMENT SUMMARY")
    print(f"=" * 60)
    print(f"📚 Total papers: {stats['total_papers']}")
    print(f"✅ Papers with abstracts: {stats['papers_with_abstracts']}")
    print(f"❌ Papers missing abstracts: {stats['papers_missing_abstracts']}")
    print(f"🔄 Papers enriched: {stats['papers_enriched']}")
    print(f"💥 Enrichment errors: {stats['enrichment_errors']}")
    
    final_with_abstracts = stats['papers_with_abstracts'] + stats['papers_enriched']
    abstract_coverage = (final_with_abstracts / stats['total_papers']) * 100
    print(f"📈 Final abstract coverage: {abstract_coverage:.1f}%")
    
    return stats

def enrich_from_crossref(doi):
    """Enrich metadata from CrossRef API"""
    import requests
    
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        'User-Agent': 'SciTeX Scholar (research@scitex.ai)',
        'mailto': 'research@scitex.ai'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        return {}
    
    data = response.json()
    work = data.get('message', {})
    
    enriched = {}
    
    # Abstract (clean HTML tags)
    if work.get('abstract'):
        abstract = work['abstract']
        # Remove JATS XML tags like <jats:p>, <jats:italic>, etc.
        abstract = re.sub(r'<[^>]+>', '', abstract)
        # Clean up extra whitespace
        abstract = ' '.join(abstract.split())
        if abstract and len(abstract) > 20:  # Only save meaningful abstracts
            enriched['abstract'] = abstract
            enriched['abstract_source'] = 'crossref'
    
    # Additional metadata
    if work.get('container-title') and not enriched.get('journal'):
        enriched['journal'] = work['container-title'][0]
        enriched['journal_source'] = 'crossref'
    
    if work.get('volume'):
        enriched['volume'] = work['volume']
    
    if work.get('issue'):
        enriched['issue'] = work['issue']
    
    if work.get('page'):
        enriched['pages'] = work['page']
    
    return enriched

if __name__ == "__main__":
    enrich_all_metadata()