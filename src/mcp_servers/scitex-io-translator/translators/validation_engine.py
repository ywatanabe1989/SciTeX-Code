#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 02:56:00 (ywatanabe)"
# File: ./mcp_servers/scitex_io_translator/translators/validation_engine.py
# ----------------------------------------
import os
__FILE__ = "./mcp_servers/scitex_io_translator/translators/validation_engine.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Validation engine for checking SciTeX compliance."""

import re
from typing import Dict, List, Any, Optional
import ast
import logging

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Validates code against SciTeX guidelines."""
    
    def __init__(self):
        # Define validation rules
        self.rules = {
            'header': {
                'description': 'SciTeX header format',
                'severity': 'error',
                'patterns': {
                    'shebang': r'^#!/usr/bin/env python3',
                    'encoding': r'^# -\*- coding: utf-8 -\*-',
                    'timestamp': r'^# Timestamp: ".*"',
                    'file': r'^# File: .*',
                    '__FILE__': r'^__FILE__ = ',
                    '__DIR__': r'^__DIR__ = os\.path\.dirname\(__FILE__\)'
                }
            },
            'imports': {
                'description': 'Import conventions',
                'severity': 'warning',
                'checks': [
                    self._check_scitex_import,
                    self._check_import_order
                ]
            },
            'io_operations': {
                'description': 'IO operation compliance',
                'severity': 'error',
                'checks': [
                    self._check_io_operations,
                    self._check_path_format
                ]
            },
            'structure': {
                'description': 'Code structure',
                'severity': 'warning',
                'checks': [
                    self._check_main_function,
                    self._check_run_main
                ]
            },
            'paths': {
                'description': 'Path conventions',
                'severity': 'warning',
                'checks': [
                    self._check_relative_paths,
                    self._check_output_organization
                ]
            }
        }
    
    def validate(self, code: str, strict: bool = False) -> Dict[str, Any]:
        """Validate code against SciTeX guidelines."""
        issues = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check header format
        header_issues = self._validate_header(code, strict)
        issues['errors'].extend(header_issues['errors'])
        issues['warnings'].extend(header_issues['warnings'])
        
        # Check imports
        import_issues = self._validate_imports(code)
        issues['warnings'].extend(import_issues)
        
        # Check IO operations
        io_issues = self._validate_io_operations(code)
        issues['errors'].extend(io_issues['errors'])
        issues['warnings'].extend(io_issues['warnings'])
        
        # Check structure
        structure_issues = self._validate_structure(code)
        issues['warnings'].extend(structure_issues)
        
        # Check paths
        path_issues = self._validate_paths(code)
        issues['warnings'].extend(path_issues)
        
        # Add suggestions
        suggestions = self.get_suggestions(code)
        issues['suggestions'].extend(suggestions)
        
        return issues
    
    def _validate_header(self, code: str, strict: bool) -> Dict[str, List[str]]:
        """Validate SciTeX header format."""
        issues = {'errors': [], 'warnings': []}
        lines = code.split('\n')
        
        # Check required header elements
        header_patterns = self.rules['header']['patterns']
        
        # In strict mode, all header elements are required
        if strict:
            if not lines or not re.match(header_patterns['shebang'], lines[0]):
                issues['errors'].append("Missing shebang: #!/usr/bin/env python3")
            
            if len(lines) < 2 or not re.match(header_patterns['encoding'], lines[1]):
                issues['errors'].append("Missing encoding declaration")
            
            # Check for timestamp
            has_timestamp = any(re.match(header_patterns['timestamp'], line) for line in lines[:10])
            if not has_timestamp:
                issues['errors'].append("Missing timestamp in header")
            
            # Check for __FILE__ and __DIR__
            has_file = any(re.match(header_patterns['__FILE__'], line) for line in lines[:20])
            has_dir = any(re.match(header_patterns['__DIR__'], line) for line in lines[:20])
            
            if not has_file:
                issues['errors'].append("Missing __FILE__ definition")
            if not has_dir:
                issues['errors'].append("Missing __DIR__ definition")
        else:
            # In non-strict mode, these are warnings
            if not lines or not lines[0].startswith('#!'):
                issues['warnings'].append("Consider adding shebang: #!/usr/bin/env python3")
        
        return issues
    
    def _validate_imports(self, code: str) -> List[str]:
        """Validate import conventions."""
        issues = []
        
        # Check for scitex import
        if 'stx.io.' in code and 'import scitex as stx' not in code:
            issues.append("Using stx.io without importing scitex as stx")
        
        # Check import style
        if 'from scitex.io import' in code:
            issues.append("Prefer 'import scitex as stx' over individual imports")
        
        return issues
    
    def _validate_io_operations(self, code: str) -> Dict[str, List[str]]:
        """Validate IO operations."""
        issues = {'errors': [], 'warnings': []}
        
        # Check for non-scitex IO operations when scitex is imported
        if 'import scitex as stx' in code:
            # These should be converted to stx.io
            patterns = [
                (r'pd\.read_csv\(', "Use stx.io.load() instead of pd.read_csv()"),
                (r'\.to_csv\(', "Use stx.io.save() instead of .to_csv()"),
                (r'np\.save\(', "Use stx.io.save() instead of np.save()"),
                (r'plt\.savefig\(', "Use stx.io.save() instead of plt.savefig()"),
            ]
            
            for pattern, message in patterns:
                if re.search(pattern, code):
                    issues['warnings'].append(message)
        
        return issues
    
    def _validate_structure(self, code: str) -> List[str]:
        """Validate code structure."""
        issues = []
        
        # Check for main function
        if re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', code):
            if 'def main(' not in code:
                issues.append("Script has if __name__ == '__main__' but no main() function")
            
            # Check for run_main pattern
            if 'import scitex as stx' in code and 'run_main()' not in code:
                issues.append("Consider using run_main() pattern for proper SciTeX initialization")
        
        return issues
    
    def _validate_paths(self, code: str) -> List[str]:
        """Validate path conventions."""
        issues = []
        
        # Check for absolute paths
        abs_path_patterns = [
            r'["\'][A-Za-z]:[/\\]',  # Windows
            r'["\']\/(?!\.)',  # Unix absolute (not ./)
        ]
        
        for pattern in abs_path_patterns:
            if re.search(pattern, code):
                issues.append("Avoid absolute paths; use relative paths starting with ./")
        
        # Check for organized output paths
        if 'stx.io.save' in code:
            # Check if outputs are organized
            save_calls = re.findall(r'stx\.io\.save\([^,]+,\s*["\']([^"\']+)', code)
            for path in save_calls:
                if not path.startswith('./'):
                    issues.append(f"Output path '{path}' should start with ./")
                
                # Check if it's organized by type
                if any(ext in path for ext in ['.png', '.jpg', '.pdf']):
                    if 'figures/' not in path and 'plots/' not in path:
                        issues.append(f"Consider organizing image '{path}' in ./figures/")
        
        return issues
    
    def _check_scitex_import(self, code: str) -> Optional[str]:
        """Check for proper scitex import."""
        if 'stx.' in code and 'import scitex as stx' not in code:
            return "Using stx.* without proper import"
        return None
    
    def _check_import_order(self, code: str) -> Optional[str]:
        """Check import order."""
        # This is a simplified check
        lines = code.split('\n')
        import_lines = [l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')]
        
        if len(import_lines) > 5:
            return "Consider organizing imports: standard library, third-party, local"
        return None
    
    def _check_io_operations(self, code: str) -> Optional[str]:
        """Check IO operations compliance."""
        if 'import scitex as stx' in code:
            if 'open(' in code and 'with open' in code:
                return "Consider using stx.io.load/save instead of open()"
        return None
    
    def _check_path_format(self, code: str) -> Optional[str]:
        """Check path format compliance."""
        # Look for paths without ./
        bad_paths = re.findall(r'["\'](?!\.\/|\/|[A-Za-z]:)([a-zA-Z0-9_]+\.[a-zA-Z]+)["\']', code)
        if bad_paths:
            return f"Paths should start with ./: {', '.join(bad_paths[:3])}"
        return None
    
    def _check_main_function(self, code: str) -> Optional[str]:
        """Check for main function."""
        if len(code.split('\n')) > 20 and 'def main' not in code:
            return "Consider organizing code in a main() function"
        return None
    
    def _check_run_main(self, code: str) -> Optional[str]:
        """Check for run_main pattern."""
        if 'def main(' in code and 'if __name__' in code:
            if 'run_main' not in code and 'import scitex as stx' in code:
                return "Consider using run_main() for proper SciTeX initialization"
        return None
    
    def _check_relative_paths(self, code: str) -> Optional[str]:
        """Check for relative paths."""
        if re.search(r'["\']\/[^.]', code):
            return "Use relative paths instead of absolute paths"
        return None
    
    def _check_output_organization(self, code: str) -> Optional[str]:
        """Check output organization."""
        # This is a simplified check
        if '.png' in code or '.jpg' in code:
            if 'figures/' not in code and 'plots/' not in code:
                return "Consider organizing image outputs in ./figures/"
        return None
    
    def get_suggestions(self, code: str) -> List[str]:
        """Get improvement suggestions."""
        suggestions = []
        
        # Suggest config extraction
        hardcoded_paths = re.findall(r'["\']\.\/[^"\']+\.[a-zA-Z]+["\']', code)
        if len(set(hardcoded_paths)) > 3:
            suggestions.append("Consider extracting paths to CONFIG/PATH.yaml")
        
        # Suggest using symlink_from_cwd
        if 'stx.io.save' in code and 'symlink_from_cwd' not in code:
            suggestions.append("Consider using symlink_from_cwd=True for outputs")
        
        # Suggest organizing by file type
        if any(ext in code for ext in ['.png', '.csv', '.pkl', '.npy']):
            suggestions.append("Organize outputs by type: ./figures/, ./data/, ./cache/")
        
        return suggestions