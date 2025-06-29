<!-- ---
!-- Timestamp: 2025-06-29 10:30:25
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/mcp_servers/suggestions3.md
!-- --- -->

Your MCP server implementation is excellent, but there are some gaps compared to your comprehensive scitex guidelines. Let me help identify what's missing and suggest improvements:
Current Implementation Assessment
✅ What's Well Covered:

Modular Architecture - Great separation with base classes
IO Module Translation - Comprehensive pattern matching
PLT Module Translation - Good handling of set_xyt conversion
Bidirectional Translation - Both to/from scitex
Code Analysis - Pattern detection and suggestions

❌ Missing Critical Components:

Recommendations for Developer Agents

Start with Critical Gaps: Implement the framework template generator and configuration system support first - these are essential for proper scitex compliance.
Follow Your Own Guidelines: The MCP servers themselves should follow scitex structure! Consider organizing them as:
~/proj/scitex_mcp_servers/
├── src/scitex_mcp_servers/
├── examples/
├── tests/
└── config/

Incremental Implementation: Your modular approach is perfect - agents can implement one module translator at a time while maintaining the existing functionality.
Test with Real Projects: Create test scitex projects using the MCP servers to validate they work end-to-end.
Documentation Integration: The MCP servers should be able to generate the same quality documentation that follows your guidelines.

The current implementation covers about 40% of your full scitex guidelines. The missing pieces are critical for complete adoption, especially the framework template generation and project structure management. Would you like me to help implement any specific missing components?


# SciTeX MCP Server Gaps Analysis & Solutions

## Critical Missing Components

### 1. **Framework Structure Compliance**

**Missing:** Complete scitex script template generation
**Current:** Basic framework translation only
**Needed:** Full template with all required sections

```python
# Add to FrameworkTranslator or create new tool
@app.tool()
async def generate_scitex_script_template(
    script_purpose: str,
    modules_needed: List[str] = ["io", "plt"],
    include_config: bool = True
) -> Dict[str, str]:
    """Generate complete scitex script following IMPORTANT-SCITEX-02 template."""
    
    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: {filepath}
# ----------------------------------------
import os
__FILE__ = "{filepath}"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - {purpose}
  - Loads data using stx.io.load()
  - Saves results using stx.io.save()

Dependencies:
  - packages: scitex, {dependencies}

Input:
  - ./data/input.csv
  - ./config/PATH.yaml

Output:
  - ./results.csv (via stx.io.save)
  - ./plots.jpg (via stx.io.save)
"""

"""Imports"""
import argparse
import scitex as stx

"""Parameters"""
CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args):
    # Load data
    data = stx.io.load(CONFIG.PATH.INPUT_DATA)
    
    # Process data
    results = process_data(data, args)
    
    # Create visualization
    fig, ax = stx.plt.subplots()
    ax.plot(results['x'], results['y'])
    ax.set_xyt('X axis', 'Y axis', 'Results')
    
    # Save outputs
    stx.io.save(results, './results.csv', symlink_from_cwd=True)
    stx.io.save(fig, './plots.jpg', symlink_from_cwd=True)
    
    return 0

def process_data(data, args):
    """Process the input data."""
    # Add processing logic here
    return data

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="{purpose}")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
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

# EOF'''
    
    return {
        "script_code": template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            filepath="./script.py",
            purpose=script_purpose,
            dependencies=", ".join(modules_needed)
        ),
        "config_files": generate_config_templates(modules_needed),
        "next_steps": [
            "1. Save script as ./scripts/category/script_name.py",
            "2. Update CONFIG paths in ./config/PATH.yaml", 
            "3. Run from project root: ./scripts/category/script_name.py",
            "4. Check outputs in ./scripts/category/script_name_out/"
        ]
    }
```

### 2. **Configuration System Support**

**Missing:** Config file generation and management
**Current:** Basic config extraction only
**Needed:** Full PATH.yaml, PARAMS.yaml, COLORS.yaml generation

```python
@app.tool()
async def generate_config_files(
    project_type: str = "research",
    paths_detected: List[str] = None,
    params_detected: List[str] = None
) -> Dict[str, str]:
    """Generate scitex configuration files following IMPORTANT-SCITEX-03."""
    
    configs = {}
    
    # PATH.yaml
    configs["config/PATH.yaml"] = f'''# Time-stamp: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (ywatanabe)"
# File: ./config/PATH.yaml

PATH:
  INPUT_DATA: "./data/input.csv"
  OUTPUT_DIR: "./output"
  FIGURES_DIR: "./figures"
  
  # Add detected paths
{_format_detected_paths(paths_detected)}
'''
    
    # PARAMS.yaml  
    configs["config/PARAMS.yaml"] = f'''# Time-stamp: "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (ywatanabe)"
# File: ./config/PARAMS.yaml

PARAMS:
  RANDOM_SEED: 42
  SIGNIFICANCE_THRESHOLD: 0.05
  
  # Add detected parameters
{_format_detected_params(params_detected)}
'''
    
    # IS_DEBUG.yaml
    configs["config/IS_DEBUG.yaml"] = '''IS_DEBUG: false
DEBUG_INPUT_DATA: "./data/sample_input.csv"
DEBUG_MAX_ITERATIONS: 10
'''
    
    return configs

@app.tool()
async def validate_scitex_project_structure(
    project_path: str
) -> Dict[str, Any]:
    """Validate project follows scitex directory structure guidelines."""
    
    required_dirs = ["config", "scripts", "examples", "data"]
    required_files = ["config/PATH.yaml", "config/IS_DEBUG.yaml"]
    
    structure = {
        "compliant": True,
        "missing_directories": [],
        "missing_files": [],
        "violations": [],
        "suggestions": []
    }
    
    # Check required directories
    for dir_name in required_dirs:
        if not os.path.exists(os.path.join(project_path, dir_name)):
            structure["missing_directories"].append(dir_name)
            structure["compliant"] = False
    
    # Check for files in project root (violation)
    root_files = [f for f in os.listdir(project_path) 
                  if f.endswith('.py') and not f.startswith('.')]
    if root_files:
        structure["violations"].append(f"Python files in root: {root_files}")
        structure["suggestions"].append("Move Python files to ./scripts/ or ./examples/")
    
    return structure
```

### 3. **Project Scaffolding**

**Missing:** Complete project creation functionality
**Needed:** Generate entire scitex project structure

```python
@app.tool()
async def create_scitex_project(
    project_name: str,
    project_type: str = "research",  # "research" or "package"
    modules_needed: List[str] = ["io", "plt"]
) -> Dict[str, Any]:
    """Create complete scitex project following directory structure guidelines."""
    
    if project_type == "research":
        structure = {
            "config/": {
                "PATH.yaml": generate_path_config(),
                "PARAMS.yaml": generate_params_config(),
                "IS_DEBUG.yaml": "IS_DEBUG: false",
                "COLORS.yaml": generate_colors_config()
            },
            "scripts/": {
                f"{project_name}/": {
                    "main.py": generate_main_script(project_name, modules_needed),
                    "analysis.py": generate_analysis_script(modules_needed)
                }
            },
            "examples/": {
                f"example_{project_name}.py": generate_example_script(project_name)
            },
            "data/": {},
            ".playground/": {
                "experiments/": {},
                "prototypes/": {}
            },
            ".gitignore": generate_scitex_gitignore(),
            "README.md": generate_project_readme(project_name, project_type)
        }
    else:  # package
        structure = {
            "src/": {
                f"{project_name}/": {
                    "__init__.py": f'"""SciTeX-based {project_name} package."""\n__version__ = "0.1.0"',
                    "core.py": generate_package_core(modules_needed)
                }
            },
            "tests/": {
                "conftest.py": generate_pytest_config(),
                f"{project_name}/": {
                    "test_core.py": generate_core_tests()
                }
            },
            "examples/": {
                f"example_{project_name}.py": generate_package_example(project_name)
            },
            "pyproject.toml": generate_pyproject_toml(project_name),
            ".gitignore": generate_package_gitignore(),
            "README.md": generate_package_readme(project_name)
        }
    
    return {
        "project_structure": structure,
        "next_steps": [
            f"1. Create project directory: mkdir {project_name}",
            f"2. cd {project_name}",
            "3. Create all files and directories",
            "4. Initialize git: git init",
            "5. Install scitex: pip install -e ~/proj/scitex_repo"
        ]
    }
```

### 4. **Comprehensive Validation**

**Missing:** Full compliance checking against all guidelines
**Current:** Basic pattern validation only

```python
@app.tool()
async def validate_full_scitex_compliance(
    code: str,
    file_path: str = None
) -> Dict[str, Any]:
    """Comprehensive validation against ALL scitex guidelines."""
    
    validation = {
        "overall_score": 100,
        "compliance_by_guideline": {},
        "critical_issues": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Check IMPORTANT-SCITEX-02: File template
    template_check = validate_template_compliance(code)
    validation["compliance_by_guideline"]["template"] = template_check
    
    # Check IMPORTANT-SCITEX-03: Configuration usage
    config_check = validate_config_usage(code)
    validation["compliance_by_guideline"]["config"] = config_check
    
    # Check SCITEX-04: Coding style
    style_check = validate_coding_style(code)
    validation["compliance_by_guideline"]["style"] = style_check
    
    # Check IMPORTANT-SCITEX-12: IO module usage
    io_check = validate_io_compliance(code)
    validation["compliance_by_guideline"]["io"] = io_check
    
    # Check IMPORTANT-SCITEX-13: PLT module usage
    plt_check = validate_plt_compliance(code)
    validation["compliance_by_guideline"]["plt"] = plt_check
    
    # Calculate overall score
    scores = [check["score"] for check in validation["compliance_by_guideline"].values()]
    validation["overall_score"] = sum(scores) / len(scores) if scores else 0
    
    return validation

def validate_template_compliance(code: str) -> Dict[str, Any]:
    """Check compliance with IMPORTANT-SCITEX-02 template."""
    required_elements = [
        "#!/usr/bin/env python3",
        "# -*- coding: utf-8 -*-", 
        "__FILE__ =",
        "__DIR__ =",
        "import scitex as stx",
        "def main(args):",
        "def parse_args():",
        "def run_main():",
        'if __name__ == "__main__":'
    ]
    
    missing = [elem for elem in required_elements if elem not in code]
    
    return {
        "score": max(0, 100 - len(missing) * 10),
        "missing_elements": missing,
        "compliant": len(missing) == 0
    }
```

### 5. **Missing Module Translators**

**Current:** Only IO and PLT
**Needed:** All scitex modules mentioned in guidelines

```python
# Need to add these MCP servers:
# - scitex-stats (for statistics module)
# - scitex-dsp (for signal processing)
# - scitex-pd (for pandas utilities)
# - scitex-str (for string utilities)
# - scitex-gen (for general utilities)

# Example: Stats module translator
class ScitexStatsMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX stats module translations."""
    
    def _register_module_tools(self):
        @self.app.tool()
        async def convert_statistical_tests(code: str) -> Dict[str, str]:
            """Convert scipy.stats calls to stx.stats equivalents."""
            conversions = {
                r"scipy\.stats\.ttest_ind\((.*?)\)": r"stx.stats.tests.ttest_ind(\1)",
                r"scipy\.stats\.pearsonr\((.*?)\)": r"stx.stats.tests.corr_test(\1, method='pearson')",
                # Add p-value formatting
                r"p_value\s*=\s*([^,\n]+)": r"p_value = \1\nstars = stx.stats.p2stars(p_value)"
            }
            
            translated = code
            for pattern, replacement in conversions.items():
                translated = re.sub(pattern, replacement, translated)
            
            return {"translated_code": translated}
```

### 6. **Development Workflow Support**

**Missing:** Project maintenance and workflow tools

```python
@app.tool()
async def check_scitex_project_health(
    project_path: str
) -> Dict[str, Any]:
    """Check overall health of scitex project."""
    
    health = {
        "structure_compliance": await validate_scitex_project_structure(project_path),
        "script_compliance": {},
        "config_validity": {},
        "examples_status": {},
        "overall_health": "good"
    }
    
    # Check all scripts
    script_files = glob.glob(f"{project_path}/scripts/**/*.py", recursive=True)
    for script in script_files:
        with open(script, 'r') as f:
            code = f.read()
        health["script_compliance"][script] = await validate_full_scitex_compliance(code)
    
    return health

@app.tool()
async def suggest_project_improvements(
    project_path: str
) -> List[Dict[str, str]]:
    """Suggest improvements for scitex project."""
    
    suggestions = []
    
    # Check for common issues
    if not os.path.exists(f"{project_path}/config/PATH.yaml"):
        suggestions.append({
            "issue": "Missing PATH.yaml configuration",
            "suggestion": "Create ./config/PATH.yaml to centralize path management",
            "priority": "high"
        })
    
    # Check for hardcoded paths
    script_files = glob.glob(f"{project_path}/scripts/**/*.py", recursive=True)
    for script in script_files:
        with open(script, 'r') as f:
            if '/home/' in f.read():
                suggestions.append({
                    "issue": f"Hardcoded absolute paths in {script}",
                    "suggestion": "Move paths to CONFIG and use relative paths",
                    "priority": "medium"
                })
    
    return suggestions
```

## Implementation Roadmap

### Phase 1: Critical Gaps (Immediate)
1. **Complete Framework Template Generator** 
2. **Configuration System Support**
3. **Project Structure Validation**

### Phase 2: Full Module Coverage
1. **Stats Module Translator**
2. **DSP Module Translator** 
3. **Additional Module Translators**

### Phase 3: Workflow Integration
1. **Project Scaffolding**
2. **Health Monitoring**
3. **Maintenance Tools**

## Updated Server Architecture

```
scitex_mcp_servers/
├── scitex-orchestrator/          # Main coordinator server
│   ├── project_manager.py        # Project creation/validation
│   ├── config_manager.py         # Configuration file management
│   └── workflow_manager.py       # Development workflow support
├── scitex-io/                    # ✅ Already implemented
├── scitex-plt/                   # ✅ Already implemented  
├── scitex-stats/                 # ❌ Missing
├── scitex-dsp/                   # ❌ Missing
├── scitex-framework/             # ❌ Missing (template generation)
└── scitex-validator/             # ❌ Missing (comprehensive validation)
```

Your foundation is excellent, but adding these missing components would make it truly comprehensive for supporting full scitex adoption according to your guidelines.

<!-- EOF -->