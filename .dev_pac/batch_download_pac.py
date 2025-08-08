#!/usr/bin/env python3
"""
Batch download PDFs for PAC collection.
Focuses on publishers with working download patterns.
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime


def download_all_pac_pdfs():
    """Download PDFs for all PAC papers using known working patterns."""
    
    library_dir = Path.home() / '.scitex' / 'scholar' / 'library'
    pac_dir = library_dir / 'pac'
    master_dir = library_dir / 'MASTER'
    
    # Statistics
    stats = {
        'total': 0,
        'already_have': 0,
        'downloaded': 0,
        'failed': 0,
        'no_doi': 0,
        'by_journal': {}
    }
    
    print("PAC Collection Batch PDF Downloader")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Process all papers
    for item in sorted(pac_dir.iterdir()):
        if not item.is_symlink() or item.name.startswith('.') or item.name == 'info':
            continue
        
        stats['total'] += 1
        
        # Get master path
        target = item.readlink()
        if target.parts[0] != '..':
            continue
            
        unique_id = target.parts[-1]
        master_path = master_dir / unique_id
        
        if not master_path.exists():
            continue
        
        # Check if PDF already exists
        pdf_files = list(master_path.glob('*.pdf'))
        if pdf_files:
            stats['already_have'] += 1
            print(f"[{stats['total']:3}] {item.name[:50]:<50} ✅ Already have PDF")
            continue
        
        # Load metadata
        metadata_file = master_path / 'metadata.json'
        if not metadata_file.exists():
            continue
            
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        journal = metadata.get('journal', 'Unknown')
        doi = metadata.get('doi', '')
        
        # Track by journal
        if journal not in stats['by_journal']:
            stats['by_journal'][journal] = {'total': 0, 'success': 0}
        stats['by_journal'][journal]['total'] += 1
        
        if not doi:
            stats['no_doi'] += 1
            print(f"[{stats['total']:3}] {item.name[:50]:<50} ❌ No DOI")
            continue
        
        # Generate filename
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        if authors and year:
            first_author = str(authors[0])
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            elif ' ' in first_author:
                first_author = first_author.split()[-1]
            import re
            first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
            filename = f"{first_author}-{year}.pdf"
        else:
            filename = f"{item.name}.pdf"
        
        output_path = master_path / filename
        
        # Try download based on journal
        success = False
        download_url = None
        
        journal_lower = journal.lower()
        
        # Scientific Reports / Nature
        if 'scientific reports' in journal_lower or 'nature communications' in journal_lower:
            article_id = doi.split('/')[-1]
            pdf_url = f'https://www.nature.com/articles/{article_id}.pdf'
            
            try:
                response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                if response.status_code == 200 and response.content[:4] == b'%PDF':
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    success = True
                    download_url = pdf_url
            except:
                pass
        
        # Frontiers journals
        elif 'frontiers' in journal_lower:
            pdf_urls = [
                f'https://doi.org/{doi}/pdf',
                f'https://www.frontiersin.org/articles/{doi}/pdf'
            ]
            for pdf_url in pdf_urls:
                try:
                    response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                    if response.status_code == 200 and response.content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                        download_url = pdf_url
                        break
                except:
                    pass
        
        # MDPI journals (Sensors, Mathematics, Diagnostics, Brain Sciences)
        elif any(j in journal_lower for j in ['sensors', 'mathematics', 'diagnostics', 'brain sciences', 'mdpi']):
            pdf_url = f'https://www.mdpi.com/{doi.split("/")[-1]}/pdf'
            
            try:
                response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                if response.status_code == 200 and response.content[:4] == b'%PDF':
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    success = True
                    download_url = pdf_url
            except:
                pass
        
        # BMC journals
        elif 'bmc' in journal_lower:
            pdf_urls = [
                f'https://doi.org/{doi}/pdf',
                f'https://bmcneurosci.biomedcentral.com/track/pdf/{doi}'
            ]
            for pdf_url in pdf_urls:
                try:
                    response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                    if response.status_code == 200 and response.content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                        download_url = pdf_url
                        break
                except:
                    pass
        
        # Hindawi journals
        elif 'hindawi' in journal_lower or 'computational intelligence' in journal_lower or 'applied bionics' in journal_lower:
            year = metadata.get('year', '')
            if year:
                pdf_url = f'https://downloads.hindawi.com/journals/{doi.split("/")[-1]}/{year}/{doi.split("/")[-1]}.pdf'
                
                try:
                    response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                    if response.status_code == 200 and response.content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                        download_url = pdf_url
                except:
                    pass
        
        # PeerJ
        elif 'peerj' in journal_lower:
            article_num = doi.split('.')[-1]
            if 'computer science' in journal_lower:
                pdf_urls = [
                    f'https://peerj.com/articles/cs-{article_num}.pdf',
                    f'https://doi.org/{doi}/pdf'
                ]
            else:
                pdf_urls = [
                    f'https://peerj.com/articles/{article_num}.pdf',
                    f'https://doi.org/{doi}/pdf'
                ]
            
            for pdf_url in pdf_urls:
                try:
                    response = requests.get(pdf_url, timeout=20, allow_redirects=True)
                    if response.status_code == 200 and response.content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        success = True
                        download_url = pdf_url
                        break
                except:
                    pass
        
        # Generic DOI attempt for other open access
        if not success and doi:
            try:
                pdf_url = f'https://doi.org/{doi}'
                response = requests.get(pdf_url, timeout=20, allow_redirects=True, headers={'Accept': 'application/pdf'})
                if response.status_code == 200 and response.content[:4] == b'%PDF':
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    success = True
                    download_url = pdf_url
            except:
                pass
        
        # Update statistics and metadata
        if success:
            stats['downloaded'] += 1
            stats['by_journal'][journal]['success'] += 1
            
            # Update metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            metadata['pdf_downloaded'] = True
            metadata['pdf_filename'] = filename
            metadata['pdf_download_url'] = download_url
            metadata['pdf_download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            file_size = output_path.stat().st_size / 1024 / 1024
            print(f"[{stats['total']:3}] {item.name[:50]:<50} ✅ Downloaded {file_size:.1f} MB")
        else:
            stats['failed'] += 1
            print(f"[{stats['total']:3}] {item.name[:50]:<50} ❌ Failed ({journal[:20]})")
        
        # Small delay between downloads
        if success:
            time.sleep(1)
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total papers: {stats['total']}")
    print(f"Already had PDFs: {stats['already_have']}")
    print(f"Successfully downloaded: {stats['downloaded']}")
    print(f"Failed to download: {stats['failed']}")
    print(f"Papers without DOI: {stats['no_doi']}")
    print()
    
    # Success by journal
    print("Success by Journal:")
    print("-" * 40)
    for journal, counts in sorted(stats['by_journal'].items(), key=lambda x: -x[1]['success']):
        if counts['success'] > 0:
            rate = counts['success'] / counts['total'] * 100
            print(f"{journal[:30]:<30} {counts['success']}/{counts['total']} ({rate:.0f}%)")
    
    print()
    print(f"Overall coverage: {(stats['already_have'] + stats['downloaded']) / stats['total'] * 100:.1f}%")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    download_all_pac_pdfs()