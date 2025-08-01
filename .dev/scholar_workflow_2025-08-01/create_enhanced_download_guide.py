#!/usr/bin/env python3
"""Create enhanced download guide with DOIs from enriched papers."""

import json
import re
from pathlib import Path

def extract_doi_from_bibtex(content, title):
    """Extract DOI for a specific paper from BibTeX content."""
    # Clean title for matching
    clean_title = title.lower()[:50]  # First 50 chars
    
    # Split into entries
    entries = content.split('@article{')
    for entry in entries[1:]:  # Skip first empty split
        # Check if this entry contains our title
        entry_lower = entry.lower()
        if clean_title in entry_lower:
            # Look for DOI
            doi_match = re.search(r'doi\s*=\s*{([^}]+)}', entry, re.IGNORECASE)
            if doi_match:
                return doi_match.group(1)
    return None

def main():
    # Load the original download URLs
    with open('download_urls.json', 'r') as f:
        papers = json.load(f)
    
    # Load enriched data if available
    enriched_dois = {}
    if Path('.dev/test_papers_enriched_final.bib').exists():
        with open('.dev/test_papers_enriched_final.bib', 'r') as f:
            enriched_content = f.read()
            
        for paper in papers:
            doi = extract_doi_from_bibtex(enriched_content, paper['title'])
            if doi:
                enriched_dois[paper['title']] = doi
    
    # Create enhanced guide
    output = """# Enhanced PDF Download Instructions

Please download the following papers and save them to: `/home/ywatanabe/proj/SciTeX-Code/downloaded_papers/`

## Download Strategy

1. **Papers with DOIs**: Use institutional access through your library website
2. **Papers without DOIs**: Use the provided URLs or search by title
3. **Alternative**: Use Unpaywall browser extension for legal open access versions

## Papers to Download

"""
    
    for i, paper in enumerate(papers, 1):
        output += f"### {i}. {paper['title'][:100]}...\n\n"
        output += f"- **Authors**: {paper['authors']}...\n"
        output += f"- **Year**: {paper['year']}\n"
        output += f"- **Journal**: {paper['journal']}\n"
        
        # Add DOI if found
        doi = enriched_dois.get(paper['title']) or paper.get('doi', '')
        if doi:
            output += f"- **DOI**: {doi}\n"
            output += f"- **DOI URL**: [https://doi.org/{doi}](https://doi.org/{doi})\n"
        
        # Add URL if available
        if paper.get('url'):
            output += f"- **Alternative URL**: [{paper['url']}]({paper['url']})\n"
        
        output += f"- **Save as**: `{paper['filename']}`\n\n"
    
    # Add helpful tips
    output += """
## Download Tips

1. **Using DOIs**:
   - Go to your library website
   - Use the DOI search or paste the DOI
   - Download the PDF through institutional access

2. **Direct URLs**:
   - Some URLs may require institutional login
   - Look for "institutional login" or "Shibboleth" options

3. **Can't find a paper?**:
   - Search Google Scholar with the title
   - Look for [PDF] links
   - Use Unpaywall or Open Access Button browser extensions

4. **Naming Convention**:
   - Please save files with the exact names provided
   - Format: `FirstAuthor-Year-JournalAbbrev.pdf`
"""
    
    with open('enhanced_download_instructions.md', 'w') as f:
        f.write(output)
    
    print(f"Enhanced guide created with {len(enriched_dois)} DOIs added")
    print(f"Total papers: {len(papers)}")

if __name__ == "__main__":
    main()