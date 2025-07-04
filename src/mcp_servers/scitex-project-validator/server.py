#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 11:15:00 (ywatanabe)"
# File: ./mcp_servers/scitex-project-validator/server.py
# ----------------------------------------

"""MCP server for validating SciTeX-based scientific project structures."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import base server from the adjacent directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scitex-base'))
from base_server import ScitexBaseMCPServer


class ScitexProjectValidatorServer(ScitexBaseMCPServer):
    """MCP server for validating individual scientific projects using SciTeX."""
    
    def __init__(self):
        super().__init__("project-validator", "1.0.0")
        
    def _register_module_tools(self):
        """Register project validation tools."""
        
        @self.app.tool()
        async def check_scitex_project_structure_for_scientific_project(project_path: str) -> Dict[str, Any]:
            """
            Validate SciTeX project structure for individual scientific projects.
            
            Args:
                project_path: Path to the scientific project to validate
            """
            
            project_path = Path(project_path).expanduser().resolve()
            
            if not project_path.exists():
                return {
                    "status": "error",
                    "message": f"Project path does not exist: {project_path}"
                }
                
            issues = []
            suggestions = []
            structure_score = 0
            max_score = 10
            
            # Check mandatory directory structure
            required_dirs = ["config", "data", "scripts", "examples", "tests", ".playground"]
            existing_dirs = [d.name for d in project_path.iterdir() if d.is_dir()]
            
            for req_dir in required_dirs:
                if req_dir in existing_dirs:
                    structure_score += 1
                    if req_dir == "scripts":
                        # Check scripts have proper SciTeX structure
                        script_issues = self._validate_scripts_directory(project_path / "scripts")
                        issues.extend(script_issues)
                else:
                    issues.append(f"❌ Missing required directory: {req_dir}/")
                    suggestions.append(f"Create directory: mkdir {req_dir}")
                    
            # Check for forbidden root directories
            forbidden_in_root = [d for d in existing_dirs if d not in required_dirs and not d.startswith('.')]
            if forbidden_in_root:
                issues.append(f"❌ Forbidden directories in project root: {forbidden_in_root}")
                suggestions.append("Move directories under config/, data/, scripts/, examples/, tests/, or .playground/")
                
            # Check config directory structure
            config_dir = project_path / "config"
            if config_dir.exists():
                if not (config_dir / "PATH.yaml").exists():
                    issues.append("❌ Missing required config/PATH.yaml file")
                    suggestions.append("Create config/PATH.yaml for path management")
                else:
                    structure_score += 1
                    
            # Check data directory with symlinks
            data_dir = project_path / "data"
            if data_dir.exists():
                symlink_count = sum(1 for item in data_dir.rglob('*') if item.is_symlink())
                if symlink_count == 0:
                    issues.append("⚠️ No symlinks found in data/ directory")
                    suggestions.append("Use symlinks from scripts/<script>_out/ to organize data")
                else:
                    structure_score += 1
                    
            # Check for proper script outputs
            scripts_dir = project_path / "scripts"
            if scripts_dir.exists():
                script_out_dirs = list(scripts_dir.rglob("*_out"))
                if script_out_dirs:
                    structure_score += 1
                    
                    # Check for log management
                    has_proper_logs = False
                    for out_dir in script_out_dirs:
                        logs_dir = out_dir / "logs"
                        if logs_dir.exists():
                            log_files = ["RUNNING", "FINISHED_SUCCESS", "FINISHED_FAILURE"]
                            if any((logs_dir / lf).exists() for lf in log_files):
                                has_proper_logs = True
                                break
                                
                    if has_proper_logs:
                        structure_score += 1
                    else:
                        issues.append("⚠️ No proper SciTeX log management found")
                        suggestions.append("Ensure scripts use stx.gen.start() and stx.gen.close()")
                        
            return {
                "status": "success",
                "project_path": str(project_path),
                "structure_score": f"{structure_score}/{max_score}",
                "compliance_level": self._get_compliance_level(structure_score, max_score),
                "issues": issues,
                "suggestions": suggestions,
                "directory_structure": self._analyze_directory_structure(project_path),
                "scitex_usage": self._analyze_scitex_usage(project_path),
                "next_steps": self._suggest_next_steps(structure_score, max_score, issues)
            }
            
        @self.app.tool()
        async def check_scitex_project_structure_for_pip_package(package_path: str) -> Dict[str, Any]:
            """
            Validate SciTeX project structure for pip package development.
            
            Args:
                package_path: Path to the pip package project to validate
            """
            
            package_path = Path(package_path).expanduser().resolve()
            
            if not package_path.exists():
                return {
                    "status": "error",
                    "message": f"Package path does not exist: {package_path}"
                }
                
            issues = []
            suggestions = []
            structure_score = 0
            max_score = 12
            
            # Check for modern Python package structure
            if (package_path / "src").exists():
                structure_score += 2
            elif (package_path / "setup.py").exists() or (package_path / "pyproject.toml").exists():
                structure_score += 1
                suggestions.append("Consider migrating to src-layout for better practices")
            else:
                issues.append("❌ No clear package structure found (no src/, setup.py, or pyproject.toml)")
                
            # Check configuration files
            config_files = ["setup.cfg", "pyproject.toml", "setup.py"]
            has_config = any((package_path / cf).exists() for cf in config_files)
            if has_config:
                structure_score += 1
            else:
                issues.append("❌ Missing package configuration (setup.cfg/pyproject.toml/setup.py)")
                suggestions.append("Create setup.cfg or pyproject.toml for package configuration")
                
            # Check testing infrastructure
            test_dirs = ["tests", "test"]
            has_tests = any((package_path / td).exists() for td in test_dirs)
            if has_tests:
                structure_score += 1
                
                # Check for pytest configuration
                pytest_configs = ["pytest.ini", "setup.cfg", "pyproject.toml"]
                has_pytest_config = any(self._has_pytest_config(package_path / pc) for pc in pytest_configs if (package_path / pc).exists())
                if has_pytest_config:
                    structure_score += 1
                else:
                    suggestions.append("Add pytest configuration for better testing")
            else:
                issues.append("❌ Missing tests directory")
                suggestions.append("Create tests/ directory with comprehensive test suite")
                
            # Check documentation
            docs_indicators = ["docs", "README.md", "README.rst"]
            has_docs = any((package_path / di).exists() for di in docs_indicators)
            if has_docs:
                structure_score += 1
            else:
                issues.append("❌ Missing documentation (docs/ or README)")
                suggestions.append("Add README.md and consider docs/ directory for comprehensive documentation")
                
            # Check for CI/CD
            ci_indicators = [".github/workflows", ".gitlab-ci.yml", "tox.ini"]
            has_ci = any((package_path / ci).exists() for ci in ci_indicators)
            if has_ci:
                structure_score += 1
            else:
                suggestions.append("Consider adding CI/CD with GitHub Actions or similar")
                
            # Check examples directory (required for SciTeX packages)
            if (package_path / "examples").exists():
                structure_score += 2
                
                # Check if examples use SciTeX format
                examples_validation = self._validate_examples_directory(package_path / "examples")
                if examples_validation["uses_scitex"]:
                    structure_score += 1
                else:
                    issues.append("⚠️ Examples directory exists but doesn't use SciTeX format")
                    suggestions.append("Convert examples to use SciTeX format as specified in guidelines")
            else:
                issues.append("❌ Missing examples/ directory")
                suggestions.append("Create examples/ directory with SciTeX-formatted example scripts")
                
            # Check for proper dependency management
            dep_files = ["requirements.txt", "setup.cfg", "pyproject.toml"]
            has_dep_management = any((package_path / df).exists() for df in dep_files)
            if has_dep_management:
                structure_score += 1
            else:
                issues.append("❌ Missing dependency management")
                suggestions.append("Define dependencies in setup.cfg or pyproject.toml")
                
            # Check code quality tools
            quality_files = [".pre-commit-config.yaml", "tox.ini", ".flake8", "mypy.ini"]
            quality_score = sum(1 for qf in quality_files if (package_path / qf).exists())
            if quality_score >= 2:
                structure_score += 1
            else:
                suggestions.append("Add code quality tools (.pre-commit-config.yaml, flake8, mypy)")
                
            return {
                "status": "success",
                "package_path": str(package_path),
                "structure_score": f"{structure_score}/{max_score}",
                "compliance_level": self._get_compliance_level(structure_score, max_score),
                "package_type": self._detect_package_type(package_path),
                "issues": issues,
                "suggestions": suggestions,
                "directory_structure": self._analyze_directory_structure(package_path),
                "scitex_integration": self._analyze_scitex_integration_for_package(package_path),
                "next_steps": self._suggest_package_next_steps(structure_score, max_score, issues)
            }
            
    def _validate_scripts_directory(self, scripts_dir: Path) -> List[str]:
        """Validate scripts directory for SciTeX compliance."""
        issues = []
        
        if not scripts_dir.exists():
            return ["❌ Scripts directory does not exist"]
            
        python_files = list(scripts_dir.rglob("*.py"))
        
        if not python_files:
            issues.append("⚠️ No Python files found in scripts directory")
            return issues
            
        non_compliant_files = []
        for py_file in python_files:
            if not self._is_scitex_compliant_script(py_file):
                non_compliant_files.append(py_file.relative_to(scripts_dir))
                
        if non_compliant_files:
            issues.append(f"❌ Non-SciTeX compliant scripts: {non_compliant_files[:3]}{'...' if len(non_compliant_files) > 3 else ''}")
            
        return issues
        
    def _is_scitex_compliant_script(self, script_path: Path) -> bool:
        """Check if a script follows SciTeX template."""
        try:
            content = script_path.read_text()
            
            # Check for required elements
            required_patterns = [
                r"import scitex as stx",
                r"def main\(args\)",
                r"def parse_args\(\)",
                r"def run_main\(\)",
                r"stx\.gen\.start\(",
                r"stx\.gen\.close\("
            ]
            
            return all(re.search(pattern, content) for pattern in required_patterns)
            
        except Exception:
            return False
            
    def _validate_examples_directory(self, examples_dir: Path) -> Dict[str, Any]:
        """Validate examples directory for SciTeX compliance."""
        
        if not examples_dir.exists():
            return {"uses_scitex": False, "file_count": 0}
            
        python_files = list(examples_dir.rglob("*.py"))
        scitex_compliant = sum(1 for f in python_files if self._is_scitex_compliant_script(f))
        
        return {
            "uses_scitex": scitex_compliant > 0,
            "file_count": len(python_files),
            "scitex_compliant_count": scitex_compliant,
            "compliance_ratio": scitex_compliant / len(python_files) if python_files else 0
        }
        
    def _has_pytest_config(self, config_file: Path) -> bool:
        """Check if file contains pytest configuration."""
        try:
            content = config_file.read_text()
            return "pytest" in content.lower() or "[tool.pytest" in content.lower()
        except Exception:
            return False
            
    def _analyze_directory_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project directory structure."""
        
        structure = {}
        for item in project_path.iterdir():
            if item.is_dir():
                file_count = len(list(item.rglob("*"))) if item.exists() else 0
                structure[item.name] = {
                    "type": "directory",
                    "file_count": file_count
                }
            else:
                structure[item.name] = {"type": "file"}
                
        return structure
        
    def _analyze_scitex_usage(self, project_path: Path) -> Dict[str, Any]:
        """Analyze SciTeX usage in the project."""
        
        python_files = list(project_path.rglob("*.py"))
        scitex_files = []
        
        for py_file in python_files:
            try:
                content = py_file.read_text()
                if "import scitex" in content or "from scitex" in content:
                    scitex_files.append(str(py_file.relative_to(project_path)))
            except Exception:
                continue
                
        return {
            "total_python_files": len(python_files),
            "scitex_using_files": len(scitex_files),
            "scitex_usage_ratio": len(scitex_files) / len(python_files) if python_files else 0,
            "scitex_files": scitex_files[:5]  # Show first 5
        }
        
    def _analyze_scitex_integration_for_package(self, package_path: Path) -> Dict[str, Any]:
        """Analyze SciTeX integration for pip packages."""
        
        # Check if scitex is in dependencies
        dep_files = ["setup.cfg", "pyproject.toml", "requirements.txt"]
        has_scitex_dep = False
        
        for dep_file in dep_files:
            file_path = package_path / dep_file
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    if "scitex" in content.lower():
                        has_scitex_dep = True
                        break
                except Exception:
                    continue
                    
        examples_analysis = self._validate_examples_directory(package_path / "examples")
        
        return {
            "has_scitex_dependency": has_scitex_dep,
            "examples_use_scitex": examples_analysis["uses_scitex"],
            "integration_level": "full" if has_scitex_dep and examples_analysis["uses_scitex"] else 
                               "partial" if has_scitex_dep or examples_analysis["uses_scitex"] else "none"
        }
        
    def _detect_package_type(self, package_path: Path) -> str:
        """Detect the type of package structure."""
        
        if (package_path / "src").exists():
            return "src-layout"
        elif (package_path / "setup.py").exists():
            return "flat-layout"
        elif (package_path / "pyproject.toml").exists():
            return "modern-pyproject"
        else:
            return "unknown"
            
    def _get_compliance_level(self, score: int, max_score: int) -> str:
        """Get compliance level based on score."""
        ratio = score / max_score
        
        if ratio >= 0.9:
            return "excellent"
        elif ratio >= 0.7:
            return "good"
        elif ratio >= 0.5:
            return "fair"
        else:
            return "needs_improvement"
            
    def _suggest_next_steps(self, score: int, max_score: int, issues: List[str]) -> List[str]:
        """Suggest next steps for scientific projects."""
        
        steps = []
        ratio = score / max_score
        
        if ratio < 0.3:
            steps.append("🚨 Start with basic directory structure: mkdir config data scripts examples tests .playground")
            steps.append("📋 Create config/PATH.yaml for path management")
            steps.append("📝 Convert first script to SciTeX format using the template")
        elif ratio < 0.7:
            steps.append("📜 Convert remaining scripts to SciTeX format")
            steps.append("🔗 Set up data symlinks from script outputs")
            steps.append("🧪 Add comprehensive tests")
        else:
            steps.append("✨ Fine-tune configuration and add advanced features")
            steps.append("📚 Expand examples and documentation")
            
        if len(issues) > 5:
            steps.append("🔧 Focus on fixing critical issues first")
            
        return steps
        
    def _suggest_package_next_steps(self, score: int, max_score: int, issues: List[str]) -> List[str]:
        """Suggest next steps for pip packages."""
        
        steps = []
        ratio = score / max_score
        
        if ratio < 0.4:
            steps.append("📦 Set up basic package structure with setup.cfg or pyproject.toml")
            steps.append("🧪 Create comprehensive test suite")
            steps.append("📖 Add README.md with installation and usage instructions")
        elif ratio < 0.7:
            steps.append("📋 Add examples/ directory with SciTeX-formatted examples")
            steps.append("🔧 Set up code quality tools (.pre-commit-config.yaml)")
            steps.append("🚀 Add CI/CD pipeline")
        else:
            steps.append("📚 Enhance documentation with docs/ directory")
            steps.append("🏷️ Prepare for PyPI publication")
            
        return steps
        
    def get_module_description(self) -> str:
        """Get description of project validator server."""
        return (
            "Validates SciTeX project structures for both individual scientific projects "
            "and pip packages. Checks compliance with SciTeX guidelines, directory structure, "
            "and provides detailed suggestions for improvement."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available validation tools."""
        return [
            "check_scitex_project_structure_for_scientific_project",
            "check_scitex_project_structure_for_pip_package"
        ]


async def main():
    """Simple CLI interface for testing."""
    if len(sys.argv) < 3:
        print("Usage: python server.py <check-scientific|check-package> <project_path>")
        print("  check-scientific: Validate scientific project structure")  
        print("  check-package: Validate pip package structure")
        return
        
    server = ScitexProjectValidatorServer()
    command = sys.argv[1]
    project_path = sys.argv[2]
    
    if command == "check-scientific":
        # For CLI testing, call the tool function directly
        tool_func = None
        for tool in server.app.tools:
            if tool.name == "check_scitex_project_structure_for_scientific_project":
                tool_func = tool.func
                break
        
        if tool_func:
            result = await tool_func(project_path)
        else:
            result = {"status": "error", "message": "Tool not found"}
        print("🔬 Scientific Project Validation Results:")
        print(f"📍 Path: {result.get('project_path', project_path)}")
        print(f"📊 Score: {result.get('structure_score', 'N/A')}")
        print(f"📈 Compliance: {result.get('compliance_level', 'unknown')}")
        
        if result.get('issues'):
            print("\n❌ Issues found:")
            for issue in result['issues']:
                print(f"  • {issue}")
                
        if result.get('suggestions'):
            print("\n💡 Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
                
        if result.get('next_steps'):
            print("\n🚀 Next steps:")
            for step in result['next_steps']:
                print(f"  • {step}")
                
    elif command == "check-package":
        # For CLI testing, call the tool function directly  
        tool_func = None
        for tool in server.app.tools:
            if tool.name == "check_scitex_project_structure_for_pip_package":
                tool_func = tool.func
                break
        
        if tool_func:
            result = await tool_func(project_path)
        else:
            result = {"status": "error", "message": "Tool not found"}
        print("📦 Package Validation Results:")
        print(f"📍 Path: {result.get('package_path', project_path)}")
        print(f"📊 Score: {result.get('structure_score', 'N/A')}")
        print(f"📈 Compliance: {result.get('compliance_level', 'unknown')}")
        print(f"🏗️ Package type: {result.get('package_type', 'unknown')}")
        print(f"🔗 SciTeX integration: {result.get('scitex_integration', {}).get('integration_level', 'unknown')}")
        
        if result.get('issues'):
            print("\n❌ Issues found:")
            for issue in result['issues']:
                print(f"  • {issue}")
                
        if result.get('suggestions'):
            print("\n💡 Suggestions:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
                
        if result.get('next_steps'):
            print("\n🚀 Next steps:")
            for step in result['next_steps']:
                print(f"  • {step}")
    else:
        print("Unknown command. Use 'check-scientific' or 'check-package'")


# Main entry point
if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(main())
    else:
        server = ScitexProjectValidatorServer()
        asyncio.run(server.run())

# EOF