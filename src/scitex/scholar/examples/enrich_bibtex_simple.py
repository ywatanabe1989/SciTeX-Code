#!/usr/bin/env python3
"""
Simple example: Enrich an existing BibTeX file with impact factors and citations.

This example shows the easiest way to enrich your bibliography with:
- Journal impact factors (2024 JCR data)
- Citation counts
- Missing DOIs
"""

from scitex.scholar import Scholar

# Method 1: Simplest - enhance in place (creates backup)
def enrich_bibtex_simple(bibtex_file):
    """Enrich a BibTeX file in the simplest way possible."""
    scholar = Scholar()
    enriched = scholar.enrich_bibtex(bibtex_file)
    print(f"Enriched {len(enriched)} papers")
    return enriched

# Method 2: Save to different file
def enrich_bibtex_to_new_file(input_file, output_file):
    """Enrich a BibTeX file and save to a new location."""
    scholar = Scholar()
    enriched = scholar.enrich_bibtex(input_file, output_file)
    print(f"Enriched {len(enriched)} papers and saved to {output_file}")
    return enriched

# Method 3: Using Papers.from_bibtex() directly
def enrich_bibtex_manual(bibtex_file):
    """Load and enrich BibTeX using Papers class directly."""
    from scitex.scholar import Papers, Scholar
    
    # Load BibTeX file
    papers = Papers.from_bibtex(bibtex_file)
    print(f"Loaded {len(papers)} papers")
    
    # Enrich with Scholar
    scholar = Scholar()
    enriched = scholar._enrich_papers(papers)
    
    # Save back
    enriched.save(bibtex_file.replace('.bib', '_enriched.bib'))
    return enriched

# Method 4: Quick one-liner function
def quick_enrich(bibtex_file):
    """One-liner to enrich a BibTeX file."""
    return Scholar().enrich_bibtex(bibtex_file)

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Use command line argument
        bibtex_file = sys.argv[1]
        print(f"Enriching {bibtex_file}...")
        enriched = enrich_bibtex_simple(bibtex_file)
        
        # Show summary
        enriched.summarize()
    else:
        print("Usage: python enrich_bibtex_simple.py <your_bibliography.bib>")
        print("\nExample BibTeX content to test:")
        print("""
@article{einstein1905,
    title = {On the electrodynamics of moving bodies},
    author = {Einstein, Albert},
    journal = {Annalen der Physik},
    year = {1905}
}

@article{watson1953,
    title = {Molecular structure of nucleic acids},
    author = {Watson, J. D. and Crick, F. H. C.},
    journal = {Nature},
    year = {1953},
    volume = {171},
    pages = {737-738}
}
        """)