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
    
    # Create mapping of bibtex keys to abstracts and other metadata
    bibtex_metadata = {}
    for i in range(len(papers)):
        paper = papers[i]
        if hasattr(paper, '_bibtex_key'):
            key = paper._bibtex_key
        elif hasattr(paper, '_additional_metadata'):
            key = paper._additional_metadata.get('bibtex_key', f'paper_{i}')
        else:
            key = f"paper_{i}"
        
        # Get all available metadata
        metadata = {
            'abstract': getattr(paper, 'abstract', None),
            'keywords': getattr(paper, 'keywords', None),
            'impact_factor': getattr(paper, 'impact_factor', None),
            'citation_count': getattr(paper, 'citation_count', None)
        }
        
        # Check additional metadata
        if hasattr(paper, '_additional_metadata'):
            for field in ['abstract', 'keywords', 'impact_factor', 'citation_count']:
                if field not in metadata or metadata[field] is None:
                    metadata[field] = paper._additional_metadata.get(field)
        
        bibtex_metadata[key] = metadata
    
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
        
        # Get additional metadata from bibtex mapping
        bibtex_key = info.get("bibtex_key")
        bibtex_meta = bibtex_metadata.get(bibtex_key, {}) if bibtex_key else {}
        
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
            "abstract": bibtex_meta.get('abstract') or full_metadata.get('abstract'),
            "abstract_source": "bibtex" if bibtex_meta.get('abstract') else ("metadata" if full_metadata.get('abstract') else None),
            "keywords": bibtex_meta.get('keywords') or full_metadata.get('keywords'),
            "volume": full_metadata.get("volume"),
            "issue": full_metadata.get("issue"),
            "pages": full_metadata.get("pages"),
            "url": full_metadata.get("url"),
            "publisher": full_metadata.get("publisher"),
            
            # Impact and citations
            "impact_factor": bibtex_meta.get('impact_factor') or full_metadata.get('impact_factor'),
            "impact_factor_source": full_metadata.get('impact_factor_source'),
            "citation_count": bibtex_meta.get('citation_count') or full_metadata.get('citation_count'),
            "citation_count_source": full_metadata.get('citation_count_source'),
            
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
            
            # Authentication needed
            "needs_openathens": info.get("doi") and not info.get("has_pdf") and not any(
                x in str(info.get("doi", "")) for x in ["10.3389", "10.1371", "10.1101", "10.7554"]
            ),
            
            # Directory info
            "storage_path": info.get("storage_path"),
        }
        
        all_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Convert year to int where possible for sorting
    df['year_sort'] = pd.to_numeric(df['year'], errors='coerce')
    
    # Sort by year and title
    df = df.sort_values(['year_sort', 'title'], ascending=[False, True])
    df = df.drop('year_sort', axis=1)
    
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
    print(f"Papers with impact factor: {df['impact_factor'].notna().sum()} ({df['impact_factor'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Papers with citation count: {df['citation_count'].notna().sum()} ({df['citation_count'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Papers needing OpenAthens: {df['needs_openathens'].sum()}")
    print(f"Average metadata completeness: {df['metadata_completeness'].mean():.1f}%")
    
    # Create OpenAthens download list
    openathens_papers = df[df['needs_openathens'] & df['doi'].notna()][
        ['storage_key', 'doi', 'title', 'journal', 'year']
    ].copy()
    
    openathens_path = Path(".dev/papers_for_openathens_download.csv")
    openathens_papers.to_csv(openathens_path, index=False)
    print(f"\nOpenAthens download list saved to: {openathens_path}")
    print(f"  {len(openathens_papers)} papers require institutional access")
    
    # Create simple status report
    status_df = df[['storage_key', 'title', 'year', 'journal', 'doi', 'has_pdf', 
                    'abstract', 'impact_factor', 'citation_count']].copy()
    status_df['title'] = status_df['title'].str[:60] + '...'
    status_df['has_abstract'] = status_df['abstract'].notna()
    status_df['has_impact_factor'] = status_df['impact_factor'].notna()
    status_df['has_citation_count'] = status_df['citation_count'].notna()
    status_df = status_df.drop(['abstract', 'impact_factor', 'citation_count'], axis=1)
    
    status_path = Path(".dev/pac_research_status_simple.csv")
    status_df.to_csv(status_path, index=False)
    print(f"\nSimple status CSV saved to: {status_path}")
    
    return df


if __name__ == "__main__":
    df = create_comprehensive_summary()