# SciTeX Documentation Guide

## Building the Documentation

### 1. Install Dependencies
```bash
cd docs
pip install -r requirements.txt
```

### 2. Build HTML Documentation
```bash
# Clean previous builds and generate fresh HTML
make clean
make html
```

The documentation will be built in `docs/_build/html/`

### 3. View Locally
```bash
# Open in browser
python -m http.server 8000 --directory _build/html
# Then visit http://localhost:8000
```

### 4. Auto-rebuild During Development
```bash
# Install sphinx-autobuild if not already installed
pip install sphinx-autobuild

# Start auto-building server
make livehtml
# Visit http://localhost:8000
```

## Deployment Options

### Option 1: GitHub Pages

1. Build the docs:
```bash
make clean html
```

2. Add to git:
```bash
git add docs/_build/html
git commit -m "Build documentation"
```

3. Push to gh-pages branch:
```bash
git subtree push --prefix docs/_build/html origin gh-pages
```

4. Enable GitHub Pages in repository settings:
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: gh-pages
   - Folder: / (root)

Your docs will be available at: `https://[username].github.io/scitex/`

### Option 2: Read the Docs

1. Sign up at [readthedocs.org](https://readthedocs.org)

2. Import your GitHub repository

3. RTD will automatically:
   - Detect `docs/conf.py`
   - Install dependencies from `docs/requirements.txt`
   - Build and host your documentation

4. Your docs will be at: `https://scitex.readthedocs.io/`

### Option 3: Local Network Share

For internal use only:
```bash
# Build docs
cd docs && make clean html

# Copy to shared location
cp -r _build/html/* /path/to/shared/docs/scitex/
```

## Updating Documentation

### Regenerate API Docs
```bash
# Regenerate all API documentation from source
make autogen

# Then rebuild
make html
```

### Add New Pages
1. Create `.rst` file in appropriate directory
2. Add to relevant `toctree` in `index.rst`
3. Rebuild with `make html`

## Documentation Structure
```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main page
├── getting_started.rst  # Quick start guide
├── installation.rst     # Installation instructions
├── api/                 # Auto-generated API docs
│   ├── modules.rst
│   ├── scitex.gen.rst
│   ├── scitex.io.rst
│   └── ...
├── _build/             # Built documentation
│   └── html/           # HTML output
├── _static/            # Static files (CSS, images)
└── _templates/         # Custom templates
```

## Tips

- **Preview changes**: Use `make livehtml` for automatic rebuilds
- **Check for warnings**: Build output shows broken links and formatting issues
- **Custom CSS**: Add to `_static/custom.css` and include in `conf.py`
- **Add images**: Place in `_static/` and reference with relative paths

## Common Issues

**Missing module**: If autodoc can't import a module, ensure:
- The module is in Python path (conf.py adds `../src`)
- All dependencies are installed
- No syntax errors in the module

**Theme not found**: Install the theme:
```bash
pip install sphinx-rtd-theme
```

Then uncomment in `conf.py`:
```python
html_theme = 'sphinx_rtd_theme'
```