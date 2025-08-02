#!/usr/bin/env python3
"""Debug title matching issues."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar.doi_resolver import DOIResolver

# The paper we know has a DOI
title1 = "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies"
title2 = "Measuring phase-amplitude coupling between neuronal oscillations of different frequencies."  # With period

resolver = DOIResolver()

print("Testing title variations:")
print("=" * 60)

# Test without period
print(f"\n1. Without period: '{title1}'")
doi1 = resolver.title_to_doi(title1, year=2010)
print(f"   Result: {doi1 if doi1 else 'Not found'}")

# Test with period
print(f"\n2. With period: '{title2}'")
doi2 = resolver.title_to_doi(title2, year=2010)
print(f"   Result: {doi2 if doi2 else 'Not found'}")

# Test with different sources
print(f"\n3. Testing individual sources:")
for source in ['crossref', 'pubmed', 'openalex']:
    doi = resolver.title_to_doi(title2, year=2010, sources=(source,))
    print(f"   {source}: {doi if doi else 'Not found'}")