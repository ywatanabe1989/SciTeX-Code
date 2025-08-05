#!/usr/bin/env python3
"""
Demo the PAC project structure creation without DOI resolution.
Shows the directory structure and file organization.
"""

import tempfile
from pathlib import Path
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_simple_bibtex():
    """Create simple BibTeX for structure demo."""
    return """
@article{sample1,
  title = {Sample paper 1},
  author = {Author, First},
  year = {2020},
  journal = {Sample Journal},
  doi = {10.1234/sample1}
}

@article{sample2,
  title = {Sample paper 2 without DOI},
  author = {Author, Second},
  year = {2021},
  journal = {Another Journal}
}

@article{sample3,
  title = {Sample paper 3 with DOI},
  author = {Author, Third},
  year = {2022},
  journal = {Third Journal},
  doi = {10.5678/sample3}
}
"""

def main():
    """Demo the project structure creation."""
    print("🏗️  PAC Project Structure Demo")
    print("=" * 50)
    
    # Create temporary BibTeX file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False, prefix='pac_demo_') as f:
        f.write(create_simple_bibtex().strip())
        temp_bibtex = Path(f.name)
    
    try:
        print(f"📄 Created demo BibTeX: {temp_bibtex}")
        
        # Import and initialize resolver (without actual resolution)
        from scitex.scholar.doi._ProjectAwareDOIResolver import ProjectAwareDOIResolver
        
        print(f"\n🔧 Creating PAC project structure...")
        resolver = ProjectAwareDOIResolver(project_name="pac")
        
        print(f"📁 Project base: {resolver.project_base}")
        print(f"📁 Project info: {resolver.project_info}")
        print(f"📁 BibTeX directory: {resolver.project_bibtex}")
        print(f"📁 Metadata directory: {resolver.project_metadata}")
        
        # Copy the demo file to show structure
        import shutil
        demo_input = resolver.project_bibtex / "demo_papers.bib"
        shutil.copy2(temp_bibtex, demo_input)
        
        # Create some demo output files
        demo_resolved = resolver.project_bibtex / "demo_papers-resolved.bib"
        demo_unresolved = resolver.project_bibtex / "demo_papers-unresolved.bib"
        demo_summary = resolver.project_bibtex / "demo_papers-summary.csv"
        
        # Create resolved BibTeX (all entries)
        with open(demo_resolved, 'w') as f:
            f.write("% Resolved BibTeX entries - Project: pac\n")
            f.write(f"% Generated: 2025-08-04 18:00:00\n")
            f.write(f"% All entries with resolution attempts\n\n")
            f.write(create_simple_bibtex().strip())
        
        # Create unresolved BibTeX (only sample2)
        with open(demo_unresolved, 'w') as f:
            f.write("% Unresolved BibTeX entries - Project: pac\n")
            f.write(f"% Generated: 2025-08-04 18:00:00\n")
            f.write(f"% Total unresolved entries: 1\n")
            f.write(f"% These entries could not be resolved automatically\n\n")
            f.write("% RESOLUTION FAILED: DOI resolution failed\n")
            f.write("@article{sample2,\n")
            f.write("  title = {Sample paper 2 without DOI},\n")
            f.write("  author = {Author, Second},\n")
            f.write("  year = {2021},\n")
            f.write("  journal = {Another Journal}\n")
            f.write("}\n")
        
        # Create summary CSV
        with open(demo_summary, 'w') as f:
            f.write("bibtex_key,title,original_doi,resolved_doi,resolution_attempted,resolution_successful,doi_source,skip_reason\n")
            f.write("sample1,Sample paper 1,10.1234/sample1,10.1234/sample1,false,true,existing,DOI already present\n")
            f.write("sample2,Sample paper 2 without DOI,,10.1234/resolved2,true,true,crossref,\n")
            f.write("sample3,Sample paper 3 with DOI,10.5678/sample3,10.5678/sample3,false,true,existing,DOI already present\n")
        
        # Create some demo metadata JSON files
        import json
        from datetime import datetime
        
        for i, key in enumerate(['sample1', 'sample2', 'sample3'], 1):
            metadata_file = resolver.project_metadata / f"{key}.json"
            metadata = {
                "paper_id": f"sample{i}",
                "title": f"Sample paper {i}",
                "project": "pac",
                "last_enrichment": {
                    "timestamp": datetime.now().isoformat(),
                    "plan": {"abstract": {"action": "skip", "reason": "demo"}},
                    "results": {"success": True}
                },
                "current_fields": {
                    "doi": {"value": f"10.1234/sample{i}", "source": "demo"},
                    "title": {"value": f"Sample paper {i}", "source": "original_bibtex"}
                }
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Demo structure created!")
        
        # Show the complete directory structure
        print(f"\n📂 PAC Project Directory Structure:")
        def show_tree(directory, prefix=""):
            """Show directory tree structure."""
            directory = Path(directory)
            files = sorted([f for f in directory.iterdir() if f.is_file()])
            dirs = sorted([d for d in directory.iterdir() if d.is_dir()])
            
            # Show directories first
            for i, d in enumerate(dirs):
                is_last_dir = (i == len(dirs) - 1) and len(files) == 0
                branch = "└── " if is_last_dir else "├── "
                print(f"{prefix}{branch}{d.name}/")
                
                next_prefix = prefix + ("    " if is_last_dir else "│   ")
                show_tree(d, next_prefix)
            
            # Show files
            for i, f in enumerate(files):
                is_last = (i == len(files) - 1)
                branch = "└── " if is_last else "├── "
                size = f.stat().st_size
                print(f"{prefix}{branch}{f.name} ({size} bytes)")
        
        print(f"pac/")
        show_tree(resolver.project_base, "")
        
        print(f"\n📄 Sample file contents:")
        print(f"\n--- demo_papers-unresolved.bib ---")
        with open(demo_unresolved, 'r') as f:
            print(f.read())
        
        print(f"\n--- demo_papers-summary.csv ---")
        with open(demo_summary, 'r') as f:
            print(f.read())
        
        print(f"\n--- sample1.json (metadata) ---")
        metadata_file = resolver.project_metadata / "sample1.json"
        with open(metadata_file, 'r') as f:
            content = json.load(f)
            print(json.dumps(content, indent=2))
        
        print(f"\n🎯 Demo completed!")
        print(f"   This shows the structure that will be created when you run:")
        print(f"   python -m scitex.scholar.resolve_dois_enhanced --bibtex papers.bib --project pac")
        
    finally:
        # Clean up temp file
        if temp_bibtex.exists():
            temp_bibtex.unlink()

if __name__ == "__main__":
    main()