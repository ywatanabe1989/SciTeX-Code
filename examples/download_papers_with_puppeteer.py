#!/usr/bin/env python3
"""Download papers using Puppeteer with OpenAthens authentication."""

import json
import re
import time
import requests
import base64
from pathlib import Path
from typing import List, Dict, Optional
import subprocess

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
            doi_match = re.search(r'doi[:/=]([0-9.]+/[^&\s]+)', url)
            if doi_match:
                paper['doi'] = doi_match.group(1)
        
        papers.append(paper)
    
    return papers

def create_puppeteer_script(cookies: Dict, papers: List[Dict], output_dir: Path) -> str:
    """Create a Puppeteer script for downloading papers."""
    
    # Convert cookies to Puppeteer format
    puppeteer_cookies = []
    for name, value in cookies.items():
        # Add cookies for multiple domains
        for domain in ['.openathens.net', '.sciencedirect.com', '.nature.com', '.springer.com']:
            puppeteer_cookies.append({
                'name': name,
                'value': value,
                'domain': domain,
                'path': '/',
                'httpOnly': True,
                'secure': True
            })
    
    script = f"""
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = '{output_dir.absolute()}';
const COOKIES = {json.dumps(puppeteer_cookies)};

const papers = {json.dumps(papers)};

async function downloadPaper(browser, paper) {{
    const page = await browser.newPage();
    
    try {{
        // Set cookies
        await page.setCookie(...COOKIES);
        
        // Configure download behavior
        const client = await page.target().createCDPSession();
        await client.send('Page.setDownloadBehavior', {{
            behavior: 'allow',
            downloadPath: OUTPUT_DIR
        }});
        
        console.log(`\\nProcessing: ${{paper.title?.substring(0, 60) || paper.id}}...`);
        
        const urls = [];
        
        if (paper.doi) {{
            // Try OpenURL resolver first
            urls.push({{
                name: 'OpenURL',
                url: `https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?url_ver=Z39.88-2004&rft_id=info:doi/${{paper.doi}}&svc_id=fulltext`
            }});
            
            // Publisher-specific URLs
            if (paper.doi.startsWith('10.1016/')) {{
                const pii = paper.doi.split('/')[1];
                urls.push({{
                    name: 'Elsevier',
                    url: `https://www.sciencedirect.com/science/article/pii/${{pii}}`
                }});
            }} else if (paper.doi.startsWith('10.1038/')) {{
                urls.push({{
                    name: 'Nature',
                    url: `https://www.nature.com/articles/${{paper.doi.split('/')[1]}}`
                }});
            }} else if (paper.doi.startsWith('10.1007/')) {{
                urls.push({{
                    name: 'Springer',
                    url: `https://link.springer.com/article/${{paper.doi}}`
                }});
            }}
            
            // Generic DOI
            urls.push({{
                name: 'DOI',
                url: `https://doi.org/${{paper.doi}}`
            }});
        }}
        
        for (const {{name, url}} of urls) {{
            console.log(`  Trying ${{name}}: ${{url.substring(0, 60)}}...`);
            
            try {{
                await page.goto(url, {{
                    waitUntil: 'networkidle2',
                    timeout: 30000
                }});
                
                // Wait a bit for page to fully load
                await page.waitForTimeout(2000);
                
                // Look for PDF download button/link
                const pdfLink = await page.evaluate(() => {{
                    // Check for direct PDF embed
                    const embed = document.querySelector('embed[type="application/pdf"]');
                    if (embed) return embed.src;
                    
                    const iframe = document.querySelector('iframe[src*=".pdf"]');
                    if (iframe) return iframe.src;
                    
                    // Look for download links
                    const links = Array.from(document.querySelectorAll('a'));
                    
                    // Priority 1: Links with "PDF" text
                    const pdfTextLink = links.find(link => {{
                        const text = link.textContent.toLowerCase();
                        return (text.includes('pdf') && text.includes('download')) ||
                               text === 'pdf' ||
                               text.includes('full text pdf');
                    }});
                    if (pdfTextLink) return pdfTextLink.href;
                    
                    // Priority 2: Links ending with .pdf
                    const pdfHrefLink = links.find(link => link.href && link.href.endsWith('.pdf'));
                    if (pdfHrefLink) return pdfHrefLink.href;
                    
                    // Priority 3: Links with download attribute
                    const downloadLink = links.find(link => 
                        link.hasAttribute('download') && 
                        (link.href.includes('pdf') || link.textContent.toLowerCase().includes('pdf'))
                    );
                    if (downloadLink) return downloadLink.href;
                    
                    return null;
                }});
                
                if (pdfLink) {{
                    console.log(`  Found PDF link: ${{pdfLink.substring(0, 60)}}...`);
                    
                    // Download the PDF
                    const response = await page.goto(pdfLink, {{
                        waitUntil: 'networkidle2',
                        timeout: 30000
                    }});
                    
                    if (response && response.headers()['content-type']?.includes('pdf')) {{
                        const buffer = await response.buffer();
                        const filename = `${{paper.id}}.pdf`;
                        const filepath = path.join(OUTPUT_DIR, filename);
                        fs.writeFileSync(filepath, buffer);
                        console.log(`  ✅ Downloaded: ${{filepath}}`);
                        return filepath;
                    }}
                }}
                
                // Try clicking download button if no direct link found
                const downloadButton = await page.$('button:has-text("Download PDF"), a:has-text("Download PDF")');
                if (downloadButton) {{
                    console.log('  Clicking download button...');
                    await downloadButton.click();
                    await page.waitForTimeout(5000); // Wait for download
                    
                    // Check if file was downloaded
                    const filename = `${{paper.id}}.pdf`;
                    const filepath = path.join(OUTPUT_DIR, filename);
                    if (fs.existsSync(filepath)) {{
                        console.log(`  ✅ Downloaded via button: ${{filepath}}`);
                        return filepath;
                    }}
                }}
                
            }} catch (error) {{
                console.log(`  Error: ${{error.message.substring(0, 50)}}`);
            }}
        }}
        
        console.log('  ❌ Failed to download');
        return null;
        
    }} finally {{
        await page.close();
    }}
}}

async function main() {{
    console.log('🚀 Starting Puppeteer with OpenAthens authentication...');
    
    const browser = await puppeteer.launch({{
        headless: false, // Set to true for production
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled'
        ]
    }});
    
    const results = [];
    
    for (const paper of papers) {{
        const filepath = await downloadPaper(browser, paper);
        results.push({{
            id: paper.id,
            success: filepath !== null,
            path: filepath
        }});
    }}
    
    await browser.close();
    
    // Summary
    console.log('\\n' + '='.repeat(60));
    console.log('📊 SUMMARY');
    console.log('='.repeat(60));
    
    const successCount = results.filter(r => r.success).length;
    console.log(`\\nTotal: ${{successCount}}/${{papers.length}} downloaded`);
    console.log(`Success rate: ${{(successCount/papers.length*100).toFixed(1)}}%`);
    
    // Save results
    const summaryPath = path.join(OUTPUT_DIR, 'puppeteer_download_summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(results, null, 2));
    console.log(`\\nResults saved to: ${{summaryPath}}`);
}}

main().catch(console.error);
"""
    
    return script

def run_puppeteer_download(session_data: Dict, papers: List[Dict], output_dir: Path):
    """Run Puppeteer script to download papers."""
    
    # Create Puppeteer script
    script_content = create_puppeteer_script(
        session_data.get('cookies', {}),
        papers,
        output_dir
    )
    
    # Save script
    script_path = output_dir / "download_papers.js"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"Created Puppeteer script: {script_path}")
    
    # Check if puppeteer is installed
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
    except:
        print("❌ Node.js not found. Please install Node.js first.")
        print("   Run: sudo apt-get install nodejs npm")
        print("   Then: npm install puppeteer")
        return
    
    # Run the script
    print("\n🚀 Running Puppeteer download script...")
    print("="*60)
    
    try:
        result = subprocess.run(
            ['node', str(script_path)],
            cwd=str(output_dir),
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Puppeteer script completed successfully")
        else:
            print(f"\n❌ Puppeteer script failed with code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running Puppeteer: {e}")

def main():
    """Main function."""
    
    # Load OpenAthens session
    session_data = load_openathens_session()
    if not session_data:
        print("Please login to OpenAthens first")
        return
    
    # Parse BibTeX
    bib_file = "/home/ywatanabe/win/downloads/papers.bib"
    papers = parse_bib_simple(bib_file, limit=5)  # Start with 5 papers
    
    # Setup output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("\n📚 Paper Downloader with Puppeteer + OpenAthens")
    print("="*60)
    print(f"Processing {len(papers)} papers from BibTeX file")
    
    # Run Puppeteer download
    run_puppeteer_download(session_data, papers, output_dir)

if __name__ == "__main__":
    main()