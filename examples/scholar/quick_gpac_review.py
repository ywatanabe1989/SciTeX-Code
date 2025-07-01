#!/usr/bin/env python3
# Quick gPAC literature review using the enhanced system

import asyncio
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from scitex.scholar import PaperAcquisition

async def quick_gpac_review():
    print("📚 Quick gPAC Literature Review")
    print("=" * 40)
    
    # Initialize system
    acquisition = PaperAcquisition()
    
    # gPAC-specific queries
    queries = [
        "phase amplitude coupling",
        "cross frequency coupling",
        "modulation index neural",
        "PAC electrophysiology",
        "GPU neural signal processing",
        "parallel EEG analysis"
    ]
    
    all_papers = []
    
    for query in queries:
        print(f"🔍 {query}")
        
        papers = await acquisition.search(
            query=query,
            sources=['pubmed', 'arxiv'],
            max_results=15,
            start_year=2015
        )
        
        all_papers.extend(papers)
        print(f"   Found: {len(papers)} papers")
    
    # Remove duplicates
    unique_papers = acquisition._deduplicate_results(all_papers)
    
    print(f"\n📊 Results Summary:")
    print(f"   Total papers: {len(unique_papers)}")
    
    # Count by source
    source_counts = {}
    open_access_count = 0
    
    for paper in unique_papers:
        source_counts[paper.source] = source_counts.get(paper.source, 0) + 1
        if paper.pdf_url or paper.has_open_access:
            open_access_count += 1
    
    print(f"   Sources: {dict(source_counts)}")
    print(f"   Open access: {open_access_count} papers")
    
    # Save results for your gPAC paper
    output_dir = Path("gpac_literature_results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate BibTeX
    bib_entries = []
    for i, paper in enumerate(unique_papers):
        if paper.title:
            key = f"paper{i+1}"
            entry = f"""@article{{{key},
  title={{{paper.title}}},
  author={{{' and '.join(paper.authors[:3])}}},
  journal={{{paper.journal or 'Unknown'}}},
  year={{{paper.year or 'Unknown'}}},
  doi={{{paper.doi or ''}}},
  note={{Found via SciTeX-Scholar}}
}}"""
            bib_entries.append(entry)
    
    bib_file = output_dir / "gpac_references.bib"
    with open(bib_file, 'w') as f:
        f.write('\n\n'.join(bib_entries))
    
    # Save metadata
    metadata = [paper.to_dict() for paper in unique_papers]
    metadata_file = output_dir / "paper_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Results saved:")
    print(f"   📚 Bibliography: {bib_file}")
    print(f"   📄 Metadata: {metadata_file}")
    
    print(f"\n🎯 For your gPAC paper:")
    print(f"1. Copy {bib_file} to ~/proj/gpac/paper/")
    print(f"2. Add \\bibliography{{gpac_references}} to main.tex")
    print(f"3. Review metadata for key papers to cite")
    print(f"4. {open_access_count} papers have PDFs available!")

if __name__ == "__main__":
    asyncio.run(quick_gpac_review())