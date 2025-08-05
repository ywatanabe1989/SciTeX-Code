#!/usr/bin/env python3
"""Create comprehensive CSV summary with all metadata including abstracts."""

import json
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar import Papers
from scitex.scholar.doi import DOIResolver


def create_comprehensive_summary():
    """Create a comprehensive CSV with all paper metadata."""
    print("=" * 80)
    print("CREATING COMPREHENSIVE CSV SUMMARY")
    print("=" * 80)
    
    # Load lookup table
    lookup_file = Path(".dev/pac_research_lookup.json")
    with open(lookup_file, 'r') as f:
        lookup_data = json.load(f)
    
    # Load original BibTeX to get abstracts
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    papers = Papers.from_bibtex(bibtex_path)
    
    # Create mapping of bibtex keys to abstracts
    bibtex_to_abstract = {}
    for i in range(len(papers)):
        paper = papers[i]
        if hasattr(paper, '_bibtex_key'):
            key = paper._bibtex_key
        elif hasattr(paper, '_additional_metadata'):
            key = paper._additional_metadata.get('bibtex_key', f'paper_{i}')
        else:
            key = f"paper_{i}"
        
        # Get abstract
        abstract = None
        if hasattr(paper, 'abstract'):
            abstract = paper.abstract
        elif hasattr(paper, '_additional_metadata'):
            abstract = paper._additional_metadata.get('abstract')
        
        bibtex_to_abstract[key] = abstract
    
    # Build comprehensive data
    all_data = []
    storage_info = lookup_data["storage_info"]
    
    for storage_key, info in storage_info.items():
        # Load full metadata from file
        metadata_path = Path(info["storage_path"]) / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                full_metadata = json.load(f)
        else:
            full_metadata = {}
        
        # Get abstract from bibtex mapping
        bibtex_key = info.get("bibtex_key")
        abstract = bibtex_to_abstract.get(bibtex_key) if bibtex_key else None
        
        # Combine all information
        row = {
            # Identifiers
            "storage_key": storage_key,
            "bibtex_key": bibtex_key,
            "doi": info.get("doi"),
            "doi_source": info.get("doi_source"),
            
            # Basic metadata
            "title": info.get("title"),
            "authors": "; ".join(info.get("authors", [])) if isinstance(info.get("authors"), list) else info.get("authors"),
            "year": info.get("year"),
            "journal": info.get("journal"),
            
            # Extended metadata
            "abstract": abstract,
            "abstract_source": "bibtex" if abstract else None,
            "keywords": "; ".join(full_metadata.get("keywords", [])) if isinstance(full_metadata.get("keywords"), list) else full_metadata.get("keywords"),
            "volume": full_metadata.get("volume"),
            "issue": full_metadata.get("issue"),
            "pages": full_metadata.get("pages"),
            "url": full_metadata.get("url"),
            "publisher": full_metadata.get("publisher"),
            
            # Status flags
            "has_pdf": info.get("has_pdf"),
            "pdf_filename": info.get("pdf_filename"),
            "pdf_size_bytes": info.get("pdf_size"),
            "metadata_completeness": info.get("metadata_completeness"),
            "missing_fields": "; ".join(info.get("missing_fields", [])),
            
            # Timestamps
            "created_at": info.get("created_at"),
            "doi_resolved_at": full_metadata.get("doi_resolved_at"),
            "pdf_downloaded_at": full_metadata.get("pdf_downloaded_at"),
            
            # Directory info
            "storage_path": info.get("storage_path"),
        }
        
        all_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Sort by year and title
    df = df.sort_values(['year', 'title'], ascending=[False, True])
    
    # Save comprehensive CSV
    csv_path = Path(".dev/pac_research_comprehensive_summary.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"\nComprehensive CSV saved to: {csv_path}")
    
    # Create summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total papers: {len(df)}")
    print(f"Papers with DOI: {df['doi'].notna().sum()} ({df['doi'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Papers with PDF: {df['has_pdf'].sum()} ({df['has_pdf'].sum()/len(df)*100:.1f}%)")
    print(f"Papers with abstract: {df['abstract'].notna().sum()} ({df['abstract'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Average metadata completeness: {df['metadata_completeness'].mean():.1f}%")
    
    # Year distribution
    print("\nPapers by year:")
    year_counts = df['year'].value_counts().sort_index(ascending=False)
    for year, count in year_counts.head(10).items():
        print(f"  {year}: {count} papers")
    
    # Journal distribution
    print("\nTop journals:")
    journal_counts = df['journal'].value_counts()
    for journal, count in journal_counts.head(10).items():
        if journal:
            print(f"  {journal}: {count} papers")
    
    # Create a simplified status report
    status_df = df[['storage_key', 'title', 'year', 'doi', 'has_pdf', 'abstract']].copy()
    status_df['title'] = status_df['title'].str[:60] + '...'
    status_df['has_abstract'] = status_df['abstract'].notna()
    status_df = status_df.drop('abstract', axis=1)
    
    status_path = Path(".dev/pac_research_status_simple.csv")
    status_df.to_csv(status_path, index=False)
    print(f"\nSimple status CSV saved to: {status_path}")
    
    # Create action items CSV
    needs_action = df[
        (df['doi'].isna()) |  # No DOI
        (~df['has_pdf']) |    # No PDF
        (df['abstract'].isna())  # No abstract
    ].copy()
    
    needs_action['needs_doi'] = needs_action['doi'].isna()
    needs_action['needs_pdf'] = ~needs_action['has_pdf']
    needs_action['needs_abstract'] = needs_action['abstract'].isna()
    
    action_df = needs_action[['storage_key', 'bibtex_key', 'title', 'year', 
                              'needs_doi', 'needs_pdf', 'needs_abstract']].copy()
    action_df['title'] = action_df['title'].str[:60] + '...'
    
    action_path = Path(".dev/pac_research_action_items.csv")
    action_df.to_csv(action_path, index=False)
    print(f"\nAction items CSV saved to: {action_path}")
    
    return df


if __name__ == "__main__":
    df = create_comprehensive_summary()