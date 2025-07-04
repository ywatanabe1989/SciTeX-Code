# Pre-commit Hooks Setup Guide for SciTeX

## Overview

Pre-commit hooks help maintain code quality by automatically checking and fixing issues before commits. This guide explains how to set up and use pre-commit hooks for the SciTeX project.

## Installation

### 1. Install pre-commit
```bash
pip install pre-commit
```

### 2. Install the git hook scripts
```bash
pre-commit install
```

This will install pre-commit into your git hooks. pre-commit will now run automatically on `git commit`.

### 3. (Optional) Run against all files
```bash
pre-commit run --all-files
```

This is useful when setting up pre-commit in an existing repository.

## Configuration

The pre-commit configuration is stored in `.pre-commit-config.yaml` and includes:

### Code Quality Hooks

1. **Black** - Python code formatter
   - Line length: 100 characters
   - Target: Python 3.11

2. **isort** - Python import sorting
   - Profile: black-compatible
   - Line length: 100 characters

3. **Flake8** - Python linting
   - Max line length: 100
   - Ignores: E203, W503, E402
   - Excludes: .old/, legacy_notebooks/

4. **MyPy** - Type checking
   - Ignores missing imports
   - Excludes: tests/, examples/

### Notebook Hooks

5. **nbstripout** - Cleans Jupyter notebooks
   - Removes output cells
   - Removes execution counts
   - Keeps markdown cells intact

### Security & Documentation

6. **Bandit** - Security checks
   - Low severity threshold
   - Excludes: tests/, examples/

7. **pydocstyle** - Docstring style checks
   - Convention: NumPy style
   - Excludes: tests/, examples/

### General Hooks

8. **Pre-commit hooks** - Various checks
   - Trailing whitespace removal
   - End of file fixing
   - YAML/JSON/TOML validation
   - Large file detection (10MB limit)
   - Private key detection
   - Merge conflict detection

9. **pyupgrade** - Python syntax upgrades
   - Target: Python 3.11+

10. **yamllint** - YAML linting
    - Relaxed rules

11. **markdownlint** - Markdown linting
    - Auto-fix enabled

## Usage

### Automatic Checking

Pre-commit will run automatically when you commit:

```bash
git add .
git commit -m "Your commit message"
```

If issues are found:
- Some will be automatically fixed (you'll need to stage the fixes)
- Others will show errors that need manual fixing

### Manual Checking

Run specific hooks:
```bash
# Run black only
pre-commit run black

# Run on specific files
pre-commit run --files src/scitex/*.py

# Run all hooks on all files
pre-commit run --all-files
```

### Skipping Hooks (Emergency Only)

If you need to skip pre-commit hooks:
```bash
git commit --no-verify -m "Emergency fix"
```

**Note:** Use this sparingly as it bypasses quality checks.

## Updating Hooks

Update all hooks to their latest versions:
```bash
pre-commit autoupdate
```

## Troubleshooting

### Common Issues

1. **Hook Installation Failed**
   ```bash
   pre-commit clean
   pre-commit install
   ```

2. **MyPy Import Errors**
   - These are often due to missing type stubs
   - Add to `--ignore-missing-imports` or install type stubs

3. **Black/isort Conflicts**
   - Ensure both use the same line length (100)
   - isort profile should be 'black'

4. **Large File Rejection**
   - Current limit: 10MB
   - Consider using Git LFS for large files
   - Or adjust limit in `.pre-commit-config.yaml`

### Excluded Directories

The following are excluded from all checks:
- `.old/`
- `legacy_notebooks/`
- `*_executed.ipynb`
- `*.bak*`
- `build/`, `dist/`
- `*_out/`
- `executed/`, `backups/`

## Best Practices

1. **Run before pushing**: `pre-commit run --all-files`
2. **Keep hooks updated**: Run `pre-commit autoupdate` monthly
3. **Fix issues promptly**: Don't accumulate technical debt
4. **Configure your editor**: Set up black/isort in your IDE
5. **Document exemptions**: If you need to skip a check, document why

## Integration with CI/CD

Pre-commit hooks are also run in GitHub Actions to ensure all commits meet quality standards. See `.github/workflows/ci.yml` for details.

## Contributing

When adding new hooks:
1. Test thoroughly with `pre-commit try-repo`
2. Document the hook's purpose
3. Ensure it doesn't conflict with existing hooks
4. Consider performance impact

---

For more information, see the [pre-commit documentation](https://pre-commit.com/).