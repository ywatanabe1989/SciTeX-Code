# SciTeX MCP Servers

Model Context Protocol (MCP) servers providing bidirectional translation between standard Python and SciTeX format for scientific computing.

## 🚀 Key Features
- **🔄 Bidirectional Translation**: Convert standard Python ↔ SciTeX format automatically
- **⚡ Module-Specific Servers**: Specialized translation for IO, plotting, statistics, and data processing
- **📊 Code Analysis**: Validate SciTeX compliance and suggest improvements
- **🔧 Configuration Management**: Extract hardcoded values to YAML configs automatically

---

## 📺 Examples

### Translation Demo

```python
# Standard Python → SciTeX
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('input.csv')
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
ax.set_xlabel('X values')
plt.savefig('output.png')

# ↓ Translates to ↓

import scitex as stx

def main(args):
    data = stx.io.load('./input.csv')
    fig, ax = stx.plt.subplots()
    ax.plot(data['x'], data['y'])
    ax.set_xyt('X values', '', '')
    stx.io.save(fig, './output.png', symlink_from_cwd=True)
    return 0
```

### Available Translation Servers

| Server | Module | Capabilities |
|--------|--------|-------------|
| scitex-io-translator | io | File I/O operations, path management, config extraction |
| scitex-plt | plt | Matplotlib enhancements, legend handling, data tracking |
| scitex-stats | stats | Statistical operations and analysis |
| scitex-pd | pd | Pandas operations and data manipulation |
| scitex-dsp | dsp | Signal processing workflows |
| scitex-torch | torch | PyTorch utilities and neural networks |
| scitex-framework | gen | Template generation and boilerplate conversion |
| scitex-analyzer | - | Code analysis and compliance validation |
| scitex-config | - | Configuration management and extraction |

---

## 📦 Installation

```bash
# Install all MCP servers
./install_all.sh

# Test installation
./test_all.sh
```

---

## 🎯 Quick Start

1. **Install servers**: Run `./install_all.sh`

2. **Configure Claude Desktop**: Add configuration from `mcp_config_example.json`

3. **Use in conversations**:
   ```
   "Translate this matplotlib code to SciTeX format"
   "Convert my SciTeX script back to standard Python for sharing"
   "Validate this code for SciTeX compliance"
   ```

### Configuration

Copy and modify `mcp_config_example.json` to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "scitex-io-translator": {
      "command": "python",
      "args": ["-m", "scitex_io_translator"]
    }
  }
}
```

## Advanced Features

- **Smart Path Conversion**: Automatic relative/absolute path handling
- **Config Extraction**: Detect and extract hardcoded values to YAML
- **Round-trip Validation**: Ensure translation accuracy
- **Compliance Checking**: Validate against SciTeX guidelines

---

## 📧 Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->