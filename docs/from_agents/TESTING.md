# SciTeX Testing Guide

## Overview

This document provides comprehensive guidelines for testing in the SciTeX project. The project maintains excellent test coverage (96%+) across 447 test files with 503+ test functions.

## Table of Contents

1. [Test Coverage Standards](#test-coverage-standards)
2. [Running Tests](#running-tests)
3. [Coverage Reporting](#coverage-reporting)
4. [CI/CD Integration](#cicd-integration)
5. [Pre-commit Hooks](#pre-commit-hooks)
6. [Writing Tests](#writing-tests)
7. [Test Organization](#test-organization)
8. [Mocking Guidelines](#mocking-guidelines)
9. [Performance Testing](#performance-testing)
10. [Troubleshooting](#troubleshooting)

## Test Coverage Standards

### Current Status
- **Overall Coverage**: 96%+
- **Test Files**: 447
- **Test Functions**: 503+
- **Minimum Required**: 85%

### Coverage Goals
- Maintain minimum 85% coverage for all modules
- Achieve 90%+ coverage for critical modules (ai, io, plt)
- 100% coverage for new features
- Exclude only genuinely untestable code

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/scitex/io/

# Run specific test file
pytest tests/scitex/io/test__save.py

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

### Using the Test Runner Script
```bash
# Run with coverage report
./run_tests_with_coverage.sh

# Generate HTML report
./run_tests_with_coverage.sh --html

# Set minimum coverage threshold
./run_tests_with_coverage.sh --min-coverage 90

# Run specific tests with coverage
./run_tests_with_coverage.sh tests/scitex/ai/
```

### Using Tox for Multi-Version Testing
```bash
# Run all environments
tox

# Run specific Python version
tox -e py39

# Run linting only
tox -e lint

# Run coverage report
tox -e coverage

# Run security checks
tox -e security
```

## Coverage Reporting

### Configuration (.coveragerc)
The project uses a comprehensive coverage configuration:

```ini
[run]
source = src/scitex
branch = True
parallel = True
omit = 
    */tests/*
    */__pycache__/*
    */.old/*
    */migrations/*
    */conftest.py
    */setup.py

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    if TYPE_CHECKING:
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    except ImportError:
```

### Generating Reports

#### Terminal Report
```bash
pytest --cov=scitex --cov-report=term-missing
```

#### HTML Report
```bash
pytest --cov=scitex --cov-report=html
# View at htmlcov/index.html
```

#### XML Report (for CI/CD)
```bash
pytest --cov=scitex --cov-report=xml
```

## CI/CD Integration

### GitHub Actions
The project uses GitHub Actions for automated testing:

```yaml
# .github/workflows/test-with-coverage.yml
- Tests across Python 3.8-3.12
- Uploads coverage to Codecov
- Generates coverage artifacts
- Fails if coverage < 85%
```

### GitLab CI
Existing pipeline configuration:
```yaml
# .gitlab-ci.yml
- Runs tests on merge requests
- Generates coverage reports
- Stores test artifacts
```

### Coverage Badge
Add to README.md:
```markdown
[![codecov](https://codecov.io/gh/ywatanabe1989/scitex/branch/main/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex)
```

## Pre-commit Hooks

### Setup
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configured Hooks
1. **Code Formatting**
   - Black (Python formatter)
   - isort (Import sorter)
   - End-of-file fixer
   - Trailing whitespace remover

2. **Code Quality**
   - Flake8 (Linting)
   - MyPy (Type checking)
   - Bandit (Security)

3. **Custom Hooks**
   - No commits to main/master
   - Test runner (ensures tests pass)

## Writing Tests

### Test Structure Template
```python
#!/usr/bin/env python3
"""Tests for module_name functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd

# Import the module to test
from scitex.module import function_name


class TestFunctionName:
    """Test suite for function_name."""
    
    @pytest.fixture
    def sample_data(self):
        """Provide sample data for tests."""
        return np.random.rand(10, 20)
    
    def test_basic_functionality(self, sample_data):
        """Test basic function operation."""
        result = function_name(sample_data)
        assert result is not None
        assert result.shape == sample_data.shape
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty input
        assert function_name([]) == expected_empty_result
        
        # Single element
        assert function_name([1]) == expected_single_result
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError, match="Invalid input"):
            function_name(None)
    
    @pytest.mark.parametrize("input_val,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_parameterized(self, input_val, expected):
        """Test with multiple input/output pairs."""
        assert function_name(input_val) == expected
```

### Best Practices

1. **Test Naming**
   - Use descriptive names: `test_save_handles_unicode_filenames`
   - Group related tests in classes
   - Prefix test methods with `test_`

2. **Test Organization**
   - One test file per source file
   - Mirror source directory structure
   - Use fixtures for common setup

3. **Assertions**
   - One logical assertion per test
   - Use specific assertions (pytest.approx for floats)
   - Include helpful assertion messages

4. **Test Data**
   - Use fixtures for reusable test data
   - Keep test data minimal but representative
   - Use factories for complex objects

## Test Organization

### Directory Structure
```
tests/
├── conftest.py          # Shared fixtures
├── scitex/
│   ├── ai/
│   │   ├── conftest.py  # Module-specific fixtures
│   │   ├── test__init__.py
│   │   └── test_classification_reporter.py
│   ├── io/
│   │   ├── test__save.py
│   │   └── test__load.py
│   └── ...
└── integration/         # Integration tests
    └── test_module_integration.py
```

### Fixture Organization
```python
# tests/conftest.py
@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory."""
    return tmp_path

@pytest.fixture
def sample_dataframe():
    """Provide sample pandas DataFrame."""
    return pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

# Module-specific fixtures in tests/scitex/module/conftest.py
```

## Mocking Guidelines

### When to Mock
- External services (APIs, databases)
- File system operations (in unit tests)
- Time-dependent functionality
- Random number generation
- Hardware dependencies

### Mocking Examples
```python
# Mock file operations
@patch('builtins.open', new_callable=mock_open, read_data='data')
def test_read_file(mock_file):
    result = read_function('file.txt')
    mock_file.assert_called_once_with('file.txt', 'r')

# Mock external dependencies
@patch('scitex.ai.genai.openai.OpenAI')
def test_ai_generation(mock_openai):
    mock_openai.return_value.generate.return_value = "response"
    result = generate_text("prompt")
    assert result == "response"

# Mock time
@patch('time.time', return_value=1234567890)
def test_timestamp(mock_time):
    result = get_timestamp()
    assert result == 1234567890
```

## Performance Testing

### Benchmarking Tests
```python
@pytest.mark.benchmark
def test_performance(benchmark):
    """Test function performance."""
    result = benchmark(expensive_function, arg1, arg2)
    assert result == expected

# Run benchmarks
pytest --benchmark-only
```

### Memory Testing
```python
def test_memory_usage():
    """Test memory efficiency."""
    import tracemalloc
    
    tracemalloc.start()
    result = memory_intensive_function()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert peak < 100 * 1024 * 1024  # Less than 100MB
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```python
   # Add to test file if needed
   import sys
   import os
   sys.path.insert(0, os.path.abspath('src'))
   ```

2. **Fixture Not Found**
   - Ensure conftest.py is in the correct directory
   - Check fixture scope and availability

3. **Coverage Missing Lines**
   - Check .coveragerc for exclusions
   - Ensure tests actually execute the code
   - Use `--cov-report=term-missing` to see missed lines

4. **Slow Tests**
   - Use pytest-xdist for parallel execution
   - Mock expensive operations
   - Use fixtures to avoid repeated setup

### Debugging Tests
```bash
# Run with debugging
pytest --pdb

# Run with print statements visible
pytest -s

# Run with full traceback
pytest --tb=long

# Run specific test with debugging
pytest -k "test_specific_function" --pdb
```

## Continuous Improvement

### Monthly Tasks
1. Review coverage reports
2. Update slow test list
3. Refactor complex tests
4. Update this documentation

### Metrics to Track
- Overall coverage percentage
- Coverage by module
- Test execution time
- Flaky test frequency

### Resources
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py documentation](https://coverage.readthedocs.io/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [tox documentation](https://tox.wiki/)

---

*Last updated: 2025-06-10*
*Maintained by: SciTeX Development Team*