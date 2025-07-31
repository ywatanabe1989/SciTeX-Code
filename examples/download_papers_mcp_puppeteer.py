#!/usr/bin/env python3
"""Download papers using MCP Puppeteer with OpenAthens authentication."""

import json
import re
import time
import base64
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

# Note: This example shows how to use Puppeteer via MCP
# In practice, you would use the MCP client to communicate with the Puppeteer server

def load_openathens_session():
    """Load OpenAthens session data."""
    session_file = Path.home() / ".scitex" / "scholar" / "openathens_session.json"
    
    if not session_file.exists():
        print("❌ No OpenAthens session found")
        return None
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    print("✓ Loaded OpenAthens session")
    return session_data

def parse_bib_simple(bib_file: str, limit: int = 5) -> List[Dict]:
    """Simple BibTeX parser."""
    papers = []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = re.split(r'@\w+{', content)[1:]
    
    for entry in entries[:limit]:
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
        
        # Extract DOI from URL
        if 'url' in paper and 'doi' not in paper:
            url = paper['url']
            # Check for DOI patterns
            if 'doi.org/' in url:
                doi_match = re.search(r'doi\.org/(.+)$', url)
                if doi_match:
                    paper['doi'] = doi_match.group(1)
            else:
                doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
                if doi_match:
                    paper['doi'] = doi_match.group(1)
        
        papers.append(paper)
    
    return papers

async def download_paper_with_mcp(paper: Dict, output_dir: Path, cookies: Dict):
    """
    Download a paper using MCP Puppeteer.
    
    This is a conceptual example showing how you would use MCP Puppeteer.
    In practice, you would need to:
    1. Have the MCP Puppeteer server running
    2. Use an MCP client library to communicate with it
    """
    
    print(f"\n📄 {paper.get('title', paper['id'])[:60]}...")
    print(f"   ID: {paper['id']}")
    if 'doi' in paper:
        print(f"   DOI: {paper['doi']}")
    
    filename = f"{paper['id']}.pdf"
    output_path = output_dir / filename
    
    if output_path.exists():
        print(f"   ✓ Already exists: {output_path}")
        return {'id': paper['id'], 'success': True, 'path': str(output_path)}
    
    # Example of MCP commands you would send:
    mcp_commands = []
    
    # 1. Navigate to OpenURL resolver
    if 'doi' in paper:
        openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/{paper['doi']}&svc_id=fulltext"
        
        mcp_commands.append({
            "tool": "puppeteer_navigate",
            "arguments": {
                "url": openurl,
                "launchOptions": {
                    "headless": False,  # Set to True for production
                    "args": ["--no-sandbox", "--disable-setuid-sandbox"]
                }
            }
        })
        
        # 2. Inject cookies via JavaScript
        cookie_js = f"""
        // Set OpenAthens cookies
        const cookies = {json.dumps([
            {'name': name, 'value': value, 'domain': '.openathens.net', 'path': '/'}
            for name, value in cookies.items()
        ])};
        
        for (const cookie of cookies) {{
            document.cookie = `${{cookie.name}}=${{cookie.value}}; domain=${{cookie.domain}}; path=${{cookie.path}}; secure`;
        }}
        """
        
        mcp_commands.append({
            "tool": "puppeteer_evaluate",
            "arguments": {
                "script": cookie_js
            }
        })
        
        # 3. Look for PDF download link
        find_pdf_js = """
        // Find PDF download link
        const links = Array.from(document.querySelectorAll('a'));
        const pdfLink = links.find(link => {
            const text = link.textContent.toLowerCase();
            const href = link.href || '';
            return (text.includes('pdf') && text.includes('download')) ||
                   text === 'pdf' ||
                   text.includes('full text pdf') ||
                   href.endsWith('.pdf');
        });
        
        if (pdfLink) {
            return pdfLink.href;
        }
        
        // Check for embedded PDF
        const embed = document.querySelector('embed[type="application/pdf"]');
        if (embed) return embed.src;
        
        const iframe = document.querySelector('iframe[src*=".pdf"]');
        if (iframe) return iframe.src;
        
        return null;
        """
        
        mcp_commands.append({
            "tool": "puppeteer_evaluate", 
            "arguments": {
                "script": find_pdf_js
            }
        })
        
        # 4. If PDF link found, navigate to it
        # 5. Download the PDF content
        # 6. Save to file
        
        # Alternative: Try clicking download button
        mcp_commands.append({
            "tool": "puppeteer_click",
            "arguments": {
                "selector": "button:has-text('Download PDF'), a:has-text('Download PDF')"
            }
        })
        
        # Take screenshot for debugging
        mcp_commands.append({
            "tool": "puppeteer_screenshot",
            "arguments": {
                "name": f"debug_{paper['id']}",
                "encoded": True
            }
        })
    
    print("   📋 MCP Commands prepared:")
    for i, cmd in enumerate(mcp_commands, 1):
        print(f"      {i}. {cmd['tool']}")
    
    print("\n   ℹ️  To actually execute these commands, you would need:")
    print("      1. MCP Puppeteer server running")
    print("      2. MCP client to send commands")
    print("      3. Logic to handle responses and save PDFs")
    
    # Simulate result
    return {'id': paper['id'], 'success': False, 'error': 'MCP client not implemented'}

async def main():
    """Main function."""
    
    # Load OpenAthens session
    session_data = load_openathens_session()
    if not session_data:
        print("Please login to OpenAthens first")
        return
    
    # Parse BibTeX
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    papers = parse_bib_simple(bib_file, limit=3)
    
    # Setup output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("\n📚 Paper Downloader with MCP Puppeteer + OpenAthens")
    print("="*60)
    print(f"Processing {len(papers)} papers")
    
    # Process papers
    results = []
    for paper in papers:
        result = await download_paper_with_mcp(
            paper, 
            output_dir, 
            session_data.get('cookies', {})
        )
        results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r.get('success', False))
    print(f"\nTotal: {success_count}/{len(papers)} downloaded")
    
    print("\n💡 Next Steps:")
    print("1. Install MCP Puppeteer server:")
    print("   npm install -g @modelcontextprotocol/server-puppeteer")
    print("\n2. Configure MCP in your Claude Desktop app")
    print("\n3. Use an MCP client library to send commands")
    print("\n4. Or use the standalone Puppeteer script: download_papers_with_puppeteer.py")

if __name__ == "__main__":
    asyncio.run(main())