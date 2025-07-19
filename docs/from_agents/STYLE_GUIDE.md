# SciTeX Style Guide

## Overview
This comprehensive style guide defines coding standards for the SciTeX project, covering Python code style, documentation, testing, and development practices.

## Table of Contents
1. [Python Style](#python-style)
2. [Import Organization](#import-organization)
3. [Code Organization](#code-organization)
4. [Error Handling](#error-handling)
5. [Testing Standards](#testing-standards)
6. [Documentation Standards](#documentation-standards)
7. [Git Practices](#git-practices)
8. [Development Workflow](#development-workflow)

## Python Style

### General Rules
- Follow PEP 8 with exceptions noted below
- Maximum line length: 88 characters (Black default)
- Use Black for code formatting
- Use isort for import sorting

### Code Formatting

```python
# Good: Clear spacing and organization
def process_data(
    data: np.ndarray,
    sample_rate: float,
    window_size: int = 256,
    overlap: float = 0.5,
) -> Tuple[np.ndarray, np.ndarray]:
    """Process signal data with windowing."""
    n_samples = data.shape[0]
    hop_size = int(window_size * (1 - overlap))
    
    # Process each window
    results = []
    for start in range(0, n_samples - window_size, hop_size):
        window = data[start : start + window_size]
        processed = _process_window(window, sample_rate)
        results.append(processed)
        
    return np.array(results), compute_timestamps(results, sample_rate)
```

### Type Hints
Always use type hints for function signatures:

```python
from typing import Dict, List, Optional, Tuple, Union

def load_data(
    filepath: Union[str, Path],
    columns: Optional[List[str]] = None,
    dtype: Optional[Dict[str, type]] = None,
) -> pd.DataFrame:
    """Load data from file."""
    pass
```

## Import Organization

### Order and Grouping
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal

# Local imports
import scitex
from scitex.io import load, save
from scitex.dsp import filter_signal

# Relative imports (only within package)
from . import utils
from ..core import base
```

### Import Style
```python
# Good: Clear what's being imported
from scitex.io import load_json, save_json
import numpy as np

# Bad: Star imports (except in __init__.py)
from scitex.io import *

# Bad: Multiple imports on one line
import os, sys, json
```

## Code Organization

### Module Structure
```python
#!/usr/bin/env python3
"""
Module description.

This module provides functionality for...
"""

# Imports
import numpy as np

# Constants
DEFAULT_SAMPLE_RATE = 1000
SUPPORTED_FORMATS = ["npy", "pkl", "h5"]

# Private module variables
_cache = {}

# Public classes
class DataProcessor:
    """Process data with various methods."""
    pass

# Public functions
def main_function():
    """Main public function."""
    pass

# Private functions
def _helper_function():
    """Private helper function."""
    pass

# Script execution
if __name__ == "__main__":
    main()
```

### Function Design

```python
# Good: Single responsibility, clear interface
def filter_signal(
    data: np.ndarray,
    low_freq: float,
    high_freq: float,
    sample_rate: float,
) -> np.ndarray:
    """Apply bandpass filter to signal."""
    nyquist = sample_rate / 2
    low_norm = low_freq / nyquist
    high_norm = high_freq / nyquist
    
    b, a = signal.butter(4, [low_norm, high_norm], btype='band')
    return signal.filtfilt(b, a, data)

# Bad: Multiple responsibilities, unclear interface
def process(data, params):
    """Process data."""
    # Filter data
    # Normalize data  
    # Save results
    # Plot results
    pass
```

### Class Design

```python
class SignalProcessor:
    """Process signals with various methods."""
    
    def __init__(self, sample_rate: float):
        """Initialize processor with sample rate."""
        self.sample_rate = sample_rate
        self._cache = {}
        
    @property
    def nyquist(self) -> float:
        """Nyquist frequency."""
        return self.sample_rate / 2
        
    def process(self, data: np.ndarray) -> np.ndarray:
        """Process signal data."""
        # Implementation
        pass
        
    def _validate_data(self, data: np.ndarray) -> None:
        """Validate input data."""
        if data.ndim not in [1, 2]:
            raise ValueError("Data must be 1D or 2D")
```

## Error Handling

### Exceptions
```python
# Good: Specific exceptions with informative messages
def load_data(filepath: str) -> Any:
    """Load data from file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    ext = Path(filepath).suffix
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {ext}. "
            f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )

# Good: Custom exceptions for domain-specific errors
class ConvergenceError(Exception):
    """Algorithm failed to converge."""
    pass
```

### Validation
```python
def process_array(data: np.ndarray, axis: int = -1) -> np.ndarray:
    """Process array along specified axis."""
    # Validate inputs
    if not isinstance(data, np.ndarray):
        raise TypeError(f"Expected np.ndarray, got {type(data)}")
        
    if axis >= data.ndim or axis < -data.ndim:
        raise ValueError(
            f"axis {axis} is out of bounds for array of dimension {data.ndim}"
        )
        
    # Process data
    return np.mean(data, axis=axis)
```

## Testing Standards

### Test Organization
```python
# tests/scitex/dsp/test_filter.py
import pytest
import numpy as np
from scitex.dsp import filter_signal


class TestFilterSignal:
    """Test filter_signal function."""
    
    def test_bandpass_filter_removes_frequencies(self):
        """Test that bandpass filter removes out-of-band frequencies."""
        # Create test signal with known frequencies
        sample_rate = 1000
        t = np.linspace(0, 1, sample_rate)
        signal = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 100 * t)
        
        # Apply filter
        filtered = filter_signal(signal, 20, 80, sample_rate)
        
        # Verify frequencies
        # ... assertions ...
        
    def test_filter_preserves_signal_length(self):
        """Test that filtering preserves signal length."""
        signal = np.random.randn(1000)
        filtered = filter_signal(signal, 1, 50, 250)
        assert len(filtered) == len(signal)
        
    def test_filter_raises_on_invalid_frequencies(self):
        """Test that filter raises error for invalid frequencies."""
        signal = np.random.randn(1000)
        with pytest.raises(ValueError, match="Invalid frequency"):
            filter_signal(signal, 100, 50, 250)  # low > high
```

### Test Naming
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<specific_behavior>`

### Test Structure
```python
# Arrange - Act - Assert pattern
def test_function_behavior():
    """Test specific behavior."""
    # Arrange: Set up test data
    input_data = create_test_data()
    expected = compute_expected_result()
    
    # Act: Call function
    result = function_under_test(input_data)
    
    # Assert: Verify result
    assert result == expected
```

## Documentation Standards

### Module Documentation
```python
"""
Module name and brief description.

Detailed description of module functionality, main use cases,
and any important notes.

Examples
--------
>>> import scitex.module
>>> result = scitex.module.function(data)

Notes
-----
Implementation details or usage notes.
"""
```

### API Documentation
All public APIs must have:
1. One-line summary
2. Parameters section with types
3. Returns section with types
4. At least one example
5. Raises section (if applicable)

### Code Comments
```python
# Good: Explains why, not what
# Use FFT for efficiency when signal length > 1000
if len(signal) > 1000:
    result = np.fft.fft(signal)
else:
    result = direct_computation(signal)

# Bad: Redundant comment
# Increment counter by 1
counter += 1
```

## Git Practices

### Commit Messages
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/maintenance

Example:
```
feat: Add wavelet transform to dsp module

- Implement continuous wavelet transform
- Add support for multiple wavelet families
- Include visualization utilities

Closes #123
```

### Branch Naming
- Feature: `feature/descriptive-name`
- Bugfix: `fix/issue-description`
- Refactor: `refactor/module-name`

## Development Workflow

### Pre-commit Checks
Configure `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length", "88", "--extend-ignore", "E203"]
```

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] Has appropriate type hints
- [ ] Includes docstrings
- [ ] Has unit tests
- [ ] Passes all CI checks
- [ ] No code duplication
- [ ] Clear error messages

### Performance Considerations
```python
# Good: Document performance characteristics
def compute_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute correlation between arrays.
    
    Time complexity: O(n)
    Space complexity: O(1)
    
    For large arrays (n > 1e6), consider using compute_correlation_chunked.
    """
    pass
```

## Tool Configuration

### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Summary
This style guide ensures consistent, maintainable code across the SciTeX project. When in doubt:
1. Follow PEP 8
2. Be consistent with existing code
3. Prioritize readability
4. Document your intentions

Remember: Code is read more often than it's written. Make it easy for others (including future you) to understand.