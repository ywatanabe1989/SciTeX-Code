#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-01 23:35:00 (ywatanabe)"
# File: examples/scholar/enhanced_literature_review_demo.py

"""
Enhanced Literature Review Demo using SciTeX Scholar.

Demonstrates AI-powered literature review capabilities including:
- Semantic Scholar integration (200M+ papers)
- Journal metrics and impact factors
- AI-powered paper analysis and summarization
- Research gap identification
- Enhanced bibliography generation
"""

import asyncio
import sys
from pathlib import Path

# Add SciTeX-Code to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scitex.scholar import (
    PaperAcquisition,
    full_literature_review,
    get_capabilities
)

async def main():
    print("🚀 SciTeX Scholar Enhanced Literature Review Demo")
    print("=" * 55)
    
    # Show capabilities
    capabilities = get_capabilities()
    print(f"📊 Scholar version: {capabilities['version']}")
    print(f"🔗 Semantic Scholar: {capabilities['semantic_scholar_integration']}")
    print(f"📈 Journal Metrics: {capabilities['journal_metrics']}")
    print(f"🤖 AI Integration: {capabilities['ai_integration']}")
    
    if capabilities['ai_integration']:
        print(f"🔧 AI Providers: {', '.join(capabilities['ai_providers'])}")
    
    print()
    
    # Demo topic
    topic = "phase amplitude coupling neural oscillations"
    print(f"🎯 Demo Topic: {topic}")
    print()
    
    # Initialize with AI if available
    ai_provider = 'anthropic' if capabilities['ai_integration'] else None
    
    print("🔍 Searching for papers...")
    acquisition = PaperAcquisition(ai_provider=ai_provider)
    
    # Basic search demonstration
    papers = await acquisition.search(
        query=topic,
        sources=['semantic_scholar', 'pubmed'],
        max_results=20,
        start_year=2020
    )
    
    print(f"📚 Found {len(papers)} papers")
    
    # Show sample paper with enhanced metadata
    if papers:
        sample = papers[0]
        print(f"\n📖 Sample Paper:")
        print(f"   Title: {sample.title[:80]}...")
        print(f"   Authors: {', '.join(sample.authors[:3])}")
        print(f"   Journal: {sample.journal}")
        print(f"   Year: {sample.year}")
        print(f"   Citations: {sample.citation_count}")
        print(f"   Impact Factor: {sample.impact_factor}")
        print(f"   Quartile: {sample.journal_quartile}")
        print(f"   Open Access: {sample.has_open_access}")
        print(f"   Source: {sample.source}")
    
    # Generate enhanced bibliography
    print(f"\n📚 Generating Enhanced Bibliography...")
    bib_content = acquisition.generate_enhanced_bibliography(
        papers=papers[:10],  # Limit for demo
        include_metrics=True
    )
    
    # Save to file
    output_dir = Path("scholar_demo_output")
    output_dir.mkdir(exist_ok=True)
    
    bib_file = output_dir / "enhanced_bibliography.bib"
    with open(bib_file, 'w', encoding='utf-8') as f:
        f.write(bib_content)
    
    print(f"✅ Bibliography saved: {bib_file}")
    
    # AI-enhanced features (if available)
    if capabilities['ai_integration']:
        print(f"\n🤖 AI-Enhanced Analysis (using {ai_provider}):")
        
        # Analyze a sample paper
        if papers:
            print("   📝 Analyzing sample paper...")
            analysis = await acquisition.analyze_paper_with_ai(papers[0])
            if 'analysis' in analysis:
                print(f"   ✅ Analysis: {analysis['analysis'][:200]}...")
            
        # Generate research summary
        print("   📊 Generating research summary...")
        summary = await acquisition.generate_research_summary(papers[:5], topic)
        if summary and not summary.startswith("AI"):
            print(f"   ✅ Summary: {summary[:200]}...")
        
        # Find research gaps
        print("   🔍 Identifying research gaps...")
        gaps = await acquisition.find_research_gaps(papers[:10], topic)
        if gaps and not gaps[0].startswith("AI"):
            print(f"   ✅ Found {len(gaps)} research gaps")
            for i, gap in enumerate(gaps[:3], 1):
                print(f"      {i}. {gap[:100]}...")
    
    # Demonstrate full literature review workflow
    if capabilities['ai_integration']:
        print(f"\n📈 Full Literature Review Workflow:")
        print("   Running comprehensive analysis...")
        
        try:
            review_results = await full_literature_review(
                topic=topic,
                ai_provider=ai_provider,
                max_papers=15
            )
            
            print(f"   ✅ Complete! Found {review_results['papers_found']} papers")
            print(f"   📝 AI Summary: {len(review_results.get('ai_summary', ''))} chars")
            print(f"   🔍 Research Gaps: {len(review_results.get('research_gaps', []))} identified")
            print(f"   📚 Bibliography: {len(review_results.get('bibliography', ''))} chars")
            
            # Save comprehensive results
            import json
            results_file = output_dir / "full_review_results.json"
            
            # Prepare serializable data
            serializable_results = {
                'topic': review_results['topic'],
                'papers_found': review_results['papers_found'],
                'ai_summary': review_results.get('ai_summary', ''),
                'research_gaps': review_results.get('research_gaps', []),
                'ai_provider': review_results.get('ai_provider', ''),
                'papers': [paper.to_dict() for paper in review_results['papers'][:5]]  # Sample
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Full results saved: {results_file}")
            
        except Exception as e:
            print(f"   ❌ Full review failed: {e}")
    
    # Citation network analysis
    if papers and papers[0].s2_paper_id:
        print(f"\n🕸️ Citation Network Analysis:")
        sample_paper = papers[0]
        
        print("   📈 Finding citations...")
        citations = await acquisition.get_paper_citations(sample_paper, limit=10)
        print(f"   ✅ Found {len(citations)} citing papers")
        
        print("   📚 Finding references...")
        references = await acquisition.get_paper_references(sample_paper, limit=10)
        print(f"   ✅ Found {len(references)} referenced papers")
        
        print("   💡 Getting recommendations...")
        recommendations = await acquisition.get_recommendations(sample_paper, limit=5)
        print(f"   ✅ Found {len(recommendations)} recommended papers")
    
    # Research trends analysis
    print(f"\n📊 Research Trends Analysis:")
    print("   Analyzing trends over 5 years...")
    
    try:
        async with acquisition.s2_client as client:
            trends = await client.analyze_research_trends(topic, years=5)
            
            if trends:
                print(f"   ✅ Total papers in field: {trends.get('total_papers', 'Unknown')}")
                print(f"   📈 Trend direction: {trends.get('trend_direction', 'Unknown')}")
                
                top_venues = trends.get('top_venues', [])[:3]
                if top_venues:
                    print(f"   🏆 Top venues:")
                    for venue, count in top_venues:
                        print(f"      - {venue}: {count} papers")
    except Exception as e:
        print(f"   ❌ Trends analysis failed: {e}")
    
    print(f"\n🎉 Demo Complete!")
    print(f"📁 Output saved to: {output_dir.absolute()}")
    
    # Usage instructions
    print(f"\n💡 Usage in your research:")
    print(f"```python")
    print(f"from scitex.scholar import PaperAcquisition, full_literature_review")
    print(f"")
    print(f"# Quick search")
    print(f"acquisition = PaperAcquisition(ai_provider='anthropic')")
    print(f"papers = await acquisition.search('your topic')")
    print(f"")
    print(f"# Full review with AI")
    print(f"results = await full_literature_review('your topic', ai_provider='anthropic')")
    print(f"```")

if __name__ == "__main__":
    asyncio.run(main())

# EOF