# SciTeX IO MCP Server

MCP server for the SciTeX IO module, providing translation and analysis tools for file I/O operations.

## Features

- **Bidirectional Translation**: Convert between standard Python I/O and SciTeX `stx.io` operations
- **Format Auto-detection**: Supports 30+ file formats (CSV, JSON, NumPy, PyTorch, HDF5, etc.)
- **Path Management**: Automatic conversion to relative paths and directory creation
- **Code Analysis**: Identify I/O patterns and suggest improvements

## Available Tools

### Translation Tools
- `translate_to_scitex`: Convert standard Python I/O to SciTeX format
- `translate_from_scitex`: Convert SciTeX I/O back to standard Python
- `suggest_improvements`: Analyze code for SciTeX improvement opportunities

### Analysis Tools
- `analyze_io_operations`: Detect and categorize all I/O operations
- `suggest_path_improvements`: Identify path handling issues
- `convert_path_to_scitex`: Convert paths to SciTeX conventions
- `validate_code`: Check for proper SciTeX IO usage

## Installation

```bash
pip install -e .
```

## Configuration

Add to your MCP settings:

```json
{
  "mcpServers": {
    "scitex-io": {
      "command": "python",
      "args": ["-m", "server"],
      "cwd": "/path/to/scitex-io"
    }
  }
}
```

## Translation Examples

### Standard Python → SciTeX

**Input:**
```python
import pandas as pd
import numpy as np

data = pd.read_csv('/home/user/data.csv')
results = process_data(data)
results.to_csv('output.csv')
np.save('arrays.npy', results.values)
```

**Output:**
```python
import pandas as pd
import numpy as np
import scitex as stx

data = stx.io.load('./data.csv')
results = process_data(data)
stx.io.save(results, './output.csv', symlink_from_cwd=True)
stx.io.save(results.values, './arrays.npy', symlink_from_cwd=True)
```

### Key Transformations

1. **Path Handling**
   - Absolute paths → Relative paths
   - Automatic `./` prefix for relative paths
   - Directory creation handled automatically

2. **Unified Interface**
   - `pd.read_*()` → `stx.io.load()`
   - `*.to_*()` → `stx.io.save()`
   - `np.load/save()` → `stx.io.load/save()`

3. **Best Practices**
   - Adds `symlink_from_cwd=True` for output files
   - Suggests config extraction for multiple paths
   - Validates proper usage patterns

## Supported Formats

- **Tabular**: CSV, TSV, Excel
- **Scientific**: NumPy, MATLAB, HDF5
- **ML/DL**: PyTorch, TensorFlow, Joblib
- **Structured**: JSON, YAML, XML
- **Images**: PNG, JPG, TIFF
- **Documents**: TXT, Markdown, PDF

# EOF