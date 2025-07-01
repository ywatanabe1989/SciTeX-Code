# SciTeX IO Translator MCP Server

An MCP (Model Context Protocol) server that translates between standard Python IO operations and SciTeX format, helping researchers adopt SciTeX conventions gradually.

## Features

- **Bidirectional Translation**: Convert standard Python to SciTeX and back
- **IO Pattern Recognition**: Automatically detects pandas, numpy, matplotlib operations
- **Path Management**: Converts absolute paths to relative, organizes outputs
- **Validation**: Checks code compliance with SciTeX guidelines
- **Config Extraction**: Optionally extracts hardcoded values to config files

## Installation

```bash
cd mcp_servers/scitex_io_translator
pip install -e .
```

## Usage

### Starting the Server

```bash
scitex-io-translator
```

Or with Python:

```python
python -m scitex_io_translator.server
```

### Available Tools

#### 1. translate_to_scitex
Converts standard Python code to SciTeX format.

```json
{
  "tool": "translate_to_scitex",
  "arguments": {
    "source_code": "import pandas as pd\ndf = pd.read_csv('data.csv')\ndf.to_csv('output.csv')",
    "target_modules": ["io"],
    "preserve_comments": true,
    "add_config_support": false
  }
}
```

#### 2. translate_from_scitex
Converts SciTeX code back to standard Python.

```json
{
  "tool": "translate_from_scitex",
  "arguments": {
    "scitex_code": "import scitex as stx\ndf = stx.io.load('./data.csv')\nstx.io.save(df, './output.csv')",
    "target_style": "pandas",
    "include_dependencies": true
  }
}
```

#### 3. validate_scitex_compliance
Validates code against SciTeX guidelines.

```json
{
  "tool": "validate_scitex_compliance",
  "arguments": {
    "code": "import scitex as stx\n# Your code here",
    "strict_mode": false
  }
}
```

#### 4. extract_io_patterns
Analyzes code to extract IO patterns.

```json
{
  "tool": "extract_io_patterns",
  "arguments": {
    "code": "df = pd.read_csv('data.csv')\nplt.savefig('plot.png')"
  }
}
```

## Translation Examples

### Standard Python → SciTeX

**Input:**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('input.csv')
fig, ax = plt.subplots()
ax.plot(df['x'], df['y'])
plt.savefig('output.png')
```

**Output:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 12:00:00 (ywatanabe)"
# File: ./script.py
# ----------------------------------------
import os
__FILE__ = "./script.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

def main():
    """Main function."""
    df = stx.io.load('./input.csv')
    fig, ax = stx.plt.subplots()
    ax.plot(df['x'], df['y'])
    stx.io.save(fig, './figures/output.png', symlink_from_cwd=True)
    return 0

def run_main():
    """Run main function with proper setup."""
    import sys
    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys, plt, verbose=True
    )
    main(CONFIG)
    stx.gen.close(CONFIG, verbose=True)

if __name__ == "__main__":
    run_main()
```

### SciTeX → Standard Python

**Input:**
```python
import scitex as stx
data = stx.io.load('./data.npy')
stx.io.save(data * 2, './output.npy')
```

**Output:**
```python
import numpy as np
import os

# Create output directories
os.makedirs(os.path.dirname("./output.npy"), exist_ok=True)

data = np.load('./data.npy')
np.save('./output.npy', data * 2)
```

## Supported Translations

### IO Operations
- `pd.read_csv()` → `stx.io.load()`
- `df.to_csv()` → `stx.io.save()`
- `np.load()` / `np.save()` → `stx.io.load()` / `stx.io.save()`
- `plt.savefig()` → `stx.io.save()`
- `pickle.load()` / `pickle.dump()` → `stx.io.load()` / `stx.io.save()`
- `json.load()` / `json.dump()` → `stx.io.load()` / `stx.io.save()`

### Path Conventions
- Absolute paths → Relative paths with `./`
- Unorganized outputs → Organized by type (`./figures/`, `./data/`, etc.)
- Hardcoded paths → Config file references (optional)

## Integration with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "scitex-io-translator": {
      "command": "python",
      "args": ["-m", "scitex_io_translator.server"],
      "cwd": "/path/to/mcp_servers/scitex_io_translator"
    }
  }
}
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Translation Patterns

1. Edit `translators/io_translator.py` to add patterns
2. Update validation rules in `translators/validation_engine.py`
3. Add tests for new patterns

## License

MIT License - See LICENSE file for details.