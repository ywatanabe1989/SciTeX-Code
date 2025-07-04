#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 11:25:00 (ywatanabe)"
# File: ./mcp_servers/scitex-project-validator/validator.py
# ----------------------------------------

"""Standalone SciTeX project structure validator."""

import re
import sys
from pathlib import Path
from typing import Dict, Any, List


class ScitexProjectValidator:
    """Validate and generate SciTeX project structures."""
    
    def check_scientific_project(self, project_path: str) -> Dict[str, Any]:
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
        
    def check_pip_package(self, package_path: str) -> Dict[str, Any]:
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
        
    def create_template_scientific_project(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """
        Create a template SciTeX scientific project structure.
        
        Args:
            project_path: Path where to create the project
            project_name: Name of the project
        """
        
        project_path = Path(project_path).expanduser().resolve()
        project_dir = project_path / project_name
        
        if project_dir.exists():
            return {
                "status": "error",
                "message": f"Project directory already exists: {project_dir}"
            }
            
        try:
            # Create directory structure
            directories = [
                "config",
                "data", 
                "scripts",
                "examples",
                "tests",
                ".playground"
            ]
            
            for dir_name in directories:
                (project_dir / dir_name).mkdir(parents=True, exist_ok=True)
                
            # Create subdirectories for organization
            (project_dir / "scripts" / "analysis").mkdir(exist_ok=True)
            (project_dir / "data" / "raw").mkdir(exist_ok=True)
            (project_dir / "data" / "processed").mkdir(exist_ok=True)
            (project_dir / ".playground" / "experiments").mkdir(exist_ok=True)
            
            created_files = []
            
            # Create config/PATH.yaml
            path_config = self._generate_path_config(project_name)
            path_file = project_dir / "config" / "PATH.yaml"
            path_file.write_text(path_config)
            created_files.append(str(path_file.relative_to(project_dir)))
            
            # Create example script
            example_script = self._generate_example_script()
            script_file = project_dir / "scripts" / "analysis" / "example_analysis.py"
            script_file.write_text(example_script)
            created_files.append(str(script_file.relative_to(project_dir)))
            
            # Create README.md
            readme_content = self._generate_scientific_readme(project_name)
            readme_file = project_dir / "README.md"
            readme_file.write_text(readme_content)
            created_files.append(str(readme_file.relative_to(project_dir)))
            
            # Create .gitignore
            gitignore_content = self._generate_gitignore()
            gitignore_file = project_dir / ".gitignore"
            gitignore_file.write_text(gitignore_content)
            created_files.append(str(gitignore_file.relative_to(project_dir)))
            
            return {
                "status": "success",
                "project_path": str(project_dir),
                "project_name": project_name,
                "directories_created": directories,
                "files_created": created_files,
                "next_steps": [
                    "📝 Edit config/PATH.yaml to set your data paths",
                    "🔬 Start adding your analysis scripts in scripts/analysis/",
                    "📊 Place raw data in data/raw/ and create symlinks from script outputs",
                    "🧪 Add tests in tests/ directory",
                    "📚 Create examples in examples/ directory"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to create project: {str(e)}"
            }
            
    def create_template_pip_package(self, package_path: str, package_name: str) -> Dict[str, Any]:
        """
        Create a template SciTeX pip package structure.
        
        Args:
            package_path: Path where to create the package
            package_name: Name of the package
        """
        
        package_path = Path(package_path).expanduser().resolve()
        package_dir = package_path / package_name
        
        if package_dir.exists():
            return {
                "status": "error",
                "message": f"Package directory already exists: {package_dir}"
            }
            
        try:
            # Create src-layout structure
            src_dir = package_dir / "src" / package_name.replace("-", "_")
            src_dir.mkdir(parents=True, exist_ok=True)
            
            # Create other directories
            directories = [
                "tests",
                "examples", 
                "docs",
                ".github/workflows"
            ]
            
            for dir_name in directories:
                (package_dir / dir_name).mkdir(parents=True, exist_ok=True)
                
            created_files = []
            
            # Create package __init__.py
            init_content = self._generate_package_init(package_name)
            init_file = src_dir / "__init__.py"
            init_file.write_text(init_content)
            created_files.append(str(init_file.relative_to(package_dir)))
            
            # Create setup.cfg
            setup_content = self._generate_setup_cfg(package_name)
            setup_file = package_dir / "setup.cfg"
            setup_file.write_text(setup_content)
            created_files.append(str(setup_file.relative_to(package_dir)))
            
            # Create pyproject.toml
            pyproject_content = self._generate_pyproject_toml(package_name)
            pyproject_file = package_dir / "pyproject.toml"
            pyproject_file.write_text(pyproject_content)
            created_files.append(str(pyproject_file.relative_to(package_dir)))
            
            # Create example SciTeX script
            example_script = self._generate_example_script()
            example_file = package_dir / "examples" / "basic_usage.py"
            example_file.write_text(example_script)
            created_files.append(str(example_file.relative_to(package_dir)))
            
            # Create README.md
            readme_content = self._generate_package_readme(package_name)
            readme_file = package_dir / "README.md"
            readme_file.write_text(readme_content)
            created_files.append(str(readme_file.relative_to(package_dir)))
            
            # Create basic test
            test_content = self._generate_basic_test(package_name)
            test_file = package_dir / "tests" / "test_basic.py"
            test_file.write_text(test_content)
            created_files.append(str(test_file.relative_to(package_dir)))
            
            # Create .gitignore
            gitignore_content = self._generate_gitignore()
            gitignore_file = package_dir / ".gitignore"
            gitignore_file.write_text(gitignore_content)
            created_files.append(str(gitignore_file.relative_to(package_dir)))
            
            return {
                "status": "success",
                "package_path": str(package_dir),
                "package_name": package_name,
                "structure": "src-layout",
                "files_created": created_files,
                "next_steps": [
                    "📦 Install in development mode: pip install -e .",
                    "🧪 Run tests: pytest",
                    "📝 Edit setup.cfg with your package details",
                    "📚 Add more examples in examples/ using SciTeX format",
                    "🚀 Set up CI/CD in .github/workflows/"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create package: {str(e)}"
            }
            
    def _generate_path_config(self, project_name: str) -> str:
        """Generate PATH.yaml configuration file."""
        return f"""# Path configuration for {project_name}
# This file defines all paths used in the project

# Data paths
data:
  raw: "./data/raw"
  processed: "./data/processed"
  external: "./data/external"

# Output paths  
outputs:
  figures: "./outputs/figures"
  models: "./outputs/models"
  reports: "./outputs/reports"

# Script-specific paths
scripts:
  analysis: "./scripts/analysis"
  preprocessing: "./scripts/preprocessing"
  visualization: "./scripts/visualization"

# Temporary workspace
playground: "./.playground"

# External data sources (modify as needed)
external_data:
  # dataset1: "/path/to/external/dataset1"
  # dataset2: "/path/to/external/dataset2"
"""

    def _generate_example_script(self) -> str:
        """Generate an example SciTeX-compliant script."""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 11:30:00 (author)"
# File: ./scripts/analysis/example_analysis.py
# ----------------------------------------
import os
__FILE__ = (
    "./scripts/analysis/example_analysis.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic SciTeX workflow
  - Loads configuration and data
  - Performs example analysis
  - Saves results with proper organization

Dependencies:
  - packages:
    - scitex, numpy, matplotlib

Input:
  - Configuration from config/PATH.yaml
  - Data files (to be specified)

Output:
  - Analysis results in script_out/
  - Figures and data files with symlinks
"""

"""Imports"""
import argparse
import scitex as stx
import numpy as np

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()

"""Parameters"""
from stx.io import load_configs
CONFIG = load_configs()

"""Functions & Classes"""
def main(args):
    """Main analysis function."""
    
    # Example: Generate some sample data
    print("🔬 Starting example analysis...")
    
    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.1, len(x))
    
    # Create a simple plot
    fig, ax = stx.plt.subplots(1, 1, figsize=(8, 6))
    ax.plot(x, y, 'b-', label='Noisy sine wave')
    ax.set_xyt('Time', 'Amplitude', 'Example Analysis Results')
    ax.legend()
    
    # Save the figure (automatically creates symlink)
    stx.io.save(fig, './outputs/example_plot.png', symlink_from_cwd=True)
    
    # Save the data
    results = {'x': x, 'y': y, 'mean_y': np.mean(y), 'std_y': np.std(y)}
    stx.io.save(results, './outputs/analysis_results.json', symlink_from_cwd=True)
    
    print(f"✅ Analysis complete. Mean: {results['mean_y']:.3f}, Std: {results['std_y']:.3f}")
    
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Example SciTeX analysis script")
    parser.add_argument(
        "--noise-level",
        "-n",
        type=float,
        default=0.1,
        help="Noise level for generated data (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
'''

    def _generate_scientific_readme(self, project_name: str) -> str:
        """Generate README for scientific project."""
        return f"""# {project_name}

A SciTeX-based scientific computing project.

## Project Structure

```
{project_name}/
├── config/                 # Configuration files
│   └── PATH.yaml          # Path definitions
├── data/                  # Centralized data storage  
│   ├── raw/              # Raw input data
│   └── processed/        # Processed data (symlinked from scripts)
├── scripts/               # Analysis scripts
│   └── analysis/         # Analysis scripts
│       └── example_analysis.py
├── examples/              # Usage examples
├── tests/                 # Test files
└── .playground/           # Temporary workspace
    └── experiments/
```

## Getting Started

1. **Install SciTeX**: 
   ```bash
   pip install -e /path/to/scitex-repo
   ```

2. **Configure paths**:
   Edit `config/PATH.yaml` to specify your data locations.

3. **Run example analysis**:
   ```bash
   cd scripts/analysis
   python example_analysis.py
   ```

4. **View results**:
   - Check `scripts/analysis/example_analysis_out/` for outputs
   - Data files are symlinked in `data/` for easy access

## SciTeX Features Used

- **Unified I/O**: `stx.io.load()` and `stx.io.save()` for all file operations
- **Enhanced plotting**: `stx.plt.subplots()` with automatic data export
- **Configuration management**: YAML-based configuration loading
- **Automatic logging**: Script execution tracking and status management
- **Data organization**: Symlinked outputs for centralized data access

## Development Guidelines

- All scripts in `scripts/` must follow SciTeX format
- Use relative paths starting with `./`
- Leverage `stx.io.save()` with `symlink_from_cwd=True` for outputs
- Organize work by categories within each directory
- Use `.playground/` for temporary experiments

## Requirements

- Python 3.8+
- SciTeX package (installed in development mode)
- NumPy, Matplotlib (handled by SciTeX dependencies)

For more information about SciTeX conventions, see the [SciTeX guidelines](docs/to_claude/guidelines/python/).
"""

    def _generate_package_readme(self, package_name: str) -> str:
        """Generate README for pip package."""
        return f"""# {package_name}

A Python package built with SciTeX integration for scientific computing.

## Installation

### Development Installation
```bash
git clone <repository-url>
cd {package_name}
pip install -e .
```

### From PyPI (when published)
```bash
pip install {package_name}
```

## Quick Start

```python
import {package_name.replace('-', '_')} as pkg

# Your package usage here
```

See `examples/basic_usage.py` for a complete SciTeX-formatted example.

## Features

- 🔬 Scientific computing integration with SciTeX
- 📊 Built-in visualization and data handling
- 🧪 Comprehensive testing with pytest
- 📚 Complete documentation and examples
- 🚀 CI/CD ready with GitHub Actions

## Package Structure

```
{package_name}/
├── src/{package_name.replace('-', '_')}/    # Source code (src-layout)
├── tests/                    # Test suite
├── examples/                 # SciTeX-formatted examples
├── docs/                     # Documentation
├── setup.cfg                 # Package configuration
├── pyproject.toml           # Build configuration
└── .github/workflows/       # CI/CD
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Building Distribution
```bash
python -m build
```

## SciTeX Integration

This package includes SciTeX-formatted examples in the `examples/` directory. These demonstrate:

- Proper script structure with `stx.gen.start()` and `stx.gen.close()`
- Configuration management via YAML files
- Unified I/O with automatic format detection
- Enhanced plotting with data export
- Reproducible workflow patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure examples follow SciTeX format
5. Submit a pull request

## License

[Your chosen license]

## Requirements

- Python 3.8+
- SciTeX (optional but recommended for examples)
- See `setup.cfg` for complete dependencies
"""

    def _generate_setup_cfg(self, package_name: str) -> str:
        """Generate setup.cfg for pip package."""
        package_module = package_name.replace('-', '_')
        return f"""[metadata]
name = {package_name}
version = 0.1.0
author = Your Name
author_email = your.email@example.com
description = A SciTeX-integrated Python package
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/yourusername/{package_name}
project_urls =
    Bug Tracker = https://github.com/yourusername/{package_name}/issues
classifiers =
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    Intended Audience :: Science/Research
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Programming Language :: Python :: 3.11
    Programming Language :: Python :: 3.12
    Topic :: Scientific/Engineering

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.8
install_requires =
    numpy
    matplotlib

[options.packages.find]
where = src

[options.extras_require]
dev =
    pytest>=7.0
    pytest-cov
    black
    isort
    flake8
    mypy
scitex =
    scitex

[tool:pytest]
minversion = 6.0
addopts = -ra -q --cov={package_module}
testpaths =
    tests

[coverage:run]
source = src

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
"""

    def _generate_pyproject_toml(self, package_name: str) -> str:
        """Generate pyproject.toml for pip package."""
        return f"""[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
"""

    def _generate_basic_test(self, package_name: str) -> str:
        """Generate basic test file."""
        package_module = package_name.replace('-', '_')
        return f'''"""Basic tests for {package_name}."""

import pytest
import {package_module}


def test_package_import():
    """Test that the package can be imported."""
    assert {package_module}.__version__ is not None


def test_basic_functionality():
    """Test basic functionality (replace with actual tests)."""
    # Add your actual tests here
    assert True


class Test{package_module.title().replace('_', '')}:
    """Test class for {package_module} functionality."""
    
    def test_example_method(self):
        """Test example method."""
        # Replace with actual test
        assert True
        
    def test_error_handling(self):
        """Test error handling."""
        # Replace with actual test
        assert True


# Integration tests (if applicable)
def test_scitex_integration():
    """Test SciTeX integration if available."""
    try:
        import scitex
        # Test integration with SciTeX
        assert True
    except ImportError:
        pytest.skip("SciTeX not available")
'''

    def _generate_package_init(self, package_name: str) -> str:
        """Generate package __init__.py."""
        package_module = package_name.replace('-', '_')
        return f'''"""
{package_name}: A SciTeX-integrated Python package.

This package provides [describe your package functionality here].
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main functionality
# from .core import main_function
# from .utils import helper_function

__all__ = [
    # "main_function",
    # "helper_function",
]
'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# SciTeX specific
*_out/
*.log
RUNNING
FINISHED_SUCCESS
FINISHED_FAILURE

# Data files (adjust as needed)
data/raw/*
!data/raw/.gitkeep
data/external/*
!data/external/.gitkeep

# OS specific
.DS_Store
Thumbs.db
"""


def main():
    """CLI interface for the validator."""
    if len(sys.argv) < 2:
        print("Usage: python validator.py <command> [args...]")
        print("Commands:")
        print("  check-scientific <project_path>    - Validate scientific project")  
        print("  check-package <package_path>       - Validate pip package")
        print("  create-scientific <path> <name>    - Create scientific project template")
        print("  create-package <path> <name>       - Create pip package template")
        return
        
    validator = ScitexProjectValidator()
    command = sys.argv[1]
    
    if command in ["check-scientific", "check-package"]:
        if len(sys.argv) < 3:
            print(f"Usage: python validator.py {command} <project_path>")
            return
            
        project_path = sys.argv[2]
        
        if command == "check-scientific":
        result = validator.check_scientific_project(project_path)
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
        result = validator.check_pip_package(project_path)
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


if __name__ == "__main__":
    main()

# EOF