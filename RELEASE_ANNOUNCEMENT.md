# 🎉 SciTeX v2.0.0 Released on PyPI!

We're excited to announce the official release of **SciTeX v2.0.0** - a comprehensive Python framework for scientific computing that makes research workflows lazy (in the best way possible)!

## 🚀 Install Now

```bash
pip install scitex
```

## 📦 What is SciTeX?

SciTeX (from "Monogusa" - lazy person in Japanese) is designed to streamline scientific Python workflows by providing:

- **Unified I/O**: Single interface for 20+ file formats
- **Enhanced Plotting**: Matplotlib wrapper that saves both plots AND data
- **Signal Processing**: Advanced DSP tools for filtering, spectral analysis, PAC
- **Statistical Analysis**: Common tests with publication-ready formatting
- **Machine Learning**: Integrated AI/ML utilities with PyTorch support
- **Reproducibility**: Built-in experiment tracking and seed management

## ✨ Key Features

### 1. One-Line File I/O
```python
import scitex

# Load any file type
data = scitex.io.load("file.csv")  # or .npy, .pkl, .json, .mat, etc.

# Save with auto directory creation
scitex.io.save(results, "output/results.csv")
```

### 2. Reproducible Experiments
```python
# Initialize with automatic logging and seed management
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
    sys, plt, seed=42
)
```

### 3. Publication-Ready Plots
```python
# Enhanced matplotlib with data tracking
fig, ax = scitex.plt.subplots()
ax.plot(x, y)
ax.set_xyt("Time (s)", "Voltage (mV)", "My Experiment")
scitex.io.save(fig, "plot.png")  # Also saves plot_data.csv!
```

### 4. Scientific Computing Tools
```python
# Signal processing
filtered = scitex.dsp.bandpass(signal, 1, 50, fs=1000)

# Statistics with formatting
result = scitex.stats.corr_test(x, y)
print(f"r={result['r']:.3f}, p={result['p']:.4f}")
```

## 📚 Documentation

- **PyPI**: https://pypi.org/project/scitex/
- **GitHub**: https://github.com/ywatanabe1989/SciTeX-Code
- **Docs**: https://scitex.readthedocs.io (coming soon)
- **Examples**: See `examples/` directory

## 🎯 Who Should Use SciTeX?

Perfect for:
- Scientific Python projects
- Machine learning experiments  
- Data analysis pipelines
- Research requiring reproducibility
- Projects with mixed file formats

## 🔥 What's New in v2.0.0

- Complete rebranding from mngs to SciTeX
- 100% test coverage on core modules
- Enhanced documentation and examples
- Improved API consistency
- Better error messages and debugging

## 🤝 Contributing

We welcome contributions! Please check our GitHub repository for:
- Issue tracker
- Development guidelines
- Feature requests

## 📊 Stats

- **Modules**: 20+ specialized modules
- **Functions**: 200+ utility functions
- **File Formats**: 20+ supported formats
- **Test Coverage**: 100% on core modules

## 🙏 Acknowledgments

Special thanks to all contributors who helped make this release possible!

---

**Start making your scientific Python workflow lazy today!**

```bash
pip install scitex
```

For questions or support, please visit our [GitHub repository](https://github.com/ywatanabe1989/SciTeX-Code).