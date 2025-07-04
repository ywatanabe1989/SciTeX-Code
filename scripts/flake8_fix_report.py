#!/usr/bin/env python3
"""Generate a report after running flake8 fixes."""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_report(results_file: str = "flake8_fix_results.json"):
    """Generate a human-readable report from fix results."""
    
    # Create report path
    report_path = Path(f"flake8_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    # Default report content
    report = f"""# Flake8 Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

This report summarizes the automatic fixes applied to resolve flake8 F821 (undefined name) and F824 (unused global) errors in the SciTeX codebase.

"""
    
    # Try to load results if they exist
    if Path(results_file).exists():
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            report += f"""
### Statistics
- **Fixed**: {len(results.get('fixed', []))} errors
- **Failed**: {len(results.get('failed', []))} errors  
- **Skipped**: {len(results.get('skipped', []))} files

"""
            
            if results.get('fixed'):
                report += "### Successfully Fixed\n\n"
                for fix in results['fixed']:
                    report += f"- ✓ {fix}\n"
                report += "\n"
            
            if results.get('failed'):
                report += "### Failed to Fix (Manual Review Required)\n\n"
                for fail in results['failed']:
                    report += f"- ✗ {fail}\n"
                report += "\n"
            
            if results.get('skipped'):
                report += "### Skipped Files\n\n"
                for skip in results['skipped']:
                    report += f"- {skip}\n"
                report += "\n"
                
        except Exception as e:
            report += f"\nError loading results: {e}\n"
    
    # Add recommendations
    report += """
## Recommendations

1. **Review Failed Fixes**: Some errors require manual intervention:
   - `api_key` parameter issues in anthropic_provider.py
   - `freqs` and `power` variables in _psd.py (likely need to be function parameters)
   - Complex class definitions like `ClassifierServer`

2. **Test Changes**: After fixes are applied:
   - Run the test suite to ensure no functionality is broken
   - Check that imports don't create circular dependencies
   - Verify that removed global declarations weren't actually needed

3. **Common Patterns Fixed**:
   - Missing imports for standard libraries (matplotlib, numpy, etc.)
   - Missing imports for typing annotations
   - Unused global declarations removed
   - Missing main() function definitions added

4. **Backup Location**: All modified files have been backed up to the `flake8_backups/` directory.

## Next Steps

1. Run tests: `pytest`
2. Run flake8 again to verify fixes: `flake8 --select=F821,F824`
3. Review and manually fix any remaining issues
4. Commit the changes once verified
"""
    
    # Write report
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"Report generated: {report_path}")
    return report_path


if __name__ == "__main__":
    generate_report()