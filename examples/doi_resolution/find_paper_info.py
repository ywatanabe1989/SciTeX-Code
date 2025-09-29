#!/usr/bin/env python3
"""Find DOI, abstract, and citation counts for a specific paper."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar

# Initialize Scholar with all features
scholar = Scholar(
    email_crossref="research@example.com",
    email_pubmed="research@example.com",
    impact_factors=True,
    citations=True
)

# The paper to find
title = "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies"

print(f"Searching for paper: {title}")
print("=" * 80)

# Method 1: Direct DOI resolution
print("\nMethod 1: Direct DOI Resolution")
print("-" * 40)

doi = scholar.resolve_doi(title=title)
if doi:
    print(f"✓ Found DOI: {doi}")
    print(f"  DOI URL: https://doi.org/{doi}")
    
    # Try to get abstract using DOI
    abstract = scholar._doi_resolver.get_abstract(doi)
    if abstract:
        print(f"\n✓ Abstract found:")
        print(f"  {abstract[:200]}...")
else:
    print("✗ DOI not found via direct resolution")

# Method 2: Search for the paper to get full enrichment
print("\n\nMethod 2: Full Paper Search with Enrichment")
print("-" * 40)

# Search for the paper
papers = scholar.search(
    title,
    limit=5,
    sources=['pubmed', 'semantic_scholar']
)

print(f"\nFound {len(papers)} papers")

# Find exact match
target_paper = None
for paper in papers:
    # Check for exact or very close title match
    if paper.title.lower().strip() == title.lower().strip():
        target_paper = paper
        break
    elif "measuring phase-amplitude coupling" in paper.title.lower():
        target_paper = paper
        break

if target_paper:
    print(f"\n✓ Found exact match!")
    print(f"\nPaper Details:")
    print(f"  Title: {target_paper.title}")
    print(f"  Authors: {', '.join(target_paper.authors[:3])}{'...' if len(target_paper.authors) > 3 else ''}")
    print(f"  Year: {target_paper.year}")
    print(f"  Journal: {target_paper.journal}")
    
    if target_paper.doi:
        print(f"\n  DOI: {target_paper.doi}")
        print(f"  URL: https://doi.org/{target_paper.doi}")
    
    if target_paper.abstract:
        print(f"\n  Abstract:")
        print(f"  {target_paper.abstract[:300]}...")
    
    if target_paper.citation_count:
        print(f"\n  Citation Count: {target_paper.citation_count}")
    
    if target_paper.impact_factor:
        print(f"  Journal Impact Factor: {target_paper.impact_factor}")
        if target_paper.journal_quartile:
            print(f"  Journal Quartile: {target_paper.journal_quartile}")
    
    # Save as BibTeX
    from scitex.scholar._core import Papers
    collection = Papers([target_paper])
    output_file = "measuring_phase_amplitude_coupling.bib"
    collection.save(output_file)
    print(f"\n✓ Saved enriched BibTeX to: {output_file}")
    
else:
    print("\n✗ Could not find exact match in search results")
    print("\nAll results found:")
    for i, paper in enumerate(papers):
        print(f"{i+1}. {paper.title[:80]}...")
        print(f"   Year: {paper.year}, Journal: {paper.journal}")

# Method 3: Try with year if we know it
print("\n\nMethod 3: DOI Resolution with Year")
print("-" * 40)

# This paper is from 2010 (Tort et al.)
doi_with_year = scholar.resolve_doi(
    title=title,
    year=2010
)

if doi_with_year:
    print(f"✓ Found DOI with year filter: {doi_with_year}")
    print(f"  DOI URL: https://doi.org/{doi_with_year}")
else:
    print("✗ DOI not found even with year")