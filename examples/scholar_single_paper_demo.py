#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 15:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/examples/scholar_single_paper_demo.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/scholar_single_paper_demo.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Step-by-step demo: Process one paper from AI2 BibTeX.

Focus on: Hülsemann et al. (2019) - Quantification of Phase-Amplitude Coupling
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from scitex.scholar.database._StorageIntegratedDB import StorageIntegratedDB
from scitex.scholar.doi import DOIResolver
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.storage import EnhancedStorageManager
from scitex.scholar.download import BrowserDownloadHelper


async def process_single_paper():
    """Process one paper step by step."""
    print("=" * 80)
    print("SINGLE PAPER PROCESSING DEMO")
    print("Paper: Quantification of Phase-Amplitude Coupling (Hülsemann et al., 2019)")
    print("=" * 80)
    
    # Initialize components
    db = StorageIntegratedDB("pac_research")
    storage = EnhancedStorageManager(db.base_dir)
    doi_resolver = DOIResolver()
    openurl_resolver = OpenURLResolver()
    
    # Step 1: Parse paper metadata from BibTeX
    print("\n1. PARSING PAPER METADATA")
    print("-" * 40)
    
    paper_metadata = {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling",
        "authors": ["Hülsemann, Mareike J.", "Naumann, E.", "Rasch, B."],
        "journal": "Frontiers in Neuroscience",
        "year": 2019,
        "volume": "13",
        "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096"
    }
    
    print("Parsed metadata:")
    for key, value in paper_metadata.items():
        if key == "title":
            print(f"  {key}: {value[:60]}...")
        else:
            print(f"  {key}: {value}")
    
    # Step 2: Add to database
    print("\n2. ADDING TO DATABASE")
    print("-" * 40)
    
    paper_id = db.add_paper(paper_metadata)
    storage_key = None
    
    # Get the storage key
    with db._get_connection() as conn:
        cursor = conn.execute(
            "SELECT storage_key FROM papers WHERE id = ?",
            (paper_id,)
        )
        row = cursor.fetchone()
        storage_key = row["storage_key"]
    
    print(f"Added to database:")
    print(f"  Paper ID: {paper_id}")
    print(f"  Storage key: {storage_key}")
    print(f"  Storage path: {storage.storage_dir / storage_key}")
    
    # Step 3: Resolve DOI
    print("\n3. RESOLVING DOI")
    print("-" * 40)
    
    # The URL is PubMed, let's try to resolve DOI
    print("Attempting DOI resolution...")
    print(f"  Title: {paper_metadata['title'][:60]}...")
    print(f"  Authors: {paper_metadata['authors'][0]} et al.")
    print(f"  Year: {paper_metadata['year']}")
    
    doi = await doi_resolver.resolve_doi_async(
        title=paper_metadata["title"],
        authors=paper_metadata["authors"],
        year=paper_metadata["year"]
    )
    
    if doi:
        print(f"\n✓ DOI resolved: {doi}")
        
        # Update database
        with db._get_connection() as conn:
            conn.execute(
                "UPDATE papers SET doi = ? WHERE id = ?",
                (doi, paper_id)
            )
            conn.commit()
    else:
        print("\n✗ DOI not found")
        # For demo, let's use a known DOI for this paper
        doi = "10.3389/fnins.2019.00573"
        print(f"  Using known DOI: {doi}")
        
        with db._get_connection() as conn:
            conn.execute(
                "UPDATE papers SET doi = ? WHERE id = ?",
                (doi, paper_id)
            )
            conn.commit()
    
    # Step 4: Generate download URLs
    print("\n4. GENERATING DOWNLOAD URLS")
    print("-" * 40)
    
    urls = []
    
    # DOI URL
    doi_url = f"https://doi.org/{doi}"
    urls.append(("DOI", doi_url))
    print(f"  DOI URL: {doi_url}")
    
    # Try OpenURL resolution (for institutional access)
    try:
        openurl_result = openurl_resolver.resolve(doi)
        if openurl_result and openurl_result.get("url"):
            urls.append(("OpenURL", openurl_result["url"]))
            print(f"  OpenURL: {openurl_result['url'][:80]}...")
    except Exception as e:
        print(f"  OpenURL resolution failed: {e}")
    
    # Original URL from BibTeX
    urls.append(("PubMed", paper_metadata["url"]))
    print(f"  PubMed: {paper_metadata['url']}")
    
    # Frontiers direct URL (since we know it's Frontiers)
    frontiers_url = f"https://www.frontiersin.org/articles/{doi}/pdf"
    urls.append(("Frontiers Direct", frontiers_url))
    print(f"  Frontiers: {frontiers_url}")
    
    # Step 5: Show storage structure that will be created
    print("\n5. STORAGE STRUCTURE")
    print("-" * 40)
    
    print(f"Files will be stored in:")
    print(f"""
    {storage.storage_dir}/{storage_key}/
    ├── fnins-13-00573.pdf              # Original filename from journal
    ├── metadata.json                   # Paper metadata
    ├── storage_metadata.json           # PDF metadata
    └── screenshots/                    # Download attempts
        ├── 20250801_151500-attempt-1-initial.jpg
        ├── 20250801_151502-attempt-1-success.jpg
        └── screenshots.json
    
    {storage.human_readable_dir}/
    └── Hulsemann-2019-FrontNeurosci-{storage_key[:4]} -> ../storage/{storage_key}
    """)
    
    # Step 6: Create download session
    print("\n6. CREATING DOWNLOAD SESSION")
    print("-" * 40)
    
    # Create a download helper HTML file
    download_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Download: Phase-Amplitude Coupling Paper</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .paper {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .urls {{ margin-top: 20px; }}
        .url-item {{ margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }}
        .url-item a {{ text-decoration: none; font-weight: bold; }}
        .instructions {{ margin-top: 30px; padding: 20px; background: #e8f4f8; border-radius: 5px; }}
        .storage-info {{ margin-top: 30px; font-family: monospace; background: #f0f0f0; padding: 15px; }}
    </style>
</head>
<body>
    <h1>Download Paper</h1>
    
    <div class="paper">
        <h2>{paper_metadata['title']}</h2>
        <p><strong>Authors:</strong> {', '.join(paper_metadata['authors'])}</p>
        <p><strong>Journal:</strong> {paper_metadata['journal']} ({paper_metadata['year']})</p>
        <p><strong>DOI:</strong> {doi}</p>
        <p><strong>Storage Key:</strong> {storage_key}</p>
    </div>
    
    <div class="urls">
        <h3>Download Options:</h3>
"""
    
    for source, url in urls:
        download_html += f"""
        <div class="url-item">
            <strong>{source}:</strong> 
            <a href="{url}" target="_blank">{url}</a>
        </div>
"""
    
    download_html += f"""
    </div>
    
    <div class="instructions">
        <h3>Instructions:</h3>
        <ol>
            <li>Try the <strong>Frontiers Direct</strong> link first (usually works without login)</li>
            <li>If that fails, try the <strong>DOI</strong> link</li>
            <li>If you have institutional access, try the <strong>OpenURL</strong> link</li>
            <li>Download the PDF to your Downloads folder</li>
            <li>Note the filename (e.g., "fnins-13-00573.pdf")</li>
        </ol>
    </div>
    
    <div class="storage-info">
        <h3>After downloading, the PDF will be stored as:</h3>
        <pre>{storage.storage_dir}/{storage_key}/[original-filename].pdf</pre>
        
        <h3>With human-readable link:</h3>
        <pre>{storage.human_readable_dir}/Hulsemann-2019-FrontNeurosci-{storage_key[:4]}</pre>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    html_path = Path(f"/tmp/download_paper_{storage_key}.html")
    with open(html_path, 'w') as f:
        f.write(download_html)
    
    print(f"Created download helper: {html_path}")
    print("\nNext steps:")
    print("1. Open the HTML file in your browser")
    print("2. Click on the download links")
    print("3. Save the PDF when it downloads")
    print("4. Run the storage step to organize the file")
    
    # Return info for next step
    return {
        "paper_id": paper_id,
        "storage_key": storage_key,
        "doi": doi,
        "urls": urls,
        "html_path": html_path,
        "db": db,
        "storage": storage
    }


def complete_storage(info: dict, downloaded_pdf_path: Path, original_filename: str):
    """Complete the storage process after manual download."""
    print("\n" + "=" * 80)
    print("COMPLETING STORAGE")
    print("=" * 80)
    
    db = info["db"]
    storage = info["storage"]
    
    # Store the PDF
    print(f"\nStoring PDF:")
    print(f"  Source: {downloaded_pdf_path}")
    print(f"  Original name: {original_filename}")
    
    stored_path = storage.store_pdf(
        storage_key=info["storage_key"],
        pdf_path=downloaded_pdf_path,
        original_filename=original_filename,
        pdf_url=info["urls"][0][1],  # Use first URL
        paper_metadata={
            "storage_key": info["storage_key"],
            "doi": info["doi"],
            "title": "Quantification of Phase-Amplitude Coupling...",
            "authors": ["Hülsemann, Mareike J.", "Naumann, E.", "Rasch, B."],
            "journal": "Frontiers in Neuroscience",
            "year": 2019
        }
    )
    
    print(f"\n✓ Stored at: {stored_path}")
    
    # Update database
    db.attach_pdf(
        paper_id=info["paper_id"],
        pdf_path=stored_path,
        original_filename=original_filename,
        pdf_url=info["urls"][0][1]
    )
    
    # Show final structure
    print(f"\nFinal storage structure:")
    storage_dir = storage.storage_dir / info["storage_key"]
    
    for item in sorted(storage_dir.iterdir()):
        print(f"  {item.name}")
        
    # Show human-readable link
    print(f"\nHuman-readable link:")
    for link in storage.human_readable_dir.iterdir():
        if link.is_symlink() and info["storage_key"] in str(link):
            print(f"  {link}")
            
    print("\n✓ Paper successfully processed and stored!")


if __name__ == "__main__":
    print("This demo will process one paper step by step.")
    print("After running this script:")
    print("1. Open the generated HTML file")
    print("2. Download the PDF manually")
    print("3. Run the storage completion step")
    print()
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        info = loop.run_until_complete(process_single_paper())
        
        print("\n" + "=" * 80)
        print("MANUAL DOWNLOAD REQUIRED")
        print("=" * 80)
        print(f"\n1. Open this file in your browser:")
        print(f"   firefox {info['html_path']}")
        print(f"\n2. Download the PDF")
        print(f"\n3. Then run this Python code to complete storage:")
        print(f"""
# After downloading the PDF:
from pathlib import Path

downloaded_pdf = Path("~/Downloads/fnins-13-00573.pdf").expanduser()
original_filename = "fnins-13-00573.pdf"

complete_storage(info, downloaded_pdf, original_filename)
""")
        
    finally:
        loop.close()

# EOF