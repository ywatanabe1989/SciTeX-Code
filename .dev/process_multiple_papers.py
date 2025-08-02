#!/usr/bin/env python3
"""Process multiple papers through the scholar pipeline."""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Papers
from scitex.scholar.doi import DOIResolver

# Import our single paper pipeline
from test_complete_single_paper_pipeline import SinglePaperPipeline


async def process_multiple_papers(num_papers: int = 5):
    """Process multiple papers through the pipeline."""
    print("=" * 80)
    print(f"PROCESSING {num_papers} PAPERS")
    print("=" * 80)
    
    start_time = time.time()
    
    # Load papers
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    papers = Papers.from_bibtex(bibtex_path)
    print(f"\nLoaded {len(papers)} papers total")
    
    # Initialize pipeline
    pipeline = SinglePaperPipeline(project_name="pac_research")
    
    # Process statistics
    stats = {
        "total": num_papers,
        "processed": 0,
        "doi_found": 0,
        "pdf_found": 0,
        "errors": 0
    }
    
    results = []
    
    # Process papers
    for i in range(min(num_papers, len(papers))):
        paper = papers[i]
        
        # Get bibtex key
        if hasattr(paper, '_bibtex_key'):
            paper_key = paper._bibtex_key
        elif hasattr(paper, '_additional_metadata'):
            paper_key = paper._additional_metadata.get('bibtex_key', f'paper_{i}')
        else:
            paper_key = f"paper_{i}"
        
        print(f"\n{'-' * 80}")
        print(f"Processing paper {i+1}/{num_papers}: {paper_key}")
        print(f"{'-' * 80}")
        
        try:
            result = await pipeline.process_paper(paper, paper_key)
            results.append(result)
            
            # Update stats
            stats["processed"] += 1
            if result.get("doi"):
                stats["doi_found"] += 1
            if result.get("pdf_stored"):
                stats["pdf_found"] += 1
                
        except Exception as e:
            print(f"✗ Error processing paper: {e}")
            stats["errors"] += 1
            results.append({
                "paper_key": paper_key,
                "error": str(e)
            })
        
        # Small delay between papers
        if i < num_papers - 1:
            await asyncio.sleep(1)
    
    # Summary
    duration = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("PROCESSING SUMMARY")
    print("=" * 80)
    print(f"""
Total papers: {stats['total']}
Processed: {stats['processed']}
DOIs found: {stats['doi_found']} ({stats['doi_found']/stats['total']*100:.1f}%)
PDFs found: {stats['pdf_found']} ({stats['pdf_found']/stats['total']*100:.1f}%)
Errors: {stats['errors']}

Time taken: {duration:.1f} seconds
Average per paper: {duration/stats['total']:.1f} seconds
""")
    
    # Show library structure
    library_dir = pipeline.library_dir
    print("\nLibrary structure:")
    print(f"{library_dir}/")
    
    # Count items in project directory
    project_items = len(list(pipeline.project_dir.iterdir())) if pipeline.project_dir.exists() else 0
    hr_items = len(list(pipeline.human_readable_dir.iterdir())) if pipeline.human_readable_dir.exists() else 0
    
    print(f"├── {pipeline.project_name}/ ({project_items} papers)")
    print(f"└── {pipeline.project_name}-human-readable/ ({hr_items} links)")
    
    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "duration_seconds": duration,
        "results": results,
        "paths": {
            "library": str(library_dir),
            "project": str(pipeline.project_dir),
            "human_readable": str(pipeline.human_readable_dir)
        }
    }
    
    report_path = Path(".dev/multi_paper_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # List papers needing PDFs
    papers_without_pdf = [r for r in results if not r.get('pdf_stored') and not r.get('error')]
    if papers_without_pdf:
        print(f"\nPapers needing PDF download ({len(papers_without_pdf)}):")
        for r in papers_without_pdf[:5]:  # Show first 5
            print(f"  - Storage key: {r.get('storage_key')}")
            if r.get('doi'):
                print(f"    DOI: https://doi.org/{r['doi']}")


async def main():
    """Run the multi-paper processing."""
    # Process first 5 papers as a test
    await process_multiple_papers(num_papers=5)


if __name__ == "__main__":
    asyncio.run(main())