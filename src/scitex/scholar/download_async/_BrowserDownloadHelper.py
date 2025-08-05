#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download_async/_BrowserDownloadHelper.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download_async/_BrowserDownloadHelper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Browser download_async helper for papers requiring authentication.

Opens multiple paper URLs in browser tabs for efficient manual download_async.
"""

import json
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from scitex import logging
from ..lookup import get_default_lookup
from .._ScholarAPI import ScholarAPI
from ..open_url import OpenURLResolver

logger = logging.getLogger(__name__)


class BrowserDownloadHelper:
    """Helper for opening papers in browser for manual download_async."""
    
    def __init__(self, library_name: str = "default", 
                 batch_size: int = 10,
                 delay_between_batches: float = 5.0):
        """Initialize browser download_async helper.
        
        Args:
            library_name: Library to use
            batch_size: Number of tabs to open at once
            delay_between_batches: Seconds to wait between batches
        """
        self.library_name = library_name
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        
        self.api = ScholarAPI(library_name)
        self.lookup = get_default_lookup()
        self.openurl = OpenURLResolver()
        
        # Session tracking
        scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
        self.session_dir = scitex_dir / "scholar" / "download_async_sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
    def create_download_async_session(self, max_papers: Optional[int] = None) -> str:
        """Create a new download_async session for papers without PDFs.
        
        Args:
            max_papers: Maximum number of papers to include
            
        Returns:
            Session ID
        """
        # Get papers needing PDFs
        papers_needing_pdf = self.api.get_papers_needing_pdf()
        
        if max_papers:
            papers_needing_pdf = papers_needing_pdf[:max_papers]
            
        if not papers_needing_pdf:
            logger.info("No papers need PDFs!")
            return None
            
        # Create session
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_path = self.session_dir / f"session_{session_id}.json"
        
        # Prepare paper URLs
        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "total_papers": len(papers_needing_pdf),
            "batch_size": self.batch_size,
            "papers": []
        }
        
        logger.info(f"Preparing URLs for {len(papers_needing_pdf)} papers...")
        
        for i, paper in enumerate(papers_needing_pdf):
            paper_info = {
                "index": i,
                "storage_key": self.lookup.lookup_by_doi(paper.doi) if paper.doi else None,
                "doi": paper.doi,
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "urls": []
            }
            
            # Add DOI URL if available
            if paper.doi:
                paper_info["urls"].append({
                    "type": "doi",
                    "url": f"https://doi.org/{paper.doi}"
                })
                
                # Try OpenURL resolution
                try:
                    openurl_result = self.openurl.resolve(paper.doi)
                    if openurl_result and openurl_result.get("url"):
                        paper_info["urls"].append({
                            "type": "openurl",
                            "url": openurl_result["url"]
                        })
                except Exception as e:
                    logger.debug(f"OpenURL resolution failed for {paper.doi}: {e}")
                    
            # Add PDF URL if available
            if paper.pdf_url:
                paper_info["urls"].append({
                    "type": "pdf_direct",
                    "url": paper.pdf_url
                })
                
            # Add Google Scholar search as fallback
            if paper.title:
                scholar_query = quote(f'"{paper.title}"')
                paper_info["urls"].append({
                    "type": "scholar_search",
                    "url": f"https://scholar.google.com/scholar?q={scholar_query}"
                })
                
            session_data["papers"].append(paper_info)
            
        # Save session
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        logger.info(f"Created download_async session: {session_id}")
        logger.info(f"Session file: {session_path}")
        
        return session_id
        
    def open_batch(self, session_id: str, batch_index: int = 0,
                   url_priority: List[str] = None) -> bool:
        """Open a batch of paper URLs in browser tabs.
        
        Args:
            session_id: Session ID
            batch_index: Which batch to open (0-based)
            url_priority: Preferred URL types in order (default: ["openurl", "doi", "pdf_direct", "scholar_search"])
            
        Returns:
            Success status
        """
        if url_priority is None:
            url_priority = ["openurl", "doi", "pdf_direct", "scholar_search"]
            
        # Load session
        session_path = self.session_dir / f"session_{session_id}.json"
        if not session_path.exists():
            logger.error(f"Session not found: {session_id}")
            return False
            
        with open(session_path, 'r') as f:
            session_data = json.load(f)
            
        # Calculate batch range
        start_idx = batch_index * self.batch_size
        end_idx = min(start_idx + self.batch_size, len(session_data["papers"]))
        
        if start_idx >= len(session_data["papers"]):
            logger.info("No more papers in this session")
            return False
            
        batch_papers = session_data["papers"][start_idx:end_idx]
        
        logger.info(f"Opening batch {batch_index + 1} ({len(batch_papers)} papers)...")
        
        # Open URLs in browser
        for paper in batch_papers:
            # Find best URL based on priority
            best_url = None
            for url_type in url_priority:
                for url_info in paper["urls"]:
                    if url_info["type"] == url_type:
                        best_url = url_info["url"]
                        break
                if best_url:
                    break
                    
            if best_url:
                logger.info(f"Opening: {paper['title'][:50]}...")
                logger.info(f"  URL: {best_url}")
                webbrowser.open_new_tab(best_url)
                time.sleep(0.5)  # Small delay between tabs
            else:
                logger.warning(f"No URL found for: {paper['title'][:50]}...")
                
        logger.info(f"Opened {len(batch_papers)} papers in browser")
        logger.info(f"Next batch: {batch_index + 1}")
        
        return True
        
    def generate_download_async_html(self, session_id: str) -> Path:
        """Generate HTML page with all paper links for manual download_async.
        
        Args:
            session_id: Session ID
            
        Returns:
            Path to generated HTML file
        """
        # Load session
        session_path = self.session_dir / f"session_{session_id}.json"
        if not session_path.exists():
            logger.error(f"Session not found: {session_id}")
            return None
            
        with open(session_path, 'r') as f:
            session_data = json.load(f)
            
        # Generate HTML
        html_path = self.session_dir / f"download_async_helper_{session_id}.html"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>SciTeX Scholar - Download Helper</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .paper {{ 
            margin-bottom: 20px; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .paper.download_asynced {{ 
            background-color: #e8f5e9;
            opacity: 0.7;
        }}
        .title {{ 
            font-weight: bold; 
            margin-bottom: 5px;
            color: #1976d2;
        }}
        .authors {{ 
            color: #666; 
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .links {{ margin-top: 10px; }}
        .links a {{ 
            margin-right: 15px; 
            padding: 5px 10px;
            background-color: #1976d2;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .links a:hover {{ background-color: #1565c0; }}
        .links a.openurl {{ background-color: #4caf50; }}
        .links a.openurl:hover {{ background-color: #45a049; }}
        .storage-key {{ 
            float: right; 
            color: #999; 
            font-family: monospace;
            font-size: 0.9em;
        }}
        .batch-header {{
            background-color: #333;
            color: white;
            padding: 10px;
            margin: 20px 0 10px 0;
            border-radius: 3px;
        }}
        .stats {{
            background-color: #f0f0f0;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .checkbox {{
            margin-right: 10px;
        }}
        #progress {{
            position: fixed;
            top: 10px;
            right: 10px;
            background-color: #333;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 1.2em;
        }}
    </style>
    <script>
        function updateProgress() {{
            const total = document.querySelectorAll('.paper').length;
            const download_asynced = document.querySelectorAll('.paper.download_asynced').length;
            document.getElementById('progress').textContent = `Downloaded: ${{download_asynced}}/${{total}}`;
        }}
        
        function markDownloaded(index) {{
            const paper = document.getElementById(`paper-${{index}}`);
            paper.classList.toggle('download_asynced');
            updateProgress();
            
            // Save state to localStorage
            const download_asynced = [];
            document.querySelectorAll('.paper.download_asynced').forEach(p => {{
                download_asynced.push(p.id);
            }});
            localStorage.setItem('download_asynced-{session_id}', JSON.stringify(download_asynced));
        }}
        
        // Restore state on page load
        window.onload = function() {{
            const saved = localStorage.getItem('download_asynced-{session_id}');
            if (saved) {{
                const download_asynced = JSON.parse(saved);
                download_asynced.forEach(id => {{
                    document.getElementById(id)?.classList.add('download_asynced');
                }});
            }}
            updateProgress();
        }};
    </script>
</head>
<body>
    <h1>SciTeX Scholar - Download Helper</h1>
    <div id="progress">Downloaded: 0/{len(session_data['papers'])}</div>
    
    <div class="stats">
        <p><strong>Session ID:</strong> {session_id}</p>
        <p><strong>Created:</strong> {session_data['created_at']}</p>
        <p><strong>Total Papers:</strong> {session_data['total_papers']}</p>
        <p><strong>Instructions:</strong> Click on the links to open papers in your authenticate_async browser. 
        Check the box when download_asynced. Your progress is automatically saved.</p>
    </div>
"""
        
        # Add papers by batch
        for batch_idx in range(0, len(session_data["papers"]), self.batch_size):
            batch_num = batch_idx // self.batch_size + 1
            html_content += f'<div class="batch-header">Batch {batch_num}</div>\n'
            
            for paper in session_data["papers"][batch_idx:batch_idx + self.batch_size]:
                idx = paper["index"]
                title = paper["title"] or "Unknown Title"
                authors = ", ".join(paper["authors"][:3]) if paper["authors"] else "Unknown Authors"
                if paper["authors"] and len(paper["authors"]) > 3:
                    authors += " et al."
                    
                html_content += f'''
    <div class="paper" id="paper-{idx}">
        <input type="checkbox" class="checkbox" onclick="markDownloaded({idx})">
        <span class="storage-key">{paper.get("storage_key", "")}</span>
        <div class="title">{title}</div>
        <div class="authors">{authors} ({paper.get("year", "?")})</div>
        <div class="links">
'''
                
                for url_info in paper["urls"]:
                    url_type = url_info["type"]
                    url = url_info["url"]
                    label = {
                        "doi": "DOI",
                        "openurl": "OpenURL (UniMelb)",
                        "pdf_direct": "Direct PDF",
                        "scholar_search": "Google Scholar"
                    }.get(url_type, url_type)
                    
                    html_content += f'            <a href="{url}" target="_blank" class="{url_type}">{label}</a>\n'
                    
                html_content += '''        </div>
    </div>
'''
                
        html_content += """
</body>
</html>
"""
        
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        logger.info(f"Generated download_async helper HTML: {html_path}")
        return html_path
        
    def open_download_async_helper(self, session_id: str) -> bool:
        """Generate and open download_async helper HTML in browser.
        
        Args:
            session_id: Session ID
            
        Returns:
            Success status
        """
        html_path = self.generate_download_async_html(session_id)
        if html_path:
            webbrowser.open(f"file://{html_path}")
            return True
        return False
        
    def list_sessions(self) -> List[Dict]:
        """List all download_async sessions."""
        sessions = []
        
        for session_file in sorted(self.session_dir.glob("session_*.json"), reverse=True):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data["session_id"],
                        "created_at": data["created_at"],
                        "total_papers": data["total_papers"],
                        "file": session_file
                    })
            except Exception as e:
                logger.error(f"Failed to read session {session_file}: {e}")
                
        return sessions


if __name__ == "__main__":
    print("SciTeX Scholar - Browser Download Helper")
    print("=" * 60)
    
    helper = BrowserDownloadHelper()
    
    print("\nUsage:")
    print("""
    # Create download_async session for papers without PDFs
    session_id = helper.create_download_async_session(max_papers=50)
    
    # Option 1: Open papers in batches
    helper.open_batch(session_id, batch_index=0)  # First 10 papers
    helper.open_batch(session_id, batch_index=1)  # Next 10 papers
    
    # Option 2: Generate HTML helper page
    helper.open_download_async_helper(session_id)
    
    # List existing sessions
    sessions = helper.list_sessions()
    """)

# EOF