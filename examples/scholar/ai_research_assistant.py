#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: examples/scholar/ai_research_assistant.py

"""
AI Research Assistant using SciTeX Scholar.

Interactive script demonstrating AI-powered research assistance including:
- Intelligent paper search and filtering
- Automated research gap identification  
- AI-generated literature summaries
- Citation network analysis
"""

import asyncio
import sys
from pathlib import Path

# Add SciTeX-Code to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scitex.scholar import PaperAcquisition, get_capabilities

class AIResearchAssistant:
    """AI-powered research assistant using SciTeX Scholar."""
    
    def __init__(self, ai_provider='anthropic'):
        self.capabilities = get_capabilities()
        self.ai_available = self.capabilities['ai_integration']
        self.scholar = PaperAcquisition(ai_provider=ai_provider if self.ai_available else None)
        self.ai_provider = ai_provider if self.ai_available else None
    
    async def research_topic(self, topic: str, max_papers: int = 20):
        """Comprehensive research analysis of a topic."""
        print(f"🔬 Researching: {topic}")
        print("=" * 50)
        
        # Step 1: Search for papers
        print("📚 Step 1: Searching literature...")
        papers = await self.scholar.search(
            query=topic,
            sources=['semantic_scholar', 'pubmed'],
            max_results=max_papers,
            start_year=2020
        )
        print(f"   Found {len(papers)} recent papers")
        
        # Step 2: Analyze top papers
        print("\n📊 Step 2: Analyzing top papers...")
        high_impact_papers = [p for p in papers if p.citation_count > 50][:10]
        print(f"   {len(high_impact_papers)} high-impact papers (>50 citations)")
        
        # Step 3: Journal analysis
        print("\n📈 Step 3: Journal impact analysis...")
        journal_metrics = {}
        for paper in papers:
            if paper.journal and paper.impact_factor:
                journal_metrics[paper.journal] = paper.impact_factor
        
        top_journals = sorted(journal_metrics.items(), key=lambda x: x[1], reverse=True)[:5]
        for journal, if_score in top_journals:
            print(f"   {journal}: IF={if_score}")
        
        # Step 4: AI Analysis (if available)
        if self.ai_available:
            print(f"\n🤖 Step 4: AI Analysis ({self.ai_provider})...")
            
            # Generate research summary
            summary = await self.scholar.generate_research_summary(papers[:10], topic)
            if summary and not summary.startswith("AI"):
                print(f"   📝 Research Summary Generated ({len(summary)} chars)")
            
            # Identify research gaps
            gaps = await self.scholar.find_research_gaps(papers[:15], topic)
            if gaps and not gaps[0].startswith("AI"):
                print(f"   🔍 Research Gaps Identified: {len(gaps)}")
                for i, gap in enumerate(gaps[:3], 1):
                    print(f"      {i}. {gap[:80]}...")
        
        # Step 5: Citation network
        print("\n🕸️ Step 5: Citation network analysis...")
        if papers and papers[0].s2_paper_id:
            top_paper = papers[0]
            
            citations = await self.scholar.get_paper_citations(top_paper, limit=10)
            references = await self.scholar.get_paper_references(top_paper, limit=10)
            
            print(f"   Top paper '{top_paper.title[:40]}...':")
            print(f"   - Cited by {len(citations)} recent papers")
            print(f"   - References {len(references)} papers")
        
        # Step 6: Generate outputs
        print("\n💾 Step 6: Generating outputs...")
        
        # Enhanced bibliography
        bib_content = self.scholar.generate_enhanced_bibliography(
            papers=papers[:15], 
            include_metrics=True
        )
        
        # Save results
        output_dir = Path("research_output")
        output_dir.mkdir(exist_ok=True)
        
        # Save bibliography
        bib_file = output_dir / f"{topic.replace(' ', '_')}_bibliography.bib"
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        
        # Save paper metadata
        import json
        papers_data = [paper.to_dict() for paper in papers[:20]]
        papers_file = output_dir / f"{topic.replace(' ', '_')}_papers.json"
        with open(papers_file, 'w', encoding='utf-8') as f:
            json.dump(papers_data, f, indent=2, ensure_ascii=False)
        
        print(f"   📚 Bibliography: {bib_file}")
        print(f"   📄 Paper data: {papers_file}")
        
        return {
            'papers_found': len(papers),
            'high_impact_papers': len(high_impact_papers),
            'top_journals': top_journals,
            'output_files': [str(bib_file), str(papers_file)]
        }
    
    async def analyze_paper(self, paper_title_or_doi: str):
        """Deep analysis of a specific paper."""
        print(f"🔍 Analyzing paper: {paper_title_or_doi}")
        
        # Search for the specific paper
        papers = await self.scholar.search(
            query=paper_title_or_doi,
            max_results=5
        )
        
        if not papers:
            print("❌ Paper not found")
            return
        
        paper = papers[0]  # Take the best match
        
        print(f"📖 Found: {paper.title}")
        print(f"📊 Citations: {paper.citation_count}")
        print(f"📈 Impact Factor: {paper.impact_factor}")
        print(f"🏆 Quartile: {paper.journal_quartile}")
        
        if self.ai_available:
            print(f"\n🤖 AI Analysis...")
            analysis = await self.scholar.analyze_paper_with_ai(paper)
            if 'analysis' in analysis:
                print(analysis['analysis'])
        
        # Citation network
        if paper.s2_paper_id:
            print(f"\n🕸️ Citation Network...")
            citations = await self.scholar.get_paper_citations(paper, limit=5)
            references = await self.scholar.get_paper_references(paper, limit=5)
            recommendations = await self.scholar.get_recommendations(paper, limit=3)
            
            print(f"Citing papers: {len(citations)}")
            print(f"Referenced papers: {len(references)}")
            print(f"Recommended papers: {len(recommendations)}")

async def interactive_demo():
    """Interactive demonstration of the AI Research Assistant."""
    print("🤖 AI Research Assistant Demo")
    print("=" * 40)
    
    assistant = AIResearchAssistant()
    
    if not assistant.ai_available:
        print("⚠️  AI features not available. Install AI dependencies for full functionality.")
        print()
    
    # Demo topics
    topics = [
        "machine learning interpretability",
        "quantum computing algorithms", 
        "CRISPR gene editing ethics"
    ]
    
    print("📋 Demo Topics:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    
    print("\n🚀 Running research analysis...")
    
    # Analyze first topic
    topic = topics[0]
    results = await assistant.research_topic(topic, max_papers=15)
    
    print(f"\n✅ Research Complete!")
    print(f"📊 Results Summary:")
    print(f"   Papers found: {results['papers_found']}")
    print(f"   High-impact papers: {results['high_impact_papers']}")
    print(f"   Output files: {len(results['output_files'])}")
    
    print(f"\n💡 Usage:")
    print(f"```python")
    print(f"from scitex.scholar import PaperAcquisition")
    print(f"assistant = PaperAcquisition(ai_provider='anthropic')")
    print(f"papers = await assistant.search('your topic')")
    print(f"summary = await assistant.generate_research_summary(papers, 'your topic')")
    print(f"```")

if __name__ == "__main__":
    asyncio.run(interactive_demo())

# EOF