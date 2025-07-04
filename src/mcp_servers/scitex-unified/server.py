#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 10:50:00 (ywatanabe)"
# File: ./mcp_servers/scitex-unified/server.py
# ----------------------------------------

"""Unified MCP server with simple entry points for SciTeX translation guidance."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Optional


class ScitexUnifiedMCPServer:
    """Simple unified MCP server with just two main tools."""
    
    def __init__(self):
        self.name = "scitex-unified"
        self.version = "1.0.0"
        
    async def translate_to_scitex(self, code: str, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point: Explain how to convert Python code to SciTeX format.
        
        Args:
            code: Python code to convert
            focus_area: Optional focus ("io", "plotting", "stats", "all")
        """
        
        # Analyze the code to understand what it does
        analysis = self._analyze_code_patterns(code)
        
        # Generate focused guidance based on detected patterns
        guidance = self._generate_conversion_guidance(analysis, focus_area)
        
        # Create a complete example if possible
        example = self._create_example_conversion(code, analysis)
        
        return {
            "original_code": code,
            "analysis": analysis,
            "conversion_guidance": guidance,
            "example_conversion": example,
            "next_steps": self._suggest_next_steps(analysis),
            "resources": [
                "📚 SciTeX I/O Tutorial: examples/scitex_io_tutorial.ipynb",
                "📊 SciTeX Plotting Guide: examples/scitex_plt_tutorial.ipynb", 
                "📈 SciTeX Stats Tutorial: examples/scitex_stats_tutorial.ipynb",
                "🤖 SciTeX AI Guide: examples/scitex_ai_tutorial.ipynb"
            ]
        }
        
    async def translate_from_scitex(self, code: str, target_style: str = "standard") -> Dict[str, Any]:
        """
        Main entry point: Explain how to convert SciTeX code to standard Python.
        
        Args:
            code: SciTeX code to convert
            target_style: "standard", "minimal", "numpy", "pandas"
        """
        
        # Analyze SciTeX usage
        scitex_analysis = self._analyze_scitex_usage(code)
        
        # Generate reverse conversion guidance
        guidance = self._generate_reverse_guidance(scitex_analysis, target_style)
        
        # Create standard Python example
        example = self._create_standard_example(code, scitex_analysis, target_style)
        
        return {
            "original_scitex_code": code,
            "scitex_analysis": scitex_analysis,
            "conversion_guidance": guidance,
            "standard_python_example": example,
            "target_style": target_style,
            "dependencies_needed": self._list_dependencies(scitex_analysis, target_style)
        }
        
    def _analyze_code_patterns(self, code: str) -> Dict[str, Any]:
        """Analyze code to understand what it does."""
        
        patterns = {
            "io_operations": [],
            "plotting_operations": [],
            "stats_operations": [],
            "data_operations": [],
            "file_paths": [],
            "libraries_used": set()
        }
        
        # I/O patterns
        io_patterns = [
            (r"pd\.read_csv", "pandas CSV reading", "pandas"),
            (r"pd\.read_excel", "pandas Excel reading", "pandas"),
            (r"\.to_csv", "pandas CSV writing", "pandas"),
            (r"np\.load", "numpy loading", "numpy"),
            (r"np\.save", "numpy saving", "numpy"),
            (r"json\.load", "JSON loading", "json"),
            (r"pickle\.load", "pickle loading", "pickle"),
            (r"plt\.savefig", "matplotlib save", "matplotlib"),
        ]
        
        for pattern, description, library in io_patterns:
            if re.search(pattern, code):
                patterns["io_operations"].append(description)
                patterns["libraries_used"].add(library)
                
        # Plotting patterns
        plot_patterns = [
            (r"plt\.plot", "line plotting"),
            (r"plt\.scatter", "scatter plotting"),
            (r"plt\.bar", "bar plotting"),
            (r"plt\.hist", "histogram"),
            (r"sns\.", "seaborn plotting"),
            (r"plt\.xlabel|plt\.ylabel|plt\.title", "axis labeling"),
        ]
        
        for pattern, description in plot_patterns:
            if re.search(pattern, code):
                patterns["plotting_operations"].append(description)
                patterns["libraries_used"].add("matplotlib")
                
        # Stats patterns
        stats_patterns = [
            (r"stats\.ttest", "t-test"),
            (r"\.corr\(\)", "correlation"),
            (r"\.describe\(\)", "descriptive statistics"),
            (r"stats\.mannwhitneyu", "Mann-Whitney test"),
        ]
        
        for pattern, description in stats_patterns:
            if re.search(pattern, code):
                patterns["stats_operations"].append(description)
                patterns["libraries_used"].add("scipy")
                
        # Extract file paths
        paths = re.findall(r"['\"]([^'\"]*\.[a-z]+)['\"]", code)
        patterns["file_paths"] = list(set(paths))
        
        return {
            "patterns": patterns,
            "complexity": self._assess_complexity(patterns),
            "main_focus": self._determine_main_focus(patterns)
        }
        
    def _generate_conversion_guidance(self, analysis: Dict[str, Any], focus_area: Optional[str]) -> List[Dict[str, Any]]:
        """Generate step-by-step guidance for converting to SciTeX."""
        
        guidance = []
        patterns = analysis["patterns"]
        
        # I/O conversion guidance
        if patterns["io_operations"] or focus_area in ["io", "all"]:
            guidance.append({
                "category": "📁 File I/O Operations",
                "priority": "high",
                "steps": [
                    {
                        "step": "Replace specific file operations with universal stx.io.load/save",
                        "examples": {
                            "pandas": "pd.read_csv('file.csv') → stx.io.load('./file.csv')",
                            "numpy": "np.load('data.npy') → stx.io.load('./data.npy')", 
                            "json": "json.load(open('file.json')) → stx.io.load('./file.json')"
                        }
                    },
                    {
                        "step": "Add symlinks for all save operations",
                        "examples": {
                            "dataframe": "stx.io.save(df, './output.csv', symlink_from_cwd=True)",
                            "figure": "stx.io.save(fig, './plot.png', symlink_from_cwd=True)",
                            "array": "stx.io.save(array, './data.npy', symlink_from_cwd=True)"
                        }
                    },
                    {
                        "step": "Convert to relative paths",
                        "examples": {
                            "before": "/absolute/path/file.csv",
                            "after": "./data/file.csv"
                        }
                    }
                ],
                "benefits": ["Unified interface", "Auto format detection", "Directory creation", "Easy file access"]
            })
            
        # Plotting guidance
        if patterns["plotting_operations"] or focus_area in ["plotting", "all"]:
            guidance.append({
                "category": "📊 Plotting Operations", 
                "priority": "medium",
                "steps": [
                    {
                        "step": "Use stx.plt.subplots() for enhanced plotting",
                        "examples": {
                            "basic": "fig, ax = stx.plt.subplots()",
                            "multiple": "fig, axes = stx.plt.subplots(2, 2)"
                        }
                    },
                    {
                        "step": "Replace xlabel/ylabel/title with ax.set_xyt()",
                        "examples": {
                            "before": "ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_title('Title')",
                            "after": "ax.set_xyt('X', 'Y', 'Title')"
                        }
                    },
                    {
                        "step": "Save plots with stx.io.save for automatic CSV export",
                        "examples": {
                            "enhanced": "stx.io.save(fig, './plot.png', symlink_from_cwd=True)"
                        }
                    }
                ],
                "benefits": ["Auto CSV export", "Enhanced features", "Consistent styling", "Data tracking"]
            })
            
        # Stats guidance  
        if patterns["stats_operations"] or focus_area in ["stats", "all"]:
            guidance.append({
                "category": "📈 Statistical Operations",
                "priority": "medium", 
                "steps": [
                    {
                        "step": "Use enhanced SciTeX statistical functions",
                        "examples": {
                            "descriptive": "stx.stats.describe(data)",
                            "correlation": "stx.stats.corr_test(x, y)",
                            "comparison": "stx.stats.brunner_munzel_test(group1, group2)"
                        }
                    },
                    {
                        "step": "Add significance formatting",
                        "examples": {
                            "p_values": "f'p = {p:.3f} {stx.stats.p2stars(p)}'"
                        }
                    }
                ],
                "benefits": ["Robust tests", "Effect sizes", "Multiple corrections", "Publication formatting"]
            })
            
        # General structure guidance
        guidance.append({
            "category": "🏗️ Code Structure",
            "priority": "low",
            "steps": [
                {
                    "step": "Wrap in main() function",
                    "examples": {
                        "structure": """
def main(args):
    # Your code here
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
"""
                    }
                },
                {
                    "step": "Add configuration file if many parameters",
                    "examples": {
                        "config": "config = stx.io.load('./CONFIG.yaml')"
                    }
                }
            ],
            "benefits": ["Better organization", "Testability", "Argument handling", "Configurability"]
        })
        
        return guidance
        
    def _create_example_conversion(self, code: str, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Create a concrete example of the conversion."""
        
        # Simple pattern-based conversion for demonstration
        converted = code
        
        # Basic I/O conversions
        converted = re.sub(r"pd\.read_csv\(['\"]([^'\"]+)['\"]\)", r"stx.io.load('./\1')", converted)
        converted = re.sub(r"\.to_csv\(['\"]([^'\"]+)['\"]\)", r".to_csv('\1')\n# Better: stx.io.save(df, './\1', symlink_from_cwd=True)", converted)
        converted = re.sub(r"plt\.savefig\(['\"]([^'\"]+)['\"]\)", r"stx.io.save(plt.gcf(), './\1', symlink_from_cwd=True)", converted)
        
        # Add import if conversions were made
        if "stx.io" in converted and "import scitex as stx" not in converted:
            converted = "import scitex as stx\n\n" + converted
            
        return {
            "original": code,
            "converted_example": converted,
            "note": "This is a simplified example. Review the guidance above for complete conversion."
        }
        
    def _generate_reverse_guidance(self, analysis: Dict[str, Any], target_style: str) -> List[Dict[str, Any]]:
        """Generate guidance for converting SciTeX back to standard Python."""
        
        guidance = []
        
        if analysis["uses_stx_io"]:
            guidance.append({
                "category": "📁 I/O Operations",
                "steps": [
                    {
                        "step": f"Replace stx.io.load with {target_style}-specific functions",
                        "examples": {
                            "csv": "stx.io.load('./file.csv') → pd.read_csv('file.csv')",
                            "numpy": "stx.io.load('./data.npy') → np.load('data.npy')",
                            "json": "stx.io.load('./data.json') → json.load(open('data.json'))"
                        }
                    },
                    {
                        "step": "Replace stx.io.save with standard save methods",
                        "examples": {
                            "dataframe": "stx.io.save(df, './file.csv') → df.to_csv('file.csv')",
                            "figure": "stx.io.save(fig, './plot.png') → fig.savefig('plot.png')",
                            "numpy": "stx.io.save(arr, './data.npy') → np.save('data.npy', arr)"
                        }
                    }
                ]
            })
            
        return guidance
        
    def _analyze_scitex_usage(self, code: str) -> Dict[str, Any]:
        """Analyze SciTeX usage in code."""
        
        return {
            "uses_stx_io": "stx.io" in code,
            "uses_stx_plt": "stx.plt" in code,
            "uses_stx_stats": "stx.stats" in code,
            "io_calls": len(re.findall(r"stx\.io\.\w+", code)),
            "plotting_calls": len(re.findall(r"stx\.plt\.\w+", code)),
            "stats_calls": len(re.findall(r"stx\.stats\.\w+", code))
        }
        
    def _list_dependencies(self, analysis: Dict[str, Any], target_style: str) -> List[str]:
        """List dependencies needed for standard Python version."""
        
        deps = []
        if analysis["uses_stx_io"]:
            deps.extend(["pandas", "numpy"])
        if analysis["uses_stx_plt"]:
            deps.append("matplotlib")
        if analysis["uses_stx_stats"]:
            deps.append("scipy")
            
        return list(set(deps))
        
    def _assess_complexity(self, patterns: Dict[str, Any]) -> str:
        """Assess code complexity for conversion."""
        total_ops = len(patterns["io_operations"]) + len(patterns["plotting_operations"]) + len(patterns["stats_operations"])
        
        if total_ops >= 10:
            return "high"
        elif total_ops >= 5:
            return "medium"
        else:
            return "low"
            
    def _determine_main_focus(self, patterns: Dict[str, Any]) -> str:
        """Determine main focus of the code."""
        io_count = len(patterns["io_operations"])
        plot_count = len(patterns["plotting_operations"])
        stats_count = len(patterns["stats_operations"])
        
        if io_count >= plot_count and io_count >= stats_count:
            return "io"
        elif plot_count >= stats_count:
            return "plotting"
        else:
            return "stats"
            
    def _suggest_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on analysis."""
        
        steps = []
        complexity = analysis["complexity"]
        focus = analysis["main_focus"]
        
        if complexity == "low":
            steps.append("🚀 Start with I/O conversions - they're the most impactful")
            steps.append("📚 Review the comprehensive tutorial for your main focus area")
        elif complexity == "medium":
            steps.append("📋 Convert incrementally, one module at a time")
            steps.append("🧪 Test each conversion to ensure functionality")
        else:
            steps.append("📝 Consider breaking down into smaller scripts first")
            steps.append("⚙️ Extract configurations to YAML files")
            steps.append("🔧 Use the educational MCP server for detailed guidance")
            
        steps.append(f"🎯 Focus tutorial: examples/scitex_{focus}_tutorial.ipynb")
        
        return steps
        
    def _create_standard_example(self, code: str, analysis: Dict[str, Any], target_style: str) -> Dict[str, str]:
        """Create standard Python example from SciTeX code."""
        
        converted = code
        
        # Remove scitex import
        converted = re.sub(r"import scitex as stx\n?", "", converted)
        
        # Convert I/O operations
        converted = re.sub(r"stx\.io\.load\(['\"]([^'\"]+)['\"]\)", self._convert_load_to_standard, converted)
        converted = re.sub(r"stx\.io\.save\(([^,]+),\s*['\"]([^'\"]+)['\"].*?\)", self._convert_save_to_standard, converted)
        
        # Add necessary imports
        imports = []
        if analysis["uses_stx_io"]:
            imports.extend(["import pandas as pd", "import numpy as np"])
        if analysis["uses_stx_plt"]:
            imports.append("import matplotlib.pyplot as plt")
        if analysis["uses_stx_stats"]:
            imports.append("from scipy import stats")
            
        if imports:
            converted = "\n".join(imports) + "\n\n" + converted
            
        return {
            "converted": converted,
            "note": "Standard Python equivalent - may need manual adjustment for complex cases"
        }
        
    def _convert_load_to_standard(self, match) -> str:
        """Convert stx.io.load to appropriate standard function."""
        path = match.group(1)
        ext = path.split('.')[-1].lower()
        
        if ext == 'csv':
            return f"pd.read_csv('{path}')"
        elif ext in ['npy', 'npz']:
            return f"np.load('{path}')"
        elif ext == 'json':
            return f"json.load(open('{path}'))"
        else:
            return f"# Load {path} with appropriate function"
            
    def _convert_save_to_standard(self, match) -> str:
        """Convert stx.io.save to appropriate standard function."""
        var = match.group(1)
        path = match.group(2)
        ext = path.split('.')[-1].lower()
        
        if ext == 'csv':
            return f"{var}.to_csv('{path}')"
        elif ext in ['png', 'jpg', 'pdf']:
            return f"{var}.savefig('{path}')"
        elif ext == 'npy':
            return f"np.save('{path}', {var})"
        else:
            return f"# Save {var} to {path} with appropriate function"


async def main():
    """Simple CLI interface for testing."""
    if len(sys.argv) < 3:
        print("Usage: python server.py <to-scitex|from-scitex> <code>")
        return
        
    server = ScitexUnifiedMCPServer()
    command = sys.argv[1]
    code = sys.argv[2]
    
    if command == "to-scitex":
        result = await server.translate_to_scitex(code)
        print("🎯 SciTeX Conversion Guidance:")
        for guidance in result["conversion_guidance"]:
            print(f"\n{guidance['category']}:")
            for step in guidance["steps"]:
                print(f"  • {step['step']}")
    elif command == "from-scitex":
        result = await server.translate_from_scitex(code)
        print("🔄 Standard Python Conversion:")
        print(result["standard_python_example"]["converted"])
    else:
        print("Unknown command. Use 'to-scitex' or 'from-scitex'")


if __name__ == "__main__":
    asyncio.run(main())

# EOF