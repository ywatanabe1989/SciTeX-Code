#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 04:05:00 (ywatanabe)"
# File: examples/scitex_scholar/example_literature_review_workflow.py

"""
Example: Complete literature review workflow.

This example demonstrates:
- Discovering papers from multiple sources
- Downloading available papers
- Building a searchable index
- Analyzing research trends
- Identifying research gaps
- Generating review summaries
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, './src')

from scitex_scholar.literature_review_workflow import LiteratureReviewWorkflow


async def main():
    """Demonstrate complete literature review workflow."""
    
    print("=== Literature Review Workflow Example ===\n")
    
    # Initialize workflow with custom workspace
    workflow = LiteratureReviewWorkflow(
        workspace_dir=Path("./example_review_workspace"),
        email="your-email@example.com"  # Replace with your email
    )
    
    # Research topic
    topic = "phase amplitude coupling seizure detection"
    
    print(f"Research Topic: '{topic}'")
    print(f"Workspace: {workflow.workspace_dir}\n")
    
    # 1. Discover Papers
    print("1. DISCOVERING PAPERS")
    print("-" * 50)
    print("Searching PubMed and arXiv...")
    
    papers = await workflow.discover_papers(
        query=topic,
        sources=['pubmed', 'arxiv'],
        max_results=10,  # Limited for demo
        start_year=2020
    )
    
    print(f"\n✓ Found {len(papers)} papers")
    
    # Show discovered papers
    print("\nDiscovered papers:")
    for i, paper in enumerate(papers[:5], 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Source: {paper.source}")
        print(f"   Year: {paper.year}")
        if paper.doi:
            print(f"   DOI: {paper.doi}")
        if paper.arxiv_id:
            print(f"   arXiv: {paper.arxiv_id}")
    
    # 2. Download Papers
    print("\n\n2. DOWNLOADING PAPERS")
    print("-" * 50)
    print("Attempting to download available PDFs...")
    
    downloaded = await workflow.acquire_papers(papers)
    
    print(f"\n✓ Downloaded {len(downloaded)} papers")
    for title, path in list(downloaded.items())[:3]:
        print(f"  - {path.name}")
    
    # 3. Index Papers
    print("\n\n3. INDEXING PAPERS")
    print("-" * 50)
    print("Creating searchable index with vector embeddings...")
    
    index_stats = await workflow.index_papers()
    
    print(f"\n✓ Indexed {index_stats.get('vector_indexed', 0)} papers")
    
    # 4. Search Indexed Literature
    print("\n\n4. SEMANTIC SEARCH")
    print("-" * 50)
    
    # Example searches
    searches = [
        "neural synchronization patterns",
        "machine learning accuracy",
        "EEG signal processing methods"
    ]
    
    for query in searches:
        print(f"\nQuery: '{query}'")
        results = await workflow.search_literature(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     Score: {result['score']:.3f}")
    
    # 5. Analyze Research Gaps
    print("\n\n5. RESEARCH GAP ANALYSIS")
    print("-" * 50)
    
    gaps = await workflow.find_research_gaps(topic)
    
    print(f"Analysis based on {gaps['papers_analyzed']} papers\n")
    
    print("Methods used in the field:")
    for method in gaps['methods_used'][:8]:
        print(f"  • {method}")
    
    print("\nDatasets used:")
    for dataset in gaps['datasets_used'][:5]:
        print(f"  • {dataset}")
    
    if gaps['potential_unused_methods']:
        print("\n💡 Potential unexplored methods:")
        for method in gaps['potential_unused_methods']:
            print(f"  • {method}")
    
    print(f"\nTemporal trend: {'📈 Growing' if gaps['temporal_trend']['increasing'] else '📉 Stable/Declining'}")
    
    # 6. Generate Review Summary
    print("\n\n6. LITERATURE REVIEW SUMMARY")
    print("-" * 50)
    
    summary = await workflow.generate_review_summary(topic)
    
    # Show preview
    print("Summary preview:\n")
    print(summary[:500] + "...")
    
    print(f"\n✓ Full summary saved to workspace")
    
    # 7. Workflow State
    print("\n\n7. WORKFLOW STATE")
    print("-" * 50)
    
    print(f"Workspace contents:")
    print(f"  Papers directory: {workflow.papers_dir}")
    print(f"  Index directory: {workflow.index_dir}")
    print(f"  Vector DB: {workflow.vector_db_dir}")
    print(f"  Metadata: {workflow.metadata_dir}")
    
    print(f"\nWorkflow statistics:")
    print(f"  Total searches: {len(workflow.state['searches'])}")
    print(f"  Downloaded papers: {len(workflow.state['downloaded_papers'])}")
    print(f"  Indexed papers: {len(workflow.state.get('indexed_papers', []))}")


async def quick_review_example():
    """Example: Quick one-command literature review."""
    print("\n\n=== QUICK LITERATURE REVIEW ===\n")
    
    from scitex_scholar.literature_review_workflow import conduct_literature_review
    
    # One command to do everything
    results = await conduct_literature_review(
        topic="deep learning EEG classification",
        sources=['pubmed', 'arxiv'],
        max_papers=20,
        start_year=2022
    )
    
    print("Review Results:")
    print(f"  Papers found: {results['papers_found']}")
    print(f"  Papers downloaded: {results['papers_downloaded']}")
    print(f"  Papers indexed: {results['papers_indexed']}")
    print(f"  Summary saved to: {results['summary_path']}")
    print(f"  Workspace: {results['workspace']}")


async def custom_workflow_example():
    """Example: Customized workflow for specific needs."""
    print("\n\n=== CUSTOM WORKFLOW EXAMPLE ===\n")
    
    workflow = LiteratureReviewWorkflow()
    
    # Step 1: Search only arXiv for recent preprints
    print("1. Searching arXiv for recent preprints...")
    arxiv_papers = await workflow.discover_papers(
        query="transformer medical imaging",
        sources=['arxiv'],
        max_results=15
    )
    print(f"   Found {len(arxiv_papers)} preprints")
    
    # Step 2: Filter by year
    recent_papers = [p for p in arxiv_papers if p.year >= "2023"]
    print(f"   Filtered to {len(recent_papers)} papers from 2023+")
    
    # Step 3: Download and index
    if recent_papers:
        downloaded = await workflow.acquire_papers(recent_papers[:5])
        print(f"   Downloaded {len(downloaded)} papers")
        
        await workflow.index_papers()
        
        # Step 4: Find similar papers in collection
        print("\n2. Finding similar papers...")
        
        if workflow.vector_engine.get_statistics()['total_documents'] > 0:
            # Search for papers similar to the first one
            first_doc_id = list(workflow.state['downloaded_papers'].values())[0]
            similar = workflow.vector_engine.find_similar_documents(
                str(first_doc_id),
                n_results=3
            )
            
            print("   Similar papers found:")
            for paper in similar:
                print(f"     - {paper.metadata.get('title', 'Unknown')}")
                print(f"       Similarity: {paper.similarity_score:.3f}")


async def analyze_existing_collection():
    """Example: Analyze an existing paper collection."""
    print("\n\n=== ANALYZE EXISTING COLLECTION ===\n")
    
    workflow = LiteratureReviewWorkflow()
    
    # Index existing PDFs without downloading new ones
    existing_pdfs = Path("./Exported Items/files")
    
    if existing_pdfs.exists():
        print(f"Indexing existing PDFs from: {existing_pdfs}")
        
        # Index the existing collection
        stats = await workflow.index_papers(
            paper_paths=list(existing_pdfs.rglob("*.pdf"))[:20]  # Limit for demo
        )
        
        print(f"\nIndexed {stats['vector_indexed']} papers")
        
        # Analyze the collection
        if stats['vector_indexed'] > 0:
            # Get collection statistics
            all_methods = set()
            all_keywords = set()
            
            for doc in workflow.search_engine.documents.values():
                methods = doc['metadata'].get('methods', [])
                all_methods.update(methods)
                
                keywords = doc['metadata'].get('keywords', [])
                all_keywords.update(keywords)
            
            print(f"\nCollection Analysis:")
            print(f"  Total papers: {len(workflow.search_engine.documents)}")
            print(f"  Unique methods: {len(all_methods)}")
            print(f"  Unique keywords: {len(all_keywords)}")
            
            if all_methods:
                print(f"\n  Top methods:")
                for method in sorted(all_methods)[:10]:
                    print(f"    • {method}")


if __name__ == "__main__":
    print("This example will:")
    print("- Search academic databases")
    print("- Download papers (requires internet)")
    print("- Create vector embeddings")
    print("- Generate a literature review\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        # Run main workflow
        asyncio.run(main())
        
        # Uncomment to run other examples
        # asyncio.run(quick_review_example())
        # asyncio.run(custom_workflow_example())
        # asyncio.run(analyze_existing_collection())
    else:
        print("Cancelled.")

# EOF