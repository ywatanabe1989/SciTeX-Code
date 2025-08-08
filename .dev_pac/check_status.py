#!/usr/bin/env python3
"""Check download status of PAC collection."""

from pathlib import Path

library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
pac_dir = library_dir / 'pac'
master_dir = library_dir / 'MASTER'

total = 0
with_pdf = 0
without_pdf = 0
by_journal = {}

for item in sorted(pac_dir.iterdir()):
    if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
        total += 1
        target = item.readlink()
        if target.parts[0] == '..':
            master_path = master_dir / target.parts[-1]
            if master_path.exists():
                pdf_files = list(master_path.glob('*.pdf'))
                
                # Get journal from metadata
                metadata_file = master_path / 'metadata.json'
                journal = 'Unknown'
                if metadata_file.exists():
                    import json
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        journal = metadata.get('journal', 'Unknown')
                
                if journal not in by_journal:
                    by_journal[journal] = {'total': 0, 'with_pdf': 0}
                by_journal[journal]['total'] += 1
                
                if pdf_files:
                    with_pdf += 1
                    by_journal[journal]['with_pdf'] += 1
                    print(f"✅ {item.name[:50]:<50} [{pdf_files[0].name}]")
                else:
                    without_pdf += 1

print()
print("=" * 60)
print(f'Total papers: {total}')
print(f'Have PDFs: {with_pdf}')
print(f'Missing PDFs: {without_pdf}')
print(f'Coverage: {with_pdf/total*100:.1f}%')
print()

print("Success by Journal:")
print("-" * 40)
for journal, counts in sorted(by_journal.items(), key=lambda x: -x[1]['with_pdf']):
    if counts['with_pdf'] > 0:
        rate = counts['with_pdf'] / counts['total'] * 100
        print(f"{journal[:35]:<35} {counts['with_pdf']}/{counts['total']} ({rate:.0f}%)")