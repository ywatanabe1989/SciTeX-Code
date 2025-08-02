#!/usr/bin/env python3
"""Download PDFs with longer timeouts and better retry logic."""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def download_pdf_with_wget(doi: str, storage_dir: Path, timeout: int = 300) -> bool:
    """Download PDF using wget with longer timeout.
    
    Args:
        doi: DOI to download
        storage_dir: Directory to save PDF
        timeout: Timeout in seconds (default 5 minutes)
    """
    print(f"  Attempting to download PDF for DOI: {doi}")
    
    # Generate potential URLs based on publisher
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
    
    # PLoS (open access)
    elif "10.1371" in doi:
        urls.extend([
            f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable",
            f"https://journals.plos.org/ploscompbiol/article/file?id={doi}&type=printable"
        ])
    
    # Nature Scientific Reports (open access)
    elif "10.1038" in doi and "s41598" in doi:
        article_id = doi.split('/')[-1]
        urls.append(f"https://www.nature.com/articles/{article_id}.pdf")
    
    # eNeuro (open access)
    elif "10.1523/eneuro" in doi:
        urls.append(f"https://www.eneuro.org/content/{doi.replace('10.1523/', '')}.full.pdf")
    
    # eLife (open access)
    elif "10.7554" in doi:
        urls.append(f"https://elifesciences.org/articles/{doi.split('/')[-1]}.pdf")
    
    # Add generic DOI URL as fallback
    urls.append(f"https://doi.org/{doi}")
    
    # Try each URL with longer timeout
    for url in urls:
        print(f"    Trying: {url}")
        
        # Generate filename
        filename = f"{doi.replace('/', '_').replace('.', '_')}.pdf"
        pdf_path = storage_dir / filename
        
        # Use wget with longer timeout and better options
        cmd = [
            "wget",
            "--timeout=" + str(timeout),  # Connection timeout
            "--read-timeout=" + str(timeout),  # Read timeout
            "--tries=3",  # Retry 3 times
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--no-check-certificate",  # Some sites have cert issues
            "-O", str(pdf_path),
            url
        ]
        
        try:
            # Run with longer subprocess timeout (timeout + buffer)
            result = subprocess.run(cmd, capture_output=True, timeout=timeout + 60)
            
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
                        print(f"    ✗ Not a PDF file (got HTML or other format)")
            else:
                # Too small or doesn't exist
                if pdf_path.exists():
                    pdf_path.unlink()
                print(f"    ✗ File too small or download failed")
        
        except subprocess.TimeoutExpired:
            print(f"    ✗ Timeout after {timeout} seconds")
            if pdf_path.exists():
                pdf_path.unlink()
        except Exception as e:
            print(f"    ✗ Error: {e}")
            if pdf_path.exists():
                pdf_path.unlink()
    
    print(f"    ✗ Failed to download PDF from all sources")
    return False


async def download_missing_pdfs():
    """Download PDFs for papers that have DOIs but no PDFs."""
    print("=" * 80)
    print("DOWNLOADING MISSING PDFS WITH LONGER TIMEOUTS")
    print("=" * 80)
    
    # Load lookup table
    lookup_file = Path(".dev/pac_research_lookup.json")
    if not lookup_file.exists():
        print("Run create_lookup_table.py first!")
        return
    
    with open(lookup_file, 'r') as f:
        lookup_data = json.load(f)
    
    storage_info = lookup_data["storage_info"]
    
    # Find papers with DOI but no PDF
    need_pdf = [(key, info) for key, info in storage_info.items() 
               if info["doi"] and not info["has_pdf"]]
    
    print(f"\nFound {len(need_pdf)} papers with DOIs but no PDFs")
    print(f"Using timeout of 5 minutes per download\n")
    
    # Process one at a time with progress
    successful = 0
    failed = []
    
    for i, (storage_key, info) in enumerate(need_pdf):
        print(f"\n[{i+1}/{len(need_pdf)}] {storage_key}: {info['title'][:60]}...")
        storage_dir = Path(info["storage_path"])
        
        # Try to download PDF
        start_time = time.time()
        success = download_pdf_with_wget(info["doi"], storage_dir, timeout=300)
        download_time = time.time() - start_time
        
        if success:
            successful += 1
            print(f"    Download completed in {download_time:.1f} seconds")
        else:
            failed.append({
                "storage_key": storage_key,
                "doi": info["doi"],
                "title": info["title"]
            })
        
        # Progress report every 10 papers
        if (i + 1) % 10 == 0:
            print(f"\n{'=' * 60}")
            print(f"Progress: {i+1}/{len(need_pdf)} processed")
            print(f"Successful: {successful}")
            print(f"Failed: {len(failed)}")
            print(f"{'=' * 60}\n")
        
        # Small delay between downloads
        await asyncio.sleep(1)
    
    # Final summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Total papers with DOIs: {len(need_pdf)}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed downloads: {len(failed)}")
    
    if failed:
        print(f"\nFailed papers (first 10):")
        for f in failed[:10]:
            print(f"  - {f['doi']}: {f['title'][:50]}...")
    
    # Save failed list for manual download
    if failed:
        failed_file = Path(".dev/failed_pdf_downloads.json")
        with open(failed_file, 'w') as f:
            json.dump(failed, f, indent=2)
        print(f"\nFailed downloads saved to: {failed_file}")


if __name__ == "__main__":
    asyncio.run(download_missing_pdfs())