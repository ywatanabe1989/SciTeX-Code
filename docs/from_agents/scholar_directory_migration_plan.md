# SciTeX Scholar Directory Migration Plan

## IMPORTANT: No-Regression Migration Strategy

This document outlines a **SAFE** migration plan for organizing `~/.scitex/scholar/` directory structure inspired by Zotero's organization. **All existing functionality must continue to work during and after migration.**

## Current Directory Structure (PRESERVED)
```
/home/ywatanabe/.scitex/scholar/
├── chrome_profile/              # Browser profile (KEEP)
├── chrome_profiles/             # Browser profiles (KEEP) 
├── chrome_profile_v2/           # Browser profile v2 (KEEP)
├── database/                    # Existing database (KEEP)
├── default_config.yaml          # Config file (KEEP)
├── doi_cache/                   # DOI cache (KEEP)
├── install_chrome_extensions.py # Script (KEEP)
├── local_index.json            # Index file (KEEP)
├── openathens_session.json     # Auth session (KEEP)
├── openathens_sessions/        # Auth sessions (KEEP)
├── pdf_index.json              # PDF index (KEEP)
├── pdfs/                       # PDF files (KEEP)
├── .scitex_salt                # Salt file (KEEP)
├── screenshots/                # Screenshots (KEEP)
├── semantic_index_test/        # Semantic index (KEEP)
├── sso_sessions/               # SSO sessions (KEEP)
├── user_*/                     # User sessions (KEEP)
└── zotero_translators/         # Translators (KEEP)
```

## New Directory Structure (ADDED)
```
/home/ywatanabe/.scitex/scholar/
├── library/                    # NEW: Zotero-style library
│   ├── storage/               # Individual paper folders (8-char IDs)
│   ├── collections/           # Paper collections/groups
│   ├── backups/              # Database backups
│   ├── indexes/              # Search indexes
│   └── scitex_scholar.sqlite # Main library database
├── cache/                     # NEW: Organized cache
│   ├── doi_cache/            # (future: symlink to existing)
│   ├── semantic_index/       # (future: migrate semantic_index_test)
│   └── sessions/             # (future: consolidate user_* dirs)
├── profiles/                  # NEW: Browser organization
│   ├── chrome/               # (future: consolidate chrome_profile*)
│   └── extensions/           # Extension management
├── workspace/                 # NEW: Active work
│   ├── screenshots/          # (future: symlink to existing)
│   ├── downloads/            # Temporary downloads
│   └── logs/                 # Operation logs
└── config/                    # NEW: Configuration
    ├── translators/          # (future: symlink to zotero_translators)
    ├── styles/               # Citation styles
    └── settings/             # User preferences
```

## Migration Strategy: Phase-by-Phase

### Phase 1: Create New Structure (COMPLETED ✅)
- ✅ Created new directories: `library/`, `cache/`, `profiles/`, `workspace/`, `config/`
- ✅ All existing files remain untouched
- ✅ No regression risk

### Phase 2: Create Symlinks (SAFE)
Create symbolic links from new structure to existing data:

```bash
# DOI cache
ln -s ../../doi_cache ~/.scitex/scholar/cache/doi_cache_link

# Screenshots  
ln -s ../../screenshots ~/.scitex/scholar/workspace/screenshots_link

# Translators
ln -s ../../zotero_translators ~/.scitex/scholar/config/translators_link

# Database
ln -s ../../database ~/.scitex/scholar/library/database_link
```

**Risk**: None - symlinks don't affect existing functionality

### Phase 3: Update Code to Support Both Structures (BACKWARD COMPATIBLE)
Modify SciTeX Scholar code to:
1. Check new locations first
2. Fall back to old locations if not found
3. Maintain full backward compatibility

Example:
```python
def get_doi_cache_dir():
    # Try new location first
    new_path = Path.home() / ".scitex" / "scholar" / "cache" / "doi_cache"
    if new_path.exists():
        return new_path
    
    # Fall back to old location
    old_path = Path.home() / ".scitex" / "scholar" / "doi_cache"
    return old_path
```

**Risk**: None - code works with both old and new structures

### Phase 4: Test New Structure (VALIDATION)
1. Run comprehensive tests with new structure
2. Verify all existing functionality works
3. Test both old and new path resolution
4. Validate no data loss

**Risk**: None - testing doesn't modify data

### Phase 5: Gradual Migration (OPTIONAL, WHEN READY)
Only after thorough testing and user approval:
1. Copy (not move) data to new locations
2. Update configuration to prefer new locations
3. Keep old locations as backup

**Risk**: Minimal - old data preserved as backup

## Code Changes Required

### 1. Path Resolution Functions
```python
class ScholarPaths:
    """Provides backward-compatible path resolution."""
    
    @staticmethod
    def get_pdfs_dir():
        # New structure
        new_path = Path.home() / ".scitex" / "scholar" / "library" / "storage"
        if new_path.exists() and list(new_path.iterdir()):
            return new_path
            
        # Fallback to existing
        return Path.home() / ".scitex" / "scholar" / "pdfs"
    
    @staticmethod  
    def get_screenshots_dir():
        # New structure
        new_path = Path.home() / ".scitex" / "scholar" / "workspace" / "screenshots"
        if new_path.exists():
            return new_path
            
        # Fallback to existing
        return Path.home() / ".scitex" / "scholar" / "screenshots"
```

### 2. Configuration Updates
Update existing configuration to support both paths without breaking changes.

### 3. Database Integration
Create new library database alongside existing database, not replacing it.

## Benefits of This Approach

1. **Zero Regression Risk**: Existing functionality preserved
2. **Gradual Migration**: Can be done incrementally
3. **Rollback Capability**: Can revert at any time
4. **Testing Phase**: Thorough validation before changes
5. **User Control**: Migration only when user is ready

## Files That Must Never Be Modified

- `openathens_session.json` - Critical for authentication
- `user_*` directories - User session data
- `pdfs/` directory - Existing PDF files
- `database/` directory - Existing database files
- `chrome_profiles/` - Browser profile data

## Implementation Status

- ✅ Phase 1: New directory structure created
- ⏳ Phase 2: Create symlinks (pending)
- ⏳ Phase 3: Update code for backward compatibility (pending)
- ⏳ Phase 4: Testing and validation (pending)
- ⏳ Phase 5: Optional migration (user decision)

## Conclusion

This migration plan ensures **zero regression** while providing a path toward better organization. The new structure can coexist with the existing structure, and migration can be done gradually and safely when ready.