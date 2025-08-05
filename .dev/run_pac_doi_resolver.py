#!/usr/bin/env python3
"""
Standalone script to run the enhanced DOI resolver on PAC papers.bib
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_minimal_bibtex_loader():
    """Create a minimal BibTeX loader since scitex.io has dependency issues."""
    def load_bibtex(file_path):
        """Load BibTeX entries from file."""
        entries = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple BibTeX parser - find entries
        import re
        
        # Find all @type{key, entries
        pattern = r'@(\w+)\s*\{\s*([^,\s]+)\s*,\s*(.*?)(?=\n@|\nReferences|\Z)'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for entry_type, key, fields_text in matches:
            entry = {
                "entry_type": entry_type.lower(),
                "key": key,
                "fields": {}
            }
            
            # Parse fields - simple approach
            field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
            field_matches = re.findall(field_pattern, fields_text)
            
            for field_name, field_value in field_matches:
                entry["fields"][field_name.lower()] = field_value.strip()
            
            entries.append(entry)
        
        return entries
    
    return load_bibtex

def main():
    """Run the PAC DOI resolver."""
    print("🔍 Running Enhanced DOI Resolver on PAC Project")
    print("=" * 60)
    
    # Paths
    papers_bib = Path("src/scitex/scholar/docs/papers.bib")
    if not papers_bib.exists():
        print(f"❌ BibTeX file not found: {papers_bib}")
        return
    
    print(f"📄 Processing: {papers_bib}")
    
    # Load BibTeX entries
    load_bibtex = create_minimal_bibtex_loader()
    try:
        entries = load_bibtex(papers_bib)
        print(f"📊 Loaded {len(entries)} BibTeX entries")
    except Exception as e:
        print(f"❌ Error loading BibTeX: {e}")
        return
    
    # Show sample entries
    print(f"\n📋 Sample entries:")
    for i, entry in enumerate(entries[:5]):  # Show first 5
        key = entry.get("key", "unknown")
        title = entry.get("fields", {}).get("title", "No title")[:50]
        if len(title) == 50:
            title += "..."
        print(f"  {i+1}. {key}: {title}")
    
    if len(entries) > 5:
        print(f"  ... and {len(entries) - 5} more entries")
    
    # Try to initialize the resolver with minimal dependencies
    try:
        # Create output directories manually
        output_base = Path.home() / ".scitex/scholar/library/pac/info/files-bib"
        output_base.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Output directory: {output_base}")
        
        # Create basic output files
        resolved_path = output_base / "papers-resolved.bib"
        unresolved_path = output_base / "papers-unresolved.bib"
        summary_path = output_base / "papers-summary.csv"
        
        # Copy original file
        import shutil
        original_path = output_base / "papers.bib"
        shutil.copy2(papers_bib, original_path)
        print(f"✅ Copied original: {original_path}")
        
        # Analyze entries for DOI status
        has_doi = []
        no_doi = []
        
        for entry in entries:
            fields = entry.get("fields", {})
            if fields.get("doi"):
                has_doi.append(entry)
            else:
                no_doi.append(entry)
        
        # Create resolved BibTeX (all entries)
        with open(resolved_path, 'w', encoding='utf-8') as f:
            f.write(f"% Resolved BibTeX entries - Project: pac\n")
            f.write(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"% Total entries: {len(entries)}\n")
            f.write(f"% Entries with DOI: {len(has_doi)}\n")
            f.write(f"% Entries without DOI: {len(no_doi)}\n\n")
            
            for entry in entries:
                entry_type = entry.get("entry_type", "article")
                key = entry.get("key", "unknown")
                fields = entry.get("fields", {})
                
                f.write(f"@{entry_type}{{{key},\n")
                for field_name, field_value in fields.items():
                    f.write(f"  {field_name} = {{{field_value}}},\n")
                f.write("}\n\n")
        
        print(f"✅ Created resolved BibTeX: {resolved_path}")
        
        # Create unresolved BibTeX (entries without DOI)
        with open(unresolved_path, 'w', encoding='utf-8') as f:
            f.write(f"% Unresolved BibTeX entries - Project: pac\n")
            f.write(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"% Total unresolved entries: {len(no_doi)}\n")
            f.write(f"% These entries need DOI resolution\n\n")
            
            if no_doi:
                for entry in no_doi:
                    entry_type = entry.get("entry_type", "article")
                    key = entry.get("key", "unknown")
                    fields = entry.get("fields", {})
                    
                    f.write(f"% NEEDS DOI RESOLUTION\n")
                    f.write(f"@{entry_type}{{{key},\n")
                    for field_name, field_value in fields.items():
                        f.write(f"  {field_name} = {{{field_value}}},\n")
                    f.write("}\n\n")
            else:
                f.write("% All entries already have DOIs!\n")
        
        print(f"✅ Created unresolved BibTeX: {unresolved_path}")
        
        # Create summary CSV
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("bibtex_key,title,has_doi,journal,year,doi\n")
            
            for entry in entries:
                key = entry.get("key", "")
                fields = entry.get("fields", {})
                title = fields.get("title", "").replace('"', '""')  # Escape quotes
                journal = fields.get("journal", "").replace('"', '""')
                year = fields.get("year", "")
                doi = fields.get("doi", "")
                has_doi_flag = "Yes" if doi else "No"
                
                f.write(f'"{key}","{title}","{has_doi_flag}","{journal}","{year}","{doi}"\n')
        
        print(f"✅ Created summary CSV: {summary_path}")
        
        # Display summary statistics
        print(f"\n📈 PAC Project Summary:")
        print(f"  Total entries: {len(entries)}")
        print(f"  Entries with DOI: {len(has_doi)} ({len(has_doi)/len(entries)*100:.1f}%)")
        print(f"  Entries without DOI: {len(no_doi)} ({len(no_doi)/len(entries)*100:.1f}%)")
        
        # Show journals represented
        journals = {}
        for entry in entries:
            journal = entry.get("fields", {}).get("journal", "Unknown")
            journals[journal] = journals.get(journal, 0) + 1
        
        print(f"\n📚 Journals represented ({len(journals)} unique):")
        sorted_journals = sorted(journals.items(), key=lambda x: x[1], reverse=True)
        for journal, count in sorted_journals[:10]:  # Top 10
            print(f"  {journal}: {count} papers")
        
        if len(sorted_journals) > 10:
            print(f"  ... and {len(sorted_journals) - 10} more journals")
        
        # Show entries that need DOI resolution
        if no_doi:
            print(f"\n❌ Entries needing DOI resolution ({len(no_doi)}):")
            for entry in no_doi[:10]:  # Show first 10
                key = entry.get("key", "unknown")
                title = entry.get("fields", {}).get("title", "No title")[:60]
                if len(title) == 60:
                    title += "..."
                print(f"  {key}: {title}")
            
            if len(no_doi) > 10:
                print(f"  ... and {len(no_doi) - 10} more entries")
        
        print(f"\n🎯 Files created in: {output_base}")
        print(f"  📄 papers.bib (original)")
        print(f"  📄 papers-resolved.bib (all entries)")  
        print(f"  ❌ papers-unresolved.bib ({len(no_doi)} entries)")
        print(f"  📊 papers-summary.csv (statistics)")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()