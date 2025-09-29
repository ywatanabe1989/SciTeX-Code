#!/usr/bin/env python3
"""
Sync PDFs from Linux Zotero library to Scholar library structure.
Copies PDFs from ~/Zotero/storage/* to ~/.scitex/scholar/library/pac/*/
"""

import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Optional

def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of file for duplicate detection."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def find_matching_paper(pdf_path: Path, pac_dir: Path) -> Optional[Path]:
    """Find matching paper in PAC collection based on title/author."""
    
    # Extract info from PDF filename
    pdf_name = pdf_path.stem
    
    # Common patterns in Zotero filenames
    # "Author et al. - Year - Title.pdf"
    # "Author et al. - Title.pdf"
    
    parts = pdf_name.split(' - ')
    if len(parts) >= 2:
        author_part = parts[0].split(' et al.')[0].split(' ')[0] if ' et al.' in parts[0] else parts[0].split(' ')[0]
        
        # Search for matching paper in PAC collection
        for item in pac_dir.iterdir():
            if item.is_symlink():
                # Check if author matches symlink name
                if author_part.lower() in item.name.lower():
                    return item.resolve()
                
                # Check metadata
                target_dir = item.resolve()
                if target_dir.exists():
                    metadata_file = target_dir / 'metadata.json'
                    if metadata_file.exists():
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        # Check title match
                        title = metadata.get('title', '')
                        if len(parts) >= 2:
                            title_part = parts[-1].lower()
                            if any(word in title.lower() for word in title_part.split()[:5]):
                                return target_dir
                        
                        # Check author match
                        authors = metadata.get('author', '')
                        if author_part.lower() in authors.lower():
                            return target_dir
    
    return None

def sync_pdfs():
    """Sync PDFs from Zotero to Scholar library."""
    
    zotero_dir = Path.home() / 'Zotero/storage'
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    
    if not zotero_dir.exists():
        print("❌ Zotero directory not found")
        return
    
    print("=" * 60)
    print("SYNCING ZOTERO PDFs TO SCHOLAR LIBRARY")
    print("=" * 60)
    
    # Find all PDFs in Zotero
    pdf_files = list(zotero_dir.glob('*/*.pdf'))
    print(f"\nFound {len(pdf_files)} PDFs in Zotero library")
    
    # Track unique PDFs (by hash)
    unique_pdfs = {}
    for pdf_path in pdf_files:
        file_hash = get_file_hash(pdf_path)
        if file_hash not in unique_pdfs:
            unique_pdfs[file_hash] = pdf_path
    
    print(f"Found {len(unique_pdfs)} unique PDFs (excluding duplicates)")
    
    # Sync each unique PDF
    synced = 0
    not_matched = []
    
    for file_hash, pdf_path in unique_pdfs.items():
        print(f"\nProcessing: {pdf_path.name[:50]}...")
        
        # Find matching paper in PAC collection
        target_dir = find_matching_paper(pdf_path, pac_dir)
        
        if target_dir:
            # Check if PDF already exists
            existing_pdfs = list(target_dir.glob('*.pdf'))
            
            if existing_pdfs:
                print(f"  → PDF already exists in {target_dir.name}")
            else:
                # Copy PDF to target directory
                dest_path = target_dir / 'main.pdf'
                shutil.copy2(pdf_path, dest_path)
                print(f"  ✅ Copied to {target_dir.name}/main.pdf")
                synced += 1
        else:
            print(f"  ⚠️  No matching paper found")
            not_matched.append(pdf_path.name)
    
    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"Total PDFs in Zotero: {len(pdf_files)}")
    print(f"Unique PDFs: {len(unique_pdfs)}")
    print(f"Newly synced: {synced}")
    print(f"Not matched: {len(not_matched)}")
    
    if not_matched:
        print("\nUnmatched PDFs:")
        for name in not_matched[:5]:
            print(f"  - {name[:60]}")
        if len(not_matched) > 5:
            print(f"  ... and {len(not_matched) - 5} more")
    
    # Check final status
    print("\nChecking PAC collection status...")
    pdfs_in_pac = 0
    for item in pac_dir.iterdir():
        if item.is_symlink():
            target = item.resolve()
            if target.exists() and list(target.glob('*.pdf')):
                pdfs_in_pac += 1
    
    print(f"PAC papers with PDFs: {pdfs_in_pac}/66")

def main():
    """Run sync process."""
    sync_pdfs()
    
    # Show final status
    print("\nRun this to see full status:")
    print("  python .dev_pac/final_status.py")

if __name__ == "__main__":
    main()