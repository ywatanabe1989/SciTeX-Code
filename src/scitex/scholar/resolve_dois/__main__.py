#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/resolve_dois/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/resolve_dois/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for resumable DOI resolution.

Usage:
    python -m scitex.scholar.resolve_dois input.bib [--output results.json] [--progress progress.json]
    
Examples:
    # Resolve DOIs from BibTeX file
    python -m scitex.scholar.resolve_dois papers.bib
    
    # Resume interrupted resolution
    python -m scitex.scholar.resolve_dois papers.bib --progress doi_resolution_20250801_143022.progress.json
    
    # Save results to JSON
    python -m scitex.scholar.resolve_dois papers.bib --output resolved_dois.json
    
    # Use specific sources
    python -m scitex.scholar.resolve_dois papers.bib --sources crossref pubmed
"""

import argparse
import json
import sys
from pathlib import Path

from scitex import logging
from ._ResumableDOIResolver import ResumableDOIResolver

logger = logging.getLogger(__name__)


def main():
    """Main CLI function for DOI resolution."""
    parser = argparse.ArgumentParser(
        description="Resolve DOIs from BibTeX file with resume capability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve DOIs from BibTeX file
  python -m scitex.scholar.resolve_dois papers.bib
  
  # Resume interrupted resolution
  python -m scitex.scholar.resolve_dois papers.bib --progress doi_resolution_20250801.progress.json
  
  # Save results to JSON
  python -m scitex.scholar.resolve_dois papers.bib --output resolved_dois.json
  
  # Use specific sources only
  python -m scitex.scholar.resolve_dois papers.bib --sources crossref semantic_scholar

This command will:
- Load papers from BibTeX file
- Resolve DOIs using multiple sources (CrossRef, PubMed, Semantic Scholar, etc.)
- Save progress automatically (can resume if interrupted)
- Handle rate limits gracefully
- Output results as JSON or updated BibTeX
        """
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input BibTeX file"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for results (JSON format)"
    )
    
    parser.add_argument(
        "--progress",
        "-p",
        type=str,
        help="Progress file to resume from (or create)"
    )
    
    parser.add_argument(
        "--sources",
        "-s",
        nargs="+",
        choices=["crossref", "pubmed", "semantic_scholar", "openalex", "arxiv"],
        help="DOI sources to use (default: all)"
    )
    
    parser.add_argument(
        "--update-bibtex",
        "-u",
        action="store_true",
        help="Update the original BibTeX file with resolved DOIs"
    )
    
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress"
    )
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.fail(f"Input file not found: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == ".bib":
        logger.warning(f"Input file does not have .bib extension: {input_path}")
    
    # Configure logging
    if args.quiet:
        logging.disable(logging.INFO)
    elif args.verbose:
        logging.getLogger("scitex.scholar").setLevel(logging.DEBUG)
    
    try:
        # Create resolver
        progress_file = Path(args.progress) if args.progress else None
        resolver = ResumableDOIResolver(progress_file)
        
        # Show status
        if not args.quiet:
            if progress_file and progress_file.exists():
                logger.info(f"Resuming from progress file: {progress_file}")
            else:
                logger.info(f"Resolving DOIs from: {input_path}")
        
        # Resolve DOIs
        results = resolver.resolve_from_bibtex(
            bibtex_path=input_path,
            sources=args.sources
        )
        
        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.success(f"Results saved to: {output_path}")
        
        # Update BibTeX if requested
        if args.update_bibtex:
            _update_bibtex_file(input_path, results)
            logger.success(f"Updated BibTeX file: {input_path}")
        
        # Show sample results
        if not args.quiet and results:
            logger.info("\nSample results:")
            for i, (title, doi) in enumerate(list(results.items())[:5]):
                logger.info(f"  {title[:60]}... -> {doi}")
            if len(results) > 5:
                logger.info(f"  ... and {len(results) - 5} more")
    
    except KeyboardInterrupt:
        logger.warning("\nDOI resolution interrupted - progress saved")
        sys.exit(1)
    except Exception as e:
        logger.fail(f"DOI resolution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _update_bibtex_file(bibtex_path: Path, doi_mapping: dict):
    """Update BibTeX file with resolved DOIs."""
    from scitex.io import load, save
    
    # Create backup
    backup_path = bibtex_path.with_suffix('.bib.bak')
    import shutil
    shutil.copy2(bibtex_path, backup_path)
    logger.info(f"Created backup: {backup_path}")
    
    # Load entries
    entries = load(str(bibtex_path))
    
    # Update DOIs
    updated_count = 0
    for entry in entries:
        fields = entry.get("fields", {})
        title = fields.get("title", "").strip()
        
        if title in doi_mapping and not fields.get("doi"):
            fields["doi"] = doi_mapping[title]
            updated_count += 1
    
    # Save updated entries
    if updated_count > 0:
        save(entries, str(bibtex_path))
        logger.info(f"Updated {updated_count} entries with DOIs")
    else:
        logger.info("No updates needed - all entries already have DOIs")


if __name__ == "__main__":
    main()

# EOF