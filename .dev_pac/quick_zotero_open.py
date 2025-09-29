#!/usr/bin/env python3
"""Quick script to open papers in Chrome for Zotero capture."""

import json
import subprocess
import time
from pathlib import Path

library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
pac_dir = library_dir / 'pac'

# Get papers without PDFs
papers_to_open = []
for item in sorted(pac_dir.iterdir()):
    if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
        master_path = library_dir / 'MASTER' / item.readlink().parts[-1]
        if master_path.exists():
            pdf_files = list(master_path.glob('*.pdf'))
            if not pdf_files:  # No PDF yet
                metadata_file = master_path / 'metadata.json'
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    doi = metadata.get('doi', '')
                    if doi:
                        papers_to_open.append({
                            'name': item.name,
                            'journal': metadata.get('journal', 'Unknown'),
                            'url': f'https://doi.org/{doi}' if not doi.startswith('http') else doi
                        })

print(f'Found {len(papers_to_open)} papers without PDFs')

# Group by publisher
ieee = [p for p in papers_to_open if 'IEEE' in p['journal']]
elsevier = [p for p in papers_to_open if any(x in p['journal'].lower() for x in ['elsevier', 'epilepsy', 'progress in neurobiology'])]

print(f'IEEE papers: {len(ieee)}')
print(f'Elsevier papers: {len(elsevier)}')

# Open IEEE papers first (they need auth)
profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'

print('\nOpening IEEE papers in Chrome...')
for paper in ieee[:5]:  # First 5 IEEE papers
    print(f'  {paper["name"][:50]}')
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
        '--new-tab',
        paper['url']
    ]
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

print('\n✅ Papers opened in Chrome with Zotero Connector!')
print('\nTO SAVE TO ZOTERO:')
print('1. Go to Chrome')
print('2. Click Zotero Connector icon in toolbar')
print('3. Papers will save with metadata + PDFs (if accessible)')
print('\nTIP: Right-click Zotero icon → Save All Tabs to Zotero')