#!/usr/bin/env python3
"""Organize enriched papers in Scholar database."""

import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

def organize_papers():
    """Organize papers from enriched BibTeX into database."""
    from src.scitex.scholar import Scholar
    from src.scitex.scholar._Papers import Papers
    from src.scitex.scholar.database import PaperDatabase, DatabaseEntry
    
    print("=== Organizing Papers in Database ===")
    
    # Load enriched papers
    bib_file = Path("src/scitex/scholar/docs/papers-partial-enriched.bib")
    papers = Papers.from_bibtex(bib_file)
    print(f"Loaded {len(papers)} papers from enriched BibTeX")
    
    # Create database
    db = PaperDatabase()
    print(f"Database location: {db.database_dir}")
    
    # Add papers to database
    added = 0
    skipped = 0
    
    for paper in papers:
        try:
            # Create database entry
            entry = DatabaseEntry(
                title=paper.title,
                authors=paper.authors,
                year=paper.year,
                journal=paper.journal,
                doi=paper.doi if hasattr(paper, 'doi') and paper.doi else None,
                abstract=paper.abstract if hasattr(paper, 'abstract') and paper.abstract else None,
                keywords=paper.keywords if hasattr(paper, 'keywords') else [],
                # Store additional metadata in custom_fields
                custom_fields={
                    'bibtex_key': paper.bibtex_key if hasattr(paper, 'bibtex_key') else None,
                    'impact_factor': paper.impact_factor if hasattr(paper, 'impact_factor') else None,
                    'citations': paper.citations if hasattr(paper, 'citations') else None,
                    'references': paper.references if hasattr(paper, 'references') else None,
                    'urls': paper.urls if hasattr(paper, 'urls') else [],
                }
            )
            
            # Add to database
            entry_id = db.add_entry(entry)
            added += 1
            print(f"✓ Added: {entry.title[:60]}... ({entry_id})")
            
        except Exception as e:
            skipped += 1
            print(f"✗ Skipped: {paper.title[:60]}... - Error: {e}")
    
    # Save database (use private method)
    db._save_database()
    
    # Show statistics
    print(f"\n=== Database Statistics ===")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\n✓ Added {added} papers to database")
    print(f"✗ Skipped {skipped} papers")
    
    # Export to JSON
    export_file = db.database_dir / "exports" / "database_summary.json"
    db.export_to_json(export_file)
    print(f"\nExported summary to: {export_file}")
    
    # Note: BibTeX export would need Papers class fix
    # For now, we have JSON export which contains all data
    
    return db

if __name__ == "__main__":
    db = organize_papers()
    print("\n=== Database organization complete ===")