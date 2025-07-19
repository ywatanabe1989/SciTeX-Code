# HDF5 to Zarr Migration Guide

## Overview

SciTeX provides powerful tools for migrating HDF5 files to the Zarr format. This migration can offer several benefits:

- **Better compression**: Multiple modern compression algorithms
- **Cloud-friendly**: Designed for distributed storage systems
- **Concurrent access**: Lock-free reading for parallel workflows
- **Flexible chunking**: Optimize for your access patterns
- **Python-native**: No need for complex HDF5 library dependencies

## Why Migrate from HDF5 to Zarr?

### Advantages of Zarr

1. **No file locking**: Multiple processes can read simultaneously
2. **Cloud storage**: Works efficiently with object stores (S3, GCS, Azure)
3. **Modern compression**: Supports Blosc, Zstandard, LZ4, and more
4. **Simpler format**: Directory-based structure is easier to understand
5. **Incremental updates**: Modify chunks without rewriting entire datasets

### When to Keep HDF5

- Complex features like dimension scales or soft links
- Existing workflows deeply integrated with HDF5
- Need for specific HDF5 features not available in Zarr

## Basic Usage

### Single File Migration

```python
from scitex.io.utils import migrate_h5_to_zarr

# Basic migration
zarr_path = migrate_h5_to_zarr("data.h5")

# Custom output path
zarr_path = migrate_h5_to_zarr("data.h5", "output.zarr")

# With compression
zarr_path = migrate_h5_to_zarr(
    "data.h5",
    compressor="zstd",  # or 'lz4', 'gzip', 'blosc', None
    chunks=True  # Auto-determine chunks
)
```

### Batch Migration

```python
from scitex.io.utils import migrate_h5_to_zarr_batch
import glob

# Find all HDF5 files
h5_files = glob.glob("data/*.h5")

# Sequential migration
zarr_paths = migrate_h5_to_zarr_batch(h5_files)

# Parallel migration
zarr_paths = migrate_h5_to_zarr_batch(
    h5_files,
    parallel=True,
    n_workers=4
)

# Migrate to specific directory
zarr_paths = migrate_h5_to_zarr_batch(
    h5_files,
    output_dir="zarr_data/"
)
```

## Advanced Features

### Compression Options

```python
# Available compressors
compressors = {
    'zstd': 'Best balance of speed and compression',
    'lz4': 'Fastest compression/decompression',
    'gzip': 'Maximum compatibility',
    'blosc': 'Multi-threaded compression',
    None: 'No compression (fastest I/O)'
}

# Custom compression level
from numcodecs import Zstd
migrate_h5_to_zarr(
    "data.h5",
    compressor=Zstd(level=9)  # Higher compression
)
```

### Chunking Strategies

```python
# Auto chunking (recommended)
migrate_h5_to_zarr("data.h5", chunks=True)

# No chunking (small arrays)
migrate_h5_to_zarr("data.h5", chunks=False)

# Custom chunks for specific access patterns
# For 3D array (time, height, width)
migrate_h5_to_zarr(
    "video.h5",
    chunks=(1, 720, 1280)  # One frame per chunk
)

# For large matrix computations
migrate_h5_to_zarr(
    "matrix.h5", 
    chunks=(1000, 1000)  # Square chunks
)
```

### Progress and Validation

```python
# Show progress during migration
migrate_h5_to_zarr(
    "large_file.h5",
    show_progress=True
)

# Validate migration integrity
migrate_h5_to_zarr(
    "important_data.h5",
    validate=True  # Checks shapes and keys
)

# Overwrite existing Zarr stores
migrate_h5_to_zarr(
    "data.h5",
    "existing.zarr",
    overwrite=True
)
```

## Handling Special Cases

### Variable-Length Strings

HDF5 variable-length strings are automatically converted:

```python
# HDF5 with vlen strings
with h5py.File("strings.h5", "w") as f:
    dt = h5py.special_dtype(vlen=str)
    f.create_dataset("text", data=["short", "longer string"], dtype=dt)

# Migrates automatically
migrate_h5_to_zarr("strings.h5")
```

### Object Arrays

Complex objects are pickled during migration:

```python
# Warning issued for object arrays
# Objects are automatically pickled
migrate_h5_to_zarr("objects.h5")
```

### Large Datasets

For very large datasets, chunking is crucial:

```python
# Infers optimal chunks (~10MB per chunk)
migrate_h5_to_zarr(
    "huge_dataset.h5",
    chunks=True,
    compressor="blosc"  # Fast parallel compression
)
```

## Performance Optimization

### Parallel Batch Processing

```python
# Process multiple files concurrently
import os

migrate_h5_to_zarr_batch(
    h5_files,
    parallel=True,
    n_workers=os.cpu_count()
)
```

### Access Pattern Optimization

Choose chunks based on how you'll access the data:

```python
# Time series: chunk along time dimension
# Shape: (time=100000, channels=64)
chunks = (10000, 64)  # Read 10k time points at once

# Images: chunk by complete images
# Shape: (num_images=1000, height=512, width=512, channels=3)
chunks = (1, 512, 512, 3)  # One image per chunk

# Matrix operations: square chunks
# Shape: (10000, 10000)
chunks = (500, 500)  # Balanced for row/column access
```

## Verification and Exploration

### Compare Before and After

```python
from scitex.io._load_modules._H5Explorer import explore_h5
from scitex.io._load_modules._ZarrExplorer import explore_zarr

# Original structure
explore_h5("original.h5")

# Migrated structure
zarr_path = migrate_h5_to_zarr("original.h5")
explore_zarr(zarr_path)
```

### Verify Data Integrity

```python
import h5py
import zarr
import numpy as np

# Load and compare
with h5py.File("data.h5", "r") as h5f:
    h5_data = h5f["dataset"][:]

z = zarr.open("data.zarr", "r")
zarr_data = z["dataset"][:]

# Should be True
assert np.array_equal(h5_data, zarr_data)
```

## Common Issues and Solutions

### Issue: Memory Error with Large Arrays

**Solution**: Ensure chunking is enabled
```python
migrate_h5_to_zarr("large.h5", chunks=True)
```

### Issue: Slow Migration

**Solution**: Use faster compression
```python
migrate_h5_to_zarr("data.h5", compressor="lz4")
```

### Issue: Object Arrays Not Supported

**Solution**: Objects are automatically pickled, but consider converting to standard types before migration for better compatibility

### Issue: HDF5-Specific Features Lost

**Solution**: Features like dimension scales, soft links, and external links require manual handling:
```python
# Save dimension scale information separately
with h5py.File("data.h5", "r") as h5f:
    scales = {}
    if h5f["data"].dims[0].items():
        scales["dim0"] = h5f["data"].dims[0][0][:]
    
# Add to Zarr as separate arrays or attributes
```

## Complete Example

```python
import numpy as np
import scitex as stx
from scitex.io.utils import migrate_h5_to_zarr
from scitex.io._load_modules._ZarrExplorer import ZarrExplorer

# Create example HDF5
stx.io.save({
    "raw_data": {
        "measurements": np.random.randn(10000, 100),
        "timestamps": np.arange(10000)
    },
    "metadata": {
        "experiment": "Test",
        "date": "2025-07-12"
    }
}, "experiment.h5")

# Migrate with optimal settings
print("Migrating HDF5 to Zarr...")
zarr_path = migrate_h5_to_zarr(
    "experiment.h5",
    "experiment.zarr",
    compressor="zstd",
    chunks=True,
    show_progress=True,
    validate=True
)

# Explore the result
print("\nExploring Zarr structure:")
with ZarrExplorer(zarr_path) as explorer:
    explorer.show()
    
    # Load specific data efficiently
    measurements = explorer.load("raw_data/measurements")
    print(f"\nMeasurements shape: {measurements.shape}")

# Access data using SciTeX
data = stx.io.load(zarr_path)
print(f"\nLoaded data keys: {list(data.keys())}")
```

## Best Practices

1. **Always use chunking** for arrays larger than 100MB
2. **Choose compressor** based on data type:
   - Float data: `zstd` or `blosc`
   - Integer data: `zstd` 
   - Already compressed: `None`
3. **Validate important migrations** with `validate=True`
4. **Batch process** multiple files in parallel when possible
5. **Test access patterns** after migration to ensure performance
6. **Document any HDF5-specific features** that require manual handling

## Summary

The HDF5 to Zarr migrator in SciTeX provides:
- **Simple API** for single and batch migrations
- **Automatic handling** of data types and structures
- **Flexible compression** and chunking options
- **Parallel processing** for multiple files
- **Validation** to ensure data integrity
- **Progress tracking** for large migrations

Use this tool when modernizing your data storage infrastructure or preparing datasets for cloud deployment.