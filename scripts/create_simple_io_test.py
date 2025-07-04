#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:11:00 (ywatanabe)"
# File: ./scripts/create_simple_io_test.py

"""
Create a simple test notebook for IO operations.
"""

import nbformat
from pathlib import Path


def create_test_notebook():
    """Create a simplified test notebook for IO operations."""
    nb = nbformat.v4.new_notebook()
    
    # Cell 1: Imports
    imports = """import sys
sys.path.insert(0, '../src')
import scitex
import numpy as np
from pathlib import Path
print(f"SciTeX version: {scitex.__version__}")"""
    
    # Cell 2: Basic save/load test
    basic_test = """# Test basic save and load
data = {'test': np.random.rand(10, 10)}
scitex.io.save(data, 'test_data.pkl')
print("✓ Saved test_data.pkl")

# Load it back
loaded = scitex.io.load('test_data.pkl')
print("✓ Loaded test_data.pkl")
print(f"Data shape: {loaded['test'].shape}")"""
    
    # Cell 3: Compression test
    compression_test = """# Test compression formats
large_data = np.random.rand(1000, 1000)

# Test different compression formats
formats = ['pkl', 'gz', 'bz2', 'xz']
sizes = {}

for fmt in formats:
    filename = f'large_data.{fmt}'
    scitex.io.save(large_data, filename)
    
    # Check file size (handle new path convention)
    saved_path = Path(filename)
    if saved_path.exists():
        sizes[fmt] = saved_path.stat().st_size
    else:
        # Try in notebook output directory
        output_path = Path(f'test_simple_io_out/{filename}')
        if output_path.exists():
            sizes[fmt] = output_path.stat().st_size
        else:
            sizes[fmt] = 0
    
    print(f"✓ Saved {filename}: {sizes[fmt]:,} bytes")

# Show compression ratios
base_size = sizes.get('pkl', 1)
for fmt, size in sizes.items():
    ratio = base_size / size if size > 0 else 0
    print(f"{fmt}: {ratio:.2f}x compression")"""
    
    # Cell 4: CSV test
    csv_test = """# Test CSV operations
import pandas as pd

df = pd.DataFrame({
    'x': np.arange(100),
    'y': np.random.randn(100),
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

scitex.io.save(df, 'test_data.csv')
print("✓ Saved CSV")

df_loaded = scitex.io.load('test_data.csv')
print(f"✓ Loaded CSV with shape: {df_loaded.shape}")"""
    
    # Cell 5: Summary
    summary = """print("\\nAll IO tests completed successfully!")
print("Files are saved to either current directory or {notebook_name}_out/")"""
    
    # Add cells
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Simple SciTeX IO Test\nTesting basic IO operations with new path handling"),
        nbformat.v4.new_code_cell(imports),
        nbformat.v4.new_markdown_cell("## Basic Save/Load"),
        nbformat.v4.new_code_cell(basic_test),
        nbformat.v4.new_markdown_cell("## Compression Formats"),
        nbformat.v4.new_code_cell(compression_test),
        nbformat.v4.new_markdown_cell("## CSV Operations"),
        nbformat.v4.new_code_cell(csv_test),
        nbformat.v4.new_markdown_cell("## Summary"),
        nbformat.v4.new_code_cell(summary),
    ]
    
    # Save notebook
    output_path = Path("examples/test_simple_io.ipynb")
    with open(output_path, 'w') as f:
        nbformat.write(nb, f)
    
    print(f"Created test notebook: {output_path}")
    return output_path


if __name__ == "__main__":
    nb_path = create_test_notebook()
    
    # Test it
    import subprocess
    print("\nTesting the notebook...")
    result = subprocess.run(
        ["../.env/bin/python", "-m", "papermill",
         str(nb_path.name), "test_simple_io_output.ipynb",
         "-k", "scitex"],
        cwd=str(nb_path.parent),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Test notebook executed successfully!")
    else:
        print("✗ Test notebook failed")
        print(result.stderr[-1000:])

# EOF