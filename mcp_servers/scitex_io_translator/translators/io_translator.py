#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 02:51:00 (ywatanabe)"
# File: ./mcp_servers/scitex_io_translator/translators/io_translator.py
# ----------------------------------------
import os
__FILE__ = "./mcp_servers/scitex_io_translator/translators/io_translator.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""IO module translator for converting between standard Python and SciTeX."""

import re
import ast
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class IOTranslator:
    """Translates IO operations between standard Python and SciTeX."""
    
    def __init__(self):
        # Define translation patterns
        self.to_scitex_patterns = [
            # pandas operations
            (r'pd\.read_csv\((.*?)\)', r'stx.io.load(\1)'),
            (r'\.to_csv\((.*?)\)', r'stx.io.save(self, \1, symlink_from_cwd=True)'),
            
            # numpy operations
            (r'np\.save\((.*?),\s*(.*?)\)', r'stx.io.save(\2, \1)'),
            (r'np\.load\((.*?)\)', r'stx.io.load(\1)'),
            (r'np\.savez\((.*?),\s*(.*?)\)', r'stx.io.save(\2, \1)'),
            (r'np\.savetxt\((.*?),\s*(.*?)\)', r'stx.io.save(\2, \1)'),
            (r'np\.loadtxt\((.*?)\)', r'stx.io.load(\1)'),
            
            # matplotlib operations
            (r'plt\.savefig\((.*?)\)', r'stx.io.save(fig, \1, symlink_from_cwd=True)'),
            (r'fig\.savefig\((.*?)\)', r'stx.io.save(fig, \1, symlink_from_cwd=True)'),
            
            # pickle operations
            (r'pickle\.dump\((.*?),\s*open\((.*?),\s*["\']wb["\']\)\)', r'stx.io.save(\1, \2)'),
            (r'pickle\.load\(open\((.*?),\s*["\']rb["\']\)\)', r'stx.io.load(\1)'),
            
            # json operations
            (r'json\.dump\((.*?),\s*open\((.*?),\s*["\']w["\']\)\)', r'stx.io.save(\1, \2)'),
            (r'json\.load\(open\((.*?)\)\)', r'stx.io.load(\1)'),
            
            # joblib operations
            (r'joblib\.dump\((.*?),\s*(.*?)\)', r'stx.io.save(\1, \2)'),
            (r'joblib\.load\((.*?)\)', r'stx.io.load(\1)'),
            
            # imports
            (r'import pandas as pd', r'import scitex as stx'),
            (r'import numpy as np', r'import scitex as stx'),
            (r'import matplotlib\.pyplot as plt', r'import scitex as stx'),
            (r'from pathlib import Path', r'import scitex as stx'),
        ]
        
        self.from_scitex_patterns = [
            # Basic stx.io operations
            (r'stx\.io\.load\((.*?)\)', self._determine_load_replacement),
            (r'stx\.io\.save\((.*?),\s*(.*?)(?:,\s*symlink_from_cwd=True)?\)', self._determine_save_replacement),
            
            # Import replacement
            (r'import scitex as stx', self._determine_imports_needed),
        ]
        
        # File extension to operation mapping
        self.extension_map = {
            '.csv': ('pd.read_csv', 'to_csv'),
            '.npy': ('np.load', 'np.save'),
            '.npz': ('np.load', 'np.savez'),
            '.pkl': ('pickle.load', 'pickle.dump'),
            '.pickle': ('pickle.load', 'pickle.dump'),
            '.json': ('json.load', 'json.dump'),
            '.txt': ('np.loadtxt', 'np.savetxt'),
            '.png': ('plt.imread', 'plt.savefig'),
            '.jpg': ('plt.imread', 'plt.savefig'),
            '.jpeg': ('plt.imread', 'plt.savefig'),
            '.pdf': ('', 'plt.savefig'),
        }
    
    def translate_to_scitex(self, code: str) -> str:
        """Translate standard Python IO operations to SciTeX."""
        result = code
        
        # Apply each pattern
        for pattern, replacement in self.to_scitex_patterns:
            result = re.sub(pattern, replacement, result)
        
        # Handle special cases
        result = self._handle_context_managers(result)
        result = self._consolidate_imports(result)
        
        return result
    
    def translate_from_scitex(self, code: str) -> str:
        """Translate SciTeX IO operations back to standard Python."""
        result = code
        
        # Track what libraries are needed
        self.needed_imports = set()
        
        # Apply reverse patterns
        for pattern, replacement_func in self.from_scitex_patterns:
            if callable(replacement_func):
                result = re.sub(pattern, replacement_func, result)
            else:
                result = re.sub(pattern, replacement_func, result)
        
        return result
    
    def _handle_context_managers(self, code: str) -> str:
        """Convert file context managers to stx.io operations."""
        # Pattern for with open(...) as f: constructs
        context_pattern = r'with\s+open\((.*?)\)\s+as\s+(\w+):\s*\n((?:\s+.*\n)*)'
        
        def replace_context(match):
            file_path = match.group(1)
            var_name = match.group(2)
            body = match.group(3)
            
            # Analyze what's being done in the body
            if 'json.dump' in body:
                return f"# Converted from context manager\nstx.io.save(data, {file_path})"
            elif 'json.load' in body:
                return f"# Converted from context manager\ndata = stx.io.load({file_path})"
            elif 'pickle.dump' in body:
                return f"# Converted from context manager\nstx.io.save(data, {file_path})"
            elif 'pickle.load' in body:
                return f"# Converted from context manager\ndata = stx.io.load({file_path})"
            else:
                # Keep original if we can't determine the pattern
                return match.group(0)
        
        return re.sub(context_pattern, replace_context, code, flags=re.MULTILINE)
    
    def _consolidate_imports(self, code: str) -> str:
        """Consolidate multiple stx imports into one."""
        lines = code.split('\n')
        new_lines = []
        has_stx_import = False
        
        for line in lines:
            if 'import scitex as stx' in line and not has_stx_import:
                new_lines.append(line)
                has_stx_import = True
            elif 'import scitex as stx' in line and has_stx_import:
                # Skip duplicate imports
                continue
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _determine_load_replacement(self, match):
        """Determine the appropriate load function based on file extension."""
        file_path = match.group(1).strip()
        
        # Try to extract file extension
        ext_match = re.search(r'\.(\w+)["\']?\s*\)', file_path)
        if ext_match:
            ext = '.' + ext_match.group(1)
            if ext in self.extension_map:
                load_func, _ = self.extension_map[ext]
                self._add_import_for_function(load_func)
                return f'{load_func}({file_path})'
        
        # Default to pandas for CSV
        self.needed_imports.add('pandas')
        return f'pd.read_csv({file_path})'
    
    def _determine_save_replacement(self, match):
        """Determine the appropriate save function based on context."""
        data_var = match.group(1).strip()
        file_path = match.group(2).strip()
        
        # Try to extract file extension
        ext_match = re.search(r'\.(\w+)["\']?\s*\)', file_path)
        if ext_match:
            ext = '.' + ext_match.group(1)
            if ext in self.extension_map:
                _, save_func = self.extension_map[ext]
                self._add_import_for_function(save_func)
                
                if save_func == 'to_csv':
                    return f'{data_var}.to_csv({file_path})'
                elif save_func in ['plt.savefig', 'fig.savefig']:
                    return f'{data_var}.savefig({file_path})'
                else:
                    return f'{save_func}({file_path}, {data_var})'
        
        # Default to numpy
        self.needed_imports.add('numpy')
        return f'np.save({file_path}, {data_var})'
    
    def _determine_imports_needed(self, match):
        """Replace stx import with needed standard imports."""
        imports = []
        
        if 'pandas' in self.needed_imports:
            imports.append('import pandas as pd')
        if 'numpy' in self.needed_imports:
            imports.append('import numpy as np')
        if 'matplotlib' in self.needed_imports:
            imports.append('import matplotlib.pyplot as plt')
        if 'pickle' in self.needed_imports:
            imports.append('import pickle')
        if 'json' in self.needed_imports:
            imports.append('import json')
        if 'joblib' in self.needed_imports:
            imports.append('import joblib')
        
        return '\n'.join(imports) if imports else '# Standard imports'
    
    def _add_import_for_function(self, func: str):
        """Add necessary import based on function name."""
        if func.startswith('pd.'):
            self.needed_imports.add('pandas')
        elif func.startswith('np.'):
            self.needed_imports.add('numpy')
        elif func.startswith('plt.') or func == 'fig.savefig':
            self.needed_imports.add('matplotlib')
        elif func.startswith('pickle.'):
            self.needed_imports.add('pickle')
        elif func.startswith('json.'):
            self.needed_imports.add('json')
        elif func.startswith('joblib.'):
            self.needed_imports.add('joblib')
    
    def extract_io_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Extract all IO patterns from code for analysis."""
        patterns = []
        
        # Define patterns to search for
        io_patterns = [
            ('pandas_read', r'pd\.read_\w+\([^)]+\)'),
            ('pandas_write', r'\.to_\w+\([^)]+\)'),
            ('numpy_load', r'np\.load\w*\([^)]+\)'),
            ('numpy_save', r'np\.save\w*\([^)]+\)'),
            ('matplotlib_save', r'(?:plt|fig)\.savefig\([^)]+\)'),
            ('pickle_ops', r'pickle\.(?:dump|load)\([^)]+\)'),
            ('json_ops', r'json\.(?:dump|load)\([^)]+\)'),
            ('stx_io', r'stx\.io\.(?:save|load)\([^)]+\)'),
            ('file_open', r'open\([^)]+\)'),
        ]
        
        for pattern_type, pattern in io_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                patterns.append({
                    'type': pattern_type,
                    'code': match.group(0),
                    'line': code[:match.start()].count('\n') + 1,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return patterns
    
    def count_conversions(self, original: str, translated: str) -> int:
        """Count how many IO operations were converted."""
        original_patterns = self.extract_io_patterns(original)
        translated_patterns = self.extract_io_patterns(translated)
        
        # Count stx.io operations in translated code
        stx_count = sum(1 for p in translated_patterns if p['type'] == 'stx_io')
        
        return stx_count