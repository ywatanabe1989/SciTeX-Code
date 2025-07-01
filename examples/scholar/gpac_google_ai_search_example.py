#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Using search_papers_with_ai with Google AI for GPAC Literature Review

This example demonstrates how to use the search_papers_with_ai function
with Google's Gemini models to search for and analyze GPAC-related papers.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scitex.scholar import search_papers_with_ai, PaperAcquisition


async def demo_google_ai_search():
    """Demonstrate searching papers with Google AI analysis."""
    
    print("🚀 GPAC Literature Review using Google AI (Gemini)")
    print("=" * 50)
    
    # IMPORTANT: Set your Google API key as environment variable
    # export GOOGLE_API_KEY="your-api-key-here"
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-api-key-here'")
        print("   Get your key from: https://aistudio.google.com/apikey")
        return
    
    # Available Google models from scitex:
    # - gemini-2.0-flash (fast, cheap)
    # - gemini-1.5-pro (powerful)
    # - gemini-1.5-flash (balanced)
    
    # Search for GPAC papers with Google AI
    print("\n🔍 Searching for GPAC papers...")
    
    try:
        # Method 1: Using convenience function with Google AI
        papers = await search_papers_with_ai(
            query="phase amplitude coupling GPU acceleration",
            ai_provider='google',  # Use Google AI
            max_results=10,
            start_year=2020
        )
        
        print(f"✅ Found {len(papers)} papers")
        
        # Display results
        for i, paper in enumerate(papers[:5], 1):
            print(f"\n📄 Paper {i}:")
            print(f"   Title: {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            print(f"   Year: {paper.year}")
            print(f"   Citations: {paper.citation_count}")
            print(f"   Open Access: {paper.has_open_access}")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return papers
    
    # Method 2: Using PaperAcquisition with custom Google model
    print("\n\n🔧 Advanced: Using specific Google model...")
    
    # Initialize with specific Google model
    acquisition = PaperAcquisition(ai_provider='google')
    
    # Search with enhanced parameters
    advanced_papers = await acquisition.search(
        query="cross-frequency coupling real-time analysis GPU",
        sources=['semantic_scholar', 'pubmed'],
        max_results=15,
        start_year=2018,
        open_access_only=True
    )
    
    print(f"✅ Found {len(advanced_papers)} open access papers")
    
    # Analyze a paper with Google AI
    if advanced_papers:
        print("\n🤖 Analyzing paper with Google AI...")
        analysis = await acquisition.analyze_paper_with_ai(advanced_papers[0])
        
        if 'analysis' in analysis:
            print(f"\n📊 AI Analysis:")
            print(analysis['analysis'])
    
    # Generate research summary
    print("\n📝 Generating research summary with Google AI...")
    summary = await acquisition.generate_research_summary(
        papers[:10], 
        "GPU-accelerated phase-amplitude coupling analysis"
    )
    print(f"\n{summary[:500]}...")  # Show first 500 chars
    
    # Find research gaps
    print("\n🔍 Identifying research gaps...")
    gaps = await acquisition.find_research_gaps(
        papers[:20],
        "GPU-accelerated PAC methods"
    )
    
    print("\n📌 Research Gaps Identified:")
    for gap in gaps[:5]:
        print(f"   • {gap}")
    
    return papers


async def demo_full_literature_review():
    """Run a complete literature review with Google AI."""
    
    print("\n\n🎯 Running Full Literature Review with Google AI")
    print("=" * 50)
    
    from scitex.scholar import full_literature_review
    
    # Run comprehensive review
    review_results = await full_literature_review(
        topic="GPU-accelerated phase-amplitude coupling analysis methods",
        ai_provider='google',
        max_papers=30
    )
    
    print(f"\n✅ Literature Review Complete!")
    print(f"   Papers found: {review_results['papers_found']}")
    print(f"   AI Provider: {review_results['ai_provider']}")
    print(f"\n📊 Summary Preview:")
    print(review_results['ai_summary'][:300] + "...")
    
    # Save results
    output_dir = Path("gpac_google_ai_review")
    output_dir.mkdir(exist_ok=True)
    
    # Save bibliography
    bib_file = output_dir / "gpac_bibliography.bib"
    with open(bib_file, 'w') as f:
        f.write(review_results['bibliography'])
    print(f"\n📚 Bibliography saved to: {bib_file}")
    
    # Save gaps analysis
    gaps_file = output_dir / "research_gaps.txt"
    with open(gaps_file, 'w') as f:
        f.write("Research Gaps in GPU-Accelerated PAC Methods\n")
        f.write("=" * 45 + "\n\n")
        for i, gap in enumerate(review_results['research_gaps'], 1):
            f.write(f"{i}. {gap}\n\n")
    print(f"🔍 Research gaps saved to: {gaps_file}")
    
    return review_results


def compare_google_models():
    """Show available Google models and their characteristics."""
    
    print("\n📊 Available Google AI Models for Literature Review:")
    print("=" * 50)
    
    models = [
        {
            'name': 'gemini-2.0-flash',
            'description': 'Fastest, most cost-effective',
            'best_for': 'Quick searches, initial screening',
            'cost': '$0.10/$0.40 per 1M tokens'
        },
        {
            'name': 'gemini-1.5-pro',
            'description': 'Most capable, best reasoning',
            'best_for': 'Deep analysis, gap identification',
            'cost': '$3.50/$10.50 per 1M tokens'
        },
        {
            'name': 'gemini-1.5-flash',
            'description': 'Balanced speed and capability',
            'best_for': 'Standard literature reviews',
            'cost': '$0.15/$0.0375 per 1M tokens'
        }
    ]
    
    for model in models:
        print(f"\n🤖 {model['name']}")
        print(f"   Description: {model['description']}")
        print(f"   Best for: {model['best_for']}")
        print(f"   Cost: {model['cost']}")
    
    print("\n💡 Tip: Set model in genai_factory() or use default (gemini-1.5-flash)")


async def main():
    """Run all demonstrations."""
    
    # Show available models
    compare_google_models()
    
    # Run basic search demo
    await demo_google_ai_search()
    
    # Run full literature review
    # Uncomment to run (takes longer)
    # await demo_full_literature_review()
    
    print("\n\n✅ Demo complete!")
    print("📌 Next steps:")
    print("   1. Set GOOGLE_API_KEY environment variable")
    print("   2. Adjust search queries for your specific GPAC research")
    print("   3. Use full_literature_review() for comprehensive analysis")
    print("   4. Experiment with different Google models for speed/quality tradeoff")


if __name__ == "__main__":
    asyncio.run(main())