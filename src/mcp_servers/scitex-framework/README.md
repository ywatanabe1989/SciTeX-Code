# SciTeX Framework MCP Server

Complete framework support for SciTeX projects - template generation, project scaffolding, and structure validation.

## Features

### 1. Script Template Generation
Generate complete SciTeX-compliant scripts following IMPORTANT-SCITEX-02:
- Full framework boilerplate
- Proper imports and structure
- CONFIG integration
- Main/parse_args/run_main pattern

### 2. Configuration Management
Generate and manage SciTeX configuration files:
- PATH.yaml - Centralized path management
- PARAMS.yaml - Experiment parameters
- IS_DEBUG.yaml - Debug settings
- COLORS.yaml - Visualization colors

### 3. Project Scaffolding
Create complete SciTeX project structures:
- Research projects with proper directories
- Package projects with src layout
- All required configuration files
- Examples and documentation

### 4. Structure Validation
Validate projects follow SciTeX guidelines:
- Directory structure compliance
- No files in project root
- Required configurations present
- Scoring and recommendations

## Available Tools

### generate_scitex_script_template
Generate a complete SciTeX script template:
```python
template = await generate_scitex_script_template(
    script_purpose="Analyze experimental data",
    modules_needed=["io", "plt", "pd"],
    include_config=True,
    script_name="./scripts/analysis/main.py"
)
```

### generate_config_files
Generate configuration files:
```python
configs = await generate_config_files(
    project_type="research",
    detected_paths=["./data/raw.csv", "./models/trained.pkl"],
    detected_params={"THRESHOLD": 0.05, "N_EPOCHS": 100}
)
```

### create_scitex_project
Create a complete project structure:
```python
project = await create_scitex_project(
    project_name="my_research",
    project_type="research",
    modules_needed=["io", "plt", "stats"],
    include_examples=True
)
```

### validate_project_structure
Validate existing project:
```python
validation = await validate_project_structure("/path/to/project")
# Returns compliance score, issues, and recommendations
```

## Installation

```bash
cd mcp_servers/scitex-framework
pip install -e .
```

## Usage

### Standalone
```bash
python server.py
```

### With MCP Client
```json
{
  "mcpServers": {
    "scitex-framework": {
      "command": "python",
      "args": ["-m", "scitex_framework.server"],
      "cwd": "/path/to/mcp_servers/scitex-framework"
    }
  }
}
```

## Template Example

The generated scripts include:
- Complete header with timestamp and file info
- Docstring with functionalities and dependencies
- Proper imports organized by section
- CONFIG loading
- Main function with argument handling
- Framework initialization and cleanup
- Full scitex.gen.start/close integration

## Project Structure Example

```
my_research/
├── config/
│   ├── PATH.yaml
│   ├── PARAMS.yaml
│   ├── IS_DEBUG.yaml
│   └── COLORS.yaml
├── scripts/
│   └── my_research/
│       ├── __init__.py
│       ├── main.py
│       └── analysis.py
├── data/
│   └── .gitkeep
├── examples/
│   └── example_my_research.py
├── .playground/
│   ├── .gitignore
│   ├── experiments/
│   └── prototypes/
├── .gitignore
├── README.md
└── requirements.txt
```

## Benefits

1. **100% Compliance** - Templates follow all SciTeX guidelines
2. **Quick Start** - Generate complete projects in seconds
3. **Best Practices** - Enforces proper structure from the start
4. **Validation** - Check existing projects for compliance
5. **Learning Tool** - See correct patterns in generated code