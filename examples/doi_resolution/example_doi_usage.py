#!/usr/bin/env python3
"""Example: Using Scholar to resolve DOIs and enrich papers."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar

# Initialize Scholar
scholar = Scholar(
    email_crossref="your_email@example.com",
    email_pubmed="your_email@example.com"
)

# Example 1: Direct DOI resolution
print("Example 1: Resolve DOI from title")
print("-" * 60)

doi = scholar.resolve_doi(
    title="The functional role of cross-frequency coupling",
    year=2010
)

if doi:
    print(f"✓ Found DOI: {doi}")
    print(f"  DOI URL: https://doi.org/{doi}")
    print(f"  Use with Zotero: Click 'Save to Zotero' on the DOI page")
else:
    print("✗ DOI not found")

# Example 2: Search and enrich papers
print("\n\nExample 2: Search papers with automatic enrichment")
print("-" * 60)

papers = scholar.search(
    "phase amplitude coupling epilepsy",
    limit=5,
    sources=['pubmed']  # PubMed has good DOI coverage
)

print(f"Found {len(papers)} papers\n")

for i, paper in enumerate(papers[:3]):
    print(f"{i+1}. {paper.title[:60]}...")
    print(f"   Year: {paper.year}")
    print(f"   Journal: {paper.journal}")
    
    if paper.doi:
        print(f"   DOI: {paper.doi}")
        print(f"   Link: https://doi.org/{paper.doi}")
    
    if paper.impact_factor:
        print(f"   Impact Factor: {paper.impact_factor}")
    
    if paper.citation_count:
        print(f"   Citations: {paper.citation_count}")
    print()

# Example 3: Enhance existing BibTeX
print("\nExample 3: Enhance existing BibTeX file")
print("-" * 60)

# This would enhance your BibTeX file with DOIs, abstracts, and citations
# enhanced = scholar.enrich_bibtex(
#     "my_papers.bib",
#     output_path="my_papers_enhanced.bib"
# )

print("scholar.enrich_bibtex() will:")
print("  • Find DOIs using CrossRef, PubMed, and OpenAlex")
print("  • Add abstracts where available")
print("  • Add citation counts")
print("  • Add journal impact factors")
print("  • Convert Semantic Scholar URLs to DOI URLs")

# Example 4: Use with Zotero
print("\n\nExample 4: Integration with Zotero")
print("-" * 60)
print("Once you have DOIs, you can:")
print("  1. Navigate to https://doi.org/{doi}")
print("  2. Click the Zotero connector in your browser")
print("  3. Zotero will download the PDF using your academic credentials")
print("  4. Metadata will be automatically extracted")
print("\nOr use Zotero's 'Add by identifier' with the DOI directly!")