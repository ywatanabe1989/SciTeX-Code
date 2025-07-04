#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:07:00 (ywatanabe)"
# File: ./mcp_servers/scitex-plt/server.py
# ----------------------------------------

"""MCP server for SciTeX PLT module operations."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Tuple
from scitex_base.base_server import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexPltMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX PLT module translations and operations."""
    
    def __init__(self):
        super().__init__("plt", "0.1.0")
        self.create_translation_tools("stx.plt")
        
        # Plotting patterns
        self.plot_patterns = [
            # Subplot creation
            (r"plt\.subplots\((.*?)\)", "subplots"),
            (r"fig,\s*ax\s*=\s*plt\.subplots\((.*?)\)", "subplots_assign"),
            (r"fig,\s*axes\s*=\s*plt\.subplots\((.*?)\)", "subplots_multi"),
            # Axis labeling
            (r"ax\.set_xlabel\(['\"]([^'\"]+)['\"]\)", "xlabel"),
            (r"ax\.set_ylabel\(['\"]([^'\"]+)['\"]\)", "ylabel"),
            (r"ax\.set_title\(['\"]([^'\"]+)['\"]\)", "title"),
            # Figure saving (handled by io module)
            (r"plt\.savefig\(['\"]([^'\"]+)['\"]\)", "savefig"),
            (r"fig\.savefig\(['\"]([^'\"]+)['\"]\)", "savefig"),
            # Common plot types
            (r"ax\.plot\((.*?)\)", "plot"),
            (r"ax\.scatter\((.*?)\)", "scatter"),
            (r"ax\.bar\((.*?)\)", "bar"),
            (r"ax\.hist\((.*?)\)", "hist"),
            # Legend
            (r"ax\.legend\((.*?)\)", "legend"),
            (r"plt\.legend\((.*?)\)", "legend"),
        ]
        
    def _register_module_tools(self):
        """Register PLT-specific tools."""
        
        @self.app.tool()
        async def analyze_plotting_operations(code: str) -> Dict[str, Any]:
            """Analyze plotting operations in the code."""
            operations = []
            
            for pattern, op_type in self.plot_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    operations.append({
                        "operation": match.group(0),
                        "type": op_type,
                        "line": code[:match.start()].count('\n') + 1,
                    })
                    
            # Check for set_xlabel/ylabel/title sequences
            label_sequences = []
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if 'set_xlabel' in line and i + 2 < len(lines):
                    if 'set_ylabel' in lines[i + 1] and 'set_title' in lines[i + 2]:
                        label_sequences.append({
                            "start_line": i + 1,
                            "end_line": i + 3,
                            "can_use_set_xyt": True,
                        })
                        
            return {
                "plotting_operations": operations,
                "total_operations": len(operations),
                "label_sequences": label_sequences,
                "uses_matplotlib": bool(re.search(r"import matplotlib < /dev/null | from matplotlib", code)),
            }
            
        @self.app.tool()
        async def suggest_data_tracking(code: str) -> List[Dict[str, str]]:
            """Suggest data tracking improvements."""
            suggestions = []
            
            # Check if using matplotlib but not scitex
            if ("plt.subplots" in code or "pyplot.subplots" in code) and "stx.plt.subplots" not in code:
                suggestions.append({
                    "issue": "Using matplotlib subplots without data tracking",
                    "suggestion": "Use stx.plt.subplots() to automatically track plotted data",
                    "benefit": "Automatic CSV export of plotted data for reproducibility",
                })
                
            # Check for multiple set_label calls
            if all(pattern in code for pattern in ["set_xlabel", "set_ylabel", "set_title"]):
                suggestions.append({
                    "issue": "Using separate calls for xlabel, ylabel, and title",
                    "suggestion": "Use ax.set_xyt(xlabel, ylabel, title) for conciseness",
                    "benefit": "More concise and readable code",
                })
                
            # Check for savefig without data export
            if ("savefig" in code) and ("stx.io.save" not in code):
                suggestions.append({
                    "issue": "Saving figures without exporting plot data",
                    "suggestion": "Use stx.io.save(fig, path) to save both figure and data",
                    "benefit": "Automatic CSV export of plotted data alongside figure",
                })
                
            return suggestions
            
        @self.app.tool()
        async def convert_axis_labels_to_xyt(
            xlabel: str,
            ylabel: str, 
            title: str
        ) -> str:
            """Convert separate axis labels to set_xyt call."""
            return f"ax.set_xyt('{xlabel}', '{ylabel}', '{title}')"
            
    def get_module_description(self) -> str:
        """Get description of PLT module functionality."""
        return (
            "SciTeX PLT module enhances matplotlib with automatic data tracking, "
            "combined axis labeling (set_xyt), and automatic CSV export of plotted data. "
            "Supports all standard matplotlib plotting functions with added reproducibility features."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "get_module_info",
            "validate_code", 
            "translate_to_scitex",
            "translate_from_scitex",
            "suggest_improvements",
            "analyze_plotting_operations",
            "suggest_data_tracking",
            "convert_axis_labels_to_xyt",
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate PLT module usage."""
        issues = []
        warnings = []
        
        # Check for scitex plt usage
        if "import scitex as stx" in code or "stx.plt" in code:
            # Check for mixing matplotlib and scitex plotting
            if "plt.subplots" in code and "stx.plt.subplots" in code:
                warnings.append("Mixing matplotlib and scitex subplot creation")
                
            # Check for non-scitex axis methods
            if "stx.plt.subplots" in code:
                if re.search(r"ax\.set_xlabel\(|ax\.set_ylabel\(|ax\.set_title\(", code):
                    warnings.append("Consider using ax.set_xyt() instead of separate label methods")
                    
        # Check for proper data export
        if "stx.plt.subplots" in code:
            if "savefig" in code and "stx.io.save" not in code:
                issues.append("Using savefig instead of stx.io.save - plot data won't be exported")
                
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
        """Translate plotting operations to SciTeX."""
        translated = code
        conversions = []
        
        # Add import if needed
        if any(pattern in code for pattern, _ in self.plot_patterns):
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
                    
        # Convert plt.subplots to stx.plt.subplots
        subplot_patterns = [
            (r"plt\.subplots\(", "stx.plt.subplots("),
            (r"pyplot\.subplots\(", "stx.plt.subplots("),
        ]
        
        for old_pattern, new_pattern in subplot_patterns:
            if re.search(old_pattern, translated):
                translated = re.sub(old_pattern, new_pattern, translated)
                conversions.append("Converted matplotlib subplots to stx.plt.subplots for data tracking")
                
        # Convert set_xlabel/ylabel/title sequences to set_xyt
        lines = translated.split('\n')
        i = 0
        while i < len(lines) - 2:
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip() if i + 1 < len(lines) else ""
            line3 = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            # Check for xlabel/ylabel/title sequence
            xlabel_match = re.search(r"(\w+)\.set_xlabel\(['\"]([^'\"]+)['\"]\)", line1)
            ylabel_match = re.search(r"(\w+)\.set_ylabel\(['\"]([^'\"]+)['\"]\)", line2)
            title_match = re.search(r"(\w+)\.set_title\(['\"]([^'\"]+)['\"]\)", line3)
            
            if xlabel_match and ylabel_match and title_match:
                ax_var = xlabel_match.group(1)
                if ax_var == ylabel_match.group(1) == title_match.group(1):
                    xlabel = xlabel_match.group(2)
                    ylabel = ylabel_match.group(2)
                    title = title_match.group(2)
                    
                    # Replace with set_xyt
                    indent = len(line1) - len(line1.lstrip())
                    replacement = " " * indent + f"{ax_var}.set_xyt('{xlabel}', '{ylabel}', '{title}')"
                    
                    lines[i] = replacement
                    lines.pop(i + 1)  # Remove ylabel line
                    lines.pop(i + 1)  # Remove title line
                    
                    conversions.append("Converted set_xlabel/ylabel/title to set_xyt")
                    continue
                    
            i += 1
            
        translated = '\n'.join(lines)
        
        # Note about savefig conversion - this is handled by IO module
        if "savefig" in translated and "stx.io.save" not in translated:
            # Add a comment about using stx.io.save
            savefig_matches = re.finditer(r"(.*\.savefig\(.*?\))", translated)
            for match in savefig_matches:
                line = match.group(0)
                if "# Use stx.io.save" not in line:
                    replacement = line + "  # Consider using stx.io.save() for data export"
                    translated = translated.replace(line, replacement)
                    
        return {
            "translated_code": translated,
            "conversions": conversions,
            "config_suggestions": {},
            "success": True,
        }
        
    async def module_from_scitex(
        self,
        code: str,
        target_style: str
    ) -> Dict[str, Any]:
        """Translate SciTeX plotting operations back to standard Python."""
        translated = code
        dependencies = set()
        
        # Convert stx.plt.subplots back to plt.subplots
        if "stx.plt.subplots" in translated:
            translated = re.sub(r"stx\.plt\.subplots\(", "plt.subplots(", translated)
            dependencies.add("matplotlib")
            
        # Convert set_xyt back to individual calls
        xyt_matches = list(re.finditer(
            r"(\w+)\.set_xyt\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\)",
            translated
        ))
        
        for match in reversed(xyt_matches):
            ax_var = match.group(1)
            xlabel = match.group(2)
            ylabel = match.group(3)
            title = match.group(4)
            
            # Get indentation
            line_start = translated.rfind('\n', 0, match.start()) + 1
            indent = match.start() - line_start
            indent_str = " " * indent
            
            replacement = (
                f"{indent_str}{ax_var}.set_xlabel('{xlabel}')\n"
                f"{indent_str}{ax_var}.set_ylabel('{ylabel}')\n"
                f"{indent_str}{ax_var}.set_title('{title}')"
            )
            
            translated = translated[:match.start()] + replacement + translated[match.end():]
            
        # Remove scitex import if not needed elsewhere
        if "stx." not in translated:
            translated = re.sub(r"import scitex as stx\n?", "", translated)
            
        # Add matplotlib import if needed
        if any(pattern in translated for pattern in ["plt.subplots", "plt.legend", "plt.savefig"]):
            if "import matplotlib.pyplot as plt" not in translated:
                # Add at the beginning with other imports
                import_lines = []
                other_lines = []
                for line in translated.split('\n'):
                    if line.strip().startswith(('import', 'from')):
                        import_lines.append(line)
                    else:
                        other_lines.append(line)
                        
                import_lines.append("import matplotlib.pyplot as plt")
                translated = '\n'.join(import_lines) + '\n' + '\n'.join(other_lines)
                
        return {
            "translated_code": translated,
            "dependencies": list(dependencies),
            "success": True,
        }
        
    async def analyze_improvement_opportunities(self, code: str) -> List[Dict[str, str]]:
        """Analyze code for PLT improvement opportunities."""
        opportunities = []
        
        # Check for missing data export
        if "plt.subplots" in code and "plt.savefig" in code:
            if "stx.plt.subplots" not in code:
                opportunities.append({
                    "pattern": "Matplotlib plotting without data tracking",
                    "suggestion": "Use stx.plt.subplots() and stx.io.save()",
                    "benefit": "Automatic CSV export of all plotted data",
                })
                
        # Check for verbose labeling
        label_count = code.count("set_xlabel") + code.count("set_ylabel") + code.count("set_title")
        if label_count >= 6:  # Multiple axes being labeled
            opportunities.append({
                "pattern": f"Found {label_count} separate label calls",
                "suggestion": "Use ax.set_xyt() for concise labeling",
                "benefit": "Reduce code by ~66% for axis labeling",
            })
            
        # Check for legend without data structure
        if "ax.legend()" in code:
            if "label=" not in code:
                opportunities.append({
                    "pattern": "Legend without labeled data",
                    "suggestion": "Add label= parameter to plot calls",
                    "benefit": "Clearer legends and better data tracking",
                })
                
        # Check for multiple similar plots
        plot_calls = code.count(".plot(") + code.count(".scatter(")
        if plot_calls > 5:
            opportunities.append({
                "pattern": f"Many plot calls ({plot_calls})",
                "suggestion": "Consider using data tracking for complex visualizations",
                "benefit": "Easier debugging and reproducibility with CSV export",
            })
            
        return opportunities


# Main entry point
if __name__ == "__main__":
    server = ScitexPltMCPServer()
    asyncio.run(server.run())

# EOF
