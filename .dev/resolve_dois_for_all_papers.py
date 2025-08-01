#!/usr/bin/env python3
"""Resolve DOIs for all 75 papers with resumable progress tracking."""

import subprocess
import sys
from pathlib import Path

# Create the Python script that will run the DOI resolution
script_content = '''
import sys
import os
sys.path.insert(0, 'src')

from pathlib import Path
from scitex import logging
from scitex.scholar.doi._ResumableDOIResolver import ResumableDOIResolver

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the BibTeX file
bibtex_file = Path("src/scitex/scholar/docs/papers.bib")

if not bibtex_file.exists():
    logger.error(f"BibTeX file not found: {bibtex_file}")
    sys.exit(1)

logger.info(f"Loading papers from: {bibtex_file}")

# Initialize resumable DOI resolver
resolver = ResumableDOIResolver(
    progress_file=Path(".dev/doi_resolution_progress.json")
)

# Resolve DOIs from BibTeX
results = resolver.resolve_from_bibtex(bibtex_file)

# Save results
import json
output_file = Path(".dev/resolved_dois.json")
output_data = {
    "total_papers": resolver.progress_data["statistics"]["total"],
    "resolved": resolver.progress_data["statistics"]["resolved"],
    "failed": resolver.progress_data["statistics"]["failed"],
    "dois": results
}

with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

logger.info(f"\\nResults saved to: {output_file}")

# Create enriched BibTeX file with DOIs
if results:
    from scitex.io import load, save
    
    # Load original entries
    entries = load(str(bibtex_file))
    
    # Add DOIs to entries
    updated_count = 0
    for entry in entries:
        title = entry.get('fields', {}).get('title', '')
        if title in results:
            entry['fields']['doi'] = results[title]
            entry['fields']['doi_source'] = 'ResumableDOIResolver'
            updated_count += 1
    
    # Save enriched BibTeX
    enriched_file = Path(".dev/papers_with_dois.bib")
    save(entries, str(enriched_file))
    logger.info(f"Created enriched BibTeX with {updated_count} DOIs: {enriched_file}")
'''

# Save the script
script_path = Path('.dev/run_doi_resolver.py')
with open(script_path, 'w') as f:
    f.write(script_content)

print(f"Created script: {script_path}")
print("\nRunning DOI resolver with resumable progress tracking...")
print("This will show rsync-like progress with ETA\n")
print("="*60)

# Run the script
try:
    result = subprocess.run(
        ['python', str(script_path)], 
        text=True,
        check=False
    )
    
    print("\n" + "="*60)
    print("DOI resolution completed!")
    print("\nCheck these files for results:")
    print("  - .dev/doi_resolution_progress.json (progress tracking)")
    print("  - .dev/resolved_dois.json (resolved DOIs)")
    print("  - .dev/papers_with_dois.bib (enriched BibTeX)")
    
except KeyboardInterrupt:
    print("\n\nProcess interrupted! Don't worry - progress was saved.")
    print("Run this script again to resume from where it left off.")
    print("Progress file: .dev/doi_resolution_progress.json")