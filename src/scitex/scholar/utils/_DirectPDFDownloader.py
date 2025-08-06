#!/usr/bin/env python3
"""
Direct PDF Downloader with Screenshot Integration

Simple approach: Jump directly to the PDF URL with authenticate_async browser
and save the PDF response directly, bypassing browser PDF viewer complexity.

Enhanced with automatic screenshot capture for debugging and verification.
"""

import asyncio
from pathlib import Path
from typing import List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DirectPDFDownloader:
    """
    Downloads PDFs by jumping directly to PDF URLs with authenticate_async browser context.
    
    This bypasses the complexity of extracting PDFs from browser viewers by
    directly navigating to the PDF URL and capturing the response.
    
    Enhanced with automatic screenshot capture for debugging and verification.
    """
    
    def __init__(self, capture_screenshots: bool = True):
        """
        Initialize DirectPDFDownloader with screenshot capabilities.
        
        Args:
            capture_screenshots: Whether to automatically capture screenshots during downloads
        """
        self.capture_screenshots = capture_screenshots
    
    async def _capture_download_screenshot(self, page, download_path: Path, stage: str) -> Optional[str]:
        """
        Capture screenshot during PDF download process.
        
        Args:
            page: Playwright page object
            download_path: Path where PDF is being download
            stage: Stage of download (e.g., 'before_navigation', 'after_navigation', 'error')
        
        Returns:
            Path to screenshot file if successful, None otherwise
        """
        if not self.capture_screenshots:
            return None
        
        try:
            # Generate screenshot filename based on PDF name and stage
            timestamp = datetime.now().strftime("%H%M%S")
            pdf_name = download_path.stem
            screenshot_name = f"{pdf_name}_{stage}_{timestamp}.png"
            screenshot_path = download_path.parent / screenshot_name
            
            # Capture screenshot - use full page for maximum information
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            screenshot_size = screenshot_path.stat().st_size / 1024  # KB
            logger.info(f"📸 Screenshot captured: {screenshot_name} ({screenshot_size:.1f} KB)")
            
            return str(screenshot_path)
            
        except Exception as e:
            logger.warning(f"Failed to capture screenshot at {stage}: {e}")
            return None
    
    async def download_pdf_async_direct(self, 
                                 page, 
                                 pdf_url: str, 
                                 download_path: Path, 
                                 timeout: int = 30000) -> Tuple[bool, Optional[str]]:
        """
        Download PDF by jumping directly to the PDF URL.
        
        Args:
            page: Playwright page with authenticate_async context
            pdf_url: Direct URL to the PDF
            download_path: Local path to save the PDF
            timeout: Timeout in milliseconds
            
        Returns:
            (success: bool, error_message: Optional[str])
        """
        try:
            # Ensure download directory exists
            download_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"🎯 Jumping directly to PDF URL: {pdf_url}")
            logger.info(f"📥 Target path: {download_path}")
            
            # Capture initial screenshot before navigation
            await self._capture_download_screenshot(page, download_path, "before_navigation")
            
            # Method 1: Try to capture PDF response directly
            pdf_content = None
            content_length = 0
            
            async def handle_response(response):
                nonlocal pdf_content, content_length
                if response.url == pdf_url:
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"📄 Response content-type: {content_type}")
                    
                    if 'application/pdf' in content_type:
                        try:
                            pdf_content = await response.body()
                            content_length = len(pdf_content)
                            logger.info(f"✅ Captured PDF content: {content_length} bytes")
                        except Exception as capture_error:
                            logger.warning(f"Failed to capture PDF content: {capture_error}")
            
            # Set up response handler
            page.on('response', handle_response)
            
            # Navigate directly to PDF URL  
            try:
                await page.goto(pdf_url, wait_until='domcontentloaded', timeout=timeout)
                await page.wait_for_timeout(3000)  # Wait for response handler
                
                # Capture screenshot after navigation
                await self._capture_download_screenshot(page, download_path, "after_navigation")
                
            except Exception as nav_error:
                logger.debug(f"Navigation completed with: {nav_error}")
                # Capture error screenshot
                await self._capture_download_screenshot(page, download_path, "navigation_error")
            
            # Remove response handler
            try:
                page.remove_listener('response', handle_response)
            except:
                pass  # Ignore if handler was not attached
            
            # Save captured PDF content
            if pdf_content and content_length > 1000:  # At least 1KB
                with open(download_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Verify saved file
                if download_path.exists():
                    file_size = download_path.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    
                    logger.info(f"✅ PDF saved successfully: {download_path.name}")
                    logger.info(f"📊 File size: {size_mb:.2f} MB ({file_size:,} bytes)")
                    
                    # Capture success screenshot
                    await self._capture_download_screenshot(page, download_path, "download_success")
                    
                    return True, None
                else:
                    return False, "File was not saved to disk"
            
            # Method 2: Fallback - use browser's built-in download
            logger.info("🔄 Trying fallback download method...")
            
            try:
                # Set up download event handler
                download_promise = page.wait_for_event('download', timeout=10000)
                
                # Trigger download (page might already be loaded)
                await page.evaluate('''
                    () => {
                        // Try to trigger download via various methods
                        if (document.querySelector('a[download]')) {
                            document.querySelector('a[download]').click();
                        } else {
                            // Force download by creating temporary link
                            const link = document.createElement('a');
                            link.href = window.location.href;
                            link.download = '';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }
                    }
                ''')
                
                # Wait for download
                download = await download_promise
                await download.save_as(str(download_path))
                
                if download_path.exists() and download_path.stat().st_size > 1000:
                    file_size = download_path.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    logger.info(f"✅ Fallback download successful: {size_mb:.2f} MB")
                    
                    # Capture fallback success screenshot
                    await self._capture_download_screenshot(page, download_path, "fallback_success")
                    
                    return True, None
                    
            except Exception as fallback_error:
                logger.debug(f"Fallback download failed: {fallback_error}")
            
            # Method 3: HTTP request with browser cookies (last resort)
            logger.info("🔄 Trying HTTP request with browser cookies...")
            
            try:
                import requests
                
                # Get cookies from browser
                cookies = await page.context.cookies()
                
                # Create requests session with cookies
                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(
                        cookie['name'], 
                        cookie['value'],
                        domain=cookie['domain'],
                        path=cookie.get('path', '/')
                    )
                
                # Add headers to mimic browser
                headers = {
                    'User-Agent': await page.evaluate('navigator.userAgent'),
                    'Accept': 'application/pdf,application/octet-stream,*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': page.url
                }
                
                # Make HTTP request
                response = session.get(pdf_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        with open(download_path, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = len(response.content)
                        if file_size > 1000:
                            size_mb = file_size / (1024 * 1024)
                            logger.info(f"✅ HTTP download successful: {size_mb:.2f} MB")
                            return True, None
                
            except Exception as http_error:
                logger.debug(f"HTTP download failed: {http_error}")
            
            return False, "All download methods failed"
            
        except Exception as e:
            error_msg = f"Direct PDF download failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    async def download_multiple_pdfs(self, 
                                   page, 
                                   pdf_urls: List[str], 
                                   download_dir: Path,
                                   filename_pattern: str = "{index}_{doi}.pdf") -> List[Tuple[str, Path, bool, Optional[str]]]:
        """
        Download multiple PDFs directly.
        
        Args:
            page: Playwright page with authenticate_async context
            pdf_urls: List of PDF URLs to download
            download_dir: Directory to save PDFs
            filename_pattern: Pattern for filenames
            
        Returns:
            List of (pdf_url, file_path, success, error_message) tuples
        """
        results = []
        
        for i, pdf_url in enumerate(pdf_urls):
            try:
                # Generate filename
                is_main = '/pdf/' in pdf_url and 'suppl' not in pdf_url
                doi_part = pdf_url.split('/')[-1] if '/' in pdf_url else f"pdf_{i}"
                
                if is_main:
                    filename = f"{doi_part}_main.pdf"
                elif 'suppl' in pdf_url:
                    filename = f"{doi_part}_supplement_{i}.pdf"
                else:
                    filename = f"{doi_part}_{i}.pdf"
                
                file_path = download_dir / filename
                
                logger.info(f"📄 Downloading PDF {i+1}/{len(pdf_urls)}: {filename}")
                
                # Download the PDF
                success, error = await self.download_pdf_async_direct(page, pdf_url, file_path)
                
                results.append((pdf_url, file_path, success, error))
                
                if success:
                    logger.info(f"✅ Downloaded: {filename}")
                else:
                    logger.warning(f"❌ Failed: {filename} - {error}")
                
                # Small delay between downloads
                await asyncio.sleep(1)
                
            except Exception as e:
                error_msg = f"Error downloading {pdf_url}: {str(e)}"
                logger.error(error_msg)
                results.append((pdf_url, None, False, error_msg))
        
        return results
    
    def create_download_report(self, results: List[Tuple[str, Path, bool, Optional[str]]]) -> str:
        """Create a download report."""
        successful = [r for r in results if r[2]]
        failed = [r for r in results if not r[2]]
        
        report = f"📊 Direct PDF Download Report\n"
        report += f"{'='*50}\n\n"
        report += f"Total PDFs: {len(results)}\n"
        report += f"✅ Successful: {len(successful)}\n"
        report += f"❌ Failed: {len(failed)}\n\n"
        
        if successful:
            report += f"✅ Successfully Downloaded:\n"
            for pdf_url, file_path, success, error in successful:
                if file_path and file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    report += f"  • {file_path.name} ({size_mb:.2f} MB)\n"
        
        if failed:
            report += f"\n❌ Failed Downloads:\n"
            for pdf_url, file_path, success, error in failed:
                report += f"  • {pdf_url[:60]}... - {error}\n"
        
        return report


# Convenience function
async def download_pdf_asyncs_direct(page, pdf_urls: List[str], download_dir: Path) -> List[Tuple[str, Path, bool, Optional[str]]]:
    """Convenience function for direct PDF downloads."""
    downloader = DirectPDFDownloader()
    return await downloader.download_multiple_pdfs(page, pdf_urls, download_dir)