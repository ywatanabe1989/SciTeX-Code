#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Using specific Google AI models for GPAC Literature Review

This example shows how to use different Google Gemini models
for various aspects of GPAC literature analysis.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scitex.scholar import PaperAcquisition, PaperMetadata
from scitex.ai import genai_factory


async def demo_with_specific_google_model():
    """Demonstrate using specific Google models for different tasks."""
    
    print("🚀 GPAC Literature Review with Custom Google Models")
    print("=" * 50)
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Error: GOOGLE_API_KEY not set!")
        return
    
    # Initialize AI clients with different Google models
    print("\n🤖 Initializing Google AI models...")
    
    # Fast model for initial screening
    fast_ai = genai_factory(
        model='gemini-2.0-flash',
        temperature=0.7,
        max_tokens=2048
    )
    
    # Powerful model for deep analysis
    powerful_ai = genai_factory(
        model='gemini-1.5-pro',
        temperature=0.3,  # Lower temperature for more focused analysis
        max_tokens=4096
    )
    
    # Balanced model for summaries
    balanced_ai = genai_factory(
        model='gemini-1.5-flash',
        temperature=0.5,
        max_tokens=3072
    )
    
    print("✅ Models initialized successfully")
    
    # Search for papers (using default model)
    print("\n🔍 Searching for GPAC papers...")
    acquisition = PaperAcquisition()
    
    papers = await acquisition.search(
        query="phase amplitude coupling GPU CUDA parallel processing",
        max_results=20,
        start_year=2019
    )
    
    print(f"✅ Found {len(papers)} papers")
    
    # Example 1: Fast screening with gemini-2.0-flash
    print("\n📋 Task 1: Fast screening with gemini-2.0-flash")
    print("-" * 40)
    
    relevant_papers = await screen_papers_fast(papers[:10], fast_ai)
    print(f"✅ Identified {len(relevant_papers)} highly relevant papers")
    
    # Example 2: Deep analysis with gemini-1.5-pro
    print("\n🔬 Task 2: Deep analysis with gemini-1.5-pro")
    print("-" * 40)
    
    if relevant_papers:
        analysis = await deep_analyze_paper(relevant_papers[0], powerful_ai)
        print("📊 Deep Analysis Result:")
        print(analysis[:500] + "...")
    
    # Example 3: Literature synthesis with gemini-1.5-flash
    print("\n📝 Task 3: Literature synthesis with gemini-1.5-flash")
    print("-" * 40)
    
    synthesis = await synthesize_findings(papers[:15], balanced_ai)
    print("📚 Synthesis:")
    print(synthesis[:500] + "...")
    
    # Example 4: Custom PaperAcquisition with specific model
    print("\n🛠️ Task 4: Full workflow with custom model")
    print("-" * 40)
    
    # Create custom acquisition system with specific model
    custom_acquisition = PaperAcquisition(ai_provider='google')
    
    # Manually set the AI client to use a specific model
    custom_acquisition.ai_client = powerful_ai
    
    # Generate comprehensive analysis
    gaps = await custom_acquisition.find_research_gaps(papers, "GPU-accelerated PAC")
    
    print("🔍 Research Gaps (using gemini-1.5-pro):")
    for i, gap in enumerate(gaps[:3], 1):
        print(f"   {i}. {gap}")
    
    return papers, relevant_papers


async def screen_papers_fast(papers: List[PaperMetadata], ai_client) -> List[PaperMetadata]:
    """Quick relevance screening using fast model."""
    
    relevant_papers = []
    
    # Create batch prompt for efficiency
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        papers_text += f"{i}. {paper.title}\n"
        papers_text += f"   Abstract: {paper.abstract[:200]}...\n\n"
    
    prompt = f"""Quickly identify which papers are MOST relevant for GPU-accelerated PAC implementation.

Papers to screen:
{papers_text}

Return ONLY the numbers of papers that are:
1. Directly about phase-amplitude coupling (PAC) methods
2. Discuss GPU, CUDA, or parallel processing
3. Present computational improvements or optimizations

Format: Just list the paper numbers (e.g., "1, 3, 7")"""
    
    try:
        response = await ai_client.generate_async(prompt)
        
        # Parse response to get paper indices
        import re
        numbers = re.findall(r'\d+', response)
        
        for num in numbers:
            idx = int(num) - 1
            if 0 <= idx < len(papers):
                relevant_papers.append(papers[idx])
                
    except Exception as e:
        print(f"Screening error: {e}")
    
    return relevant_papers


async def deep_analyze_paper(paper: PaperMetadata, ai_client) -> str:
    """Perform deep analysis of a single paper using powerful model."""
    
    prompt = f"""Perform an in-depth technical analysis of this paper for GPU-accelerated PAC implementation:

Title: {paper.title}
Authors: {', '.join(paper.authors[:5])}
Year: {paper.year}
Citations: {paper.citation_count}

Abstract: {paper.abstract}

Please analyze:
1. **Technical Approach**: What specific PAC algorithms or GPU techniques are used?
2. **Performance Metrics**: What speedups or improvements are reported?
3. **Implementation Details**: Programming languages, frameworks, hardware used?
4. **Validation**: How was the method validated? What datasets?
5. **Limitations**: What are the stated or implied limitations?
6. **Relevance to gPAC**: How can this inform our GPU-accelerated PAC implementation?

Provide specific technical details and quantitative results where available."""
    
    try:
        analysis = await ai_client.generate_async(prompt)
        return analysis
    except Exception as e:
        return f"Analysis failed: {e}"


async def synthesize_findings(papers: List[PaperMetadata], ai_client) -> str:
    """Synthesize findings across multiple papers using balanced model."""
    
    # Group papers by theme
    gpu_papers = []
    method_papers = []
    application_papers = []
    
    for paper in papers:
        content = f"{paper.title} {paper.abstract}".lower()
        if any(term in content for term in ['gpu', 'cuda', 'parallel']):
            gpu_papers.append(paper)
        if any(term in content for term in ['algorithm', 'method', 'technique']):
            method_papers.append(paper)
        if any(term in content for term in ['clinical', 'application', 'real-world']):
            application_papers.append(paper)
    
    prompt = f"""Synthesize the current state of GPU-accelerated PAC research based on these papers:

GPU/Parallel Computing Papers ({len(gpu_papers)}):
{format_paper_list(gpu_papers[:5])}

PAC Method Papers ({len(method_papers)}):
{format_paper_list(method_papers[:5])}

Application Papers ({len(application_papers)}):
{format_paper_list(application_papers[:5])}

Please provide:
1. **Current State**: What's the current landscape of GPU-accelerated PAC?
2. **Key Technologies**: What GPU frameworks and techniques are most used?
3. **Performance Gains**: What speedups are typically achieved?
4. **Common Challenges**: What technical challenges are repeatedly mentioned?
5. **Future Directions**: Where is the field heading?

Keep the synthesis concise but informative."""
    
    try:
        synthesis = await ai_client.generate_async(prompt)
        return synthesis
    except Exception as e:
        return f"Synthesis failed: {e}"


def format_paper_list(papers: List[PaperMetadata]) -> str:
    """Format papers for prompt."""
    result = ""
    for paper in papers:
        result += f"- {paper.title} ({paper.year}, {paper.citation_count} citations)\n"
    return result


async def compare_model_performance():
    """Compare performance of different Google models."""
    
    print("\n⚡ Performance Comparison of Google Models")
    print("=" * 50)
    
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  Error: GOOGLE_API_KEY not set!")
        return
    
    # Test prompt
    test_prompt = """Analyze this PAC method description and identify GPU optimization opportunities:
    
"We present a novel phase-amplitude coupling measure based on the Kullback-Leibler divergence 
between the phase-conditioned amplitude distributions. The method requires computing histograms
for each phase bin and calculating statistical divergences iteratively."

What GPU optimizations would you suggest?"""
    
    models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    
    for model_name in models:
        print(f"\n🤖 Testing {model_name}...")
        
        try:
            import time
            ai = genai_factory(model=model_name, temperature=0.3)
            
            start = time.time()
            response = await ai.generate_async(test_prompt)
            elapsed = time.time() - start
            
            print(f"⏱️  Response time: {elapsed:.2f}s")
            print(f"📝 Response preview: {response[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run demonstrations."""
    
    print("🎯 Google AI Models for GPAC Literature Review")
    print("=" * 50)
    
    # Run custom model demo
    await demo_with_specific_google_model()
    
    # Compare model performance
    await compare_model_performance()
    
    print("\n\n✅ Demo complete!")
    print("\n💡 Key Takeaways:")
    print("1. Use gemini-2.0-flash for fast screening of many papers")
    print("2. Use gemini-1.5-pro for deep technical analysis")
    print("3. Use gemini-1.5-flash for balanced tasks like synthesis")
    print("4. You can mix models in a single workflow for optimal results")


if __name__ == "__main__":
    asyncio.run(main())