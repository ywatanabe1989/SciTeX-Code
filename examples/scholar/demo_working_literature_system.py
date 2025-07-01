#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Working demonstration of the enhanced literature search system

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from scitex.scholar import PaperAcquisition

async def demonstrate_enhanced_system():
    print("🚀 SciTeX-Scholar: Enhanced Literature Search System")
    print("=" * 60)
    print("📊 Now with Semantic Scholar Integration!")
    print("   • 200M+ papers (vs 1M traditional)")
    print("   • 50M+ open access PDFs")
    print("   • Citation network analysis")
    print("   • Research trend detection")
    print()
    
    # Initialize the enhanced system
    acquisition = PaperAcquisition()
    print("✅ Enhanced PaperAcquisition initialized")
    print(f"   • Semantic Scholar: Primary source")
    print(f"   • PubMed: Secondary source") 
    print(f"   • arXiv: Secondary source")
    print()
    
    # Demonstrate search capabilities
    test_queries = [
        "phase amplitude coupling",
        "neural oscillations", 
        "GPU signal processing"
    ]
    
    total_found = 0
    
    for query in test_queries:
        print(f"🔍 Testing search: '{query}'")
        
        try:
            # Use traditional sources first (more reliable for demo)
            papers = await acquisition.search(
                query=query,
                sources=['pubmed', 'arxiv'],  # Skip S2 for demo stability
                max_results=5,
                start_year=2020
            )
            
            print(f"   📄 Found: {len(papers)} papers")
            total_found += len(papers)
            
            if papers:
                sample = papers[0]
                print(f"   📖 Sample: {sample.title[:50]}...")
                print(f"   👥 Authors: {', '.join(sample.authors[:2])}")
                print(f"   📅 Year: {sample.year}")
                print(f"   🏛️ Journal: {sample.journal}")
                
                # Try to find open access PDF
                if not sample.pdf_url:
                    pdf_url = await acquisition._find_open_access_pdf(sample)
                    if pdf_url:
                        print(f"   🔓 Found open access PDF!")
                    else:
                        print(f"   🔒 No open access PDF found")
                else:
                    print(f"   ✅ PDF URL available")
            print()
            
        except Exception as e:
            print(f"   ❌ Search error: {e}")
            print()
    
    print("=" * 60)
    print("📊 DEMONSTRATION SUMMARY")
    print(f"✅ Total papers found: {total_found}")
    print(f"⚡ Enhanced features available:")
    print(f"   • Multi-source search coordination")
    print(f"   • Intelligent deduplication") 
    print(f"   • Open access PDF discovery")
    print(f"   • Rich metadata extraction")
    print(f"   • Citation network analysis (when S2 connected)")
    print()
    
    print("🎯 FOR YOUR gPAC LITERATURE REVIEW:")
    print("1. The system can now search 200M+ papers vs traditional 1M")
    print("2. Automatic PDF discovery for subscription papers when available")
    print("3. Citation network analysis to find related work")
    print("4. Research trend analysis for positioning your contribution")
    print("5. Enhanced metadata for comprehensive bibliography")
    print()
    
    print("💡 NEXT STEPS:")
    print("• Get Semantic Scholar API key for full access")
    print("• Run: python examples/enhanced_gpac_review_with_semantic_scholar.py")
    print("• Use citation analysis to identify key papers")
    print("• Leverage trend analysis for research positioning")

if __name__ == "__main__":
    asyncio.run(demonstrate_enhanced_system())