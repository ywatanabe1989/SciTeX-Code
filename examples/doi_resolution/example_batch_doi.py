#!/usr/bin/env python3
"""Simple example of batch DOI resolution."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar.batch_doi_resolver import BatchDOIResolver

# Papers from your BibTeX file that need DOIs
papers = [
    {
        'title': 'The functional role of cross-frequency coupling',
        'year': 2010
    },
    {
        'title': 'Measuring phase-amplitude coupling between neuronal oscillations of different frequencies',
        'year': 2010  
    },
    {
        'title': 'Modulation of gamma and alpha activity during a working memory task engaging the dorsal or ventral stream',
        'year': 2007
    },
    {
        'title': 'Theta-gamma coupling increases during the learning of item-context associations',
        'year': 2009
    },
    {
        'title': 'Phase-amplitude coupling supports phase coding in human ECoG',
        'year': 2015
    }
]

# Create batch resolver
print("Batch DOI Resolution Example")
print("=" * 60)
print(f"Processing {len(papers)} papers...\n")

resolver = BatchDOIResolver(
    email="research@example.com",
    max_workers=3  # Process 3 papers in parallel
)

# Resolve DOIs in batch
results = resolver.resolve_batch(papers, show_progress=True)

# Summary
print(f"\n{'='*60}")
print("Results Summary:")
print(f"{'='*60}")

success_count = sum(1 for r in results if r['doi'])
abstract_count = sum(1 for r in results if r['abstract'])

print(f"Total papers: {len(results)}")
print(f"DOIs found: {success_count} ({success_count/len(results)*100:.0f}%)")
print(f"Abstracts found: {abstract_count} ({abstract_count/len(results)*100:.0f}%)")

# Show details
print(f"\nDetailed Results:")
for i, result in enumerate(results):
    print(f"\n{i+1}. {result['title'][:60]}...")
    if result['doi']:
        print(f"   ✓ DOI: {result['doi']}")
        print(f"   ✓ URL: https://doi.org/{result['doi']}")
        print(f"   ✓ Abstract: {'Yes' if result['abstract'] else 'No'}")
    else:
        print("   ✗ DOI not found")

print("\n" + "="*60)
print("Batch processing advantages:")
print("  • Processes multiple papers in parallel")
print("  • Respects API rate limits")
print("  • Shows progress bar")
print("  • Handles errors gracefully")
print("  • Returns all results at once")
print("="*60)