<!-- ---
!-- Timestamp: 2025-06-21 13:51:19
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/README.md
!-- --- -->


# SciTeX
Scientific tools from literature to LaTeX Manuscript - A comprehensive Python framework for the entire scientific research workflow.

<!-- badges -->
[![PyPI version](https://badge.fury.io/py/scitex.svg)](https://badge.fury.io/py/scitex)
[![Python Versions](https://img.shields.io/pypi/pyversions/scitex.svg)](https://pypi.org/project/scitex/)
[![License](https://img.shields.io/github/license/ywatanabe1989/SciTeX-Code)](https://github.com/ywatanabe1989/SciTeX-Code/blob/main/LICENSE)
[![Tests](https://github.com/ywatanabe1989/SciTeX-Code/actions/workflows/ci.yml/badge.svg)](https://github.com/ywatanabe1989/SciTeX-Code/actions)
[![Coverage](https://codecov.io/gh/ywatanabe1989/SciTeX-Code/branch/main/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/SciTeX-Code)
[![Documentation](https://readthedocs.org/projects/scitex/badge/?version=latest)](https://scitex.readthedocs.io/en/latest/?badge=latest)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## ✨ Key Features

- **Standardized Project Structure**: Consistent organization for reproducible research
- **Configuration Management**: YAML-based configuration with path management
- **Enhanced I/O**: Unified interface for 30+ file formats with automatic tracking
- **Smart Plotting**: Matplotlib wrapper with automatic data export
- **Statistical Tools**: Enhanced stats with p-value formatting and reports
- **AI Development Tools**: MCP servers for code translation and validation
- **Comprehensive Validation**: Code quality checks and best practices enforcement

## 📦 Installation

```bash
pip install scitex
```


## Submodules

| Category              | Submodule                                         | Description                      |
|-----------------------|---------------------------------------------------|----------------------------------|
| **Fundamentals**      | [`scitex.gen`](./src/scitex/gen#readme)               | General utilities                |
|                       | [`scitex.io`](./src/scitex/io#readme)                 | Input/Output operations          |
|                       | [`scitex.utils`](./src/scitex/utils#readme)           | General utilities                |
|                       | [`scitex.dict`](./src/scitex/dict#readme)             | Dictionary utilities             |
|                       | [`scitex.str`](./src/scitex/str#readme)               | String manipulation              |
|                       | [`scitex.torch`](./src/scitex/torch#readme)           | PyTorch utilities                |
| **Data Science**      | [`scitex.plt`](./src/scitex/plt#readme)               | Plotting with automatic tracking |
|                       | [`scitex.stats`](./src/scitex/stats#readme)           | Statistical analysis             |
|                       | [`scitex.pd`](./src/scitex/pd#readme)                 | Pandas utilities                 |
|                       | [`scitex.tex`](./src/scitex/tex#readme)               | LaTeX utilities                  |
| **AI: ML/PR**         | [`scitex.ai`](./src/scitex/ai#readme)                 | AI and Machine Learning          |
|                       | [`scitex.nn`](./src/scitex/nn#readme)                 | Neural Networks                  |
|                       | [`scitex.torch`](./src/scitex/torch#readme)           | PyTorch utilities                |
|                       | [`scitex.db`](./src/scitex/db#readme)                 | Database operations              |
|                       | [`scitex.linalg`](./src/scitex/linalg#readme)         | Linear algebra                   |
| **Signal Processing** | [`scitex.dsp`](./src/scitex/dsp#readme)               | Digital Signal Processing        |
| **Statistics**        | [`scitex.stats`](./src/scitex/stats#readme)           | Statistical analysis tools       |
| **Literature**        | [`scitex.scholar`](./src/scitex/scholar#readme)       | Academic paper search & download |
| **ETC**               | [`scitex.decorators`](./src/scitex/decorators#readme) | Function decorators              |
|                       | [`scitex.gists`](./src/scitex/gists#readme)           | Code snippets                    |
|                       | [`scitex.resource`](./src/scitex/resource#readme)     | Resource management              |
|                       | [`scitex.web`](./src/scitex/web#readme)               | Web-related functions            |

## 🚀 Quick Start

```python
import scitex

# Start an experiment with automatic logging
config, info = scitex.gen.start(sys, sdir="./experiments")

# Load and process data
data = scitex.io.load("data.csv")
processed = scitex.pd.force_df(data)

# Signal processing
signal, time, fs = scitex.dsp.demo_sig(sig_type="chirp")
filtered = scitex.dsp.filt.bandpass(signal, fs, bands=[[10, 50]])

# Machine learning workflow
reporter = scitex.ai.ClassificationReporter()
metrics = reporter.evaluate(y_true, y_pred)

# Visualization
fig, ax = scitex.plt.subplots()
ax.plot(time, signal[0, 0, :])
scitex.io.save(fig, "signal_plot.png")

# Close experiment
scitex.gen.close(config, info)
```

## 🆕 What's New in v2.0

### 📚 Scholar Module with Enhanced Search Capabilities

The Scholar module now supports **5 search engines** including the newly added **CrossRef**:
- **PubMed**: Biomedical literature database
- **Semantic Scholar**: AI-powered research tool with citation graphs
- **Google Scholar**: Comprehensive academic search (via scholarly package)
- **CrossRef**: DOI registration agency with 150M+ scholarly works (NEW!)
- **arXiv**: Preprint repository for physics, mathematics, computer science

```python
from scitex.scholar import Scholar

# Initialize Scholar
scholar = Scholar()

# Search across multiple databases
papers = scholar.search(
    query="machine learning",
    sources=["pubmed", "crossref", "arxiv"],  # Mix and match sources
    limit=20
)
```

Features:
- Automatic enrichment with 2024 JCR impact factors
- YAML configuration support
- PDF download with institutional access (OpenAthens - now fully working!)
- Unified API across all search engines

### 🤖 MCP Servers for AI-Assisted Development

SciTeX now includes Model Context Protocol (MCP) servers that work with AI assistants like Claude:

### Available MCP Servers
- **scitex-io**: Bidirectional translation for 30+ file formats
- **scitex-plt**: Matplotlib enhancement translations
- **scitex-stats**: Statistical function translations with p-value formatting
- **scitex-dsp**: Signal processing translations
- **scitex-pd**: Pandas operation translations
- **scitex-torch**: PyTorch deep learning translations
- **scitex-analyzer**: Code analysis with comprehensive validation
- **scitex-framework**: Template and project generation
- **scitex-config**: Configuration management
- **scitex-orchestrator**: Workflow coordination
- **scitex-validator**: Compliance validation

### Quick Setup
```bash
cd mcp_servers
./install_all.sh
# Configure your AI assistant with mcp_config_example.json
./launch_all.sh
```

See [MCP Servers Documentation](./mcp_servers/README.md) for details.

## 📖 Documentation

### Online Documentation
- **[Read the Docs](https://scitex.readthedocs.io/)**: Complete API reference and guides
- **[Interactive Examples](https://scitex.readthedocs.io/en/latest/examples/index.html)**: Browse all tutorial notebooks
- **[Quick Start Guide](https://scitex.readthedocs.io/en/latest/getting_started.html)**: Get up and running quickly

### Local Resources
- **[Master Tutorial Index](./examples/00_SCITEX_MASTER_INDEX.ipynb)**: Comprehensive guide to all features
- **[Examples Directory](./examples/)**: 25+ Jupyter notebooks covering all modules
- **[Module List](./docs/scitex_modules.csv)**: Complete list of all functions

### Key Tutorials
1. **[I/O Operations](./examples/01_scitex_io.ipynb)**: Essential file handling (start here!)
2. **[Plotting](./examples/14_scitex_plt.ipynb)**: Publication-ready visualizations
3. **[Statistics](./examples/11_scitex_stats.ipynb)**: Research-grade statistical analysis
4. **[Scholar](./examples/16_scitex_scholar.ipynb)**: Literature management with impact factors
5. **[AI/ML](./examples/16_scitex_ai.ipynb)**: Complete machine learning toolkit

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.


## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->