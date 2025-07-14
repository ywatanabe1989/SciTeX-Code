# SciTeX IO Translator - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scitex-code.git
cd scitex-code/mcp_servers/scitex_io_translator

# Install the MCP server
pip install -e .
```

## Configuration for Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "scitex-io-translator": {
      "command": "python",
      "args": ["-m", "scitex_io_translator.server"],
      "cwd": "/path/to/scitex-code/mcp_servers/scitex_io_translator"
    }
  }
}
```

## Basic Usage Examples

### 1. Convert Your First Script

Ask Claude:
```
Please convert this pandas script to SciTeX format:

import pandas as pd
df = pd.read_csv('data.csv')
result = df.groupby('category').mean()
result.to_csv('output.csv')
```

Claude will use the MCP server to translate it to:
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:50:00 (ywatanabe)"
# File: ./script.py
# ----------------------------------------
import os
__FILE__ = "./script.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

def main():
    """Main function."""
    df = stx.io.load('./data.csv')
    result = df.groupby('category').mean()
    stx.io.save(result, './output.csv', symlink_from_cwd=True)
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

### 2. Validate Existing SciTeX Code

Ask Claude:
```
Can you check if this code follows SciTeX best practices?

import scitex as stx
data = stx.io.load('measurements.csv')
stx.io.save(data, '/tmp/output.csv')
```

### 3. Convert Back to Standard Python

Ask Claude:
```
Convert this SciTeX code back to standard Python for sharing:

import scitex as stx
df = stx.io.load('./data.csv')
fig, ax = stx.plt.subplots()
ax.plot(df['x'], df['y'])
ax.set_xyt('Time', 'Value', 'Data Plot')
stx.io.save(fig, './figures/plot.png')
```

## Common Translation Patterns

### File I/O
| Standard Python | SciTeX |
|----------------|---------|
| `pd.read_csv('file.csv')` | `stx.io.load('./file.csv')` |
| `df.to_csv('out.csv')` | `stx.io.save(df, './out.csv')` |
| `np.load('data.npy')` | `stx.io.load('./data.npy')` |
| `plt.savefig('fig.png')` | `stx.io.save(fig, './figures/fig.png')` |

### Paths
- Absolute paths → Relative paths with `./`
- Outputs organized by type: `./figures/`, `./data/`, `./results/`
- Automatic symlink creation with `symlink_from_cwd=True`

### Matplotlib
| Standard Python | SciTeX |
|----------------|---------|
| `plt.subplots()` | `stx.plt.subplots()` |
| `ax.set_xlabel()` + `ax.set_ylabel()` + `ax.set_title()` | `ax.set_xyt(xlabel, ylabel, title)` |

## Tips for Effective Use

1. **Batch Translation**: Convert multiple files at once by providing all code to Claude

2. **Config Extraction**: Ask Claude to extract hardcoded values:
   ```
   Convert this to SciTeX and extract configuration values:
   [your code with hardcoded paths and parameters]
   ```

3. **Validation First**: Before converting large codebases, validate a sample:
   ```
   Is this code SciTeX compliant? What would need to change?
   [your code sample]
   ```

4. **Incremental Migration**: Start with IO operations, then add other modules:
   ```
   Convert just the file I/O operations to SciTeX format first
   ```

## Troubleshooting

### MCP Server Not Found
- Ensure the server is installed: `pip install -e .`
- Check the path in your Claude Desktop config
- Restart Claude Desktop after configuration changes

### Translation Errors
- Make sure your Python code is syntactically valid
- For complex code, try smaller sections first
- Ask Claude to explain any warnings or suggestions

### Path Issues
- SciTeX prefers relative paths starting with `./`
- Use forward slashes even on Windows
- Let the translator organize output paths automatically

## Next Steps

1. Install other SciTeX MCP servers for additional functionality
2. Read the [SciTeX documentation](https://scitex.readthedocs.io)
3. Join the SciTeX community for support and best practices

## Need Help?

Ask Claude:
- "How do I convert matplotlib code to SciTeX?"
- "What's the SciTeX equivalent of pickle.dump()?"
- "Can you validate my SciTeX code and suggest improvements?"

The MCP server will handle the technical details while Claude provides guidance!