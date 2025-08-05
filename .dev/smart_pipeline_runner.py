#!/usr/bin/env python3
"""Smart pipeline runner that uses lookup table to avoid redundant work."""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Papers
from scitex.scholar.doi import DOIResolver


class SmartPipelineRunner:
    """Smart runner that checks what's already done."""
    
    def __init__(self):
        # Load lookup table
        self.lookup_file = Path(".dev/pac_research_lookup.json")
        self.load_lookup()
        
        # Progress tracking
        self.progress_file = Path(".dev/smart_pipeline_progress.json")
        self.load_progress()
        
        # Initialize components
        self.doi_resolver = DOIResolver()
    
    def load_lookup(self):
        """Load the lookup table."""
        if self.lookup_file.exists():
            with open(self.lookup_file, 'r') as f:
                self.lookup_data = json.load(f)
        else:
            print("No lookup table found. Run create_lookup_table.py first.")
            sys.exit(1)
    
    def load_progress(self):
        """Load progress tracking."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "dois_resolved": [],
                "pdfs_downloaded": [],
                "metadata_enriched": [],
                "errors": []
            }
    
    def save_progress(self):
        """Save progress."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def download_pdf_with_wget(self, doi: str, storage_dir: Path) -> bool:
        """Download PDF using wget with various strategies."""
        print(f"  Attempting to download PDF for DOI: {doi}")
        
        # Generate potential URLs
        urls = []
        
        # Frontiers (open access)
        if "10.3389" in doi:
            urls.extend([
                f"https://www.frontiersin.org/articles/{doi}/pdf",
                f"https://www.frontiersin.org/journals/articles/{doi}/pdf"
            ])
        
        # bioRxiv/medRxiv (open access)
        elif "10.1101" in doi:
            urls.extend([
                f"https://www.biorxiv.org/content/{doi}v1.full.pdf",
                f"https://www.biorxiv.org/content/{doi}.full.pdf",
                f"https://www.medrxiv.org/content/{doi}v1.full.pdf"
            ])
        
        # MDPI (open access)
        elif "10.3390" in doi:
            # Extract journal and article ID
            parts = doi.split('/')
            if len(parts) >= 2:
                journal_code = parts[0].split('.')[-1]
                article_id = parts[-1]
                urls.append(f"https://www.mdpi.com/{journal_code}/article/{doi}/pdf")
        
        # PLoS (open access)
        elif "10.1371" in doi:
            urls.extend([
                f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable",
                f"https://journals.plos.org/ploscompbiol/article/file?id={doi}&type=printable"
            ])
        
        # IEEE (try anyway)
        elif "10.1109" in doi:
            urls.append(f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={doi.split('.')[-1]}")
        
        # Nature Scientific Reports (open access)
        elif "10.1038" in doi and "s41598" in doi:
            article_id = doi.split('/')[-1]
            urls.append(f"https://www.nature.com/articles/{article_id}.pdf")
        
        # eNeuro (open access)
        elif "10.1523/eneuro" in doi:
            urls.append(f"https://www.eneuro.org/content/{doi.replace('10.1523/', '')}.full.pdf")
        
        # Add generic DOI URL as fallback
        urls.append(f"https://doi.org/{doi}")
        
        # Try each URL
        for url in urls:
            print(f"    Trying: {url}")
            
            # Generate filename
            filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
            pdf_path = storage_dir / filename
            
            # Use wget with proper headers
            cmd = [
                "wget", "-q", "--timeout=30",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-O", str(pdf_path),
                url
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=60)
                
                # Check if we got a valid PDF
                if pdf_path.exists() and pdf_path.stat().st_size > 10000:
                    # Verify it's a PDF
                    with open(pdf_path, 'rb') as f:
                        header = f.read(5)
                        if header.startswith(b'%PDF'):
                            print(f"    ✓ SUCCESS! Downloaded {filename} ({pdf_path.stat().st_size:,} bytes)")
                            return True
                        else:
                            # Not a PDF, probably HTML
                            pdf_path.unlink()
                else:
                    # Too small or doesn't exist
                    if pdf_path.exists():
                        pdf_path.unlink()
            
            except Exception as e:
                print(f"    Error: {e}")
                if pdf_path.exists():
                    pdf_path.unlink()
        
        print(f"    ✗ Failed to download PDF from all sources")
        return False
    
    async def process_papers_needing_pdfs(self):
        """Process papers that have DOIs but no PDFs."""
        print("\n" + "=" * 80)
        print("DOWNLOADING PDFS FOR PAPERS WITH DOIS")
        print("=" * 80)
        
        storage_info = self.lookup_data["storage_info"]
        
        # Find papers with DOI but no PDF
        need_pdf = [(key, info) for key, info in storage_info.items() 
                   if info["doi"] and not info["has_pdf"]]
        
        print(f"\nFound {len(need_pdf)} papers with DOIs but no PDFs")
        
        # Process in batches
        batch_size = 10
        successful = 0
        
        for i in range(0, len(need_pdf), batch_size):
            batch = need_pdf[i:i+batch_size]
            
            print(f"\n{'=' * 40}")
            print(f"Processing batch {i//batch_size + 1}/{(len(need_pdf) + batch_size - 1)//batch_size}")
            print(f"{'=' * 40}")
            
            for storage_key, info in batch:
                if storage_key in self.progress["pdfs_downloaded"]:
                    print(f"\nSkipping {storage_key} - already processed")
                    continue
                
                print(f"\n[{storage_key}] {info['title'][:60]}...")
                storage_dir = Path(info["storage_path"])
                
                # Try to download PDF
                success = self.download_pdf_with_wget(info["doi"], storage_dir)
                
                if success:
                    successful += 1
                    self.progress["pdfs_downloaded"].append(storage_key)
                    self.save_progress()
                else:
                    self.progress["errors"].append({
                        "storage_key": storage_key,
                        "doi": info["doi"],
                        "error": "PDF download failed",
                        "timestamp": datetime.now().isoformat()
                    })
                    self.save_progress()
                
                # Small delay
                await asyncio.sleep(0.5)
            
            # Pause between batches
            if i + batch_size < len(need_pdf):
                print(f"\nPausing 5 seconds before next batch...")
                await asyncio.sleep(5)
        
        print(f"\n{'=' * 80}")
        print(f"PDF DOWNLOAD SUMMARY")
        print(f"{'=' * 80}")
        print(f"Successfully downloaded: {successful}/{len(need_pdf)} PDFs")
    
    async def process_papers_needing_dois(self):
        """Process papers that don't have DOIs."""
        print("\n" + "=" * 80)
        print("RESOLVING DOIS FOR PAPERS WITHOUT THEM")
        print("=" * 80)
        
        storage_info = self.lookup_data["storage_info"]
        
        # Find papers without DOI
        need_doi = [(key, info) for key, info in storage_info.items() 
                   if not info["doi"]]
        
        print(f"\nFound {len(need_doi)} papers without DOIs")
        
        successful = 0
        
        for storage_key, info in need_doi:
            if storage_key in self.progress["dois_resolved"]:
                print(f"\nSkipping {storage_key} - already processed")
                continue
            
            print(f"\n[{storage_key}] {info['title'][:60] if info['title'] else 'No title'}...")
            
            # Try to resolve DOI
            if info.get('title') and info.get('year'):
                try:
                    # Format authors
                    authors = info.get('authors', [])
                    if isinstance(authors, list):
                        authors_str = ' and '.join(authors)
                    else:
                        authors_str = str(authors)
                    
                    # Resolve DOI
                    doi_result = await self.doi_resolver.title_to_doi_async(
                        title=info['title'],
                        year=str(info['year']),
                        authors=authors_str,
                        sources=['crossref', 'semanticscholar']
                    )
                    
                    if doi_result:
                        if isinstance(doi_result, dict):
                            doi = doi_result.get('doi')
                        else:
                            doi = doi_result
                        
                        if doi:
                            print(f"  ✓ Found DOI: {doi}")
                            
                            # Update metadata file
                            metadata_path = Path(info["storage_path"]) / "metadata.json"
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                            
                            metadata['doi'] = doi
                            metadata['doi_source'] = 'SmartPipelineRunner'
                            metadata['doi_resolved_at'] = datetime.now().isoformat()
                            
                            with open(metadata_path, 'w') as f:
                                json.dump(metadata, f, indent=2)
                            
                            successful += 1
                            self.progress["dois_resolved"].append(storage_key)
                            self.save_progress()
                        else:
                            print(f"  ✗ No DOI found")
                    else:
                        print(f"  ✗ No DOI found")
                        
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    self.progress["errors"].append({
                        "storage_key": storage_key,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
                    self.save_progress()
            else:
                print(f"  ✗ Missing title or year - cannot resolve DOI")
            
            # Small delay
            await asyncio.sleep(0.5)
        
        print(f"\n{'=' * 80}")
        print(f"DOI RESOLUTION SUMMARY")
        print(f"{'=' * 80}")
        print(f"Successfully resolved: {successful}/{len(need_doi)} DOIs")
    
    async def run(self):
        """Run the smart pipeline."""
        print("=" * 80)
        print("SMART PIPELINE RUNNER")
        print("=" * 80)
        print(f"Using lookup table from: {self.lookup_file}")
        
        start_time = time.time()
        
        # First resolve missing DOIs
        await self.process_papers_needing_dois()
        
        # Rebuild lookup table to include newly resolved DOIs
        print("\nRebuilding lookup table...")
        subprocess.run(["python", ".dev/create_lookup_table.py"], capture_output=True)
        self.load_lookup()
        
        # Then download PDFs for all papers with DOIs
        await self.process_papers_needing_pdfs()
        
        # Final summary
        total_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("SMART PIPELINE COMPLETE")
        print("=" * 80)
        print(f"Total time: {total_time/60:.1f} minutes")
        print(f"\nProgress saved to: {self.progress_file}")
        print("\nRun create_lookup_table.py again to see updated status")


if __name__ == "__main__":
    runner = SmartPipelineRunner()
    asyncio.run(runner.run())