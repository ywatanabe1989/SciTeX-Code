#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:32:00 (ywatanabe)"
# File: ./mcp_servers/scitex-framework/server.py
# ----------------------------------------

"""MCP server for SciTeX framework template generation and project scaffolding."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from scitex_base.base_server import ScitexBaseMCPServer


class ScitexFrameworkMCPServer(ScitexBaseMCPServer):
    """MCP server for SciTeX framework operations and project management."""
    
    def __init__(self):
        super().__init__("framework", "0.1.0")
        
    def _register_module_tools(self):
        """Register framework-specific tools."""
        
        @self.app.tool()
        async def generate_scitex_script_template(
            script_purpose: str,
            modules_needed: List[str] = ["io", "plt"],
            include_config: bool = True,
            script_name: str = "script.py"
        ) -> Dict[str, str]:
            """Generate complete SciTeX script following IMPORTANT-SCITEX-02 template."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Build imports based on modules needed
            module_imports = []
            if "plt" in modules_needed:
                module_imports.append("import matplotlib.pyplot as plt")
            if "pd" in modules_needed:
                module_imports.append("import pandas as pd")
            if "np" in modules_needed or "numpy" in modules_needed:
                module_imports.append("import numpy as np")
                
            template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: {script_name}
# ----------------------------------------
import os
__FILE__ = "{script_name}"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - {script_purpose}
  - Loads data using stx.io.load()
  - Saves results using stx.io.save()

Dependencies:
  - packages: scitex{', ' + ', '.join(modules_needed) if modules_needed else ''}

Input:
  - ./data/input.csv (via CONFIG.PATH.INPUT_DATA)
  - ./config/PATH.yaml
  - ./config/PARAMS.yaml

Output:
  - ./results.csv (via stx.io.save)
  - ./plots.jpg (via stx.io.save with automatic CSV export)
"""

"""Imports"""
import argparse
import scitex as stx
{chr(10).join(module_imports)}

"""Parameters"""
CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args):
    """Main processing function."""
    # Load data
    data = stx.io.load(CONFIG.PATH.INPUT_DATA)
    
    # Process data
    results = process_data(data, args)
    
    {'# Create visualization' if 'plt' in modules_needed else ''}
    {'fig, ax = stx.plt.subplots()' if 'plt' in modules_needed else ''}
    {'ax.plot(results["x"], results["y"])' if 'plt' in modules_needed else ''}
    {'ax.set_xyt("X axis", "Y axis", "Results")' if 'plt' in modules_needed else ''}
    
    # Save outputs
    stx.io.save(results, './results.csv', symlink_from_cwd=True)
    {'stx.io.save(fig, "./plots.jpg", symlink_from_cwd=True)' if 'plt' in modules_needed else ''}
    
    return 0

def process_data(data, args):
    """Process the input data.
    
    Args:
        data: Input data loaded from file
        args: Command line arguments
        
    Returns:
        Processed results
    """
    # Add processing logic here
    if args.verbose:
        stx.str.printc(f"Processing {{len(data)}} records...", c="yellow")
    
    # Example processing
    results = data.copy()
    
    return results

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="{script_purpose}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode")
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args

def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    {'import matplotlib.pyplot as plt' if 'plt' in modules_needed else ''}

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=args.verbose,
        agg={'True' if 'plt' in modules_needed else 'False'},
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=args.verbose,
        notify=False,
        message="",
        exit_status=exit_status,
    )

if __name__ == "__main__":
    run_main()

# EOF'''
            
            return {
                "script_code": template,
                "next_steps": [
                    "1. Save script to ./scripts/category/script_name.py",
                    "2. Create config files if needed (use generate_config_files tool)",
                    "3. Update CONFIG paths in ./config/PATH.yaml",
                    "4. Run from project root: python ./scripts/category/script_name.py",
                    "5. Check outputs in ./scripts/category/script_name_out/"
                ],
                "required_configs": ["PATH.yaml", "PARAMS.yaml", "IS_DEBUG.yaml"] if include_config else []
            }
            
        @self.app.tool()
        async def generate_config_files(
            project_type: str = "research",
            detected_paths: List[str] = None,
            detected_params: Dict[str, Any] = None
        ) -> Dict[str, str]:
            """Generate SciTeX configuration files following IMPORTANT-SCITEX-03."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            configs = {}
            
            # PATH.yaml
            path_entries = ["  INPUT_DATA: \"./data/input.csv\"",
                          "  OUTPUT_DIR: \"./output\"",
                          "  FIGURES_DIR: \"./figures\"",
                          "  MODELS_DIR: \"./models\""]
            
            if detected_paths:
                path_entries.append("\n  # Detected paths")
                for i, path in enumerate(detected_paths):
                    var_name = self._path_to_var_name(path)
                    path_entries.append(f"  {var_name}: \"{path}\"")
                    
            configs["config/PATH.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/PATH.yaml

PATH:
{chr(10).join(path_entries)}
'''
            
            # PARAMS.yaml
            param_entries = ["  RANDOM_SEED: 42",
                           "  SIGNIFICANCE_THRESHOLD: 0.05",
                           "  N_ITERATIONS: 1000",
                           "  BATCH_SIZE: 32"]
            
            if detected_params:
                param_entries.append("\n  # Detected parameters")
                for key, value in detected_params.items():
                    param_entries.append(f"  {key}: {value}")
                    
            configs["config/PARAMS.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/PARAMS.yaml

PARAMS:
{chr(10).join(param_entries)}
'''
            
            # IS_DEBUG.yaml
            configs["config/IS_DEBUG.yaml"] = '''IS_DEBUG: false

# Debug settings
DEBUG_INPUT_DATA: "./data/sample_input.csv"
DEBUG_MAX_ITERATIONS: 10
DEBUG_BATCH_SIZE: 4
'''
            
            # COLORS.yaml (optional but useful)
            configs["config/COLORS.yaml"] = '''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/COLORS.yaml

COLORS:
  PRIMARY: "#1f77b4"
  SECONDARY: "#ff7f0e"
  SUCCESS: "#2ca02c"
  WARNING: "#d62728"
  INFO: "#9467bd"
  
  # Plot colors
  LINE_COLORS:
    - "#1f77b4"
    - "#ff7f0e"
    - "#2ca02c"
    - "#d62728"
    - "#9467bd"
'''
            
            return configs
            
        @self.app.tool()
        async def create_scitex_project(
            project_name: str,
            project_type: str = "research",
            modules_needed: List[str] = ["io", "plt"],
            include_examples: bool = True
        ) -> Dict[str, Any]:
            """Create complete SciTeX project following directory structure guidelines."""
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate main script
            main_script = await self.generate_scitex_script_template(
                f"Main analysis script for {project_name}",
                modules_needed,
                True,
                f"./scripts/{project_name}/main.py"
            )
            
            # Generate configs
            configs = await self.generate_config_files(project_type)
            
            if project_type == "research":
                structure = {
                    "config/": configs,
                    "scripts/": {
                        f"{project_name}/": {
                            "main.py": main_script["script_code"],
                            "analysis.py": await self._generate_analysis_script(project_name, modules_needed),
                            "__init__.py": f'"""Scripts for {project_name} project."""'
                        }
                    },
                    "data/": {
                        ".gitkeep": "# Keep this directory in git"
                    },
                    "examples/": {
                        f"example_{project_name}.py": await self._generate_example_script(project_name)
                    } if include_examples else {},
                    ".playground/": {
                        ".gitignore": "*\n!.gitignore",
                        "experiments/": {".gitkeep": ""},
                        "prototypes/": {".gitkeep": ""}
                    },
                    ".gitignore": self._generate_gitignore(),
                    "README.md": self._generate_readme(project_name, project_type),
                    "requirements.txt": self._generate_requirements(modules_needed)
                }
            else:  # package
                structure = {
                    "src/": {
                        project_name.replace("-", "_"): {
                            "__init__.py": f'"""SciTeX-based {project_name} package."""\n\n__version__ = "0.1.0"',
                            "core.py": await self._generate_package_core(project_name, modules_needed),
                            "utils.py": "# Utility functions"
                        }
                    },
                    "tests/": {
                        "conftest.py": self._generate_pytest_config(),
                        f"test_{project_name}.py": self._generate_tests(project_name)
                    },
                    "examples/": {
                        f"example_{project_name}.py": await self._generate_example_script(project_name)
                    } if include_examples else {},
                    "config/": configs,
                    "pyproject.toml": self._generate_pyproject_toml(project_name),
                    ".gitignore": self._generate_gitignore(),
                    "README.md": self._generate_readme(project_name, project_type)
                }
                
            return {
                "project_structure": structure,
                "files_to_create": self._flatten_structure(structure),
                "next_steps": [
                    f"1. Create project directory: mkdir -p {project_name}",
                    f"2. cd {project_name}",
                    "3. Create all files and directories from the structure",
                    "4. Initialize git: git init",
                    "5. Install scitex: pip install -e ~/proj/scitex_repo",
                    "6. Install requirements: pip install -r requirements.txt",
                    "7. Run example: python examples/example_*.py"
                ],
                "total_files": len(self._flatten_structure(structure))
            }
            
        @self.app.tool()
        async def validate_project_structure(
            project_path: str
        ) -> Dict[str, Any]:
            """Validate project follows SciTeX directory structure guidelines."""
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
                
            validation = {
                "compliant": True,
                "score": 100,
                "issues": [],
                "warnings": [],
                "structure_analysis": {}
            }
            
            # Check required directories for research project
            required_dirs = ["config", "scripts", "data"]
            recommended_dirs = ["examples", "tests", ".playground"]
            
            for dir_name in required_dirs:
                if not (project / dir_name).exists():
                    validation["issues"].append(f"Missing required directory: {dir_name}")
                    validation["compliant"] = False
                    validation["score"] -= 20
                    
            for dir_name in recommended_dirs:
                if not (project / dir_name).exists():
                    validation["warnings"].append(f"Missing recommended directory: {dir_name}")
                    validation["score"] -= 5
                    
            # Check for Python files in root (violation)
            root_py_files = list(project.glob("*.py"))
            if root_py_files:
                validation["issues"].append(
                    f"Python files found in project root: {[f.name for f in root_py_files]}"
                )
                validation["compliant"] = False
                validation["score"] -= 10
                
            # Check config files
            required_configs = ["PATH.yaml", "IS_DEBUG.yaml"]
            for config in required_configs:
                if not (project / "config" / config).exists():
                    validation["issues"].append(f"Missing config file: config/{config}")
                    validation["score"] -= 10
                    
            # Analyze structure
            validation["structure_analysis"] = {
                "total_python_files": len(list(project.rglob("*.py"))),
                "total_config_files": len(list(project.glob("config/*.yaml"))),
                "has_examples": (project / "examples").exists(),
                "has_tests": (project / "tests").exists(),
                "scripts_organized": len(list((project / "scripts").iterdir())) > 0 if (project / "scripts").exists() else False
            }
            
            validation["score"] = max(0, validation["score"])
            
            return validation
            
    def _path_to_var_name(self, path: str) -> str:
        """Convert path to valid variable name."""
        base = Path(path).stem.upper()
        return re.sub(r'[^A-Z0-9_]', '_', base)
        
    async def _generate_analysis_script(self, project_name: str, modules: List[str]) -> str:
        """Generate analysis script template."""
        template = await self.generate_scitex_script_template(
            f"Analysis functions for {project_name}",
            modules,
            True,
            f"./scripts/{project_name}/analysis.py"
        )
        return template["script_code"]
        
    async def _generate_example_script(self, project_name: str) -> str:
        """Generate example script."""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Example usage of {project_name}

import sys
sys.path.append('.')

from scripts.{project_name}.main import main, parse_args

if __name__ == "__main__":
    # Example with custom arguments
    class Args:
        verbose = True
        debug = False
    
    args = Args()
    main(args)
'''
        
    async def _generate_package_core(self, project_name: str, modules: List[str]) -> str:
        """Generate package core module."""
        return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Core functionality for {project_name}."""

import scitex as stx
{chr(10).join([f"import {m}" for m in modules if m in ["numpy", "pandas"]])}

class {project_name.replace("-", " ").title().replace(" ", "")}:
    """Main class for {project_name}."""
    
    def __init__(self, config_path: str = "./config"):
        """Initialize with configuration."""
        self.config = stx.io.load_configs(config_path)
        
    def process(self, data):
        """Process data according to configuration."""
        # Implementation here
        return data
'''
        
    def _generate_pytest_config(self) -> str:
        """Generate pytest configuration."""
        return '''"""Pytest configuration."""
import pytest
import scitex as stx

@pytest.fixture
def test_config():
    """Load test configuration."""
    return stx.io.load_configs("./tests/config")
'''
        
    def _generate_tests(self, project_name: str) -> str:
        """Generate basic tests."""
        return f'''"""Tests for {project_name}."""
import pytest
from src.{project_name.replace("-", "_")}.core import *

def test_import():
    """Test that package can be imported."""
    assert True
'''
        
    def _generate_pyproject_toml(self, project_name: str) -> str:
        """Generate pyproject.toml for package."""
        return f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "0.1.0"
description = "SciTeX-based {project_name} package"
requires-python = ">= 3.8"
dependencies = [
    "scitex",
    "numpy",
    "pandas",
    "matplotlib",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "black",
    "flake8",
]
'''
        
    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# SciTeX specific
*_out/
.old/
.tmp/
*.log

# Data files (add specific patterns as needed)
*.csv
*.xlsx
*.h5
*.pkl

# Jupyter
.ipynb_checkpoints/
*.ipynb

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Keep playground experimental
.playground/*
!.playground/.gitignore
'''
        
    def _generate_readme(self, project_name: str, project_type: str) -> str:
        """Generate README.md."""
        return f'''# {project_name}

SciTeX-based {project_type} project.

## Setup

1. Install SciTeX:
   ```bash
   pip install -e ~/proj/scitex_repo
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

{"Run the main analysis script:" if project_type == "research" else "Import and use the package:"}
```bash
{"python ./scripts/" + project_name + "/main.py" if project_type == "research" else "from " + project_name.replace("-", "_") + " import *"}
```

## Project Structure

```
{project_name}/
├── config/          # Configuration files
├── scripts/         # Analysis scripts
├── data/           # Data files (git-ignored)
├── examples/       # Example usage
└── README.md       # This file
```

## Configuration

Edit files in `config/` to customize:
- `PATH.yaml` - File paths
- `PARAMS.yaml` - Parameters
- `IS_DEBUG.yaml` - Debug settings
'''
        
    def _generate_requirements(self, modules: List[str]) -> str:
        """Generate requirements.txt."""
        reqs = ["scitex"]
        if "plt" in modules:
            reqs.append("matplotlib")
        if "pd" in modules:
            reqs.append("pandas")
        if "np" in modules or "numpy" in modules:
            reqs.append("numpy")
        if "stats" in modules:
            reqs.append("scipy")
        return '\n'.join(reqs)
        
    def _flatten_structure(self, structure: Dict, prefix: str = "") -> List[str]:
        """Flatten nested structure to list of file paths."""
        files = []
        for key, value in structure.items():
            path = f"{prefix}/{key}" if prefix else key
            if isinstance(value, dict):
                files.extend(self._flatten_structure(value, path))
            else:
                files.append(path)
        return files
        
    def get_module_description(self) -> str:
        """Get description of framework functionality."""
        return (
            "SciTeX framework server provides complete script template generation, "
            "project scaffolding, configuration management, and structure validation "
            "following all SciTeX guidelines for reproducible scientific computing."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "generate_scitex_script_template",
            "generate_config_files",
            "create_scitex_project",
            "validate_project_structure",
            "get_module_info",
            "validate_code"
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate framework compliance."""
        issues = []
        
        # Check for required template elements
        required = [
            "#!/usr/bin/env python3",
            "__FILE__ =",
            "__DIR__ =",
            "import scitex as stx",
            "CONFIG = stx.io.load_configs()",
            "def main(args):",
            "def run_main():",
            "stx.gen.start(",
            "stx.gen.close("
        ]
        
        for element in required:
            if element not in code:
                issues.append(f"Missing required element: {element}")
                
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 10)
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexFrameworkMCPServer()
    asyncio.run(server.run())

# EOF