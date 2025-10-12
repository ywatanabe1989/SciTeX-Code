<!-- ---
!-- Timestamp: 2025-10-09 10:41:59
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/README.md
!-- --- -->

# SciTeX

A Python framework for scientific research that makes the entire research pipeline more standardized, structured, and reproducible by automating repetitive processes.

Part of the fully open-source SciTeX project: https://scitex.ai

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

## 📦 Module Overview

SciTeX is organized into focused modules for different aspects of scientific computing:

### 🔧 Core Utilities
| Module                                          | Description                                                         |
|-------------------------------------------------|---------------------------------------------------------------------|
| [`scitex.gen`](./src/scitex/gen#readme)         | Project setup, session management, and experiment tracking          |
| [`scitex.io`](./src/scitex/io#readme)           | Universal I/O for 30+ formats (CSV, JSON, HDF5, Zarr, pickle, etc.) |
| [`scitex.path`](./src/scitex/path#readme)       | Path manipulation and project structure utilities                   |
| [`scitex.logging`](./src/scitex/logging#readme) | Structured logging with color support and context                   |

### 📊 Data Science & Statistics
| Module                                      | Description                                                              |
|---------------------------------------------|--------------------------------------------------------------------------|
| [`scitex.stats`](./src/scitex/stats#readme) | 16 statistical tests, effect sizes, power analysis, multiple corrections |
| [`scitex.plt`](./src/scitex/plt#readme)     | Enhanced matplotlib with auto-export and scientific captions             |
| [`scitex.pd`](./src/scitex/pd#readme)       | Pandas extensions for research workflows                                 |

### 🧠 AI & Machine Learning
| Module                                      | Description                                             |
|---------------------------------------------|---------------------------------------------------------|
| [`scitex.ai`](./src/scitex/ai#readme)       | GenAI (7 providers), classification, training utilities |
| [`scitex.torch`](./src/scitex/torch#readme) | PyTorch training loops, metrics, and utilities          |
| [`scitex.nn`](./src/scitex/nn#readme)       | Custom neural network layers                            |

### 🌊 Signal Processing
| Module                                  | Description                                                   |
|-----------------------------------------|---------------------------------------------------------------|
| [`scitex.dsp`](./src/scitex/dsp#readme) | Filtering, spectral analysis, wavelets, PAC, ripple detection |

### 📚 Literature Management
| Module                                          | Description                                                     |
|-------------------------------------------------|-----------------------------------------------------------------|
| [`scitex.scholar`](./src/scitex/scholar#readme) | Paper search, PDF download, BibTeX enrichment with IF/citations |

### 🌐 Web & Browser
| Module                                          | Description                                                |
|-------------------------------------------------|------------------------------------------------------------|
| [`scitex.browser`](./src/scitex/browser#readme) | Playwright automation with debugging, PDF handling, popups |

### 🗄️ Data Management
| Module                                | Description                         |
|---------------------------------------|-------------------------------------|
| [`scitex.db`](./src/scitex/db#readme) | SQLite3 and PostgreSQL abstractions |

### 🛠️ Utilities
| Module                                                | Description                                         |
|-------------------------------------------------------|-----------------------------------------------------|
| [`scitex.decorators`](./src/scitex/decorators#readme) | Function decorators for caching, timing, validation |
| [`scitex.rng`](./src/scitex/rng#readme)               | Reproducible random number generation               |
| [`scitex.resource`](./src/scitex/resource#readme)     | System resource monitoring (CPU, memory, GPU)       |
| [`scitex.dict`](./src/scitex/dict#readme)             | Dictionary manipulation and nested access           |
| [`scitex.str`](./src/scitex/str#readme)               | String utilities for scientific text processing     |

## 🚀 Quick Start

### Use Case 1: Data Analysis with Statistics

```python
import scitex as stx

# Load data
data = stx.io.load("experiment_data.csv")
control = data[data['group'] == 'control']['response']
treatment = data[data['group'] == 'treatment']['response']

# Statistical comparison
from scitex.stats.tests.parametric import ttest_ind
from scitex.stats.effect_sizes import cohens_d

result = ttest_ind(control, treatment)
effect = cohens_d(treatment, control)

print(f"{result['formatted']}")  # "t(58) = 2.45, p = 0.017*"
print(f"Cohen's d = {effect['d']:.2f} ({effect['interpretation']})")

# Visualization
fig, ax = stx.plt.subplots()
ax.boxplot([control, treatment], labels=['Control', 'Treatment'])
stx.io.save(fig, "comparison.png")  # Saves figure + data as CSV
```

### Use Case 2: Signal Processing Pipeline

```python
import scitex as stx

# Load EEG/neural data
signal = stx.io.load("neural_recording.h5")  # (n_channels, n_epochs, n_timepoints)
fs = 1000  # Sampling rate

# Preprocessing
from scitex.dsp import filt, psd, wavelet

# Filter to theta band (4-8 Hz)
theta = filt.bandpass(signal, fs, bands=[[4, 8]])

# Power spectral density
freqs, power = psd(signal, fs)

# Time-frequency analysis
import numpy as np
tf_freqs = np.logspace(np.log10(1), np.log10(100), 50)
wavelet_coeffs = wavelet(signal, fs, freqs=tf_freqs)

# Save results
stx.io.save(theta, "processed/theta_filtered.npy")
stx.io.save(power, "processed/psd_results.h5")
```

### Use Case 3: Literature Management

```python
import scitex as stx

# Search and download academic papers
scholar = stx.scholar.Scholar(project="my_research")

# Enrich BibTeX with citations and impact factors
papers = scholar.load_bibtex("references.bib")
enriched = scholar.enrich_papers(papers)

# Filter high-impact papers
high_impact = enriched.filter(
    year_min=2020,
    min_citations=50,
    min_impact_factor=5.0
)

# Download PDFs (requires institutional access)
import asyncio
dois = [p.doi for p in high_impact if p.doi]
asyncio.run(scholar.download_pdfs_from_dois_async(dois))

# Export results
scholar.save_papers_as_bibtex(high_impact, "high_impact_papers.bib")
```

### Use Case 4: Machine Learning Workflow

```python
import scitex as stx
import numpy as np

# Load and prepare data
X_train = stx.io.load("features_train.npy")
y_train = stx.io.load("labels_train.npy")
X_test = stx.io.load("features_test.npy")
y_test = stx.io.load("labels_test.npy")

# Train model
from scitex.ai import ClassificationReporter, EarlyStopping

model = YourModel()  # Your PyTorch/sklearn model
early_stopper = EarlyStopping(patience=10)

# Training loop
for epoch in range(100):
    train_loss = train_epoch(model, X_train, y_train)
    val_loss = validate(model, X_val, y_val)

    early_stopper(val_loss, model)
    if early_stopper.early_stop:
        break

# Evaluate with comprehensive metrics
reporter = ClassificationReporter(save_dir="./results")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

reporter.calc_metrics(y_test, y_pred, y_prob, labels=['class0', 'class1'])
reporter.summarize()  # Prints confusion matrix, ROC, PR curves
reporter.save()  # Saves all metrics and plots
```

### Use Case 5: Complete Research Script

```python
#!/usr/bin/env python3
import scitex as stx
import sys
import matplotlib.pyplot as plt

def main(args):
    # Load experimental data
    data = stx.io.load("data.csv")

    # Preprocess
    processed = preprocess_data(data)

    # Statistical analysis
    results = perform_statistical_tests(processed)

    # Generate publication-quality figures
    fig, axes = stx.plt.subplots(2, 2, figsize=(12, 10))
    plot_results(axes, results)
    stx.io.save(fig, "results/figure1.png")  # Auto-exports data as CSV

    # Save results
    stx.io.save(results, "results/statistical_results.json")

    return 0

if __name__ == '__main__':
    # Initialize SciTeX session (logging, reproducibility, etc.)
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys, plt,
        file=__file__,
        verbose=True
    )

    # Run main analysis
    exit_status = main(None)

    # Cleanup and finalize
    stx.session.close(CONFIG, exit_status=exit_status)
```

### Common Patterns

```python
import scitex as stx

# Universal I/O - format auto-detected
data = stx.io.load("data.csv")       # → pandas DataFrame
array = stx.io.load("data.npy")      # → numpy array
model = stx.io.load("model.pth")     # → PyTorch state dict
config = stx.io.load("config.yaml")  # → dict

# Caching expensive operations
@stx.io.cache(cache_dir=".cache")
def expensive_computation(x):
    return process_large_dataset(x)

# Reproducible random numbers
rng = stx.rng.get_rng(seed=42)
random_data = rng.normal(0, 1, size=1000)

# Path management
project_root = stx.path.find_git_root()
data_dir = project_root / "data"
latest_results = stx.path.find_latest("results/experiment_v*.csv")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx
    parser = argparse.ArgumentParser(description='')
    args = parser.parse_args()
    return args

def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    # Start an session with:
    #   Collect configs defined in ./config/*yaml
    #   Prepare runtime directory as /path/to/script_out/RUNNING/YYYY_MMDD_mmss_<4-random-digit>/
    #   Start logging to <runtime_directory>/logs/{stdout.log,stderr.log}
    #   Setup matplotlib wrapper for saving plotted data as csv
    #   CC: Custom colors for plotting
    #   rng: Fix random seeds for common packages as 42
    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    # Check the runtime status at the end
    exit_status = main(args)

    # Close the session with:
    #   Route all logs and outputs created by the session to RUNNING
    #   Send notification user (needs setup)
    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )
```

## 
<details>

<summary>Recommended Python Script Template for SciTeX project</summary>

``` python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2024-11-03 10:33:13 (ywatanabe)"
# File: placeholder.py

__FILE__ = "placeholder.py"

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import os
import sys
import argparse
import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args):
    return 0

import argparse
def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument(
    #     "--var",
    #     "-v",
    #     type=int,
    #     choices=None,
    #     default=1,
    #     help="(default: %(default)s)",
    # )
    # parser.add_argument(
    #     "--flag",
    #     "-f",
    #     action="store_true",
    #     default=False,
    #     help="(default: %%(default)s)",
    # )
    args = parser.parse_args()
    return args

def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys
    import matplotlib.pyplot as plt
    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )

if __name__ == '__main__':
    run_main()

# EOF
```

</details>


## 📖 Documentation

### Online Documentation
- **[Read the Docs](https://scitex.readthedocs.io/)**: Complete API reference and guides
- **[Interactive Examples](https://scitex.readthedocs.io/en/latest/examples/index.html)**: Browse all tutorial notebooks
- **[Quick Start Guide](https://scitex.readthedocs.io/en/latest/getting_started.html)**: Get up and running quickly

### Local Resources
- **[Master Tutorial Index](./examples/00_SCITEX_MASTER_INDEX.ipynb)**: Comprehensive guide to all features
- **[Examples Directory](./examples/)**: 25+ Jupyter notebooks covering all modules
- **[Module List](./docs/scitex_modules.csv)**: Complete list of all functions
- **(Experimental) [MCP Servers Documentation](./mcp_servers/README.md)**

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

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->