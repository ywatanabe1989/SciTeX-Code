#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Demo: Enhanced Bibliography with Impact Factors

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from scitex.scholar import PaperAcquisition, JournalMetrics, lookup_journal_impact_factor

async def demo_enhanced_bibliography():
    print("📚 Demo: Enhanced Bibliography with Journal Metrics")
    print("=" * 55)
    print("🎯 Demonstrates automatic impact factor lookup in BibTeX")
    print()
    
    # Initialize enhanced system
    acquisition = PaperAcquisition()
    
    # Test journal metrics first
    print("🔍 Testing Journal Metrics Lookup:")
    test_journals = [
        "Nature",
        "Science", 
        "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "PLOS ONE",
        "arXiv preprint",
        "Journal of Neuroscience"
    ]
    
    for journal in test_journals:
        impact_factor = lookup_journal_impact_factor(journal)
        print(f"  📊 {journal}: IF = {impact_factor}")
    
    print()
    
    # Search for papers
    print("🔍 Searching for sample papers...")
    try:
        papers = await acquisition.search(
            query="neural networks machine learning",
            sources=['pubmed', 'arxiv'],  # Use stable sources
            max_results=5,
            start_year=2020
        )
        
        print(f"📄 Found {len(papers)} papers")
        
        if papers:
            # Show sample paper with metrics
            sample = papers[0]
            print(f"\n📖 Sample paper: {sample.title[:60]}...")
            print(f"   📚 Journal: {sample.journal}")
            print(f"   📊 Impact Factor: {sample.impact_factor}")
            print(f"   🏆 Quartile: {sample.journal_quartile}")
            print(f"   📈 Citations: {sample.citation_count}")
            
            # Generate enhanced bibliography
            print(f"\n📚 Generating Enhanced Bibliography...")
            
            # Create output directory
            output_dir = Path("bibliography_demo")
            output_dir.mkdir(exist_ok=True)
            
            # Generate with metrics
            bib_with_metrics = acquisition.generate_enhanced_bibliography(
                papers=papers,
                include_metrics=True,
                output_file=output_dir / "enhanced_bibliography_with_metrics.bib"
            )
            
            # Generate without metrics (traditional)
            bib_without_metrics = acquisition.generate_enhanced_bibliography(
                papers=papers,
                include_metrics=False,
                output_file=output_dir / "traditional_bibliography.bib"
            )
            
            print(f"✅ Generated two bibliography files:")
            print(f"   📊 With metrics: bibliography_demo/enhanced_bibliography_with_metrics.bib")
            print(f"   📝 Traditional: bibliography_demo/traditional_bibliography.bib")
            
            # Show sample BibTeX entry
            print(f"\n📋 Sample Enhanced BibTeX Entry:")
            print("=" * 50)
            
            # Get first few lines of the enhanced bibliography
            sample_entry = bib_with_metrics.split('\n\n')[1] if '\n\n' in bib_with_metrics else bib_with_metrics.split('\n')[6:25]
            if isinstance(sample_entry, list):
                sample_entry = '\n'.join(sample_entry)
            else:
                sample_entry = sample_entry[:500] + "..." if len(sample_entry) > 500 else sample_entry
            
            print(sample_entry)
            print("=" * 50)
            
            print(f"\n🎯 Enhanced Features:")
            print(f"✅ Impact factors automatically included")
            print(f"✅ Journal quartiles (Q1, Q2, Q3, Q4)")
            print(f"✅ Citation counts from Semantic Scholar")
            print(f"✅ Open access status")
            print(f"✅ Multiple identifiers (DOI, arXiv, PMID)")
            
            print(f"\n📄 LaTeX Usage:")
            print(f"   \\bibliography{{enhanced_bibliography_with_metrics}}")
            print(f"   \\cite{{PaperKey}} % Automatically includes IF in references")
            
            print(f"\n💡 Benefits for Academic Writing:")
            print(f"   • Reviewers can easily assess source quality")
            print(f"   • Automatic journal ranking information")
            print(f"   • Enhanced metadata for comprehensive references")
            print(f"   • Impact factor trends for field analysis")
            
        else:
            print("❌ No papers found. Creating sample bibliography instead...")
            
            # Create sample papers with known high-impact journals
            sample_papers = [
                {
                    'title': 'Deep Learning for Scientific Discovery',
                    'authors': ['Smith, J.', 'Johnson, M.'],
                    'journal': 'Nature',
                    'year': '2023',
                    'doi': '10.1038/s41586-023-12345-6',
                    'citation_count': 150,
                    'has_open_access': False
                },
                {
                    'title': 'GPU Acceleration in Neural Networks',
                    'authors': ['Brown, A.', 'Davis, L.'],
                    'journal': 'IEEE Transactions on Pattern Analysis and Machine Intelligence',
                    'year': '2023',
                    'doi': '10.1109/TPAMI.2023.67890',
                    'citation_count': 89,
                    'has_open_access': True
                }
            ]
            
            # Use journal metrics service directly
            metrics = JournalMetrics()
            for paper_dict in sample_papers:
                entry = metrics.create_enhanced_bibtex_entry(paper_dict, include_metrics=True)
                print(f"\n📋 Sample Enhanced Entry:")
                print(entry)
    
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("Creating sample bibliography with mock data...")
        
        # Show mock enhanced entry
        mock_entry = """@article{Smith2023deep,
  title={Deep Learning for Scientific Discovery},
  author={Smith, J. and Johnson, M.},
  journal={Nature},
  year={2023},
  doi={10.1038/s41586-023-12345-6},
  impactfactor={49.962},
  quartile={Q1},
  journalrank={1},
  citedby={150},
  note={via semantic_scholar}
}"""
        
        print(f"\n📋 Example Enhanced BibTeX Entry:")
        print("=" * 50)
        print(mock_entry)
        print("=" * 50)
    
    print(f"\n🎉 Enhanced Bibliography Demo Complete!")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_bibliography())