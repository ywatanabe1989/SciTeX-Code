#!/usr/bin/env python3
"""Organize existing PDF into enhanced storage structure."""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import os

def organize_hulsemann_paper():
    """Organize the already downloaded Hülsemann paper."""
    print("=" * 80)
    print("ORGANIZING EXISTING PDF INTO ENHANCED STORAGE")
    print("=" * 80)
    
    # Paths
    existing_pdf = Path("/home/ywatanabe/.scitex/scholar/pdfs/Hlsemann2019QuantificationOPA.pdf")
    
    # Base directories
    scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
    library_dir = scitex_dir / "scholar" / "library"
    
    # Use the existing storage directory
    storage_base = library_dir / "storage"
    
    # Generate storage key for this paper
    storage_key = "HLSE2019"  # Using a meaningful key based on author/year
    storage_dir = storage_base / storage_key
    
    print(f"\n1. SETTING UP STORAGE")
    print("-" * 40)
    print(f"Existing PDF: {existing_pdf}")
    print(f"Storage key: {storage_key}")
    print(f"Storage directory: {storage_dir}")
    
    # Create storage directory
    storage_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = storage_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Paper metadata from BibTeX
    metadata = {
        "storage_key": storage_key,
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling",
        "authors": ["Hülsemann, Mareike J.", "Naumann, E.", "Rasch, B."],
        "journal": "Frontiers in Neuroscience",
        "year": 2019,
        "volume": "13",
        "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096",
        "doi": "10.3389/fnins.2019.00573",  # Known DOI
        "bibtex_key": "Hlsemann2019QuantificationOPA"
    }
    
    # Save metadata
    metadata_path = storage_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n2. COPYING PDF WITH ORIGINAL FILENAME")
    print("-" * 40)
    
    # Determine the original filename (from Frontiers)
    original_filename = "fnins-13-00573.pdf"
    dest_path = storage_dir / original_filename
    
    print(f"Copying to: {dest_path}")
    shutil.copy2(existing_pdf, dest_path)
    
    # Create storage metadata
    with open(dest_path, 'rb') as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()
    
    storage_metadata = {
        "storage_key": storage_key,
        "filename": original_filename,
        "original_filename": original_filename,
        "source_filename": existing_pdf.name,
        "pdf_url": f"https://doi.org/{metadata['doi']}",
        "pdf_hash": pdf_hash,
        "size_bytes": dest_path.stat().st_size,
        "stored_at": datetime.now().isoformat()
    }
    
    storage_metadata_path = storage_dir / "storage_metadata.json"
    with open(storage_metadata_path, 'w') as f:
        json.dump(storage_metadata, f, indent=2)
    
    print(f"Size: {storage_metadata['size_bytes']:,} bytes")
    print(f"Hash: {pdf_hash[:16]}...")
    
    # Create human-readable link
    print("\n3. CREATING HUMAN-READABLE LINK")
    print("-" * 40)
    
    # Create storage-human-readable directory at library level
    human_readable_base = library_dir / "storage-human-readable"
    human_readable_base.mkdir(exist_ok=True)
    
    # Generate citation name
    citation_name = "Hulsemann-2019-FrontNeurosci-HLSE"
    link_path = human_readable_base / citation_name
    
    # Create relative symlink
    relative_target = Path("../storage") / storage_key
    
    if link_path.exists():
        link_path.unlink()
    
    try:
        link_path.symlink_to(relative_target)
        print(f"Created symlink: {citation_name} -> {relative_target}")
    except Exception as e:
        print(f"Could not create symlink: {e}")
    
    # Show final structure
    print("\n4. FINAL STRUCTURE")
    print("-" * 40)
    
    print(f"\nStorage directory contents:")
    for item in sorted(storage_dir.iterdir()):
        if item.is_dir():
            print(f"  {item.name}/")
        else:
            size_kb = item.stat().st_size / 1024
            print(f"  {item.name} ({size_kb:.1f} KB)")
    
    print(f"\nHuman-readable links:")
    if human_readable_base.exists():
        for link in sorted(human_readable_base.iterdir()):
            if storage_key in str(link.resolve()):
                print(f"  {link.name} -> {link.resolve().relative_to(library_dir)}")
    
    # Create an index entry
    print("\n5. CREATING INDEX ENTRY")
    print("-" * 40)
    
    index_path = library_dir / "paper_index.json"
    
    # Load existing index or create new
    if index_path.exists():
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {"papers": {}}
    
    # Add this paper
    index["papers"][storage_key] = {
        "title": metadata["title"],
        "authors": metadata["authors"],
        "year": metadata["year"],
        "doi": metadata["doi"],
        "storage_key": storage_key,
        "pdf_filename": original_filename,
        "human_readable_link": citation_name,
        "indexed_at": datetime.now().isoformat()
    }
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Added to index: {index_path}")
    
    print("\n✓ Successfully organized existing PDF!")
    print(f"\nThe paper is now available at:")
    print(f"  Storage: {storage_dir}")
    print(f"  Human-readable: {link_path}")
    print(f"  PDF: {dest_path}")
    
    return {
        "storage_key": storage_key,
        "storage_dir": str(storage_dir),
        "pdf_path": str(dest_path),
        "link_path": str(link_path)
    }


if __name__ == "__main__":
    result = organize_hulsemann_paper()
    
    # Save result for reference
    with open(".dev/organized_paper_info.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nOrganization info saved to: .dev/organized_paper_info.json")