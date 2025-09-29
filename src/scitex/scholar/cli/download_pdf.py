#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-16 23:56:08 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/cli/download_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/download_pdf.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line interface for paywalled PDF downloads.

Usage:
    python -m scitex.scholar.download bibtex <file.bib> [--project NAME]
    python -m scitex.scholar.download paper --doi <DOI> [--title TITLE]
    python -m scitex.scholar.download paper --url <URL>
    python -m scitex.scholar.download info
"""

import argparse
import sys

from scitex import logging
from scitex.scholar.core import Paper

logger = logging.getLogger(__name__)


def create_parser():
    """Create argument parser for download_pdf command."""
    parser = argparse.ArgumentParser(
        description="Download PDFs from paywalled journals using institutional authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Download PDFs from BibTeX file
python -m scitex.scholar download bibtex pac.bib --project myproject

# Download single paper by DOI
python -m scitex.scholar download paper --doi 10.1038/nature12345

# Download single paper by URL
python -m scitex.scholar download paper --url https://www.nature.com/articles/nature12345

# Show system info
python -m scitex.scholar download info""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # BibTeX command
    bibtex_parser = subparsers.add_parser(
        "bibtex", help="Download PDFs from BibTeX file"
    )
    bibtex_parser.add_argument("file", help="BibTeX file path")
    bibtex_parser.add_argument(
        "--project",
        default="default",
        help="Project name for organization (default: default)",
    )
    bibtex_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent downloads (default: 3)",
    )

    # Paper command
    paper_parser = subparsers.add_parser("paper", help="Download single paper")
    paper_group = paper_parser.add_mutually_exclusive_group(required=True)
    paper_group.add_argument("--doi", help="DOI of the paper")
    paper_group.add_argument("--url", help="URL of the paper")
    paper_parser.add_argument(
        "--title", help="Paper title (for DOI-based downloads)"
    )
    paper_parser.add_argument(
        "--project",
        default="default",
        help="Project name for organization (default: default)",
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")

    return parser


def main():
    """Main entry point for paywalled PDF download CLI."""
    #     parser = argparse.ArgumentParser(
    #         description="SciTeX Scholar - Paywalled PDF Downloader",
    #         formatter_class=argparse.RawDescriptionHelpFormatter,
    #         epilog="""
    # Examples:
    #     # Download PDFs from BibTeX file
    #     python -m scitex.scholar.download bibtex pac.bib --project myproject

    #     # Download single paper by DOI
    #     python -m scitex.scholar.download paper --doi 10.1038/nature12345

    #     # Download single paper by URL
    #     python -m scitex.scholar.download paper --url https://www.nature.com/articles/nature12345

    #     # Show system info
    #     python -m scitex.scholar.download info
    #         """,
    #     )

    parser = create_parser()

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # BibTeX command
    bibtex_parser = subparsers.add_parser(
        "bibtex", help="Download PDFs from BibTeX file"
    )
    bibtex_parser.add_argument("file", help="BibTeX file path")
    bibtex_parser.add_argument(
        "--project",
        default="default",
        help="Project name for organization (default: default)",
    )
    bibtex_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent downloads (default: 3)",
    )

    # Paper command
    paper_parser = subparsers.add_parser("paper", help="Download single paper")
    paper_group = paper_parser.add_mutually_exclusive_group(required=True)
    paper_group.add_argument("--doi", help="DOI of the paper")
    paper_group.add_argument("--url", help="URL of the paper")
    paper_parser.add_argument(
        "--title", help="Paper title (for DOI-based downloads)"
    )
    paper_parser.add_argument(
        "--project",
        default="default",
        help="Project name for organization (default: default)",
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == "bibtex":
        import asyncio
        from pathlib import Path

        downloader = SmartScholarPDFDownloader()
        bibtex_path = Path(args.file)

        if not bibtex_path.exists():
            print(f"Error: BibTeX file not found: {bibtex_path}")
            return 1

        print(f"\n🎯 SciTeX Scholar - Paywalled PDF Downloader")
        print(f"📄 Processing: {bibtex_path}")
        print(f"🏢 Project: {args.project}")
        print(f"🔐 Focus: Institutional authentication for paywalled content")
        print(f"⚡ Concurrent downloads: {args.max_concurrent}")

        try:
            results = downloader.download_from_bibtex(
                bibtex_path, max_concurrent=args.max_concurrent
            )

            success_count = sum(1 for s, _ in results.values() if s)
            print(f"\n✅ Downloaded {success_count}/{len(results)} PDFs")
            print(f"📁 Files saved to Scholar library")

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    elif args.command == "paper":
        import asyncio

        downloader = SmartScholarPDFDownloader()

        # Create paper object
        if args.doi:
            paper = Paper(title=args.title or "Unknown", doi=args.doi)
        else:
            paper = Paper(title=args.title or "Unknown", url=args.url)

        print(f"\n🎯 SciTeX Scholar - Paywalled PDF Downloader")
        print(f"📄 Paper: {paper.title}")
        print(f"🔗 {'DOI' if args.doi else 'URL'}: {args.doi or args.url}")
        print(f"🏢 Project: {args.project}")
        print(f"🔐 Using institutional authentication")

        try:
            success, pdf_path = asyncio.run(downloader.download_single(paper))

            if success and pdf_path:
                print(f"\n✅ Downloaded successfully: {pdf_path}")
            else:
                print(f"\n❌ Download failed")
                return 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    elif args.command == "info":
        downloader = SmartScholarPDFDownloader()
        info = downloader.get_strategy_info()

        print(f"\n🎯 SciTeX Scholar - Paywalled PDF Downloader")
        print(f"=" * 50)
        print(f"Strategy: {info['strategy']}")
        print(f"Focus: {info['focus']}")
        print(f"Authentication: {info['authentication']}")
        print(f"Extensions: {', '.join(info['extensions'])}")
        print(f"Zotero Translators: {info['zotero_translators']}")
        print(f"=" * 50)
        print(
            f"\n💡 This tool specializes in accessing paywalled academic content"
        )
        print(f"   that requires institutional authentication.")
        print(
            f"\n🏆 Competitive Advantage: Access content others can't reach!"
        )
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
