#!/usr/bin/env python3
"""
Download PDFs from PAC collection using crawl4ai integration.
Uses the existing Scholar system with authentication.
"""

import sys
import os
sys.path.insert(0, '/home/ywatanabe/proj/scitex_repo/src')

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

# Import Scholar modules
from scitex import logging
from scitex.scholar.browser.crawl4ai_integration import Crawl4AIIntegration

logger = logging.getLogger(__name__)


class PacPDFDownloaderCrawl4AI:
    """Download PDFs from PAC collection using crawl4ai."""
    
    def __init__(self):
        self.crawl4ai = Crawl4AIIntegration()
        logger.success("Initialized Crawl4AI integration")
        
    def get_papers_needing_pdfs(self, limit: int = 5) -> List[Dict]:
        """Get papers from pac collection that need PDFs."""
        library_dir = Path.home() / ".scitex" / "scholar" / "library"
        pac_dir = library_dir / "pac"
        master_dir = library_dir / "MASTER"
        
        if not pac_dir.exists():
            logger.error(f"Collection directory not found: {pac_dir}")
            return []
        
        papers = []
        count = 0
        
        logger.info("Scanning pac collection for papers without PDFs...")
        
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
                                    logger.info(f"  {count}. {item.name}")
                                    
                            except Exception as e:
                                logger.error(f"Error reading {unique_id}: {e}")
                                continue
        
        logger.success(f"Found {len(papers)} papers needing PDFs")
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
    
    def generate_filename(self, paper: Dict) -> str:
        """Generate filename for downloaded PDF."""
        metadata = paper['metadata']
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        
        if authors and year:
            first_author = str(authors[0]) if authors else 'Unknown'
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            elif ' ' in first_author:
                # Get last name from "First Last" format
                first_author = first_author.split()[-1]
            
            # Clean for filename
            import re
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
            
            logger.success("Updated metadata")
            
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
    
    async def download_paper_pdf(self, paper: Dict) -> bool:
        """Download PDF for a single paper using crawl4ai."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {paper['human_name']}")
        logger.info(f"{'='*80}")
        
        metadata = paper['metadata']
        logger.info(f"Title: {metadata.get('title', 'N/A')[:70]}...")
        logger.info(f"Year: {metadata.get('year', 'N/A')}")
        logger.info(f"Journal: {metadata.get('journal', 'N/A')}")
        
        # Get URL
        url = self.get_paper_url(metadata)
        if not url:
            logger.error("No suitable URL found in metadata")
            return False
        
        logger.info(f"URL: {url}")
        
        # Generate output path
        filename = self.generate_filename(paper)
        output_path = paper['master_path'] / filename
        
        try:
            # Extract content using crawl4ai
            logger.info("Extracting content with crawl4ai...")
            content = await self.crawl4ai.extract_content(url)
            
            if content:
                logger.success(f"Got content ({len(content)} chars)")
                
                # Try to find PDF links
                logger.info("Looking for PDF links...")
                pdf_links = await self.crawl4ai.extract_pdf_links(url)
                
                if pdf_links:
                    logger.success(f"Found {len(pdf_links)} PDF links")
                    
                    # Try downloading each PDF link
                    for pdf_url in pdf_links[:3]:  # Try first 3
                        logger.info(f"Trying: {pdf_url}")
                        
                        # Try downloading the PDF
                        success = await self.crawl4ai.download_pdf(
                            pdf_url, 
                            str(output_path)
                        )
                        
                        if success:
                            # Verify it's a PDF
                            if output_path.exists():
                                with open(output_path, 'rb') as f:
                                    header = f.read(4)
                                    if header == b'%PDF':
                                        file_size = output_path.stat().st_size
                                        logger.success(f"Downloaded PDF: {file_size / 1024 / 1024:.1f} MB")
                                        self.update_metadata(paper, filename, pdf_url)
                                        return True
                                    else:
                                        logger.error(f"Not a valid PDF (header: {header})")
                                        output_path.unlink()
                else:
                    logger.warning("No PDF links found")
                    
                    # Try publisher-specific patterns
                    logger.info("Trying publisher-specific patterns...")
                    
                    # Check for known publishers
                    journal = metadata.get('journal', '').lower()
                    doi = metadata.get('doi', '')
                    
                    pdf_patterns = []
                    
                    # MATEC Web of Conferences (EDP Sciences)
                    if 'matec' in journal:
                        # Pattern: https://www.matec-conferences.org/articles/matecconf/pdf/2018/67/matecconf_icongdm2018_03016.pdf
                        if doi:
                            # Extract article number from DOI
                            import re
                            match = re.search(r'10\.1051/matecconf/(\d+)(\d+)', doi)
                            if match:
                                year_part = match.group(1)[:4]
                                article_num = match.group(2)
                                pdf_patterns.append(
                                    f"https://www.matec-conferences.org/articles/matecconf/pdf/{year_part}/*/matecconf_*_{article_num}.pdf"
                                )
                    
                    # IEEE
                    elif 'ieee' in journal:
                        if doi:
                            # IEEE Xplore pattern
                            import re
                            match = re.search(r'10\.1109/([^/]+)', doi)
                            if match:
                                pdf_patterns.append(f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={match.group(1)}")
                    
                    # Frontiers
                    elif 'frontiers' in journal:
                        if url:
                            pdf_patterns.append(f"{url}/pdf")
                    
                    # Nature
                    elif 'nature' in journal:
                        if doi:
                            import re
                            match = re.search(r'nature\.com/articles/([^/?]+)', url) if url else None
                            if match:
                                pdf_patterns.append(f"https://www.nature.com/articles/{match.group(1)}.pdf")
                    
                    # Scientific Reports
                    elif 'scientific reports' in journal:
                        if doi:
                            import re
                            match = re.search(r'10\.1038/([^/]+)', doi)
                            if match:
                                pdf_patterns.append(f"https://www.nature.com/articles/{match.group(1)}.pdf")
                    
                    # Try pattern URLs
                    for pattern_url in pdf_patterns:
                        logger.info(f"Trying pattern: {pattern_url}")
                        
                        success = await self.crawl4ai.download_pdf(
                            pattern_url,
                            str(output_path)
                        )
                        
                        if success and output_path.exists():
                            with open(output_path, 'rb') as f:
                                header = f.read(4)
                                if header == b'%PDF':
                                    file_size = output_path.stat().st_size
                                    logger.success(f"Downloaded PDF: {file_size / 1024 / 1024:.1f} MB")
                                    self.update_metadata(paper, filename, pattern_url)
                                    return True
                                else:
                                    output_path.unlink()
            
            # Take a screenshot for debugging
            logger.info("Taking screenshot for debugging...")
            screenshot_path = paper['master_path'] / f"screenshot_{int(time.time())}.png"
            await self.crawl4ai.take_screenshot(url, str(screenshot_path))
            logger.info(f"Screenshot saved: {screenshot_path.name}")
            
        except Exception as e:
            logger.error(f"Error processing paper: {e}")
            return False
        
        logger.error(f"Failed to download PDF for {paper['human_name']}")
        return False


async def main():
    """Main function to download PDFs with crawl4ai."""
    logger.info("🚀 PAC Collection PDF Downloader (Crawl4AI)")
    logger.info("=" * 60)
    
    downloader = PacPDFDownloaderCrawl4AI()
    
    # Get papers needing PDFs
    papers = downloader.get_papers_needing_pdfs(limit=5)
    
    if not papers:
        logger.success("No papers need PDFs!")
        return
    
    logger.info(f"\nWill attempt to download {len(papers)} PDFs:")
    for i, paper in enumerate(papers, 1):
        metadata = paper['metadata']
        logger.info(f"  {i}. {paper['human_name']}")
        logger.info(f"     Journal: {metadata.get('journal', 'N/A')}")
        logger.info(f"     Year: {metadata.get('year', 'N/A')}")
        logger.info(f"     DOI: {metadata.get('doi', 'N/A')}")
    
    # Download PDFs
    successful = 0
    
    for paper in papers:
        try:
            success = await downloader.download_paper_pdf(paper)
            
            if success:
                successful += 1
                logger.success(f"SUCCESS: {paper['human_name']}")
            else:
                logger.error(f"FAILED: {paper['human_name']}")
            
            # Wait between downloads
            if paper != papers[-1]:
                logger.info("Waiting 3 seconds...")
                await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Error processing {paper['human_name']}: {e}")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.success(f"Download Session Complete!")
    logger.info(f"Successful downloads: {successful}/{len(papers)}")
    
    if successful > 0:
        logger.success(f"Downloaded {successful} PDFs successfully!")
        logger.info("Working patterns can be applied to remaining papers")
    else:
        logger.warning("No PDFs downloaded this session")
        logger.info("May need institutional authentication or manual intervention")


if __name__ == "__main__":
    asyncio.run(main())