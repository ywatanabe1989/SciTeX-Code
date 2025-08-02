#!/usr/bin/env python3
"""Complete the paper storage after manual download."""

import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

def complete_storage(pdf_path: Path, original_filename: str = None):
    """Complete storage after downloading PDF."""
    print("=" * 80)
    print("COMPLETING PAPER STORAGE")
    print("=" * 80)
    
    # Load demo info
    with open(".dev/demo_info.json", 'r') as f:
        info = json.load(f)
    
    storage_dir = Path(info["storage_dir"])
    base_dir = Path(info["base_dir"])
    storage_key = info["storage_key"]
    
    # Load metadata
    with open(storage_dir / "metadata.json", 'r') as f:
        metadata = json.load(f)
    
    print(f"\nPaper: {metadata['title'][:60]}...")
    print(f"Storage key: {storage_key}")
    
    # Step 1: Copy PDF to storage
    print("\n1. STORING PDF")
    print("-" * 40)
    
    if not pdf_path.exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        return False
    
    # Determine filename
    if not original_filename:
        original_filename = pdf_path.name
    
    dest_path = storage_dir / original_filename
    print(f"Copying PDF:")
    print(f"  From: {pdf_path}")
    print(f"  To: {dest_path}")
    
    shutil.copy2(pdf_path, dest_path)
    
    # Step 2: Create storage metadata
    print("\n2. CREATING STORAGE METADATA")
    print("-" * 40)
    
    # Calculate hash
    with open(dest_path, 'rb') as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()
    
    storage_metadata = {
        "storage_key": storage_key,
        "filename": original_filename,
        "original_filename": original_filename,
        "pdf_url": metadata.get("doi", ""),
        "pdf_hash": pdf_hash,
        "size_bytes": dest_path.stat().st_size,
        "stored_at": datetime.now().isoformat()
    }
    
    storage_metadata_path = storage_dir / "storage_metadata.json"
    with open(storage_metadata_path, 'w') as f:
        json.dump(storage_metadata, f, indent=2)
    
    print(f"Created storage metadata:")
    print(f"  Size: {storage_metadata['size_bytes']:,} bytes")
    print(f"  Hash: {pdf_hash[:16]}...")
    
    # Step 3: Create human-readable link
    print("\n3. CREATING HUMAN-READABLE LINK")
    print("-" * 40)
    
    # Generate citation name
    first_author = metadata["authors"][0].split(",")[0].strip()
    first_author = "".join(c for c in first_author if c.isalnum())
    year = metadata["year"]
    journal = metadata["journal"]
    
    # Abbreviate journal
    journal_abbrev = {
        "Frontiers in Neuroscience": "FrontNeurosci",
        "Nature": "Nature",
        "Science": "Science",
        "Cell": "Cell"
    }.get(journal, journal.replace(" ", "")[:12])
    
    citation_name = f"{first_author}-{year}-{journal_abbrev}-{storage_key[:4]}"
    
    # Create human-readable directory
    human_readable_dir = base_dir / "storage-human-readable"
    human_readable_dir.mkdir(exist_ok=True)
    
    # Create symlink
    link_path = human_readable_dir / citation_name
    relative_target = Path("../storage") / storage_key
    
    if link_path.exists():
        link_path.unlink()
    
    try:
        link_path.symlink_to(relative_target)
        print(f"Created symlink:")
        print(f"  {citation_name} -> {relative_target}")
    except Exception as e:
        print(f"Note: Could not create symlink (may not be supported): {e}")
    
    # Step 4: Update metadata status
    print("\n4. UPDATING STATUS")
    print("-" * 40)
    
    metadata["status"] = "complete"
    metadata["pdf_filename"] = original_filename
    metadata["pdf_stored_at"] = datetime.now().isoformat()
    
    with open(storage_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("Updated status to: complete")
    
    # Step 5: Show final structure
    print("\n5. FINAL STORAGE STRUCTURE")
    print("-" * 40)
    
    print(f"\n{storage_dir}/")
    for item in sorted(storage_dir.iterdir()):
        if item.is_dir():
            print(f"├── {item.name}/")
            for subitem in sorted(item.iterdir())[:3]:
                print(f"│   └── {subitem.name}")
        else:
            size_kb = item.stat().st_size / 1024
            print(f"├── {item.name} ({size_kb:.1f} KB)")
    
    print(f"\n{human_readable_dir}/")
    for link in sorted(human_readable_dir.iterdir()):
        if storage_key in str(link):
            print(f"└── {link.name} -> {link.resolve().relative_to(base_dir)}")
    
    print("\n✓ Paper successfully stored and organized!")
    print(f"\nYou can now access the PDF at:")
    print(f"  Direct: {dest_path}")
    print(f"  Human-readable: {link_path}")
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python complete_paper_storage.py <path_to_downloaded_pdf> [original_filename]")
        print("\nExample:")
        print("  python complete_paper_storage.py ~/Downloads/fnins-13-00573.pdf")
        print("\nOr if you want to specify a different original filename:")
        print("  python complete_paper_storage.py ~/Downloads/downloaded.pdf fnins-13-00573.pdf")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1]).expanduser()
    original_filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    complete_storage(pdf_path, original_filename)