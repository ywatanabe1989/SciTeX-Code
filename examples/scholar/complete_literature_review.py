#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:20:00 (ywatanabe)"
# File: examples/complete_literature_review.py

"""
Complete literature review example.

This script demonstrates the full workflow from paper discovery
to semantic search and gap analysis.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, './src')

from scitex_scholar.literature_review_workflow import LiteratureReviewWorkflow


async def main():
    """Run complete literature review workflow."""
    
    print("=== SciTeX-Scholar: Complete Literature Review Workflow ===\n")
    
    # Initialize workflow
    workflow = LiteratureReviewWorkflow(
        workspace_dir=Path("./my_literature_review"),
        email="your-email@example.com"  # Replace with your email
    )
    
    # Define research topic
    topic = "phase amplitude coupling seizure detection EEG"
    
    print(f"Research Topic: {topic}")
    print("="*60)
    
    # Step 1: Discover papers
    print("\n📚 Step 1: Discovering relevant papers...")
    papers = await workflow.discover_papers(
        query=topic,
        sources=['pubmed', 'arxiv'],
        max_results=20,
        start_year=2020
    )
    print(f"✓ Found {len(papers)} papers")
    
    # Show some discovered papers
    print("\nSample of discovered papers:")
    for i, paper in enumerate(papers[:5], 1):
        print(f"{i}. {paper.title}")
        print(f"   Source: {paper.source} | Year: {paper.year}")
    
    # Step 2: Download available papers
    print("\n📥 Step 2: Downloading available papers...")
    downloaded = await workflow.acquire_papers(papers)
    print(f"✓ Downloaded {len(downloaded)} papers")
    
    # Step 3: Index papers for semantic search
    print("\n🔍 Step 3: Indexing papers with vector embeddings...")
    index_stats = await workflow.index_papers()
    print(f"✓ Indexed {index_stats.get('vector_indexed', 0)} papers")
    
    # Step 4: Demonstrate semantic search
    print("\n🧠 Step 4: Semantic Search Examples")
    print("-"*60)
    
    # Search 1: Conceptual search
    query1 = "neural synchronization patterns during epileptic events"
    print(f"\nQuery: '{query1}'")
    results1 = await workflow.search_literature(query1, n_results=3)
    
    for result in results1:
        print(f"- {result['title']}")
        print(f"  Score: {result['score']:.3f} | Year: {result['year']}")
    
    # Search 2: Method-specific search
    query2 = "machine learning classification accuracy"
    print(f"\n\nQuery: '{query2}'")
    results2 = await workflow.search_literature(query2, search_type='chunk', n_results=3)
    
    for result in results2:
        print(f"- {result['title']}")
        if result['highlights']:
            print(f"  Highlight: ...{result['highlights'][0][:100]}...")
    
    # Step 5: Analyze research gaps
    print("\n\n📊 Step 5: Research Gap Analysis")
    print("-"*60)
    
    gaps = await workflow.find_research_gaps(topic)
    
    print(f"Papers analyzed: {gaps['papers_analyzed']}")
    print(f"\nMethods used in the field:")
    for method in gaps['methods_used'][:10]:
        print(f"  • {method}")
    
    print(f"\nDatasets used:")
    for dataset in gaps['datasets_used'][:10]:
        print(f"  • {dataset}")
    
    if gaps['potential_unused_methods']:
        print(f"\n💡 Potential research opportunities:")
        print("Methods not yet explored in this area:")
        for method in gaps['potential_unused_methods']:
            print(f"  • {method}")
    
    # Step 6: Generate review summary
    print("\n\n📝 Step 6: Generating Literature Review Summary")
    print("-"*60)
    
    summary = await workflow.generate_review_summary(topic)
    print("\nSummary preview:")
    print(summary[:500] + "...")
    
    # Step 7: Complete pipeline (alternative approach)
    print("\n\n🚀 Alternative: Run Complete Pipeline in One Call")
    print("-"*60)
    
    # This would do all steps automatically
    # results = await workflow.full_review_pipeline(
    #     topic="your research topic",
    #     sources=['pubmed', 'arxiv'],
    #     max_papers=50,
    #     start_year=2020
    # )
    
    print("\nWorkflow complete!")
    print(f"\n📁 All results saved in: {workflow.workspace_dir}")
    print("\nYou can now:")
    print("1. Read the generated literature review summary")
    print("2. Use semantic search to explore specific aspects")
    print("3. Find similar papers to any interesting paper")
    print("4. Identify research gaps and opportunities")


if __name__ == "__main__":
    print("\n⚠️  Note: This example will:")
    print("- Search real academic databases (PubMed, arXiv)")
    print("- Download freely available PDFs")
    print("- Create vector embeddings (requires ~2GB RAM)")
    print("- Take 2-5 minutes on first run\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(main())
    else:
        print("Cancelled.")

# EOF