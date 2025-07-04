# Read the Docs Setup for SciTeX

This document explains how to set up and utilize Read the Docs (RTD) for the SciTeX project documentation.

## 🎯 What We've Configured

### 1. **Read the Docs Configuration** (`.readthedocs.yaml`)
- ✅ RTD v2 configuration format
- ✅ Python 3.11 build environment
- ✅ Sphinx documentation builder
- ✅ PDF and ePub export formats
- ✅ Automated dependency installation

### 2. **Enhanced Sphinx Configuration** (`docs/conf.py`)
- ✅ RTD theme integration
- ✅ MyST parser for Markdown support
- ✅ Jupyter notebook integration (nbsphinx)
- ✅ Copy button for code blocks
- ✅ Type hints in documentation
- ✅ GitHub integration links
- ✅ Enhanced navigation and search

### 3. **Documentation Dependencies** (`docs/requirements.txt`)
- ✅ All required Sphinx extensions
- ✅ Scientific computing packages for autodoc
- ✅ Theme and formatting tools
- ✅ Jupyter notebook support

### 4. **Package Configuration** (`setup.cfg`)
- ✅ Updated `docs` extras with modern versions
- ✅ Comprehensive documentation build requirements

## 🚀 Setting Up Read the Docs

### Step 1: Connect to Read the Docs

1. **Visit** [readthedocs.org](https://readthedocs.org/)
2. **Sign in** with your GitHub account
3. **Import** the SciTeX-Code repository:
   - Go to "My Projects" → "Import a Project"
   - Select `ywatanabe1989/SciTeX-Code`
   - Click "Import"

### Step 2: Configure the Project

**Project Settings:**
- **Name**: `scitex` or `SciTeX-Code`
- **Repository URL**: `https://github.com/ywatanabe1989/SciTeX-Code`
- **Default Branch**: `main` (or `develop` for development docs)
- **Language**: `English`
- **Programming Language**: `Python`

**Advanced Settings:**
- **Python Interpreter**: `CPython 3.11`
- **Requirements File**: `docs/requirements.txt`
- **Documentation Type**: `Sphinx Html`
- **Configuration File**: `docs/conf.py`

### Step 3: Build Configuration

RTD will automatically detect and use:
- `.readthedocs.yaml` for build configuration
- `docs/conf.py` for Sphinx settings
- `docs/requirements.txt` for dependencies
- `setup.cfg` extras for package installation

## 📚 Available Documentation Features

### **Main Documentation Site**
Once configured, your documentation will be available at:
```
https://scitex.readthedocs.io/
```

### **Multiple Format Support**
- **HTML**: Interactive web documentation
- **PDF**: Complete documentation as PDF
- **ePub**: E-book format for offline reading

### **Advanced Features**

1. **Jupyter Notebook Integration**
   - All 44+ example notebooks automatically rendered
   - Interactive code examples
   - Execution output preserved

2. **API Documentation**
   - Auto-generated from docstrings
   - Type hints displayed
   - Cross-references between modules

3. **Version Management**
   - Multiple versions (stable, latest, development)
   - Branch-based documentation
   - Tag-based releases

4. **Search & Navigation**
   - Full-text search across all content
   - Hierarchical navigation
   - Cross-references and links

## 🔧 Local Testing

Test the documentation build locally before pushing:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View locally
open _build/html/index.html
```

## 📖 Content Structure

Our RTD setup includes:

### **User Guide**
- Getting Started
- Installation
- Complete Reference Guide
- **44+ Example Notebooks** (comprehensive coverage)
- Tutorials and Workflows

### **API Reference**
- Auto-generated module documentation
- Function and class references
- Type annotations
- Usage examples

### **Development**
- Contributing guidelines
- Changelog
- License information

## 🎨 Customization Options

### **Theme Customization**
Add custom CSS/JS in `docs/_static/`:
```css
/* docs/_static/custom.css */
.wy-side-nav-search { background: #your-color; }
```

### **Logo and Branding**
Update `docs/conf.py`:
```python
html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"
```

### **Additional Pages**
Add new `.rst` or `.md` files in `docs/` and reference in `index.rst`:
```rst
.. toctree::
   :maxdepth: 2
   
   your_new_page
```

## 📊 Analytics and Monitoring

### **RTD Analytics**
- Page view statistics
- Search query analysis
- User engagement metrics
- Download statistics

### **Build Monitoring**
- Automatic build notifications
- Build status badges
- Error reporting and logs

## 🔄 Automated Updates

### **GitHub Integration**
- Documentation builds on every push
- Pull request previews
- Branch-specific documentation
- Release documentation

### **Webhook Configuration**
RTD automatically configures webhooks for:
- Push events
- Pull request events
- Release events
- Tag creation

## 🎯 Benefits for SciTeX Users

### **For Researchers**
- **Professional Documentation**: Publication-ready documentation
- **Example Gallery**: 44+ interactive notebook examples
- **Multiple Formats**: HTML, PDF, ePub for different use cases
- **Offline Access**: Download documentation for offline use

### **For Developers**
- **API Reference**: Complete function and class documentation
- **Integration Examples**: Real-world usage patterns
- **Development Guides**: Contributing and development workflows
- **Version History**: Documentation for all versions

### **For the Project**
- **Professional Presence**: Enhanced project credibility
- **Better Adoption**: Easier onboarding for new users
- **Community Building**: Central hub for documentation
- **SEO Benefits**: Better discoverability

## 🚦 Status and Next Steps

### ✅ **Completed**
- RTD configuration files created
- Sphinx configuration enhanced
- Example documentation structure
- Dependencies configured
- GitHub integration prepared

### 🔄 **Next Steps**
1. **Connect Repository** to Read the Docs
2. **Configure Project** settings on RTD
3. **Trigger First Build** and verify
4. **Custom Domain** (optional): `docs.scitex.io`
5. **Analytics Setup** for usage tracking

### 📈 **Future Enhancements**
- Interactive tutorials
- Video content integration
- Multi-language support
- Advanced search features
- API usage analytics

## 🔗 Useful Links

- [Read the Docs Documentation](https://docs.readthedocs.io/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [RTD Theme Documentation](https://sphinx-rtd-theme.readthedocs.io/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [nbsphinx](https://nbsphinx.readthedocs.io/)

---

**Result**: Professional, comprehensive documentation hosting with automated builds, multiple formats, and excellent user experience for the SciTeX project! 🎉