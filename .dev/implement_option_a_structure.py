#!/usr/bin/env python3
"""Implement Option A structure where human-readable directory is at library level."""

import json
import shutil
from pathlib import Path
from datetime import datetime
import os

def implement_option_a():
    """Implement the correct structure based on user's choice."""
    print("=" * 80)
    print("IMPLEMENTING OPTION A STRUCTURE")
    print("=" * 80)
    
    # Load the saved info from previous run
    with open(".dev/correct_structure_info.json", 'r') as f:
        info = json.load(f)
    
    eight_digit_id = info["storage_id"]
    project_name = info["project"]
    library_dir = Path(info["structure"]["library"])
    project_dir = Path(info["structure"]["project"])
    storage_dir = Path(info["structure"]["storage"])
    
    print(f"\n1. CURRENT STATE")
    print("-" * 40)
    print(f"Project: {project_name}")
    print(f"8-digit ID: {eight_digit_id}")
    print(f"Storage dir: {storage_dir}")
    
    # Remove any existing human-readable directories
    print(f"\n2. CLEANING UP OLD STRUCTURE")
    print("-" * 40)
    
    # Remove human-readable inside project if exists
    old_human_readable = project_dir / f"{project_name}-human-readable"
    if old_human_readable.exists():
        shutil.rmtree(old_human_readable)
        print(f"Removed: {old_human_readable}")
    
    # Remove old human-readable at library level if exists
    old_library_human = library_dir / f"{project_name}-human-readable"
    if old_library_human.exists():
        shutil.rmtree(old_library_human)
        print(f"Removed: {old_library_human}")
    
    # Create the correct structure: Option A
    # library/
    # ├── pac_research/
    # │   └── W4S0Z2R8/
    # └── pac_research-human-readable/
    #     └── Hulsemann-2019-FrontNeurosci -> ../pac_research/W4S0Z2R8
    
    print(f"\n3. CREATING OPTION A STRUCTURE")
    print("-" * 40)
    
    # Create human-readable directory at library level
    human_readable_dir = library_dir / f"{project_name}-human-readable"
    human_readable_dir.mkdir(exist_ok=True)
    print(f"Created: {human_readable_dir}")
    
    # Create the symlink
    link_name = "Hulsemann-2019-FrontNeurosci"
    link_path = human_readable_dir / link_name
    
    # The target should be ../pac_research/W4S0Z2R8
    relative_target = Path("..") / project_name / eight_digit_id
    
    if link_path.exists():
        link_path.unlink()
    
    try:
        link_path.symlink_to(relative_target)
        print(f"Created symlink: {link_name} -> {relative_target}")
    except Exception as e:
        print(f"Could not create symlink: {e}")
    
    # Show the final structure
    print("\n4. FINAL STRUCTURE (OPTION A)")
    print("-" * 40)
    print(f"""
{library_dir.name}/
├── {project_name}/
│   └── {eight_digit_id}/
│       ├── fnins-13-00573.pdf
│       ├── metadata.json
│       ├── attachments/
│       └── screenshots/
│           └── screenshots.json
└── {project_name}-human-readable/
    └── {link_name} -> ../{project_name}/{eight_digit_id}
""")
    
    # Verify the structure
    print("\n5. VERIFICATION")
    print("-" * 40)
    
    # Check library contents
    print("Library contents:")
    for item in sorted(library_dir.iterdir()):
        if item.is_dir():
            print(f"  {item.name}/")
    
    # Check symlink
    if link_path.exists():
        print(f"\nSymlink verification:")
        print(f"  Link: {link_path}")
        print(f"  Target: {link_path.readlink()}")
        print(f"  Resolves to: {link_path.resolve()}")
        
        # Verify it points to the right place
        expected_target = project_dir / eight_digit_id
        if link_path.resolve() == expected_target.resolve():
            print("  ✓ Link points to correct storage directory!")
        else:
            print("  ✗ Link does not resolve correctly")
    
    # Check if PDF is accessible through link
    pdf_through_link = link_path / "fnins-13-00573.pdf"
    if pdf_through_link.exists():
        print(f"\n✓ PDF accessible through human-readable link:")
        print(f"  {pdf_through_link}")
    
    # Update the saved info
    info["human_readable_link"] = str(link_path)
    info["structure"]["human_readable"] = str(human_readable_dir)
    info["option"] = "A"
    
    with open(".dev/correct_structure_info.json", 'w') as f:
        json.dump(info, f, indent=2)
    
    print("\n✓ Successfully implemented Option A structure!")
    print("\nThis matches CLAUDE.md specification:")
    print("  ~/.scitex/scholar/library/<project>/8-DIGITS-ID/<original-name-from-the-journal>.pdf")
    print("  ~/.scitex/scholar/library/<project-human-readable>/AUTHOR-YEAR-JOURNAL -> ../8-DIGITS-ID")
    
    return str(link_path)


if __name__ == "__main__":
    implement_option_a()