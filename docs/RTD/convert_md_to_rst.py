#!/usr/bin/env python3
"""Convert markdown documentation to reStructuredText for Sphinx."""

import os
import subprocess
from pathlib import Path

def convert_md_to_rst(md_file, rst_file):
    """Convert a markdown file to reStructuredText using pandoc."""
    try:
        subprocess.run(
            ['pandoc', '-f', 'markdown', '-t', 'rst', '-o', str(rst_file), str(md_file)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Converted: {md_file} -> {rst_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {md_file}: {e}")
        # Fallback: create a simple rst file that includes the markdown
        with open(rst_file, 'w') as f:
            f.write(f".. include:: {md_file.relative_to(rst_file.parent)}\n")
            f.write("   :parser: myst_parser.sphinx_\n")
        print(f"Created fallback rst for: {md_file}")

def main():
    # Paths
    sphinx_dir = Path(__file__).parent
    scitex_guidelines = sphinx_dir.parent / "scitex_guidelines" / "modules"
    
    # Create module documentation directory
    modules_dir = sphinx_dir / "modules"
    modules_dir.mkdir(exist_ok=True)
    
    # Module mapping
    modules = {
        "gen": "gen/README.md",
        "io": "io/README.md", 
        "plt": "plt/README.md",
        "dsp": "dsp/README.md",
        "stats": "stats/README.md",
        "pd": "pd/README.md",
    }
    
    # Convert each module's documentation
    for module_name, md_path in modules.items():
        md_file = scitex_guidelines / md_path
        rst_file = modules_dir / f"{module_name}.rst"
        
        if md_file.exists():
            convert_md_to_rst(md_file, rst_file)
        else:
            # Create placeholder
            with open(rst_file, 'w') as f:
                f.write(f"{module_name.upper()} Module\n")
                f.write("=" * (len(module_name) + 7) + "\n\n")
                f.write(f"Documentation for the {module_name} module.\n\n")
                f.write(".. note::\n\n")
                f.write("   This documentation is being developed.\n")

if __name__ == "__main__":
    main()