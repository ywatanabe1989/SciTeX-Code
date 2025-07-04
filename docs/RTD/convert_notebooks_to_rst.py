#!/usr/bin/env python3
"""
Convert Jupyter notebooks to RST format for Read the Docs.
"""

import os
import subprocess
from pathlib import Path
import re


def convert_notebook_to_rst(notebook_path, output_dir):
    """Convert a single notebook to RST format."""
    notebook_path = Path(notebook_path)
    output_dir = Path(output_dir)
    
    # Create output filename
    output_name = notebook_path.stem + '.rst'
    output_path = output_dir / output_name
    
    # Create RST header
    title = notebook_path.stem.replace('_', ' ').title()
    title = title.replace('Scitex', 'SciTeX')  # Fix capitalization
    
    # For master index, use special title
    if '00_SCITEX_MASTER_INDEX' in str(notebook_path):
        title = "SciTeX Master Tutorial Index"
    
    header = f"""{title}
{'=' * len(title)}

.. note::
   This page is generated from the Jupyter notebook `{notebook_path.name} <https://github.com/scitex/scitex/blob/main/examples/{notebook_path.name}>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook {notebook_path.name}

"""
    
    # Use nbconvert to convert notebook content
    try:
        # Convert to RST
        cmd = [
            'jupyter', 'nbconvert',
            '--to', 'rst',
            '--output', str(output_path.absolute()),
            '--output-dir', str(output_dir.absolute()),
            str(notebook_path.absolute())
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error converting {notebook_path}: {result.stderr}")
            # Create a simple stub file
            with open(output_path, 'w') as f:
                f.write(header)
                f.write(f"\n.. warning::\n   Notebook conversion failed. Please view the notebook directly on GitHub.\n")
        else:
            # Read the generated RST
            with open(output_path, 'r') as f:
                content = f.read()
            
            # Clean up the content
            # Remove the auto-generated title
            content = re.sub(r'^.*?\n=+\n', '', content, count=1)
            
            # Write final content
            with open(output_path, 'w') as f:
                f.write(header)
                f.write(content)
                
            print(f"✓ Converted {notebook_path.name} → {output_path.name}")
            
    except Exception as e:
        print(f"Error converting {notebook_path}: {e}")
        # Create a stub file
        with open(output_path, 'w') as f:
            f.write(header)
            f.write(f"\n.. warning::\n   Notebook conversion is not available. Please install jupyter and nbconvert.\n")
            f.write(f"\n   View the notebook on GitHub: https://github.com/scitex/scitex/blob/main/examples/{notebook_path.name}\n")


def main():
    """Convert all example notebooks to RST."""
    # Paths
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/docs/RTD/examples")
    
    # Create output directory if needed
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Get all notebooks
    notebooks = sorted(examples_dir.glob("*.ipynb"))
    
    # Filter out test outputs and other non-tutorial notebooks
    notebooks = [nb for nb in notebooks if not any(x in nb.name for x in ['test_output', 'output'])]
    
    print(f"Found {len(notebooks)} notebooks to convert")
    
    # Convert each notebook
    for notebook in notebooks:
        convert_notebook_to_rst(notebook, output_dir)
    
    print(f"\n✓ Conversion complete! RST files saved to {output_dir}")


if __name__ == "__main__":
    main()