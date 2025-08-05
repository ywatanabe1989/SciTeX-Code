#!/usr/bin/env python3
"""
Quick test of Phase 1.5 on first 5 entries
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi.utils import URLDOIExtractor, PubMedConverter

def quick_test():
    """Test Phase 1.5 on first 5 entries"""
    
    # Initialize utilities
    url_extractor = URLDOIExtractor()
    pubmed_converter = PubMedConverter(email="research@scitex.ai")
    
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract first 5 entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"Testing first 5 of {len(entries)} entries...")
    
    for i, entry in enumerate(entries[:5], 1):
        print(f"\n{i}. Processing entry...")
        
        # Extract info
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1) if title_match else "Unknown Title"
        title_short = title[:50] + "..." if len(title) > 50 else title
        
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        url = url_match.group(1) if url_match else None
        
        print(f"   📄 {title_short}")
        print(f"   🔗 {url[:60] + '...' if url and len(url) > 60 else url}")
        
        # Test URL DOI extraction
        if url:
            doi = url_extractor.extract_doi_from_url(url)
            if doi:
                print(f"   ✅ URL DOI: {doi}")
                continue
        
        # Test PubMed conversion
        if url and ('pubmed' in url.lower() or 'ncbi.nlm.nih.gov' in url):
            pmid_match = re.search(r'pubmed/(\d+)', url)
            if pmid_match:
                pmid = pmid_match.group(1)
                try:
                    doi = pubmed_converter.pmid_to_doi(pmid)
                    if doi:
                        print(f"   ✅ PubMed {pmid} → DOI: {doi}")
                        continue
                except Exception as e:
                    print(f"   ⚠️  PubMed error: {e}")
        
        # Test CorpusID extraction
        if url and 'CorpusId:' in url:
            corpus_match = re.search(r'CorpusId:(\d+)', url)
            if corpus_match:
                corpus_id = corpus_match.group(1)
                print(f"   📄 Found CorpusID: {corpus_id} (would test API)")
                # Don't actually call API in quick test
                continue
        
        print(f"   ❌ No DOI recovery method found")

if __name__ == "__main__":
    quick_test()