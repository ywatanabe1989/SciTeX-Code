#!/usr/bin/env python3
"""
Enrich all 75 papers from the BibTeX file with DOIs and metadata.
Step 7 of the Scholar workflow.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scitex.scholar import enrich_bibtex

# Input and output files
input_file = "src/scitex/scholar/docs/from_user/papers.bib"
output_file = "src/scitex/scholar/docs/papers-enriched.bib"

print(f"Enriching BibTeX file: {input_file}")
print(f"Output will be saved to: {output_file}")

# Run enrichment
try:
    enrich_bibtex(
        input_file,
        output_file
    )
    print("\n✓ Enrichment completed successfully!")
    print(f"Enriched BibTeX saved to: {output_file}")
except Exception as e:
    print(f"\n✗ Error during enrichment: {e}")
    import traceback
    traceback.print_exc()