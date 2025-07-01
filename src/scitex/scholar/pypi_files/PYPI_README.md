# SciTeX-Scholar PyPI Publishing Guide

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

2. **API Tokens**: Generate tokens from your account settings:
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

3. **Configure Credentials**: 
   ```bash
   cp .pypirc.template ~/.pypirc
   # Edit ~/.pypirc with your tokens
   chmod 600 ~/.pypirc
   ```

## Building the Package

```bash
# Run the build script
./build_for_pypi.sh
```

This will:
- Clean previous builds
- Install/update build tools
- Build source and wheel distributions
- Check the distributions with twine

## Testing on TestPyPI

1. **Upload to TestPyPI**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Test Installation**:
   ```bash
   # Create a test environment
   python -m venv test_env
   source test_env/bin/activate  # On Windows: test_env\Scripts\activate
   
   # Install from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ scitex-scholar
   
   # Test it works
   python -c "import scitex_scholar; print(scitex_scholar.__version__)"
   ```

## Publishing to PyPI

Once tested successfully:

```bash
python -m twine upload dist/*
```

## Post-Publication

1. **Verify Installation**:
   ```bash
   pip install scitex-scholar
   ```

2. **Update GitHub**:
   - Tag the release: `git tag v0.1.0`
   - Push tags: `git push --tags`
   - Create GitHub release

3. **Announce**:
   - Update project README with PyPI badge
   - Share on social media/forums

## Version Management

To release a new version:
1. Update version in `pyproject.toml`
2. Update version in `src/scitex_scholar/__init__.py`
3. Update `CHANGELOG.md`
4. Rebuild and republish

## Troubleshooting

- **Name conflict**: If "scitex-scholar" is taken, try "scitexscholar" or "scitex-scholar-yw"
- **Description too long**: PyPI has limits on description length
- **Missing dependencies**: Ensure all dependencies are in pyproject.toml
- **Upload errors**: Check your ~/.pypirc configuration