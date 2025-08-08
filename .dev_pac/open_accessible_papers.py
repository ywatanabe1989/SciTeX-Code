#!/usr/bin/env python3
"""Open papers that ARE accessible through OpenAthens subscription."""

import json
import subprocess
import time
from pathlib import Path

library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
pac_dir = library_dir / 'pac'

# Get papers still needing PDFs
papers_to_open = []

for item in sorted(pac_dir.iterdir()):
    if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
        master_path = library_dir / 'MASTER' / item.readlink().parts[-1]
        if master_path.exists() and not list(master_path.glob('*.pdf')):
            metadata_file = master_path / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                doi = metadata.get('doi', '')
                if doi:
                    journal = metadata.get('journal', '')
                    url = f'https://doi.org/{doi}' if not doi.startswith('http') else doi
                    
                    # Skip IEEE (not subscribed)
                    if 'IEEE' in journal:
                        continue
                    
                    # Focus on likely accessible journals
                    # Elsevier, Nature, Springer, Oxford, etc. ARE usually subscribed
                    if any(x in journal.lower() for x in [
                        'elsevier', 'epilepsy', 'progress in neurobiology',
                        'nature', 'springer', 'oxford', 'brain',
                        'journal of neural', 'journal of neuroscience',
                        'cognitive', 'biomedical', 'engineering',
                        'frontiers', 'peerj', 'hindawi', 'bmc'
                    ]):
                        papers_to_open.append({
                            'name': item.name,
                            'journal': journal,
                            'url': url
                        })

print(f'Found {len(papers_to_open)} potentially accessible papers')

# Group by publisher type
elsevier = [p for p in papers_to_open if any(x in p['journal'].lower() for x in ['elsevier', 'epilepsy', 'progress', 'engineering'])]
nature = [p for p in papers_to_open if 'nature' in p['journal'].lower()]
neuro = [p for p in papers_to_open if any(x in p['journal'].lower() for x in ['neuroscience', 'neural', 'brain', 'cognitive'])]
other = [p for p in papers_to_open if p not in elsevier and p not in nature and p not in neuro]

print(f'\nBreakdown:')
print(f'  Elsevier journals: {len(elsevier)}')
print(f'  Nature journals: {len(nature)}')
print(f'  Neuroscience journals: {len(neuro)}')
print(f'  Other accessible: {len(other)}')

# Open in Chrome
profile_dir = Path.home() / '.scitex' / 'scholar' / 'cache' / 'chrome'

print('\nOpening Elsevier papers (likely subscribed):')
for paper in elsevier[:5]:
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

print('\nOpening Nature papers:')
for paper in nature[:3]:
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

print('\n✅ Papers opened in Chrome with OpenAthens authentication')
print('\nTO CAPTURE:')
print('1. Click Zotero Connector icon in Chrome toolbar')
print('2. Right-click → Save All Tabs to Zotero')
print('3. PDFs should download for subscribed journals')
print('\nNOTE: IEEE papers skipped (not subscribed)')