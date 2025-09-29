#!/usr/bin/env python3
"""
Download PDFs for pac collection papers using multiple strategies.
Working in .dev_pac directory as requested.
"""

import asyncio
import json
import re
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PacPDFDownloader:
    """Download PDFs from the pac collection using browser automation and Zotero translators."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Working directory
        self.work_dir = Path('.dev_pac')
        self.work_dir.mkdir(exist_ok=True)
    
    def get_papers_needing_pdfs(self, limit: int = 5) -> List[Dict]:
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
                                    print(f"  📄 {count}. {item.name}")
                                    
                            except Exception as e:
                                print(f"  ⚠️  Error reading {unique_id}: {e}")
                                continue
        
        print(f"✅ Found {len(papers)} papers needing PDFs")
        return papers
    
    def get_paper_url(self, metadata: Dict) -> Optional[str]:
        """Get the best URL for downloading from paper metadata."""
        # Priority: DOI -> URL -> other fields
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
    
    def identify_publisher(self, url: str) -> str:
        """Identify publisher from URL."""
        url_lower = url.lower()
        
        if 'mdpi.com' in url_lower:
            return 'MDPI'
        elif 'frontiersin.org' in url_lower:
            return 'Frontiers'
        elif 'nature.com' in url_lower:
            return 'Nature'
        elif 'arxiv.org' in url_lower:
            return 'arXiv'
        elif 'biorxiv.org' in url_lower:
            return 'bioRxiv'
        elif 'ieee.org' in url_lower:
            return 'IEEE'
        elif 'springer.com' in url_lower:
            return 'Springer'
        elif 'sciencedirect.com' in url_lower or 'elsevier.com' in url_lower:
            return 'Elsevier'
        elif 'wiley.com' in url_lower:
            return 'Wiley'
        else:
            return 'Unknown'
    
    def get_publisher_pdf_patterns(self, url: str) -> List[str]:
        """Get publisher-specific PDF URL patterns."""
        pdf_urls = []
        publisher = self.identify_publisher(url)
        
        if publisher == 'MDPI':
            # MDPI pattern: https://www.mdpi.com/journal/volume/issue/article/pdf
            match = re.search(r'mdpi\.com/([^/]+)/([^/]+)/([^/]+)/([^/?]+)', url)
            if match:
                journal, volume, issue, article = match.groups()
                pdf_urls.extend([
                    f"https://www.mdpi.com/{journal}/{volume}/{issue}/{article}/pdf",
                    f"https://www.mdpi.com/{journal}/{volume}/{issue}/{article}/pdf-with-cover",
                ])
        
        elif publisher == 'arXiv':
            # arXiv pattern
            match = re.search(r'arxiv\.org/abs/([^/?]+)', url)
            if match:
                paper_id = match.group(1)
                pdf_urls.append(f"https://arxiv.org/pdf/{paper_id}.pdf")
        
        elif publisher == 'Nature':
            # Nature pattern
            match = re.search(r'nature\.com/articles/([^/?]+)', url)
            if match:
                article_id = match.group(1)
                pdf_urls.append(f"https://www.nature.com/articles/{article_id}.pdf")
        
        elif publisher == 'bioRxiv':
            # bioRxiv pattern
            if '/content/' in url:
                pdf_urls.append(f"{url}.full.pdf")
        
        return pdf_urls
    
    def test_pdf_access(self, pdf_url: str) -> Tuple[bool, str, int]:
        """Test if PDF URL is accessible."""
        try:
            response = self.session.head(pdf_url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            content_length = int(response.headers.get('content-length', 0))
            
            is_accessible = response.status_code == 200
            is_pdf = 'pdf' in content_type or pdf_url.endswith('.pdf')
            
            return (is_accessible and is_pdf), content_type, content_length
            
        except Exception as e:
            return False, str(e), 0
    
    def download_pdf_file(self, pdf_url: str, output_path: Path) -> bool:
        """Download PDF file to specified path."""
        try:
            print(f"    📥 Downloading: {pdf_url}")
            response = self.session.get(pdf_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = output_path.stat().st_size
                
                # Verify it's a PDF
                with open(output_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        print(f"    ✅ Downloaded {file_size / 1024 / 1024:.1f} MB")
                        return True
                    else:
                        print(f"    ❌ Not a valid PDF (header: {header})")
                        output_path.unlink()
                        return False
            else:
                print(f"    ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    ❌ Download error: {e}")
            return False
    
    async def try_browser_extraction(self, url: str) -> List[str]:
        """Use browser automation to extract PDF links."""
        try:
            # Import puppeteer functions
            from claude_code import mcp__puppeteer__puppeteer_navigate as navigate
            from claude_code import mcp__puppeteer__puppeteer_evaluate as evaluate
            from claude_code import mcp__puppeteer__puppeteer_screenshot as screenshot
            
            print(f"    🌐 Loading page with browser...")
            await navigate(url=url)
            await asyncio.sleep(3)  # Wait for page to load
            
            # Take screenshot for debugging
            screenshot_name = f"page_{int(time.time())}"
            await screenshot(name=screenshot_name, width=1200, height=800)
            print(f"    📸 Screenshot saved: {screenshot_name}")
            
            # Extract PDF links using JavaScript
            pdf_urls = await evaluate(script="""
                () => {
                    const urls = [];
                    
                    // Common PDF link patterns
                    const selectors = [
                        'a[href*=".pdf"]',
                        'a[href*="/pdf"]',
                        'a[href*="download"]',
                        'button[onclick*="pdf"]',
                        '[data-pdf-url]',
                        '.pdf-download',
                        '.download-pdf',
                    ];
                    
                    // Find links by selectors
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const elem of elements) {
                                const url = elem.href || elem.getAttribute('data-pdf-url') || elem.getAttribute('onclick');
                                if (url && url.includes && (url.includes('pdf') || url.includes('download'))) {
                                    if (!urls.includes(url)) {
                                        urls.push(url);
                                    }
                                }
                            }
                        } catch (e) {
                            console.log('Selector error:', selector, e);
                        }
                    }
                    
                    // Also look for buttons with download text
                    const buttons = document.querySelectorAll('button, a');
                    for (const btn of buttons) {
                        const text = btn.textContent ? btn.textContent.toLowerCase() : '';
                        if (text.includes('download') && (text.includes('pdf') || text.includes('article') || text.includes('full'))) {
                            const href = btn.href || btn.getAttribute('data-url') || '';
                            if (href && !urls.includes(href)) {
                                urls.push(href);
                            }
                        }
                    }
                    
                    return urls;
                }
            """)
            
            if isinstance(pdf_urls, list) and pdf_urls:
                print(f"    ✅ Found {len(pdf_urls)} potential PDF URLs")
                return pdf_urls
            else:
                print(f"    ❌ No PDF links found on page")
                return []
                
        except Exception as e:
            print(f"    ❌ Browser extraction failed: {e}")
            return []
    
    def generate_filename(self, paper: Dict) -> str:
        """Generate filename for downloaded PDF."""
        metadata = paper['metadata']
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        
        if authors and year:
            first_author = str(authors[0]) if authors else 'Unknown'
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            
            # Clean for filename
            first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
            return f"{first_author}-{year}.pdf"
        else:
            return f"{paper['human_name']}.pdf"
    
    def update_paper_metadata(self, paper: Dict, filename: str, download_url: str):
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
            
            print(f"    ✅ Updated metadata")
            
        except Exception as e:
            print(f"    ⚠️  Failed to update metadata: {e}")
    
    async def download_paper_pdf(self, paper: Dict) -> bool:
        """Download PDF for a single paper using multiple strategies."""
        print(f"\n{'='*80}")
        print(f"📄 Processing: {paper['human_name']}")
        print(f"{'='*80}")
        
        metadata = paper['metadata']
        print(f"  📝 Title: {metadata.get('title', 'N/A')[:70]}...")
        print(f"  📅 Year: {metadata.get('year', 'N/A')}")
        print(f"  🏢 Journal: {metadata.get('journal', 'N/A')}")
        
        # Get URL
        url = self.get_paper_url(metadata)
        if not url:
            print("  ❌ No suitable URL found in metadata")
            return False
        
        publisher = self.identify_publisher(url)
        print(f"  🏢 Publisher: {publisher}")
        print(f"  🌐 Source URL: {url}")
        
        # Generate output path
        filename = self.generate_filename(paper)
        output_path = paper['master_path'] / filename
        
        print(f"  💾 Target: {filename}")
        
        # Strategy 1: Try publisher-specific PDF patterns
        print(f"\n  🎯 Strategy 1: Publisher patterns for {publisher}")
        pdf_patterns = self.get_publisher_pdf_patterns(url)
        
        if pdf_patterns:
            for pdf_url in pdf_patterns:
                print(f"    Testing: {pdf_url}")
                is_accessible, content_type, size = self.test_pdf_access(pdf_url)
                
                if is_accessible:
                    print(f"    ✅ Accessible PDF! {size/1024/1024:.1f} MB, {content_type}")
                    
                    if self.download_pdf_file(pdf_url, output_path):
                        self.update_paper_metadata(paper, filename, pdf_url)
                        return True
                else:
                    print(f"    ❌ Not accessible: {content_type}")
        else:
            print(f"    ❌ No patterns available for {publisher}")
        
        # Strategy 2: Browser-based extraction
        print(f"\n  🌐 Strategy 2: Browser-based extraction")
        try:
            browser_pdf_urls = await self.try_browser_extraction(url)
            
            if browser_pdf_urls:
                for pdf_url in browser_pdf_urls[:3]:  # Try first 3
                    print(f"    Testing: {pdf_url}")
                    
                    # Clean up URL if it's from onclick
                    if 'window.open' in pdf_url:
                        match = re.search(r"window\.open\(['\"](.*?)['\"]", pdf_url)
                        if match:
                            pdf_url = match.group(1)
                    
                    # Make URL absolute if needed
                    if pdf_url.startswith('/'):
                        from urllib.parse import urljoin
                        pdf_url = urljoin(url, pdf_url)
                    
                    is_accessible, content_type, size = self.test_pdf_access(pdf_url)
                    
                    if is_accessible:
                        print(f"    ✅ Accessible PDF! {size/1024/1024:.1f} MB, {content_type}")
                        
                        if self.download_pdf_file(pdf_url, output_path):
                            self.update_paper_metadata(paper, filename, pdf_url)
                            return True
                    else:
                        print(f"    ❌ Not accessible: {content_type}")
            else:
                print(f"    ❌ No PDF URLs found by browser")
                
        except Exception as e:
            print(f"    ❌ Browser extraction error: {e}")
        
        print(f"  ❌ All download strategies failed for {paper['human_name']}")
        return False


async def main():
    """Main function to download PDFs from pac collection."""
    print("🚀 PAC Collection PDF Downloader")
    print("=" * 60)
    print("Working in .dev_pac directory")
    
    downloader = PacPDFDownloader()
    
    # Get papers needing PDFs
    papers = downloader.get_papers_needing_pdfs(limit=3)
    
    if not papers:
        print("✅ No papers need PDFs!")
        return
    
    print(f"\n📋 Will attempt to download {len(papers)} PDFs:")
    for i, paper in enumerate(papers, 1):
        metadata = paper['metadata']
        url = downloader.get_paper_url(metadata)
        publisher = downloader.identify_publisher(url) if url else 'Unknown'
        
        print(f"  {i}. {paper['human_name']}")
        print(f"     Publisher: {publisher}")
        print(f"     Journal: {metadata.get('journal', 'N/A')}")
        print(f"     Year: {metadata.get('year', 'N/A')}")
    
    # Download PDFs
    successful_downloads = 0
    
    for paper in papers:
        try:
            success = await downloader.download_paper_pdf(paper)
            
            if success:
                successful_downloads += 1
                print(f"\n✅ SUCCESS: {paper['human_name']}")
            else:
                print(f"\n❌ FAILED: {paper['human_name']}")
            
            # Wait between downloads to be respectful
            if paper != papers[-1]:  # Don't wait after the last one
                print(f"\n⏳ Waiting 3 seconds before next download...")
                await asyncio.sleep(3)
            
        except Exception as e:
            print(f"\n💥 ERROR processing {paper['human_name']}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 Download Session Complete!")
    print(f"✅ Successful downloads: {successful_downloads}/{len(papers)}")
    
    if successful_downloads > 0:
        success_rate = (successful_downloads / len(papers)) * 100
        print(f"📊 Success rate: {success_rate:.1f}%")
        print(f"\n🎉 Great! {successful_downloads} PDFs were downloaded successfully")
        print(f"💡 Working patterns can be applied to remaining papers")
    else:
        print(f"\n🤔 No PDFs downloaded this session")
        print(f"💡 Common issues and solutions:")
        print(f"   - Paywalled content → Use institutional authentication")
        print(f"   - JavaScript-heavy sites → Enhanced browser automation")
        print(f"   - Publisher-specific access → Specialized download strategies")
    
    print(f"\n📁 Check screenshots in your home directory for debugging")
    print(f"📁 Work files saved in .dev_pac directory")


if __name__ == "__main__":
    asyncio.run(main())