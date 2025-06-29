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


class ScitexAnalyzerMCPServer(ScitexBaseMCPServer):
    """MCP server for analyzing and understanding SciTeX code."""
    
    def __init__(self):
        super().__init__("analyzer", "0.1.0")
        
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
        
    def get_module_description(self) -> str:
        """Get description of analyzer functionality."""
        return (
            "SciTeX analyzer provides comprehensive code analysis, pattern detection, "
            "and improvement suggestions for scientific Python projects. "
            "It helps understand code structure, identify anti-patterns, and suggest best practices."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "analyze_scitex_project",
            "explain_scitex_pattern",
            "suggest_scitex_improvements",
            "find_scitex_examples",
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


# Main entry point
if __name__ == "__main__":
    server = ScitexAnalyzerMCPServer()
    asyncio.run(server.run())

# EOF