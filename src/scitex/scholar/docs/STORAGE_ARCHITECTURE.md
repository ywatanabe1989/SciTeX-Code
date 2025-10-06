# SciTeX Scholar Storage Architecture

## Summary: No More Manual pdfs Directory!

**Answer to your question**: Yes, you're correct! With the new unified CLI and MASTER storage architecture, **we don't need the manual `pdfs` directory anymore**.

## Old Structure (No Longer Needed)
```
neurovista/
├── pdfs/                     ❌ Manual PDF storage - NOT NEEDED
│   ├── 10.1093_brain_awx098.pdf
│   └── 10.1371_journal.pone.0081920.pdf
└── DOI_10.1038_xxx           ❌ DOI-based symlinks
```

## New Structure (Automatic & Organized)
```
library/
├── MASTER/
│   ├── AECB5227/             # Hash-based ID from DOI
│   │   ├── metadata.json     # Complete metadata
│   │   └── Cook-2013-LancetNeurology.pdf  # Properly named PDF
│   └── B4030896/
│       ├── metadata.json
│       └── Grigorovsky-2020-BrainCommunications.pdf
└── neurovista/
    ├── Cook-2013-LancetNeurology -> ../MASTER/AECB5227  ✅ Human-readable
    └── Grigorovsky-2020-BrainCommunications -> ../MASTER/B4030896

```

## Key Improvements

### 1. **Centralized MASTER Storage**
- All PDFs stored once in MASTER/{8-char-hash}/
- No duplicates across projects
- Consistent metadata.json tracking

### 2. **Human-Readable Symlinks**
- Format: `Author-Year-Journal` (e.g., `Cook-2013-LancetNeurology`)
- NOT: `DOI_10.1038_xxx` format
- Easy to browse and understand

### 3. **Automatic Management**
```bash
# Everything handled automatically:
python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download
```

## Migration from Old Structure

If you have existing PDFs in `project/pdfs/`:

```bash
# Dry run to see what will happen
python -m scitex.scholar.utils.migrate_pdfs_to_master --project neurovista --dry-run

# Actually migrate
python -m scitex.scholar.utils.migrate_pdfs_to_master --project neurovista

# After verifying, remove old pdfs directory
rm -rf ~/.scitex/scholar/library/neurovista/pdfs
```

## Benefits of New Architecture

1. **No Manual PDF Management** - CLI handles everything
2. **Deduplication** - Same paper across projects stored once
3. **Better Organization** - Human-readable names, not DOI strings
4. **Metadata Tracking** - Every PDF has metadata.json
5. **Scalability** - Hash-based IDs prevent conflicts
6. **Project Isolation** - Each project has its own symlink organization

## How It Works

When you download a paper:

1. **Generate unique ID**: `hashlib.md5(doi).hexdigest()[:8].upper()` → `AECB5227`
2. **Store in MASTER**: `MASTER/AECB5227/Cook-2013-LancetNeurology.pdf`
3. **Create metadata**: `MASTER/AECB5227/metadata.json`
4. **Link from project**: `neurovista/Cook-2013-LancetNeurology → ../MASTER/AECB5227`

## Commands That Handle Everything

```bash
# Create project
python -m scitex.scholar --project myresearch --create-project

# Enrich and download
python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich --download

# Download single paper
python -m scitex.scholar --doi "10.1038/nature12373" --project myresearch --download

# List papers
python -m scitex.scholar --project myresearch --list
```

## Technical Details

- **Storage Manager**: `LibraryManager` handles all storage operations
- **Scholar Interface**: `Scholar` class provides unified API
- **Separation of Concerns**:
  - Scholar = Interface/coordinator
  - LibraryManager = Storage operations
  - URLFinder = URL resolution
  - PDFDownloader = Download operations

## Conclusion

The manual `pdfs` directory is obsolete. The new system is:
- ✅ Fully automated
- ✅ Better organized
- ✅ Human-readable
- ✅ Deduplicated
- ✅ Metadata-rich

Simply use the unified CLI and let it handle everything!