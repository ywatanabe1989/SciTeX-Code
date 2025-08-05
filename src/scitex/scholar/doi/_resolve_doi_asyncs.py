#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 13:35:00"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/resolve_doi_asyncs.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/resolve_doi_asyncs.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import asyncio
import sys
from pathlib import Path

from ._SingleDOIResolver import SingleDOIResolver
from ._BibTeXDOIResolver import BibTeXDOIResolver


async def resolve_single_doi(title: str):
    """Resolve DOI for a single title."""
    resolver = SingleDOIResolver()
    doi = await resolver.resolve_async(title)
    
    if doi:
        print(f"\nFound DOI: {doi}")
        print(f"URL: https://doi.org/{doi}")
    else:
        print("\nNo DOI found")


async def resolve_bibtex_dois(args):
    """Resolve DOIs for all entries in a BibTeX file."""
    resolver = BibTeXDOIResolver(
        bibtex_path=Path(args.bibtex),
        output_path=Path(args.output) if args.output else None,
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
    )
    
    # Reset progress if requested
    if args.reset and resolver.progress_file.exists():
        resolver.progress_file.unlink()
        resolver.progress = resolver._load_progress()
        print("Progress reset.")
    
    # Resolve DOIs
    try:
        total, resolved, failed = await resolver.resolve_all_async()
        resolver.print_summary()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted! Progress has been saved.")
        print(f"Resume with: python -m scitex.scholar.resolve_doi_asyncs --bibtex {args.bibtex}")
        return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Resolve DOIs from paper titles or BibTeX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve DOI for a single title
  python -m scitex.scholar.resolve_doi_asyncs --title "Attention is All You Need"
  
  # Resolve DOIs from BibTeX file (resumable)
  python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib
  
  # Resume interrupted processing
  python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib
  
  # Save to different file
  python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib --output papers-with-dois.bib
  
  # Use more worker_asyncs for faster processing
  python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib --worker_asyncs 5
  
  # Reset progress and start fresh
  python -m scitex.scholar.resolve_doi_asyncs --bibtex papers.bib --reset
        """
    )
    
    # Create mutually exclusive group for title vs bibtex
    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        "--title", "-t",
        type=str,
        help="Paper title to search for DOI"
    )
    
    input_group.add_argument(
        "--bibtex", "-b",
        type=str,
        help="Path to BibTeX file for batch DOI resolution"
    )
    
    # Options for BibTeX processing
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output BibTeX file (defaults to input file)"
    )
    
    parser.add_argument(
        "--worker_asyncs", "-w",
        type=int,
        default=3,
        help="Maximum concurrent worker_asyncs for BibTeX processing (default: 3)"
    )
    
    parser.add_argument(
        "--cache-dir",
        type=str,
        help="Directory for progress cache (default: ~/.scitex/scholar/doi_cache)"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset progress and start from scratch (BibTeX mode only)"
    )

    args = parser.parse_args()
    
    # Execute appropriate function
    if args.title:
        asyncio.run(resolve_single_doi(args.title))
        return 0
    else:
        # BibTeX mode
        success = asyncio.run(resolve_bibtex_dois(args))
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
