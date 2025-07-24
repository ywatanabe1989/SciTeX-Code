#!/usr/bin/env python3
"""Final BibTeX enhancement with better handling."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar

# Initialize Scholar
print("Initializing Scholar for BibTeX enhancement...")
scholar = Scholar(
    email_crossref="research@example.com",
    email_pubmed="research@example.com"
)

# Input and output paths
input_path = "/home/ywatanabe/win/downloads/papers.bib"
output_path = "/home/ywatanabe/win/downloads/papers_enhanced_final.bib"

print(f"Input: {input_path}")
print(f"Output: {output_path}\n")

# Enhance with all features enabled
print("Starting enhancement (this may take a few minutes)...")
print("Note: Using PubMed and local sources to avoid API timeouts\n")

try:
    enhanced = scholar.enrich_bibtex(
        input_path,
        output_path=output_path,
        backup=True,
        preserve_original_fields=True,
        add_missing_abstracts=False,  # Skip to speed up
        add_missing_urls=False        # Skip to speed up
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("Enhancement Complete!")
    print(f"{'='*60}")
    print(f"Total papers processed: {len(enhanced)}")
    
    # Count enrichments
    doi_count = sum(1 for p in enhanced if p.doi)
    if_count = sum(1 for p in enhanced if p.impact_factor and p.impact_factor > 0)
    citation_count = sum(1 for p in enhanced if p.citation_count)
    abstract_count = sum(1 for p in enhanced if p.abstract)
    
    print(f"\nEnrichment Statistics:")
    print(f"  Papers with DOIs: {doi_count} ({doi_count/len(enhanced)*100:.1f}%)")
    print(f"  Papers with impact factors: {if_count} ({if_count/len(enhanced)*100:.1f}%)")
    print(f"  Papers with citations: {citation_count} ({citation_count/len(enhanced)*100:.1f}%)")
    print(f"  Papers with abstracts: {abstract_count} ({abstract_count/len(enhanced)*100:.1f}%)")
    
    # Show sample enhanced entries
    print(f"\nSample enhanced entries:")
    for i, paper in enumerate(enhanced[:3]):
        print(f"\n{i+1}. {paper.title[:60]}...")
        if paper.doi:
            print(f"   DOI: {paper.doi}")
        if paper.impact_factor:
            print(f"   Impact Factor: {paper.impact_factor} ({paper.journal_quartile})")
        if paper.citation_count:
            print(f"   Citations: {paper.citation_count}")
    
    print(f"\nEnhanced BibTeX saved to: {output_path}")
    
except Exception as e:
    print(f"Error during enhancement: {e}")
    import traceback
    traceback.print_exc()