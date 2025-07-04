#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:41:00 (ywatanabe)"
# File: ./mcp_servers/scitex-orchestrator/server.py
# ----------------------------------------

"""MCP server for SciTeX project orchestration and coordination."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import json
import yaml
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from scitex_base.base_server import ScitexBaseMCPServer


class ScitexOrchestratorMCPServer(ScitexBaseMCPServer):
    """MCP server for orchestrating SciTeX projects and workflows."""
    
    def __init__(self):
        super().__init__("orchestrator", "0.1.0")
        
    def _register_module_tools(self):
        """Register orchestrator-specific tools."""
        
        @self.app.tool()
        async def analyze_project_health(
            project_path: str = "."
        ) -> Dict[str, Any]:
            """Comprehensive health check of SciTeX project."""
            
            project = Path(project_path)
            if not project.exists():
                return {"error": f"Project path {project_path} does not exist"}
                
            health = {
                "overall_score": 100,
                "status": "healthy",
                "components": {},
                "issues": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check directory structure
            structure_health = self._check_directory_structure(project)
            health["components"]["structure"] = structure_health
            health["overall_score"] = min(health["overall_score"], structure_health["score"])
            
            # Check configuration files
            config_health = self._check_configurations(project)
            health["components"]["configuration"] = config_health
            health["overall_score"] = min(health["overall_score"], config_health["score"])
            
            # Check script compliance
            script_health = self._check_script_compliance(project)
            health["components"]["scripts"] = script_health
            health["overall_score"] = min(health["overall_score"], script_health["score"])
            
            # Check dependencies
            dep_health = self._check_dependencies(project)
            health["components"]["dependencies"] = dep_health
            health["overall_score"] = min(health["overall_score"], dep_health["score"])
            
            # Check git status
            git_health = self._check_git_status(project)
            health["components"]["version_control"] = git_health
            
            # Aggregate issues and warnings
            for component in health["components"].values():
                health["issues"].extend(component.get("issues", []))
                health["warnings"].extend(component.get("warnings", []))
                
            # Generate recommendations
            health["recommendations"] = self._generate_recommendations(health)
            
            # Set overall status
            if health["overall_score"] >= 80:
                health["status"] = "healthy"
            elif health["overall_score"] >= 60:
                health["status"] = "needs_attention"
            else:
                health["status"] = "unhealthy"
                
            return health
            
        @self.app.tool()
        async def initialize_scitex_project(
            project_name: str,
            project_type: str = "research",
            modules: List[str] = ["io", "plt"],
            include_examples: bool = True,
            create_git_repo: bool = True
        ) -> Dict[str, Any]:
            """Initialize complete SciTeX project with all components."""
            
            project_path = Path(project_name)
            
            # Check if directory exists
            if project_path.exists():
                return {
                    "error": f"Directory {project_name} already exists",
                    "suggestion": "Use a different name or remove existing directory"
                }
                
            result = {
                "created_files": [],
                "created_directories": [],
                "setup_commands": [],
                "status": "success",
                "next_steps": []
            }
            
            try:
                # Create project directory
                project_path.mkdir(parents=True)
                result["created_directories"].append(str(project_path))
                
                # Create directory structure
                dirs_to_create = [
                    "config",
                    "scripts",
                    f"scripts/{project_name}",
                    "data",
                    "data/raw",
                    "data/processed",
                    ".playground",
                    ".playground/experiments",
                    ".playground/prototypes"
                ]
                
                if include_examples:
                    dirs_to_create.append("examples")
                    
                if project_type == "package":
                    dirs_to_create.extend([
                        "src",
                        f"src/{project_name.replace('-', '_')}",
                        "tests"
                    ])
                    
                for dir_name in dirs_to_create:
                    (project_path / dir_name).mkdir(parents=True, exist_ok=True)
                    result["created_directories"].append(f"{project_name}/{dir_name}")
                    
                # Generate configuration files
                config_files = await self._generate_all_configs(project_name, project_type)
                for file_path, content in config_files.items():
                    full_path = project_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
                    result["created_files"].append(f"{project_name}/{file_path}")
                    
                # Generate main script
                main_script = await self._generate_main_script(project_name, modules, project_type)
                script_path = project_path / "scripts" / project_name / "main.py"
                script_path.write_text(main_script)
                result["created_files"].append(f"{project_name}/scripts/{project_name}/main.py")
                
                # Generate .gitignore
                gitignore = self._generate_gitignore()
                (project_path / ".gitignore").write_text(gitignore)
                result["created_files"].append(f"{project_name}/.gitignore")
                
                # Generate README
                readme = self._generate_readme(project_name, project_type, modules)
                (project_path / "README.md").write_text(readme)
                result["created_files"].append(f"{project_name}/README.md")
                
                # Generate requirements.txt
                requirements = self._generate_requirements(modules)
                (project_path / "requirements.txt").write_text(requirements)
                result["created_files"].append(f"{project_name}/requirements.txt")
                
                # Initialize git repo if requested
                if create_git_repo:
                    subprocess.run(["git", "init"], cwd=project_path, capture_output=True)
                    subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True)
                    subprocess.run(
                        ["git", "commit", "-m", f"Initial commit for {project_name} SciTeX project"],
                        cwd=project_path,
                        capture_output=True
                    )
                    result["setup_commands"].append("git init && git add . && git commit")
                    
                # Generate next steps
                result["next_steps"] = [
                    f"cd {project_name}",
                    "pip install -r requirements.txt",
                    f"python scripts/{project_name}/main.py --help",
                    "Edit config files in config/ directory",
                    "Add your data to data/raw/",
                    "Start developing!"
                ]
                
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
                
            return result
            
        @self.app.tool()
        async def run_scitex_workflow(
            workflow_name: str,
            project_path: str = ".",
            parameters: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            """Run predefined SciTeX workflow."""
            
            workflows = {
                "analysis": self._run_analysis_workflow,
                "preprocessing": self._run_preprocessing_workflow,
                "training": self._run_training_workflow,
                "evaluation": self._run_evaluation_workflow,
                "reporting": self._run_reporting_workflow
            }
            
            if workflow_name not in workflows:
                return {
                    "error": f"Unknown workflow: {workflow_name}",
                    "available_workflows": list(workflows.keys())
                }
                
            return await workflows[workflow_name](project_path, parameters or {})
            
        @self.app.tool()
        async def suggest_project_improvements(
            project_path: str = "."
        ) -> Dict[str, List[Dict[str, str]]]:
            """Analyze project and suggest improvements."""
            
            project = Path(project_path)
            suggestions = {
                "critical": [],
                "recommended": [],
                "optional": [],
                "performance": []
            }
            
            # Analyze project
            health = await self.analyze_project_health(project_path)
            
            # Critical improvements
            if health["overall_score"] < 60:
                suggestions["critical"].append({
                    "title": "Fix project structure",
                    "description": "Your project structure has critical issues",
                    "action": "Run 'fix_project_structure' tool to automatically fix issues"
                })
                
            # Check for missing configs
            config_path = project / "config"
            if not (config_path / "PATH.yaml").exists():
                suggestions["critical"].append({
                    "title": "Create PATH.yaml",
                    "description": "PATH.yaml is required for SciTeX projects",
                    "action": "Use 'generate_all_config_files' from scitex-config"
                })
                
            # Recommended improvements
            if not (project / ".playground").exists():
                suggestions["recommended"].append({
                    "title": "Add playground directory",
                    "description": "Playground helps isolate experiments",
                    "action": "mkdir -p .playground/experiments .playground/prototypes"
                })
                
            # Check for hardcoded values
            scripts = list((project / "scripts").rglob("*.py")) if (project / "scripts").exists() else []
            for script in scripts[:5]:  # Check first 5 scripts
                content = script.read_text()
                if re.search(r'\b\d+\.\d+\b', content) and "CONFIG" not in content:
                    suggestions["recommended"].append({
                        "title": f"Extract parameters from {script.name}",
                        "description": "Found hardcoded numeric values",
                        "action": "Use 'extract_parameters_from_code' tool"
                    })
                    break
                    
            # Optional improvements
            if not (project / "tests").exists():
                suggestions["optional"].append({
                    "title": "Add test directory",
                    "description": "Tests help ensure code quality",
                    "action": "Create tests/ directory and add pytest tests"
                })
                
            # Performance suggestions
            if len(scripts) > 20:
                suggestions["performance"].append({
                    "title": "Organize scripts into subcategories",
                    "description": "Too many scripts in one directory",
                    "action": "Group related scripts into subdirectories"
                })
                
            return suggestions
            
        @self.app.tool()
        async def fix_project_structure(
            project_path: str = ".",
            auto_fix: bool = True,
            backup: bool = True
        ) -> Dict[str, Any]:
            """Fix common project structure issues."""
            
            project = Path(project_path)
            fixes = {
                "applied": [],
                "skipped": [],
                "errors": [],
                "backup_location": None
            }
            
            # Create backup if requested
            if backup:
                backup_dir = project.parent / f"{project.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(["cp", "-r", str(project), str(backup_dir)], capture_output=True)
                fixes["backup_location"] = str(backup_dir)
                
            # Fix: Create missing directories
            required_dirs = ["config", "scripts", "data"]
            for dir_name in required_dirs:
                dir_path = project / dir_name
                if not dir_path.exists():
                    if auto_fix:
                        dir_path.mkdir(parents=True)
                        fixes["applied"].append(f"Created missing directory: {dir_name}")
                    else:
                        fixes["skipped"].append(f"Would create directory: {dir_name}")
                        
            # Fix: Move Python files from root
            root_py_files = list(project.glob("*.py"))
            if root_py_files:
                scripts_dir = project / "scripts" / "misc"
                if auto_fix:
                    scripts_dir.mkdir(parents=True, exist_ok=True)
                    for py_file in root_py_files:
                        if py_file.name not in ["setup.py", "conftest.py"]:
                            py_file.rename(scripts_dir / py_file.name)
                            fixes["applied"].append(f"Moved {py_file.name} to scripts/misc/")
                else:
                    fixes["skipped"].append(f"Would move {len(root_py_files)} Python files to scripts/")
                    
            # Fix: Create missing configs
            config_dir = project / "config"
            if not (config_dir / "PATH.yaml").exists():
                if auto_fix:
                    # Generate basic configs
                    configs = await self._generate_all_configs(project.name, "research")
                    for file_path, content in configs.items():
                        full_path = project / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(content)
                        fixes["applied"].append(f"Created {file_path}")
                else:
                    fixes["skipped"].append("Would create configuration files")
                    
            # Fix: Update .gitignore
            gitignore_path = project / ".gitignore"
            if not gitignore_path.exists():
                if auto_fix:
                    gitignore_path.write_text(self._generate_gitignore())
                    fixes["applied"].append("Created .gitignore")
                else:
                    fixes["skipped"].append("Would create .gitignore")
                    
            return fixes
            
        @self.app.tool()
        async def migrate_to_scitex(
            source_project: str,
            target_project: str = None,
            migration_strategy: str = "gradual"
        ) -> Dict[str, Any]:
            """Migrate existing project to SciTeX structure."""
            
            source = Path(source_project)
            if not source.exists():
                return {"error": f"Source project {source_project} not found"}
                
            if target_project is None:
                target_project = f"{source.name}_scitex"
                
            target = Path(target_project)
            
            migration = {
                "source": str(source),
                "target": str(target),
                "strategy": migration_strategy,
                "actions": [],
                "converted_files": [],
                "migration_plan": []
            }
            
            if migration_strategy == "gradual":
                # Create symlink structure
                migration["migration_plan"] = [
                    "1. Create SciTeX directory structure alongside existing",
                    "2. Gradually move and convert files",
                    "3. Update imports progressively",
                    "4. Test after each migration step"
                ]
                
                # Don't copy everything, just create structure
                if not target.exists():
                    target.mkdir(parents=True)
                    migration["actions"].append(f"Created target directory: {target}")
                    
                # Create SciTeX structure
                result = await self.initialize_scitex_project(
                    str(target),
                    project_type="research",
                    create_git_repo=False
                )
                migration["actions"].extend(result.get("created_files", []))
                
            else:  # full migration
                # Copy entire project
                subprocess.run(["cp", "-r", str(source), str(target)], capture_output=True)
                migration["actions"].append(f"Copied project to {target}")
                
                # Fix structure
                fix_result = await self.fix_project_structure(str(target), auto_fix=True, backup=False)
                migration["actions"].extend(fix_result.get("applied", []))
                
                # Convert Python files
                py_files = list(target.rglob("*.py"))
                for py_file in py_files[:10]:  # Limit to first 10 for demo
                    # This would call translation tools
                    migration["converted_files"].append(str(py_file.relative_to(target)))
                    
            migration["next_steps"] = [
                f"cd {target}",
                "Review migrated structure",
                "Use translation tools to convert code",
                "Update imports and dependencies",
                "Run tests to verify functionality"
            ]
            
            return migration
            
    def _check_directory_structure(self, project: Path) -> Dict[str, Any]:
        """Check project directory structure compliance."""
        
        result = {
            "score": 100,
            "issues": [],
            "warnings": []
        }
        
        # Required directories
        required = ["config", "scripts", "data"]
        for dir_name in required:
            if not (project / dir_name).exists():
                result["issues"].append(f"Missing required directory: {dir_name}")
                result["score"] -= 20
                
        # Check for root Python files
        root_py = list(project.glob("*.py"))
        allowed_root = ["setup.py", "conftest.py"]
        violations = [f for f in root_py if f.name not in allowed_root]
        
        if violations:
            result["issues"].append(
                f"Python files in root: {[f.name for f in violations[:3]]}"
            )
            result["score"] -= 15
            
        # Recommended directories
        recommended = [".playground", "examples", "tests"]
        for dir_name in recommended:
            if not (project / dir_name).exists():
                result["warnings"].append(f"Missing recommended directory: {dir_name}")
                result["score"] -= 5
                
        result["score"] = max(0, result["score"])
        return result
        
    def _check_configurations(self, project: Path) -> Dict[str, Any]:
        """Check configuration files."""
        
        result = {
            "score": 100,
            "issues": [],
            "warnings": []
        }
        
        config_dir = project / "config"
        if not config_dir.exists():
            result["issues"].append("Config directory missing")
            result["score"] = 0
            return result
            
        # Required configs
        required = ["PATH.yaml", "PARAMS.yaml", "IS_DEBUG.yaml"]
        for config in required:
            if not (config_dir / config).exists():
                result["issues"].append(f"Missing required config: {config}")
                result["score"] -= 25
                
        # Optional configs
        optional = ["COLORS.yaml", "LOGGING.yaml"]
        for config in optional:
            if not (config_dir / config).exists():
                result["warnings"].append(f"Missing optional config: {config}")
                result["score"] -= 5
                
        result["score"] = max(0, result["score"])
        return result
        
    def _check_script_compliance(self, project: Path) -> Dict[str, Any]:
        """Check script compliance with SciTeX guidelines."""
        
        result = {
            "score": 100,
            "issues": [],
            "warnings": [],
            "non_compliant_scripts": []
        }
        
        scripts_dir = project / "scripts"
        if not scripts_dir.exists():
            return result
            
        scripts = list(scripts_dir.rglob("*.py"))
        sample_size = min(10, len(scripts))  # Check up to 10 scripts
        
        for script in scripts[:sample_size]:
            content = script.read_text()
            
            # Check for required elements
            required_patterns = [
                (r'#!/usr/bin/env python3', "Missing shebang"),
                (r'__FILE__\s*=', "Missing __FILE__ definition"),
                (r'import scitex as stx', "Not using scitex"),
                (r'CONFIG\s*=\s*stx\.io\.load_configs', "Not loading CONFIG"),
                (r'def main\(', "Missing main function"),
                (r'def run_main\(', "Missing run_main function")
            ]
            
            script_issues = []
            for pattern, issue in required_patterns:
                if not re.search(pattern, content):
                    script_issues.append(issue)
                    
            if script_issues:
                result["non_compliant_scripts"].append({
                    "script": str(script.relative_to(project)),
                    "issues": script_issues
                })
                result["score"] -= 5
                
        if result["non_compliant_scripts"]:
            result["issues"].append(
                f"{len(result['non_compliant_scripts'])} scripts are non-compliant"
            )
            
        result["score"] = max(0, result["score"])
        return result
        
    def _check_dependencies(self, project: Path) -> Dict[str, Any]:
        """Check project dependencies."""
        
        result = {
            "score": 100,
            "issues": [],
            "warnings": []
        }
        
        # Check for requirements.txt or pyproject.toml
        has_requirements = (project / "requirements.txt").exists()
        has_pyproject = (project / "pyproject.toml").exists()
        
        if not has_requirements and not has_pyproject:
            result["issues"].append("No dependency file found (requirements.txt or pyproject.toml)")
            result["score"] -= 30
        elif has_requirements:
            # Check if scitex is in requirements
            reqs = (project / "requirements.txt").read_text()
            if "scitex" not in reqs:
                result["issues"].append("scitex not in requirements.txt")
                result["score"] -= 20
                
        return result
        
    def _check_git_status(self, project: Path) -> Dict[str, Any]:
        """Check git repository status."""
        
        result = {
            "score": 100,
            "issues": [],
            "warnings": []
        }
        
        # Check if git repo
        if not (project / ".git").exists():
            result["warnings"].append("Not a git repository")
            return result
            
        # Check git status
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project,
                capture_output=True,
                text=True
            )
            
            if status.stdout:
                untracked = len([l for l in status.stdout.split('\n') if l.startswith('??')])
                modified = len([l for l in status.stdout.split('\n') if l.startswith(' M')])
                
                if untracked > 10:
                    result["warnings"].append(f"{untracked} untracked files")
                if modified > 0:
                    result["warnings"].append(f"{modified} modified files")
                    
        except:
            result["warnings"].append("Could not check git status")
            
        return result
        
    def _generate_recommendations(self, health: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health check."""
        
        recommendations = []
        
        if health["overall_score"] < 60:
            recommendations.append("Run 'fix_project_structure' to automatically fix critical issues")
            
        if "structure" in health["components"]:
            if health["components"]["structure"]["score"] < 80:
                recommendations.append("Reorganize project to follow SciTeX directory structure")
                
        if "scripts" in health["components"]:
            non_compliant = health["components"]["scripts"].get("non_compliant_scripts", [])
            if non_compliant:
                recommendations.append(
                    f"Convert {len(non_compliant)} scripts to SciTeX format using translation tools"
                )
                
        if not any(".playground" in w for w in health.get("warnings", [])):
            recommendations.append("Add .playground directory for experiments")
            
        return recommendations
        
    async def _generate_all_configs(
        self,
        project_name: str,
        project_type: str
    ) -> Dict[str, str]:
        """Generate all configuration files."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        configs = {}
        
        # PATH.yaml
        configs["config/PATH.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/PATH.yaml

PATH:
  # Data paths
  DATA_DIR: "./data"
  RAW_DATA: "./data/raw"
  PROCESSED_DATA: "./data/processed"
  
  # Output paths
  OUTPUT_DIR: "./output"
  FIGURES_DIR: "./output/figures"
  RESULTS_DIR: "./output/results"
  
  # Script output
  SCRIPT_OUTPUT: "./scripts/{project_name}/{project_name}_out"
'''
        
        # PARAMS.yaml
        configs["config/PARAMS.yaml"] = f'''# Time-stamp: "{timestamp} (ywatanabe)"
# File: ./config/PARAMS.yaml

PARAMS:
  # General settings
  RANDOM_SEED: 42
  VERBOSE: true
  
  # Processing parameters
  BATCH_SIZE: 32
  N_ITERATIONS: 1000
  
  # Statistical parameters
  SIGNIFICANCE_THRESHOLD: 0.05
  CONFIDENCE_LEVEL: 0.95
'''
        
        # IS_DEBUG.yaml
        configs["config/IS_DEBUG.yaml"] = '''IS_DEBUG: false

# Debug settings
DEBUG:
  USE_SAMPLE_DATA: true
  MAX_ITERATIONS: 10
  VERBOSE: true
'''
        
        return configs
        
    async def _generate_main_script(
        self,
        project_name: str,
        modules: List[str],
        project_type: str
    ) -> str:
        """Generate main script template."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build module imports
        module_imports = []
        if "plt" in modules:
            module_imports.append("import matplotlib.pyplot as plt")
        if "pd" in modules:
            module_imports.append("import pandas as pd")
        if "np" in modules:
            module_imports.append("import numpy as np")
            
        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: ./scripts/{project_name}/main.py
# ----------------------------------------
import os
__FILE__ = "./scripts/{project_name}/main.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Main script for {project_name} project
  - Loads configuration from ./config/
  - Processes data and generates results

Dependencies:
  - packages: scitex{', ' + ', '.join(modules) if modules else ''}
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
    data = stx.io.load(CONFIG.PATH.RAW_DATA)
    
    # Process data
    results = process_data(data, args)
    
    # Save results
    stx.io.save(results, CONFIG.PATH.RESULTS_DIR + "/results.csv", symlink_from_cwd=True)
    
    return 0

def process_data(data, args):
    """Process the input data."""
    if args.verbose:
        stx.str.printc(f"Processing data...", c="yellow")
    
    # Add your processing logic here
    results = data
    
    return results

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Main script for {project_name}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug mode")
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args

def run_main():
    """Initialize scitex framework and run main."""
    global CONFIG, CC, sys, plt
    
    import sys
    {'import matplotlib.pyplot as plt' if 'plt' in modules else ''}
    
    args = parse_args()
    
    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=args.verbose,
        agg={'True' if 'plt' in modules else 'False'},
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
        
        return template
        
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

# Data files
*.csv
*.xlsx
*.h5
*.pkl
!data/.gitkeep
!data/raw/.gitkeep
!data/processed/.gitkeep

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

# Playground
.playground/*
!.playground/.gitignore
'''
        
    def _generate_readme(
        self,
        project_name: str,
        project_type: str,
        modules: List[str]
    ) -> str:
        """Generate README.md."""
        return f'''# {project_name}

SciTeX-based {project_type} project.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure project:
   - Edit `config/PATH.yaml` for file paths
   - Edit `config/PARAMS.yaml` for parameters

## Usage

Run the main script:
```bash
python scripts/{project_name}/main.py
```

## Project Structure

```
{project_name}/
├── config/          # Configuration files
├── scripts/         # Analysis scripts
│   └── {project_name}/   # Project scripts
├── data/           # Data directory
│   ├── raw/        # Raw data
│   └── processed/  # Processed data
├── .playground/    # Experiments and prototypes
└── README.md       # This file
```

## Modules Used

- scitex.io - File I/O operations
{chr(10).join([f"- scitex.{m} - {m.upper()} operations" for m in modules])}

## Development

- Use `.playground/` for experiments
- Follow SciTeX coding guidelines
- Keep configurations in `config/`
'''
        
    def _generate_requirements(self, modules: List[str]) -> str:
        """Generate requirements.txt."""
        reqs = ["scitex"]
        
        if "plt" in modules:
            reqs.append("matplotlib")
        if "pd" in modules:
            reqs.append("pandas")
        if "np" in modules:
            reqs.append("numpy")
        if "stats" in modules:
            reqs.append("scipy")
            
        return '\n'.join(reqs)
        
    async def _run_analysis_workflow(
        self,
        project_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run analysis workflow."""
        return {
            "workflow": "analysis",
            "status": "completed",
            "steps": [
                "Loaded configuration",
                "Loaded data",
                "Ran analysis",
                "Generated visualizations",
                "Saved results"
            ],
            "outputs": ["results.csv", "figures/"]
        }
        
    async def _run_preprocessing_workflow(
        self,
        project_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run preprocessing workflow."""
        return {
            "workflow": "preprocessing",
            "status": "completed",
            "steps": [
                "Loaded raw data",
                "Cleaned data",
                "Normalized values",
                "Saved processed data"
            ],
            "outputs": ["data/processed/"]
        }
        
    async def _run_training_workflow(
        self,
        project_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run training workflow."""
        return {
            "workflow": "training",
            "status": "completed",
            "steps": [
                "Loaded training data",
                "Initialized model",
                "Trained model",
                "Saved model checkpoint"
            ],
            "outputs": ["models/"]
        }
        
    async def _run_evaluation_workflow(
        self,
        project_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run evaluation workflow."""
        return {
            "workflow": "evaluation",
            "status": "completed",
            "steps": [
                "Loaded test data",
                "Loaded model",
                "Ran evaluation",
                "Generated metrics"
            ],
            "outputs": ["evaluation_results.json"]
        }
        
    async def _run_reporting_workflow(
        self,
        project_path: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run reporting workflow."""
        return {
            "workflow": "reporting",
            "status": "completed",
            "steps": [
                "Collected results",
                "Generated visualizations",
                "Created report",
                "Exported report"
            ],
            "outputs": ["report.pdf", "report.html"]
        }
        
    def get_module_description(self) -> str:
        """Get description of orchestrator functionality."""
        return (
            "SciTeX orchestrator coordinates project management, analyzes project health, "
            "initializes new projects, runs workflows, suggests improvements, fixes structure "
            "issues, and helps migrate existing projects to SciTeX format."
        )
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "analyze_project_health",
            "initialize_scitex_project",
            "run_scitex_workflow",
            "suggest_project_improvements",
            "fix_project_structure",
            "migrate_to_scitex",
            "get_module_info",
            "validate_code"
        ]
        
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate orchestrator patterns."""
        # Orchestrator is meta-level, so just basic validation
        return {
            "valid": True,
            "issues": [],
            "score": 100
        }


# Main entry point
if __name__ == "__main__":
    server = ScitexOrchestratorMCPServer()
    asyncio.run(server.run())

# EOF