#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: examples/scholar/quick_scholar_demo.py

"""
Quick SciTeX Scholar Demo.

Simple demonstration showing how to use the enhanced scholar module
for literature search with journal metrics and AI integration.
"""

import asyncio
import sys
from pathlib import Path

# Add SciTeX-Code to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scitex.scholar import PaperAcquisition, get_capabilities

async def quick_demo():
    print("📚 Quick SciTeX Scholar Demo")
    print("=" * 30)
    
    # Check capabilities
    caps = get_capabilities()
    print(f"🔧 Version: {caps['version']}")
    print(f"🤖 AI Available: {caps['ai_integration']}")
    print()
    
    # Initialize scholar
    ai_provider = 'anthropic' if caps['ai_integration'] else None
    scholar = PaperAcquisition(ai_provider=ai_provider)
    
    # Quick search
    print("🔍 Searching for 'neural networks'...")
    papers = await scholar.search(
        query="neural networks",
        sources=['semantic_scholar'],
        max_results=5
    )
    
    print(f"📄 Found {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title[:60]}...")
        print(f"   Journal: {paper.journal}")
        print(f"   Citations: {paper.citation_count}")
        print(f"   Impact Factor: {paper.impact_factor}")
        print()
    
    # Generate bibliography
    if papers:
        bib = scholar.generate_enhanced_bibliography(papers[:3])
        print("📚 Sample BibTeX entry:")
        print(bib.split('\n\n')[1] if '\n\n' in bib else "")
    
    print("✅ Demo complete!")

if __name__ == "__main__":
    asyncio.run(quick_demo())