<!-- ---
!-- Timestamp: 2025-06-29 10:26:25
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/mcp_servers/suggestions2.md
!-- --- -->

# Enhanced SciTeX MCP Server for Developer Agents

## Beyond Translation: Comprehensive Developer Support

### 1. **Code Understanding & Analysis**

```python
@app.tool()
async def analyze_scitex_project(
    project_path: str,
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """Analyze an entire scitex project for patterns, issues, and improvements."""
    
    return {
        "project_structure": {
            "compliant_files": [...],
            "non_compliant_files": [...],
            "missing_directories": [...],
            "config_files": {...},
        },
        "code_patterns": {
            "common_patterns": [...],
            "anti_patterns": [...],
            "inconsistencies": [...],
        },
        "dependencies": {
            "scitex_modules_used": [...],
            "external_dependencies": [...],
            "version_conflicts": [...],
        },
        "recommendations": [
            "Consider extracting common paths to PATH.yaml",
            "Multiple scripts could share configuration",
            "Some hardcoded parameters should be configurable",
        ]
    }

@app.tool()
async def explain_scitex_pattern(
    code_snippet: str,
    pattern_type: str = "auto_detect"
) -> Dict[str, Any]:
    """Explain scitex patterns in code for learning purposes."""
    
    return {
        "pattern_name": "scitex_io_save_pattern",
        "explanation": "This uses scitex's unified save function...",
        "benefits": [
            "Automatic directory creation",
            "Consistent file handling across formats",
            "Built-in symlink support for CWD access",
        ],
        "related_patterns": [...],
        "common_mistakes": [...],
        "best_practices": [...],
    }

@app.tool()
async def suggest_scitex_improvements(
    code: str,
    context: str = "research_script"
) -> List[Dict[str, Any]]:
    """Suggest specific scitex improvements for code."""
    
    return [
        {
            "type": "performance",
            "suggestion": "Use stx.io.cache for expensive computations",
            "code_location": "line 45-67",
            "current_code": "# expensive computation repeated",
            "improved_code": "result = stx.io.cache('computation_id', 'result')",
            "impact": "Reduces runtime from 5min to 30sec on subsequent runs",
        },
        {
            "type": "reproducibility", 
            "suggestion": "Extract magic numbers to config",
            "code_location": "line 23",
            "current_code": "threshold = 0.05",
            "improved_code": "threshold = CONFIG.PARAMS.SIGNIFICANCE_THRESHOLD",
            "impact": "Makes threshold configurable across experiments",
        },
    ]
```

### 2. **Project Generation & Scaffolding**

```python
@app.tool()
async def create_scitex_project(
    project_name: str,
    project_type: str,  # "research", "package", "analysis"
    modules_needed: List[str] = ["io", "plt", "stats"],
    include_examples: bool = True,
) -> Dict[str, Any]:
    """Generate a complete scitex project structure."""
    
    return {
        "files_created": {
            "config/": {
                "PATH.yaml": "# Generated path configurations",
                "PARAMS.yaml": "# Generated parameter configurations", 
                "IS_DEBUG.yaml": "IS_DEBUG: false",
            },
            "scripts/": {
                f"{project_name}/": {
                    "main.py": "# Generated main script with scitex template",
                    "analysis.py": "# Generated analysis script",
                }
            },
            "examples/": {
                f"example_{project_name}.py": "# Generated example script",
            },
            ".gitignore": "# Scitex-specific gitignore",
            "README.md": "# Generated with scitex usage instructions",
            "requirements.txt": "# Dependencies including scitex",
        },
        "next_steps": [
            "Edit config/PATH.yaml with your data paths",
            "Run ./examples/example_project.py to test setup",
            "Customize scripts/main.py for your analysis",
        ]
    }

@app.tool()
async def generate_scitex_script(
    script_purpose: str,
    input_data_types: List[str],  # ["csv", "npy", "images"]
    output_types: List[str],     # ["plots", "tables", "models"]
    analysis_type: str = "exploratory",
) -> Dict[str, str]:
    """Generate a complete scitex script template."""
    
    return {
        "script_code": "# Complete generated scitex script",
        "config_yaml": "# Generated configuration",
        "example_usage": "# How to run and customize the script",
        "documentation": "# Explanation of the generated code",
    }
```

### 3. **Configuration Management**

```python
@app.tool()
async def optimize_scitex_config(
    project_path: str,
    merge_similar: bool = True,
) -> Dict[str, Any]:
    """Optimize scitex configuration files across project."""
    
    return {
        "current_configs": {
            "scripts/analysis1/config/PATH.yaml": {...},
            "scripts/analysis2/config/PATH.yaml": {...},
        },
        "optimized_config": {
            "config/PATH.yaml": {
                "# Merged and organized paths": "...",
            },
        },
        "changes_needed": [
            {
                "file": "scripts/analysis1/main.py",
                "change": "Update CONFIG.PATH.DATA reference",
                "old": "CONFIG.PATH.LOCAL_DATA", 
                "new": "CONFIG.PATH.SHARED_DATA",
            }
        ],
        "benefits": [
            "Reduced configuration duplication",
            "Centralized path management",
            "Easier to maintain across scripts",
        ]
    }

@app.tool()
async def validate_scitex_config(
    config_path: str,
    check_file_existence: bool = True,
) -> Dict[str, Any]:
    """Validate scitex configuration files."""
    
    return {
        "config_validity": {
            "syntax_valid": True,
            "structure_valid": True,
            "references_valid": False,
        },
        "issues": [
            {
                "type": "missing_file",
                "config_key": "PATH.TRAINING_DATA",
                "config_value": "./data/training.csv",
                "issue": "File does not exist",
                "suggestion": "Create file or update path",
            }
        ],
        "suggestions": [
            "Consider using f-strings for dynamic paths",
            "Add DEBUG versions of expensive-to-compute paths",
        ]
    }
```

### 4. **Development Workflow Support**

```python
@app.tool()
async def run_scitex_pipeline(
    scripts: List[str],
    dry_run: bool = False,
    parallel: bool = False,
) -> Dict[str, Any]:
    """Execute scitex scripts with proper dependency management."""
    
    return {
        "execution_plan": [
            {"script": "data_preparation.py", "estimated_time": "2min"},
            {"script": "analysis.py", "estimated_time": "15min", "depends_on": ["data_preparation.py"]},
            {"script": "visualization.py", "estimated_time": "5min", "depends_on": ["analysis.py"]},
        ],
        "results": {
            "data_preparation.py": {"status": "success", "runtime": "1.8min", "outputs": [...]},
            "analysis.py": {"status": "success", "runtime": "12.3min", "outputs": [...]},
        },
        "summary": {
            "total_runtime": "19.1min",
            "files_created": 15,
            "total_output_size": "2.3GB",
        }
    }

@app.tool()
async def debug_scitex_script(
    script_path: str,
    error_log: str = None,
) -> Dict[str, Any]:
    """Help debug scitex script issues."""
    
    return {
        "common_issues": [
            {
                "issue": "ModuleNotFoundError: scitex",
                "solution": "Install scitex: pip install -e ~/proj/scitex_repo",
                "prevention": "Add scitex to requirements.txt",
            }
        ],
        "code_issues": [
            {
                "line": 45,
                "issue": "Using absolute path in save operation",
                "current": "stx.io.save(data, '/home/user/results.csv')",
                "fixed": "stx.io.save(data, './results.csv')",
                "explanation": "Scitex expects relative paths for reproducibility",
            }
        ],
        "suggestions": [
            "Add CONFIG validation at script start",
            "Use stx.io.cache for expensive operations",
            "Add progress indicators for long-running operations",
        ]
    }
```

### 5. **Learning & Documentation**

```python
@app.tool()
async def explain_scitex_concept(
    concept: str,  # "io_save_behavior", "config_system", "framework_structure"
    detail_level: str = "intermediate",
) -> Dict[str, Any]:
    """Explain scitex concepts with examples."""
    
    return {
        "concept": "scitex_io_save_behavior",
        "summary": "Scitex save function creates script-relative output directories...",
        "detailed_explanation": "When you call stx.io.save() from /path/to/script.py...",
        "examples": [
            {
                "scenario": "Saving from script.py",
                "code": "stx.io.save(data, './results.csv')",
                "result": "Creates /path/to/script_out/results.csv",
                "explanation": "Script-relative output directory",
            }
        ],
        "common_confusion": [
            "Why not save to current working directory?",
            "How does symlink_from_cwd work?",
        ],
        "best_practices": [...],
        "related_concepts": ["config_system", "path_management"],
    }

@app.tool()
async def generate_scitex_documentation(
    project_path: str,
    doc_type: str = "usage_guide",  # "api_docs", "usage_guide", "troubleshooting"
) -> Dict[str, str]:
    """Generate project-specific scitex documentation."""
    
    return {
        "README.md": "# Generated project README with scitex usage",
        "docs/USAGE.md": "# How to use this scitex project",
        "docs/CONFIG.md": "# Configuration file documentation",
        "docs/TROUBLESHOOTING.md": "# Common issues and solutions",
    }
```

### 6. **Quality Assurance & Testing**

```python
@app.tool()
async def generate_scitex_tests(
    script_path: str,
    test_type: str = "integration",  # "unit", "integration", "end_to_end"
) -> Dict[str, str]:
    """Generate appropriate tests for scitex scripts."""
    
    return {
        "test_script.py": "# Generated pytest test file",
        "test_data/": {
            "sample_input.csv": "# Generated test data",
            "expected_output.csv": "# Expected results",
        },
        "conftest.py": "# Pytest configuration for scitex",
        "run_tests.sh": "# Script to run all tests",
    }

@app.tool()
async def benchmark_scitex_performance(
    script_path: str,
    baseline_version: str = None,
) -> Dict[str, Any]:
    """Benchmark scitex script performance."""
    
    return {
        "performance_metrics": {
            "total_runtime": "2.3min",
            "memory_peak": "1.2GB",
            "io_operations": 45,
            "plots_generated": 12,
        },
        "bottlenecks": [
            {
                "location": "data loading (line 23)",
                "time_spent": "45%",
                "suggestion": "Consider using stx.io.cache",
            }
        ],
        "optimization_suggestions": [
            "Use vectorized operations instead of loops",
            "Cache intermediate results",
            "Reduce plot resolution for draft mode",
        ]
    }
```

### 7. **Migration & Maintenance**

```python
@app.tool()
async def migrate_to_latest_scitex(
    project_path: str,
    current_version: str,
    target_version: str = "latest",
) -> Dict[str, Any]:
    """Help migrate project to newer scitex version."""
    
    return {
        "breaking_changes": [
            {
                "change": "stx.plt.subplots API updated",
                "impact": "3 files need updating",
                "migration_script": "# Auto-generated migration code",
            }
        ],
        "new_features": [
            {
                "feature": "stx.io.cache improvements",
                "benefit": "Better caching performance",
                "adoption_suggestion": "Consider using in analysis.py",
            }
        ],
        "migration_plan": [
            "Update requirements.txt",
            "Run migration scripts",
            "Test all scripts",
            "Update documentation",
        ]
    }

@app.tool()
async def refactor_for_scitex_best_practices(
    code: str,
    focus_areas: List[str] = ["performance", "maintainability", "reproducibility"],
) -> Dict[str, Any]:
    """Suggest comprehensive refactoring for scitex best practices."""
    
    return {
        "refactoring_suggestions": [
            {
                "category": "reproducibility",
                "current_issue": "Hardcoded random seeds",
                "solution": "Use CONFIG.PARAMS.RANDOM_SEED",
                "impact": "Ensures reproducible results",
                "effort": "low",
            }
        ],
        "architectural_improvements": [
            "Split monolithic script into focused modules",
            "Extract common utilities to shared functions",
            "Implement proper error handling",
        ],
        "code_quality_metrics": {
            "before": {"complexity": 8.2, "maintainability": "C"},
            "after": {"complexity": 4.1, "maintainability": "A"},
        }
    }
```

## Why These Features Matter for Developer Agents

1. **Learning Support** - Agents can understand scitex patterns and explain them to users
2. **Project Management** - Agents can scaffold, organize, and maintain entire projects
3. **Quality Assurance** - Agents can ensure code quality and catch issues early
4. **Workflow Integration** - Agents can execute complex multi-script pipelines
5. **Knowledge Base** - Agents become scitex experts, not just translators
6. **Maintenance Helper** - Agents can help keep projects up-to-date and optimized

This comprehensive approach makes the MCP server a **development partner** rather than just a translation tool. Developer agents become much more effective at helping researchers adopt and maintain scitex-based workflows.

<!-- EOF -->