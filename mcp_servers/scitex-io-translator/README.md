# SciTeX IO Translator Module

The IO Translator module provides bidirectional translation between standard Python file I/O operations and SciTeX format for scientific computing reproducibility.

## Core Translation Features

The IO Translator automatically converts file operations while maintaining SciTeX conventions for reproducibility and path management.

### Supported File Operations

| Standard Python | SciTeX Equivalent | Features |
|-----------------|-------------------|----------|
| `pd.read_csv()` | `stx.io.load()` | Auto-detection, relative paths |
| `df.to_csv()` | `stx.io.save()` | Organized output directories |
| `np.save()` | `stx.io.save()` | Symlink creation, data tracking |
| `plt.savefig()` | `stx.io.save(fig)` | Figure management with symlinks |
| `pickle.load()` | `stx.io.load()` | Format auto-detection |
| `json.dump()` | `stx.io.save()` | Unified save interface |

### Example Usage

```python
# Standard Python → SciTeX
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Original code
data = pd.read_csv('/absolute/path/data.csv')
results = np.array([1, 2, 3])
np.save('/absolute/path/results.npy', results)

fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
plt.savefig('/absolute/path/plot.png')

# ↓ Translates to ↓

import scitex as stx

def main(args):
    data = stx.io.load('./data.csv')
    results = np.array([1, 2, 3])
    stx.io.save(results, './results.npy')
    
    fig, ax = stx.plt.subplots()
    ax.plot(data['x'], data['y'])
    stx.io.save(fig, './figures/plot.png', symlink_from_cwd=True)
    return 0
```

## Path Management

The translator automatically handles path conversions following SciTeX conventions:

- **Absolute → Relative**: Converts absolute paths to script-relative paths
- **Config Extraction**: Moves hardcoded paths to `./config/PATH.yaml`
- **Output Organization**: Ensures proper directory structure (`./figures/`, `./data/`)
- **Symlink Creation**: Adds `symlink_from_cwd=True` for plots and results

### Smart Path Detection

```python
# Detects and converts various path patterns:
'/home/user/data.csv' → './data.csv'
'../shared/file.json' → './file.json' (with config entry)
'C:\\Windows\\data.txt' → './data.txt' (cross-platform)
```

## MCP Server Tools

### translate_to_scitex
Converts standard Python code to SciTeX format.

```json
{
  "tool": "translate_to_scitex",
  "arguments": {
    "source_code": "import pandas as pd\ndf = pd.read_csv('data.csv')",
    "preserve_comments": true,
    "add_config_support": false
  }
}
```

### translate_from_scitex
Converts SciTeX code back to standard Python for sharing.

```json
{
  "tool": "translate_from_scitex",
  "arguments": {
    "scitex_code": "import scitex as stx\ndf = stx.io.load('./data.csv')",
    "target_style": "pandas"
  }
}
```

### validate_scitex_compliance
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

## Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->