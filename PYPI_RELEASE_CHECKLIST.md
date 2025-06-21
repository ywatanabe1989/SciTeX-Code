# PyPI Release Checklist for SciTeX

## Pre-release Checklist

### ✅ Code Quality
- [x] All imports use 'scitex' instead of 'scitex'
- [x] Version number updated in both `pyproject.toml` and `__version__.py` (currently 2.0.0)
- [x] All temporary files cleaned up (__pycache__, *.pyc, *.egg-info, build/, dist/)
- [x] Package structure follows best practices

### 📋 Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG or release notes prepared
- [ ] API documentation updated

### 🧪 Testing
- [ ] All tests pass locally
- [ ] CI/CD pipeline passes
- [ ] Package installs correctly in a clean environment

### 📦 Package Configuration
- [x] pyproject.toml properly configured
- [x] Package name: scitex
- [x] Version: 2.0.0
- [x] Description and metadata present
- [x] Dependencies listed
- [x] Project URLs configured

## Build and Release Steps

1. **Clean the project**
   ```bash
   bash scripts/cleanup_for_pypi.sh
   ```

2. **Install build tools** (if not already installed)
   ```bash
   pip install build twine
   ```

3. **Build the package**
   ```bash
   python -m build
   ```

4. **Check the built distributions**
   ```bash
   ls -la dist/
   ```

5. **Test the package locally** (optional but recommended)
   ```bash
   pip install dist/scitex-2.0.0-py3-none-any.whl
   python -c "import scitex; print(scitex.__version__)"
   pip uninstall scitex
   ```

6. **Upload to TestPyPI first** (optional but recommended)
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

7. **Upload to PyPI**
   ```bash
   python -m twine upload dist/*
   ```

8. **Tag the release**
   ```bash
   git tag -a v2.0.0 -m "Release version 2.0.0: Migration from scitex to scitex"
   git push origin v2.0.0
   ```

## Post-release

- [ ] Verify package on PyPI: https://pypi.org/project/scitex/
- [ ] Test installation: `pip install scitex`
- [ ] Update project documentation with installation instructions
- [ ] Announce the release

## Notes

- The package has been renamed from 'scitex' to 'scitex'
- Version 2.0.0 marks this major transition
- All imports have been updated throughout the codebase
- Legacy references only exist in example/documentation files outside the main package