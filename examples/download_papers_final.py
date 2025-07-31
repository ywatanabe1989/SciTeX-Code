#!/usr/bin/env python3
"""Final comprehensive paper downloader combining multiple strategies."""

import os
import re
import time
import asyncio
import requests
from pathlib import Path
from typing import List, Dict, Optional

# Try different download methods
HAVE_CRAWL4AI = False
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    HAVE_CRAWL4AI = True
    print("✓ Crawl4AI is available")
except ImportError:
    print("✗ Crawl4AI not available, using fallback methods")

def parse_bib_simple(bib_file: str) -> List[Dict]:
    """Simple BibTeX parser to extract paper info."""
    papers = []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by @article entries
    entries = re.split(r'@\w+{', content)[1:]  # Skip empty first element
    
    for entry in entries:
        # Extract ID
        id_match = re.match(r'([^,]+),', entry)
        if not id_match:
            continue
            
        paper = {'id': id_match.group(1)}
        
        # Extract fields
        for field in ['title', 'author', 'journal', 'year', 'url', 'doi', 'volume', 'pages']:
            pattern = rf'{field}\s*=\s*{{([^}}]+)}}'
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                paper[field] = match.group(1).strip()
        
        # Try to extract DOI from URL if not explicitly provided
        if 'url' in paper and 'doi' not in paper:
            url = paper['url']
            # Pattern 1: https://doi.org/...
            doi_match = re.search(r'https?://doi\.org/(.+)$', url)
            if doi_match:
                paper['doi'] = doi_match.group(1)
            # Pattern 2: DOI in URL
            else:
                doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
                if doi_match:
                    paper['doi'] = doi_match.group(1)
        
        papers.append(paper)
    
    return papers

def download_with_requests(paper: Dict, output_dir: Path) -> Optional[str]:
    """Try downloading with direct HTTP requests."""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        return str(output_path)
    
    urls_to_try = []
    
    # Build URL list based on DOI patterns
    if 'doi' in paper:
        doi = paper['doi']
        
        # Open access publishers
        if doi.startswith('10.3389/'):  # Frontiers
            urls_to_try.append(f"https://www.frontiersin.org/articles/{doi}/pdf")
        elif doi.startswith('10.1371/'):  # PLOS
            urls_to_try.append(f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable")
        elif doi.startswith('10.1186/'):  # BMC
            urls_to_try.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
        elif doi.startswith('10.7554/'):  # eLife
            urls_to_try.append(f"https://elifesciences.org/download/aHR0cHM6Ly9jZG4uZWxpZmVzY2llbmNlcy5vcmcvYXJ0aWNsZXMv{doi.split('/')[-1]}/elife-{doi.split('/')[-1]}-v1.pdf")
        
        # PubMed Central
        pmcid_patterns = [
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/doi/{doi}/pdf/",
            f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={doi}&blobtype=pdf"
        ]
        urls_to_try.extend(pmcid_patterns)
        
        # Generic DOI
        urls_to_try.append(f"https://doi.org/{doi}")
    
    # Try institutional resolver
    if 'doi' in paper:
        openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{paper['doi']}&svc_id=fulltext"
        urls_to_try.append(openurl)
    
    for url in urls_to_try:
        try:
            print(f"    Trying: {url[:60]}...")
            response = session.get(url, timeout=30, allow_redirects=True)
            
            if response.status_code == 200 and (
                'pdf' in response.headers.get('content-type', '').lower() or 
                response.content.startswith(b'%PDF')
            ):
                output_path.write_bytes(response.content)
                return str(output_path)
                
        except Exception as e:
            print(f"    Failed: {str(e)[:50]}")
        
        time.sleep(0.5)
    
    return None

async def download_with_crawl4ai(paper: Dict, output_dir: Path) -> Optional[str]:
    """Try downloading with Crawl4AI for JavaScript-heavy sites."""
    
    if not HAVE_CRAWL4AI or 'doi' not in paper:
        return None
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        return str(output_path)
    
    # Configure browser
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        verbose=False
    )
    
    # Try institutional access
    url = f"https://doi.org/{paper['doi']}"
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    wait_until="networkidle",
                    delay_before_return_html=2.0,
                    js_code="""
                    // Look for PDF links
                    const links = document.querySelectorAll('a');
                    for (const link of links) {
                        const href = link.href || '';
                        const text = link.textContent.toLowerCase();
                        if (href.endsWith('.pdf') || 
                            (text.includes('pdf') && text.includes('download'))) {
                            return href;
                        }
                    }
                    return null;
                    """
                )
            )
            
            # Check if we found a PDF URL via JavaScript
            if hasattr(result, 'js_result') and result.js_result:
                pdf_url = result.js_result
                print(f"    Found PDF URL: {pdf_url}")
                
                # Download the PDF
                pdf_response = requests.get(pdf_url, timeout=30)
                if pdf_response.content.startswith(b'%PDF'):
                    output_path.write_bytes(pdf_response.content)
                    return str(output_path)
                    
    except Exception as e:
        print(f"    Crawl4AI error: {str(e)[:50]}")
    
    return None

async def download_paper(paper: Dict, output_dir: Path) -> Dict:
    """Try multiple methods to download a paper."""
    
    print(f"\n📄 {paper.get('title', paper['id'])[:60]}...")
    print(f"   ID: {paper['id']}")
    if 'doi' in paper:
        print(f"   DOI: {paper['doi']}")
    
    # Method 1: Direct HTTP requests
    print("   Method 1: Direct download...")
    pdf_path = download_with_requests(paper, output_dir)
    
    # Method 2: Crawl4AI for complex sites
    if not pdf_path and HAVE_CRAWL4AI:
        print("   Method 2: Crawl4AI browser automation...")
        pdf_path = await download_with_crawl4ai(paper, output_dir)
    
    if pdf_path:
        print(f"   ✅ Success: {pdf_path}")
        return {'id': paper['id'], 'success': True, 'path': pdf_path}
    else:
        print(f"   ❌ Failed to download")
        return {'id': paper['id'], 'success': False}

async def main():
    """Main download function."""
    
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("📚 Scientific Paper Downloader")
    print("="*60)
    
    # Parse BibTeX
    print(f"\nParsing: {bib_file}")
    papers = parse_bib_simple(bib_file)
    print(f"Found {len(papers)} papers")
    
    # Download papers
    print(f"\nStarting downloads to: {output_dir.absolute()}")
    print("="*60)
    
    results = []
    
    # Process in batches to avoid overwhelming
    batch_size = 5
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        batch_results = await asyncio.gather(
            *[download_paper(paper, output_dir) for paper in batch]
        )
        results.extend(batch_results)
        
        # Progress report
        success_count = sum(1 for r in results if r['success'])
        print(f"\n--- Progress: {success_count}/{len(results)} downloaded ---")
        
        if i + batch_size < len(papers):
            await asyncio.sleep(2)  # Be polite between batches
    
    # Final summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\nTotal papers: {len(papers)}")
    print(f"Downloaded: {success_count}")
    print(f"Failed: {len(papers) - success_count}")
    print(f"Success rate: {success_count/len(papers)*100:.1f}%")
    
    # Save summary
    summary_file = output_dir / "download_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Download Summary - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total: {success_count}/{len(papers)} papers downloaded\n\n")
        
        f.write("SUCCESSFUL:\n")
        for r in results:
            if r['success']:
                f.write(f"✅ {r['id']}\n")
        
        f.write("\nFAILED:\n")
        for r in results:
            if not r['success']:
                f.write(f"❌ {r['id']}\n")
    
    print(f"\nSummary saved to: {summary_file}")

if __name__ == "__main__":
    asyncio.run(main())