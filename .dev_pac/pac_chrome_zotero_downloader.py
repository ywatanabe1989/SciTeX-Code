#!/usr/bin/env python3
"""
PAC Collection PDF Downloader using Chrome + Zotero Translators.

This script:
1. Opens all paper DOI URLs in Chrome tabs using authenticated browser
2. Runs Zotero translators on each tab to extract PDF URLs
3. Downloads the PDFs
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

# Add scitex_repo to path
import sys
sys.path.insert(0, '/home/ywatanabe/proj/scitex_repo/src')

from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser import BrowserManager
from scitex.scholar.download._ZoteroTranslatorRunner import ZoteroTranslatorRunner

logger = logging.getLogger(__name__)


class PacChromeZoteroDownloader:
    """Download PDFs using Chrome with authentication and Zotero translators."""
    
    def __init__(self):
        self.auth_manager = AuthenticationManager()
        self.browser_manager = None
        self.translator_runner = ZoteroTranslatorRunner()
        self.browser = None
        self.context = None
        
        # Statistics
        self.stats = {
            'total': 0,
            'already_have': 0,
            'downloaded': 0,
            'failed': 0,
            'no_doi': 0,
        }
        
        # Results tracking
        self.results = []
    
    async def initialize_browser(self):
        """Initialize authenticated browser with extensions."""
        logger.info("Initializing authenticated browser...")
        
        self.browser_manager = BrowserManager(
            browser_mode="headless",  # Use headless for automation
            auth_manager=self.auth_manager,
        )
        
        # Get browser with authentication profile
        await self.browser_manager.get_browser_async_with_profile()
        self.context = self.browser_manager._shared_context
        
        logger.success("Browser initialized with authentication and extensions")
    
    def get_all_pac_papers(self) -> List[Dict]:
        """Get all papers from pac collection."""
        library_dir = Path.home() / ".scitex" / "scholar" / "library"
        pac_dir = library_dir / "pac"
        master_dir = library_dir / "MASTER"
        
        if not pac_dir.exists():
            logger.error(f"Collection directory not found: {pac_dir}")
            return []
        
        papers = []
        
        logger.info("Scanning PAC collection...")
        
        for item in sorted(pac_dir.iterdir()):
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
                                
                                paper = {
                                    'human_name': item.name,
                                    'unique_id': unique_id,
                                    'master_path': master_path,
                                    'metadata': metadata,
                                }
                                
                                # Check if PDF already exists
                                pdf_files = list(master_path.glob("*.pdf"))
                                paper['has_pdf'] = len(pdf_files) > 0
                                if pdf_files:
                                    paper['pdf_file'] = pdf_files[0].name
                                
                                papers.append(paper)
                                
                            except Exception as e:
                                logger.error(f"Error reading {unique_id}: {e}")
                                continue
        
        return papers
    
    def get_paper_url(self, metadata: Dict) -> Optional[str]:
        """Get URL from paper metadata."""
        if 'doi' in metadata and metadata['doi']:
            doi = metadata['doi']
            if not doi.startswith('http'):
                return f"https://doi.org/{doi}"
            return doi
        
        url_fields = ['url', 'publisher_url', 'journal_url']
        for field in url_fields:
            if field in metadata and metadata[field]:
                return metadata[field]
        
        return None
    
    async def open_papers_in_tabs(self, papers: List[Dict], batch_size: int = 10) -> List[Tuple[Dict, any]]:
        """Open papers in Chrome tabs in batches."""
        paper_tabs = []
        papers_with_urls = []
        
        # Filter papers with URLs
        for paper in papers:
            if paper['has_pdf']:
                continue
                
            url = self.get_paper_url(paper['metadata'])
            if url:
                papers_with_urls.append((paper, url))
            else:
                self.stats['no_doi'] += 1
                logger.warning(f"No URL for: {paper['human_name']}")
        
        logger.info(f"Opening {len(papers_with_urls)} papers in Chrome tabs (batch size: {batch_size})")
        
        # Process in batches
        for i in range(0, len(papers_with_urls), batch_size):
            batch = papers_with_urls[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} papers)")
            
            batch_tabs = []
            for paper, url in batch:
                try:
                    # Open new tab
                    page = await self.context.new_page()
                    
                    # Navigate to URL
                    logger.info(f"Opening: {paper['human_name'][:40]} -> {url}")
                    
                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        await page.wait_for_load_state('networkidle', timeout=10000)
                        batch_tabs.append((paper, page))
                        logger.success(f"Loaded: {paper['human_name'][:40]}")
                    except Exception as e:
                        logger.error(f"Failed to load {paper['human_name']}: {e}")
                        await page.close()
                        
                except Exception as e:
                    logger.error(f"Error opening tab for {paper['human_name']}: {e}")
            
            # Process this batch with Zotero translators
            if batch_tabs:
                await self.process_batch_with_zotero(batch_tabs)
            
            # Close tabs from this batch
            for paper, page in batch_tabs:
                try:
                    await page.close()
                except:
                    pass
            
            # Wait between batches
            if i + batch_size < len(papers_with_urls):
                logger.info("Waiting 5 seconds before next batch...")
                await asyncio.sleep(5)
        
        return paper_tabs
    
    async def process_batch_with_zotero(self, paper_tabs: List[Tuple[Dict, any]]):
        """Process a batch of tabs with Zotero translators."""
        logger.info(f"Running Zotero translators on {len(paper_tabs)} tabs")
        
        for paper, page in paper_tabs:
            try:
                # Get current URL (might have redirected)
                current_url = page.url
                logger.info(f"Processing: {paper['human_name'][:40]}")
                logger.info(f"  URL: {current_url}")
                
                # Find matching translator
                matching_translator = None
                for name, translator in self.translator_runner._translators.items():
                    try:
                        if re.search(translator['target_regex'], current_url):
                            matching_translator = translator
                            logger.info(f"  Matched translator: {translator['label']}")
                            break
                    except:
                        pass
                
                if not matching_translator:
                    logger.warning(f"  No matching translator for URL pattern")
                    continue
                
                # Run translator
                try:
                    # Inject Zotero shim
                    await page.evaluate(self.translator_runner._zotero_shim)
                    
                    # Run translator code
                    translator_code = matching_translator['content']
                    
                    # Extract detect and do functions
                    detect_match = re.search(r'function detectWeb\([^)]*\)\s*{([^}]+)}', translator_code)
                    do_match = re.search(r'function doWeb\([^)]*\)\s*{(.+)}', translator_code, re.DOTALL)
                    
                    if detect_match and do_match:
                        # Check if translator detects content
                        detect_result = await page.evaluate(f"""
                            (function() {{
                                var doc = document;
                                var url = window.location.href;
                                {detect_match.group(0)}
                                return detectWeb(doc, url);
                            }})()
                        """)
                        
                        if detect_result:
                            logger.info(f"  Detected type: {detect_result}")
                            
                            # Run doWeb to extract data
                            result = await page.evaluate(f"""
                                (function() {{
                                    var doc = document;
                                    var url = window.location.href;
                                    var items = [];
                                    
                                    // Override Zotero.selectItems
                                    window.Zotero.selectItems = function(items, callback) {{
                                        // Auto-select first item
                                        var keys = Object.keys(items);
                                        if (keys.length > 0) {{
                                            callback(keys[0]);
                                        }}
                                    }};
                                    
                                    // Capture complete callback
                                    window.Zotero.Item.prototype.complete = function() {{
                                        items.push(this);
                                    }};
                                    
                                    {translator_code}
                                    
                                    doWeb(doc, url);
                                    
                                    // Return captured items
                                    return items;
                                }})()
                            """)
                            
                            if result and len(result) > 0:
                                item = result[0]
                                logger.success(f"  Extracted metadata: {item.get('title', 'Unknown')[:50]}")
                                
                                # Look for PDF attachments
                                if 'attachments' in item:
                                    for attachment in item['attachments']:
                                        if attachment.get('mimeType') == 'application/pdf':
                                            pdf_url = attachment.get('url')
                                            if pdf_url:
                                                logger.success(f"  Found PDF URL: {pdf_url}")
                                                
                                                # Download PDF
                                                await self.download_pdf(paper, pdf_url, page)
                                                break
                                else:
                                    logger.warning(f"  No PDF attachments found")
                            else:
                                logger.warning(f"  No items extracted")
                        else:
                            logger.warning(f"  Translator did not detect content")
                    else:
                        logger.warning(f"  Could not parse translator functions")
                        
                except Exception as e:
                    logger.error(f"  Error running translator: {e}")
                    
            except Exception as e:
                logger.error(f"Error processing {paper['human_name']}: {e}")
    
    async def download_pdf(self, paper: Dict, pdf_url: str, page: any):
        """Download PDF for a paper."""
        try:
            filename = self.generate_filename(paper)
            output_path = paper['master_path'] / filename
            
            logger.info(f"  Downloading PDF: {filename}")
            
            # Navigate to PDF URL
            response = await page.goto(pdf_url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status == 200:
                # Get content
                content = await response.body()
                
                # Check if it's a PDF
                if content[:4] == b'%PDF':
                    # Save PDF
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    
                    file_size = output_path.stat().st_size
                    logger.success(f"  Downloaded: {file_size / 1024 / 1024:.1f} MB")
                    
                    # Update metadata
                    self.update_metadata(paper, filename, pdf_url)
                    
                    self.stats['downloaded'] += 1
                    self.results.append({
                        'name': paper['human_name'],
                        'status': 'SUCCESS',
                        'message': f"Downloaded {file_size / 1024 / 1024:.1f} MB"
                    })
                    return True
                else:
                    logger.error(f"  Not a PDF (header: {content[:4]})")
            else:
                logger.error(f"  Failed to download (status: {response.status if response else 'None'})")
                
        except Exception as e:
            logger.error(f"  Download error: {e}")
        
        self.stats['failed'] += 1
        self.results.append({
            'name': paper['human_name'],
            'status': 'FAILED',
            'message': str(e) if 'e' in locals() else 'Download failed'
        })
        return False
    
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
            metadata['pdf_download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            metadata['pdf_download_method'] = 'chrome_zotero'
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
    
    async def run(self):
        """Run the download process."""
        logger.info("=" * 80)
        logger.success("PAC COLLECTION PDF DOWNLOADER (Chrome + Zotero)")
        logger.info("=" * 80)
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize browser
        await self.initialize_browser()
        
        # Get all papers
        papers = self.get_all_pac_papers()
        self.stats['total'] = len(papers)
        
        logger.info(f"Found {len(papers)} papers in PAC collection")
        
        # Count existing PDFs
        already_have = sum(1 for p in papers if p['has_pdf'])
        self.stats['already_have'] = already_have
        need_download = len(papers) - already_have
        
        logger.success(f"Already have PDFs: {already_have}")
        logger.info(f"Need to download: {need_download}")
        
        if need_download == 0:
            logger.success("All papers already have PDFs!")
            return
        
        # Process papers
        await self.open_papers_in_tabs(papers, batch_size=5)
        
        # Print summary
        self.print_summary()
        
        # Close browser
        if self.browser_manager:
            await self.browser_manager.close()
    
    def print_summary(self):
        """Print download summary."""
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total papers: {self.stats['total']}")
        logger.success(f"Already had PDFs: {self.stats['already_have']}")
        logger.success(f"Successfully downloaded: {self.stats['downloaded']}")
        logger.error(f"Failed to download: {self.stats['failed']}")
        logger.warning(f"Papers without DOI/URL: {self.stats['no_doi']}")
        
        # Calculate success rate
        total_attempted = self.stats['downloaded'] + self.stats['failed']
        if total_attempted > 0:
            success_rate = (self.stats['downloaded'] / total_attempted) * 100
            logger.info(f"Download success rate: {success_rate:.1f}%")
        
        coverage = ((self.stats['already_have'] + self.stats['downloaded']) / self.stats['total'] * 100)
        logger.info(f"Collection coverage: {coverage:.1f}%")
        
        # List failed papers
        failed_papers = [r for r in self.results if r['status'] == 'FAILED']
        if failed_papers:
            logger.info("")
            logger.warning("Failed downloads:")
            for paper in failed_papers[:10]:  # Show first 10
                logger.error(f"  - {paper['name']}: {paper['message']}")


async def main():
    """Main function."""
    downloader = PacChromeZoteroDownloader()
    await downloader.run()


if __name__ == "__main__":
    asyncio.run(main())