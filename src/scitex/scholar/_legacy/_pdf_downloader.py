#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:20:00"
# Author: Claude
# Filename: _pdf_downloader.py

"""
PDF downloader for scientific papers.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import re
from urllib.parse import urlparse, quote

from ._paper import Paper


logger = logging.getLogger(__name__)


class PDFDownloader:
    """Download PDFs for scientific papers."""
    
    def __init__(
        self,
        download_dir: Optional[Path] = None,
        timeout: int = 30,
        max_concurrent: int = 3,
    ):
        """Initialize PDF downloader.
        
        Parameters
        ----------
        download_dir : Path, optional
            Directory to save PDFs (default: current directory)
        timeout : int
            Download timeout in seconds
        max_concurrent : int
            Maximum concurrent downloads
        """
        self.download_dir = Path(download_dir) if download_dir else Path.cwd()
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        
        # Headers for requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SciTeX Scholar/1.0; +https://github.com/ywatanabe/scitex)"
        }
    
    async def download_paper(
        self,
        paper: Paper,
        session: Optional[aiohttp.ClientSession] = None,
        force: bool = False,
    ) -> Optional[Path]:
        """Download PDF for a single paper.
        
        Parameters
        ----------
        paper : Paper
            Paper to download
        session : aiohttp.ClientSession, optional
            Session for connection pooling
        force : bool
            Force re-download even if file exists
        
        Returns
        -------
        Path or None
            Path to downloaded PDF, or None if failed
        """
        # Check if already has PDF
        if paper.pdf_path and paper.pdf_path.exists() and not force:
            logger.info(f"PDF already exists: {paper.pdf_path}")
            return paper.pdf_path
        
        # Generate filename
        filename = self._generate_filename(paper)
        pdf_path = self.download_dir / filename
        
        # Check if already downloaded
        if pdf_path.exists() and not force:
            paper.pdf_path = pdf_path
            logger.info(f"PDF already downloaded: {pdf_path}")
            return pdf_path
        
        # Get PDF URL
        pdf_url = self._get_pdf_url(paper)
        if not pdf_url:
            logger.warning(f"No PDF URL available for: {paper.title}")
            return None
        
        # Download
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            logger.info(f"Downloading PDF from: {pdf_url}")
            
            async with session.get(
                pdf_url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Verify it's a PDF
                    if not content.startswith(b"%PDF"):
                        logger.error(f"Downloaded content is not a PDF for: {paper.title}")
                        return None
                    
                    # Save PDF
                    with open(pdf_path, "wb") as f:
                        f.write(content)
                    
                    paper.pdf_path = pdf_path
                    logger.info(f"Downloaded PDF to: {pdf_path}")
                    return pdf_path
                else:
                    logger.error(f"Failed to download PDF (status {response.status}): {paper.title}")
                    return None
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout downloading PDF: {paper.title}")
            return None
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
        finally:
            if close_session:
                await session.close()
    
    async def download_papers(
        self,
        papers: List[Paper],
        force: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Path]:
        """Download PDFs for multiple papers.
        
        Parameters
        ----------
        papers : List[Paper]
            Papers to download
        force : bool
            Force re-download even if files exist
        progress_callback : callable, optional
            Callback function(completed, total)
        
        Returns
        -------
        Dict[str, Path]
            Mapping of paper identifiers to PDF paths
        """
        results = {}
        
        # Create semaphore for concurrent downloads
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_semaphore(paper):
            async with semaphore:
                path = await self.download_paper(paper, session, force)
                if path:
                    results[paper.get_identifier()] = path
                
                if progress_callback:
                    progress_callback(len(results), len(papers))
                
                return path
        
        # Download all papers
        async with aiohttp.ClientSession() as session:
            tasks = [download_with_semaphore(paper) for paper in papers]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def _generate_filename(self, paper: Paper) -> str:
        """Generate filename for PDF."""
        # Clean title for filename
        title = re.sub(r"[^\w\s-]", "", paper.title)
        title = re.sub(r"[-\s]+", "-", title)
        title = title[:100]  # Limit length
        
        # Add year if available
        if paper.year:
            filename = f"{paper.year}_{title}.pdf"
        else:
            filename = f"{title}.pdf"
        
        return filename
    
    def _get_pdf_url(self, paper: Paper) -> Optional[str]:
        """Get PDF URL for a paper."""
        # Check metadata for PDF URL
        if paper.metadata and "pdf_url" in paper.metadata:
            return paper.metadata["pdf_url"]
        
        # Source-specific URL generation
        if paper.source == "arxiv" and paper.arxiv_id:
            # arXiv PDF URL
            return f"https://arxiv.org/pdf/{paper.arxiv_id}.pdf"
        
        elif paper.source == "pubmed" and paper.pmid:
            # PubMed Central PDF (if available)
            # Note: This requires checking PMC availability
            return self._get_pmc_pdf_url(paper.pmid)
        
        elif paper.doi:
            # Try Sci-Hub (for educational purposes only)
            # Note: Use responsibly and check local regulations
            return f"https://sci-hub.se/{paper.doi}"
        
        return None
    
    def _get_pmc_pdf_url(self, pmid: str) -> Optional[str]:
        """Get PMC PDF URL from PMID (if available)."""
        # This would require an API call to check PMC availability
        # For now, return None
        # In a full implementation, you would:
        # 1. Query PMC to check if full text is available
        # 2. Get the PMC ID
        # 3. Construct the PDF URL
        return None
    
    async def download_from_url(
        self,
        url: str,
        filename: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> Optional[Path]:
        """Download PDF from a direct URL.
        
        Parameters
        ----------
        url : str
            PDF URL
        filename : str, optional
            Filename to save as
        session : aiohttp.ClientSession, optional
            Session for connection pooling
        
        Returns
        -------
        Path or None
            Path to downloaded PDF
        """
        if not filename:
            # Extract filename from URL
            parsed = urlparse(url)
            filename = Path(parsed.path).name
            if not filename.endswith(".pdf"):
                filename = "downloaded_paper.pdf"
        
        pdf_path = self.download_dir / filename
        
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            async with session.get(
                url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save PDF
                    with open(pdf_path, "wb") as f:
                        f.write(content)
                    
                    logger.info(f"Downloaded PDF to: {pdf_path}")
                    return pdf_path
                else:
                    logger.error(f"Failed to download from {url} (status {response.status})")
                    return None
        
        except Exception as e:
            logger.error(f"Error downloading from {url}: {e}")
            return None
        finally:
            if close_session:
                await session.close()


# Example usage
if __name__ == "__main__":
    async def main():
        # Create downloader
        downloader = PDFDownloader(download_dir=Path("./papers"))
        
        # Example paper
        paper = Paper(
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer", "et al."],
            abstract="The dominant sequence transduction models...",
            source="arxiv",
            year=2017,
            arxiv_id="1706.03762",
        )
        
        # Download single paper
        pdf_path = await downloader.download_paper(paper)
        if pdf_path:
            print(f"Downloaded to: {pdf_path}")
        
        # Download from URL
        url = "https://arxiv.org/pdf/1706.03762.pdf"
        path = await downloader.download_from_url(url, "attention_paper.pdf")
        if path:
            print(f"Downloaded from URL to: {path}")
    
    # Run example
    asyncio.run(main())