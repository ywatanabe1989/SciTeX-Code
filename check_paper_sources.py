#!/usr/bin/env python3
# Check what sources and journals we can access

import sys
sys.path.insert(0, 'src')
from scitex.scholar import Scholar

scholar = Scholar()

print("Testing access to different sources...")
print("="*60)

# Test queries
test_queries = {
    "Nature paper": '"Nature" neuroscience 2023',
    "Science paper": '"Science" brain imaging',
    "Cell paper": '"Cell" epilepsy',
    "General epilepsy": 'epilepsy detection EEG'
}

for desc, query in test_queries.items():
    print(f"\n{desc}: {query}")
    print("-"*40)
    
    # Try each source
    for source in ['semantic_scholar', 'pubmed', 'arxiv']:
        try:
            results = scholar.search(query, sources=[source], limit=5)
            print(f"\n{source}: {len(results)} results")
            
            # Show what we got
            for paper in results.papers[:3]:
                print(f"  - {paper.title[:60]}...")
                print(f"    Journal: {paper.journal or 'N/A'}")
                print(f"    Source: {paper.source}")
                print(f"    Year: {paper.year}, Citations: {paper.citation_count or 0}")
                
        except Exception as e:
            print(f"\n{source}: ERROR - {e}")

# Check if we need email for PubMed
print("\n" + "="*60)
print("Configuration Check:")
print(f"Email configured: {scholar.email}")
print(f"API keys configured: {list(scholar.api_keys.keys())}")

print("\nTo access subscription journals through PubMed, set your email:")
print('export SCHOLAR_EMAIL="your.email@university.edu"')
print("\nFor better Semantic Scholar access, get an API key:")
print("https://www.semanticscholar.org/product/api")