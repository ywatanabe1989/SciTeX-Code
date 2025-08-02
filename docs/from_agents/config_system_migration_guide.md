# SciTeX Scholar Config System Migration Guide

## Overview

The new config system introduces directory tidiness constraints and organized path management to enhance maintainability and consistency. This guide outlines the migration from hardcoded paths to the new configuration-based system.

## What's Been Implemented

### 1. Enhanced PathManager (`src/scitex/scholar/config/_PathManager.py`)

**Features:**
- **Directory Tidiness Constraints**: Automatic file naming sanitization, size limits, retention policies
- **Organized Structure**: Hierarchical organization similar to Zotero
- **Automatic Maintenance**: Cleanup of old files, size enforcement, empty directory removal
- **Path Validation**: Sanitization of filenames and collection names
- **Storage Statistics**: Comprehensive reporting of directory usage

**Directory Structure:**
```
~/.scitex/scholar/
├── cache/ [Max: 1GB, 30d retention]
│   ├── chrome/
│   ├── auth/
│   │   └── <auth_type>/
│   └── <cache_type>/
│       └── <cache_name>.json
├── config/
│   └── <config_name>.yaml
├── library/
│   ├── indexes/
│   ├── <collection_name>/
│   │   └── <unique_id>/
│   └── <collection_name>-human-readable/
│       └── <Author>-<Year>-<Journal>/
├── log/
├── workspace/ [Max: 2GB, 7d retention]
│   ├── downloads/ [Max: 1GB, 3d retention]
│   ├── logs/
│   └── screenshots/ [Max: 500MB, 14d retention]
│       └── <screenshot_type>/
└── backup/
```

### 2. ScholarConfig (`src/scitex/scholar/config/_ScholarConfig.py`)

**Features:**
- Configuration cascade (direct → config → env → default)
- YAML config with environment variable substitution
- Integrated PathManager access via `config.paths`
- Resolution logging and debugging

### 3. Tidiness Constraints (`TidinessConstraints` class)

**Default Constraints:**
- Max filename length: 100 characters
- Cache retention: 30 days
- Workspace retention: 7 days
- Screenshots retention: 14 days
- Downloads retention: 3 days
- Max cache size: 1GB
- Max workspace size: 2GB

## Migration Status

### ✅ Completed
- [x] Enhanced PathManager with tidiness constraints
- [x] ScholarConfig with cascade resolution
- [x] Directory structure validation and creation
- [x] Automatic maintenance and cleanup
- [x] File naming sanitization
- [x] Storage statistics and monitoring
- [x] Audit tool for existing installations
- [x] Test suite for config system verification

### ✅ Fixed Components
- [x] DOIResolver: Updated to use `config.resolve()` instead of `config.auth.get()`
- [x] OpenAthensAuthenticator: Fixed path concatenation issues
- [x] Test pipeline: Updated to use new config system

### 🔄 Migration Needed

The following components need to be updated to use the new config system:

1. **Import Updates Required:**
   ```python
   # Old
   from scitex.scholar.utils._scholar_paths import scholar_paths
   
   # New
   from scitex.scholar.config._ScholarConfig import ScholarConfig
   config = ScholarConfig()
   ```

2. **Path Access Updates:**
   ```python
   # Old
   pdf_dir = scholar_paths.get_pdfs_dir()
   
   # New
   pdf_dir = config.paths.get_downloads_dir()  # or appropriate method
   ```

3. **Components with Known Issues:**
   - `src/scitex/scholar/utils/_scholar_paths.py` (legacy, needs migration)
   - Any components using hardcoded paths
   - Components accessing `config.auth.get()` pattern

## Audit Results

Recent audit found:
- **Total Files**: 10,099 files (1,049.6 MB)
- **Obsolete Files**: 1,386 files
- **Old Backups**: Files cleaned during maintenance
- **Duplicate Files**: 3,646 potential duplicates
- **Versioned Source**: 47 versioned source files
- **Maintenance Impact**: 464 cache files cleaned, 4 size violations fixed

## How to Use the New System

### Basic Usage

```python
from scitex.scholar.config._ScholarConfig import ScholarConfig

# Create config instance
config = ScholarConfig()

# Access paths
downloads_dir = config.paths.get_downloads_dir()
cache_dir = config.paths.get_cache_dir("doi_cache")
screenshots_dir = config.paths.get_screenshots_dir("openurl")

# Resolve configuration values
email = config.resolve("crossref_email", default="research@example.com")

# Get paper storage paths
paper_info = {
    "title": "Paper Title",
    "url": "https://example.com",
    "authors": ["Author, First"],
    "year": "2024",
    "journal": "Nature"
}
paths = config.paths.get_paper_storage_paths(paper_info, "my_collection")
```

### Maintenance

```python
# Run maintenance
results = config.paths.perform_maintenance()
print(f"Cleaned {results['cache_cleaned']} cache files")

# Get storage statistics
stats = config.paths.get_storage_stats()
for name, info in stats.items():
    print(f"{name}: {info['size_mb']:.1f}MB")
```

### Custom Constraints

```python
from scitex.scholar.config._PathManager import PathManager, TidinessConstraints

constraints = TidinessConstraints(
    max_cache_size_mb=500,    # 500MB cache limit
    cache_retention_days=14,   # 14 day retention
    max_filename_length=80     # 80 char filenames
)

path_manager = PathManager(constraints=constraints)
```

## Testing

Run the config system tests:
```bash
python .dev/test_config_system.py
```

Run the audit tool:
```bash
python .dev/audit_and_cleanup_scholar.py
```

## Migration Checklist

For each component that needs updating:

1. [ ] Update imports to use `ScholarConfig`
2. [ ] Replace hardcoded paths with `config.paths.get_*()` methods
3. [ ] Update configuration access to use `config.resolve()`
4. [ ] Test functionality with new config system
5. [ ] Verify paths are created correctly
6. [ ] Check that tidiness constraints are applied

## Benefits

### For Developers
- **Consistent Paths**: All path management centralized
- **Easy Configuration**: Environment variable support
- **Debugging**: Configuration resolution logging
- **Maintainable**: Clear separation of concerns

### For Users
- **Automatic Cleanup**: Old files removed automatically
- **Size Management**: Directories stay within reasonable limits
- **Organized Structure**: Easy to find files
- **Safe Operations**: File naming validation prevents issues

### For System
- **Storage Efficiency**: Automatic maintenance prevents bloat
- **Performance**: Organized structure improves access times
- **Reliability**: Validated paths prevent errors
- **Monitoring**: Built-in statistics and reporting

## Next Steps

1. **Continue Migration**: Update remaining components as needed
2. **Monitor Usage**: Use audit tool to track improvements
3. **Customize Constraints**: Adjust limits based on usage patterns
4. **Documentation**: Update user documentation with new paths
5. **Training**: Familiarize team with new config patterns

## Support

For any issues during migration:
1. Check the test suite for examples
2. Review audit report for specific problems
3. Use config resolution logging for debugging
4. Consult this guide for migration patterns

The new config system enhances the codebase to be more consistent and maintainable while providing powerful directory management features.