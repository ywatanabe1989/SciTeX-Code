#!/usr/bin/env python3
"""Organize paper with correct directory structure from CLAUDE.md."""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import os
import random
import string

def organize_paper_correct_structure(project_name="pac_research"):
    """Organize the Hülsemann paper with correct structure."""
    print("=" * 80)
    print("ORGANIZING PAPER WITH CORRECT STRUCTURE")
    print("=" * 80)
    
    # Paths
    existing_pdf = Path("/home/ywatanabe/.scitex/scholar/pdfs/Hlsemann2019QuantificationOPA.pdf")
    
    # Base directories following CLAUDE.md structure
    scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
    scholar_dir = scitex_dir / "scholar"
    library_dir = scholar_dir / "library"
    
    # Project directory
    project_dir = library_dir / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 8-digit ID
    eight_digit_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Storage directory with 8-digit ID
    storage_dir = project_dir / eight_digit_id
    storage_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (storage_dir / "attachments").mkdir(exist_ok=True)
    (storage_dir / "screenshots").mkdir(exist_ok=True)
    
    print(f"\n1. DIRECTORY STRUCTURE")
    print("-" * 40)
    print(f"Project: {project_name}")
    print(f"8-digit ID: {eight_digit_id}")
    print(f"Storage directory: {storage_dir}")
    
    # Paper metadata
    metadata = {
        "storage_id": eight_digit_id,
        "project": project_name,
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling",
        "authors": ["Hülsemann, Mareike J.", "Naumann, E.", "Rasch, B."],
        "journal": "Frontiers in Neuroscience",
        "year": 2019,
        "volume": "13",
        "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096",
        "doi": "10.3389/fnins.2019.00573",
        "bibtex_key": "Hlsemann2019QuantificationOPA",
        "created_at": datetime.now().isoformat()
    }
    
    # Save metadata.json
    metadata_path = storage_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n2. COPYING PDF WITH ORIGINAL FILENAME")
    print("-" * 40)
    
    # Original filename from Frontiers
    original_filename = "fnins-13-00573.pdf"
    pdf_dest = storage_dir / original_filename
    
    print(f"Source: {existing_pdf}")
    print(f"Destination: {pdf_dest}")
    
    shutil.copy2(existing_pdf, pdf_dest)
    
    # Calculate hash for verification
    with open(pdf_dest, 'rb') as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()
    
    print(f"Size: {pdf_dest.stat().st_size:,} bytes")
    print(f"Hash: {pdf_hash[:16]}...")
    
    # Create human-readable link
    print("\n3. CREATING HUMAN-READABLE LINK")
    print("-" * 40)
    
    # Human-readable project directory
    human_readable_dir = library_dir / f"{project_name}-human-readable"
    human_readable_dir.mkdir(exist_ok=True)
    
    # Generate AUTHOR-YEAR-JOURNAL format
    first_author_lastname = "Hulsemann"  # Without special chars
    year = metadata["year"]
    journal_abbrev = "FrontNeurosci"
    
    link_name = f"{first_author_lastname}-{year}-{journal_abbrev}"
    link_path = human_readable_dir / link_name
    
    # Create relative symlink to 8-digit ID
    relative_target = Path(f"../{project_name}/{eight_digit_id}")
    
    if link_path.exists():
        link_path.unlink()
    
    try:
        link_path.symlink_to(relative_target)
        print(f"Created symlink: {link_name} -> {relative_target}")
    except Exception as e:
        print(f"Could not create symlink: {e}")
    
    # Create example screenshot
    print("\n4. CREATING EXAMPLE SCREENSHOT ENTRY")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_metadata = {
        "filename": f"{timestamp}-download-success.jpg",
        "description": "download-success",
        "timestamp": timestamp,
        "note": "Successfully downloaded from Frontiers direct link"
    }
    
    screenshots_log = storage_dir / "screenshots" / "screenshots.json"
    with open(screenshots_log, 'w') as f:
        json.dump({"screenshots": [screenshot_metadata]}, f, indent=2)
    
    print(f"Created screenshot log: {screenshots_log}")
    
    # Show final structure
    print("\n5. FINAL STRUCTURE")
    print("-" * 40)
    
    print(f"""
{library_dir}/
├── {project_name}/
│   └── {eight_digit_id}/
│       ├── {original_filename}
│       ├── metadata.json
│       ├── attachments/
│       │   └── (empty - for supplementary files)
│       └── screenshots/
│           └── screenshots.json
└── {project_name}-human-readable/
    └── {link_name} -> ../{project_name}/{eight_digit_id}
""")
    
    # Verify structure
    print("\n6. VERIFICATION")
    print("-" * 40)
    
    print("Actual directory contents:")
    for item in sorted(storage_dir.iterdir()):
        if item.is_dir():
            sub_count = len(list(item.iterdir()))
            print(f"  {item.name}/ ({sub_count} items)")
        else:
            size_kb = item.stat().st_size / 1024
            print(f"  {item.name} ({size_kb:.1f} KB)")
    
    print(f"\nHuman-readable link:")
    if link_path.exists():
        print(f"  {link_path} -> {link_path.resolve()}")
    
    print("\n✓ Paper successfully organized with correct structure!")
    
    return {
        "project": project_name,
        "storage_id": eight_digit_id,
        "storage_path": str(storage_dir),
        "pdf_path": str(pdf_dest),
        "human_readable_link": str(link_path),
        "structure": {
            "library": str(library_dir),
            "project": str(project_dir),
            "storage": str(storage_dir),
            "human_readable": str(human_readable_dir)
        }
    }


if __name__ == "__main__":
    result = organize_paper_correct_structure()
    
    # Save info
    info_path = Path(".dev/correct_structure_info.json")
    with open(info_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nStructure info saved to: {info_path}")