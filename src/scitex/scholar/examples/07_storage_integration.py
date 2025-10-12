#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-07 09:55:15 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/07_storage_integration.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/07_storage_integration.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

"""
Functionalities:
- Demonstrates enhanced Paper, Papers, and Scholar storage integration
- Shows individual paper storage operations
- Demonstrates project-level collection management
- Tests global Scholar library operations

Dependencies:
- scripts:
  - None
- packages:
  - scitex, asyncio

Input:
- Scholar library configuration
- Sample paper metadata

Output:
- Console output showing storage operations
- Papers stored in Scholar library with proper organization
"""

"""Imports"""
import argparse
import asyncio

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_paper_storage() -> None:
    """Demonstrate individual Paper storage capabilities."""
    from pathlib import Path

    from scitex.scholar.core.Paper import Paper
    from scitex.scholar.storage import ScholarLibrary

    print("=== Paper Storage Demo ===")

    # Create a sample paper with Pydantic structure
    paper = Paper()
    paper.metadata.basic.title = (
        "Enhanced Storage Integration for Scientific Literature Management"
    )
    paper.metadata.basic.authors = ["Claude AI", "SciTeX Team"]
    paper.metadata.basic.year = 2025
    paper.metadata.basic.abstract = "This paper demonstrates enhanced storage integration capabilities for scientific literature management systems."
    paper.metadata.publication.journal = "Nature AI Research"
    paper.metadata.publication.impact_factor = 42.778
    paper.metadata.citation_count.total = 1234
    paper.metadata.set_doi(
        "10.1038/nature.ai.2025.001"
    )  # Auto-syncs DOI and URL
    paper.container.projects = ["storage_demo"]

    print(f"Created paper with title: {paper.metadata.basic.title}")
    print(f"DOI: {paper.metadata.id.doi}")
    print(f"DOI URL (auto-synced): {paper.metadata.url.doi}")
    print(f"Impact Factor: {paper.metadata.publication.impact_factor}")
    print(f"Citation Count: {paper.metadata.citation_count.total}")

    # Save to library using project name
    library = ScholarLibrary(project="storage_demo")
    library_id = library.save_paper(paper=paper)
    print(f"✓ Saved to library with ID: {library_id}")

    # Verify saved location
    master_dir = Path.home() / ".scitex/scholar/library/MASTER" / library_id
    if master_dir.exists():
        print(f"✓ Paper stored at: {master_dir}")
        metadata_file = master_dir / "metadata.json"
        if metadata_file.exists():
            print(f"✓ Metadata file exists: {metadata_file}")

    print()


async def demonstrate_papers_collection() -> None:
    """Demonstrate Papers collection project management."""
    from pathlib import Path

    from scitex.scholar.core.Paper import Paper
    from scitex.scholar.core.Papers import Papers
    from scitex.scholar.storage import ScholarLibrary

    project = "storage_demo"

    print("=== Papers Collection Demo ===")

    # Create a collection of papers using Pydantic structure
    papers_list = []

    # Paper 1
    p1 = Paper()
    p1.metadata.basic.title = (
        "Deep Learning for Scientific Literature Analysis"
    )
    p1.metadata.basic.authors = ["Alice Researcher", "Bob Scholar"]
    p1.metadata.basic.year = 2024
    p1.metadata.publication.journal = "AI Journal"
    p1.metadata.set_doi("10.1000/ai.2024.001")
    p1.container.projects = [project]
    papers_list.append(p1)

    # Paper 2
    p2 = Paper()
    p2.metadata.basic.title = "Automated PDF Processing with Machine Learning"
    p2.metadata.basic.authors = ["Charlie Data", "Diana Code"]
    p2.metadata.basic.year = 2024
    p2.metadata.publication.journal = "Data Science Review"
    p2.metadata.set_doi("10.1000/ds.2024.002")
    p2.container.projects = [project]
    papers_list.append(p2)

    # Paper 3
    p3 = Paper()
    p3.metadata.basic.title = "Metadata Enrichment for Academic Papers"
    p3.metadata.basic.authors = ["Eve Meta", "Frank Info"]
    p3.metadata.basic.year = 2025
    p3.metadata.publication.journal = "Information Systems"
    p3.metadata.set_doi("10.1000/is.2025.001")
    p3.container.projects = [project]
    papers_list.append(p3)

    collection = Papers(papers_list)
    print(f"Created collection with {len(collection)} papers")

    # Save to library - using Path is also supported
    library_dir = Path.home() / ".scitex/scholar/library"
    library = ScholarLibrary(library_dir)
    saved_ids = []
    for paper in collection:
        library_id = library.save_paper(paper=paper)
        saved_ids.append(library_id)

    print(f"Saved {len(saved_ids)} papers to library")

    print()


async def demonstrate_scholar_global() -> None:
    """Demonstrate Scholar global library management."""
    from pathlib import Path

    print("=== Scholar Global Management Demo ===")

    library_dir = Path.home() / ".scitex/scholar/library"

    # List projects by checking library directory structure
    if library_dir.exists():
        projects = [
            d
            for d in library_dir.iterdir()
            if d.is_dir() and d.name != "MASTER" and not d.name.startswith(".")
        ]
        print(f"Available projects ({len(projects)}):")
        for project in projects:
            # Count symlinks in each project
            symlinks = [f for f in project.iterdir() if f.is_symlink()]
            print(f"  - {project.name}: {len(symlinks)} papers")

    # Count papers in MASTER storage
    master_dir = library_dir / "MASTER"
    if master_dir.exists():
        paper_count = len([d for d in master_dir.iterdir() if d.is_dir()])
        print(f"\n✓ Total papers in MASTER storage: {paper_count}")

    print()


async def main_async(args) -> bool:
    """Main async function for storage integration demo."""
    print("🗄️  Scholar Storage Integration Demo")
    print("=" * 50)

    try:
        await demonstrate_paper_storage()
        await demonstrate_papers_collection()
        await demonstrate_scholar_global()

        print("✅ Storage integration demo completed successfully")
        return True

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def main(args) -> int:
    """Main function wrapper for asyncio execution."""
    success = asyncio.run(main_async(args))
    return 0 if success else 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar storage integration capabilities"
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
