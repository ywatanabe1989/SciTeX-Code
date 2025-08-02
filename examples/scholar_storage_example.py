#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/examples/scholar_storage_example.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/scholar_storage_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Example of enhanced storage system with original filename preservation.

Demonstrates:
1. Storing PDFs with original filenames
2. Creating human-readable links
3. Using the lookup index
4. Browser download helper integration
"""

from pathlib import Path
import tempfile

from scitex.scholar.storage import EnhancedStorageManager
from scitex.scholar.lookup import get_default_lookup
from scitex.scholar.download import BrowserDownloadHelper


def example_pdf_storage():
    """Example of storing PDFs with original filenames."""
    print("=" * 60)
    print("Enhanced Storage Example")
    print("=" * 60)
    
    # Initialize components
    storage = EnhancedStorageManager()
    lookup = get_default_lookup()
    
    # Example paper metadata
    paper_metadata = {
        "storage_key": "ABCD1234",
        "doi": "10.1038/s41586-023-06312-0",
        "title": "Quantum entanglement in neural networks",
        "authors": ["Smith, John", "Doe, Jane", "Brown, Alice"],
        "year": 2023,
        "journal": "Nature"
    }
    
    # Simulate storing a PDF with original filename
    print("\n1. Storing PDF with original filename from journal:")
    
    # Create a dummy PDF for demonstration
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(b"PDF content here")
        tmp_path = Path(tmp.name)
    
    try:
        # Store with original filename
        stored_path = storage.store_pdf(
            storage_key="ABCD1234",
            pdf_path=tmp_path,
            original_filename="s41586-023-06312-0.pdf",  # Nature's naming convention
            pdf_url="https://www.nature.com/articles/s41586-023-06312-0.pdf",
            paper_metadata=paper_metadata
        )
        
        print(f"  Stored at: {stored_path}")
        print(f"  Human-readable link: Smith-2023-Nature-ABCD -> storage/ABCD1234")
        
        # Update lookup index
        lookup.add_entry(
            storage_key="ABCD1234",
            doi=paper_metadata["doi"],
            title=paper_metadata["title"],
            authors=paper_metadata["authors"],
            year=paper_metadata["year"],
            has_pdf=True,
            pdf_size=stored_path.stat().st_size
        )
        
        lookup.mark_pdf_downloaded(
            storage_key="ABCD1234",
            pdf_size=stored_path.stat().st_size,
            pdf_filename="s41586-023-06312-0.pdf",
            original_filename="s41586-023-06312-0.pdf"
        )
        
    finally:
        tmp_path.unlink()
    
    print("\n2. Storage structure created:")
    print("""
    storage/
    └── ABCD1234/
        ├── s41586-023-06312-0.pdf    # Original filename preserved
        └── storage_metadata.json      # Metadata about the file
        
    storage-human-readable/
    └── Smith-2023-Nature-ABCD -> ../storage/ABCD1234
    """)
    
    # Show how to retrieve
    print("\n3. Retrieving PDF information:")
    pdf_info = storage.get_pdf_info("ABCD1234")
    if pdf_info:
        print(f"  Filename: {pdf_info['filename']}")
        print(f"  Original: {pdf_info['original_filename']}")
        print(f"  Size: {pdf_info['size_bytes']} bytes")
        print(f"  Hash: {pdf_info['pdf_hash'][:16]}...")
    
    # Show lookup functionality
    print("\n4. Quick lookup by DOI:")
    storage_key = lookup.lookup_by_doi("10.1038/s41586-023-06312-0")
    print(f"  DOI -> Storage key: {storage_key}")
    
    # Show statistics
    print("\n5. Storage statistics:")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_browser_download_workflow():
    """Example of browser download workflow."""
    print("\n" + "=" * 60)
    print("Browser Download Workflow Example")
    print("=" * 60)
    
    print("""
    When automated downloads fail due to authentication:
    
    1. Create download session:
       $ python -m scitex.scholar.download create --max-papers 20
       
    2. Open papers in browser (10 at a time):
       $ python -m scitex.scholar.download open SESSION_ID --batch 0
       
    3. Or use HTML helper page:
       $ python -m scitex.scholar.download html SESSION_ID
       
    The HTML page will:
    - Show all papers needing PDFs
    - Provide multiple URL options (OpenURL, DOI, Google Scholar)
    - Track download progress
    - Group papers in batches for easier management
    """)


def example_concurrent_access():
    """Example showing concurrent access benefits."""
    print("\n" + "=" * 60)
    print("Concurrent Access Benefits")
    print("=" * 60)
    
    print("""
    Directory-based storage enables concurrent workers:
    
    # Worker 1: Processing papers A-H
    storage/AAAA1111/nature-2023-quantum.pdf
    storage/BBBB2222/science-2023-ai.pdf
    
    # Worker 2: Processing papers I-P  
    storage/IIII3333/prl-2023-physics.pdf
    storage/JJJJ4444/cell-2023-biology.pdf
    
    # Worker 3: Processing papers Q-Z
    storage/QQQQ5555/jmlr-2023-ml.pdf
    storage/RRRR6666/cvpr-2023-vision.pdf
    
    Benefits:
    - No file locking between workers
    - Natural work distribution
    - Easy crash recovery
    - Scales linearly in HPC environments
    """)


if __name__ == "__main__":
    # Run examples
    example_pdf_storage()
    example_browser_download_workflow()
    example_concurrent_access()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
    The enhanced storage system provides:
    
    1. Original filename preservation
       - storage/ABCD1234/s41586-023-06312-0.pdf
       
    2. Human-readable organization
       - storage-human-readable/Smith-2023-Nature-ABCD
       
    3. Fast lookups without database
       - DOI -> storage_key mapping in JSON
       
    4. Concurrent worker support
       - Each paper in its own directory
       - No locking conflicts
       
    5. Browser download integration
       - HTML helper for manual downloads
       - Progress tracking
       - Multiple URL options
    """)

# EOF