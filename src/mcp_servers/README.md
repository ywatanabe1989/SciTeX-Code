# SciTeX MCP Servers

Model Context Protocol (MCP) servers providing bidirectional translation between standard Python and SciTeX format for scientific computing.

## 🚀 Key Features
- **🔄 Bidirectional Translation**: Convert standard Python ↔ SciTeX format automatically
- **⚡ Module-Specific Servers**: Specialized translation for IO, plotting, statistics, and data processing
- **📊 Code Analysis**: Validate SciTeX compliance and suggest improvements
- **🔧 Configuration Management**: Extract hardcoded values to YAML configs automatically
- **🧪 Developer Support**: Test generation, performance optimization, migration assistance
- **📚 Interactive Learning**: Tutorials, concept explanations, and best practices

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

### Available MCP Servers

| Server | Module | Capabilities |
|--------|--------|-------------|
| **Translation Servers** | | |
| scitex-io-translator | io | File I/O operations, path management, config extraction |
| scitex-plt | plt | Matplotlib enhancements, legend handling, data tracking |
| scitex-stats | stats | Statistical operations and analysis |
| scitex-pd | pd | Pandas operations and data manipulation |
| scitex-dsp | dsp | Signal processing workflows |
| scitex-torch | torch | PyTorch utilities and neural networks |
| **Development Support** | | |
| scitex-analyzer | - | Code analysis and compliance validation |
| scitex-developer | - | **Comprehensive developer support (test generation, performance, migration)** |
| scitex-config | - | Configuration management and extraction |
| scitex-framework | gen | Template generation and boilerplate conversion |

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
   "Generate tests for my data processing script"
   "Create a performance optimization plan"
   "Help me migrate to the latest SciTeX version"
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

### Translation & Analysis
- **Smart Path Conversion**: Automatic relative/absolute path handling
- **Config Extraction**: Detect and extract hardcoded values to YAML
- **Round-trip Validation**: Ensure translation accuracy
- **Compliance Checking**: Validate against SciTeX guidelines

### Developer Support (scitex-developer)
- **Test Generation**: Create comprehensive test suites with pytest/unittest
- **Performance Analysis**: Profile scripts and identify bottlenecks
- **Migration Assistance**: Automated help for version upgrades
- **Code Quality**: Measure complexity, maintainability, and security
- **Interactive Learning**: Custom tutorials and concept explanations
- **Refactoring Support**: Best practices and pattern suggestions

---

## 📧 Contact
Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->