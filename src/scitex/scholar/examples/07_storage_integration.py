#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 15:22:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/07_storage_integration.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

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
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
async def demonstrate_paper_storage() -> None:
    """Demonstrate individual Paper storage capabilities."""
    from scitex.scholar.core import Paper
    from scitex.scholar.config import ScholarConfig
    
    config = ScholarConfig()
    
    print("=== Paper Storage Demo ===")
    
    # Create a sample paper
    paper = Paper(
        title="Enhanced Storage Integration for Scientific Literature Management",
        authors=["Claude AI", "SciTeX Team"],
        journal="Nature AI Research", 
        year=2025,
        doi="10.1038/nature.ai.2025.001",
        abstract="This paper demonstrates enhanced storage integration capabilities for scientific literature management systems.",
        project="storage_demo",
        config=config
    )
    
    print(f"Created paper: {paper}")
    
    # Save to library
    library_id = paper.save_to_library()
    print(f"Saved to library with ID: {library_id}")
    
    # Create another paper and load from library
    paper2 = Paper.from_library(library_id, config)
    print(f"Loaded from library: {paper2}")
    
    print()


async def demonstrate_papers_collection() -> None:
    """Demonstrate Papers collection project management."""
    from scitex.scholar.core import Paper, Papers
    from scitex.scholar.config import ScholarConfig
    
    config = ScholarConfig()
    project = "storage_demo"
    
    print("=== Papers Collection Demo ===")
    
    # Create a collection of papers
    papers_data = [
        {
            "title": "Deep Learning for Scientific Literature Analysis",
            "authors": ["Alice Researcher", "Bob Scholar"],
            "journal": "AI Journal",
            "year": 2024,
            "doi": "10.1000/ai.2024.001"
        },
        {
            "title": "Automated PDF Processing with Machine Learning",
            "authors": ["Charlie Data", "Diana Code"],
            "journal": "Data Science Review",
            "year": 2024,
            "doi": "10.1000/ds.2024.002"
        },
        {
            "title": "Metadata Enrichment for Academic Papers",
            "authors": ["Eve Meta", "Frank Info"],
            "journal": "Information Systems",
            "year": 2025,
            "doi": "10.1000/is.2025.001"
        }
    ]
    
    papers_list = [
        Paper(project=project, config=config, **data) 
        for data in papers_data
    ]
    
    collection = Papers(papers_list, project=project, config=config)
    print(f"Created collection with {len(collection)} papers")
    
    # Save to library
    save_results = collection.save_to_library()
    print(f"Library save results: {save_results}")
    
    # Get project statistics
    stats = collection.get_project_statistics()
    print("Project statistics:")
    pprint(stats)
    
    # Create project symlinks
    symlink_results = collection.create_project_symlinks()
    print(f"Symlink creation results: {symlink_results}")
    
    # Sync with library
    sync_results = collection.sync_with_library()
    print(f"Library sync results: {sync_results}")
    
    print()


async def demonstrate_scholar_global() -> None:
    """Demonstrate Scholar global library management."""
    from scitex.scholar.core import Scholar
    
    print("=== Scholar Global Management Demo ===")
    
    scholar = Scholar(project="storage_demo")
    
    # Create a new project
    new_project_dir = scholar.create_project(
        "test_project", 
        description="Test project for storage integration demo"
    )
    print(f"Created project at: {new_project_dir}")
    
    # List all projects
    projects = scholar.list_projects()
    print("Available projects:")
    for project in projects:
        print(f"  - {project['name']}: {project.get('description', 'No description')}")
    
    # Get library statistics
    library_stats = scholar.get_library_statistics()
    print("Library statistics:")
    pprint(library_stats)
    
    # Search across projects
    search_results = scholar.search_across_projects("learning")
    print(f"Search results for 'learning': {len(search_results)} papers found")
    
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

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
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