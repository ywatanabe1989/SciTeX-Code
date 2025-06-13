<!-- ---
!-- title: README.md
!-- author: ywatanabe
!-- date: 2024-11-03 01:50:49
!-- --- -->

# Testing Guide

## Setup

```bash
pip install pytest pytest-cov coverage
```

## Running Tests

### pytest

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_specific.py

# Specific test function
pytest tests/test_specific.py::test_function
```

### unittest

```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest tests/test_specific.py

# Run specific test class
python -m unittest tests.test_specific.TestClass

# Run specific test method
python -m unittest tests.test_specific.TestClass.test_method
```

## Coverage

```bash
# Generate coverage report
coverage run -m pytest
coverage report
coverage html  # Creates htmlcov/index.html
```

## Test File Structure

```python
# test_example.py
import pytest
from package import module

def test_function():
    assert module.function() == expected

class TestClass:
    def test_method(self):
        assert module.method() == expected
```

## Common Assertions

```python
assert value == expected
assert value != expected
assert value is None
assert value is not None
assert value in container
assert value not in container
assert callable(value)
assert isinstance(value, type)
assert raises(Exception, callable, args)
```

## `generate_test_structure.sh`
``` bash
#!/bin/bash
# Time-stamp: "2024-11-03 01:30:42 (ywatanabe)"
# File: ./scitex_repo/docs/generate_test_structure.sh

SRC="./src/scitex/"
TGT="./tests/"

# Create directory structure
find "$SRC" -type d \
     ! -path "*/\.*" \
     ! -path "*/deprecated*" \
     ! -path "*/archive*" \
     ! -path "*/backup*" \
     ! -path "*/tmp*" \
     ! -path "*/temp*" \
     ! -path "*/__pycache__*" \
     | while read -r dir; do
    test_dir="${dir/src/tests}"
    mkdir -p "$test_dir"
done

# Create test files for each Python file
find "$SRC" -name "*.py" \
     ! -path "*/\.*" \
     ! -path "*/deprecated*" \
     ! -path "*/archive*" \
     ! -path "*/backup*" \
     ! -path "*/tmp*" \
     ! -path "*/temp*" \
     ! -path "*/__pycache__*" \
     | while read -r src_file; do
    test_file="${src_file/src/tests}"
    test_file="$(dirname "$test_file")/test_$(basename "${test_file%.py}").py"

    if [[ ! -f "$test_file" ]]; then
        cat > "$test_file" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from scitex.${src_file#$SRC} import *

def test_placeholder():
    pass
EOF
    fi
done

# EOF
```
