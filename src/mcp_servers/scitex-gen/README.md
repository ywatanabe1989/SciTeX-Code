# SciTeX Gen MCP Server

MCP server for SciTeX general utilities (gen) module operations.

## Overview

The scitex-gen MCP server provides translation and enhancement capabilities for general utility operations in scientific computing, focusing on the SciTeX gen module which includes:

- **Data Normalization**: Z-score, min-max scaling, outlier clipping
- **Caching**: Function result caching for performance
- **Path Management**: File and directory path utilities
- **Timestamp Tracking**: Experiment time management
- **Environment Detection**: Host and platform checking
- **Experiment Lifecycle**: Start/close experiment management

## Installation

```bash
cd mcp_servers/scitex-gen
pip install -e .
```

## Available Tools

### Core MCP Tools
- `get_module_info`: Get information about the gen module
- `validate_code`: Validate gen module usage
- `translate_to_scitex`: Convert standard Python to SciTeX gen patterns
- `translate_from_scitex`: Convert SciTeX gen code back to standard Python
- `suggest_improvements`: Analyze code for improvement opportunities

### Gen-Specific Tools
- `analyze_utility_usage`: Analyze general utility patterns in code
- `suggest_gen_improvements`: Suggest gen module improvements
- `convert_normalization_to_scitex`: Convert normalization operations
- `create_experiment_setup`: Generate experiment initialization code

## Usage Examples

### Translation Example

```python
# Standard Python normalization
data_normalized = (data - np.mean(data)) / np.std(data)
data_scaled = (data - data.min()) / (data.max() - data.min())

# Translates to SciTeX:
data_normalized = stx.gen.to_z(data)
data_scaled = stx.gen.to_01(data)
```

### Caching Example

```python
# Standard Python with functools
@functools.lru_cache(maxsize=128)
def expensive_computation(n):
    return sum(i**2 for i in range(n))

# Translates to SciTeX:
@stx.gen.cache
def expensive_computation(n):
    return sum(i**2 for i in range(n))
```

### Experiment Management

```python
# Standard Python setup
import random
import numpy as np
random.seed(42)
np.random.seed(42)

# Translates to SciTeX:
config = stx.gen.start(
    description="My experiment",
    verbose=True
)
# ... experiment code ...
stx.gen.close()
```

## Key Features

1. **Normalization Utilities**
   - Z-score normalization with `to_z()`
   - Min-max scaling with `to_01()` 
   - Outlier clipping with `clip_perc()`
   - Bias removal with `unbias()`

2. **Performance Optimization**
   - Automatic caching with `@cache` decorator
   - Efficient array operations
   - Memory-conscious implementations

3. **Experiment Management**
   - Reproducible experiment setup
   - Time tracking with TimeStamper
   - Automatic output organization

4. **Path and Environment**
   - Robust path handling
   - Platform detection
   - File organization utilities

## Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "scitex-gen": {
      "command": "python",
      "args": ["-m", "scitex_gen.server"],
      "cwd": "/path/to/mcp_servers/scitex-gen"
    }
  }
}
```

## Testing

```bash
# Run the test suite
python test_server.py
```

## See Also

- [SciTeX Documentation](https://scitex.readthedocs.io)
- [Gen Module Guide](https://scitex.readthedocs.io/en/latest/modules/gen.html)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)