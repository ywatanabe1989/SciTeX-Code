#!/usr/bin/env python3
"""Run the full scholar pipeline from BibTeX to organized PDFs."""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import random
import string
import shutil
import hashlib
from typing import Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Papers
from scitex.scholar.doi import DOIResolver, BatchDOIResolver
from scitex.scholar.enrichment import MetadataEnricher, ResumableEnricher
# from scitex.scholar.download import BrowserDownloadHelper
# from scitex.scholar.storage import EnhancedStorageManager
# from scitex.scholar.lookup import LookupIndex


class ScholarPipeline:
    """Full scholar workflow pipeline."""
    
    def __init__(self, project_name: str = "pac_research"):
        self.project_name = project_name
        self.start_time = time.time()
        
        # Set up directories
        self.scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
        self.scholar_dir = self.scitex_dir / "scholar"
        self.library_dir = self.scholar_dir / "library"
        self.project_dir = self.library_dir / project_name
        self.human_readable_dir = self.library_dir / f"{project_name}-human-readable"
        
        # Create directories
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.human_readable_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.doi_resolver = DOIResolver()
        self.enricher = MetadataEnricher()
        # self.storage = EnhancedStorageManager()
        # self.lookup = LookupIndex()
        # self.download_helper = BrowserDownloadHelper()
        
        # Statistics
        self.stats = {
            "total_papers": 0,
            "dois_resolved": 0,
            "metadata_enriched": 0,
            "pdfs_downloaded": 0,
            "pdfs_organized": 0,
            "failed_downloads": 0
        }
    
    def generate_storage_key(self) -> str:
        """Generate 8-character storage key."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    async def load_bibtex(self, bibtex_path: Path) -> Papers:
        """Load papers from BibTeX file."""
        print("\n" + "=" * 80)
        print("STEP 1: LOADING BIBTEX FILE")
        print("=" * 80)
        
        papers = Papers.from_bibtex(bibtex_path)
        self.stats["total_papers"] = len(papers)
        
        print(f"Loaded {len(papers)} papers from {bibtex_path}")
        print(f"First 3 papers:")
        for i, (key, paper) in enumerate(list(papers.items())[:3]):
            print(f"  {i+1}. {paper.get('title', 'No title')[:60]}...")
        
        return papers
    
    async def resolve_dois(self, papers: Papers) -> Papers:
        """Resolve DOIs for papers."""
        print("\n" + "=" * 80)
        print("STEP 2: RESOLVING DOIS")
        print("=" * 80)
        
        papers_needing_doi = [(k, p) for k, p in papers.items() if not p.get('doi')]
        print(f"Papers needing DOI resolution: {len(papers_needing_doi)}/{len(papers)}")
        
        if papers_needing_doi:
            # Process in small batches
            batch_size = 5
            for i in range(0, len(papers_needing_doi), batch_size):
                batch = papers_needing_doi[i:i+batch_size]
                print(f"\nProcessing batch {i//batch_size + 1}/{(len(papers_needing_doi) + batch_size - 1)//batch_size}")
                
                for key, paper in batch:
                    title = paper.get('title', '')
                    year = paper.get('year', '')
                    authors = paper.get('author', '')
                    
                    print(f"  Resolving: {title[:50]}...")
                    try:
                        doi = await self.doi_resolver.title_to_doi_async(
                            title=title,
                            year=year,
                            authors=authors,
                            sources=['crossref', 'openalex', 'semanticscholar']
                        )
                        if doi:
                            papers[key]['doi'] = doi
                            papers[key]['doi_source'] = 'ResumableDOIResolver'
                            self.stats["dois_resolved"] += 1
                            print(f"    ✓ Found DOI: {doi}")
                        else:
                            print(f"    ✗ No DOI found")
                    except Exception as e:
                        print(f"    ✗ Error: {e}")
                
                # Small delay between batches
                if i + batch_size < len(papers_needing_doi):
                    await asyncio.sleep(1)
        
        print(f"\nDOIs resolved: {self.stats['dois_resolved']}/{len(papers_needing_doi)}")
        return papers
    
    async def enrich_metadata(self, papers: Papers) -> Papers:
        """Enrich paper metadata."""
        print("\n" + "=" * 80)
        print("STEP 3: ENRICHING METADATA")
        print("=" * 80)
        
        enriched_count = 0
        for key, paper in papers.items():
            if paper.get('doi'):
                print(f"\nEnriching: {paper.get('title', '')[:50]}...")
                try:
                    enriched = self.enricher.enrich_from_doi(paper['doi'])
                    if enriched:
                        # Merge enriched data
                        for field, value in enriched.items():
                            if value and not paper.get(field):
                                paper[field] = value
                                paper[f"{field}_source"] = 'PaperEnricher'
                        enriched_count += 1
                        print(f"  ✓ Enriched with {len(enriched)} fields")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
        
        self.stats["metadata_enriched"] = enriched_count
        print(f"\nMetadata enriched: {enriched_count}/{len(papers)}")
        return papers
    
    def organize_paper(self, paper: Dict, pdf_path: Optional[Path] = None) -> Dict:
        """Organize a single paper in the directory structure."""
        # Generate storage key
        storage_key = self.generate_storage_key()
        storage_dir = self.project_dir / storage_key
        storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (storage_dir / "attachments").mkdir(exist_ok=True)
        (storage_dir / "screenshots").mkdir(exist_ok=True)
        
        # Save metadata
        metadata = {
            "storage_id": storage_key,
            "project": self.project_name,
            **paper,
            "created_at": datetime.now().isoformat()
        }
        
        with open(storage_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Handle PDF if provided
        pdf_filename = None
        if pdf_path and pdf_path.exists():
            # Determine original filename
            if paper.get('doi'):
                # Try to get journal-style filename
                pdf_filename = f"{paper.get('journal', 'unknown')}-{paper.get('volume', 'v')}-{paper.get('pages', 'p').replace('-', '_')}.pdf"
                pdf_filename = pdf_filename.replace(' ', '_').replace('/', '_')
            else:
                pdf_filename = pdf_path.name
            
            dest_path = storage_dir / pdf_filename
            shutil.copy2(pdf_path, dest_path)
            
            # Calculate hash
            with open(dest_path, 'rb') as f:
                pdf_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Save storage metadata
            storage_metadata = {
                "storage_key": storage_key,
                "filename": pdf_filename,
                "original_filename": pdf_filename,
                "pdf_hash": pdf_hash,
                "size_bytes": dest_path.stat().st_size,
                "stored_at": datetime.now().isoformat()
            }
            
            with open(storage_dir / "storage_metadata.json", 'w') as f:
                json.dump(storage_metadata, f, indent=2)
        
        # Create human-readable link
        authors = paper.get('author', 'Unknown')
        if isinstance(authors, str):
            first_author = authors.split(' and ')[0].split(',')[0].strip()
        elif isinstance(authors, list):
            first_author = authors[0].split(',')[0].strip()
        else:
            first_author = 'Unknown'
        
        first_author = ''.join(c for c in first_author if c.isalnum())
        year = paper.get('year', 'YYYY')
        journal = paper.get('journal', paper.get('booktitle', 'Unknown'))
        
        # Abbreviate journal
        journal_parts = journal.split()
        if len(journal_parts) > 1:
            journal_abbrev = ''.join(word[0].upper() for word in journal_parts if word[0].isupper())
        else:
            journal_abbrev = journal[:10].replace(' ', '')
        
        link_name = f"{first_author}-{year}-{journal_abbrev}"
        link_path = self.human_readable_dir / link_name
        
        # Create relative symlink
        relative_target = Path("..") / self.project_name / storage_key
        
        if link_path.exists():
            link_path.unlink()
        
        try:
            link_path.symlink_to(relative_target)
        except Exception as e:
            print(f"Could not create symlink: {e}")
        
        return {
            "storage_key": storage_key,
            "storage_dir": str(storage_dir),
            "pdf_filename": pdf_filename,
            "human_readable_link": str(link_path)
        }
    
    async def download_pdfs(self, papers: Papers) -> Tuple[List[str], List[str]]:
        """Attempt to download PDFs for papers."""
        print("\n" + "=" * 80)
        print("STEP 4: DOWNLOADING PDFS")
        print("=" * 80)
        
        downloaded = []
        failed = []
        
        # For this demo, we'll just check if we already have the PDFs
        existing_pdfs_dir = self.scholar_dir / "pdfs"
        
        for key, paper in papers.items():
            title = paper.get('title', 'Unknown')
            print(f"\nProcessing: {title[:50]}...")
            
            # Check if PDF already exists
            existing_pdf = None
            if existing_pdfs_dir.exists():
                # Look for matching PDF
                for pdf in existing_pdfs_dir.glob("*.pdf"):
                    if key.lower() in pdf.stem.lower():
                        existing_pdf = pdf
                        break
            
            # Organize the paper
            if existing_pdf:
                print(f"  ✓ Found existing PDF: {existing_pdf.name}")
                result = self.organize_paper(paper, existing_pdf)
                downloaded.append(key)
                self.stats["pdfs_downloaded"] += 1
                self.stats["pdfs_organized"] += 1
            else:
                print(f"  ✗ No PDF found")
                result = self.organize_paper(paper)
                failed.append(key)
                self.stats["failed_downloads"] += 1
            
            # Update lookup index (if available)
            # if paper.get('doi') and hasattr(self, 'lookup'):
            #     self.lookup.add_entry(
            #         doi=paper['doi'],
            #         storage_key=result['storage_key'],
            #         has_pdf=existing_pdf is not None,
            #         original_filename=result.get('pdf_filename')
            #     )
        
        print(f"\nDownload summary:")
        print(f"  Downloaded: {len(downloaded)}")
        print(f"  Failed: {len(failed)}")
        
        return downloaded, failed
    
    def generate_download_helper(self, papers: Papers, failed_keys: List[str]):
        """Generate HTML helper for manual downloads."""
        print("\n" + "=" * 80)
        print("STEP 5: GENERATING DOWNLOAD HELPER")
        print("=" * 80)
        
        if not failed_keys:
            print("No failed downloads - skipping helper generation")
            return
        
        failed_papers = {k: papers[k] for k in failed_keys if k in papers}
        
        # Create simple download list
        download_list_path = Path(".dev/papers_to_download.txt")
        with open(download_list_path, 'w') as f:
            f.write(f"Papers needing manual download ({len(failed_papers)} total):\n\n")
            for i, (key, paper) in enumerate(failed_papers.items(), 1):
                f.write(f"{i}. {paper.get('title', 'Unknown')}\n")
                if paper.get('doi'):
                    f.write(f"   DOI: https://doi.org/{paper['doi']}\n")
                if paper.get('url'):
                    f.write(f"   URL: {paper['url']}\n")
                f.write("\n")
        
        print(f"Created download list:")
        print(f"  File: {download_list_path}")
        print(f"  Papers to download: {len(failed_papers)}")
    
    def generate_report(self):
        """Generate final report."""
        print("\n" + "=" * 80)
        print("FINAL REPORT")
        print("=" * 80)
        
        duration = time.time() - self.start_time
        
        print(f"""
Pipeline Summary:
-----------------
Total papers processed: {self.stats['total_papers']}
DOIs resolved: {self.stats['dois_resolved']}
Metadata enriched: {self.stats['metadata_enriched']}
PDFs downloaded: {self.stats['pdfs_downloaded']}
PDFs organized: {self.stats['pdfs_organized']}
Failed downloads: {self.stats['failed_downloads']}

Time taken: {duration:.1f} seconds

Project structure:
  Library: {self.library_dir}
  Project: {self.project_dir}
  Human-readable: {self.human_readable_dir}
""")
        
        # Save report
        report_path = Path(".dev/pipeline_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                "project_name": self.project_name,
                "statistics": self.stats,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "paths": {
                    "library": str(self.library_dir),
                    "project": str(self.project_dir),
                    "human_readable": str(self.human_readable_dir)
                }
            }, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
    
    async def run(self, bibtex_path: Path):
        """Run the full pipeline."""
        print("=" * 80)
        print("SCHOLAR WORKFLOW PIPELINE")
        print("=" * 80)
        print(f"Project: {self.project_name}")
        print(f"BibTeX: {bibtex_path}")
        
        # Step 1: Load BibTeX
        papers = await self.load_bibtex(bibtex_path)
        
        # Step 2: Resolve DOIs (limit to first 5 for demo)
        print("\n[NOTE: Limiting to first 5 papers for demo]")
        demo_papers = Papers(dict(list(papers.items())[:5]))
        demo_papers = await self.resolve_dois(demo_papers)
        
        # Step 3: Enrich metadata
        demo_papers = await self.enrich_metadata(demo_papers)
        
        # Step 4: Download/organize PDFs
        downloaded, failed = await self.download_pdfs(demo_papers)
        
        # Step 5: Generate download helper
        if failed:
            self.generate_download_helper(demo_papers, failed)
        
        # Step 6: Generate report
        self.generate_report()
        
        print("\n✓ Pipeline completed!")


async def main():
    """Run the scholar pipeline."""
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    
    if not bibtex_path.exists():
        print(f"Error: BibTeX file not found: {bibtex_path}")
        return
    
    pipeline = ScholarPipeline(project_name="pac_research")
    await pipeline.run(bibtex_path)


if __name__ == "__main__":
    asyncio.run(main())