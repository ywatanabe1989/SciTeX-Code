<!-- ---
!-- Timestamp: 2025-06-21 13:51:19
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/proj/SciTeX-Code/README.md
!-- --- -->


# SciTeX
A Python framework for standardized scientific projects.

<!-- badges -->
[![PyPI version](https://badge.fury.io/py/scitex.svg)](https://badge.fury.io/py/scitex)
[![Python Versions](https://img.shields.io/pypi/pyversions/scitex.svg)](https://pypi.org/project/scitex/)
[![License](https://img.shields.io/github/license/ywatanabe1989/SciTeX-Code)](https://github.com/ywatanabe1989/SciTeX-Code/blob/main/LICENSE)
[![Tests](https://github.com/ywatanabe1989/SciTeX-Code/actions/workflows/ci.yml/badge.svg)](https://github.com/ywatanabe1989/SciTeX-Code/actions)
[![Coverage](https://codecov.io/gh/ywatanabe1989/SciTeX-Code/branch/main/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/SciTeX-Code)
[![Documentation](https://readthedocs.org/projects/scitex/badge/?version=latest)](https://scitex.readthedocs.io/en/latest/?badge=latest)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

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

## 📖 Documentation

- **[Full Documentation](https://scitex.readthedocs.io/)**: Complete API reference and guides
- **[Examples](./examples/)**: Practical examples and workflows
- **[Module List](./docs/scitex_modules.csv)**: Complete list of all functions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.


## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->