#!/usr/bin/env python3
"""
Simple standalone PDF downloader using crawl4ai directly.
No complex dependencies, just crawl4ai and basic Python.
"""

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from crawl4ai import AsyncWebCrawler


async def download_pdf_with_crawl4ai(url: str, output_path: Path) -> bool:
    """Download PDF using crawl4ai."""
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            # Try to download the PDF
            result = await crawler.arun(
                url=url,
                bypass_cache=True,
                wait_for="networkidle",
                timeout=30000
            )
            
            # Check if we got a PDF
            if result.success:
                # Save content if it's PDF
                content = result.raw_html
                if content and len(content) > 1000:
                    # Check for PDF header in content
                    if content[:4] == b'%PDF' or '%PDF' in content[:100]:
                        with open(output_path, 'wb') as f:
                            f.write(content.encode() if isinstance(content, str) else content)
                        return True
            
            return False
            
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


async def extract_pdf_links(url: str) -> List[str]:
    """Extract PDF links from a webpage using crawl4ai."""
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=url,
                bypass_cache=True,
                wait_for="networkidle",
                timeout=30000
            )
            
            if result.success:
                # Extract PDF links from HTML
                html = result.html
                pdf_links = []
                
                # Find all links that might be PDFs
                link_patterns = [
                    r'href="([^"]*\.pdf[^"]*)"',
                    r'href="([^"]*\/pdf[^"]*)"',
                    r'data-pdf-url="([^"]*)"',
                    r'href="([^"]*download[^"]*pdf[^"]*)"',
                ]
                
                for pattern in link_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    pdf_links.extend(matches)
                
                # Make URLs absolute
                from urllib.parse import urljoin
                absolute_links = []
                for link in pdf_links:
                    if link.startswith('http'):
                        absolute_links.append(link)
                    else:
                        absolute_links.append(urljoin(url, link))
                
                return list(set(absolute_links))  # Remove duplicates
            
            return []
            
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        return []


def get_papers_needing_pdfs(limit: int = 5) -> List[Dict]:
    """Get papers from pac collection that need PDFs."""
    library_dir = Path.home() / ".scitex" / "scholar" / "library"
    pac_dir = library_dir / "pac"
    master_dir = library_dir / "MASTER"
    
    if not pac_dir.exists():
        print(f"❌ Collection directory not found: {pac_dir}")
        return []
    
    papers = []
    count = 0
    
    print(f"📚 Scanning pac collection for papers without PDFs...")
    
    for item in sorted(pac_dir.iterdir()):
        if count >= limit:
            break
            
        if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
            target = item.readlink()
            if target.parts[0] == '..':
                unique_id = target.parts[-1]
                master_path = master_dir / unique_id
                
                if master_path.exists():
                    metadata_file = master_path / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            # Check if PDF already exists
                            pdf_files = list(master_path.glob("*.pdf"))
                            if len(pdf_files) == 0:  # No PDF yet
                                paper = {
                                    'human_name': item.name,
                                    'unique_id': unique_id,
                                    'master_path': master_path,
                                    'metadata': metadata,
                                }
                                papers.append(paper)
                                count += 1
                                print(f"  {count}. {item.name}")
                                
                        except Exception as e:
                            print(f"  ⚠️  Error reading {unique_id}: {e}")
                            continue
    
    print(f"✅ Found {len(papers)} papers needing PDFs")
    return papers


def get_paper_url(metadata: Dict) -> Optional[str]:
    """Get the best URL for downloading from paper metadata."""
    if 'doi' in metadata and metadata['doi']:
        doi = metadata['doi']
        if not doi.startswith('http'):
            return f"https://doi.org/{doi}"
        return doi
    
    url_fields = ['url', 'publisher_url', 'journal_url', 'source_url']
    for field in url_fields:
        if field in metadata and metadata[field]:
            return metadata[field]
    
    return None


def get_publisher_pdf_patterns(url: str, metadata: Dict) -> List[str]:
    """Get publisher-specific PDF URL patterns."""
    pdf_patterns = []
    journal = metadata.get('journal', '').lower()
    doi = metadata.get('doi', '')
    
    # MATEC Web of Conferences
    if 'matec' in journal and doi:
        # Extract from DOI: 10.1051/matecconf/201821003016
        match = re.search(r'10\.1051/matecconf/(\d{4})(\d+)(\d+)', doi)
        if match:
            year = match.group(1)
            volume = match.group(2)
            article = match.group(3)
            # Direct PDF pattern
            pdf_patterns.append(f"https://www.matec-conferences.org/articles/matecconf/pdf/{year}/{volume}/matecconf_*_{article}.pdf")
            # Alternative pattern
            pdf_patterns.append(f"https://doi.org/{doi}/pdf")
    
    # IEEE
    elif 'ieee' in journal and doi:
        # IEEE pattern
        match = re.search(r'10\.1109/([^/]+)', doi)
        if match:
            pdf_patterns.append(f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={match.group(1)}")
    
    # Frontiers
    elif 'frontiers' in journal:
        if url:
            pdf_patterns.append(f"{url}/pdf")
            pdf_patterns.append(f"{url}/full/pdf")
    
    # Nature/Scientific Reports
    elif ('nature' in journal or 'scientific reports' in journal) and doi:
        match = re.search(r'10\.1038/([^/]+)', doi)
        if match:
            pdf_patterns.append(f"https://www.nature.com/articles/{match.group(1)}.pdf")
    
    # PeerJ
    elif 'peerj' in journal and doi:
        match = re.search(r'peerj\.([^/]+)/(\d+)', doi)
        if match:
            pdf_patterns.append(f"https://peerj.com/articles/{match.group(2)}.pdf")
    
    # BMC/Springer
    elif 'bmc' in journal and doi:
        pdf_patterns.append(f"https://doi.org/{doi}/pdf")
    
    return pdf_patterns


def generate_filename(paper: Dict) -> str:
    """Generate filename for downloaded PDF."""
    metadata = paper['metadata']
    authors = metadata.get('authors', [])
    year = metadata.get('year', '')
    
    if authors and year:
        first_author = str(authors[0]) if authors else 'Unknown'
        # Clean author name
        if ',' in first_author:
            first_author = first_author.split(',')[0]
        elif ' ' in first_author:
            # Get last name from "First Last" format  
            parts = first_author.split()
            # Handle "First Middle Last" by taking the last part
            first_author = parts[-1]
        
        # Clean for filename
        first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
        return f"{first_author}-{year}.pdf"
    else:
        return f"{paper['human_name']}.pdf"


def update_metadata(paper: Dict, filename: str, download_url: str):
    """Update paper metadata with download information."""
    try:
        metadata_file = paper['master_path'] / "metadata.json"
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        metadata['pdf_downloaded'] = True
        metadata['pdf_filename'] = filename
        metadata['pdf_download_url'] = download_url
        metadata['pdf_download_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✅ Updated metadata")
        
    except Exception as e:
        print(f"  ⚠️  Failed to update metadata: {e}")


async def download_paper_pdf(paper: Dict) -> bool:
    """Download PDF for a single paper."""
    print(f"\n{'='*80}")
    print(f"📄 Processing: {paper['human_name']}")
    print(f"{'='*80}")
    
    metadata = paper['metadata']
    print(f"  📝 Title: {metadata.get('title', 'N/A')[:70]}...")
    print(f"  📅 Year: {metadata.get('year', 'N/A')}")
    print(f"  🏢 Journal: {metadata.get('journal', 'N/A')}")
    
    # Get URL
    url = get_paper_url(metadata)
    if not url:
        print("  ❌ No suitable URL found in metadata")
        return False
    
    print(f"  🌐 URL: {url}")
    
    # Generate output path
    filename = generate_filename(paper)
    output_path = paper['master_path'] / filename
    
    print(f"  💾 Target: {filename}")
    
    # Strategy 1: Try publisher-specific patterns
    print(f"\n  🎯 Strategy 1: Publisher-specific patterns")
    pdf_patterns = get_publisher_pdf_patterns(url, metadata)
    
    if pdf_patterns:
        for pattern_url in pdf_patterns:
            print(f"    Testing: {pattern_url}")
            
            if await download_pdf_with_crawl4ai(pattern_url, output_path):
                # Verify it's a PDF
                if output_path.exists():
                    with open(output_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            file_size = output_path.stat().st_size
                            print(f"    ✅ Downloaded PDF: {file_size / 1024 / 1024:.1f} MB")
                            update_metadata(paper, filename, pattern_url)
                            return True
                        else:
                            print(f"    ❌ Not a valid PDF")
                            output_path.unlink()
    
    # Strategy 2: Extract PDF links from page
    print(f"\n  🕷️  Strategy 2: Extract PDF links from page")
    pdf_links = await extract_pdf_links(url)
    
    if pdf_links:
        print(f"    ✅ Found {len(pdf_links)} PDF candidates")
        
        for pdf_url in pdf_links[:3]:  # Try first 3
            print(f"    Testing: {pdf_url}")
            
            if await download_pdf_with_crawl4ai(pdf_url, output_path):
                # Verify it's a PDF
                if output_path.exists():
                    with open(output_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            file_size = output_path.stat().st_size
                            print(f"    ✅ Downloaded PDF: {file_size / 1024 / 1024:.1f} MB")
                            update_metadata(paper, filename, pdf_url)
                            return True
                        else:
                            output_path.unlink()
    else:
        print(f"    ❌ No PDF links found")
    
    print(f"  ❌ All strategies failed")
    return False


async def main():
    """Main function to download PDFs."""
    print("🚀 Simple Crawl4AI PDF Downloader")
    print("=" * 60)
    
    # Get papers needing PDFs
    papers = get_papers_needing_pdfs(limit=3)
    
    if not papers:
        print("✅ No papers need PDFs!")
        return
    
    print(f"\n📋 Will attempt to download {len(papers)} PDFs")
    
    # Download PDFs
    successful = 0
    
    for paper in papers:
        try:
            success = await download_paper_pdf(paper)
            
            if success:
                successful += 1
                print(f"\n✅ SUCCESS: {paper['human_name']}")
            else:
                print(f"\n❌ FAILED: {paper['human_name']}")
            
            # Wait between downloads
            if paper != papers[-1]:
                print(f"\n⏳ Waiting 3 seconds...")
                await asyncio.sleep(3)
            
        except Exception as e:
            print(f"\n💥 Error processing {paper['human_name']}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 Download Session Complete!")
    print(f"✅ Successful downloads: {successful}/{len(papers)}")
    
    if successful > 0:
        print(f"🎉 Downloaded {successful} PDFs successfully!")
    else:
        print(f"🤔 No PDFs downloaded - may need authentication")


if __name__ == "__main__":
    asyncio.run(main())