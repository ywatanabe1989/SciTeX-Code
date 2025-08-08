#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line tool for managing the Scholar paper database."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from _PaperDatabase import PaperDatabase
from _ScholarDatabaseIntegration import ScholarDatabaseIntegration
import logging

logger = logging.getLogger(__name__)


def import_bibtex(args):
    """Import papers from BibTeX file."""
    integration = ScholarDatabaseIntegration(args.database)
    
    # Run async workflow
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        results = loop.run_until_complete(
            integration.process_bibtex_workflow(
                Path(args.bibtex),
                download_pdf_asyncs=args.download,
                validate_pdfs=args.validate
            )
        )
    finally:
        loop.close()
    
    # Print results
    print(f"\nImport Summary:")
    print(f"  Total entries: {results['total_entries']}")
    print(f"  Added to database: {results['database_added']}")
    
    if args.download:
        print(f"  PDFs download: {results['pdfs_download']}")
        
    if args.validate:
        print(f"  PDFs validated: {results['pdfs_validated']}")
        
    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors'][:5]:
            print(f"  - {error['entry']}: {error['error']}")


def search_papers(args):
    """Search papers in database."""
    db = PaperDatabase(args.database)
    
    # Build filters
    filters = {}
    if args.year:
        filters['year'] = args.year
    if args.journal:
        filters['journal'] = args.journal
    if args.has_pdf is not None:
        filters['has_pdf'] = args.has_pdf
    if args.validated is not None:
        filters['validation_status'] = 'valid' if args.validated else 'invalid'
    
    # Search
    entries = db.search_entries(
        query=args.query,
        filters=filters,
        limit=args.limit
    )
    
    # Display results
    print(f"\nFound {len(entries)} papers:")
    for entry in entries:
        pdf_indicator = "📄" if entry.pdf_path else "  "
        valid_indicator = "✓" if entry.validation_status == 'valid' else "✗" if entry.validation_status == 'invalid' else "?"
        
        print(f"\n{pdf_indicator}{valid_indicator} {entry.title}")
        print(f"   Authors: {', '.join(entry.authors[:3])}{'...' if len(entry.authors) > 3 else ''}")
        print(f"   Year: {entry.year} | Journal: {entry.journal}")
        
        if entry.doi:
            print(f"   DOI: {entry.doi}")
            
        if args.verbose and entry.abstract:
            print(f"   Abstract: {entry.abstract[:150]}...")


def show_async_statistics(args):
    """Show database statistics."""
    integration = ScholarDatabaseIntegration(args.database)
    summary = integration.get_workflow_summary()
    
    print("\nDatabase Statistics:")
    print("=" * 50)
    
    db_stats = summary['database']
    print(f"Total papers: {db_stats['total_entries']}")
    print(f"Papers with PDFs: {db_stats['pdfs_count']}")
    print(f"Validated papers: {db_stats['validated_count']}")
    print(f"Average quality score: {db_stats['avg_quality_score']:.2f}")
    
    print("\nPapers by Year:")
    for year, count in sorted(db_stats['by_year'].items(), reverse=True)[:10]:
        print(f"  {year}: {count}")
        
    print("\nTop Journals:")
    for journal, count in db_stats['top_journals'][:10]:
        print(f"  {journal}: {count}")
        
    print("\nWorkflow Progress:")
    workflow = summary['workflow']
    for step, count in workflow.items():
        print(f"  {step.replace('_', ' ').title()}: {count}")


def export_papers(args):
    """Export papers from database."""
    integration = ScholarDatabaseIntegration(args.database)
    
    if args.validated_only:
        integration.export_validated_papers(
            Path(args.output),
            format=args.format
        )
        print(f"Exported validated papers to: {args.output}")
    else:
        db = PaperDatabase(args.database)
        
        # Build filters
        filters = {}
        if args.year:
            filters['year'] = args.year
        if args.journal:
            filters['journal'] = args.journal
            
        entries = db.search_entries(filters=filters)
        
        if args.format == 'bibtex':
            integration._export_to_bibtex(entries, Path(args.output))
        else:
            integration._export_to_json(entries, Path(args.output))
            
        print(f"Exported {len(entries)} papers to: {args.output}")


def validate_pdfs(args):
    """Validate PDFs in database."""
    integration = ScholarDatabaseIntegration(args.database)
    db = integration.database
    
    # Get entries with PDFs
    entries = db.search_entries(filters={'has_pdf': True})
    
    if args.unvalidated_only:
        entries = [e for e in entries if e.validation_status is None]
        
    print(f"Validating {len(entries)} PDFs...")
    
    validated = 0
    invalid = 0
    
    for entry in entries:
        if entry.pdf_path and Path(entry.pdf_path).exists():
            # Create paper object for validation
            from _Paper import Paper
            paper = Paper(
                title=entry.title,
                authors=entry.authors,
                year=entry.year,
                doi=entry.doi
            )
            
            validation = integration._validate_pdf_for_entry(
                entry.entry_id,
                Path(entry.pdf_path),
                paper
            )
            
            if validation['valid']:
                validated += 1
                print(f"✓ {entry.title[:60]}...")
            else:
                invalid += 1
                print(f"✗ {entry.title[:60]}... - {validation['reason']}")
                
    print(f"\nValidation Summary:")
    print(f"  Valid: {validated}")
    print(f"  Invalid: {invalid}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Scholar paper database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--database", "-d",
        type=str,
        help="Database directory (default: ~/.scitex/scholar/database)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import papers from BibTeX")
    import_parser.add_argument("bibtex", help="BibTeX file to import")
    import_parser.add_argument("--download", action="store_true", help="Download PDFs")
    import_parser.add_argument("--validate", action="store_true", help="Validate PDFs")
    import_parser.set_defaults(func=import_bibtex)
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search papers")
    search_parser.add_argument("query", nargs="?", help="Search query")
    search_parser.add_argument("--year", type=int, help="Filter by year")
    search_parser.add_argument("--journal", help="Filter by journal")
    search_parser.add_argument("--has-pdf", action="store_true", help="Only papers with PDFs")
    search_parser.add_argument("--validated", action="store_true", help="Only validated papers")
    search_parser.add_argument("--limit", type=int, default=20, help="Maximum results")
    search_parser.add_argument("--verbose", "-v", action="store_true", help="Show abstracts")
    search_parser.set_defaults(func=search_papers)
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Show database statistics")
    stats_parser.set_defaults(func=show_async_statistics)
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export papers")
    export_parser.add_argument("output", help="Output file")
    export_parser.add_argument("--format", choices=["bibtex", "json"], default="bibtex")
    export_parser.add_argument("--validated-only", action="store_true", help="Only validated papers")
    export_parser.add_argument("--year", type=int, help="Filter by year")
    export_parser.add_argument("--journal", help="Filter by journal")
    export_parser.set_defaults(func=export_papers)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate PDFs")
    validate_parser.add_argument("--unvalidated-only", action="store_true", help="Only unvalidated PDFs")
    validate_parser.set_defaults(func=validate_pdfs)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Execute command
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())