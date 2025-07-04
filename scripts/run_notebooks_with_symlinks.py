#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:43:00 (ywatanabe)"
# File: ./scripts/run_notebooks_with_symlinks.py

"""
Run notebooks with papermill, creating symlinks for backward compatibility.

This script creates temporary symlinks from the old expected paths to the new
output directories to allow notebooks to run without modification.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def create_notebook_symlinks(notebook_path: Path) -> list[Path]:
    """Create symlinks for notebook outputs."""
    symlinks = []
    notebook_dir = notebook_path.parent
    notebook_base = notebook_path.stem
    
    # Expected old paths
    old_paths = [
        notebook_dir / "io_examples",
        notebook_dir / "outputs", 
        notebook_dir / "results",
        notebook_dir / "figures"
    ]
    
    # New output directory
    new_out_dir = notebook_dir / f"{notebook_base}_out"
    
    for old_path in old_paths:
        # If old path doesn't exist and new path does, create symlink
        new_path = new_out_dir / old_path.name
        
        if not old_path.exists():
            # Create parent dirs if needed
            old_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create relative symlink
            try:
                os.symlink(
                    os.path.relpath(new_path, old_path.parent),
                    old_path
                )
                symlinks.append(old_path)
                print(f"Created symlink: {old_path} -> {new_path}")
            except Exception as e:
                print(f"Failed to create symlink {old_path}: {e}")
    
    return symlinks


def run_notebook_with_symlinks(notebook_path: Path, output_path: Path):
    """Run a notebook with temporary symlinks."""
    # Create symlinks
    symlinks = create_notebook_symlinks(notebook_path)
    
    try:
        # Run papermill
        cmd = [
            sys.executable,
            "-m", "papermill",
            str(notebook_path),
            str(output_path),
            "-k", "scitex",
            "--progress-bar"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ Successfully executed: {notebook_path.name}")
            return True
        else:
            print(f"✗ Failed to execute: {notebook_path.name}")
            print(f"  Error: {result.stderr}")
            return False
            
    finally:
        # Clean up symlinks
        for symlink in symlinks:
            try:
                if symlink.is_symlink():
                    symlink.unlink()
                    print(f"Removed symlink: {symlink}")
            except Exception as e:
                print(f"Failed to remove symlink {symlink}: {e}")


def main():
    """Run selected notebooks with symlink workaround."""
    # Quick test with a few notebooks
    test_notebooks = [
        "01_scitex_io.ipynb",
        "02_scitex_gen.ipynb", 
        "11_scitex_stats.ipynb"
    ]
    
    examples_dir = Path("examples").resolve()
    
    for notebook_name in test_notebooks:
        notebook_path = examples_dir / notebook_name
        
        if not notebook_path.exists():
            print(f"Notebook not found: {notebook_path}")
            continue
            
        output_path = notebook_path.parent / f"{notebook_path.stem}_test_output.ipynb"
        
        print(f"\nTesting {notebook_name}...")
        run_notebook_with_symlinks(notebook_path, output_path)


if __name__ == "__main__":
    main()

# EOF