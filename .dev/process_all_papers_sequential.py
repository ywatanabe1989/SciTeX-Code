#!/usr/bin/env python3
"""Process all papers from BibTeX file sequentially."""

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
from test_complete_single_paper_pipeline import SinglePaperPipeline


class SequentialProcessor:
    """Process all papers sequentially with progress tracking."""
    
    def __init__(self, project_name: str = "pac_research"):
        self.project_name = project_name
        self.pipeline = SinglePaperPipeline(project_name)
        
        # Progress tracking
        self.progress_file = Path(".dev/processing_progress.json")
        self.results_file = Path(".dev/all_papers_results.json")
        self.load_progress()
    
    def load_progress(self):
        """Load previous progress if exists."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "processed_keys": [],
                "last_processed_index": -1,
                "results": []
            }
    
    def save_progress(self):
        """Save current progress."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    async def process_all_papers(self, bibtex_path: Path, batch_size: int = 10):
        """Process all papers from BibTeX file."""
        print("=" * 80)
        print("SEQUENTIAL PAPER PROCESSING")
        print("=" * 80)
        
        # Load papers
        papers = Papers.from_bibtex(bibtex_path)
        total_papers = len(papers)
        print(f"\nTotal papers in BibTeX: {total_papers}")
        
        # Check previous progress
        start_index = self.progress["last_processed_index"] + 1
        if start_index > 0:
            print(f"Resuming from paper {start_index + 1} (already processed {start_index} papers)")
        
        # Statistics
        stats = {
            "total": total_papers,
            "processed": len(self.progress["processed_keys"]),
            "doi_found": 0,
            "pdf_found": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Count existing stats
        for result in self.progress["results"]:
            if result.get("doi"):
                stats["doi_found"] += 1
            if result.get("pdf_stored"):
                stats["pdf_found"] += 1
            if result.get("error"):
                stats["errors"] += 1
        
        start_time = time.time()
        batch_start_time = time.time()
        
        # Process papers
        for i in range(start_index, total_papers):
            paper = papers[i]
            
            # Get bibtex key
            if hasattr(paper, '_bibtex_key'):
                paper_key = paper._bibtex_key
            elif hasattr(paper, '_additional_metadata'):
                paper_key = paper._additional_metadata.get('bibtex_key', f'paper_{i}')
            else:
                paper_key = f"paper_{i}"
            
            # Skip if already processed
            if paper_key in self.progress["processed_keys"]:
                print(f"\nSkipping already processed paper: {paper_key}")
                stats["skipped"] += 1
                continue
            
            # Process paper
            print(f"\n{'-' * 80}")
            print(f"Processing paper {i+1}/{total_papers}: {paper_key}")
            print(f"{'-' * 80}")
            
            try:
                result = await self.pipeline.process_paper(paper, paper_key)
                
                # Add to results
                self.progress["results"].append(result)
                self.progress["processed_keys"].append(paper_key)
                self.progress["last_processed_index"] = i
                
                # Update stats
                stats["processed"] += 1
                if result.get("doi"):
                    stats["doi_found"] += 1
                if result.get("pdf_stored"):
                    stats["pdf_found"] += 1
                
                # Save progress after each paper
                self.save_progress()
                
            except Exception as e:
                print(f"\n✗ Error processing paper: {e}")
                error_result = {
                    "paper_key": paper_key,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.progress["results"].append(error_result)
                self.progress["processed_keys"].append(paper_key)
                self.progress["last_processed_index"] = i
                stats["errors"] += 1
                self.save_progress()
            
            # Batch delay and progress report
            if (i + 1 - start_index) % batch_size == 0 and i < total_papers - 1:
                batch_time = time.time() - batch_start_time
                papers_processed = i + 1 - start_index
                
                print(f"\n{'=' * 40}")
                print(f"BATCH PROGRESS REPORT")
                print(f"{'=' * 40}")
                print(f"Papers processed in this session: {papers_processed}")
                print(f"Total processed: {stats['processed']}/{total_papers} ({stats['processed']/total_papers*100:.1f}%)")
                print(f"DOIs found: {stats['doi_found']} ({stats['doi_found']/stats['processed']*100:.1f}%)")
                print(f"PDFs found: {stats['pdf_found']} ({stats['pdf_found']/stats['processed']*100:.1f}%)")
                print(f"Errors: {stats['errors']}")
                print(f"Batch time: {batch_time:.1f}s (avg {batch_time/batch_size:.1f}s/paper)")
                
                # Estimate remaining time
                avg_time_per_paper = batch_time / batch_size
                remaining_papers = total_papers - (i + 1)
                est_remaining_time = remaining_papers * avg_time_per_paper
                print(f"\nEstimated time remaining: {est_remaining_time/60:.1f} minutes")
                
                print(f"\nPausing for 5 seconds to avoid rate limits...")
                await asyncio.sleep(5)
                batch_start_time = time.time()
            
            # Small delay between papers
            elif i < total_papers - 1:
                await asyncio.sleep(0.5)
        
        # Final summary
        total_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("FINAL PROCESSING SUMMARY")
        print("=" * 80)
        print(f"""
Total papers: {stats['total']}
Processed: {stats['processed']}
DOIs found: {stats['doi_found']} ({stats['doi_found']/stats['processed']*100:.1f}% of processed)
PDFs found: {stats['pdf_found']} ({stats['pdf_found']/stats['processed']*100:.1f}% of processed)
Errors: {stats['errors']}
Skipped (already processed): {stats['skipped']}

Total time: {total_time/60:.1f} minutes
Average per paper: {total_time/max(papers_processed, 1):.1f} seconds
""")
        
        # Save final results
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "total_time_seconds": total_time,
            "papers_processed": len(self.progress["results"]),
            "results": self.progress["results"]
        }
        
        with open(self.results_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print(f"Final report saved to: {self.results_file}")
        
        # List papers without PDFs
        papers_without_pdf = [r for r in self.progress["results"] 
                            if not r.get('pdf_stored') and not r.get('error') and r.get('doi')]
        
        if papers_without_pdf:
            print(f"\n{len(papers_without_pdf)} papers have DOIs but no PDFs.")
            print("Creating download list...")
            
            download_list_path = Path(".dev/papers_to_download.txt")
            with open(download_list_path, 'w') as f:
                f.write(f"Papers with DOIs but no PDFs ({len(papers_without_pdf)} total):\n\n")
                for i, result in enumerate(papers_without_pdf, 1):
                    f.write(f"{i}. Storage key: {result['storage_key']}\n")
                    f.write(f"   DOI: https://doi.org/{result['doi']}\n")
                    f.write(f"   Human-readable: {result.get('human_readable_link', 'N/A')}\n\n")
            
            print(f"Download list saved to: {download_list_path}")


async def main():
    """Run the sequential processor."""
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    
    if not bibtex_path.exists():
        print(f"Error: BibTeX file not found: {bibtex_path}")
        return
    
    processor = SequentialProcessor(project_name="pac_research")
    
    # Process all papers with batch size of 10
    await processor.process_all_papers(bibtex_path, batch_size=10)


if __name__ == "__main__":
    asyncio.run(main())