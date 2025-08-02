#!/usr/bin/env python3
"""Run the complete pipeline for each paper including PDF downloads."""

import asyncio
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import os
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Papers
from test_complete_single_paper_pipeline import SinglePaperPipeline


class EnhancedPipeline(SinglePaperPipeline):
    """Enhanced pipeline that includes PDF download."""
    
    async def download_pdf_for_paper(self, doi: str, storage_dir: Path) -> Optional[Path]:
        """Download PDF using various methods."""
        if not doi:
            return None
        
        print("\n  Attempting PDF download...")
        
        # Method 1: Try using Unpaywall for open access
        unpaywall_url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
        
        # Method 2: Direct DOI link
        doi_url = f"https://doi.org/{doi}"
        
        # Method 3: Use puppeteer if available
        if doi.startswith("10.3389"):  # Frontiers is open access
            pdf_url = f"https://www.frontiersin.org/articles/{doi}/pdf"
            try:
                # Use wget or curl
                filename = f"{doi.replace('/', '_')}.pdf"
                pdf_path = storage_dir / filename
                
                cmd = f"wget -q --user-agent='Mozilla/5.0' -O '{pdf_path}' '{pdf_url}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                
                if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 1000:
                    # Check if it's a PDF
                    with open(pdf_path, 'rb') as f:
                        header = f.read(5)
                        if header.startswith(b'%PDF'):
                            print(f"    ✓ Downloaded PDF: {filename}")
                            return pdf_path
                        else:
                            pdf_path.unlink()
            except Exception as e:
                print(f"    Error: {e}")
        
        # Method 4: Try bioRxiv/medRxiv
        if doi.startswith("10.1101"):
            pdf_url = f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
            try:
                filename = f"{doi.replace('/', '_')}.pdf"
                pdf_path = storage_dir / filename
                
                cmd = f"wget -q --user-agent='Mozilla/5.0' -O '{pdf_path}' '{pdf_url}'"
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                
                if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 1000:
                    with open(pdf_path, 'rb') as f:
                        header = f.read(5)
                        if header.startswith(b'%PDF'):
                            print(f"    ✓ Downloaded PDF from bioRxiv: {filename}")
                            return pdf_path
                        else:
                            pdf_path.unlink()
            except Exception as e:
                print(f"    Error: {e}")
        
        print("    ✗ Could not download PDF")
        return None
    
    async def process_paper(self, paper, paper_key: str):
        """Process a single paper through the complete pipeline."""
        print("=" * 80)
        print("COMPLETE SINGLE PAPER PIPELINE")
        print("=" * 80)
        
        # Call the parent process_paper to do all the standard steps
        result = await super().process_paper(paper, paper_key)
        
        # Now try to download PDF if we don't have one
        if result and result.get("doi") and not result.get("pdf_stored"):
            storage_key = result["storage_key"]
            doi = result["doi"]
            storage_dir = self.project_dir / storage_key
            
            # Try to download PDF
            pdf_path = await self.download_pdf_for_paper(doi, storage_dir)
            
            if pdf_path:
                # Update metadata to reflect PDF
                metadata_path = storage_dir / "metadata.json"
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata["pdf_filename"] = pdf_path.name
                metadata["pdf_downloaded_at"] = datetime.now().isoformat()
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                result["pdf_stored"] = True
                result["pdf_filename"] = pdf_path.name
                
                print(f"\n✓ PDF successfully downloaded and stored!")
        
        return result


async def run_complete_pipeline_for_all():
    """Run the complete pipeline for all papers."""
    print("=" * 80)
    print("RUNNING COMPLETE PIPELINE FOR ALL PAPERS")
    print("=" * 80)
    
    # Load papers
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    papers = Papers.from_bibtex(bibtex_path)
    print(f"\nLoaded {len(papers)} papers from BibTeX\n")
    
    # Initialize enhanced pipeline
    pipeline = EnhancedPipeline(project_name="pac_research")
    
    # Statistics
    stats = {
        "total": len(papers),
        "processed": 0,
        "doi_found": 0,
        "pdf_downloaded": 0,
        "errors": 0
    }
    
    results = []
    start_time = time.time()
    
    # Process each paper
    for i in range(len(papers)):
        paper = papers[i]
        
        # Get bibtex key
        if hasattr(paper, '_bibtex_key'):
            paper_key = paper._bibtex_key
        elif hasattr(paper, '_additional_metadata'):
            paper_key = paper._additional_metadata.get('bibtex_key', f'paper_{i}')
        else:
            paper_key = f"paper_{i}"
        
        print(f"\n{'#' * 80}")
        print(f"# PROCESSING PAPER {i+1}/{len(papers)}: {paper_key}")
        print(f"{'#' * 80}")
        
        try:
            # Run complete pipeline for this paper
            result = await pipeline.process_paper(paper, paper_key)
            results.append(result)
            
            # Update statistics
            stats["processed"] += 1
            if result.get("doi"):
                stats["doi_found"] += 1
            if result.get("pdf_stored"):
                stats["pdf_downloaded"] += 1
            
            # Progress report every 10 papers
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / (i + 1)
                remaining = (len(papers) - i - 1) * avg_time
                
                print(f"\n{'=' * 60}")
                print(f"PROGRESS REPORT: {i+1}/{len(papers)} papers processed")
                print(f"DOIs found: {stats['doi_found']} ({stats['doi_found']/(i+1)*100:.1f}%)")
                print(f"PDFs downloaded: {stats['pdf_downloaded']} ({stats['pdf_downloaded']/(i+1)*100:.1f}%)")
                print(f"Time elapsed: {elapsed/60:.1f} min")
                print(f"Est. time remaining: {remaining/60:.1f} min")
                print(f"{'=' * 60}")
            
        except Exception as e:
            print(f"\n✗ Error processing paper: {e}")
            stats["errors"] += 1
            results.append({"paper_key": paper_key, "error": str(e)})
        
        # Small delay between papers
        if i < len(papers) - 1:
            await asyncio.sleep(1)
    
    # Final summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE - FINAL SUMMARY")
    print("=" * 80)
    print(f"""
Total papers: {stats['total']}
Processed: {stats['processed']}
DOIs found: {stats['doi_found']} ({stats['doi_found']/stats['total']*100:.1f}%)
PDFs downloaded: {stats['pdf_downloaded']} ({stats['pdf_downloaded']/stats['total']*100:.1f}%)
Errors: {stats['errors']}

Total time: {total_time/60:.1f} minutes
Average per paper: {total_time/stats['total']:.1f} seconds
""")
    
    # Save complete results
    complete_results = {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats,
        "total_time_seconds": total_time,
        "results": results
    }
    
    results_path = Path(".dev/complete_pipeline_results.json")
    with open(results_path, 'w') as f:
        json.dump(complete_results, f, indent=2)
    
    print(f"Complete results saved to: {results_path}")
    
    # List successfully downloaded PDFs
    pdfs_downloaded = [r for r in results if r.get("pdf_stored")]
    if pdfs_downloaded:
        print(f"\nSuccessfully downloaded {len(pdfs_downloaded)} PDFs:")
        for r in pdfs_downloaded[:10]:  # Show first 10
            print(f"  - {r.get('storage_key')}: {r.get('pdf_filename', 'Unknown')}")
        if len(pdfs_downloaded) > 10:
            print(f"  ... and {len(pdfs_downloaded) - 10} more")


if __name__ == "__main__":
    # Clear any previous incomplete runs
    import warnings
    warnings.filterwarnings("ignore")
    
    asyncio.run(run_complete_pipeline_for_all())