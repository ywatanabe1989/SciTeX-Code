# Pre-commit Setup Guide

## Installation

```bash
pip install pre-commit
pre-commit install
```

## Features

- **Black**: Code formatting (88 char line length)
- **isort**: Import sorting (black-compatible)
- **flake8**: Linting with scientific Python conventions
- **bandit**: Security vulnerability scanning
- **mypy**: Type checking
- **pydocstyle**: Docstring validation (NumPy style)
- **nbstripout**: Clean Jupyter notebooks
- **shellcheck**: Shell script validation

## Usage

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files (automatic on commit)
git commit -m "message"

# Skip hooks temporarily
git commit -m "message" --no-verify

# Update hooks
pre-commit autoupdate
```

## Configuration

Edit `.pre-commit-config.yaml` to:
- Add/remove hooks
- Modify arguments
- Exclude paths

## Benefits

1. **Consistent code style** across contributors
2. **Catch issues early** before code review
3. **Automated quality checks** on every commit
4. **Security scanning** for common vulnerabilities
5. **Clean notebooks** without output cells

---
Pre-commit hooks ensure code quality automatically! 🎯