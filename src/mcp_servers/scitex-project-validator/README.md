# SciTeX Project Validator MCP Server

This MCP server validates SciTeX project structures for both individual scientific projects and pip packages, ensuring compliance with SciTeX guidelines.

## Available Tools

### 1. `check_scitex_project_structure_for_scientific_project`

Validates individual scientific projects using SciTeX.

**Parameters:**
- `project_path` (str): Path to the scientific project to validate

**Validates:**
- Required directory structure: `config/`, `data/`, `scripts/`, `examples/`, `tests/`, `.playground/`
- No forbidden directories in project root
- SciTeX-compliant script format in `scripts/`
- Proper configuration files (`config/PATH.yaml`)
- Data organization with symlinks
- Log management via `stx.gen.start()` and `stx.gen.close()`

### 2. `check_scitex_project_structure_for_pip_package`

Validates pip package projects for SciTeX integration.

**Parameters:**
- `package_path` (str): Path to the pip package project to validate

**Validates:**
- Modern Python package structure (src-layout preferred)
- Package configuration (`setup.cfg`, `pyproject.toml`)
- Testing infrastructure with pytest
- Documentation (`README.md`, `docs/`)
- CI/CD setup
- SciTeX integration in examples
- Dependency management
- Code quality tools

## Usage Examples

### Scientific Project Validation

```python
# Check a research project
result = await check_scitex_project_structure_for_scientific_project(
    "/path/to/my/research/project"
)

print(f"Compliance: {result['compliance_level']}")
print(f"Score: {result['structure_score']}")
for issue in result['issues']:
    print(f"Issue: {issue}")
for suggestion in result['suggestions']:
    print(f"Suggestion: {suggestion}")
```

### Pip Package Validation

```python
# Check a package under development
result = await check_scitex_project_structure_for_pip_package(
    "/path/to/my/package"
)

print(f"Package type: {result['package_type']}")
print(f"SciTeX integration: {result['scitex_integration']['integration_level']}")
for step in result['next_steps']:
    print(f"Next: {step}")
```

## Expected Project Structures

### Scientific Project Structure

```
research-project/
├── config/
│   └── PATH.yaml          # Required path configuration
├── data/                  # Centralized data with symlinks
│   └── category/
│       └── file.ext -> ../../scripts/script_out/file.ext
├── scripts/               # SciTeX-formatted scripts
│   └── category/
│       ├── analysis.py    # Must follow SciTeX template
│       └── analysis_out/  # Auto-generated outputs
│           ├── data/
│           └── logs/      # RUNNING, FINISHED_SUCCESS, FINISHED_FAILURE
├── examples/              # Example usage
├── tests/                 # Test files
└── .playground/           # Temporary workspace
    └── category/
```

### Pip Package Structure

```
my-package/
├── src/my_package/        # src-layout (preferred)
├── tests/                 # Comprehensive test suite
├── examples/              # SciTeX-formatted examples (required)
├── docs/                  # Documentation
├── setup.cfg              # Package configuration
├── pyproject.toml         # Modern configuration
├── README.md              # Documentation
├── .pre-commit-config.yaml # Code quality
└── .github/workflows/     # CI/CD
```

## Compliance Levels

- **Excellent** (90%+): Project fully compliant with SciTeX guidelines
- **Good** (70-89%): Minor issues, mostly compliant
- **Fair** (50-69%): Several issues need addressing
- **Needs Improvement** (<50%): Major structural problems

## Installation

1. Install dependencies:
   ```bash
   pip install -e /path/to/scitex-repo
   ```

2. Run the server:
   ```bash
   python server.py
   ```

3. Connect via MCP client to use validation tools

## Key SciTeX Requirements

### For All Projects

1. **Scripts must use SciTeX format** with mandatory template
2. **Proper directory structure** - no arbitrary directories in root
3. **Configuration management** via YAML files
4. **Logging and reproducibility** via `stx.gen.start()` and `stx.gen.close()`

### For Scientific Projects

- Centralized data management with symlinks
- Organized script outputs with log tracking
- Temporal workspace in `.playground/`

### For Pip Packages

- Examples directory with SciTeX-formatted scripts
- Modern packaging practices (src-layout)
- Comprehensive testing and documentation
- Optional but recommended SciTeX dependency

This validator ensures your projects follow SciTeX best practices for reproducible scientific computing.