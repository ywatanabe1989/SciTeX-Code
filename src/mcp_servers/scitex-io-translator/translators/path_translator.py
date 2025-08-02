#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 02:52:00 (ywatanabe)"
# File: ./mcp_servers/scitex_io_translator/translators/path_translator.py
# ----------------------------------------
import os
__FILE__ = "./mcp_servers/scitex_io_translator/translators/path_translator.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Path translator for converting between absolute and relative paths."""

import re
from pathlib import Path
from typing import List, Tuple
from scitex import logging

logger = logging.getLogger(__name__)


class PathTranslator:
    """Handles path conversions for SciTeX compliance."""
    
    def __init__(self):
        # Common output directory patterns
        self.output_patterns = [
            'results', 'output', 'outputs', 'figures', 'plots', 
            'data', 'processed', 'cache', 'logs', 'checkpoints'
        ]
        
        # File patterns to convert
        self.file_patterns = [
            r'["\']([A-Za-z]:[/\\].*?)["\']',  # Windows absolute paths
            r'["\'](\/.+?)["\']',  # Unix absolute paths
            r'["\']((?:\.\.[/\\])+.+?)["\']',  # Parent directory paths
        ]
    
    def convert_to_relative_paths(self, code: str) -> str:
        """Convert absolute paths to relative paths."""
        result = code
        
        # Convert absolute paths
        for pattern in self.file_patterns:
            matches = re.finditer(pattern, result)
            for match in reversed(list(matches)):
                abs_path = match.group(1)
                rel_path = self._to_relative_path(abs_path)
                result = result[:match.start()] + f'"{rel_path}"' + result[match.end():]
        
        # Ensure paths follow SciTeX conventions
        result = self._apply_scitex_path_conventions(result)
        
        return result
    
    def ensure_output_dirs(self, code: str) -> str:
        """Add directory creation for output paths in standard Python."""
        lines = code.split('\n')
        new_lines = []
        imports_added = False
        
        # Collect all output paths
        output_paths = self._find_output_paths(code)
        
        # Add imports if needed
        if output_paths and not imports_added:
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    new_lines.extend(lines[:i])
                    new_lines.append('import os')
                    new_lines.append('')
                    new_lines.extend(lines[i:])
                    imports_added = True
                    break
        
        # Add directory creation
        if output_paths:
            # Find where to insert directory creation
            main_start = self._find_main_start(new_lines if imports_added else lines)
            if main_start >= 0:
                lines_to_insert = ['# Create output directories']
                for path in output_paths:
                    lines_to_insert.append(f'os.makedirs(os.path.dirname("{path}"), exist_ok=True)')
                lines_to_insert.append('')
                
                final_lines = (new_lines if imports_added else lines)
                result_lines = (
                    final_lines[:main_start] + 
                    lines_to_insert + 
                    final_lines[main_start:]
                )
                return '\n'.join(result_lines)
        
        return '\n'.join(new_lines) if imports_added else code
    
    def _to_relative_path(self, path: str) -> str:
        """Convert absolute path to relative path."""
        path_obj = Path(path)
        
        # If it's already relative, return as-is
        if not path_obj.is_absolute():
            return path
        
        # Try to make it relative to common directories
        try:
            # Get the file name and parent directory
            file_name = path_obj.name
            parent_name = path_obj.parent.name
            
            # Check if it's in a common output directory
            if parent_name.lower() in self.output_patterns:
                return f'./{parent_name}/{file_name}'
            else:
                # Default to just the filename in current directory
                return f'./{file_name}'
        except Exception:
            # If conversion fails, return original
            return path
    
    def _apply_scitex_path_conventions(self, code: str) -> str:
        """Apply SciTeX path conventions."""
        # Ensure all paths start with ./
        result = re.sub(r'["\']((?!\.\/|\/|[A-Za-z]:)[^"\']+\.(csv|txt|json|pkl|npy|npz|png|jpg|pdf))["\']', 
                       r'"./\1"', code)
        
        # Group outputs by type
        result = self._organize_output_paths(result)
        
        return result
    
    def _organize_output_paths(self, code: str) -> str:
        """Organize output paths by file type."""
        # Map of extensions to preferred directories
        extension_dirs = {
            ('.png', '.jpg', '.jpeg', '.pdf'): 'figures',
            ('.csv', '.txt', '.tsv'): 'data',
            ('.pkl', '.pickle', '.joblib'): 'cache',
            ('.npy', '.npz'): 'arrays',
            ('.json', '.yaml', '.yml'): 'config',
        }
        
        result = code
        
        for extensions, preferred_dir in extension_dirs.items():
            for ext in extensions:
                # Find save operations with these extensions
                pattern = rf'(stx\.io\.save\([^,]+,\s*["\'])([^/]+{ext})["\']'
                result = re.sub(pattern, rf'\1./{preferred_dir}/\2"', result)
        
        return result
    
    def _find_output_paths(self, code: str) -> List[str]:
        """Find all paths that are being written to."""
        output_paths = []
        
        # Patterns that indicate output operations
        output_patterns = [
            r'\.to_csv\(["\'](.+?)["\']',
            r'\.save\(["\'](.+?)["\']',
            r'savefig\(["\'](.+?)["\']',
            r'dump\(.+?,\s*["\'](.+?)["\']',
            r'savetxt\(["\'](.+?)["\']',
            r'open\(["\'](.+?)["\']\s*,\s*["\']w',
        ]
        
        for pattern in output_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                path = match.group(1)
                if '/' in path:  # Only paths with directories
                    output_paths.append(path)
        
        return list(set(output_paths))
    
    def _find_main_start(self, lines: List[str]) -> int:
        """Find where the main code starts."""
        for i, line in enumerate(lines):
            # Look for function definitions or main code
            if (line.strip().startswith('def ') or 
                line.strip().startswith('if __name__') or
                (line.strip() and not line.strip().startswith('#') and 
                 not line.strip().startswith('import') and
                 not line.strip().startswith('from'))):
                return i
        return -1
    
    def count_path_conversions(self, original: str, translated: str) -> int:
        """Count how many paths were converted."""
        # Count paths starting with ./ in translated code
        relative_paths = len(re.findall(r'["\']\./', translated))
        
        # Count absolute paths in original
        absolute_paths = 0
        for pattern in self.file_patterns:
            absolute_paths += len(re.findall(pattern, original))
        
        return min(relative_paths, absolute_paths)  # Conservative estimate