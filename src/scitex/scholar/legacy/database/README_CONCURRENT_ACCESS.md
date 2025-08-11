# Concurrent Access in SciTeX Scholar

## Directory-Based Architecture Benefits

Yes, exactly! The directory-based approach (inspired by Zotero) enables excellent concurrent handling:

### Structure
```
storage/
├── by_key/
│   ├── ABCD1234/        # Paper 1 - Worker A can process
│   │   ├── paper.pdf
│   │   ├── metadata.json
│   │   └── annotations.json
│   ├── EFGH5678/        # Paper 2 - Worker B can process  
│   │   ├── paper.pdf
│   │   ├── metadata.json
│   │   └── annotations.json
│   └── IJKL9012/        # Paper 3 - Worker C can process
│       └── ...
```

### Concurrent Worker Benefits

1. **No Lock Contention**
   - Each paper has its own directory
   - Workers never compete for the same files
   - Natural work distribution

2. **Atomic Operations**
   ```python
   # Safe concurrent write pattern
   temp_file = f"{file_path}.tmp.{worker_async_id}"
   write_to(temp_file)
   os.rename(temp_file, file_path)  # Atomic on most filesystems
   ```

3. **Easy Parallelization**
   ```python
   # Example: Process papers in parallel
   from concurrent.futures import ProcessPoolExecutor
   
   def process_paper(storage_key):
       paper_dir = storage_dir / "by_key" / storage_key
       # Each worker_async operates independently
       
   with ProcessPoolExecutor(max_worker=8) as executor:
       executor.map(process_paper, all_storage_keys)
   ```

4. **Natural Sharding**
   - Worker 1: Keys starting with A-F
   - Worker 2: Keys starting with G-M
   - Worker 3: Keys starting with N-S
   - Worker 4: Keys starting with T-Z

5. **Crash Recovery**
   - If a worker_async crashes, only one paper affected
   - Easy to identify incomplete operations (temp files)
   - Simple cleanup and restart

### HPC/Cluster Benefits

- **Network Filesystem Friendly**: Works well with NFS, Lustre, etc.
- **No Database Server**: No single point of failure
- **Bandwidth Efficient**: Workers only access their assigned papers
- **Cache Friendly**: Each worker_async's files stay in local cache

### Database Role

The SQLite database is used for:
- Fast searching across all papers
- Maintaining relationships (collections, tags)
- Generating statistics
- But NOT required for basic operations

This means:
- Workers can operate even if database is locked
- Database can be rebuilt from directory contents
- Search index can be updated asynchronously

### Example Concurrent Workflow

```python
# DOI Resolution (Step 4)
Worker 1: Resolving DOIs for papers without DOI
Worker 2: Resolving DOIs for papers without DOI  
Worker 3: Resolving DOIs for papers without DOI
# Each writes to their assigned paper directories

# PDF Download (Step 7)
Worker 1: Downloading PDFs for papers A-H
Worker 2: Downloading PDFs for papers I-P
Worker 3: Downloading PDFs for papers Q-Z
# No conflicts, natural parallelization

# Enrichment (Step 6)
Worker 1: Enriching metadata for batch 1
Worker 2: Enriching metadata for batch 2
# Each updates their own directories
```

This architecture scales linearly with the number of worker_asyncs!