#!/usr/bin/env python3
"""
Complete paper downloader using MCP tools with OpenAthens authentication.
This script demonstrates how to use MCP Puppeteer and c4ai-sse for downloading academic papers.
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import asyncio

def load_openathens_session() -> Optional[Dict]:
    """Load OpenAthens session cookies."""
    session_file = Path.home() / ".scitex" / "scholar" / "openathens_session.json"
    
    if not session_file.exists():
        print("❌ No OpenAthens session found")
        return None
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    print("✅ Loaded OpenAthens session")
    return session_data

def parse_bibtex(bib_file: str, limit: Optional[int] = None) -> List[Dict]:
    """Parse BibTeX file to extract paper information."""
    papers = []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by @ entries
    entries = re.split(r'@\w+{', content)[1:]
    
    if limit:
        entries = entries[:limit]
    
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
            if 'doi.org/' in url:
                doi_match = re.search(r'doi\.org/(.+)$', url)
                if doi_match:
                    paper['doi'] = doi_match.group(1)
            # Pattern 2: DOI in URL parameters
            else:
                doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
                if doi_match:
                    paper['doi'] = doi_match.group(1)
        
        papers.append(paper)
    
    return papers

def build_download_urls(paper: Dict) -> List[Tuple[str, str]]:
    """Build prioritized list of URLs to try for downloading."""
    urls = []
    
    if 'doi' in paper:
        doi = paper['doi']
        
        # Priority 1: University of Melbourne OpenURL resolver
        openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
        urls.append(("OpenURL", openurl))
        
        # Priority 2: Publisher-specific patterns
        if doi.startswith('10.1016/'):  # Elsevier
            pii = doi.split('/')[-1]
            urls.append(("Elsevier", f"https://www.sciencedirect.com/science/article/pii/{pii}"))
        elif doi.startswith('10.1038/'):  # Nature
            urls.append(("Nature", f"https://www.nature.com/articles/{doi.split('/')[-1]}"))
        elif doi.startswith('10.1007/'):  # Springer
            urls.append(("Springer", f"https://link.springer.com/article/{doi}"))
        elif doi.startswith('10.3389/'):  # Frontiers (Open Access)
            urls.append(("Frontiers", f"https://www.frontiersin.org/articles/{doi}/full"))
        elif doi.startswith('10.1371/'):  # PLOS (Open Access)
            urls.append(("PLOS", f"https://journals.plos.org/plosone/article?id={doi}"))
        
        # Priority 3: Generic DOI
        urls.append(("DOI", f"https://doi.org/{doi}"))
    
    # Priority 4: Direct URL if provided
    if 'url' in paper:
        urls.append(("Direct", paper['url']))
    
    return urls

async def download_paper_with_mcp(paper: Dict, output_dir: Path, session_data: Dict) -> Dict:
    """
    Download a paper using MCP tools.
    
    This function demonstrates the MCP commands that would be used.
    In actual implementation, these would be called via the MCP client.
    """
    
    print(f"\n📄 Processing: {paper.get('title', paper['id'])[:60]}...")
    print(f"   ID: {paper['id']}")
    if 'doi' in paper:
        print(f"   DOI: {paper['doi']}")
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    # Check if already exists
    if output_path.exists():
        print(f"   ✅ Already exists: {output_path}")
        return {'id': paper['id'], 'success': True, 'path': str(output_path)}
    
    # Get URLs to try
    urls = build_download_urls(paper)
    
    # MCP commands to execute
    mcp_sequence = []
    
    for source, url in urls[:3]:  # Try first 3 URLs
        print(f"   Trying {source}: {url[:60]}...")
        
        # Command 1: Navigate to URL
        mcp_sequence.append({
            "tool": "mcp__puppeteer__puppeteer_navigate",
            "args": {
                "url": url,
                "allowDangerous": False
            },
            "description": f"Navigate to {source}"
        })
        
        # Command 2: Wait for page to load
        mcp_sequence.append({
            "tool": "mcp__puppeteer__puppeteer_evaluate",
            "args": {
                "script": "new Promise(resolve => setTimeout(resolve, 2000))"
            },
            "description": "Wait 2 seconds for page load"
        })
        
        # Command 3: Inject OpenAthens cookies if needed
        if source in ["OpenURL", "Elsevier", "Nature", "Springer"]:
            cookie_script = f"""
            // Inject OpenAthens cookies
            const cookies = {json.dumps(session_data.get('cookies', {}))};
            Object.entries(cookies).forEach(([name, value]) => {{
                document.cookie = `${{name}}=${{value}}; path=/; secure`;
            }});
            """
            mcp_sequence.append({
                "tool": "mcp__puppeteer__puppeteer_evaluate",
                "args": {"script": cookie_script},
                "description": "Inject OpenAthens cookies"
            })
        
        # Command 4: Find PDF download link/button
        find_pdf_script = """
        (() => {
            // Check for direct PDF embed
            const embed = document.querySelector('embed[type="application/pdf"]');
            if (embed) return {type: 'embed', url: embed.src};
            
            const iframe = document.querySelector('iframe[src*=".pdf"]');
            if (iframe) return {type: 'iframe', url: iframe.src};
            
            // Look for download links
            const links = Array.from(document.querySelectorAll('a'));
            
            // Priority 1: Links with PDF text
            const pdfLink = links.find(link => {
                const text = (link.textContent || '').toLowerCase();
                const href = link.href || '';
                return (text.includes('pdf') && (text.includes('download') || text.includes('full text'))) ||
                       text === 'pdf' ||
                       href.endsWith('.pdf');
            });
            
            if (pdfLink) return {type: 'link', url: pdfLink.href, selector: null};
            
            // Priority 2: Download buttons
            const downloadBtn = document.querySelector(
                'button:has-text("Download PDF"), ' +
                'a.download-pdf, ' +
                'button.pdf-download, ' +
                '[aria-label*="Download PDF"]'
            );
            
            if (downloadBtn) {
                // Get selector for clicking
                const id = downloadBtn.id ? `#${downloadBtn.id}` : null;
                const classes = downloadBtn.className ? `.${downloadBtn.className.split(' ').join('.')}` : null;
                return {type: 'button', selector: id || classes || 'button'};
            }
            
            return null;
        })()
        """
        
        mcp_sequence.append({
            "tool": "mcp__puppeteer__puppeteer_evaluate",
            "args": {"script": find_pdf_script},
            "description": "Find PDF download element"
        })
        
        # Command 5: Alternative - Use c4ai-sse to generate PDF
        mcp_sequence.append({
            "tool": "mcp__c4ai-sse__pdf",
            "args": {
                "url": url,
                "output_path": str(output_path)
            },
            "description": f"Generate PDF using c4ai-sse"
        })
        
        # Command 6: Take screenshot for debugging
        mcp_sequence.append({
            "tool": "mcp__puppeteer__puppeteer_screenshot",
            "args": {
                "name": f"debug_{paper['id']}_{source}",
                "width": 1920,
                "height": 1080
            },
            "description": "Capture debug screenshot"
        })
    
    # Print MCP command sequence
    print("\n   📋 MCP Command Sequence:")
    for i, cmd in enumerate(mcp_sequence, 1):
        print(f"      {i}. {cmd['tool']} - {cmd['description']}")
    
    print("\n   ℹ️  Note: In production, these commands would be executed via MCP client")
    print("   💡 The script would:")
    print("      1. Navigate to each URL with authentication")
    print("      2. Find and click PDF download links")
    print("      3. Or use c4ai-sse to generate PDFs")
    print("      4. Save downloaded PDFs to output directory")
    
    # Simulate result (in production, this would be based on actual MCP execution)
    return {'id': paper['id'], 'success': False, 'error': 'MCP execution not implemented'}

async def main():
    """Main function to orchestrate paper downloads."""
    
    # Configuration
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Load OpenAthens session
    session_data = load_openathens_session()
    if not session_data:
        print("⚠️  No OpenAthens session found. Some papers may not be accessible.")
        session_data = {'cookies': {}}
    
    print("\n📚 MCP-Based Paper Downloader")
    print("="*60)
    
    # Parse BibTeX file
    print(f"Parsing BibTeX file: {bib_file}")
    papers = parse_bibtex(bib_file, limit=5)  # Start with 5 papers for testing
    print(f"Found {len(papers)} papers to process")
    
    # Download papers
    results = []
    for paper in papers:
        result = await download_paper_with_mcp(paper, output_dir, session_data)
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 DOWNLOAD SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r.get('success', False))
    print(f"\nTotal papers: {len(papers)}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed: {len(papers) - success_count}")
    print(f"Success rate: {success_count/len(papers)*100:.1f}%")
    
    # Implementation notes
    print("\n" + "="*60)
    print("💡 IMPLEMENTATION NOTES")
    print("="*60)
    print("\nTo actually execute this script with MCP:")
    print("1. Use Claude's built-in MCP tools (as shown in command sequence)")
    print("2. Or implement an MCP client to communicate with MCP servers")
    print("3. The key MCP servers for this task are:")
    print("   - mcp__puppeteer: Browser automation and navigation")
    print("   - mcp__c4ai-sse: Advanced web scraping and PDF generation")
    print("   - mcp__filesystem: File operations for saving PDFs")
    print("\nThe script demonstrates the complete workflow and MCP commands needed.")

if __name__ == "__main__":
    asyncio.run(main())