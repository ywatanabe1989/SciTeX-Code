#!/usr/bin/env python3
"""
Demo script showing the enhanced DOI resolver with unresolved BibTeX generation.
"""

import tempfile
from pathlib import Path

# Create a sample BibTeX file with mix of resolvable and unresolvable entries
sample_bibtex = """
@article{goodpaper2023,
  title = {The functional role of cross-frequency coupling in neural computation},
  author = {Smith, John and Johnson, Mary},
  year = {2010},
  journal = {Trends in Neurosciences}
}

@article{badpaper2023,
  title = {This is a completely fake paper title that will never be found},
  author = {Fake, Author and Nonexistent, Person},
  year = {2099},
  journal = {Journal of Imaginary Science}
}

@article{alreadyresolved2023,
  title = {Deep learning for scientific discovery},
  author = {Wilson, Alice},  
  year = {2020},
  journal = {Nature},
  doi = {10.1038/s41586-020-2649-2}
}

@article{anotherbad2023,
  title = {Quantum computing with purple unicorns},
  author = {Magic, Researcher},
  year = {2025},
  journal = {Unicorn Quarterly}
}
"""

def main():
    """Run demonstration of enhanced DOI resolver."""
    print("🧪 Demo: Enhanced DOI Resolver with Unresolved BibTeX Generation")
    print("=" * 70)
    
    # Create temporary BibTeX file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
        f.write(sample_bibtex.strip())
        temp_bibtex = Path(f.name)
    
    try:
        print(f"📄 Created sample BibTeX: {temp_bibtex}")
        print("\n📋 Sample entries:")
        print("  ✅ goodpaper2023 - Should resolve successfully")
        print("  ❌ badpaper2023 - Will fail resolution")  
        print("  ✅ alreadyresolved2023 - Already has DOI (skip)")
        print("  ❌ anotherbad2023 - Will fail resolution")
        
        # Import and run resolver
        from src.scitex.scholar.doi._ProjectAwareDOIResolver import ProjectAwareDOIResolver
        
        resolver = ProjectAwareDOIResolver(
            project_name="demo",
            max_workers=2  # Keep it simple for demo
        )
        
        print(f"\n🔍 Running DOI resolution...")
        resolved_path, unresolved_path, summary_path = resolver.resolve_from_bibtex(
            bibtex_path=temp_bibtex,
            create_summary=True,
            preserve_existing=True
        )
        
        print(f"\n✅ Resolution completed!")
        print(f"📄 Resolved BibTeX: {resolved_path}")
        print(f"❌ Unresolved BibTeX: {unresolved_path}")
        print(f"📊 Summary CSV: {summary_path}")
        
        # Show unresolved file content
        if unresolved_path.exists():
            print(f"\n📋 Unresolved BibTeX content:")
            print("-" * 50)
            with open(unresolved_path, 'r') as f:
                content = f.read()
                # Show first 20 lines to avoid too much output
                lines = content.split('\n')[:20]
                print('\n'.join(lines))
                if len(content.split('\n')) > 20:
                    print("... (truncated)")
            print("-" * 50)
        
        # Show project summary  
        summary = resolver.get_project_summary()
        print(f"\n📈 Final Project Summary:")
        print(f"  Total entries: {summary['total_entries']}")
        print(f"  Entries with DOI: {summary['entries_with_doi']}")
        print(f"  Resolved by SciTeX: {summary['entries_resolved_by_scitex']}")
        
        print(f"\n🎯 Demo completed! Check the generated files:")
        print(f"  📁 Project directory: {resolver.project_base}")
        
    finally:
        # Clean up temp file
        temp_bibtex.unlink()

if __name__ == "__main__":
    main()