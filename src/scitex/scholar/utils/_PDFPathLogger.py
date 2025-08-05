#!/usr/bin/env python3
"""
PDF Path Logger

Utility to log and save detected PDF paths for later processing.
This allows us to capture PDF URLs even when direct download_async fails.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PDFPathLogger:
    """
    Logger for detected PDF paths and metadata.
    
    Saves PDF detection results to various formats for later processing,
    analysis, or manual download_async.
    """
    
    def __init__(self, base_dir: Path = None):
        """Initialize PDF path logger."""
        self.base_dir = base_dir or Path("download_asyncs")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped log directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = self.base_dir / f"pdf_detection_logs_{timestamp}"
        self.log_dir.mkdir(exist_ok=True)
        
        # Log files
        self.json_log = self.log_dir / "detected_pdfs.json"
        self.csv_log = self.log_dir / "detected_pdfs.csv"
        self.urls_log = self.log_dir / "pdf_urls.txt"
        self.report_log = self.log_dir / "detection_report.md"
        
        # Initialize data storage
        self.detected_pdfs = []
        
        logger.info(f"PDF Path Logger initialized: {self.log_dir}")
    
    def log_detection_result(self, 
                           url: str, 
                           doi: str,
                           pdf_urls: List[str], 
                           detection_method: str,
                           translator_used: str,
                           confidence: float,
                           local_paths: List[str] = None,
                           download_async_status: List[bool] = None,
                           metadata: Dict[str, Any] = None):
        """
        Log a PDF detection result.
        
        Args:
            url: Source page URL
            doi: DOI of the paper
            pdf_urls: List of detected PDF URLs (remote)
            detection_method: Method used for detection
            translator_used: Zotero translator used
            confidence: Confidence score
            local_paths: List of local file paths (where PDFs are/should be saved)
            download_async_status: List of download_async success status for each PDF
            metadata: Additional metadata
        """
        # Ensure lists are same length
        local_paths = local_paths or [None] * len(pdf_urls)
        download_async_status = download_async_status or [False] * len(pdf_urls)
        
        # Create PDF entries with both URL and local path info
        pdf_entries = []
        for i, pdf_url in enumerate(pdf_urls):
            local_path = local_paths[i] if i < len(local_paths) else None
            download_asynced = download_async_status[i] if i < len(download_async_status) else False
            
            pdf_entries.append({
                "url": pdf_url,
                "local_path": str(local_path) if local_path else None,
                "download_asynced": download_asynced,
                "is_main": self._is_main_pdf(pdf_url),
                "is_supplementary": self._is_supplementary_pdf(pdf_url),
                "file_exists": Path(local_path).exists() if local_path else False,
                "file_size_mb": self._get_file_size_mb(local_path) if local_path else None
            })
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source_url": url,
            "doi": doi,
            "pdf_urls": pdf_urls,  # Keep for backward compatibility
            "pdf_entries": pdf_entries,  # New detailed structure
            "main_pdf_url": self._identify_main_pdf(pdf_urls),
            "main_pdf_path": self._identify_main_pdf_path(pdf_entries),
            "supplementary_pdfs": self._identify_supplementary_pdfs(pdf_urls),
            "detection_method": detection_method,
            "translator_used": translator_used,
            "confidence": confidence,
            "pdf_count": len(pdf_urls),
            "download_asynced_count": sum(entry["download_asynced"] for entry in pdf_entries),
            "total_size_mb": sum(entry["file_size_mb"] or 0 for entry in pdf_entries),
            "metadata": metadata or {}
        }
        
        self.detected_pdfs.append(entry)
        
        # Log immediately for real-time tracking
        logger.info(f"📄 Logged {len(pdf_urls)} PDFs for {doi}: {detection_method}")
        for i, pdf_url in enumerate(pdf_urls, 1):
            is_main = '/pdf/' in pdf_url and 'suppl' not in pdf_url
            marker = '🎯 MAIN' if is_main else '📎 SUPP'
            logger.info(f"  {i}. {marker} {pdf_url}")
    
    def _is_main_pdf(self, pdf_url: str) -> bool:
        """Check if a PDF URL is likely the main article."""
        return '/pdf/' in pdf_url and 'suppl' not in pdf_url and 'supplement' not in pdf_url
    
    def _is_supplementary_pdf(self, pdf_url: str) -> bool:
        """Check if a PDF URL is likely supplementary material."""
        return 'suppl' in pdf_url or 'supplement' in pdf_url or 'supporting' in pdf_url
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB, return None if file doesn't exist."""
        try:
            if file_path and Path(file_path).exists():
                return Path(file_path).stat().st_size / (1024 * 1024)
        except:
            pass
        return None
    
    def _identify_main_pdf(self, pdf_urls: List[str]) -> str:
        """Identify the main PDF from a list of URLs."""
        for url in pdf_urls:
            if self._is_main_pdf(url):
                return url
        return pdf_urls[0] if pdf_urls else ""
    
    def _identify_main_pdf_path(self, pdf_entries: List[Dict]) -> str:
        """Identify the main PDF local path from entries."""
        for entry in pdf_entries:
            if entry["is_main"] and entry["local_path"]:
                return entry["local_path"]
        return ""
    
    def _identify_supplementary_pdfs(self, pdf_urls: List[str]) -> List[str]:
        """Identify supplementary PDFs from a list of URLs."""
        return [url for url in pdf_urls if self._is_supplementary_pdf(url)]
    
    def save_all_formats(self):
        """Save logged data to all output formats."""
        self._save_json()
        self._save_csv()
        self._save_urls_list()
        self._save_markdown_report()
        
        logger.info(f"📊 Saved PDF detection results to {len(self.detected_pdfs)} entries:")
        logger.info(f"  📄 JSON: {self.json_log}")
        logger.info(f"  📊 CSV: {self.csv_log}")
        logger.info(f"  🔗 URLs: {self.urls_log}")
        logger.info(f"  📋 Report: {self.report_log}")
    
    def _save_json(self):
        """Save detection results as JSON."""
        with open(self.json_log, 'w') as f:
            json.dump({
                "detection_session": {
                    "timestamp": datetime.now().isoformat(),
                    "total_detections": len(self.detected_pdfs),
                    "total_pdfs": sum(entry["pdf_count"] for entry in self.detected_pdfs)
                },
                "detected_pdfs": self.detected_pdfs
            }, f, indent=2)
    
    def _save_csv(self):
        """Save detection results as CSV."""
        if not self.detected_pdfs:
            return
            
        with open(self.csv_log, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'timestamp', 'doi', 'source_url', 'main_pdf_url', 'main_pdf_path',
                'supplementary_count', 'total_pdfs', 'download_asynced_count', 'total_size_mb',
                'detection_method', 'translator_used', 'confidence'
            ])
            
            # Data rows
            for entry in self.detected_pdfs:
                writer.writerow([
                    entry['timestamp'],
                    entry['doi'],
                    entry['source_url'],
                    entry['main_pdf_url'],
                    entry['main_pdf_path'],
                    len(entry['supplementary_pdfs']),
                    entry['pdf_count'],
                    entry['download_asynced_count'],
                    entry['total_size_mb'],
                    entry['detection_method'],
                    entry['translator_used'],
                    entry['confidence']
                ])
    
    def _save_urls_list(self):
        """Save all PDF URLs as a simple text list."""
        with open(self.urls_log, 'w') as f:
            f.write("# Detected PDF URLs\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total entries: {len(self.detected_pdfs)}\n\n")
            
            for entry in self.detected_pdfs:
                f.write(f"## {entry['doi']}\n")
                f.write(f"# Source: {entry['source_url']}\n")
                f.write(f"# Method: {entry['detection_method']} ({entry['translator_used']})\n")
                
                for url in entry['pdf_urls']:
                    f.write(f"{url}\n")
                f.write("\n")
    
    def _save_markdown_report(self):
        """Save a human-readable markdown report."""
        with open(self.report_log, 'w') as f:
            f.write("# PDF Detection Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Detections:** {len(self.detected_pdfs)}\n")
            
            total_pdfs = sum(entry["pdf_count"] for entry in self.detected_pdfs)
            main_pdfs = sum(1 for entry in self.detected_pdfs if entry.get("main_pdf_url") or entry.get("main_pdf"))
            supp_pdfs = sum(len(entry["supplementary_pdfs"]) for entry in self.detected_pdfs)
            
            f.write(f"**Total PDFs Found:** {total_pdfs}\n")
            f.write(f"**Main Articles:** {main_pdfs}\n")
            f.write(f"**Supplementary Materials:** {supp_pdfs}\n\n")
            
            # Method statistics
            methods = {}
            for entry in self.detected_pdfs:
                method = entry['detection_method']
                methods[method] = methods.get(method, 0) + 1
            
            f.write("## Detection Methods Used\n\n")
            for method, count in methods.items():
                f.write(f"- **{method}:** {count} papers\n")
            f.write("\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            for i, entry in enumerate(self.detected_pdfs, 1):
                f.write(f"### {i}. {entry['doi']}\n\n")
                f.write(f"**Source:** {entry['source_url']}\n\n")
                f.write(f"**Detection Method:** {entry['detection_method']}\n")
                f.write(f"**Translator:** {entry['translator_used']}\n")
                f.write(f"**Confidence:** {entry['confidence']:.1%}\n")
                f.write(f"**PDFs Found:** {entry['pdf_count']}\n\n")
                
                if entry['main_pdf']:
                    f.write(f"**Main PDF:** {entry['main_pdf']}\n\n")
                
                if entry['supplementary_pdfs']:
                    f.write("**Supplementary Materials:**\n")
                    for supp in entry['supplementary_pdfs']:
                        f.write(f"- {supp}\n")
                    f.write("\n")
                
                f.write("---\n\n")
    
    def get_all_pdf_urls(self) -> List[str]:
        """Get all detected PDF URLs as a flat list."""
        all_urls = []
        for entry in self.detected_pdfs:
            all_urls.extend(entry['pdf_urls'])
        return all_urls
    
    def get_main_pdfs(self) -> List[Dict[str, str]]:
        """Get all main PDF URLs with their DOIs."""
        main_pdfs = []
        for entry in self.detected_pdfs:
            if entry['main_pdf']:
                main_pdfs.append({
                    'doi': entry['doi'],
                    'url': entry['main_pdf'],
                    'source': entry['source_url']
                })
        return main_pdfs
    
    def create_browser_helper_html(self) -> str:
        """Create an HTML file to help with manual PDF download_asyncs."""
        html_file = self.log_dir / "manual_download_async_helper.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Download Helper</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .paper {{ border: 1px solid #ccc; margin: 10px 0; padding: 15px; }}
                .main-pdf {{ background-color: #e8f5e8; font-weight: bold; }}
                .supp-pdf {{ background-color: #f0f0f0; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .doi {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .method {{ color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>PDF Download Helper</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Papers: {len(self.detected_pdfs)}</p>
            <p><strong>Instructions:</strong> Click links to open PDFs, then save manually using browser.</p>
            <hr>
        """
        
        for i, entry in enumerate(self.detected_pdfs, 1):
            html_content += f"""
            <div class="paper">
                <div class="doi">{i}. {entry['doi']}</div>
                <div class="method">Method: {entry['detection_method']} | Confidence: {entry['confidence']:.1%}</div>
                <br>
            """
            
            # Main PDF first
            if entry['main_pdf']:
                html_content += f'<div class="main-pdf">🎯 MAIN: <a href="{entry["main_pdf"]}" target="_blank">{entry["main_pdf"]}</a></div>'
            
            # Supplementary PDFs
            for supp in entry['supplementary_pdfs']:
                html_content += f'<div class="supp-pdf">📎 SUPP: <a href="{supp}" target="_blank">{supp}</a></div>'
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"📋 Created manual download_async helper: {html_file}")
        return str(html_file)


# Convenience functions
def create_pdf_logger(base_dir: Path = None) -> PDFPathLogger:
    """Create a new PDF path logger."""
    return PDFPathLogger(base_dir)


def log_pdf_detection(logger: PDFPathLogger, 
                     url: str, 
                     doi: str, 
                     pdf_urls: List[str],
                     detection_method: str,
                     translator_used: str, 
                     confidence: float,
                     metadata: Dict[str, Any] = None):
    """Convenience function to log PDF detection."""
    logger.log_detection_result(
        url, doi, pdf_urls, detection_method, 
        translator_used, confidence, metadata
    )