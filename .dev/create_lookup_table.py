#!/usr/bin/env python3
"""Create comprehensive lookup table for all papers."""

import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional


def scan_pac_research_directory():
    """Scan the pac_research directory and build lookup table."""
    print("=" * 80)
    print("BUILDING LOOKUP TABLE FOR PAC_RESEARCH")
    print("=" * 80)
    
    # Base directory
    library_dir = Path("/home/ywatanabe/.scitex/scholar/library")
    pac_research_dir = library_dir / "pac_research"
    human_readable_dir = library_dir / "pac_research-human-readable"
    
    # Lookup tables
    doi_to_storage = {}  # DOI -> storage_key
    storage_to_info = {}  # storage_key -> full info
    bibtex_to_storage = {}  # bibtex_key -> storage_key
    
    # Statistics
    stats = {
        "total_directories": 0,
        "with_doi": 0,
        "with_pdf": 0,
        "with_enriched_metadata": 0,
        "missing_doi": 0,
        "missing_pdf": 0
    }
    
    # Scan each storage directory
    for storage_dir in sorted(pac_research_dir.iterdir()):
        if not storage_dir.is_dir() or len(storage_dir.name) != 8:
            continue
        
        stats["total_directories"] += 1
        storage_key = storage_dir.name
        
        # Read metadata
        metadata_path = storage_dir / "metadata.json"
        if not metadata_path.exists():
            continue
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Extract key information
        info = {
            "storage_key": storage_key,
            "storage_path": str(storage_dir),
            "bibtex_key": metadata.get("bibtex_key"),
            "title": metadata.get("title"),
            "authors": metadata.get("authors"),
            "year": metadata.get("year"),
            "journal": metadata.get("journal"),
            "doi": metadata.get("doi"),
            "doi_source": metadata.get("doi_source"),
            "created_at": metadata.get("created_at"),
            "has_pdf": False,
            "pdf_filename": None,
            "pdf_size": None,
            "metadata_completeness": 0,
            "missing_fields": []
        }
        
        # Check for PDF
        pdf_files = list(storage_dir.glob("*.pdf"))
        if pdf_files:
            info["has_pdf"] = True
            info["pdf_filename"] = pdf_files[0].name
            info["pdf_size"] = pdf_files[0].stat().st_size
            stats["with_pdf"] += 1
        else:
            stats["missing_pdf"] += 1
        
        # Check DOI
        if info["doi"]:
            doi_to_storage[info["doi"]] = storage_key
            stats["with_doi"] += 1
        else:
            stats["missing_doi"] += 1
        
        # Check bibtex key
        if info["bibtex_key"]:
            bibtex_to_storage[info["bibtex_key"]] = storage_key
        
        # Check metadata completeness
        important_fields = [
            "title", "authors", "year", "journal", "doi",
            "abstract", "keywords", "volume", "pages", "url"
        ]
        
        missing_fields = []
        for field in important_fields:
            if not metadata.get(field):
                missing_fields.append(field)
        
        info["missing_fields"] = missing_fields
        info["metadata_completeness"] = (len(important_fields) - len(missing_fields)) / len(important_fields) * 100
        
        if info["metadata_completeness"] > 70:
            stats["with_enriched_metadata"] += 1
        
        # Store info
        storage_to_info[storage_key] = info
    
    # Print summary
    print(f"\nSCANNED RESULTS:")
    print(f"Total storage directories: {stats['total_directories']}")
    print(f"With DOI: {stats['with_doi']} ({stats['with_doi']/stats['total_directories']*100:.1f}%)")
    print(f"With PDF: {stats['with_pdf']} ({stats['with_pdf']/stats['total_directories']*100:.1f}%)")
    print(f"With enriched metadata: {stats['with_enriched_metadata']} ({stats['with_enriched_metadata']/stats['total_directories']*100:.1f}%)")
    print(f"\nMissing DOI: {stats['missing_doi']}")
    print(f"Missing PDF: {stats['missing_pdf']}")
    
    # Save lookup tables
    lookup_data = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "doi_to_storage": doi_to_storage,
        "bibtex_to_storage": bibtex_to_storage,
        "storage_info": storage_to_info
    }
    
    lookup_file = Path(".dev/pac_research_lookup.json")
    with open(lookup_file, 'w') as f:
        json.dump(lookup_data, f, indent=2)
    
    print(f"\nLookup table saved to: {lookup_file}")
    
    # Create CSV for easy viewing
    df = pd.DataFrame.from_dict(storage_to_info, orient='index')
    csv_file = Path(".dev/pac_research_status.csv")
    df.to_csv(csv_file, index=False)
    print(f"Status CSV saved to: {csv_file}")
    
    return lookup_data


def create_status_report(lookup_data: Dict):
    """Create a detailed status report."""
    print("\n" + "=" * 80)
    print("DETAILED STATUS REPORT")
    print("=" * 80)
    
    storage_info = lookup_data["storage_info"]
    
    # Papers needing DOI
    need_doi = [info for info in storage_info.values() if not info["doi"]]
    print(f"\n1. PAPERS NEEDING DOI RESOLUTION ({len(need_doi)}):")
    for info in need_doi[:5]:
        print(f"   - {info['bibtex_key']}: {info['title'][:50]}...")
    if len(need_doi) > 5:
        print(f"   ... and {len(need_doi) - 5} more")
    
    # Papers needing PDF
    need_pdf = [info for info in storage_info.values() if info["doi"] and not info["has_pdf"]]
    print(f"\n2. PAPERS WITH DOI BUT NO PDF ({len(need_pdf)}):")
    for info in need_pdf[:5]:
        print(f"   - {info['storage_key']}: {info['doi']}")
        print(f"     {info['title'][:60]}...")
    if len(need_pdf) > 5:
        print(f"   ... and {len(need_pdf) - 5} more")
    
    # Papers with incomplete metadata
    incomplete = [info for info in storage_info.values() 
                 if info["metadata_completeness"] < 50]
    print(f"\n3. PAPERS WITH INCOMPLETE METADATA ({len(incomplete)}):")
    for info in incomplete[:5]:
        print(f"   - {info['bibtex_key']}: {info['metadata_completeness']:.0f}% complete")
        print(f"     Missing: {', '.join(info['missing_fields'][:5])}")
    if len(incomplete) > 5:
        print(f"   ... and {len(incomplete) - 5} more")
    
    # Papers fully complete
    complete = [info for info in storage_info.values() 
               if info["doi"] and info["has_pdf"] and info["metadata_completeness"] > 70]
    print(f"\n4. FULLY COMPLETE PAPERS ({len(complete)}):")
    for info in complete[:5]:
        print(f"   ✓ {info['bibtex_key']}: {info['pdf_filename']}")
    if len(complete) > 5:
        print(f"   ... and {len(complete) - 5} more")
    
    # Create action items
    print("\n" + "=" * 80)
    print("ACTION ITEMS")
    print("=" * 80)
    print(f"1. Resolve DOIs for {len(need_doi)} papers")
    print(f"2. Download PDFs for {len(need_pdf)} papers with DOIs")
    print(f"3. Enrich metadata for {len(incomplete)} papers")
    print(f"\nNext step: Run targeted operations based on what's missing")


def check_paper_status(identifier: str, lookup_data: Dict) -> Optional[Dict]:
    """Check status of a specific paper by DOI, bibtex key, or storage key."""
    storage_info = lookup_data["storage_info"]
    
    # Try as storage key
    if identifier in storage_info:
        return storage_info[identifier]
    
    # Try as DOI
    if identifier in lookup_data["doi_to_storage"]:
        storage_key = lookup_data["doi_to_storage"][identifier]
        return storage_info[storage_key]
    
    # Try as bibtex key
    if identifier in lookup_data["bibtex_to_storage"]:
        storage_key = lookup_data["bibtex_to_storage"][identifier]
        return storage_info[storage_key]
    
    return None


if __name__ == "__main__":
    # Build lookup table
    lookup_data = scan_pac_research_directory()
    
    # Create status report
    create_status_report(lookup_data)
    
    # Example: Check specific paper
    print("\n" + "=" * 80)
    print("EXAMPLE: Checking specific paper")
    print("=" * 80)
    
    # Try to find the Hülsemann paper
    paper_info = check_paper_status("10.3389/fnins.2019.00573", lookup_data)
    if paper_info:
        print(f"Found paper by DOI:")
        print(f"  Storage: {paper_info['storage_key']}")
        print(f"  Title: {paper_info['title'][:60]}...")
        print(f"  Has PDF: {paper_info['has_pdf']}")
        print(f"  PDF: {paper_info['pdf_filename']}")
        print(f"  Metadata completeness: {paper_info['metadata_completeness']:.0f}%")