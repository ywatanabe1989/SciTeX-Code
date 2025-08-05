#!/usr/bin/env python3
"""
Update symlinks to use hyphens instead of spaces in journal names
"""

import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig

def update_symlinks_with_hyphens():
    """Update symlinks to use hyphens in journal names."""
    
    print("🔗 Updating PAC Symlinks to Use Hyphens")
    print("=" * 50)
    
    config = ScholarConfig()
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    if not pac_dir.exists():
        print(f"❌ PAC directory doesn't exist: {pac_dir}")
        return
    
    updated_count = 0
    
    # Find symlinks with spaces in names
    for symlink_path in pac_dir.glob("*"):
        if symlink_path.is_symlink():
            current_name = symlink_path.name
            
            # Check if name has spaces that should be hyphens
            if " " in current_name:
                # Create new name with hyphens
                new_name = current_name.replace(" ", "-")
                new_path = pac_dir / new_name
                
                print(f"🔄 Updating: {current_name}")
                print(f"   -> {new_name}")
                
                try:
                    # Get the target of the current symlink
                    target = symlink_path.readlink()
                    
                    # Remove old symlink
                    symlink_path.unlink()
                    
                    # Create new symlink with hyphenated name
                    new_path.symlink_to(target)
                    
                    updated_count += 1
                    print(f"   ✅ Updated successfully")
                    
                except Exception as e:
                    print(f"   💥 Error: {e}")
                    # Try to restore original symlink
                    try:
                        symlink_path.symlink_to(target)
                    except:
                        pass
    
    print(f"\n📊 Results:")
    print(f"   Updated symlinks: {updated_count}")
    
    # Show current state
    print(f"\n🔗 Current PAC symlinks:")
    for symlink_path in sorted(pac_dir.glob("*"))[:5]:
        if symlink_path.is_symlink():
            print(f"   {symlink_path.name}")

if __name__ == "__main__":
    update_symlinks_with_hyphens()