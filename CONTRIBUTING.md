# Contributing to SciTeX

Thank you for your interest in contributing to SciTeX! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Contributions](#making-contributions)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Style Guide](#style-guide)
8. [Submitting Changes](#submitting-changes)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/scitex_repo.git
   cd scitex_repo
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ywatanabe1989/scitex_repo.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   make install
   # Or manually:
   pip install -e .
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Making Contributions

### 1. Choose an Issue

- Check the [issue tracker](https://github.com/ywatanabe1989/scitex_repo/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

Create a branch for your feature or fix:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Write Code

Follow these guidelines:
- Keep changes focused and atomic
- Write clear, self-documenting code
- Add docstrings to all functions and classes
- Follow the existing code style

### 4. Add Tests

All new features must include tests:
```python
# tests/scitex/module_name/test_new_feature.py
import pytest
import scitex

def test_new_feature():
    """Test description."""
    result = scitex.module.new_feature(input_data)
    assert result == expected_output

def test_new_feature_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError):
        scitex.module.new_feature(invalid_input)
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
make test

# Run specific module tests
make test-module MODULE=gen

# Run tests with coverage
make test-coverage

# Run tests in parallel
make test-fast
```

### Test Requirements

- Maintain or improve test coverage (currently 100%)
- Test both normal cases and edge cases
- Include integration tests for cross-module features
- Ensure all tests pass before submitting

### Test Structure

```
tests/
├── scitex/
│   ├── module_name/
│   │   ├── test_function1.py
│   │   ├── test_function2.py
│   │   └── test_module_comprehensive.py
│   └── ...
└── integration/
    └── test_module_integration.py
```

## Documentation

### Docstring Format

Use NumPy-style docstrings:

```python
def function_name(param1, param2=None):
    """
    Brief description of function.
    
    Longer description if needed, explaining the purpose
    and behavior of the function.
    
    Parameters
    ----------
    param1 : type
        Description of param1.
    param2 : type, optional
        Description of param2. Default is None.
    
    Returns
    -------
    return_type
        Description of return value.
    
    Raises
    ------
    ValueError
        When invalid parameters are provided.
    
    Examples
    --------
    >>> result = function_name(data)
    >>> print(result)
    expected_output
    
    Notes
    -----
    Additional information about the implementation.
    
    See Also
    --------
    related_function : Related functionality.
    """
    pass
```

### Updating Documentation

1. Update docstrings in the code
2. Update module documentation in `docs/scitex_guidelines/modules/`
3. Add examples if introducing new features
4. Build and check documentation:
   ```bash
   make docs
   make docs-serve  # View at http://localhost:8000
   ```

## Style Guide

### Code Style

- Follow PEP 8 with 88-character line limit (Black's default)
- Use meaningful variable names
- Prefer clarity over cleverness

### Automatic Formatting

```bash
# Format code automatically
make format

# Check code style
make lint
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Local imports

```python
import os
import sys

import numpy as np
import pandas as pd

from ..decorators import torch_fn
from ..utils import helper_function
```

## Submitting Changes

### 1. Commit Your Changes

Write clear commit messages:
```bash
git add .
git commit -m "Add feature: brief description

- Detailed explanation of what changed
- Why the change was made
- Any breaking changes or migrations needed"
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:
   - Description of changes
   - Related issue numbers
   - Test results
   - Documentation updates

### 4. PR Review Process

- PRs require at least one review
- Address review comments promptly
- Keep the PR updated with the main branch:
  ```bash
  git fetch upstream
  git rebase upstream/main
  ```

## Additional Resources

### Project Structure

```
scitex_repo/
├── src/scitex/          # Source code
├── tests/             # Test files
├── docs/              # Documentation
├── examples/          # Example scripts
├── project_management/# Project tracking
└── .github/workflows/ # CI/CD configuration
```

### Useful Commands

```bash
# Run specific test file
pytest tests/scitex/io/test_save.py -v

# Check test coverage for a module
pytest tests/scitex/gen --cov=src/scitex/gen

# Profile code
python -m cProfile -s cumulative your_script.py

# Find TODO items
grep -r "TODO" src/scitex
```

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in discussions
- Contact maintainers

## Thank You!

Your contributions make SciTeX better for everyone. We appreciate your time and effort in improving the project!