#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Preview cleanup actions
# ----------------------------------------

"""
Preview what files will be moved/archived during cleanup.
"""

from pathlib import Path
from cleanup_scholar_files import FILES_TO_ORGANIZE, FILES_TO_REMOVE

REPO_ROOT = Path("/home/ywatanabe/proj/SciTeX-Code")

def preview_cleanup():
    """Preview cleanup actions."""
    
    print("=== Preview Scholar Files Cleanup ===\n")
    
    # Count existing files
    existing = {"examples": 0, "archive": 0, "remove": 0, "missing": 0}
    
    print("1. OpenAthens Examples → scholar/examples/openathens/")
    for file in FILES_TO_ORGANIZE["examples_openathens"]:
        if (REPO_ROOT / file).exists():
            print(f"   ✓ {file}")
            existing["examples"] += 1
        else:
            print(f"   ✗ {file} (not found)")
            existing["missing"] += 1
    
    print("\n2. PDF Download Scripts → .archive/")
    for file in FILES_TO_ORGANIZE["archive_pdf_downloads"]:
        if (REPO_ROOT / file).exists():
            print(f"   ✓ {file}")
            existing["archive"] += 1
        else:
            print(f"   ✗ {file} (not found)")
            existing["missing"] += 1
    
    print("\n3. Test Data → scholar/tests/data/")
    for file in FILES_TO_ORGANIZE["test_data"]:
        if (REPO_ROOT / file).exists():
            if "cookie" in file.lower():
                print(f"   🗑️  {file} (will be removed for privacy)")
                existing["remove"] += 1
            else:
                print(f"   ✓ {file}")
                existing["examples"] += 1
    
    print("\n4. Documentation → scholar/docs/")
    for file in FILES_TO_ORGANIZE["documentation"]:
        if (REPO_ROOT / file).exists():
            print(f"   ✓ {file}")
            existing["examples"] += 1
    
    print("\n5. Test Directories → .archive/test_outputs/")
    for dir_name in FILES_TO_ORGANIZE["test_directories"]:
        if (REPO_ROOT / dir_name).exists():
            print(f"   ✓ {dir_name}")
            existing["archive"] += 1
    
    print("\n6. Files to Remove")
    for file in FILES_TO_REMOVE:
        if (REPO_ROOT / file).exists():
            print(f"   🗑️  {file}")
            existing["remove"] += 1
    
    print(f"\n=== Summary ===")
    print(f"Files to move to examples: {existing['examples']}")
    print(f"Files to archive: {existing['archive']}")
    print(f"Files to remove: {existing['remove']}")
    print(f"Files not found: {existing['missing']}")
    print(f"\nTotal files to process: {sum(existing.values()) - existing['missing']}")


if __name__ == "__main__":
    preview_cleanup()