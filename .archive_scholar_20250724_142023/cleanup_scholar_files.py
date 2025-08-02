#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Cleanup Scholar-related files from repository root
# ----------------------------------------

"""
Organize Scholar-related development files from the repository root.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Repository root
REPO_ROOT = Path("/home/ywatanabe/proj/SciTeX-Code")

# Categorize files
FILES_TO_ORGANIZE = {
    # OpenAthens test scripts (move to examples)
    "examples_openathens": [
        "test_openathens_simple.py",
        "test_authenticated_browser.py",
        "capture_cookies_and_test.py",
        "test_openathens_debug.py",
        "test_openathens_interactive.py",
        "test_openathens_reuse_session.py",
        "test_openathens_paywalled.py",
        "quick_test_openathens_dois.py",
        "test_direct_pdf_download.py",
        "test_openathens_debug_download.py",
        "test_openathens_flow.py",
        "test_openathens_manual.py",
        "test_openathens_session_reuse.py",
        "test_openathens_final.py",
        "download_specific_paper.py",
        "download_nature_neuro_paper.py",
    ],
    
    # PDF download scripts (archive)
    "archive_pdf_downloads": [
        "auto_download_pdfs.py",
        "direct_doi_downloader.py",
        "doi_to_pdf_simple.py",
        "download_all_pdfs.py",
        "download_paywalled_papers.py",
        "download_pdfs_auto.py",
        "download_pdfs_from_bibtex.py",
        "download_pdfs_with_tabs.py",
        "download_with_unimelb.py",
        "full_automation.py",
        "login_to_publishers.py",
        "openathens_pdf_downloader.py",
        "phase1_login_setup.py",
        "phase1_login_setup_sso.py",
        "phase1_login_setup_windows.py",
        "phase2_download_pdfs.py",
        "quick_download_pdfs.py",
        "setup_publisher_logins.py",
        "simple_doi_downloader.py",
        "unimelb_pdf_downloader.py",
    ],
    
    # Data files (move to test data)
    "test_data": [
        "dois.txt",
        "openathens_session_cookies.json",
        "openathens_auth_cookies.json",
        "openathens_cookies.json",
    ],
    
    # Documentation (move to docs)
    "documentation": [
        "README_PDF_DOWNLOAD.md",
        "scholar_dependency_graph.md",
    ],
    
    # Utility scripts (archive)
    "archive_utilities": [
        "scholar_dependency_visualization.py",
        "zotero_fix.py",
    ],
    
    # Test directories (archive)
    "test_directories": [
        "test_auto_pdfs/",
        "test_open_access_pdfs/",
        "test_pdfs/",
        "quick_pdfs/",
        "direct_download_test/",
        "final_openathens_test/",
        "nature_neuro_paper/",
        "openathens_pdfs/",
        "openathens_test_pdfs/",
        "paywalled_pdfs_test/",
        "requested_paper/",
    ],
}

# Files to definitely remove (empty or redundant)
FILES_TO_REMOVE = [
    '"tomize with ScholarConfig"',  # Looks like a typo/fragment
    'emantic_scholar_api_key=your-api-key,',  # Fragment
    'scholar_dependencies.dot',  # Generated file
]


def create_archive_dir():
    """Create archive directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = REPO_ROOT / f".archive_scholar_{timestamp}"
    archive_dir.mkdir(exist_ok=True)
    return archive_dir


def organize_files():
    """Organize Scholar-related files."""
    
    print("=== Organizing Scholar Files ===\n")
    
    # Create directories
    archive_dir = create_archive_dir()
    examples_dir = REPO_ROOT / "src" / "scitex" / "scholar" / "examples" / "openathens"
    docs_dir = REPO_ROOT / "src" / "scitex" / "scholar" / "docs"
    test_data_dir = REPO_ROOT / "src" / "scitex" / "scholar" / "tests" / "data"
    
    examples_dir.mkdir(parents=True, exist_ok=True)
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Summary
    summary = {
        "moved_to_examples": [],
        "archived": [],
        "removed": [],
        "not_found": [],
    }
    
    # 1. Move OpenAthens examples
    print("1. Moving OpenAthens examples to scholar/examples/openathens/")
    for file in FILES_TO_ORGANIZE["examples_openathens"]:
        src = REPO_ROOT / file
        if src.exists():
            dst = examples_dir / file
            print(f"   Moving: {file}")
            shutil.move(str(src), str(dst))
            summary["moved_to_examples"].append(file)
        else:
            summary["not_found"].append(file)
    
    # 2. Archive PDF download scripts
    print("\n2. Archiving PDF download scripts")
    pdf_archive = archive_dir / "pdf_download_scripts"
    pdf_archive.mkdir(exist_ok=True)
    
    for file in FILES_TO_ORGANIZE["archive_pdf_downloads"]:
        src = REPO_ROOT / file
        if src.exists():
            dst = pdf_archive / file
            print(f"   Archiving: {file}")
            shutil.move(str(src), str(dst))
            summary["archived"].append(file)
    
    # 3. Move test data
    print("\n3. Moving test data files")
    for file in FILES_TO_ORGANIZE["test_data"]:
        src = REPO_ROOT / file
        if src.exists():
            # Keep openathens_session_cookies.json, remove others
            if file == "openathens_session_cookies.json":
                print(f"   Keeping: {file}")
                summary["moved_to_examples"].append(f"{file} (kept in root)")
            elif "cookie" in file.lower():
                os.remove(src)
                summary["removed"].append(file)
                print(f"   Removed (privacy): {file}")
            else:
                dst = test_data_dir / file
                print(f"   Moving: {file}")
                shutil.move(str(src), str(dst))
                summary["moved_to_examples"].append(file)
    
    # 4. Skip documentation (keep in root)
    print("\n4. Skipping documentation files (keeping in root)")
    for file in FILES_TO_ORGANIZE["documentation"]:
        src = REPO_ROOT / file
        if src.exists():
            print(f"   Keeping: {file}")
            summary["moved_to_examples"].append(f"{file} (kept in root)")
    
    # 5. Archive utility scripts
    print("\n5. Archiving utility scripts")
    util_archive = archive_dir / "utilities"
    util_archive.mkdir(exist_ok=True)
    
    for file in FILES_TO_ORGANIZE["archive_utilities"]:
        src = REPO_ROOT / file
        if src.exists():
            dst = util_archive / file
            print(f"   Archiving: {file}")
            shutil.move(str(src), str(dst))
            summary["archived"].append(file)
    
    # 6. Archive test directories
    print("\n6. Archiving test directories")
    test_dirs_archive = archive_dir / "test_outputs"
    test_dirs_archive.mkdir(exist_ok=True)
    
    for dir_name in FILES_TO_ORGANIZE["test_directories"]:
        src = REPO_ROOT / dir_name
        if src.exists():
            dst = test_dirs_archive / dir_name
            print(f"   Archiving: {dir_name}")
            shutil.move(str(src), str(dst))
            summary["archived"].append(dir_name)
    
    # 7. Remove fragments
    print("\n7. Removing file fragments")
    for file in FILES_TO_REMOVE:
        src = REPO_ROOT / file
        if src.exists():
            print(f"   Removing: {file}")
            os.remove(src)
            summary["removed"].append(file)
    
    # Create summary file
    summary_file = archive_dir / "CLEANUP_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(f"# Scholar Files Cleanup Summary\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"## Moved to Examples\n")
        for file in summary["moved_to_examples"]:
            f.write(f"- {file}\n")
        
        f.write(f"\n## Archived\n")
        for file in summary["archived"]:
            f.write(f"- {file}\n")
        
        f.write(f"\n## Removed\n")
        for file in summary["removed"]:
            f.write(f"- {file}\n")
        
        f.write(f"\n## Not Found\n")
        for file in summary["not_found"]:
            f.write(f"- {file}\n")
    
    print(f"\n=== Summary ===")
    print(f"Moved to examples: {len(summary['moved_to_examples'])}")
    print(f"Archived: {len(summary['archived'])}")
    print(f"Removed: {len(summary['removed'])}")
    print(f"Not found: {len(summary['not_found'])}")
    print(f"\nArchive directory: {archive_dir}")
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    # Confirm before proceeding
    print("This will organize Scholar-related files from the repository root.")
    print("Files will be moved to appropriate locations or archived.")
    response = input("\nProceed? (yes/no): ")
    
    if response.lower() == "yes":
        organize_files()
        print("\n✅ Cleanup complete!")
    else:
        print("Cleanup cancelled.")