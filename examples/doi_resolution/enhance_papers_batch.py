#!/usr/bin/env python3
"""Enhance papers.bib in smaller batches to avoid rate limits."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar
from scitex.io import load

# Load the original BibTeX file
print("Loading original BibTeX file...")
entries = load("/home/ywatanabe/win/downloads/papers.bib")
print(f"Found {len(entries)} entries")

# Process in batches of 10
batch_size = 10
enhanced_collections = []

# Initialize Scholar
scholar = Scholar(
    email_crossref="research@example.com",  # Add your email for better rates
    email_pubmed="research@example.com"
)

# Process each batch
for i in range(0, len(entries), batch_size):
    batch_entries = entries[i:i+batch_size]
    batch_num = i // batch_size + 1
    total_batches = (len(entries) + batch_size - 1) // batch_size
    
    print(f"\nProcessing batch {batch_num}/{total_batches} (entries {i+1}-{min(i+batch_size, len(entries))})...")
    
    # Write batch to temporary file
    batch_file = Path(f"temp_batch_{batch_num}.bib")
    
    # Convert entries back to BibTeX format
    bibtex_content = ""
    for entry in batch_entries:
        # Reconstruct BibTeX entry
        bibtex_content += f"@{entry['entry_type']}{{{entry['key']},\n"
        for field, value in entry['fields'].items():
            bibtex_content += f"  {field} = {{{value}}},\n"
        bibtex_content += "}\n\n"
    
    batch_file.write_text(bibtex_content)
    
    # Enhance this batch
    try:
        enhanced = scholar.enrich_bibtex(
            batch_file,
            backup=False,
            add_missing_abstracts=False,  # Skip abstracts to speed up
            add_missing_urls=False        # Skip URL updates to speed up
        )
        enhanced_collections.append(enhanced)
        
        # Summary for this batch
        doi_count = sum(1 for p in enhanced if p.doi)
        if_count = sum(1 for p in enhanced if p.impact_factor and p.impact_factor > 0)
        print(f"  - Found {doi_count} DOIs")
        print(f"  - Found {if_count} impact factors")
        
    except Exception as e:
        print(f"  - Error processing batch: {e}")
    finally:
        # Clean up temp file
        if batch_file.exists():
            batch_file.unlink()
    
    # Add delay between batches to avoid rate limits
    if batch_num < total_batches:
        import time
        print("  - Waiting 5 seconds before next batch...")
        time.sleep(5)

# Combine all enhanced papers
print("\n" + "="*60)
print("Combining all enhanced papers...")

all_papers = []
for collection in enhanced_collections:
    all_papers.extend(collection.papers)

# Create final collection
from scitex.scholar._core import Papers
final_collection = Papers(all_papers)

# Save enhanced BibTeX
output_path = "/home/ywatanabe/win/downloads/papers_enhanced_batch.bib"
final_collection.save(output_path)

# Summary
print(f"\nEnhancement complete!")
print(f"Total papers: {len(all_papers)}")
print(f"Papers with DOIs: {sum(1 for p in all_papers if p.doi)}")
print(f"Papers with impact factors: {sum(1 for p in all_papers if p.impact_factor and p.impact_factor > 0)}")
print(f"Papers with citations: {sum(1 for p in all_papers if p.citation_count)}")
print(f"\nEnhanced BibTeX saved to: {output_path}")