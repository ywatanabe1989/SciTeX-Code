#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:46:00 (ywatanabe)"
# File: ./mcp_servers/scitex-validator/server.py
# ----------------------------------------

"""MCP server for comprehensive SciTeX compliance validation."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import ast
import yaml
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from scitex_base.base_server import ScitexBaseMCPServer


class ScitexValidatorMCPServer(ScitexBaseMCPServer):
    """MCP server for validating SciTeX compliance across all guidelines."""
    
    def __init__(self):
        super().__init__("validator", "0.1.0")
        self._load_guidelines()
        
    def _load_guidelines(self):
        """Load all SciTeX guidelines for validation."""
        self.guidelines = {
            "SCITEX-01": {
                "name": "Project Structure",
                "description": "Project organization and directory structure",
                "rules": [
                    "No Python files in project root (except setup.py, conftest.py)",
                    "Required directories: config/, scripts/, data/",
                    "Recommended: examples/, tests/, .playground/",
                    "Scripts organized by category under scripts/"
                ]
            },
            "SCITEX-02": {
                "name": "Script Template",
                "description": "Required script structure and components",
                "rules": [
                    "Shebang: #!/usr/bin/env python3",
                    "Encoding: # -*- coding: utf-8 -*-",
                    "Timestamp header with author",
                    "__FILE__ and __DIR__ definitions",
                    "Docstring with Functionalities, Dependencies, Input, Output",
                    "Section headers: Imports, Parameters, Functions & Classes",
                    "main() and run_main() functions",
                    "stx.gen.start() and stx.gen.close() calls"
                ]
            },
            "SCITEX-03": {
                "name": "Configuration System",
                "description": "Configuration file usage",
                "rules": [
                    "CONFIG = stx.io.load_configs()",
                    "Required: PATH.yaml, PARAMS.yaml, IS_DEBUG.yaml",
                    "No hardcoded paths (use CONFIG.PATH.*)",
                    "No hardcoded parameters (use CONFIG.PARAMS.*)"
                ]
            },
            "SCITEX-04": {
                "name": "Coding Style",
                "description": "SciTeX-specific coding conventions",
                "rules": [
                    "import scitex as stx",
                    "Use stx.io.load() and stx.io.save()",
                    "Relative paths only",
                    "symlink_from_cwd=True for outputs",
                    "Use stx.plt.subplots() for plotting",
                    "Use ax.set_xyt() for axis labels"
                ]
            },
            "SCITEX-05": {
                "name": "Module Usage",
                "description": "Proper use of SciTeX modules",
                "rules": [
                    "stx.io for all file operations",
                    "stx.plt for matplotlib enhancements",
                    "stx.stats for statistical operations",
                    "stx.dsp for signal processing",
                    "stx.str for string utilities",
                    "stx.gen for system operations"
                ]
            }
        }
        
    def _register_module_tools(self):
        """Register validator-specific tools."""
        
        @self.app.tool()
        async def validate_full_compliance(
            file_or_project: str,
            detailed: bool = True,
            fix_suggestions: bool = True
        ) -> Dict[str, Any]:
            """Comprehensive validation against all SciTeX guidelines."""
            
            path = Path(file_or_project)
            
            if path.is_file():
                return await self._validate_file_compliance(path, detailed, fix_suggestions)
            elif path.is_dir():
                return await self._validate_project_compliance(path, detailed, fix_suggestions)
            else:
                return {"error": f"Path {file_or_project} not found"}
                
        @self.app.tool()
        async def validate_specific_guideline(
            file_or_project: str,
            guideline_id: str,
            auto_fix: bool = False
        ) -> Dict[str, Any]:
            """Validate against specific SciTeX guideline."""
            
            if guideline_id not in self.guidelines:
                return {
                    "error": f"Unknown guideline: {guideline_id}",
                    "available": list(self.guidelines.keys())
                }
                
            path = Path(file_or_project)
            guideline = self.guidelines[guideline_id]
            
            validation = {
                "guideline": guideline_id,
                "name": guideline["name"],
                "compliance": True,
                "score": 100,
                "violations": [],
                "fixes_applied": []
            }
            
            if guideline_id == "SCITEX-01":
                validation.update(self._validate_project_structure(path, auto_fix))
            elif guideline_id == "SCITEX-02":
                validation.update(self._validate_script_template(path, auto_fix))
            elif guideline_id == "SCITEX-03":
                validation.update(self._validate_configuration(path, auto_fix))
            elif guideline_id == "SCITEX-04":
                validation.update(self._validate_coding_style(path, auto_fix))
            elif guideline_id == "SCITEX-05":
                validation.update(self._validate_module_usage(path, auto_fix))
                
            return validation
            
        @self.app.tool()
        async def generate_compliance_report(
            project_path: str = ".",
            output_format: str = "markdown"
        ) -> Dict[str, Any]:
            """Generate comprehensive compliance report."""
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project {project_path} not found"}
                
            # Run full validation
            validation = await self.validate_full_compliance(project_path, detailed=True)
            
            report = {
                "project": str(project.absolute()),
                "timestamp": datetime.now().isoformat(),
                "overall_score": validation.get("overall_score", 0),
                "status": validation.get("status", "unknown"),
                "guidelines": {}
            }
            
            # Detailed guideline results
            for guideline_id, guideline in self.guidelines.items():
                result = await self.validate_specific_guideline(project_path, guideline_id)
                report["guidelines"][guideline_id] = {
                    "name": guideline["name"],
                    "score": result.get("score", 0),
                    "violations": len(result.get("violations", [])),
                    "compliance": result.get("compliance", False)
                }
                
            # Generate formatted report
            if output_format == "markdown":
                report["formatted"] = self._format_markdown_report(report)
            elif output_format == "json":
                report["formatted"] = report
            elif output_format == "html":
                report["formatted"] = self._format_html_report(report)
                
            return report
            
        @self.app.tool()
        async def check_script_template(
            script_path: str,
            template_type: str = "analysis"
        ) -> Dict[str, Any]:
            """Check if script follows SciTeX template structure."""
            
            script = Path(script_path)
            if not script.exists():
                return {"error": f"Script {script_path} not found"}
                
            content = script.read_text()
            
            # Define required elements by template type
            templates = {
                "analysis": {
                    "required_sections": [
                        "#!/usr/bin/env python3",
                        "# -*- coding: utf-8 -*-",
                        "# Timestamp:",
                        "__FILE__ =",
                        "__DIR__ =",
                        '"""Functionalities:',
                        '"""Imports"""',
                        '"""Parameters"""',
                        '"""Functions & Classes"""',
                        "def main(args):",
                        "def run_main():",
                        "stx.gen.start(",
                        "stx.gen.close("
                    ],
                    "required_imports": [
                        "import scitex as stx",
                        "import argparse"
                    ]
                },
                "utility": {
                    "required_sections": [
                        "#!/usr/bin/env python3",
                        "# -*- coding: utf-8 -*-",
                        "__FILE__ =",
                        '"""',
                        "import scitex as stx"
                    ],
                    "required_imports": []
                }
            }
            
            template = templates.get(template_type, templates["analysis"])
            
            validation = {
                "template_type": template_type,
                "compliant": True,
                "score": 100,
                "missing_elements": [],
                "suggestions": []
            }
            
            # Check required sections
            for element in template["required_sections"]:
                if element not in content:
                    validation["missing_elements"].append(element)
                    validation["compliant"] = False
                    validation["score"] -= 100 // len(template["required_sections"])
                    
            # Check imports
            for imp in template["required_imports"]:
                if imp not in content:
                    validation["missing_elements"].append(f"Missing import: {imp}")
                    validation["score"] -= 5
                    
            # Generate suggestions
            if validation["missing_elements"]:
                validation["suggestions"] = self._generate_template_fixes(
                    content, validation["missing_elements"], template_type
                )
                
            validation["score"] = max(0, validation["score"])
            return validation
            
        @self.app.tool()
        async def validate_config_usage(
            script_path: str
        ) -> Dict[str, Any]:
            """Validate proper configuration usage in script."""
            
            script = Path(script_path)
            if not script.exists():
                return {"error": f"Script {script_path} not found"}
                
            content = script.read_text()
            
            validation = {
                "compliant": True,
                "score": 100,
                "issues": [],
                "hardcoded_values": [],
                "suggestions": []
            }
            
            # Check CONFIG loading
            if "CONFIG = stx.io.load_configs()" not in content:
                validation["issues"].append("CONFIG not loaded properly")
                validation["compliant"] = False
                validation["score"] -= 30
                
            # Check for hardcoded paths
            hardcoded_paths = re.findall(r'["\'](/[^"\']+\.[a-zA-Z]+)["\']', content)
            if hardcoded_paths:
                validation["hardcoded_values"].extend([
                    {"type": "path", "value": p} for p in hardcoded_paths
                ])
                validation["issues"].append(f"Found {len(hardcoded_paths)} hardcoded paths")
                validation["score"] -= 10 * len(hardcoded_paths)
                
            # Check for hardcoded numeric parameters
            # Skip common safe values like 0, 1, 2
            numeric_pattern = r'\b(?<!\.)\d{3,}(?!\.)|\b\d+\.\d+\b'
            hardcoded_numbers = re.findall(numeric_pattern, content)
            
            # Filter out line numbers, years, etc.
            suspicious_numbers = [
                n for n in hardcoded_numbers 
                if float(n) not in [0, 1, 2] and not (1900 <= float(n) <= 2100)
            ]
            
            if suspicious_numbers:
                validation["hardcoded_values"].extend([
                    {"type": "parameter", "value": n} for n in suspicious_numbers[:5]
                ])
                validation["issues"].append(f"Found {len(suspicious_numbers)} hardcoded parameters")
                validation["score"] -= 5 * len(suspicious_numbers)
                
            # Generate suggestions
            if validation["hardcoded_values"]:
                validation["suggestions"] = self._generate_config_suggestions(
                    validation["hardcoded_values"]
                )
                
            validation["score"] = max(0, validation["score"])
            return validation
            
        @self.app.tool()
        async def validate_module_patterns(
            code: str,
            module: str = "all"
        ) -> Dict[str, Any]:
            """Validate proper use of SciTeX module patterns."""
            
            validation = {
                "module": module,
                "compliant": True,
                "score": 100,
                "anti_patterns": [],
                "suggestions": []
            }
            
            # Define anti-patterns by module
            anti_patterns = {
                "io": [
                    (r'pd\.read_csv\(', "Use stx.io.load() instead of pd.read_csv()"),
                    (r'\.to_csv\(', "Use stx.io.save() instead of to_csv()"),
                    (r'open\([^)]+\)\.read\(\)', "Use stx.io.load() instead of open().read()"),
                    (r'plt\.savefig\(', "Use stx.io.save(fig, ...) instead of plt.savefig()"),
                    (r'["\']/[\w/]+', "Use relative paths instead of absolute paths")
                ],
                "plt": [
                    (r'plt\.subplots\(', "Use stx.plt.subplots() instead of plt.subplots()"),
                    (r'ax\.set_xlabel\(', "Use ax.set_xyt() instead of separate set_xlabel/ylabel/title"),
                    (r'ax\.set_ylabel\(', "Use ax.set_xyt() instead of separate set_xlabel/ylabel/title"),
                    (r'plt\.show\(\)', "Avoid plt.show() in scripts, save figures instead")
                ],
                "stats": [
                    (r'scipy\.stats\.', "Import and use stx.stats instead of scipy.stats directly"),
                    (r'statsmodels\.', "Use stx.stats wrappers for statsmodels"),
                    (r'print\(.*p[-_]?value', "Use stx.stats.p2stars() for p-value formatting")
                ]
            }
            
            # Check patterns
            patterns_to_check = anti_patterns.get(module, [])
            if module == "all":
                patterns_to_check = sum(anti_patterns.values(), [])
                
            for pattern, message in patterns_to_check:
                matches = re.findall(pattern, code, re.IGNORECASE)
                if matches:
                    validation["anti_patterns"].append({
                        "pattern": pattern,
                        "message": message,
                        "occurrences": len(matches),
                        "examples": matches[:3]
                    })
                    validation["score"] -= 10
                    validation["compliant"] = False
                    
            # Generate fix suggestions
            if validation["anti_patterns"]:
                validation["suggestions"] = self._generate_pattern_fixes(
                    validation["anti_patterns"]
                )
                
            validation["score"] = max(0, validation["score"])
            return validation
            
    async def _validate_file_compliance(
        self,
        file_path: Path,
        detailed: bool,
        fix_suggestions: bool
    ) -> Dict[str, Any]:
        """Validate single file compliance."""
        
        if not file_path.suffix == '.py':
            return {"error": "Only Python files can be validated"}
            
        content = file_path.read_text()
        
        validation = {
            "file": str(file_path),
            "overall_compliance": True,
            "overall_score": 100,
            "guidelines": {}
        }
        
        # Check each applicable guideline
        guidelines_to_check = ["SCITEX-02", "SCITEX-03", "SCITEX-04", "SCITEX-05"]
        
        for guideline_id in guidelines_to_check:
            result = await self.validate_specific_guideline(str(file_path), guideline_id)
            validation["guidelines"][guideline_id] = result
            
            if not result.get("compliance", True):
                validation["overall_compliance"] = False
                
            score_impact = result.get("score", 100)
            validation["overall_score"] = min(validation["overall_score"], score_impact)
            
        # Add fix suggestions if requested
        if fix_suggestions and not validation["overall_compliance"]:
            validation["fix_suggestions"] = self._generate_file_fixes(validation)
            
        return validation
        
    async def _validate_project_compliance(
        self,
        project_path: Path,
        detailed: bool,
        fix_suggestions: bool
    ) -> Dict[str, Any]:
        """Validate entire project compliance."""
        
        validation = {
            "project": str(project_path),
            "overall_compliance": True,
            "overall_score": 100,
            "status": "compliant",
            "summary": {},
            "files_checked": 0,
            "non_compliant_files": []
        }
        
        # Validate project structure (SCITEX-01)
        structure_result = await self.validate_specific_guideline(
            str(project_path), "SCITEX-01"
        )
        validation["summary"]["structure"] = structure_result
        
        if not structure_result.get("compliance", True):
            validation["overall_compliance"] = False
            validation["overall_score"] = min(
                validation["overall_score"],
                structure_result.get("score", 0)
            )
            
        # Validate configuration (SCITEX-03)
        config_result = await self.validate_specific_guideline(
            str(project_path), "SCITEX-03"
        )
        validation["summary"]["configuration"] = config_result
        
        # Validate Python files
        scripts_dir = project_path / "scripts"
        if scripts_dir.exists():
            py_files = list(scripts_dir.rglob("*.py"))
            validation["files_checked"] = len(py_files)
            
            # Sample files for detailed check (limit to 10)
            for py_file in py_files[:10]:
                file_result = await self._validate_file_compliance(
                    py_file, detailed=False, fix_suggestions=False
                )
                
                if not file_result.get("overall_compliance", True):
                    validation["non_compliant_files"].append({
                        "file": str(py_file.relative_to(project_path)),
                        "score": file_result.get("overall_score", 0),
                        "main_issues": self._summarize_issues(file_result)
                    })
                    
        # Calculate overall status
        if validation["overall_score"] >= 90:
            validation["status"] = "excellent"
        elif validation["overall_score"] >= 70:
            validation["status"] = "good"
        elif validation["overall_score"] >= 50:
            validation["status"] = "needs_improvement"
        else:
            validation["status"] = "non_compliant"
            
        # Add recommendations
        if fix_suggestions:
            validation["recommendations"] = self._generate_project_recommendations(validation)
            
        return validation
        
    def _validate_project_structure(self, path: Path, auto_fix: bool) -> Dict[str, Any]:
        """Validate SCITEX-01: Project Structure."""
        
        result = {
            "compliance": True,
            "score": 100,
            "violations": [],
            "fixes_applied": []
        }
        
        if path.is_file():
            # For files, check they're not in root
            if path.parent == path.parent.parent:  # Simplified root check
                result["violations"].append("Python file in project root")
                result["compliance"] = False
                result["score"] -= 50
            return result
            
        # For directories
        # Check required directories
        required_dirs = ["config", "scripts", "data"]
        for dir_name in required_dirs:
            if not (path / dir_name).exists():
                result["violations"].append(f"Missing required directory: {dir_name}")
                result["compliance"] = False
                result["score"] -= 20
                
                if auto_fix:
                    (path / dir_name).mkdir(parents=True, exist_ok=True)
                    result["fixes_applied"].append(f"Created {dir_name}/")
                    
        # Check for root Python files
        root_py_files = list(path.glob("*.py"))
        allowed = ["setup.py", "conftest.py"]
        violations = [f for f in root_py_files if f.name not in allowed]
        
        if violations:
            result["violations"].append(
                f"Python files in root: {[f.name for f in violations]}"
            )
            result["compliance"] = False
            result["score"] -= 30
            
        result["score"] = max(0, result["score"])
        return result
        
    def _validate_script_template(self, path: Path, auto_fix: bool) -> Dict[str, Any]:
        """Validate SCITEX-02: Script Template."""
        
        result = {
            "compliance": True,
            "score": 100,
            "violations": [],
            "fixes_applied": []
        }
        
        if path.is_dir():
            # For directories, skip
            return result
            
        content = path.read_text()
        
        # Required elements
        required = [
            ("#!/usr/bin/env python3", "Missing shebang"),
            ("# -*- coding: utf-8 -*-", "Missing encoding"),
            ("# Timestamp:", "Missing timestamp header"),
            ("__FILE__ =", "Missing __FILE__ definition"),
            ("__DIR__ =", "Missing __DIR__ definition"),
            ('"""', "Missing docstring"),
            ("import scitex as stx", "Missing scitex import"),
            ("def main(", "Missing main() function"),
            ("def run_main(", "Missing run_main() function"),
            ("stx.gen.start(", "Missing stx.gen.start()"),
            ("stx.gen.close(", "Missing stx.gen.close()")
        ]
        
        for element, message in required:
            if element not in content:
                result["violations"].append(message)
                result["compliance"] = False
                result["score"] -= 10
                
        result["score"] = max(0, result["score"])
        return result
        
    def _validate_configuration(self, path: Path, auto_fix: bool) -> Dict[str, Any]:
        """Validate SCITEX-03: Configuration System."""
        
        result = {
            "compliance": True,
            "score": 100,
            "violations": [],
            "fixes_applied": []
        }
        
        if path.is_file():
            content = path.read_text()
            
            # Check CONFIG loading
            if "CONFIG = stx.io.load_configs()" not in content:
                result["violations"].append("CONFIG not loaded with stx.io.load_configs()")
                result["compliance"] = False
                result["score"] -= 30
                
            # Check for hardcoded paths
            hardcoded = re.findall(r'["\'](/[^"\']+)["\']', content)
            if hardcoded:
                result["violations"].append(f"Hardcoded paths: {hardcoded[:3]}")
                result["compliance"] = False
                result["score"] -= 20
                
        else:
            # For project directory
            config_dir = path / "config"
            if not config_dir.exists():
                result["violations"].append("Missing config directory")
                result["compliance"] = False
                result["score"] = 0
                return result
                
            # Check required config files
            required_configs = ["PATH.yaml", "PARAMS.yaml", "IS_DEBUG.yaml"]
            for config in required_configs:
                if not (config_dir / config).exists():
                    result["violations"].append(f"Missing {config}")
                    result["compliance"] = False
                    result["score"] -= 25
                    
        result["score"] = max(0, result["score"])
        return result
        
    def _validate_coding_style(self, path: Path, auto_fix: bool) -> Dict[str, Any]:
        """Validate SCITEX-04: Coding Style."""
        
        result = {
            "compliance": True,
            "score": 100,
            "violations": [],
            "fixes_applied": []
        }
        
        if path.is_dir():
            return result
            
        content = path.read_text()
        
        # Check for anti-patterns
        anti_patterns = [
            (r'pd\.read_csv\(', "Using pd.read_csv instead of stx.io.load"),
            (r'\.to_csv\(', "Using to_csv instead of stx.io.save"),
            (r'plt\.savefig\(', "Using plt.savefig instead of stx.io.save"),
            (r'plt\.subplots\(', "Using plt.subplots instead of stx.plt.subplots"),
            (r'ax\.set_xlabel\(', "Using separate axis labels instead of ax.set_xyt")
        ]
        
        for pattern, message in anti_patterns:
            if re.search(pattern, content):
                result["violations"].append(message)
                result["compliance"] = False
                result["score"] -= 10
                
        result["score"] = max(0, result["score"])
        return result
        
    def _validate_module_usage(self, path: Path, auto_fix: bool) -> Dict[str, Any]:
        """Validate SCITEX-05: Module Usage."""
        
        result = {
            "compliance": True,
            "score": 100,
            "violations": [],
            "fixes_applied": []
        }
        
        if path.is_dir():
            return result
            
        content = path.read_text()
        
        # Check if using scitex modules properly
        if "import scitex" not in content and "from scitex" not in content:
            result["violations"].append("Not importing scitex")
            result["compliance"] = False
            result["score"] -= 50
            
        # Check for direct usage of libraries that should use scitex wrappers
        unwrapped = [
            (r'from scipy import stats', "Use stx.stats instead of scipy.stats directly"),
            (r'import matplotlib\.pyplot as plt\n', "Should also import stx.plt"),
            (r'from pathlib import Path', "Consider using stx.io for path operations")
        ]
        
        for pattern, message in unwrapped:
            if re.search(pattern, content):
                result["violations"].append(message)
                result["score"] -= 10
                
        result["score"] = max(0, result["score"])
        return result
        
    def _generate_template_fixes(
        self,
        content: str,
        missing_elements: List[str],
        template_type: str
    ) -> List[str]:
        """Generate suggestions for fixing template issues."""
        
        suggestions = []
        
        if "#!/usr/bin/env python3" in missing_elements:
            suggestions.append("Add shebang at the very beginning of the file")
            
        if "Missing scitex import" in missing_elements:
            suggestions.append("Add 'import scitex as stx' to imports section")
            
        if "Missing main() function" in missing_elements:
            suggestions.append("Add main(args) function to process data")
            
        if "Missing run_main() function" in missing_elements:
            suggestions.append("Add run_main() function with stx.gen.start/close")
            
        return suggestions
        
    def _generate_config_suggestions(
        self,
        hardcoded_values: List[Dict[str, str]]
    ) -> List[str]:
        """Generate suggestions for configuration issues."""
        
        suggestions = []
        
        paths = [v for v in hardcoded_values if v["type"] == "path"]
        if paths:
            suggestions.append(
                f"Move {len(paths)} hardcoded paths to config/PATH.yaml"
            )
            suggestions.append(
                "Example: Replace '/data/file.csv' with CONFIG.PATH.DATA_FILE"
            )
            
        params = [v for v in hardcoded_values if v["type"] == "parameter"]
        if params:
            suggestions.append(
                f"Move {len(params)} numeric parameters to config/PARAMS.yaml"
            )
            suggestions.append(
                "Example: Replace '0.05' with CONFIG.PARAMS.SIGNIFICANCE_THRESHOLD"
            )
            
        return suggestions
        
    def _generate_pattern_fixes(
        self,
        anti_patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate fixes for anti-pattern issues."""
        
        suggestions = []
        
        for pattern in anti_patterns:
            suggestions.append(f"Fix: {pattern['message']}")
            if pattern["examples"]:
                suggestions.append(f"  Found {pattern['occurrences']} occurrences")
                
        return suggestions
        
    def _summarize_issues(self, file_result: Dict[str, Any]) -> List[str]:
        """Summarize main issues from file validation."""
        
        issues = []
        
        for guideline_id, result in file_result.get("guidelines", {}).items():
            if not result.get("compliance", True):
                violations = result.get("violations", [])
                if violations:
                    issues.append(f"{guideline_id}: {violations[0]}")
                    
        return issues[:3]  # Top 3 issues
        
    def _generate_file_fixes(self, validation: Dict[str, Any]) -> List[str]:
        """Generate fix suggestions for file issues."""
        
        fixes = []
        
        for guideline_id, result in validation.get("guidelines", {}).items():
            if not result.get("compliance", True):
                guideline_name = self.guidelines[guideline_id]["name"]
                fixes.append(f"\n{guideline_id} - {guideline_name}:")
                
                violations = result.get("violations", [])
                for v in violations[:3]:
                    fixes.append(f"  - {v}")
                    
        return fixes
        
    def _generate_project_recommendations(
        self,
        validation: Dict[str, Any]
    ) -> List[str]:
        """Generate project-level recommendations."""
        
        recommendations = []
        
        score = validation.get("overall_score", 100)
        
        if score < 50:
            recommendations.append(
                "CRITICAL: Run 'fix_project_structure' from orchestrator to fix major issues"
            )
            
        if validation.get("non_compliant_files"):
            count = len(validation["non_compliant_files"])
            recommendations.append(
                f"Convert {count} non-compliant files using translation tools"
            )
            
        structure = validation.get("summary", {}).get("structure", {})
        if not structure.get("compliance", True):
            recommendations.append(
                "Fix project structure issues (missing directories, root files)"
            )
            
        config = validation.get("summary", {}).get("configuration", {})
        if not config.get("compliance", True):
            recommendations.append(
                "Create missing configuration files with 'generate_all_config_files'"
            )
            
        if score >= 90:
            recommendations.append(
                "Excellent compliance! Consider adding more tests and documentation"
            )
            
        return recommendations
        
    def _format_markdown_report(self, report: Dict[str, Any]) -> str:
        """Format report as markdown."""
        
        md = f"""# SciTeX Compliance Report

**Project**: {report['project']}  
**Generated**: {report['timestamp']}  
**Overall Score**: {report['overall_score']}/100  
**Status**: {report['status'].upper()}

## Guideline Compliance

| Guideline | Name | Score | Violations | Status |
|-----------|------|-------|------------|--------|
"""
        
        for gid, result in report["guidelines"].items():
            status = "✅" if result["compliance"] else "❌"
            md += f"| {gid} | {result['name']} | {result['score']} | {result['violations']} | {status} |\n"
            
        md += "\n## Recommendations\n\n"
        
        if report["overall_score"] < 90:
            md += "1. Run full validation with fix suggestions\n"
            md += "2. Use translation tools to convert non-compliant code\n"
            md += "3. Review and apply SciTeX guidelines\n"
        else:
            md += "Project has excellent compliance! Keep up the good work.\n"
            
        return md
        
    def _format_html_report(self, report: Dict[str, Any]) -> str:
        """Format report as HTML."""
        
        status_color = {
            "excellent": "green",
            "good": "blue",
            "needs_improvement": "orange",
            "non_compliant": "red"
        }.get(report["status"], "gray")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SciTeX Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; }}
        .score {{ font-size: 48px; color: {status_color}; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f0f0f0; }}
        .compliant {{ color: green; }}
        .non-compliant {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SciTeX Compliance Report</h1>
        <p>Project: {report['project']}</p>
        <p>Generated: {report['timestamp']}</p>
        <div class="score">{report['overall_score']}/100</div>
        <p>Status: <strong>{report['status'].upper()}</strong></p>
    </div>
    
    <h2>Guideline Compliance</h2>
    <table>
        <tr>
            <th>Guideline</th>
            <th>Name</th>
            <th>Score</th>
            <th>Violations</th>
            <th>Status</th>
        </tr>"""
        
        for gid, result in report["guidelines"].items():
            status_class = "compliant" if result["compliance"] else "non-compliant"
            status_icon = "✅" if result["compliance"] else "❌"
            html += f"""
        <tr>
            <td>{gid}</td>
            <td>{result['name']}</td>
            <td>{result['score']}</td>
            <td>{result['violations']}</td>
            <td class="{status_class}">{status_icon}</td>
        </tr>"""
            
        html += """
    </table>
</body>
</html>"""
        
        return html
        
    def get_module_description(self) -> str:
        """Get description of validator functionality."""
        return (
            "SciTeX validator provides comprehensive compliance checking against all "
            "SciTeX guidelines. It validates project structure, script templates, "
            "configuration usage, coding style, and module patterns. Generates detailed "
            "reports and fix suggestions."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "validate_full_compliance",
            "validate_specific_guideline",
            "generate_compliance_report",
            "check_script_template",
            "validate_config_usage",
            "validate_module_patterns",
            "get_module_info",
            "validate_code"
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate code against all guidelines."""
        # This is meta-validation, so we run our own validation
        return await self.validate_module_patterns(code, "all")


# Main entry point
if __name__ == "__main__":
    server = ScitexValidatorMCPServer()
    asyncio.run(server.run())

# EOF