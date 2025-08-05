#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 01:47:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Demonstration of the unified DOI resolver interface."""

import asyncio
import sys
import argparse
from pathlib import Path

from . import DOIResolver


async def demo_unified_resolver():
    """Demonstrate the unified DOI resolver with different input types."""
    resolver = DOIResolver()
    
    print("=== Unified DOI Resolver Demo ===\n")
    
    # Example 1: Single DOI
    print("1. Resolving single DOI:")
    single_doi = "10.1038/nature12373"
    print(f"   Input: {single_doi}")
    try:
        result = await resolver.resolve_async(single_doi)
        print(f"   Result: {result.get('title', 'No title found')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 2: Multiple DOIs
    print("2. Resolving multiple DOIs:")
    doi_list = ["10.1038/nature12373", "10.1126/science.abc123"]
    print(f"   Input: {doi_list}")
    try:
        results = await resolver.resolve_async(doi_list)
        print(f"   Results: {len(results)} papers resolved")
        for i, result in enumerate(results):
            print(f"     {i+1}. {result.get('title', 'No title found')}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Example 3: BibTeX content
    print("3. Resolving from BibTeX content:")
    bibtex_content = '''
    @article{example2023,
        title={Example Paper},
        author={Author, A.},
        year={2023},
        journal={Nature},
        doi={10.1038/nature12373}
    }
    '''
    print("   Input: BibTeX content (sample)")
    try:
        results = await resolver.resolve_async(bibtex_content)
        print(f"   Results: {len(results)} papers resolved from BibTeX")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("=== Simple Unified API ===")
    print("One resolver handles all input types automatically:")
    print("  from scitex.scholar.doi import DOIResolver")
    print()
    print("  resolver = DOIResolver()")
    print("  await resolver.resolve_async('10.1038/nature12373')    # Single DOI")
    print("  await resolver.resolve_async(['doi1', 'doi2'])         # DOI list") 
    print("  await resolver.resolve_async('papers.bib')             # BibTeX file")
    print("  await resolver.resolve_async('@article{...}')          # BibTeX content")
    print()
    print("✨ No need to choose between different resolvers - it just works!")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DOI Resolver Demo")
    parser.add_argument("--demo", action="store_true", help="Run unified resolver demo")
    parser.add_argument("--project", type=str, default="default", 
                       help="Project name for Scholar library (default: default)")
    parser.add_argument("--max-workers", type=int, default=4,
                       help="Maximum concurrent workers for batch processing (default: 4)")
    parser.add_argument("--sources", nargs="+", 
                       help="Specific DOI sources to use (e.g., crossref pubmed)")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from previous progress file")
    parser.add_argument("input", nargs="?", help="DOI, file path, or BibTeX content to resolve")
    
    args = parser.parse_args()
    
    if args.demo:
        await demo_unified_resolver()
    elif args.input:
        resolver = DOIResolver()
        try:
            # Build kwargs from command line arguments
            kwargs = {
                "project": args.project,
                "max_workers": args.max_workers,
                "resume": args.resume,
            }
            if args.sources:
                kwargs["sources"] = args.sources
            
            result = await resolver.resolve_async(args.input, **kwargs)
            print(f"Resolved: {result}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())

# EOF