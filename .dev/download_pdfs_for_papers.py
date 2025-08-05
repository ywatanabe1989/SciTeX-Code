#!/usr/bin/env python3
"""Download PDFs for papers with DOIs."""

import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Tuple
import hashlib


class PDFDownloader:
    """Download PDFs for academic papers."""
    
    def __init__(self):
        self.session = None
        self.download_dir = Path(".dev/downloaded_pdfs")
        self.download_dir.mkdir(exist_ok=True)
        
        # Progress tracking
        self.progress_file = Path(".dev/pdf_download_progress.json")
        self.load_progress()
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    def load_progress(self):
        """Load download progress."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "downloaded": [],
                "failed": [],
                "results": {}
            }
    
    def save_progress(self):
        """Save download progress."""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    async def __aenter__(self):
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    def get_pdf_urls(self, doi: str) -> List[str]:
        """Generate potential PDF URLs from DOI."""
        urls = []
        
        # Direct DOI URL
        urls.append(f"https://doi.org/{doi}")
        
        # Common publisher patterns
        if "10.3389" in doi:  # Frontiers
            # Extract article ID from DOI like 10.3389/fnins.2019.00573
            parts = doi.split('/')
            if len(parts) >= 3:
                journal = parts[1].split('.')[-1]  # e.g., fnins
                article_id = parts[-1]  # e.g., 00573
                urls.extend([
                    f"https://www.frontiersin.org/articles/{doi}/pdf",
                    f"https://www.frontiersin.org/articles/{doi}/full/pdf",
                    f"https://www.frontiersin.org/journals/{journal}/articles/{doi}/pdf"
                ])
        
        elif "10.1016" in doi:  # Elsevier
            pii = doi.split('/')[-1]
            urls.extend([
                f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft",
                f"https://pdf.sciencedirectassets.com/pii/{pii}"
            ])
        
        elif "10.1101" in doi:  # bioRxiv
            urls.extend([
                f"https://www.biorxiv.org/content/{doi}.full.pdf",
                f"https://www.biorxiv.org/content/{doi}v1.full.pdf"
            ])
        
        elif "10.1038" in doi:  # Nature
            urls.append(f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf")
        
        elif "10.1109" in doi:  # IEEE
            urls.append(f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={doi.split('.')[-1]}")
        
        elif "10.1523" in doi:  # Journal of Neuroscience
            urls.extend([
                f"https://www.jneurosci.org/content/{doi}.full.pdf",
                f"https://www.eneuro.org/content/{doi}.full.pdf"
            ])
        
        elif "10.3390" in doi:  # MDPI
            journal_id = doi.split('/')[1].split('.')[-1]
            urls.append(f"https://www.mdpi.com/{journal_id}/pdf")
        
        # Add Sci-Hub as last resort
        urls.extend([
            f"https://sci-hub.se/{doi}",
            f"https://sci-hub.st/{doi}",
            f"https://sci-hub.ru/{doi}"
        ])
        
        return urls
    
    async def download_pdf(self, url: str, dest_path: Path) -> bool:
        """Download PDF from URL."""
        try:
            async with self.session.get(url, timeout=30, allow_redirects=True) as response:
                # Check if we got a PDF
                content_type = response.headers.get('content-type', '')
                if response.status == 200 and ('pdf' in content_type or response.content_length > 10000):
                    # Download to temp file first
                    temp_path = dest_path.with_suffix('.tmp')
                    
                    async with aiofiles.open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    # Check if it's actually a PDF
                    with open(temp_path, 'rb') as f:
                        header = f.read(5)
                        if header.startswith(b'%PDF'):
                            # It's a PDF, move to final location
                            temp_path.rename(dest_path)
                            return True
                        else:
                            # Not a PDF, remove temp file
                            temp_path.unlink()
                            return False
        except Exception as e:
            print(f"  Error downloading from {url}: {e}")
            return False
        
        return False
    
    async def download_paper_pdf(self, storage_key: str, doi: str, storage_dir: Path) -> Optional[str]:
        """Try to download PDF for a paper."""
        print(f"\nAttempting to download PDF for {storage_key}")
        print(f"DOI: {doi}")
        
        # Skip if already downloaded
        if storage_key in self.progress["downloaded"]:
            print("  Already downloaded")
            return self.progress["results"].get(storage_key, {}).get("filename")
        
        # Get potential URLs
        urls = self.get_pdf_urls(doi)
        
        # Try each URL
        for i, url in enumerate(urls, 1):
            print(f"  Try {i}/{len(urls)}: {url[:80]}...")
            
            # Generate filename
            if "frontiersin.org" in url and "fnins" in doi:
                # Special case for Frontiers
                filename = f"fnins-{doi.split('.')[-1]}.pdf"
            else:
                # Generic filename
                filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
            
            dest_path = storage_dir / filename
            
            # Try download
            success = await self.download_pdf(url, dest_path)
            
            if success:
                print(f"  ✓ Success! Downloaded to {filename}")
                
                # Update progress
                self.progress["downloaded"].append(storage_key)
                self.progress["results"][storage_key] = {
                    "doi": doi,
                    "filename": filename,
                    "url": url,
                    "size": dest_path.stat().st_size,
                    "downloaded_at": datetime.now().isoformat()
                }
                self.save_progress()
                
                return filename
            
            # Small delay between attempts
            await asyncio.sleep(0.5)
        
        # All attempts failed
        print(f"  ✗ Failed to download PDF")
        self.progress["failed"].append(storage_key)
        self.progress["results"][storage_key] = {
            "doi": doi,
            "error": "All download attempts failed",
            "attempted_at": datetime.now().isoformat()
        }
        self.save_progress()
        
        return None


async def download_missing_pdfs():
    """Download PDFs for papers that don't have them."""
    print("=" * 80)
    print("DOWNLOADING MISSING PDFs")
    print("=" * 80)
    
    # Load the papers that need PDFs
    results_file = Path(".dev/all_papers_results.json")
    if not results_file.exists():
        print("No results file found. Run processing first.")
        return
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Get papers with DOIs but no PDFs
    papers_needing_pdf = [
        r for r in data["results"] 
        if r.get("doi") and not r.get("pdf_stored") and not r.get("error")
    ]
    
    print(f"\nFound {len(papers_needing_pdf)} papers needing PDFs")
    
    # Process in batches
    batch_size = 5
    async with PDFDownloader() as downloader:
        for i in range(0, len(papers_needing_pdf), batch_size):
            batch = papers_needing_pdf[i:i+batch_size]
            print(f"\n{'=' * 40}")
            print(f"Processing batch {i//batch_size + 1}/{(len(papers_needing_pdf) + batch_size - 1)//batch_size}")
            print(f"{'=' * 40}")
            
            # Download PDFs in parallel within batch
            tasks = []
            for paper in batch:
                storage_key = paper["storage_key"]
                doi = paper["doi"]
                
                # Get storage directory
                storage_dir = Path(f"/home/ywatanabe/.scitex/scholar/library/pac_research/{storage_key}")
                
                task = downloader.download_paper_pdf(storage_key, doi, storage_dir)
                tasks.append(task)
            
            # Wait for batch to complete
            results = await asyncio.gather(*tasks)
            
            # Summary for batch
            successful = sum(1 for r in results if r is not None)
            print(f"\nBatch complete: {successful}/{len(batch)} PDFs downloaded")
            
            # Pause between batches
            if i + batch_size < len(papers_needing_pdf):
                print("\nPausing 5 seconds before next batch...")
                await asyncio.sleep(5)
    
    # Final summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    
    with open(downloader.progress_file, 'r') as f:
        final_progress = json.load(f)
    
    print(f"Total downloaded: {len(final_progress['downloaded'])}")
    print(f"Total failed: {len(final_progress['failed'])}")
    
    # Show some successful downloads
    if final_progress['downloaded']:
        print("\nSuccessfully downloaded (first 5):")
        for key in final_progress['downloaded'][:5]:
            result = final_progress['results'].get(key, {})
            print(f"  - {key}: {result.get('filename', 'Unknown')}")


if __name__ == "__main__":
    # Run the downloader
    asyncio.run(download_missing_pdfs())