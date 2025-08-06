#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 14:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for browser download helper.

Usage:
    python -m scitex.scholar.download create [--max-papers N]
    python -m scitex.scholar.download open <session_id> [--batch N]
    python -m scitex.scholar.download html <session_id>
    python -m scitex.scholar.download list
"""

import argparse
import sys
from datetime import datetime

from scitex import logging
from ._BrowserDownloadHelper import BrowserDownloadHelper

logger = logging.getLogger(__name__)


def main():
    """Main entry point for download helper CLI."""
    parser = argparse.ArgumentParser(
        description="SciTeX Scholar - Browser Download Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create a new download session for up to 50 papers
    python -m scitex.scholar.download create --max-papers 50
    
    # Open first batch in browser tabs
    python -m scitex.scholar.download open 20250801_141500 --batch 0
    
    # Generate and open HTML helper page
    python -m scitex.scholar.download html 20250801_141500
    
    # List all sessions
    python -m scitex.scholar.download list
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new download session")
    create_parser.add_argument(
        "--max-papers", type=int, default=None,
        help="Maximum number of papers to include"
    )
    create_parser.add_argument(
        "--library", default="default",
        help="Library name (default: default)"
    )
    
    # Open command
    open_parser = subparsers.add_parser("open", help="Open papers in browser")
    open_parser.add_argument("session_id", help="Session ID")
    open_parser.add_argument(
        "--batch", type=int, default=0,
        help="Batch index to open (default: 0)"
    )
    open_parser.add_argument(
        "--priority", nargs="+",
        default=["openurl", "doi", "pdf_direct", "scholar_search"],
        help="URL priority order"
    )
    
    # HTML command
    html_parser = subparsers.add_parser("html", help="Generate and open HTML helper")
    html_parser.add_argument("session_id", help="Session ID")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List download sessions")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Execute command
    if args.command == "create":
        helper = BrowserDownloadHelper(library_name=args.library)
        session_id = helper.create_download_session(max_papers=args.max_papers)
        
        if session_id:
            print(f"\nCreated download session: {session_id}")
            print(f"\nNext steps:")
            print(f"  1. Open papers in browser:")
            print(f"     python -m scitex.scholar.download open {session_id}")
            print(f"  2. Or use HTML helper:")
            print(f"     python -m scitex.scholar.download html {session_id}")
            
    elif args.command == "open":
        helper = BrowserDownloadHelper()
        success = helper.open_batch(
            args.session_id, 
            batch_index=args.batch,
            url_priority=args.priority
        )
        
        if success:
            print(f"\nOpened batch {args.batch} in browser")
            print(f"To open next batch:")
            print(f"  python -m scitex.scholar.download open {args.session_id} --batch {args.batch + 1}")
            
    elif args.command == "html":
        helper = BrowserDownloadHelper()
        success = helper.open_download_helper(args.session_id)
        
        if success:
            print(f"\nOpened download helper in browser")
            print(f"Check the boxes as you download each paper.")
            print(f"Your progress is automatically saved.")
            
    elif args.command == "list":
        helper = BrowserDownloadHelper()
        sessions = helper.list_sessions()
        
        if not sessions:
            print("No download sessions found")
        else:
            print(f"\nFound {len(sessions)} download session(s):\n")
            print(f"{'Session ID':<20} {'Created':<20} {'Papers':<10}")
            print("-" * 60)
            
            for session in sessions:
                created = datetime.fromisoformat(session["created_at"])
                created_str = created.strftime("%Y-%m-%d %H:%M")
                print(f"{session['session_id']:<20} {created_str:<20} {session['total_papers']:<10}")
                
    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF