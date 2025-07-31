#!/usr/bin/env python3
"""Download papers using existing OpenAthens session cookies."""

import json
import re
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

# Try to import Crawl4AI for advanced downloading
HAVE_CRAWL4AI = False
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    HAVE_CRAWL4AI = True
    print("✓ Crawl4AI available for advanced downloads")
except ImportError:
    print("✗ Crawl4AI not available, using requests only")

def load_openathens_session():
    """Load OpenAthens session cookies from saved file."""
    session_file = Path.home() / ".scitex" / "scholar" / "openathens_session.json"
    
    if not session_file.exists():
        print("❌ No OpenAthens session found")
        return None
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    print("✓ Loaded OpenAthens session")
    return session_data

def create_authenticated_session(session_data):
    """Create a requests session with OpenAthens cookies."""
    session = requests.Session()
    
    # Set user agent
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    # Add OpenAthens cookies
    if 'cookies' in session_data:
        for name, value in session_data['cookies'].items():
            session.cookies.set(name, value, domain='.openathens.net')
            # Also set for common academic domains
            if name in ['oa-session', 'oa-xsrf-token']:
                session.cookies.set(name, value, domain='.sciencedirect.com')
                session.cookies.set(name, value, domain='.nature.com')
                session.cookies.set(name, value, domain='.springer.com')
    
    return session

def parse_bib_simple(bib_file: str) -> List[Dict]:
    """Simple BibTeX parser."""
    papers = []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = re.split(r'@\w+{', content)[1:]
    
    for entry in entries[:10]:  # Process first 10 for testing
        id_match = re.match(r'([^,]+),', entry)
        if not id_match:
            continue
            
        paper = {'id': id_match.group(1)}
        
        # Extract fields
        for field in ['title', 'author', 'journal', 'year', 'url', 'doi']:
            pattern = rf'{field}\s*=\s*{{([^}}]+)}}'
            match = re.search(pattern, entry, re.IGNORECASE)
            if match:
                paper[field] = match.group(1).strip()
        
        # Extract DOI from URL if not explicit
        if 'url' in paper and 'doi' not in paper:
            url = paper['url']
            doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
            if doi_match:
                paper['doi'] = doi_match.group(1)
        
        papers.append(paper)
    
    return papers

def download_with_openathens(paper: Dict, output_dir: Path, session: requests.Session) -> Optional[str]:
    """Download paper using OpenAthens authenticated session."""
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        print(f"    ✓ Already exists: {output_path}")
        return str(output_path)
    
    urls_to_try = []
    
    if 'doi' in paper:
        doi = paper['doi']
        
        # Priority 1: OpenURL resolver with OpenAthens
        openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
        urls_to_try.append(("OpenURL", openurl))
        
        # Priority 2: Direct publisher links that might recognize OpenAthens
        if doi.startswith('10.1016/'):  # Elsevier
            pii = doi.split('/')[-1]
            urls_to_try.append(("Elsevier", f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft?md5=&pid="))
        elif doi.startswith('10.1038/'):  # Nature
            urls_to_try.append(("Nature", f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf"))
        elif doi.startswith('10.1007/'):  # Springer
            urls_to_try.append(("Springer", f"https://link.springer.com/content/pdf/{doi}.pdf"))
        
        # Priority 3: DOI.org (might redirect to authenticated version)
        urls_to_try.append(("DOI", f"https://doi.org/{doi}"))
        
        # Priority 4: Open access alternatives
        if doi.startswith('10.3389/'):  # Frontiers
            urls_to_try.append(("Frontiers", f"https://www.frontiersin.org/articles/{doi}/pdf"))
        
        # Priority 5: PubMed Central
        urls_to_try.append(("PMC", f"https://www.ncbi.nlm.nih.gov/pmc/articles/doi/{doi}/pdf/"))
    
    for source, url in urls_to_try:
        try:
            print(f"    Trying {source}: {url[:60]}...")
            
            # Add referer header for some publishers
            headers = {'Referer': 'https://login.openathens.net/'}
            
            response = session.get(url, timeout=30, allow_redirects=True, headers=headers)
            
            # Check if we got a PDF
            content_type = response.headers.get('content-type', '').lower()
            is_pdf = 'pdf' in content_type or response.content[:4] == b'%PDF'
            
            if response.status_code == 200 and is_pdf:
                # Save the PDF
                output_path.write_bytes(response.content)
                print(f"    ✅ Downloaded via {source}: {output_path}")
                return str(output_path)
            else:
                print(f"    Not a PDF (status: {response.status_code})")
                
        except Exception as e:
            print(f"    Error: {str(e)[:50]}")
        
        time.sleep(0.5)  # Be polite
    
    return None

async def download_with_crawl4ai_auth(paper: Dict, output_dir: Path, cookies: Dict) -> Optional[str]:
    """Use Crawl4AI with OpenAthens cookies for complex sites."""
    
    if not HAVE_CRAWL4AI or 'doi' not in paper:
        return None
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        return str(output_path)
    
    # Configure browser with cookies
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        # Set cookies
        cookies=[
            {
                "name": name,
                "value": value,
                "domain": ".openathens.net",
                "path": "/"
            }
            for name, value in cookies.items()
            if name in ['oa-session', 'oa-xsrf-token', 'oatmpsid']
        ]
    )
    
    url = f"https://doi.org/{paper['doi']}"
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    wait_until="networkidle",
                    delay_before_return_html=3.0,
                    js_code="""
                    // Look for PDF download links
                    const links = Array.from(document.querySelectorAll('a'));
                    const pdfLink = links.find(link => {
                        const href = link.href || '';
                        const text = link.textContent.toLowerCase();
                        return href.endsWith('.pdf') || 
                               (text.includes('pdf') && (text.includes('download') || text.includes('full text')));
                    });
                    return pdfLink ? pdfLink.href : null;
                    """
                )
            )
            
            if hasattr(result, 'js_result') and result.js_result:
                print(f"    Found PDF link via browser: {result.js_result}")
                # Download the PDF
                pdf_response = requests.get(result.js_result, timeout=30)
                if pdf_response.content.startswith(b'%PDF'):
                    output_path.write_bytes(pdf_response.content)
                    return str(output_path)
                    
    except Exception as e:
        print(f"    Crawl4AI error: {str(e)[:50]}")
    
    return None

async def main():
    """Main download function using OpenAthens authentication."""
    
    # Load OpenAthens session
    session_data = load_openathens_session()
    if not session_data:
        print("Please login to OpenAthens first using the Scholar module")
        return
    
    # Create authenticated session
    auth_session = create_authenticated_session(session_data)
    
    # Parse BibTeX file
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("\n📚 Paper Downloader with OpenAthens Authentication")
    print("="*60)
    
    papers = parse_bib_simple(bib_file)
    print(f"Processing first {len(papers)} papers from BibTeX file")
    
    results = []
    
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}/{len(papers)}] {paper.get('title', paper['id'])[:60]}...")
        print(f"   ID: {paper['id']}")
        if 'doi' in paper:
            print(f"   DOI: {paper['doi']}")
        
        # Try authenticated download
        pdf_path = download_with_openathens(paper, output_dir, auth_session)
        
        # If failed, try browser automation with auth
        if not pdf_path and HAVE_CRAWL4AI:
            print("   Trying browser automation with auth...")
            pdf_path = await download_with_crawl4ai_auth(
                paper, output_dir, session_data.get('cookies', {})
            )
        
        if pdf_path:
            results.append({'id': paper['id'], 'success': True, 'path': pdf_path})
        else:
            results.append({'id': paper['id'], 'success': False})
            print("   ❌ Failed to download")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\nTotal: {success_count}/{len(papers)} downloaded")
    print(f"Success rate: {success_count/len(papers)*100:.1f}%")
    
    # List successful downloads
    print("\n✅ Successful downloads:")
    for r in results:
        if r['success']:
            print(f"   {r['id']}")
    
    # Save summary
    summary_file = output_dir / "openathens_download_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"OpenAthens Download Summary - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total: {success_count}/{len(papers)} papers downloaded\n\n")
        
        f.write("SUCCESSFUL:\n")
        for r in results:
            if r['success']:
                f.write(f"✅ {r['id']} -> {r['path']}\n")
        
        f.write("\nFAILED:\n")
        for r in results:
            if not r['success']:
                f.write(f"❌ {r['id']}\n")
    
    print(f"\nSummary saved to: {summary_file}")

if __name__ == "__main__":
    asyncio.run(main())