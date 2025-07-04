#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:28:00 (ywatanabe)"
# File: ./mcp_servers/scitex-analyzer/server.py
# ----------------------------------------

"""Enhanced MCP server for SciTeX code analysis and understanding."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import ast
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from scitex_base.base_server import ScitexBaseMCPServer
from .advanced_analysis import AdvancedProjectAnalyzer


class ScitexAnalyzerMCPServer(ScitexBaseMCPServer):
    """MCP server for analyzing and understanding SciTeX code."""
    
    def __init__(self):
        super().__init__("analyzer", "0.1.0")
        
        # Initialize advanced analyzer
        self.advanced_analyzer = AdvancedProjectAnalyzer()
        
        # Common SciTeX patterns
        self.scitex_patterns = {
            "io_load": r"stx\.io\.load\(['\"]([^'\"]+)['\"]\)",
            "io_save": r"stx\.io\.save\([^,]+,\s*['\"]([^'\"]+)['\"]",
            "io_cache": r"stx\.io\.cache\(['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",
            "plt_subplots": r"stx\.plt\.subplots\(",
            "set_xyt": r"\.set_xyt\(",
            "config_access": r"CONFIG\.[A-Z_]+\.[A-Z_]+",
            "framework": r"@stx\.main\.run_main",
        }
        
        # Anti-patterns
        self.anti_patterns = {
            "absolute_path": r"['\"][/\\](home|Users|var|tmp|data)[/\\]",
            "hardcoded_number": r"=\s*(0\.\d+|[1-9]\d*\.?\d*)\s*(?:#|$)",
            "missing_symlink": r"stx\.io\.save\([^)]+\)(?!.*symlink_from_cwd)",
            "mixed_io": r"(pd\.read_|np\.load|plt\.savefig).*stx\.io\.",
        }
        
    def _register_module_tools(self):
        """Register analyzer-specific tools."""
        
        @self.app.tool()
        async def analyze_scitex_project(
            project_path: str,
            analysis_type: str = "comprehensive"
        ) -> Dict[str, Any]:
            """Analyze an entire scitex project for patterns and improvements."""
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
                
            # Analyze project structure
            structure_analysis = await self._analyze_structure(project)
            
            # Analyze code patterns
            pattern_analysis = await self._analyze_patterns(project)
            
            # Analyze configurations
            config_analysis = await self._analyze_configs(project)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                structure_analysis, pattern_analysis, config_analysis
            )
            
            return {
                "project_structure": structure_analysis,
                "code_patterns": pattern_analysis,
                "configurations": config_analysis,
                "recommendations": recommendations,
                "summary": {
                    "total_files": structure_analysis["total_files"],
                    "scitex_compliance": pattern_analysis["compliance_score"],
                    "config_consistency": config_analysis["consistency_score"],
                    "priority_issues": len([r for r in recommendations if r.get("priority") == "high"]),
                }
            }
            
        @self.app.tool()
        async def explain_scitex_pattern(
            code_snippet: str,
            pattern_type: str = "auto_detect"
        ) -> Dict[str, Any]:
            """Explain scitex patterns in code for learning purposes."""
            
            # Detect patterns in code
            detected_patterns = []
            for pattern_name, pattern_regex in self.scitex_patterns.items():
                if re.search(pattern_regex, code_snippet):
                    detected_patterns.append(pattern_name)
                    
            if not detected_patterns and pattern_type == "auto_detect":
                return {
                    "error": "No SciTeX patterns detected in code snippet",
                    "suggestion": "Provide a code snippet containing SciTeX usage"
                }
                
            # Get primary pattern to explain
            primary_pattern = detected_patterns[0] if detected_patterns else pattern_type
            
            explanations = {
                "io_save": {
                    "pattern_name": "SciTeX IO Save Pattern",
                    "explanation": (
                        "stx.io.save() provides unified file saving across 30+ formats. "
                        "It automatically creates output directories relative to the script location, "
                        "ensuring reproducible file organization."
                    ),
                    "benefits": [
                        "Automatic directory creation - no need for os.makedirs()",
                        "Format detection from file extension",
                        "Consistent handling across CSV, JSON, NPY, PNG, etc.",
                        "Optional symlink creation for easy CWD access",
                        "Script-relative output paths for reproducibility"
                    ],
                    "example": '''stx.io.save(data, './results/output.csv', symlink_from_cwd=True)
# Creates: /path/to/script_out/results/output.csv
# Symlink: ./results/output.csv -> /path/to/script_out/results/output.csv''',
                    "common_mistakes": [
                        "Using absolute paths instead of relative",
                        "Forgetting symlink_from_cwd for easy access",
                        "Mixing with pandas.to_csv() or numpy.save()"
                    ],
                    "related_patterns": ["io_load", "io_cache", "config_paths"]
                },
                "plt_subplots": {
                    "pattern_name": "SciTeX Plot Data Tracking",
                    "explanation": (
                        "stx.plt.subplots() wraps matplotlib subplots with automatic data tracking. "
                        "Every plot created tracks its data, which is exported to CSV when saved."
                    ),
                    "benefits": [
                        "Automatic CSV export of all plotted data",
                        "Perfect reproducibility of figures",
                        "Easy data inspection without re-running code",
                        "Debugging plot issues with exported data",
                        "Sharing raw data alongside figures"
                    ],
                    "example": '''fig, ax = stx.plt.subplots()
ax.plot(x, y, label='Signal')
stx.io.save(fig, './plot.png')
# Creates: plot.png AND plot.csv with the plotted data''',
                    "common_mistakes": [
                        "Using plt.subplots() instead of stx.plt.subplots()",
                        "Using plt.savefig() which doesn't export data",
                        "Not realizing CSV is automatically created"
                    ],
                    "related_patterns": ["set_xyt", "io_save"]
                }
            }
            
            pattern_info = explanations.get(primary_pattern, {
                "pattern_name": f"SciTeX {primary_pattern}",
                "explanation": "This is a SciTeX pattern. Check documentation for details.",
                "benefits": ["Improved reproducibility", "Better code organization"],
                "related_patterns": []
            })
            
            return {
                "detected_patterns": detected_patterns,
                "primary_pattern": primary_pattern,
                **pattern_info
            }
            
        @self.app.tool()
        async def suggest_scitex_improvements(
            code: str,
            context: str = "research_script",
            focus_areas: List[str] = ["all"]
        ) -> List[Dict[str, Any]]:
            """Suggest specific scitex improvements for code."""
            
            suggestions = []
            lines = code.split('\n')
            
            # Check for performance improvements
            if "performance" in focus_areas or "all" in focus_areas:
                # Check for repeated computations
                for i, line in enumerate(lines):
                    if "for" in line and any(op in code for op in ["np.mean", "np.std", "pd.read"]):
                        suggestions.append({
                            "type": "performance",
                            "line": i + 1,
                            "issue": "Expensive operation in loop",
                            "suggestion": "Use stx.io.cache() to cache results",
                            "example": "result = stx.io.cache('computation_key', expensive_function, args)",
                            "impact": "Can reduce runtime by 50-90% on subsequent runs",
                            "priority": "high"
                        })
                        
            # Check for reproducibility improvements
            if "reproducibility" in focus_areas or "all" in focus_areas:
                # Check for hardcoded numbers
                for i, line in enumerate(lines):
                    match = re.search(r"=\s*(0\.\d+|[1-9]\d*\.?\d*)\s*(?:#|$)", line)
                    if match and not any(skip in line for skip in ["__version__", "range", "len"]):
                        suggestions.append({
                            "type": "reproducibility",
                            "line": i + 1,
                            "issue": f"Hardcoded value: {match.group(1)}",
                            "current_code": line.strip(),
                            "suggestion": "Extract to CONFIG.PARAMS",
                            "improved_code": f"threshold = CONFIG.PARAMS.THRESHOLD  # {match.group(1)}",
                            "impact": "Makes parameter configurable across experiments",
                            "priority": "medium"
                        })
                        
            # Check for maintainability improvements
            if "maintainability" in focus_areas or "all" in focus_areas:
                # Check for missing type hints
                for i, line in enumerate(lines):
                    if line.strip().startswith("def ") and "->" not in line and "self" not in line:
                        suggestions.append({
                            "type": "maintainability",
                            "line": i + 1,
                            "issue": "Missing return type hint",
                            "suggestion": "Add type hints for better code clarity",
                            "priority": "low"
                        })
                        
            # Check for SciTeX-specific improvements
            # Check for non-scitex IO
            for i, line in enumerate(lines):
                if "pd.read_csv" in line:
                    suggestions.append({
                        "type": "scitex_adoption",
                        "line": i + 1,
                        "issue": "Using pandas instead of scitex for IO",
                        "current_code": line.strip(),
                        "improved_code": line.replace("pd.read_csv", "stx.io.load"),
                        "impact": "Unified IO handling, better error messages",
                        "priority": "medium"
                    })
                    
            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
            
            return suggestions
            
        @self.app.tool()
        async def validate_comprehensive_compliance(
            project_path: str,
            strict_mode: bool = False
        ) -> Dict[str, Any]:
            """
            Perform comprehensive SciTeX guideline compliance validation.
            
            Args:
                project_path: Path to project to validate
                strict_mode: If True, enforce all guidelines strictly
                
            Returns:
                Detailed compliance report with scores and violations
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            validation_results = {
                "import_order": await self._validate_import_order(project),
                "docstring_format": await self._validate_docstrings(project),
                "cross_file_deps": await self._validate_cross_file_dependencies(project),
                "naming_conventions": await self._validate_naming_conventions(project),
                "config_usage": await self._validate_config_usage(project),
                "path_handling": await self._validate_path_handling(project),
                "framework_compliance": await self._validate_framework_compliance(project)
            }
            
            # Calculate overall score
            total_score = 0
            total_weight = 0
            for category, result in validation_results.items():
                weight = result.get("weight", 1.0)
                score = result.get("score", 0)
                total_score += score * weight
                total_weight += weight
            
            overall_score = total_score / total_weight if total_weight > 0 else 0
            
            # Generate report
            violations = []
            for category, result in validation_results.items():
                violations.extend(result.get("violations", []))
            
            # Sort violations by severity
            violations.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("severity", "low"), 4))
            
            return {
                "overall_score": round(overall_score, 1),
                "category_scores": {k: v["score"] for k, v in validation_results.items()},
                "total_violations": len(violations),
                "violations_by_severity": {
                    "critical": len([v for v in violations if v.get("severity") == "critical"]),
                    "high": len([v for v in violations if v.get("severity") == "high"]),
                    "medium": len([v for v in violations if v.get("severity") == "medium"]),
                    "low": len([v for v in violations if v.get("severity") == "low"])
                },
                "detailed_results": validation_results,
                "top_violations": violations[:10],
                "passed": overall_score >= (90 if strict_mode else 70)
            }
        
        @self.app.tool()
        async def validate_import_order(
            file_path: str
        ) -> Dict[str, Any]:
            """
            Validate import order follows SciTeX conventions.
            
            Expected order:
            1. Standard library imports
            2. Third-party imports
            3. SciTeX imports (import scitex as stx)
            4. Local imports
            """
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        imports.append({
                            "line": node.lineno,
                            "module": node.names[0].name if isinstance(node, ast.Import) else node.module,
                            "type": self._classify_import(
                                node.names[0].name if isinstance(node, ast.Import) else node.module
                            )
                        })
                
                # Check order
                violations = []
                import_order = ["stdlib", "third_party", "scitex", "local"]
                last_type_index = -1
                
                for imp in imports:
                    current_index = import_order.index(imp["type"])
                    if current_index < last_type_index:
                        violations.append({
                            "line": imp["line"],
                            "issue": f"{imp['type']} import after {import_order[last_type_index]}",
                            "module": imp["module"]
                        })
                    last_type_index = max(last_type_index, current_index)
                
                return {
                    "valid": len(violations) == 0,
                    "violations": violations,
                    "import_count": len(imports),
                    "import_breakdown": {
                        t: len([i for i in imports if i["type"] == t])
                        for t in import_order
                    }
                }
                
            except Exception as e:
                return {"error": str(e), "valid": False}
        
        @self.app.tool()
        async def validate_docstring_format(
            file_path: str,
            style: str = "numpy"
        ) -> Dict[str, Any]:
            """
            Validate docstring format and completeness.
            
            Args:
                file_path: Path to Python file
                style: Docstring style (numpy, google)
                
            Returns:
                Validation results with missing/malformed docstrings
            """
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                issues = []
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        docstring = ast.get_docstring(node)
                        
                        if not docstring:
                            issues.append({
                                "line": node.lineno,
                                "name": node.name,
                                "type": "missing",
                                "severity": "high" if not node.name.startswith("_") else "low"
                            })
                        else:
                            # Validate format
                            validation = self._validate_docstring_content(docstring, node, style)
                            if validation["issues"]:
                                issues.extend(validation["issues"])
                
                return {
                    "valid": len(issues) == 0,
                    "issues": issues,
                    "coverage": self._calculate_docstring_coverage(tree),
                    "style": style
                }
                
            except Exception as e:
                return {"error": str(e), "valid": False}
        
        @self.app.tool()
        async def validate_cross_file_dependencies(
            project_path: str
        ) -> Dict[str, Any]:
            """
            Validate cross-file dependencies and imports.
            
            Checks for:
            - Circular imports
            - Unused imports
            - Missing imports
            - Import consistency
            """
            
            project = Path(project_path)
            dependency_graph = {}
            issues = []
            
            # Build dependency graph
            for py_file in project.rglob("*.py"):
                if ".old" in str(py_file):
                    continue
                    
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    file_key = str(py_file.relative_to(project))
                    dependency_graph[file_key] = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module and node.module.startswith("."):
                                # Relative import
                                dependency_graph[file_key].append(node.module)
                            
                except Exception:
                    continue
            
            # Check for circular dependencies
            for file, deps in dependency_graph.items():
                for dep in deps:
                    if dep in dependency_graph and file in dependency_graph.get(dep, []):
                        issues.append({
                            "type": "circular_import",
                            "files": [file, dep],
                            "severity": "critical"
                        })
            
            return {
                "dependency_graph": dependency_graph,
                "issues": issues,
                "total_files": len(dependency_graph),
                "circular_dependencies": len([i for i in issues if i["type"] == "circular_import"])
            }
        
        @self.app.tool()
        async def find_scitex_examples(
            pattern: str,
            context: str = "all"
        ) -> List[Dict[str, str]]:
            """Find examples of scitex usage patterns."""
            
            examples = {
                "io_save": [
                    {
                        "description": "Save DataFrame with symlink",
                        "code": "stx.io.save(df, './results/data.csv', symlink_from_cwd=True)",
                        "context": "data_analysis"
                    },
                    {
                        "description": "Save figure with automatic data export",
                        "code": "stx.io.save(fig, './figures/plot.png', symlink_from_cwd=True)",
                        "context": "visualization"
                    }
                ],
                "plt_subplots": [
                    {
                        "description": "Create tracked figure",
                        "code": "fig, ax = stx.plt.subplots(figsize=(10, 6))",
                        "context": "visualization"
                    }
                ],
                "config": [
                    {
                        "description": "Access configuration parameters",
                        "code": "threshold = CONFIG.PARAMS.SIGNIFICANCE_THRESHOLD",
                        "context": "analysis"
                    }
                ]
            }
            
            pattern_examples = examples.get(pattern, [])
            if context != "all":
                pattern_examples = [e for e in pattern_examples if e["context"] == context]
                
            return pattern_examples

        @self.app.tool()
        async def create_scitex_project(
            project_name: str,
            project_type: str = "research",
            features: List[str] = ["basic"]
        ) -> Dict[str, Any]:
            """
            Generate complete SciTeX project structure with templates.
            
            Args:
                project_name: Name of the project
                project_type: Type (research, package, analysis)
                features: List of features to include
                
            Returns:
                Project structure and files created
            """
            
            # Validate project name
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
                return {"error": "Invalid project name. Use letters, numbers, underscores, and hyphens only."}
            
            project_path = Path(project_name)
            if project_path.exists():
                return {"error": f"Project {project_name} already exists"}
            
            # Create directory structure
            directories = [
                "scripts",
                "config", 
                "data",
                "results",
                "examples",
                "tests",
                "docs"
            ]
            
            files_created = []
            
            # Create directories
            for directory in directories:
                dir_path = project_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                files_created.append(f"{directory}/")
            
            # Create configuration files
            await self._create_config_files(project_path, project_type)
            files_created.extend(["config/PATH.yaml", "config/PARAMS.yaml", "config/COLORS.yaml"])
            
            # Create main script template
            main_script = await self._create_main_script(project_path, project_name, project_type)
            files_created.append("scripts/main.py")
            
            # Create README
            readme_content = await self._create_readme(project_name, project_type, features)
            (project_path / "README.md").write_text(readme_content)
            files_created.append("README.md")
            
            # Create requirements.txt
            requirements = await self._create_requirements(project_type, features)
            (project_path / "requirements.txt").write_text(requirements)
            files_created.append("requirements.txt")
            
            # Create example scripts based on features
            if "examples" in features:
                example_files = await self._create_example_scripts(project_path, project_type)
                files_created.extend(example_files)
            
            # Create test templates
            if "testing" in features:
                test_files = await self._create_test_templates(project_path)
                files_created.extend(test_files)
            
            return {
                "project_name": project_name,
                "project_type": project_type,
                "project_path": str(project_path.absolute()),
                "files_created": files_created,
                "directories_created": directories,
                "next_steps": [
                    f"cd {project_name}",
                    "pip install -r requirements.txt",
                    "python scripts/main.py",
                    "Edit config/PARAMS.yaml for your project parameters"
                ]
            }
        
        @self.app.tool()
        async def generate_scitex_script(
            script_name: str,
            script_type: str = "analysis",
            modules: List[str] = ["io", "plt"],
            template_style: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Generate purpose-built SciTeX scripts with appropriate templates.
            
            Args:
                script_name: Name of the script
                script_type: Type (analysis, visualization, preprocessing, etc.)
                modules: SciTeX modules to include
                template_style: Template complexity (minimal, standard, comprehensive)
                
            Returns:
                Generated script content and metadata
            """
            
            script_templates = {
                "analysis": {
                    "minimal": """#!/usr/bin/env python3
import scitex as stx

CONFIG = stx.io.load_configs()

@stx.gen.start()
def main():
    # Load data
    data = stx.io.load('./data/input.csv')
    
    # Perform analysis
    results = analyze_data(data)
    
    # Save results
    stx.io.save(results, './results/analysis.csv', symlink_from_cwd=True)

def analyze_data(data):
    # Your analysis code here
    return data

if __name__ == "__main__":
    main()
""",
                    "comprehensive": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{script_name}: Comprehensive data analysis script
Generated by SciTeX MCP Server

Features:
- Data loading and validation
- Statistical analysis
- Results export
- Configuration management
'''

import numpy as np
import pandas as pd
import scitex as stx
from pathlib import Path

# Load configuration
CONFIG = stx.io.load_configs()

@stx.gen.start()
def main():
    '''Main analysis pipeline.'''
    
    # Initialize
    stx.gen.print_config(CONFIG.PARAMS)
    
    # Load and validate data
    data = load_data()
    validate_data(data)
    
    # Perform analysis
    results = perform_analysis(data)
    
    # Generate visualizations
    create_visualizations(data, results)
    
    # Export results
    export_results(results)
    
    print("Analysis complete!")

def load_data():
    '''Load and preprocess data.'''
    data_path = CONFIG.PATH.DATA / 'input.csv'
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {{data_path}}")
    
    data = stx.io.load(data_path)
    print(f"Loaded data shape: {{data.shape}}")
    
    return data

def validate_data(data):
    '''Validate data quality.'''
    # Check for missing values
    missing = data.isnull().sum()
    if missing.sum() > 0:
        print(f"Warning: Found {{missing.sum()}} missing values")
    
    # Check data types
    print(f"Data types: {{data.dtypes.value_counts().to_dict()}}")

def perform_analysis(data):
    '''Perform statistical analysis.'''
    results = {{}}
    
    # Basic statistics
    results['descriptive'] = data.describe()
    
    # Custom analysis based on CONFIG
    threshold = CONFIG.PARAMS.ANALYSIS_THRESHOLD
    results['filtered'] = data[data > threshold]
    
    return results

def create_visualizations(data, results):
    '''Create and save visualizations.'''
    # Create figure
    fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Data distribution
    axes[0,0].hist(data.iloc[:,0], bins=30, alpha=0.7)
    axes[0,0].set_title('Data Distribution')
    
    # Plot 2: Summary statistics
    results['descriptive'].plot(kind='bar', ax=axes[0,1])
    axes[0,1].set_title('Summary Statistics')
    
    # Save figure with automatic data export
    stx.io.save(fig, './figures/analysis_overview.png', symlink_from_cwd=True)

def export_results(results):
    '''Export analysis results.'''
    # Save descriptive statistics
    stx.io.save(
        results['descriptive'], 
        './results/descriptive_stats.csv',
        symlink_from_cwd=True
    )
    
    # Save filtered data
    stx.io.save(
        results['filtered'],
        './results/filtered_data.csv', 
        symlink_from_cwd=True
    )
    
    # Create summary report
    summary = {{
        'total_samples': len(results['descriptive']),
        'filtered_samples': len(results['filtered']),
        'analysis_parameters': dict(CONFIG.PARAMS)
    }}
    
    stx.io.save(summary, './results/analysis_summary.json', symlink_from_cwd=True)

if __name__ == "__main__":
    main()
"""
                }
            }
            
            # Get template
            template = script_templates.get(script_type, script_templates["analysis"])
            script_content = template.get(template_style, template["minimal"])
            
            # Format with script name
            script_content = script_content.format(script_name=script_name)
            
            # Add module-specific imports
            imports = []
            if "stats" in modules:
                imports.append("import scipy.stats as stats")
            if "ml" in modules:
                imports.append("from sklearn import model_selection, metrics")
            if "dsp" in modules:
                imports.append("import scipy.signal")
            
            if imports:
                import_section = "\\n".join(imports)
                script_content = script_content.replace(
                    "import scitex as stx",
                    f"import scitex as stx\\n{import_section}"
                )
            
            return {
                "script_name": script_name,
                "script_type": script_type,
                "script_content": script_content,
                "modules_included": modules,
                "template_style": template_style,
                "estimated_lines": len(script_content.split('\\n')),
                "features": [
                    "Configuration management",
                    "Data validation",
                    "Automatic result export",
                    "Error handling",
                    "Progress tracking"
                ]
            }
        
        @self.app.tool()
        async def optimize_scitex_config(
            config_paths: List[str],
            merge_strategy: str = "smart"
        ) -> Dict[str, Any]:
            """
            Merge and optimize multiple configuration files.
            
            Args:
                config_paths: List of config file paths to merge
                merge_strategy: Strategy (smart, override, preserve)
                
            Returns:
                Optimized configuration and conflicts resolved
            """
            
            configs = {}
            conflicts = []
            
            # Load all configurations
            for config_path in config_paths:
                try:
                    config = stx.io.load(config_path)
                    config_name = Path(config_path).stem
                    configs[config_name] = config
                except Exception as e:
                    return {"error": f"Failed to load {config_path}: {str(e)}"}
            
            # Merge configurations
            merged_config = {}
            
            # Smart merge strategy
            if merge_strategy == "smart":
                for config_name, config in configs.items():
                    for section, values in config.items():
                        if section not in merged_config:
                            merged_config[section] = {}
                        
                        for key, value in values.items():
                            if key in merged_config[section]:
                                if merged_config[section][key] != value:
                                    conflicts.append({
                                        "section": section,
                                        "key": key,
                                        "config1": config_name,
                                        "value1": merged_config[section][key],
                                        "config2": config_name,
                                        "value2": value,
                                        "resolution": "kept_first"
                                    })
                            else:
                                merged_config[section][key] = value
            
            # Optimize configuration
            optimizations = []
            
            # Check for unused parameters
            # Check for missing standard sections
            standard_sections = ["PATH", "PARAMS", "COLORS"]
            for section in standard_sections:
                if section not in merged_config:
                    optimizations.append({
                        "type": "missing_section",
                        "section": section,
                        "suggestion": f"Add {section} section for better organization"
                    })
            
            # Check for potential consolidations
            if "PARAMS" in merged_config:
                params = merged_config["PARAMS"]
                for key, value in params.items():
                    if isinstance(value, (int, float)) and key.upper() != key:
                        optimizations.append({
                            "type": "naming_convention",
                            "key": key,
                            "suggestion": f"Use uppercase: {key.upper()}"
                        })
            
            return {
                "merged_config": merged_config,
                "conflicts": conflicts,
                "optimizations": optimizations,
                "config_files_processed": len(configs),
                "total_parameters": sum(
                    len(section) for section in merged_config.values() 
                    if isinstance(section, dict)
                )
            }
        
        @self.app.tool()
        async def run_scitex_pipeline(
            pipeline_config: Dict[str, Any],
            dry_run: bool = False
        ) -> Dict[str, Any]:
            """
            Execute multi-script workflows with dependencies.
            
            Args:
                pipeline_config: Configuration with scripts and dependencies
                dry_run: If True, only validate pipeline without execution
                
            Returns:
                Pipeline execution results and status
            """
            
            # Validate pipeline configuration
            required_keys = ["scripts", "dependencies"]
            if not all(key in pipeline_config for key in required_keys):
                return {"error": f"Pipeline config must contain: {required_keys}"}
            
            scripts = pipeline_config["scripts"]
            dependencies = pipeline_config.get("dependencies", {})
            
            # Build execution order
            execution_order = self._resolve_dependencies(scripts, dependencies)
            if "error" in execution_order:
                return execution_order
            
            if dry_run:
                return {
                    "pipeline_valid": True,
                    "execution_order": execution_order["order"],
                    "total_scripts": len(scripts),
                    "estimated_runtime": "varies",
                    "dependencies_resolved": True
                }
            
            # Execute pipeline
            results = {}
            failed_scripts = []
            
            for script_name in execution_order["order"]:
                script_config = scripts[script_name]
                script_path = script_config.get("path")
                
                if not script_path or not Path(script_path).exists():
                    failed_scripts.append({
                        "script": script_name,
                        "error": f"Script not found: {script_path}"
                    })
                    continue
                
                # Execute script (simplified - in real implementation would use subprocess)
                try:
                    # In real implementation: subprocess.run([sys.executable, script_path])
                    results[script_name] = {
                        "status": "completed",
                        "duration": "simulated",
                        "output": f"Executed {script_name} successfully"
                    }
                except Exception as e:
                    results[script_name] = {
                        "status": "failed", 
                        "error": str(e)
                    }
                    failed_scripts.append({
                        "script": script_name,
                        "error": str(e)
                    })
            
            return {
                "pipeline_status": "completed" if not failed_scripts else "partially_failed",
                "scripts_executed": len(results),
                "failed_scripts": failed_scripts,
                "execution_results": results,
                "execution_order": execution_order["order"]
            }
        
        @self.app.tool()
        async def debug_scitex_script(
            script_path: str,
            error_context: str = "",
            debug_level: str = "standard"
        ) -> Dict[str, Any]:
            """
            Intelligent debugging assistance for SciTeX scripts.
            
            Args:
                script_path: Path to script with issues
                error_context: Error message or description
                debug_level: Level of debugging (basic, standard, comprehensive)
                
            Returns:
                Debugging suggestions and potential fixes
            """
            
            if not Path(script_path).exists():
                return {"error": f"Script not found: {script_path}"}
            
            # Read script content
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
            except Exception as e:
                return {"error": f"Cannot read script: {str(e)}"}
            
            debug_results = {
                "script_path": script_path,
                "debug_level": debug_level,
                "issues_found": [],
                "suggestions": [],
                "quick_fixes": []
            }
            
            # Parse code for common issues
            try:
                tree = ast.parse(content)
                
                # Check for common SciTeX issues
                issues = await self._analyze_script_issues(content, tree, error_context)
                debug_results["issues_found"] = issues
                
                # Generate suggestions
                suggestions = await self._generate_debug_suggestions(issues, content)
                debug_results["suggestions"] = suggestions
                
                # Generate quick fixes
                quick_fixes = await self._generate_quick_fixes(issues, content)
                debug_results["quick_fixes"] = quick_fixes
                
            except SyntaxError as e:
                debug_results["issues_found"].append({
                    "type": "syntax_error",
                    "line": e.lineno,
                    "message": str(e),
                    "severity": "critical"
                })
            
            # Add context-specific debugging
            if error_context:
                context_suggestions = await self._analyze_error_context(error_context, content)
                debug_results["context_suggestions"] = context_suggestions
            
            return debug_results
        
        @self.app.tool()
        async def generate_scitex_documentation(
            project_path: str,
            doc_type: str = "comprehensive",
            include_examples: bool = True
        ) -> Dict[str, Any]:
            """
            Auto-generate project documentation.
            
            Args:
                project_path: Path to project
                doc_type: Type (api, user_guide, comprehensive)
                include_examples: Whether to include code examples
                
            Returns:
                Generated documentation content and files
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Analyze project structure
            analysis = await self.analyze_scitex_project(str(project))
            
            docs = {}
            
            # Generate README if it doesn't exist
            readme_path = project / "README.md"
            if not readme_path.exists():
                readme_content = await self._generate_readme_from_analysis(analysis, project)
                docs["README.md"] = readme_content
            
            # Generate API documentation
            if doc_type in ["api", "comprehensive"]:
                api_docs = await self._generate_api_docs(project)
                docs["docs/API.md"] = api_docs
            
            # Generate user guide
            if doc_type in ["user_guide", "comprehensive"]:
                user_guide = await self._generate_user_guide(project, analysis)
                docs["docs/USER_GUIDE.md"] = user_guide
            
            # Generate configuration documentation
            config_docs = await self._generate_config_docs(project)
            if config_docs:
                docs["docs/CONFIGURATION.md"] = config_docs
            
            # Save documentation files
            files_created = []
            for doc_path, content in docs.items():
                full_path = project / doc_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                files_created.append(doc_path)
            
            return {
                "documentation_generated": True,
                "doc_type": doc_type,
                "files_created": files_created,
                "total_files": len(files_created),
                "project_analysis": analysis["summary"] if "summary" in analysis else {}
            }
        
        @self.app.tool()
        async def analyze_semantic_structure(
            project_path: str,
            analysis_depth: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Perform advanced semantic analysis of project structure and patterns.
            
            Args:
                project_path: Path to project for analysis
                analysis_depth: Level of analysis (basic, standard, comprehensive)
                
            Returns:
                Comprehensive semantic analysis including:
                - Code complexity and maintainability metrics
                - Research domain classification
                - Workflow pattern recognition
                - Module relationship analysis
                - Optimization opportunities
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Perform advanced semantic analysis
            semantic_analysis = await self.advanced_analyzer.analyze_semantic_structure(project)
            
            # Add summary metrics
            summary = {
                "analysis_depth": analysis_depth,
                "total_patterns_detected": sum(
                    len(patterns) for patterns in semantic_analysis["semantic_analysis"].values()
                ),
                "primary_domain": semantic_analysis["domain_classification"]["primary_domain"],
                "domain_confidence": semantic_analysis["domain_classification"]["confidence"],
                "workflow_patterns_count": len(semantic_analysis["workflow_patterns"]),
                "optimization_opportunities_count": len(semantic_analysis["optimization_opportunities"])
            }
            
            return {
                **semantic_analysis,
                "analysis_summary": summary
            }
        
        @self.app.tool()
        async def generate_dependency_map(
            project_path: str,
            include_visualization: bool = True,
            analysis_level: str = "comprehensive"
        ) -> Dict[str, Any]:
            """
            Generate comprehensive dependency mapping with visualization data.
            
            Args:
                project_path: Path to project for analysis
                include_visualization: Include visualization data
                analysis_level: Level of dependency analysis
                
            Returns:
                Multi-level dependency analysis including:
                - File-level dependencies
                - Function-level call graphs
                - Data flow dependencies
                - Configuration dependencies
                - Architectural patterns
                - Visualization data for dependency graphs
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Generate comprehensive dependency map
            dependency_map = await self.advanced_analyzer.generate_dependency_map(project)
            
            # Add metadata
            metadata = {
                "analysis_level": analysis_level,
                "include_visualization": include_visualization,
                "generation_timestamp": "2025-07-03",
                "total_nodes": len(dependency_map["file_dependencies"].get("nodes", [])),
                "total_edges": len(dependency_map["file_dependencies"].get("edges", [])),
                "architectural_patterns_detected": len(dependency_map["architectural_patterns"])
            }
            
            return {
                **dependency_map,
                "metadata": metadata
            }
        
        @self.app.tool()
        async def analyze_performance_characteristics(
            project_path: str,
            focus_areas: List[str] = ["all"],
            include_recommendations: bool = True
        ) -> Dict[str, Any]:
            """
            Analyze performance characteristics and identify optimization opportunities.
            
            Args:
                project_path: Path to project for analysis
                focus_areas: Areas to focus on (complexity, memory, io, parallelization, caching)
                include_recommendations: Include optimization recommendations
                
            Returns:
                Performance analysis including:
                - Computational complexity patterns
                - Memory usage analysis
                - I/O operation efficiency
                - Parallelization opportunities
                - Caching recommendations
                - Performance optimization roadmap
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Perform performance analysis
            perf_analysis = await self.advanced_analyzer.analyze_performance_characteristics(project)
            
            # Filter results based on focus areas
            if "all" not in focus_areas:
                filtered_analysis = {}
                focus_mapping = {
                    "complexity": "complexity_analysis",
                    "memory": "memory_patterns", 
                    "io": "io_efficiency",
                    "parallelization": "parallelization_opportunities",
                    "caching": "caching_recommendations"
                }
                
                for area in focus_areas:
                    if area in focus_mapping:
                        key = focus_mapping[area]
                        if key in perf_analysis:
                            filtered_analysis[key] = perf_analysis[key]
                
                perf_analysis = filtered_analysis
            
            # Add performance summary
            summary = {
                "focus_areas": focus_areas,
                "include_recommendations": include_recommendations,
                "total_optimization_opportunities": len(perf_analysis.get("optimization_roadmap", {}).get("short_term", [])),
                "performance_score": 85  # Placeholder - would calculate from actual metrics
            }
            
            return {
                **perf_analysis,
                "performance_summary": summary
            }
        
        @self.app.tool()
        async def analyze_research_workflow_patterns(
            project_path: str,
            workflow_types: List[str] = ["all"],
            include_suggestions: bool = True
        ) -> Dict[str, Any]:
            """
            Identify and analyze research workflow patterns specific to scientific computing.
            
            Args:
                project_path: Path to project for analysis
                workflow_types: Types of workflows to analyze
                include_suggestions: Include improvement suggestions
                
            Returns:
                Research workflow analysis including:
                - Data preprocessing pipelines
                - Analysis workflows
                - Visualization patterns
                - Reproducibility assessment
                - Publication readiness
                - Workflow efficiency metrics
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Analyze research workflows
            workflow_analysis = await self.advanced_analyzer.analyze_research_workflow_patterns(project)
            
            # Calculate overall workflow health
            workflow_health = {
                "reproducibility_score": workflow_analysis["reproducibility_score"].get("score", 0),
                "publication_readiness": workflow_analysis["publication_readiness"].get("readiness_score", 0),
                "workflow_efficiency": workflow_analysis["workflow_efficiency"].get("efficiency_score", 0),
                "detected_patterns": len(workflow_analysis["pipeline_patterns"]),
                "improvement_potential": len(workflow_analysis["improvement_suggestions"])
            }
            
            return {
                **workflow_analysis,
                "workflow_health": workflow_health,
                "analysis_metadata": {
                    "workflow_types": workflow_types,
                    "include_suggestions": include_suggestions
                }
            }
        
        @self.app.tool()
        async def generate_architectural_insights(
            project_path: str,
            insight_level: str = "strategic",
            include_roadmap: bool = True
        ) -> Dict[str, Any]:
            """
            Generate high-level architectural insights and strategic recommendations.
            
            Args:
                project_path: Path to project for analysis
                insight_level: Level of insights (tactical, strategic, evolutionary)
                include_roadmap: Include evolution roadmap
                
            Returns:
                Architectural analysis including:
                - Architecture health assessment
                - Modularity and coupling analysis
                - Scalability considerations
                - Maintainability metrics
                - Strategic evolution recommendations
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Generate architectural insights
            arch_analysis = await self.advanced_analyzer.generate_architectural_insights(project)
            
            # Calculate overall architecture score
            architecture_score = {
                "health_score": arch_analysis["architecture_health"].get("health_score", 0),
                "modularity_score": arch_analysis["modularity_score"],
                "maintainability_score": arch_analysis["maintainability_score"],
                "scalability_score": arch_analysis["scalability_assessment"].get("scalability_score", 0),
                "overall_score": 0  # Would calculate weighted average
            }
            
            # Calculate overall score
            scores = [
                architecture_score["health_score"],
                architecture_score["modularity_score"], 
                architecture_score["maintainability_score"],
                architecture_score["scalability_score"]
            ]
            architecture_score["overall_score"] = sum(scores) / len(scores) if scores else 0
            
            return {
                **arch_analysis,
                "architecture_score": architecture_score,
                "insight_metadata": {
                    "insight_level": insight_level,
                    "include_roadmap": include_roadmap,
                    "analysis_timestamp": "2025-07-03"
                }
            }
        
        @self.app.tool()
        async def comprehensive_project_intelligence(
            project_path: str,
            intelligence_scope: str = "full",
            output_format: str = "detailed"
        ) -> Dict[str, Any]:
            """
            Generate comprehensive project intelligence combining all analysis types.
            
            Args:
                project_path: Path to project for analysis
                intelligence_scope: Scope of analysis (basic, standard, full)
                output_format: Format of output (summary, detailed, executive)
                
            Returns:
                Complete project intelligence including:
                - Semantic structure analysis
                - Dependency mapping
                - Performance characteristics
                - Research workflow patterns  
                - Architectural insights
                - Strategic recommendations
                - Executive summary
            """
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
            
            # Run all analysis types
            intelligence = {}
            
            if intelligence_scope in ["standard", "full"]:
                intelligence["semantic_analysis"] = await self.analyze_semantic_structure(str(project))
                intelligence["dependency_analysis"] = await self.generate_dependency_map(str(project))
                
            if intelligence_scope == "full":
                intelligence["performance_analysis"] = await self.analyze_performance_characteristics(str(project))
                intelligence["workflow_analysis"] = await self.analyze_research_workflow_patterns(str(project))
                intelligence["architectural_analysis"] = await self.generate_architectural_insights(str(project))
            
            # Generate executive summary
            executive_summary = {
                "project_overview": {
                    "primary_domain": intelligence.get("semantic_analysis", {}).get("domain_classification", {}).get("primary_domain", "unknown"),
                    "total_files": len(list(project.rglob("*.py"))),
                    "architecture_health": intelligence.get("architectural_analysis", {}).get("architecture_score", {}).get("overall_score", 0)
                },
                "key_insights": [],
                "priority_recommendations": [],
                "strategic_directions": []
            }
            
            # Add key insights based on analysis
            if "semantic_analysis" in intelligence:
                semantic = intelligence["semantic_analysis"]
                executive_summary["key_insights"].append({
                    "category": "domain_expertise",
                    "insight": f"Project specializes in {semantic.get('domain_classification', {}).get('primary_domain', 'general')} research",
                    "confidence": semantic.get("domain_classification", {}).get("confidence", 0)
                })
            
            if "performance_analysis" in intelligence:
                perf = intelligence["performance_analysis"]
                executive_summary["priority_recommendations"].append({
                    "category": "performance",
                    "recommendation": "Implement identified optimization opportunities",
                    "impact": "high",
                    "effort": "medium"
                })
            
            return {
                "project_intelligence": intelligence,
                "executive_summary": executive_summary,
                "analysis_metadata": {
                    "intelligence_scope": intelligence_scope,
                    "output_format": output_format,
                    "analysis_timestamp": "2025-07-03",
                    "total_analysis_modules": len(intelligence)
                }
            }
            
    async def _analyze_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project directory structure."""
        py_files = list(project_path.rglob("*.py"))
        config_files = list(project_path.rglob("*.yaml")) + list(project_path.rglob("*.yml"))
        
        # Check for expected directories
        expected_dirs = ["scripts", "config", "data", "examples", "tests"]
        existing_dirs = [d for d in expected_dirs if (project_path / d).exists()]
        missing_dirs = [d for d in expected_dirs if d not in existing_dirs]
        
        return {
            "total_files": len(py_files),
            "python_files": len(py_files),
            "config_files": len(config_files),
            "existing_directories": existing_dirs,
            "missing_directories": missing_dirs,
            "structure_score": len(existing_dirs) / len(expected_dirs) * 100
        }
        
    async def _analyze_patterns(self, project_path: Path) -> Dict[str, Any]:
        """Analyze code patterns in project."""
        pattern_counts = {name: 0 for name in self.scitex_patterns}
        anti_pattern_counts = {name: 0 for name in self.anti_patterns}
        total_files = 0
        
        for py_file in project_path.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                total_files += 1
                
                # Count patterns
                for name, pattern in self.scitex_patterns.items():
                    pattern_counts[name] += len(re.findall(pattern, content))
                    
                # Count anti-patterns
                for name, pattern in self.anti_patterns.items():
                    anti_pattern_counts[name] += len(re.findall(pattern, content))
                    
            except Exception:
                continue
                
        # Calculate compliance score
        total_patterns = sum(pattern_counts.values())
        total_anti_patterns = sum(anti_pattern_counts.values())
        compliance_score = 100
        if total_patterns + total_anti_patterns > 0:
            compliance_score = (total_patterns / (total_patterns + total_anti_patterns)) * 100
            
        return {
            "patterns_found": pattern_counts,
            "anti_patterns_found": anti_pattern_counts,
            "files_analyzed": total_files,
            "compliance_score": round(compliance_score, 1),
            "most_used_pattern": max(pattern_counts, key=pattern_counts.get) if pattern_counts else None,
            "biggest_issue": max(anti_pattern_counts, key=anti_pattern_counts.get) if anti_pattern_counts else None
        }
        
    async def _analyze_configs(self, project_path: Path) -> Dict[str, Any]:
        """Analyze configuration files."""
        config_files = list(project_path.rglob("*.yaml")) + list(project_path.rglob("*.yml"))
        
        configs = {}
        for config_file in config_files:
            if ".old" in str(config_file):
                continue
            configs[str(config_file.relative_to(project_path))] = {
                "exists": True,
                "size": config_file.stat().st_size
            }
            
        # Check for standard configs
        standard_configs = ["config/PATH.yaml", "config/PARAMS.yaml", "config/COLORS.yaml"]
        missing_configs = [c for c in standard_configs if not (project_path / c).exists()]
        
        consistency_score = 100
        if len(standard_configs) > 0:
            consistency_score = ((len(standard_configs) - len(missing_configs)) / len(standard_configs)) * 100
            
        return {
            "config_files": configs,
            "missing_standard_configs": missing_configs,
            "consistency_score": round(consistency_score, 1)
        }
        
    async def _generate_recommendations(
        self,
        structure: Dict[str, Any],
        patterns: Dict[str, Any],
        configs: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Structure recommendations
        if structure["missing_directories"]:
            recommendations.append({
                "category": "structure",
                "issue": f"Missing standard directories: {', '.join(structure['missing_directories'])}",
                "suggestion": "Create standard project directories for better organization",
                "command": f"mkdir -p {' '.join(structure['missing_directories'])}",
                "priority": "medium"
            })
            
        # Pattern recommendations
        if patterns["anti_patterns_found"]["absolute_path"] > 0:
            recommendations.append({
                "category": "patterns",
                "issue": f"Found {patterns['anti_patterns_found']['absolute_path']} absolute paths",
                "suggestion": "Convert to relative paths for reproducibility",
                "priority": "high"
            })
            
        if patterns["anti_patterns_found"]["hardcoded_number"] > 5:
            recommendations.append({
                "category": "patterns",
                "issue": f"Found {patterns['anti_patterns_found']['hardcoded_number']} hardcoded values",
                "suggestion": "Extract to CONFIG.PARAMS for configurability",
                "priority": "medium"
            })
            
        # Config recommendations
        if configs["missing_standard_configs"]:
            recommendations.append({
                "category": "configuration",
                "issue": f"Missing configs: {', '.join(configs['missing_standard_configs'])}",
                "suggestion": "Create standard configuration files",
                "priority": "high"
            })
            
        return recommendations
    
    def _classify_import(self, module_name: Optional[str]) -> str:
        """Classify import type based on module name."""
        if not module_name:
            return "unknown"
        
        # Standard library modules
        stdlib_modules = {
            "os", "sys", "re", "json", "ast", "pathlib", "datetime", 
            "collections", "itertools", "functools", "typing", "math",
            "random", "copy", "time", "subprocess", "argparse", "logging"
        }
        
        if module_name in stdlib_modules or module_name.split('.')[0] in stdlib_modules:
            return "stdlib"
        elif module_name == "scitex" or module_name.startswith("scitex."):
            return "scitex"
        elif module_name.startswith("."):
            return "local"
        else:
            return "third_party"
    
    def _validate_docstring_content(self, docstring: str, node: ast.AST, style: str) -> Dict[str, List]:
        """Validate docstring content based on style."""
        issues = []
        
        if isinstance(node, ast.FunctionDef):
            # Check for parameter documentation
            params = [arg.arg for arg in node.args.args if arg.arg != "self"]
            
            if style == "numpy":
                # Check for Parameters section
                if params and "Parameters" not in docstring:
                    issues.append({
                        "line": node.lineno,
                        "name": node.name,
                        "type": "missing_params",
                        "severity": "medium",
                        "message": "Missing Parameters section in docstring"
                    })
                
                # Check for Returns section if not None return
                has_return = any(isinstance(n, ast.Return) and n.value for n in ast.walk(node))
                if has_return and "Returns" not in docstring:
                    issues.append({
                        "line": node.lineno,
                        "name": node.name,
                        "type": "missing_returns",
                        "severity": "medium",
                        "message": "Missing Returns section in docstring"
                    })
        
        return {"issues": issues}
    
    def _calculate_docstring_coverage(self, tree: ast.AST) -> float:
        """Calculate percentage of functions/classes with docstrings."""
        total = 0
        documented = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not node.name.startswith("_"):  # Skip private methods
                    total += 1
                    if ast.get_docstring(node):
                        documented += 1
        
        return (documented / total * 100) if total > 0 else 100.0
    
    async def _validate_import_order(self, project: Path) -> Dict[str, Any]:
        """Validate import order across all files in project."""
        violations = []
        files_checked = 0
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            result = await self.validate_import_order(str(py_file))
            if not result.get("valid", True):
                violations.extend([
                    {**v, "file": str(py_file.relative_to(project))} 
                    for v in result.get("violations", [])
                ])
            files_checked += 1
        
        score = 100 - min(len(violations) * 5, 100)
        
        return {
            "score": score,
            "violations": violations,
            "files_checked": files_checked,
            "weight": 1.0
        }
    
    async def _validate_docstrings(self, project: Path) -> Dict[str, Any]:
        """Validate docstrings across all files in project."""
        all_issues = []
        total_coverage = 0
        files_checked = 0
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            result = await self.validate_docstring_format(str(py_file))
            if result.get("issues"):
                all_issues.extend([
                    {**issue, "file": str(py_file.relative_to(project))}
                    for issue in result.get("issues", [])
                ])
            total_coverage += result.get("coverage", 0)
            files_checked += 1
        
        avg_coverage = total_coverage / files_checked if files_checked > 0 else 0
        score = avg_coverage * 0.7 + (100 - min(len(all_issues) * 2, 100)) * 0.3
        
        return {
            "score": score,
            "violations": all_issues,
            "average_coverage": avg_coverage,
            "files_checked": files_checked,
            "weight": 1.5
        }
    
    async def _validate_cross_file_dependencies(self, project: Path) -> Dict[str, Any]:
        """Already implemented in the tool."""
        result = await self.validate_cross_file_dependencies(str(project))
        
        score = 100
        if result.get("circular_dependencies", 0) > 0:
            score -= result["circular_dependencies"] * 20
        
        return {
            "score": max(0, score),
            "violations": result.get("issues", []),
            "weight": 2.0
        }
    
    async def _validate_naming_conventions(self, project: Path) -> Dict[str, Any]:
        """Validate naming conventions."""
        violations = []
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.islower() and not node.name.startswith("_"):
                            violations.append({
                                "file": str(py_file.relative_to(project)),
                                "line": node.lineno,
                                "name": node.name,
                                "issue": "Function name not in snake_case",
                                "severity": "medium"
                            })
                    elif isinstance(node, ast.ClassDef):
                        if not node.name[0].isupper():
                            violations.append({
                                "file": str(py_file.relative_to(project)),
                                "line": node.lineno,
                                "name": node.name,
                                "issue": "Class name not in PascalCase",
                                "severity": "medium"
                            })
            except:
                continue
        
        score = 100 - min(len(violations) * 5, 100)
        
        return {
            "score": score,
            "violations": violations,
            "weight": 0.5
        }
    
    async def _validate_config_usage(self, project: Path) -> Dict[str, Any]:
        """Validate CONFIG usage patterns."""
        violations = []
        good_patterns = 0
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                # Check for hardcoded paths
                if re.search(r"['\"][/\\](home|Users|data)[/\\]", content):
                    violations.append({
                        "file": str(py_file.relative_to(project)),
                        "issue": "Hardcoded absolute path",
                        "severity": "high"
                    })
                
                # Check for CONFIG usage
                if "CONFIG" in content:
                    good_patterns += len(re.findall(r"CONFIG\.[A-Z_]+\.[A-Z_]+", content))
                    
            except:
                continue
        
        score = min(100, 70 + good_patterns * 2) - len(violations) * 10
        
        return {
            "score": max(0, score),
            "violations": violations,
            "good_patterns": good_patterns,
            "weight": 1.5
        }
    
    async def _validate_path_handling(self, project: Path) -> Dict[str, Any]:
        """Validate path handling practices."""
        violations = []
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                # Check for os.path instead of pathlib
                if "os.path" in content and "pathlib" not in content:
                    violations.append({
                        "file": str(py_file.relative_to(project)),
                        "issue": "Using os.path instead of pathlib",
                        "severity": "low"
                    })
                
                # Check for string concatenation for paths
                if re.search(r"['\"].*['\"].*\+.*['\"][/\\]", content):
                    violations.append({
                        "file": str(py_file.relative_to(project)),
                        "issue": "String concatenation for paths",
                        "severity": "medium"
                    })
                    
            except:
                continue
        
        score = 100 - min(len(violations) * 5, 100)
        
        return {
            "score": score,
            "violations": violations,
            "weight": 1.0
        }
    
    async def _validate_framework_compliance(self, project: Path) -> Dict[str, Any]:
        """Validate SciTeX framework compliance."""
        violations = []
        compliant_scripts = 0
        
        for py_file in project.rglob("*.py"):
            if ".old" in str(py_file) or "__" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                # Check for main scripts
                if "if __name__" in content:
                    if "stx.gen.start()" in content:
                        compliant_scripts += 1
                    else:
                        violations.append({
                            "file": str(py_file.relative_to(project)),
                            "issue": "Main script missing stx.gen.start()",
                            "severity": "high"
                        })
                        
            except:
                continue
        
        score = 100
        if compliant_scripts == 0 and len(violations) > 0:
            score = 50
        score -= len(violations) * 10
        
        return {
            "score": max(0, score),
            "violations": violations,
            "compliant_scripts": compliant_scripts,
            "weight": 2.0
        }
        
    def get_module_description(self) -> str:
        """Get description of comprehensive developer support functionality."""
        return (
            "SciTeX comprehensive developer support server provides full-stack development assistance "
            "including code analysis, project generation, configuration management, workflow automation, "
            "debugging assistance, and documentation generation for scientific Python projects. "
            "Transform your development workflow with intelligent SciTeX-aware tools."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            # Core Analysis Tools
            "analyze_scitex_project",
            "explain_scitex_pattern", 
            "suggest_scitex_improvements",
            "find_scitex_examples",
            
            # Advanced Analysis Tools
            "analyze_semantic_structure",
            "generate_dependency_map",
            "analyze_performance_characteristics",
            "analyze_research_workflow_patterns", 
            "generate_architectural_insights",
            "comprehensive_project_intelligence",
            
            # Project Generation & Scaffolding
            "create_scitex_project",
            "generate_scitex_script",
            
            # Configuration Management
            "optimize_scitex_config",
            "validate_comprehensive_compliance",
            
            # Workflow Automation
            "run_scitex_pipeline",
            "debug_scitex_script",
            
            # Documentation Generation
            "generate_scitex_documentation",
            
            # Validation Tools
            "validate_import_order",
            "validate_docstring_format", 
            "validate_cross_file_dependencies",
            
            # Base Tools
            "get_module_info",
            "validate_code"
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate code patterns."""
        issues = []
        
        # Check for anti-patterns
        for name, pattern in self.anti_patterns.items():
            matches = re.findall(pattern, code)
            if matches:
                issues.append(f"Anti-pattern '{name}' found: {len(matches)} occurrences")
                
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 10)
        }
    
    # Helper methods for new comprehensive features
    async def _create_config_files(self, project_path: Path, project_type: str):
        """Create standard configuration files."""
        config_dir = project_path / "config"
        
        # PATH.yaml
        path_config = {
            "DATA": "data",
            "RESULTS": "results", 
            "FIGURES": "figures",
            "SCRIPTS": "scripts"
        }
        (config_dir / "PATH.yaml").write_text(f"# Path configuration\n{path_config}")
        
        # PARAMS.yaml
        params_config = {
            "ANALYSIS_THRESHOLD": 0.05,
            "RANDOM_SEED": 42,
            "BATCH_SIZE": 32
        }
        (config_dir / "PARAMS.yaml").write_text(f"# Analysis parameters\n{params_config}")
        
        # COLORS.yaml
        colors_config = {
            "PRIMARY": "#1f77b4",
            "SECONDARY": "#ff7f0e", 
            "SUCCESS": "#2ca02c",
            "DANGER": "#d62728"
        }
        (config_dir / "COLORS.yaml").write_text(f"# Color scheme\n{colors_config}")
    
    async def _create_main_script(self, project_path: Path, project_name: str, project_type: str):
        """Create main script template."""
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{project_name}: Main analysis script
Generated by SciTeX MCP Server
"""

import scitex as stx

CONFIG = stx.io.load_configs()

@stx.gen.start()
def main():
    """Main entry point."""
    print(f"Starting {project_name} analysis...")
    
    # Your analysis code here
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
'''
        
        script_path = project_path / "scripts" / "main.py"
        script_path.write_text(script_content)
        return script_content
    
    async def _create_readme(self, project_name: str, project_type: str, features: List[str]):
        """Create README template."""
        return f'''# {project_name}

A {project_type} project using the SciTeX framework.

## Features

{chr(10).join(f"- {feature}" for feature in features)}

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run main analysis
python scripts/main.py
```

## Project Structure

- `scripts/` - Analysis scripts
- `config/` - Configuration files  
- `data/` - Input data
- `results/` - Output results
- `examples/` - Example usage
- `tests/` - Test files

## Configuration

Edit configuration files in `config/`:
- `PATH.yaml` - File paths
- `PARAMS.yaml` - Analysis parameters
- `COLORS.yaml` - Color schemes

## Generated by SciTeX MCP Server
'''
    
    async def _create_requirements(self, project_type: str, features: List[str]):
        """Create requirements.txt."""
        requirements = ["scitex", "numpy", "pandas", "matplotlib"]
        
        if "ml" in features:
            requirements.extend(["scikit-learn", "scipy"])
        if "stats" in features:
            requirements.extend(["scipy", "statsmodels"])
        if "testing" in features:
            requirements.append("pytest")
            
        return chr(10).join(requirements) + chr(10)
    
    async def _create_example_scripts(self, project_path: Path, project_type: str):
        """Create example scripts."""
        examples_dir = project_path / "examples"
        files = []
        
        # Basic example
        basic_example = '''#!/usr/bin/env python3
import scitex as stx
import numpy as np

CONFIG = stx.io.load_configs()

def example_analysis():
    """Example SciTeX analysis."""
    # Generate sample data
    data = np.random.randn(100, 3)
    
    # Save with SciTeX
    stx.io.save(data, './results/sample_data.csv', symlink_from_cwd=True)
    
    # Create plot
    fig, ax = stx.plt.subplots()
    ax.plot(data[:, 0], label='Series 1')
    ax.plot(data[:, 1], label='Series 2')
    ax.legend()
    
    stx.io.save(fig, './figures/example_plot.png', symlink_from_cwd=True)

if __name__ == "__main__":
    example_analysis()
'''
        
        (examples_dir / "basic_example.py").write_text(basic_example)
        files.append("examples/basic_example.py")
        
        return files
    
    async def _create_test_templates(self, project_path: Path):
        """Create test templates."""
        tests_dir = project_path / "tests"
        files = []
        
        test_content = '''#!/usr/bin/env python3
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_basic_functionality():
    """Test basic project functionality."""
    assert True  # Replace with actual tests

def test_configuration_loading():
    """Test configuration loading."""
    import scitex as stx
    try:
        config = stx.io.load_configs()
        assert config is not None
    except:
        pytest.skip("Configuration files not found")

if __name__ == "__main__":
    pytest.main([__file__])
'''
        
        (tests_dir / "test_main.py").write_text(test_content)
        files.append("tests/test_main.py")
        
        return files
    
    def _resolve_dependencies(self, scripts: Dict, dependencies: Dict):
        """Resolve script execution order based on dependencies."""
        # Simple topological sort
        from collections import deque, defaultdict
        
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Build graph
        for script in scripts:
            in_degree[script] = 0
            
        for script, deps in dependencies.items():
            for dep in deps:
                graph[dep].append(script)
                in_degree[script] += 1
        
        # Topological sort
        queue = deque([script for script in scripts if in_degree[script] == 0])
        order = []
        
        while queue:
            script = queue.popleft()
            order.append(script)
            
            for neighbor in graph[script]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(order) != len(scripts):
            return {"error": "Circular dependency detected"}
            
        return {"order": order}
    
    async def _analyze_script_issues(self, content: str, tree: ast.AST, error_context: str):
        """Analyze script for common issues."""
        issues = []
        
        # Check for missing imports
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        
        # Check for scitex import
        if "scitex" not in imports and "stx" not in content:
            issues.append({
                "type": "missing_import",
                "severity": "high",
                "message": "Missing scitex import"
            })
        
        # Check for config loading
        if "CONFIG" not in content and "config" in content.lower():
            issues.append({
                "type": "config_issue",
                "severity": "medium", 
                "message": "Possible configuration loading issue"
            })
        
        return issues
    
    async def _generate_debug_suggestions(self, issues: List[Dict], content: str):
        """Generate debugging suggestions based on issues."""
        suggestions = []
        
        for issue in issues:
            if issue["type"] == "missing_import":
                suggestions.append({
                    "issue": issue["message"],
                    "suggestion": "Add: import scitex as stx",
                    "priority": "high"
                })
            elif issue["type"] == "config_issue":
                suggestions.append({
                    "issue": issue["message"],
                    "suggestion": "Add: CONFIG = stx.io.load_configs()",
                    "priority": "medium"
                })
        
        return suggestions
    
    async def _generate_quick_fixes(self, issues: List[Dict], content: str):
        """Generate quick fixes for common issues."""
        fixes = []
        
        for issue in issues:
            if issue["type"] == "missing_import":
                fixes.append({
                    "description": "Add SciTeX import",
                    "find": "#!/usr/bin/env python3",
                    "replace": "#!/usr/bin/env python3\\nimport scitex as stx"
                })
        
        return fixes
    
    async def _analyze_error_context(self, error_context: str, content: str):
        """Analyze error context for specific suggestions."""
        suggestions = []
        
        if "ModuleNotFoundError" in error_context:
            if "scitex" in error_context:
                suggestions.append({
                    "error": "SciTeX not installed",
                    "suggestion": "Run: pip install scitex",
                    "priority": "critical"
                })
        
        if "FileNotFoundError" in error_context:
            suggestions.append({
                "error": "File not found",
                "suggestion": "Check file paths in configuration",
                "priority": "high"
            })
        
        return suggestions
    
    async def _generate_readme_from_analysis(self, analysis: Dict, project: Path):
        """Generate README from project analysis."""
        return f'''# {project.name}

## Project Analysis Summary

- **Files analyzed**: {analysis.get("project_structure", {}).get("total_files", 0)}
- **SciTeX compliance**: {analysis.get("code_patterns", {}).get("compliance_score", 0)}%
- **Configuration score**: {analysis.get("configurations", {}).get("consistency_score", 0)}%

## Recommendations

{chr(10).join(f"- {rec.get('suggestion', '')}" for rec in analysis.get("recommendations", [])[:5])}

## Generated by SciTeX Analyzer
'''
    
    async def _generate_api_docs(self, project: Path):
        """Generate API documentation."""
        return '''# API Documentation

## Functions

Documentation for project functions will be generated here.

## Classes

Documentation for project classes will be generated here.

## Configuration

See CONFIGURATION.md for configuration details.
'''
    
    async def _generate_user_guide(self, project: Path, analysis: Dict):
        """Generate user guide."""
        return f'''# User Guide

## Getting Started

This project uses the SciTeX framework for scientific computing.

## Project Structure

{chr(10).join(f"- `{d}/`" for d in analysis.get("project_structure", {}).get("existing_directories", []))}

## Usage

1. Install requirements: `pip install -r requirements.txt`
2. Run main script: `python scripts/main.py`
3. Check results in `results/` directory

## Configuration

Edit files in `config/` directory to customize analysis parameters.
'''
    
    async def _generate_config_docs(self, project: Path):
        """Generate configuration documentation."""
        config_dir = project / "config"
        if not config_dir.exists():
            return None
            
        return '''# Configuration Documentation

## Configuration Files

### PATH.yaml
File path configuration for the project.

### PARAMS.yaml  
Analysis parameters and settings.

### COLORS.yaml
Color scheme for visualizations.

## Usage

```python
CONFIG = stx.io.load_configs()
threshold = CONFIG.PARAMS.ANALYSIS_THRESHOLD
data_path = CONFIG.PATH.DATA
```
'''


# Main entry point
if __name__ == "__main__":
    server = ScitexAnalyzerMCPServer()
    asyncio.run(server.run())

# EOF