# SciTeX MCP Servers

This directory contains Model Context Protocol (MCP) servers for SciTeX modules, enabling bidirectional translation between standard Python and SciTeX format.

## Overview

The SciTeX MCP servers have evolved from simple translators to comprehensive development partners:

### Core Capabilities
- **Translation**: Bidirectional conversion between standard Python and SciTeX
- **Project Generation**: Complete project scaffolding with proper structure
- **Code Analysis**: Deep understanding of patterns and anti-patterns
- **Framework Support**: Full template generation following all guidelines
- **Configuration Management**: Generate and validate config files
- **Validation**: Comprehensive compliance checking

## Available Servers

### 1. scitex-io
File I/O operations translator supporting 30+ formats.

**Key Features:**
- Converts `pd.read_csv()` → `stx.io.load()`
- Converts `plt.savefig()` → `stx.io.save()`
- Automatic path conversion (absolute → relative)
- Directory creation handled automatically

**Tools:**
- `translate_to_scitex`
- `translate_from_scitex`
- `analyze_io_operations`
- `suggest_path_improvements`
- `validate_code`

### 2. scitex-plt
Matplotlib enhancement translator with data tracking.

**Key Features:**
- Converts `plt.subplots()` → `stx.plt.subplots()`
- Combines `set_xlabel/ylabel/title` → `set_xyt()`
- Automatic CSV export of plot data
- Data tracking for reproducibility

**Tools:**
- `translate_to_scitex`
- `translate_from_scitex`
- `analyze_plotting_operations`
- `suggest_data_tracking`
- `convert_axis_labels_to_xyt`

### 3. scitex-analyzer
Advanced code analysis and understanding for SciTeX projects.

**Key Features:**
- Complete project analysis and scoring
- Pattern detection and explanation
- Anti-pattern identification
- Prioritized improvement suggestions

**Tools:**
- `analyze_scitex_project` - Full project analysis
- `explain_scitex_pattern` - Pattern understanding
- `suggest_scitex_improvements` - Targeted suggestions
- `find_scitex_examples` - Usage examples

### 4. scitex-framework (NEW)
Complete framework support for template generation and project scaffolding.

**Key Features:**
- Generate complete SciTeX script templates
- Create project structures (research/package)
- Configuration file generation
- Structure validation and scoring

**Tools:**
- `generate_scitex_script_template` - Full script templates
- `generate_config_files` - PATH/PARAMS/DEBUG configs
- `create_scitex_project` - Complete project scaffolding
- `validate_project_structure` - Structure compliance

## Installation

### Install Individual Servers
```bash
cd mcp_servers/scitex-io
pip install -e .

cd ../scitex-plt
pip install -e .
```

### Install All Servers
```bash
cd mcp_servers
./install_all.sh
```

## Configuration

### For Claude Desktop

Add to your MCP configuration file:

```json
{
  "mcpServers": {
    "scitex-io": {
      "command": "python",
      "args": ["-m", "scitex_io.server"],
      "cwd": "/path/to/mcp_servers/scitex-io"
    },
    "scitex-plt": {
      "command": "python", 
      "args": ["-m", "scitex_plt.server"],
      "cwd": "/path/to/mcp_servers/scitex-plt"
    }
  }
}
```

### Running Servers Manually

```bash
# Run IO server
cd scitex-io
python server.py

# Run PLT server  
cd scitex-plt
python server.py
```

## Usage Examples

### IO Translation

**Standard Python:**
```python
import pandas as pd
data = pd.read_csv('/home/user/data.csv')
data.to_csv('output.csv')
```

**SciTeX (via MCP):**
```python
import scitex as stx
data = stx.io.load('./data.csv')
stx.io.save(data, './output.csv', symlink_from_cwd=True)
```

### PLT Translation

**Standard Matplotlib:**
```python
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Plot')
plt.savefig('plot.png')
```

**SciTeX (via MCP):**
```python
fig, ax = stx.plt.subplots()
ax.plot(x, y)
ax.set_xyt('X', 'Y', 'Plot')
stx.io.save(fig, './plot.png', symlink_from_cwd=True)
# Also creates plot.csv with the data
```

## Architecture

```
mcp_servers/
├── scitex-base/          # Base classes for all servers
│   ├── base_server.py    # Abstract base server
│   └── __init__.py
├── scitex-io/            # IO module server
│   ├── server.py         # Main server implementation
│   ├── pyproject.toml    # Package configuration
│   └── README.md         # Server documentation
├── scitex-plt/           # PLT module server
│   ├── server.py         # Main server implementation
│   ├── pyproject.toml    # Package configuration
│   └── README.md         # Server documentation
└── README.md             # This file
```

## Extending

To create a new SciTeX module MCP server:

1. Create new directory: `scitex-{module}/`
2. Inherit from `ScitexBaseMCPServer`
3. Implement required methods:
   - `_register_module_tools()`
   - `get_module_description()`
   - `validate_module_usage()`
4. Add translation logic specific to the module

Example structure:
```python
from scitex_base.base_server import ScitexBaseMCPServer

class ScitexModuleMCPServer(ScitexBaseMCPServer):
    def __init__(self):
        super().__init__("module_name", "0.1.0")
        # Module-specific initialization
```

## Development

### Running Tests
```bash
# Test individual server
cd scitex-io
python test_server.py

# Test all servers
cd mcp_servers
./test_all.sh
```

### Adding New Features
1. Add tool method to server class
2. Register in `_register_module_tools()`
3. Update `get_available_tools()`
4. Add tests for new functionality

## Benefits

1. **Gradual Migration**: Convert code incrementally
2. **Bidirectional**: Work with both formats
3. **Validation**: Ensure SciTeX compliance
4. **Learning**: Understand SciTeX patterns through examples
5. **Collaboration**: Share code in any format

## Future Servers

Planned MCP servers for other SciTeX modules:
- `scitex-dsp`: Digital signal processing
- `scitex-stats`: Statistical operations
- `scitex-pd`: Pandas enhancements
- `scitex-torch`: PyTorch utilities
- `scitex-nn`: Neural network helpers

## Contributing

1. Follow SciTeX coding guidelines
2. Maintain bidirectional translation accuracy
3. Add comprehensive tests
4. Update documentation

# EOF