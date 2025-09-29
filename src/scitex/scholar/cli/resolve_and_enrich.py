#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 04:29:44 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/resolve_and_enrich.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/resolve_and_enrich.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import json
import sys
from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Resolve DOIs, abstracts, citation counts, journal IFs and assign project in SciTeX Scholar Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
# Resolve and enrich with project organization
python -m scitex.scholar resolve-and-enrich --bibtex pac.bib --project myproject

# Show project summary
python -m scitex.scholar resolve-and-enrich --project myproject --summary""",
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--bibtex", type=Path, help="BibTeX file to process"
    )
    input_group.add_argument(
        "--title", type=str, help="Single paper title to resolve"
    )

    # Project organization
    parser.add_argument(
        "--project",
        type=str,
        default="default",
        help="Project name for organizing results (default: 'default')",
    )

    # Processing options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-resolution of existing DOIs",
    )
    parser.add_argument(
        "--no-enrich", action="store_true", help="Skip metadata enrichment"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=Path,
        help="Output BibTeX file path (auto-generated if not specified)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate and display project summary",
    )

    # Performance options
    parser.add_argument(
        "--worker_asyncs",
        type=int,
        default=4,
        help="Number of concurrent worker_asyncs (default: 4)",
    )
    return parser


def main():
    import asyncio

    async def async_main():
        # Use ScholarEngine instead of legacy metadata modules
        from ..config import ScholarConfig
        from ..engines.ScholarEngine import ScholarEngine
        from ..storage.ScholarLibrary import ScholarLibrary

        parser = create_parser()
        args = parser.parse_args()

        # Validate arguments
        if not args.bibtex and not args.title and not args.summary:
            parser.error("Must specify --bibtex, --title, or --summary")

        try:
            # Initialize working components
            config = ScholarConfig()
            engine = ScholarEngine(config=config)
            library = ScholarLibrary(project=args.project, config=config)

            logger.info(
                f"Initialized ScholarEngine with {len(engine.engines)} engines"
            )
            logger.info(f"Project: {args.project}")

            if args.summary:
                await display_project_summary(library, args.project)
                return

            if args.bibtex:
                await process_bibtex_file(engine, library, args)
            elif args.title:
                await process_single_title(engine, library, args)

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error during resolution: {e}")
            print(f"\nError: {e}")
            sys.exit(1)

    # Run async main
    asyncio.run(async_main())


def process_bibtex_file(resolver: SingleDOIResolver, args):
    if not args.bibtex.exists():
        print(f"BibTeX file not found: {args.bibtex}")
        sys.exit(1)

    print(f"\nProcessing BibTeX file: {args.bibtex}")
    print(f"Project: {args.project}")
    print(f"Workers: {args.worker_asyncs}")
    print(f"Force resolution: {'Yes' if args.force else 'No'}")

    output_path, unresolved_path, summary_path = resolver.resolve_from_bibtex(
        bibtex_path=args.bibtex,
        output_bibtex_path=args.output,
        create_summary=True,
        preserve_existing=not args.force,
    )

    print(f"\nDOI resolution completed!")
    print(f"Resolved BibTeX: {output_path}")
    print(f"Unresolved BibTeX: {unresolved_path}")
    print(f"Summary table: {summary_path}")

    # Count unresolved entries
    unresolved_count = 0
    if unresolved_path.exists():
        try:
            with open(unresolved_path, "r", encoding="utf-8") as f:
                content = f.read()
            import re

            unresolved_count = len(
                re.findall(r"^@\w+\{", content, re.MULTILINE)
            )
        except Exception:
            pass

    # Display summary
    project_summary = resolver.get_project_summary()
    print(f"\nProject Summary:")
    print(f"  Total entries: {project_summary['total_entries']}")
    print(f"  Entries with DOI: {project_summary['entries_with_doi']}")
    print(
        f"  Resolved by SciTeX: {project_summary['entries_resolved_by_scitex']}"
    )
    print(f"  Unresolved entries: {unresolved_count}")

    if unresolved_count > 0:
        print(
            f"\n{unresolved_count} entries could not be resolved automatically"
        )
        print(f"Check {unresolved_path.name} for manual review")


def process_single_title(resolver: SingleDOIResolver, args):
    print(f"\nResolving DOI for title: {args.title}")
    print(f"Project: {args.project}")

    doi = resolver.doi_resolver.resolve(title=args.title)

    if doi:
        print(f"DOI found: {doi}")

        from datetime import datetime

        metadata = {
            "title": args.title,
            "doi": doi,
            "resolution_timestamp": datetime.now().isoformat(),
            "project": args.project,
            "method": "single_title_resolution",
        }

        safe_title = "".join(
            c for c in args.title[:50] if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_title = safe_title.replace(" ", "_")
        metadata_file = resolver.project_metadata / f"single_{safe_title}.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Metadata saved: {metadata_file}")
    else:
        print("DOI not found")


def enrich_project_metadata(project_name: str):
    print(f"\nStarting metadata enrichment for project: {project_name}")
    enricher = MetadataEnricher(project_name=project_name)
    results = enricher.batch_enrich_from_metadata_files(preserve_existing=True)

    print(f"\nEnrichment Summary:")
    print(
        f"  Total files processed: {results['processed']}/{results['total_files']}"
    )

    for field_name, stats in results["enrichment_summary"].items():
        attempted = stats["attempted"]
        successful = stats["successful"]
        skipped = stats["skipped"]
        if attempted > 0:
            success_rate = (successful / attempted) * 100
            print(f"  {field_name.replace('_', ' ').title()}:")
            print(
                f"    Attempted: {attempted}, Successful: {successful} ({success_rate:.1f}%), Skipped: {skipped}"
            )

    if results["errors"]:
        print(f"\nErrors encountered: {len(results['errors'])}")
        for error in results["errors"][:5]:
            print(f"    {error}")


def display_project_summary(resolver: SingleDOIResolver):
    summary = resolver.get_project_summary()
    print(f"\nProject Summary: {summary['project']}")
    print(f"Project path: {summary['project_path']}")
    print(f"Last updated: {summary['last_updated']}")
    print(f"\nStatistics:")
    print(f"  Total entries: {summary['total_entries']}")
    print(f"  Entries with DOI: {summary['entries_with_doi']}")
    print(f"  Resolved by SciTeX: {summary['entries_resolved_by_scitex']}")

    if summary["sources"]:
        print(f"\nDOI Sources:")
        for source, count in summary["sources"].items():
            print(f"  {source}: {count}")


if __name__ == "__main__":
    main()


# python -m scitex.scholar.cli.resolve_and_enrich

# EOF
