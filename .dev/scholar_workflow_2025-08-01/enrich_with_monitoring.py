#!/usr/bin/env python3
"""Enrich papers with monitoring and error handling."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scitex.scholar import enrich_bibtex

def main():
    input_file = "src/scitex/scholar/docs/papers.bib"
    output_file = "src/scitex/scholar/docs/papers-enriched.bib"
    
    print(f"Starting enrichment of {input_file}")
    print(f"Output will be saved to {output_file}")
    
    start_time = time.time()
    
    # Run enrichment with minimal arguments
    enrich_bibtex(
        input_file,
        output_file
    )
    
    elapsed_time = time.time() - start_time
    print(f"\nEnrichment completed in {elapsed_time:.2f} seconds")
    print(f"Check output at: {output_file}")

if __name__ == "__main__":
    main()