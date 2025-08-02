# Why Zotero Uses SQLite

## Zotero's Use Case is Different

### 1. **User Interface Requirements**
- Zotero is primarily a GUI application
- Needs instant search, sorting, and filtering
- Complex queries across metadata fields
- Tag hierarchies and collections
- Related items and citations

### 2. **Single User, Local Access**
- Designed for single-user desktop use
- No concurrent multi-user access needed
- All operations happen on local machine
- Sync is handled separately via Zotero servers

### 3. **Complex Relationships**
- Items have parent-child relationships
- Collections and subcollections
- Tags, notes, and attachments
- Citation networks

### 4. **SQLite Benefits for Zotero**
- Zero configuration database
- Single file storage (zotero.sqlite)
- Full SQL query capabilities
- Embedded - no server needed
- Fast for single-user access
- ACID compliance for data integrity

## Why Directory-Based Works Better for SciTeX Scholar

### 1. **HPC/Distributed Environment**
- Multiple workers accessing files concurrently
- No centralized database server
- File locking is problematic in HPC

### 2. **Simple Data Model**
- Papers are independent entities
- No complex relationships needed
- Metadata is relatively flat

### 3. **Direct File Access**
- PDFs need to be accessible to external tools
- Each paper is self-contained
- Easy to move/backup individual papers

### 4. **Your Specific Infrastructure**
- 10TB SSD NAS optimized for file access
- File system handles concurrent access
- No database administration overhead

## The Key Difference

**Zotero** needs:
- Complex queries ("show all papers by author X with tag Y from year Z")
- Instant UI updates
- Collection management
- Citation tracking

**SciTeX Scholar** needs:
- Concurrent access by multiple workers
- Direct PDF file access
- Simple lookups (DOI → file location)
- HPC compatibility

## Hybrid Approach Makes Sense

You could add a SQLite index later for:
- Fast DOI lookups
- Progress tracking
- Search capabilities

But keep files in directories for:
- Concurrent access
- Direct PDF editing
- HPC compatibility
- Backup simplicity