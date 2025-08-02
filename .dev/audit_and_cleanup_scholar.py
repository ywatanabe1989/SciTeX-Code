#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 02:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/.dev/audit_and_cleanup_scholar.py
# ----------------------------------------
"""
SciTeX Scholar Audit and Cleanup Tool

This script audits both the ~/.scitex/scholar directory and source code,
identifying obsolete files and providing cleanup recommendations.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict

# Add src to path
sys.path.insert(0, "src")

from scitex.scholar.config._PathManager import PathManager, TidinessConstraints


@dataclass
class AuditResult:
    """Results of the audit process."""
    
    # Directory statistics
    total_files: int = 0
    total_size_mb: float = 0.0
    
    # Obsolete files
    obsolete_files: List[str] = None
    old_backup_files: List[str] = None
    duplicate_files: List[str] = None
    
    # Source code analysis
    versioned_source_files: List[str] = None
    unused_source_files: List[str] = None
    
    # Cleanup recommendations
    files_to_archive: List[str] = None
    files_to_delete: List[str] = None
    directories_to_reorganize: List[str] = None
    
    def __post_init__(self):
        # Initialize lists if None
        for field_name in ['obsolete_files', 'old_backup_files', 'duplicate_files',
                          'versioned_source_files', 'unused_source_files',
                          'files_to_archive', 'files_to_delete', 'directories_to_reorganize']:
            if getattr(self, field_name) is None:
                setattr(self, field_name, [])


class ScholarAuditor:
    """Comprehensive auditor for SciTeX Scholar directory and source code."""
    
    def __init__(self, scholar_dir: Path = None, source_dir: Path = None):
        self.scholar_dir = scholar_dir or Path.home() / ".scitex" / "scholar"
        self.source_dir = source_dir or Path("src/scitex/scholar")
        self.path_manager = PathManager()
        self.result = AuditResult()
        
    def audit_scholar_directory(self) -> Dict:
        """Audit the ~/.scitex/scholar directory structure."""
        print("🔍 Auditing ~/.scitex/scholar directory...")
        
        if not self.scholar_dir.exists():
            print(f"❌ Scholar directory not found: {self.scholar_dir}")
            return {}
            
        # Get directory statistics
        total_size = 0
        file_count = 0
        
        for file_path in self.scholar_dir.rglob("*"):
            if file_path.is_file():
                file_count += 1
                try:
                    total_size += file_path.stat().st_size
                except (PermissionError, OSError):
                    pass
                    
        self.result.total_files = file_count
        self.result.total_size_mb = total_size / (1024 * 1024)
        
        # Find obsolete files
        self._find_obsolete_files()
        self._find_old_backup_files()
        self._find_duplicate_files()
        
        print(f"📊 Found {file_count:,} files ({self.result.total_size_mb:.1f} MB)")
        print(f"🗑️  Obsolete files: {len(self.result.obsolete_files)}")
        print(f"📦 Old backup files: {len(self.result.old_backup_files)}")
        print(f"👥 Duplicate files: {len(self.result.duplicate_files)}")
        
        return self._get_directory_breakdown()
        
    def _find_obsolete_files(self):
        """Find obsolete files in the scholar directory."""
        obsolete_patterns = [
            r"\.old/",
            r"---",
            r"_backup",
            r"_tmp",
            r"\.tmp",
            r"\.bak",
            r"\.orig",
            r"_old",
            r"regression_test",
        ]
        
        for file_path in self.scholar_dir.rglob("*"):
            if file_path.is_file():
                file_str = str(file_path)
                for pattern in obsolete_patterns:
                    if pattern in file_str:
                        self.result.obsolete_files.append(file_str)
                        break
                        
    def _find_old_backup_files(self):
        """Find old backup files that can be safely removed."""
        cutoff_date = datetime.now() - timedelta(days=30)  # 30 days old
        
        for file_path in self.scholar_dir.rglob("*"):
            if file_path.is_file():
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date and any(pattern in str(file_path) for pattern in ['.old', '_backup', '---']):
                        self.result.old_backup_files.append(str(file_path))
                except (PermissionError, OSError):
                    pass
                    
    def _find_duplicate_files(self):
        """Find potential duplicate files."""
        # Simple duplicate detection based on size and name patterns
        file_sizes = {}
        
        for file_path in self.scholar_dir.rglob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size in file_sizes:
                        file_sizes[size].append(str(file_path))
                    else:
                        file_sizes[size] = [str(file_path)]
                except (PermissionError, OSError):
                    pass
                    
        # Find files with same size (potential duplicates)
        for size, files in file_sizes.items():
            if len(files) > 1 and size > 1024:  # Only check files > 1KB
                self.result.duplicate_files.extend(files)
                
    def _get_directory_breakdown(self) -> Dict:
        """Get detailed breakdown of directory usage."""
        breakdown = {}
        
        for item in self.scholar_dir.iterdir():
            if item.is_dir():
                size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                file_count = sum(1 for f in item.rglob("*") if f.is_file())
                breakdown[item.name] = {
                    "size_mb": size / (1024 * 1024),
                    "file_count": file_count,
                    "path": str(item)
                }
                
        return breakdown
        
    def audit_source_code(self) -> Dict:
        """Audit the source code for obsolete files."""
        print("\n🔍 Auditing source code...")
        
        if not self.source_dir.exists():
            print(f"❌ Source directory not found: {self.source_dir}")
            return {}
            
        # Find versioned files
        self._find_versioned_source_files()
        self._find_unused_source_files()
        
        print(f"📝 Versioned source files: {len(self.result.versioned_source_files)}")
        print(f"🚫 Potentially unused files: {len(self.result.unused_source_files)}")
        
        return self._get_source_breakdown()
        
    def _find_versioned_source_files(self):
        """Find versioned source files (e.g., *_v01.py, *_old.py)."""
        version_patterns = [
            r"_v\d+",
            r"_old",
            r"_backup",
            r"_deprecated",
            r"\.old/",
            r"-not-",
            r"-with-",
            r"-without-",
        ]
        
        for file_path in self.source_dir.rglob("*.py"):
            file_str = str(file_path)
            for pattern in version_patterns:
                if pattern in file_str:
                    self.result.versioned_source_files.append(file_str)
                    break
                    
    def _find_unused_source_files(self):
        """Find potentially unused source files."""
        # This is a simplified approach - in practice, you'd use AST analysis
        all_py_files = list(self.source_dir.rglob("*.py"))
        
        for file_path in all_py_files:
            # Skip __init__.py and already identified versioned files
            if (file_path.name == "__init__.py" or 
                str(file_path) in self.result.versioned_source_files):
                continue
                
            # Check if file is imported anywhere (very basic check)
            module_name = file_path.stem
            is_imported = False
            
            for other_file in all_py_files:
                if other_file == file_path:
                    continue
                    
                try:
                    content = other_file.read_text()
                    if f"import {module_name}" in content or f"from {module_name}" in content:
                        is_imported = True
                        break
                except (PermissionError, UnicodeDecodeError):
                    pass
                    
            if not is_imported:
                self.result.unused_source_files.append(str(file_path))
                
    def _get_source_breakdown(self) -> Dict:
        """Get breakdown of source code structure."""
        breakdown = {}
        
        for item in self.source_dir.rglob("*"):
            if item.is_dir():
                py_files = list(item.glob("*.py"))
                breakdown[str(item.relative_to(self.source_dir))] = {
                    "py_files": len(py_files),
                    "total_files": len(list(item.glob("*"))),
                }
                
        return breakdown
        
    def generate_cleanup_recommendations(self):
        """Generate cleanup recommendations."""
        print("\n💡 Generating cleanup recommendations...")
        
        # Files to archive (move to backup)
        self.result.files_to_archive.extend(self.result.versioned_source_files)
        
        # Files to delete (old backups > 30 days)
        self.result.files_to_delete.extend(self.result.old_backup_files)
        
        # Directories to reorganize
        for file_path in self.result.obsolete_files:
            dir_path = str(Path(file_path).parent)
            if dir_path not in self.result.directories_to_reorganize:
                self.result.directories_to_reorganize.append(dir_path)
                
    def create_cleanup_script(self, output_path: Path = None):
        """Create a cleanup script based on recommendations."""
        if output_path is None:
            output_path = Path(".dev/cleanup_scholar.sh")
            
        script_content = f"""#!/bin/bash
# SciTeX Scholar Cleanup Script
# Generated on: {datetime.now().isoformat()}
# 
# This script will clean up obsolete files in the SciTeX Scholar system.
# IMPORTANT: Review all operations before running!

set -e  # Exit on error

echo "🧹 SciTeX Scholar Cleanup Script"
echo "================================="

# Backup important files first
BACKUP_DIR="$HOME/.scitex/scholar/backup/cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup in $BACKUP_DIR"

# Archive versioned source files
echo "📝 Archiving versioned source files..."
"""

        # Add file operations
        for file_path in self.result.files_to_archive[:10]:  # Limit to first 10
            script_content += f'cp "{file_path}" "$BACKUP_DIR/" 2>/dev/null || true\n'
            
        script_content += """
# Clean up old backup files (>30 days)
echo "🗑️  Removing old backup files..."
"""

        for file_path in self.result.files_to_delete[:10]:  # Limit to first 10
            script_content += f'rm -f "{file_path}" 2>/dev/null || true\n'
            
        script_content += """
echo "✅ Cleanup complete!"
echo "📊 Summary:"
echo "  - Files archived: {archived_count}"
echo "  - Files deleted: {deleted_count}"
echo "  - Backup location: $BACKUP_DIR"
""".format(
            archived_count=len(self.result.files_to_archive),
            deleted_count=len(self.result.files_to_delete)
        )
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(script_content)
        output_path.chmod(0o755)
        
        print(f"📝 Cleanup script created: {output_path}")
        
    def run_maintenance(self):
        """Run PathManager maintenance."""
        print("\n🔧 Running PathManager maintenance...")
        
        results = self.path_manager.perform_maintenance()
        
        print("📊 Maintenance results:")
        for key, value in results.items():
            print(f"  - {key}: {value}")
            
    def save_audit_report(self, output_path: Path = None):
        """Save detailed audit report."""
        if output_path is None:
            output_path = Path(".dev/scholar_audit_report.json")
            
        report = {
            "audit_date": datetime.now().isoformat(),
            "scholar_directory": str(self.scholar_dir),
            "source_directory": str(self.source_dir),
            "results": asdict(self.result),
            "path_manager_stats": self.path_manager.get_storage_stats(),
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📊 Audit report saved: {output_path}")
        
    def print_summary(self):
        """Print audit summary."""
        print("\n📊 AUDIT SUMMARY")
        print("=" * 50)
        print(f"📁 Scholar Directory: {self.scholar_dir}")
        print(f"📝 Source Directory: {self.source_dir}")
        print(f"📊 Total Files: {self.result.total_files:,}")
        print(f"💾 Total Size: {self.result.total_size_mb:.1f} MB")
        print()
        print("🗑️  Files to Clean:")
        print(f"  - Obsolete files: {len(self.result.obsolete_files)}")
        print(f"  - Old backups: {len(self.result.old_backup_files)}")
        print(f"  - Duplicates: {len(self.result.duplicate_files)}")
        print(f"  - Versioned source: {len(self.result.versioned_source_files)}")
        print(f"  - Unused source: {len(self.result.unused_source_files)}")
        print()
        print("💡 Recommendations:")
        print(f"  - Archive: {len(self.result.files_to_archive)} files")
        print(f"  - Delete: {len(self.result.files_to_delete)} files")
        print(f"  - Reorganize: {len(self.result.directories_to_reorganize)} directories")
        

def main():
    """Main audit function."""
    print("🚀 SciTeX Scholar Audit & Cleanup Tool")
    print("=" * 60)
    
    auditor = ScholarAuditor()
    
    # Run audits
    scholar_breakdown = auditor.audit_scholar_directory()
    source_breakdown = auditor.audit_source_code()
    
    # Generate recommendations
    auditor.generate_cleanup_recommendations()
    
    # Run maintenance
    auditor.run_maintenance()
    
    # Create outputs
    auditor.create_cleanup_script()
    auditor.save_audit_report()
    
    # Print summary
    auditor.print_summary()
    
    print("\n✅ Audit complete!")
    print("📝 Review the generated cleanup script before running it.")
    print("📊 Check the audit report for detailed analysis.")


if __name__ == "__main__":
    main()

# EOF