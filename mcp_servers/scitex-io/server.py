#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:03:00 (ywatanabe)"
# File: ./mcp_servers/scitex-io/server.py
# ----------------------------------------

"""MCP server for SciTeX IO module operations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Tuple
from scitex_base.base_server import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexIOMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX IO module translations and operations."""
    
    def __init__(self):
        super().__init__("io", "0.1.0")
        self.create_translation_tools("stx.io")
        
        # IO operation patterns
        self.load_patterns = [
            # Pandas
            (r"pd\.read_csv\((.*?)\)", "pandas", "csv"),
            (r"pd\.read_excel\((.*?)\)", "pandas", "excel"),
            (r"pd\.read_hdf\((.*?)\)", "pandas", "hdf5"),
            (r"pd\.read_json\((.*?)\)", "pandas", "json"),
            # NumPy
            (r"np\.load\((.*?)\)", "numpy", "npy"),
            (r"np\.loadtxt\((.*?)\)", "numpy", "txt"),
            # PyTorch
            (r"torch\.load\((.*?)\)", "torch", "pth"),
            # JSON
            (r"json\.load\(open\((.*?)\)\)", "json", "json"),
            # Pickle
            (r"pickle\.load\(open\((.*?),\s*['\"]rb['\"]\)\)", "pickle", "pkl"),
            # YAML
            (r"yaml\.load\(open\((.*?)\)", "yaml", "yaml"),
            # Generic file read
            (r"open\((.*?),\s*['\"]r['\"].*?\)\.read\(\)", "builtin", "txt"),
        ]
        
        self.save_patterns = [
            # Pandas
            (r"\.to_csv\((.*?)\)", "pandas", "csv"),
            (r"\.to_excel\((.*?)\)", "pandas", "excel"),
            (r"\.to_hdf\((.*?)\)", "pandas", "hdf5"),
            (r"\.to_json\((.*?)\)", "pandas", "json"),
            # NumPy
            (r"np\.save\((.*?),\s*(.*?)\)", "numpy", "npy"),
            (r"np\.savetxt\((.*?),\s*(.*?)\)", "numpy", "txt"),
            # PyTorch
            (r"torch\.save\((.*?),\s*(.*?)\)", "torch", "pth"),
            # Matplotlib
            (r"plt\.savefig\((.*?)\)", "matplotlib", "img"),
            (r"fig\.savefig\((.*?)\)", "matplotlib", "img"),
            # JSON
            (r"json\.dump\((.*?),\s*open\((.*?),\s*['\"]w['\"]\)\)", "json", "json"),
            # Pickle
            (r"pickle\.dump\((.*?),\s*open\((.*?),\s*['\"]wb['\"]\)\)", "pickle", "pkl"),
        ]
        
    def _register_module_tools(self):
        """Register IO-specific tools."""
        
        @self.app.tool()
        async def analyze_io_operations(code: str) -> Dict[str, Any]:
            """Analyze IO operations in the code."""
            loads = []
            saves = []
            
            # Analyze load operations
            for pattern, lib, fmt in self.load_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    loads.append({
                        "operation": match.group(0),
                        "library": lib,
                        "format": fmt,
                        "line": code[:match.start()].count('\n') + 1,
                    })
                    
            # Analyze save operations
            for pattern, lib, fmt in self.save_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    saves.append({
                        "operation": match.group(0),
                        "library": lib,
                        "format": fmt,
                        "line": code[:match.start()].count('\n') + 1,
                    })
                    
            return {
                "load_operations": loads,
                "save_operations": saves,
                "total_operations": len(loads) + len(saves),
                "libraries_used": list(set([op["library"] for op in loads + saves])),
            }
            
        @self.app.tool()
        async def suggest_path_improvements(code: str) -> List[Dict[str, str]]:
            """Suggest path handling improvements."""
            suggestions = []
            
            # Check for absolute paths
            abs_paths = re.findall(r"['\"]([/\\](?:home|Users|var|tmp|data)[/\\][^'\"]+)['\"]", code)
            for path in abs_paths:
                suggestions.append({
                    "issue": f"Absolute path: {path}",
                    "suggestion": f"Use relative path: './{os.path.basename(path)}'",
                    "severity": "high",
                })
                
            # Check for hardcoded paths without config
            hardcoded = re.findall(r"['\"]([./]+[^'\"]+\.[a-z]{2,4})['\"]", code)
            if len(hardcoded) > 3:
                suggestions.append({
                    "issue": f"Found {len(hardcoded)} hardcoded paths",
                    "suggestion": "Consider extracting paths to PATH.yaml config file",
                    "severity": "medium",
                })
                
            # Check for missing output directory creation
            if any(pattern in code for pattern in ["save", "write", "dump"]):
                if "makedirs" not in code and "mkdir" not in code:
                    suggestions.append({
                        "issue": "Saving files without directory creation",
                        "suggestion": "stx.io.save() automatically creates directories",
                        "severity": "info",
                    })
                    
            return suggestions
            
        @self.app.tool()
        async def convert_path_to_scitex(
            path: str,
            operation: str = "save"
        ) -> Dict[str, str]:
            """Convert a path to SciTeX convention."""
            # Remove absolute path components
            if path.startswith('/'):
                parts = path.split('/')
                # Keep only last 2-3 components
                path = './' + '/'.join(parts[-2:])
                
            # Ensure starts with ./
            if not path.startswith('./'):
                path = './' + path
                
            result = {
                "original": path,
                "scitex_path": path,
                "requires_symlink": operation == "save",
            }
            
            # For save operations, adjust path
            if operation == "save":
                result["note"] = "Use symlink_from_cwd=True for easy access"
                
            return result
            
    def get_module_description(self) -> str:
        """Get description of IO module functionality."""
        return (
            "SciTeX IO module provides unified file loading and saving with "
            "automatic format detection, path management, and directory creation. "
            "Supports 30+ file formats including CSV, JSON, NumPy, PyTorch, HDF5, etc."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "get_module_info",
            "validate_code",
            "translate_to_scitex",
            "translate_from_scitex",
            "suggest_improvements",
            "analyze_io_operations",
            "suggest_path_improvements",
            "convert_path_to_scitex",
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate IO module usage."""
        issues = []
        warnings = []
        
        # Check for direct file operations when stx.io is imported
        if "import scitex as stx" in code or "stx.io" in code:
            # Check for non-scitex IO operations
            for pattern, lib, _ in self.load_patterns + self.save_patterns:
                if re.search(pattern, code) and lib != "scitex":
                    issues.append(f"Using {lib} IO instead of stx.io")
                    
        # Check path conventions
        if "stx.io.save" in code:
            # Check for absolute paths
            abs_paths = re.findall(r"stx\.io\.save\([^,]+,\s*['\"]([/\\][^'\"]+)['\"]", code)
            for path in abs_paths:
                issues.append(f"Absolute path in stx.io.save: {path}")
                
            # Check for missing symlink parameter
            save_calls = re.findall(r"stx\.io\.save\([^)]+\)", code)
            for call in save_calls:
                if "symlink_from_cwd" not in call:
                    warnings.append("Missing symlink_from_cwd parameter in stx.io.save")
                    
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 20 - len(warnings) * 10),
        }
        
    async def module_to_scitex(
        self,
        code: str,
        preserve_comments: bool,
        add_config_support: bool
    ) -> Dict[str, Any]:
        """Translate IO operations to SciTeX."""
        translated = code
        conversions = []
        config_suggestions = {}
        
        # Add import if needed
        if any(re.search(p[0], code) for p in self.load_patterns + self.save_patterns):
            if "import scitex as stx" not in translated:
                # Add after imports
                lines = translated.split('\n')
                import_idx = -1
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import', 'from')):
                        import_idx = i
                if import_idx >= 0:
                    lines.insert(import_idx + 1, "import scitex as stx")
                    translated = '\n'.join(lines)
                    
        # Convert load operations
        for pattern, lib, fmt in self.load_patterns:
            matches = list(re.finditer(pattern, translated))
            for match in reversed(matches):  # Process in reverse to maintain positions
                # Extract path
                path_match = re.search(r"['\"]([^'\"]+)['\"]", match.group(1))
                if path_match:
                    path = path_match.group(1)
                    # Convert to relative path
                    if path.startswith('/'):
                        path = './' + path.split('/')[-1]
                    
                    replacement = f"stx.io.load('{path}')"
                    translated = translated[:match.start()] + replacement + translated[match.end():]
                    conversions.append(f"Converted {lib} load to stx.io.load")
                    
        # Convert save operations
        for pattern, lib, fmt in self.save_patterns:
            if lib == "pandas":
                # Handle DataFrame.to_* methods
                matches = list(re.finditer(pattern, translated))
                for match in reversed(matches):
                    # Find the dataframe variable
                    line_start = translated.rfind('\n', 0, match.start()) + 1
                    line = translated[line_start:match.start()]
                    df_match = re.search(r"(\w+)\.", line)
                    if df_match:
                        df_var = df_match.group(1)
                        path_match = re.search(r"['\"]([^'\"]+)['\"]", match.group(1))
                        if path_match:
                            path = path_match.group(1)
                            if path.startswith('/'):
                                path = './' + path.split('/')[-1]
                            
                            replacement = f"stx.io.save({df_var}, '{path}', symlink_from_cwd=True)"
                            full_match_start = line_start + df_match.start()
                            translated = translated[:full_match_start] + replacement + translated[match.end():]
                            conversions.append(f"Converted {lib} save to stx.io.save")
                            
            elif lib in ["numpy", "torch"]:
                # Handle np.save(path, data) style
                matches = list(re.finditer(pattern, translated))
                for match in reversed(matches):
                    parts = match.groups()
                    if len(parts) == 2:
                        path, data = parts
                        path = re.search(r"['\"]([^'\"]+)['\"]", path).group(1)
                        if path.startswith('/'):
                            path = './' + path.split('/')[-1]
                        
                        replacement = f"stx.io.save({data}, '{path}', symlink_from_cwd=True)"
                        translated = translated[:match.start()] + replacement + translated[match.end():]
                        conversions.append(f"Converted {lib} save to stx.io.save")
                        
            elif lib == "matplotlib":
                # Handle plt.savefig / fig.savefig
                matches = list(re.finditer(pattern, translated))
                for match in reversed(matches):
                    path_match = re.search(r"['\"]([^'\"]+)['\"]", match.group(1))
                    if path_match:
                        path = path_match.group(1)
                        if path.startswith('/'):
                            path = './' + path.split('/')[-1]
                        
                        # Determine figure variable
                        fig_var = "plt.gcf()" if "plt.savefig" in match.group(0) else "fig"
                        replacement = f"stx.io.save({fig_var}, '{path}', symlink_from_cwd=True)"
                        translated = translated[:match.start()] + replacement + translated[match.end():]
                        conversions.append(f"Converted {lib} save to stx.io.save")
                        
        # Extract configs if requested
        if add_config_support:
            paths = re.findall(r"['\"]([./][^'\"]+\.[a-z]{2,4})['\"]", translated)
            if len(paths) > 3:
                config_suggestions["PATH.yaml"] = {
                    f"PATH_{i}": path for i, path in enumerate(set(paths))
                }
                
        return {
            "translated_code": translated,
            "conversions": conversions,
            "config_suggestions": config_suggestions,
            "success": True,
        }
        
    async def module_from_scitex(
        self,
        code: str,
        target_style: str
    ) -> Dict[str, Any]:
        """Translate SciTeX IO operations back to standard Python."""
        translated = code
        dependencies = set()
        
        # Find all stx.io.load calls
        load_matches = list(re.finditer(r"stx\.io\.load\(['\"]([^'\"]+)['\"]\)", translated))
        for match in reversed(load_matches):
            path = match.group(1)
            ext = path.split('.')[-1].lower() if '.' in path else ''
            
            # Determine appropriate replacement
            if ext in ['csv', 'tsv']:
                replacement = f"pd.read_csv('{path}')"
                dependencies.add("pandas")
            elif ext in ['xlsx', 'xls']:
                replacement = f"pd.read_excel('{path}')"
                dependencies.add("pandas")
            elif ext in ['npy', 'npz']:
                replacement = f"np.load('{path}')"
                dependencies.add("numpy")
            elif ext == 'json':
                replacement = f"json.load(open('{path}'))"
                dependencies.add("json")
            elif ext in ['pkl', 'pickle']:
                replacement = f"pickle.load(open('{path}', 'rb'))"
                dependencies.add("pickle")
            elif ext in ['pth', 'pt']:
                replacement = f"torch.load('{path}')"
                dependencies.add("torch")
            elif ext in ['yaml', 'yml']:
                replacement = f"yaml.load(open('{path}'), Loader=yaml.SafeLoader)"
                dependencies.add("yaml")
            else:
                replacement = f"open('{path}').read()"
                
            translated = translated[:match.start()] + replacement + translated[match.end():]
            
        # Find all stx.io.save calls
        save_matches = list(re.finditer(
            r"stx\.io\.save\(([^,]+),\s*['\"]([^'\"]+)['\"](?:,\s*symlink_from_cwd=\w+)?\)",
            translated
        ))
        for match in reversed(save_matches):
            data_var = match.group(1).strip()
            path = match.group(2)
            ext = path.split('.')[-1].lower() if '.' in path else ''
            
            # Determine appropriate replacement
            if ext in ['csv', 'tsv']:
                replacement = f"{data_var}.to_csv('{path}')"
                dependencies.add("pandas")
            elif ext in ['xlsx', 'xls']:
                replacement = f"{data_var}.to_excel('{path}')"
                dependencies.add("pandas")
            elif ext in ['npy']:
                replacement = f"np.save('{path}', {data_var})"
                dependencies.add("numpy")
            elif ext == 'json':
                replacement = f"json.dump({data_var}, open('{path}', 'w'))"
                dependencies.add("json")
            elif ext in ['pkl', 'pickle']:
                replacement = f"pickle.dump({data_var}, open('{path}', 'wb'))"
                dependencies.add("pickle")
            elif ext in ['pth', 'pt']:
                replacement = f"torch.save({data_var}, '{path}')"
                dependencies.add("torch")
            elif ext in ['png', 'jpg', 'jpeg', 'pdf', 'svg']:
                replacement = f"{data_var}.savefig('{path}')"
                dependencies.add("matplotlib")
            else:
                replacement = f"open('{path}', 'w').write({data_var})"
                
            translated = translated[:match.start()] + replacement + translated[match.end():]
            
        # Remove scitex import if not needed
        if "stx." not in translated:
            translated = re.sub(r"import scitex as stx\n?", "", translated)
            
        # Add required imports
        import_lines = []
        if "pandas" in dependencies:
            import_lines.append("import pandas as pd")
        if "numpy" in dependencies:
            import_lines.append("import numpy as np")
        if "matplotlib" in dependencies:
            import_lines.append("import matplotlib.pyplot as plt")
        if "json" in dependencies:
            import_lines.append("import json")
        if "pickle" in dependencies:
            import_lines.append("import pickle")
        if "torch" in dependencies:
            import_lines.append("import torch")
        if "yaml" in dependencies:
            import_lines.append("import yaml")
            
        if import_lines:
            translated = '\n'.join(import_lines) + '\n\n' + translated
            
        return {
            "translated_code": translated,
            "dependencies": list(dependencies),
            "success": True,
        }
        
    async def analyze_improvement_opportunities(self, code: str) -> List[Dict[str, str]]:
        """Analyze code for IO improvement opportunities."""
        opportunities = []
        
        # Check for repeated file operations
        file_ops = re.findall(r"open\(['\"]([^'\"]+)['\"]", code)
        file_counts = {}
        for f in file_ops:
            file_counts[f] = file_counts.get(f, 0) + 1
        
        for f, count in file_counts.items():
            if count > 1:
                opportunities.append({
                    "pattern": f"Multiple operations on {f}",
                    "suggestion": f"Consider caching with stx.io.cache()",
                    "benefit": "Reduce file I/O overhead",
                })
                
        # Check for missing error handling
        if "open(" in code and "try:" not in code:
            opportunities.append({
                "pattern": "File operations without error handling",
                "suggestion": "stx.io handles errors gracefully with warnings",
                "benefit": "More robust file handling",
            })
            
        # Check for manual directory creation
        if "os.makedirs" in code or "Path.mkdir" in code:
            opportunities.append({
                "pattern": "Manual directory creation",
                "suggestion": "stx.io.save() creates directories automatically",
                "benefit": "Simpler code, less boilerplate",
            })
            
        return opportunities


# Main entry point
if __name__ == "__main__":
    server = ScitexIOMCPServer()
    asyncio.run(server.run())

# EOF