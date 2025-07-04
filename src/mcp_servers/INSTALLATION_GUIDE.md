# SciTeX MCP Servers - Installation & Usage Guide

## Quick Start for Claude Code Users

### 🎯 Essential Setup (Recommended)

For most users who want to **convert Python code to SciTeX format**, you only need these servers:

```bash
# 1. Essential servers for SciTeX conversion
mcp_servers/
├── scitex-base/              # Foundation (automatically used)
├── scitex-unified/           # 🎯 Main entry point
├── scitex-io/                # 🎯 I/O conversions  
├── scitex-plt/               # 🎯 Plotting conversions
├── scitex-stats/             # 🎯 Statistics conversions
└── scitex-project-validator/ # 🎯 Project validation & templates
```

### Installation

1. **Prerequisites**:
   ```bash
   # Install SciTeX package
   pip install -e /path/to/scitex-repo
   
   # Install MCP dependencies
   pip install mcp
   ```

2. **Quick Setup**:
   ```bash
   cd /path/to/SciTeX-Code/mcp_servers
   
   # Install essential servers
   pip install -e ./scitex-base
   pip install -e ./scitex-unified  
   pip install -e ./scitex-io
   pip install -e ./scitex-plt
   pip install -e ./scitex-stats
   pip install -e ./scitex-project-validator
   ```

### 🚀 Usage with Claude Code

#### Primary Interface: `scitex-unified`

The main entry point with simple functions:

```python
# Convert Python code to SciTeX format
result = translate_to_scitex("""
import pandas as pd
data = pd.read_csv('input.csv')
data.to_csv('output.csv')
""")

# Convert SciTeX back to standard Python  
result = translate_from_scitex("""
import scitex as stx
data = stx.io.load('./input.csv')
stx.io.save(data, './output.csv', symlink_from_cwd=True)
""")
```

#### Module-Specific Guidance

For detailed help with specific modules:

```python
# I/O operations guidance
explain_io_conversion(your_code)
suggest_scitex_workflow(your_code) 
create_learning_plan("beginner")

# Plotting conversions
convert_matplotlib_to_scitex(plot_code)
enhance_plotting_workflow(plot_code)

# Statistics conversions  
convert_stats_to_scitex(stats_code)
suggest_robust_alternatives(stats_code)

# Project validation
check_scitex_project_structure_for_scientific_project("/path/to/project")
create_template_scientific_project("/path", "my_project")
```

## Configuration for Claude Code

### MCP Configuration File

Create `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "scitex-unified": {
      "command": "python",
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-unified/server.py"]
    },
    "scitex-io": {
      "command": "python", 
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-io/server.py"]
    },
    "scitex-plt": {
      "command": "python",
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-plt/server.py"]
    },
    "scitex-stats": {
      "command": "python",
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-stats/server.py"]
    },
    "scitex-project-validator": {
      "command": "python",
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-project-validator/server.py"]
    }
  }
}
```

### Simplified Configuration (Just the Essentials)

For most users, you can start with just the unified server:

```json
{
  "mcpServers": {
    "scitex": {
      "command": "python",
      "args": ["/path/to/SciTeX-Code/mcp_servers/scitex-unified/server.py"]
    }
  }
}
```

## Common Workflows

### 1. Convert Existing Python Script

```python
# Your original Python code
code = '''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = pd.read_csv('data.csv')
plt.plot(data['x'], data['y'])
plt.savefig('plot.png')
'''

# Get conversion guidance
result = translate_to_scitex(code)
print(result['conversion_guidance'])
print(result['example_conversion'])
```

### 2. Validate Project Structure

```python
# Check if your project follows SciTeX conventions
result = check_scitex_project_structure_for_scientific_project("/path/to/project")

print(f"Compliance: {result['compliance_level']}")
for issue in result['issues']:
    print(f"Issue: {issue}")
for suggestion in result['suggestions']:
    print(f"Fix: {suggestion}")
```

### 3. Create New SciTeX Project

```python
# Generate a complete SciTeX project template
result = create_template_scientific_project("/path/to/workspace", "my_analysis")

print(f"Created: {result['project_path']}")
print("Next steps:")
for step in result['next_steps']:
    print(f"  - {step}")
```

## Advanced Setup (Optional Specialized Servers)

If you need specific functionality:

```bash
# Digital signal processing
pip install -e ./scitex-dsp

# PyTorch integration  
pip install -e ./scitex-torch

# Pandas operations
pip install -e ./scitex-pd

# General utilities
pip install -e ./scitex-gen
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure SciTeX is installed
   ```bash
   pip install -e /path/to/scitex-repo
   ```

2. **Server Not Found**: Check MCP configuration file path
   ```bash
   # Verify file exists
   cat ~/.config/claude-code/mcp.json
   ```

3. **Permission Issues**: Ensure Python scripts are executable
   ```bash
   chmod +x /path/to/SciTeX-Code/mcp_servers/*/server.py
   ```

### Validation

Test your setup:

```bash
# Test unified server directly
cd /path/to/SciTeX-Code/mcp_servers/scitex-unified
python server.py to-scitex "pd.read_csv('file.csv')"

# Test project validator
cd /path/to/SciTeX-Code/mcp_servers/scitex-project-validator  
python validator.py check-scientific /path/to/test/project
```

## Benefits of This Setup

✅ **Simple Entry Point**: `scitex-unified` handles most conversion needs  
✅ **Educational Approach**: Provides guidance instead of brittle automation  
✅ **Modular Design**: Add specialized servers as needed  
✅ **Complete Workflow**: From code conversion to project structure  
✅ **Claude Code Integration**: Works seamlessly with Claude Code MCP protocol  

## Getting Help

- **Basic conversions**: Use `scitex-unified`
- **I/O questions**: Use `scitex-io` 
- **Plotting help**: Use `scitex-plt`
- **Statistics guidance**: Use `scitex-stats`
- **Project setup**: Use `scitex-project-validator`

This setup gives you everything needed to easily convert Python code to follow SciTeX conventions!