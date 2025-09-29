#!/usr/bin/env python3
"""Check detailed PDF status."""

import json
from pathlib import Path

pac_dir = Path.home() / '.scitex/scholar/library/pac'

with_pdf = []
without_pdf = []

for item in sorted(pac_dir.iterdir()):
    if item.is_symlink():
        target = item.resolve()
        if target.exists():
            pdfs = list(target.glob('*.pdf'))
            metadata_file = target / 'metadata.json'
            
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                
                if pdfs:
                    with_pdf.append(item.name)
                else:
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:
                        without_pdf.append((item.name, journal))

print("Papers WITH PDFs:")
for name in with_pdf[:10]:
    print(f"  ✓ {name}")
if len(with_pdf) > 10:
    print(f"  ... and {len(with_pdf) - 10} more")

print(f"\nTotal with PDFs: {len(with_pdf)}")

print("\nPapers WITHOUT PDFs (first 10):")
for name, journal in without_pdf[:10]:
    print(f"  ✗ {name}")
    print(f"    {journal}")

print(f"\nTotal without PDFs: {len(without_pdf)}")