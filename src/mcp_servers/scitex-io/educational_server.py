#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 10:45:00 (ywatanabe)"
# File: ./mcp_servers/scitex-io/educational_server.py
# ----------------------------------------

"""Educational MCP server for SciTeX IO - provides guidance instead of translation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Tuple
from scitex_base.base_server import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexIOEducationalServer(ScitexBaseMCPServer):
    """Educational MCP server for SciTeX IO - focuses on teaching rather than translation."""
    
    def __init__(self):
        super().__init__("io-education", "0.2.0")
        
    def _register_module_tools(self):
        """Register educational tools for IO operations."""
        
        @self.app.tool()
        async def explain_io_conversion(code: str) -> Dict[str, Any]:
            """Explain how to convert I/O operations to SciTeX with examples."""
            
            explanations = []
            detected_patterns = []
            
            # Detect and explain pandas operations
            if re.search(r"pd\.read_csv", code):
                detected_patterns.append("pandas CSV reading")
                explanations.append({
                    "pattern": "pd.read_csv()",
                    "explanation": "Convert pandas CSV reading to SciTeX universal I/O",
                    "before": "data = pd.read_csv('input.csv')",
                    "after": "data = stx.io.load('./input.csv')",
                    "benefits": [
                        "Automatic format detection",
                        "Consistent error handling", 
                        "Built-in caching support",
                        "Works with 30+ file formats"
                    ],
                    "notes": [
                        "Use relative paths starting with './'",
                        "SciTeX automatically detects CSV format",
                        "No need to specify pandas parameters - stx.io.load handles intelligently"
                    ]
                })
                
            if re.search(r"\.to_csv\(", code):
                detected_patterns.append("pandas CSV saving")
                explanations.append({
                    "pattern": "DataFrame.to_csv()",
                    "explanation": "Convert pandas CSV saving to SciTeX universal save",
                    "before": "df.to_csv('output.csv', index=False)",
                    "after": "stx.io.save(df, './output.csv', symlink_from_cwd=True)",
                    "benefits": [
                        "Automatic directory creation",
                        "Creates symlinks for easy access",
                        "Consistent across all data types",
                        "Built-in backup and versioning"
                    ],
                    "notes": [
                        "symlink_from_cwd=True creates easy access link in current directory",
                        "SciTeX handles index=False automatically for DataFrames",
                        "Output directory is created automatically if it doesn't exist"
                    ]
                })
                
            # Detect matplotlib operations
            if re.search(r"plt\.savefig|fig\.savefig", code):
                detected_patterns.append("matplotlib figure saving")
                explanations.append({
                    "pattern": "plt.savefig() / fig.savefig()",
                    "explanation": "Convert matplotlib saving to SciTeX enhanced save",
                    "before": "plt.savefig('plot.png', dpi=300, bbox_inches='tight')",
                    "after": "stx.io.save(fig, './plot.png', symlink_from_cwd=True)",
                    "benefits": [
                        "Automatic CSV export of plot data",
                        "Consistent file organization",
                        "Built-in metadata tracking",
                        "Automatic DPI and format optimization"
                    ],
                    "notes": [
                        "Plot data is automatically exported as CSV for reuse",
                        "Figure metadata is tracked for reproducibility",
                        "Use 'fig' variable or plt.gcf() to get current figure"
                    ]
                })
                
            # Detect numpy operations
            if re.search(r"np\.save|np\.load", code):
                detected_patterns.append("numpy array operations")
                explanations.append({
                    "pattern": "np.save() / np.load()",
                    "explanation": "Convert numpy operations to SciTeX universal I/O",
                    "before": "np.save('data.npy', array); array = np.load('data.npy')",
                    "after": "stx.io.save(array, './data.npy', symlink_from_cwd=True); array = stx.io.load('./data.npy')",
                    "benefits": [
                        "Unified interface across all formats",
                        "Better error messages and debugging",
                        "Automatic compression for large arrays",
                        "Integration with SciTeX workflow"
                    ],
                    "notes": [
                        "SciTeX automatically chooses optimal numpy format",
                        "Large arrays are compressed automatically",
                        "Compatible with existing .npy files"
                    ]
                })
                
            # General guidance if no specific patterns found
            if not detected_patterns:
                explanations.append({
                    "pattern": "General I/O operations",
                    "explanation": "General guidance for converting to SciTeX I/O",
                    "principles": [
                        "Replace library-specific load/save with stx.io.load/save",
                        "Use relative paths starting with './'",
                        "Add symlink_from_cwd=True for save operations",
                        "Let SciTeX auto-detect formats instead of specifying"
                    ],
                    "examples": {
                        "JSON": {
                            "before": "with open('data.json') as f: data = json.load(f)",
                            "after": "data = stx.io.load('./data.json')"
                        },
                        "Pickle": {
                            "before": "with open('data.pkl', 'rb') as f: data = pickle.load(f)",
                            "after": "data = stx.io.load('./data.pkl')"
                        },
                        "Excel": {
                            "before": "data = pd.read_excel('data.xlsx', sheet_name='Sheet1')",
                            "after": "data = stx.io.load('./data.xlsx')  # Auto-detects main sheet"
                        }
                    }
                })
                
            return {
                "detected_patterns": detected_patterns,
                "explanations": explanations,
                "total_suggestions": len(explanations),
                "recommendation": "Apply changes incrementally and test each conversion"
            }
            
        @self.app.tool()
        async def suggest_scitex_workflow(code: str) -> Dict[str, Any]:
            """Suggest overall workflow improvements for SciTeX adoption."""
            
            suggestions = []
            
            # Analyze overall structure
            has_main_function = "def main(" in code
            has_config_loading = "config" in code.lower() or "yaml" in code.lower()
            has_error_handling = "try:" in code or "except:" in code
            
            if not has_main_function:
                suggestions.append({
                    "aspect": "Code Structure",
                    "issue": "Missing main() function",
                    "suggestion": "Wrap your script in a main() function for better organization",
                    "example": '''
def main(args):
    """Main analysis function."""
    # Your code here
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
''',
                    "benefits": ["Better testability", "Cleaner imports", "Argument handling", "Exit code management"]
                })
                
            if not has_config_loading:
                # Check for hardcoded values
                numbers = re.findall(r'\b\d+\.?\d*\b', code)
                strings = re.findall(r"['\"]([^'\"]+\.[a-z]+)['\"]", code)
                
                if len(numbers) > 5 or len(strings) > 3:
                    suggestions.append({
                        "aspect": "Configuration Management",
                        "issue": "Hardcoded values detected",
                        "suggestion": "Extract parameters to a YAML config file",
                        "example": '''
# CONFIG.yaml
parameters:
  threshold: 0.05
  iterations: 1000
  output_format: "png"
  
paths:
  input_data: "./data/experiment.csv"
  output_dir: "./results/"

# In your script:
config = stx.io.load('./CONFIG.yaml')
threshold = config['parameters']['threshold']
''',
                        "benefits": ["Easy parameter tuning", "Better reproducibility", "Simplified collaboration"]
                    })
                    
            if not has_error_handling:
                suggestions.append({
                    "aspect": "Error Handling",
                    "issue": "Limited error handling detected",
                    "suggestion": "SciTeX provides graceful error handling, but you can add custom handling",
                    "example": '''
try:
    data = stx.io.load('./data.csv')
    results = analyze_data(data)
    stx.io.save(results, './results.json', symlink_from_cwd=True)
except FileNotFoundError as e:
    print(f"❌ Data file not found: {e}")
    return 1
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    return 1
''',
                    "benefits": ["Graceful failure", "Better debugging", "User-friendly messages"]
                })
                
            # Check for path handling
            absolute_paths = re.findall(r"['\"]([/\\][^'\"]+)['\"]", code)
            if absolute_paths:
                suggestions.append({
                    "aspect": "Path Management",
                    "issue": f"Found {len(absolute_paths)} absolute paths",
                    "suggestion": "Convert to relative paths for better portability",
                    "example": '''
# Instead of:
data = stx.io.load('/home/user/data/experiment.csv')

# Use:
data = stx.io.load('./data/experiment.csv')

# Or even better, use config:
config = stx.io.load('./CONFIG.yaml')
data = stx.io.load(config['paths']['input_data'])
''',
                    "benefits": ["Portable across systems", "Better collaboration", "Cleaner organization"]
                })
                
            return {
                "workflow_suggestions": suggestions,
                "structure_score": len([s for s in [has_main_function, has_config_loading, has_error_handling] if s]),
                "improvement_potential": "high" if len(suggestions) > 2 else "medium" if suggestions else "low"
            }
            
        @self.app.tool()
        async def create_learning_plan(experience_level: str = "beginner") -> Dict[str, Any]:
            """Create a personalized learning plan for SciTeX I/O adoption."""
            
            plans = {
                "beginner": {
                    "description": "New to SciTeX - start with basics",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Replace basic file operations",
                            "focus": "Convert simple pd.read_csv() and df.to_csv() calls",
                            "example": "data = stx.io.load('./data.csv') instead of pd.read_csv('data.csv')",
                            "practice": "Convert 2-3 simple data loading scripts"
                        },
                        {
                            "step": 2,
                            "title": "Add symlinks for outputs",
                            "focus": "Use symlink_from_cwd=True for all save operations",
                            "example": "stx.io.save(results, './output.json', symlink_from_cwd=True)",
                            "practice": "Apply to all your save operations"
                        },
                        {
                            "step": 3,
                            "title": "Organize with relative paths",
                            "focus": "Convert absolute paths to relative paths",
                            "example": "./data/file.csv instead of /full/path/to/file.csv",
                            "practice": "Reorganize one project's file structure"
                        }
                    ]
                },
                "intermediate": {
                    "description": "Some Python experience - focus on integration",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Unified I/O across formats",
                            "focus": "Replace all format-specific loads with stx.io.load",
                            "example": "Works for CSV, JSON, NumPy, Pickle, Excel automatically",
                            "practice": "Convert a multi-format project"
                        },
                        {
                            "step": 2,
                            "title": "Configuration extraction",
                            "focus": "Move hardcoded values to YAML configs",
                            "example": "Extract thresholds, paths, parameters to CONFIG.yaml",
                            "practice": "Refactor one analysis script with configs"
                        },
                        {
                            "step": 3,
                            "title": "Enhanced plotting workflow",
                            "focus": "Use stx.io.save for plots to get automatic CSV export",
                            "example": "stx.io.save(fig, './plot.png') exports plot data as CSV too",
                            "practice": "Convert plotting scripts to get data export"
                        }
                    ]
                },
                "advanced": {
                    "description": "Experienced user - optimize workflows",
                    "steps": [
                        {
                            "step": 1,
                            "title": "Complete project conversion",
                            "focus": "Convert entire projects to SciTeX patterns",
                            "example": "Main function, config files, unified I/O, proper structure",
                            "practice": "Migrate one complete research project"
                        },
                        {
                            "step": 2,
                            "title": "Advanced I/O features",
                            "focus": "Use caching, compression, metadata tracking",
                            "example": "stx.io.cache for repeated loads, automatic compression",
                            "practice": "Optimize performance-critical workflows"
                        },
                        {
                            "step": 3,
                            "title": "Integration with other modules",
                            "focus": "Combine I/O with stx.plt, stx.stats for complete workflows",
                            "example": "End-to-end pipeline from data to publication-ready outputs",
                            "practice": "Create template workflow for your domain"
                        }
                    ]
                }
            }
            
            plan = plans.get(experience_level, plans["beginner"])
            
            return {
                "learning_plan": plan,
                "estimated_time": f"{len(plan['steps'])} weeks (1 step per week)",
                "next_action": plan["steps"][0]["title"],
                "resources": [
                    "SciTeX I/O Tutorial Notebook",
                    "SciTeX Documentation",
                    "Example scripts in /examples/io/"
                ]
            }
            
    def get_module_description(self) -> str:
        """Get description of educational IO server."""
        return (
            "Educational guidance for SciTeX I/O adoption. Provides explanations, "
            "examples, and learning plans instead of automated translation. "
            "Helps users understand SciTeX patterns and apply them correctly."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available educational tools."""
        return [
            "explain_io_conversion",
            "suggest_scitex_workflow", 
            "create_learning_plan"
        ]


# Main entry point
if __name__ == "__main__":
    server = ScitexIOEducationalServer()
    asyncio.run(server.run())

# EOF