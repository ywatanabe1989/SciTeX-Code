#!/usr/bin/env python3
"""
Direct crawl4ai PDF downloader for PAC collection.
Uses crawl4ai HTTP API directly without complex dependencies.
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
import re


class DirectCrawl4AIDownloader:
    """Download PDFs using crawl4ai HTTP API directly."""
    
    def __init__(self, base_url: str = "http://localhost:11235"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # Check if crawl4ai is available
        if self.is_available():
            print("✅ Crawl4AI server is available")
        else:
            print("❌ Crawl4AI server not available at", base_url)
    
    def is_available(self) -> bool:
        """Check if crawl4ai server is available."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
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
        
        print("📚 Scanning pac collection for papers without PDFs...")
        
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
    
    def get_paper_url(self, metadata: Dict) -> Optional[str]:
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
    
    def extract_pdf_links_via_crawl4ai(self, url: str) -> List[str]:
        """Extract PDF links using crawl4ai JavaScript execution."""
        try:
            # JavaScript to extract PDF links
            scripts = [
                """
                (function() {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links
                        .filter(link => link.href && (
                            link.href.includes('.pdf') || 
                            link.href.includes('/pdf') ||
                            link.textContent.toLowerCase().includes('pdf') ||
                            link.textContent.toLowerCase().includes('download')
                        ))
                        .map(link => link.href);
                })()
                """
            ]
            
            payload = {
                "url": url,
                "scripts": scripts
            }
            
            response = self.session.post(
                f"{self.base_url}/execute_js",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and 'js_execution_result' in result:
                    links = result['js_execution_result']
                    if isinstance(links, list):
                        return links
            
            return []
            
        except Exception as e:
            print(f"    ❌ Error extracting PDF links: {e}")
            return []
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Get page content via crawl4ai."""
        try:
            payload = {"url": url}
            response = self.session.post(
                f"{self.base_url}/html",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("html", "")
            
            return None
            
        except Exception as e:
            print(f"    ❌ Error getting page content: {e}")
            return None
    
    def extract_pdf_links_from_html(self, html: str, base_url: str) -> List[str]:
        """Extract PDF links from HTML content."""
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
                absolute_links.append(urljoin(base_url, link))
        
        return list(set(absolute_links))  # Remove duplicates
    
    def download_pdf(self, pdf_url: str, output_path: Path) -> bool:
        """Download PDF file."""
        try:
            print(f"    📥 Downloading: {pdf_url}")
            
            response = self.session.get(pdf_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify it's a PDF
                with open(output_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        file_size = output_path.stat().st_size
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
    
    def get_publisher_pdf_patterns(self, url: str, metadata: Dict) -> List[str]:
        """Get publisher-specific PDF URL patterns."""
        pdf_patterns = []
        journal = metadata.get('journal', '').lower()
        doi = metadata.get('doi', '')
        
        # MATEC Web of Conferences
        if 'matec' in journal and doi:
            # Direct PDF URL for MATEC
            pdf_patterns.append(f"https://www.matec-conferences.org/articles/matecconf/pdf/{doi.split('/')[-1][:4]}/matecconf_{doi.split('/')[-1]}.pdf")
        
        # IEEE
        elif 'ieee' in journal and url:
            # IEEE might have stamp URLs
            if 'ieeexplore' in url:
                pdf_patterns.append(url.replace('/document/', '/stamp/stamp.jsp?tp=&arnumber='))
        
        # Frontiers
        elif 'frontiers' in journal and url:
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
        
        return pdf_patterns
    
    def generate_filename(self, paper: Dict) -> str:
        """Generate filename for downloaded PDF."""
        metadata = paper['metadata']
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        
        if authors and year:
            first_author = str(authors[0]) if authors else 'Unknown'
            # Clean author name
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            elif ' and ' in first_author:
                first_author = first_author.split(' and ')[0]
            
            # Get last name
            if ' ' in first_author:
                parts = first_author.strip().split()
                first_author = parts[-1]
            
            # Clean for filename
            first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
            return f"{first_author}-{year}.pdf"
        else:
            return f"{paper['human_name']}.pdf"
    
    def update_metadata(self, paper: Dict, filename: str, download_url: str):
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
    
    def download_paper_pdf(self, paper: Dict) -> bool:
        """Download PDF for a single paper."""
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
        
        print(f"  🌐 URL: {url}")
        
        # Generate output path
        filename = self.generate_filename(paper)
        output_path = paper['master_path'] / filename
        
        print(f"  💾 Target: {filename}")
        
        # Strategy 1: Try publisher-specific patterns
        print(f"\n  🎯 Strategy 1: Publisher-specific patterns")
        pdf_patterns = self.get_publisher_pdf_patterns(url, metadata)
        
        if pdf_patterns:
            for pattern_url in pdf_patterns:
                print(f"    Testing: {pattern_url}")
                
                if self.download_pdf(pattern_url, output_path):
                    self.update_metadata(paper, filename, pattern_url)
                    return True
        else:
            print(f"    No patterns for this publisher")
        
        # Strategy 2: Get page and extract PDF links
        if self.is_available():
            print(f"\n  🕷️  Strategy 2: Extract PDF links via crawl4ai")
            
            # Try JavaScript extraction first
            pdf_links = self.extract_pdf_links_via_crawl4ai(url)
            
            if not pdf_links:
                # Fall back to HTML parsing
                print(f"    Getting page HTML...")
                html = self.get_page_content(url)
                
                if html:
                    print(f"    Got {len(html)} chars of HTML")
                    pdf_links = self.extract_pdf_links_from_html(html, url)
            
            if pdf_links:
                print(f"    ✅ Found {len(pdf_links)} PDF candidates")
                
                for pdf_url in pdf_links[:3]:  # Try first 3
                    print(f"    Testing: {pdf_url}")
                    
                    if self.download_pdf(pdf_url, output_path):
                        self.update_metadata(paper, filename, pdf_url)
                        return True
            else:
                print(f"    ❌ No PDF links found")
        
        print(f"  ❌ All strategies failed")
        return False


def main():
    """Main function to download PDFs."""
    print("🚀 Direct Crawl4AI PDF Downloader")
    print("=" * 60)
    
    downloader = DirectCrawl4AIDownloader()
    
    if not downloader.is_available():
        print("\n⚠️  Crawl4AI server not running!")
        print("Start it with: docker run -d -p 11235:11235 --name crawl4ai unclecode/crawl4ai:0.6.0rc1-r2")
        return
    
    # Get papers needing PDFs
    papers = downloader.get_papers_needing_pdfs(limit=5)
    
    if not papers:
        print("✅ No papers need PDFs!")
        return
    
    print(f"\n📋 Will attempt to download {len(papers)} PDFs")
    
    # Download PDFs
    successful = 0
    
    for paper in papers:
        try:
            success = downloader.download_paper_pdf(paper)
            
            if success:
                successful += 1
                print(f"\n✅ SUCCESS: {paper['human_name']}")
            else:
                print(f"\n❌ FAILED: {paper['human_name']}")
            
            # Wait between downloads
            if paper != papers[-1]:
                print(f"\n⏳ Waiting 3 seconds...")
                time.sleep(3)
            
        except Exception as e:
            print(f"\n💥 Error processing {paper['human_name']}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 Download Session Complete!")
    print(f"✅ Successful downloads: {successful}/{len(papers)}")
    
    if successful > 0:
        print(f"🎉 Downloaded {successful} PDFs successfully!")
    else:
        print(f"🤔 No PDFs downloaded - may need authentication or manual intervention")


if __name__ == "__main__":
    main()