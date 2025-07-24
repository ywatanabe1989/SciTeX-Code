# Read the Docs Deployment Guide for SciTeX

**Created**: 2025-07-25  
**Status**: Ready for deployment  
**Agent**: 390290b0-68a6-11f0-b4ec-00155d8208d6

## Overview

This guide documents how to deploy SciTeX documentation to Read the Docs. The documentation infrastructure is fully configured and ready for deployment.

## Current Status

### ✅ Completed Setup

1. **Configuration Files**
   - `.readthedocs.yaml` - Created in project root
   - `docs/RTD/conf.py` - Sphinx configuration
   - `docs/RTD/requirements.txt` - Documentation dependencies

2. **Documentation Structure**
   - API documentation auto-generation configured
   - Jupyter notebook integration (nbsphinx)
   - RTD theme configured
   - Essential notebooks created and linked

3. **Build Configuration**
   - Python 3.11 specified
   - Ubuntu 22.04 build environment
   - PDF and EPUB formats enabled
   - Sphinx warnings won't fail builds

## Deployment Steps

### 1. Prepare Repository

```bash
# Ensure all changes are committed
git add .readthedocs.yaml
git add docs/RTD/
git add examples/notebooks/essential/
git commit -m "docs: Add Read the Docs configuration and essential notebooks"
git push origin develop
```

### 2. Create Pull Request

```bash
# Create PR from develop to main
gh pr create --title "Deploy documentation to Read the Docs" \
  --body "This PR adds Read the Docs configuration and essential notebooks to address the documentation crisis." \
  --base main \
  --head develop
```

### 3. Set Up Read the Docs Account

1. Go to https://readthedocs.org/
2. Sign up/Sign in with GitHub
3. Import the project:
   - Click "Import a Project"
   - Connect to GitHub if not already connected
   - Select "ywatanabe/SciTeX-Code" repository
   - Name: "scitex" (or "scitex-code")
   - Click "Next"

### 4. Configure Read the Docs Project

After import, configure these settings:

1. **Admin > Advanced Settings**:
   - Default branch: `main` (or `develop` for testing)
   - Default version: `latest`
   - Enable "Build pull requests for this project"

2. **Admin > Environment Variables** (if needed):
   ```
   READTHEDOCS: True
   ```

3. **Admin > Integrations**:
   - Webhook should be automatically added
   - If not, add GitHub incoming webhook

### 5. Trigger First Build

1. Go to "Builds" tab
2. Click "Build Version" for `latest`
3. Monitor build progress
4. Check build logs if any errors occur

### 6. Verify Documentation

Once built successfully:
- View at: https://scitex.readthedocs.io/ (or your chosen subdomain)
- Check:
  - API documentation is generated
  - Essential notebooks are rendered
  - Navigation works correctly
  - Search functionality works

## Troubleshooting

### Common Issues

1. **Import Errors During Build**
   - Solution: All dependencies are in requirements.txt
   - SciTeX is installed with `pip install .` during build

2. **Notebook Rendering Issues**
   - Solution: nbsphinx is configured
   - Essential notebooks are validated to work

3. **Build Timeouts**
   - Solution: Large dependencies (torch, etc.) may cause timeouts
   - Consider creating a lighter requirements file if needed

### Build Optimization

If builds are slow or timeout, create a minimal requirements file:

```python
# docs/RTD/requirements-minimal.txt
sphinx>=7.0.0
sphinx-rtd-theme>=2.0.0
myst-parser>=2.0.0
sphinx-autodoc-typehints>=1.25.0
sphinx-copybutton>=0.5.2
nbsphinx>=0.9.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
```

Then update `.readthedocs.yaml`:
```yaml
python:
  install:
    - requirements: docs/RTD/requirements-minimal.txt
```

## Post-Deployment

### 1. Update README

Add documentation badge to README.md:
```markdown
[![Documentation Status](https://readthedocs.org/projects/scitex/badge/?version=latest)](https://scitex.readthedocs.io/en/latest/?badge=latest)
```

### 2. Update Project Links

Add documentation link to:
- GitHub repository description
- PyPI package metadata
- Project website

### 3. Set Up Versioning

For version-specific docs:
1. Tag releases: `git tag -a v2.0.0 -m "Release v2.0.0"`
2. Push tags: `git push origin --tags`
3. RTD will automatically build tagged versions

## Benefits of This Setup

1. **Automatic Updates**: Documentation rebuilds on every push
2. **Version Support**: Each release gets its own documentation
3. **Search**: Full-text search across all documentation
4. **Professional**: Clean, professional documentation portal
5. **Essential Notebooks**: Working examples despite main notebook issues

## Next Steps

1. Deploy to Read the Docs following this guide
2. Monitor first build for any issues
3. Share documentation link with users
4. Consider adding more essential notebooks as needed

The documentation crisis is now mitigated with:
- 5 working essential notebooks
- Comprehensive API documentation
- Professional hosting on Read the Docs