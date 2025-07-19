# SciTeX Zarr Module Usage Guide

## Overview

The SciTeX Zarr module provides efficient storage and retrieval of hierarchical array data using the Zarr format. Zarr is particularly well-suited for large scientific datasets, offering chunking, compression, and concurrent read access.

## Key Features

- **Hierarchical Storage**: Organize data in groups and datasets
- **Compression**: Multiple algorithms (zstd, lz4, gzip) for space efficiency
- **Chunking**: Handle large arrays without loading entire datasets into memory
- **Type Preservation**: Maintains Python/NumPy data types across save/load cycles
- **Interactive Exploration**: Browse and inspect Zarr stores without loading data
- **Seamless Integration**: Works with SciTeX's unified I/O interface

## Basic Usage

### Saving Data

```python
import scitex as stx
import numpy as np

# Simple save
data = {
    "array": np.random.randn(1000, 1000),
    "metadata": {
        "experiment": "test",
        "version": 1.0
    }
}
stx.io.save(data, "./output.zarr")

# With compression options
stx.io.save(data, "./compressed.zarr", compressor="zstd", chunks=(100, 100))
```

### Loading Data

```python
# Load entire store
loaded = stx.io.load("./output.zarr")

# Load specific subset
metadata = stx.io.load("./output.zarr", key="metadata")
array_data = stx.io.load("./output.zarr", key="array")
```

### Exploring Zarr Stores

```python
from scitex.io._load_modules._ZarrExplorer import explore_zarr, ZarrExplorer

# Quick exploration
explore_zarr("./output.zarr")

# Detailed exploration
with ZarrExplorer("./output.zarr") as explorer:
    # List keys
    keys = explorer.keys("/")
    
    # Check key existence
    if explorer.has_key("array"):
        # Load specific data
        array = explorer.load("array")
    
    # Show structure
    explorer.show()
```

## Data Types Support

### Basic Types
- **Scalars**: int, float, bool, string, None
- **Collections**: lists, dicts (automatically pickled)
- **NumPy Arrays**: All dtypes including complex numbers
- **Custom Objects**: Pickled for complex types

### Example: Mixed Data Types

```python
data = {
    # Scalars
    "count": 42,
    "ratio": 3.14159,
    "active": True,
    "name": "Experiment A",
    
    # Arrays
    "measurements": np.random.randn(1000),
    "image": np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8),
    "complex_data": np.array([1+2j, 3+4j]),
    
    # Nested structures
    "results": {
        "accuracy": 0.95,
        "predictions": np.random.randn(100, 10),
        "labels": ["cat", "dog", "bird"]
    }
}

stx.io.save(data, "./mixed_types.zarr")
```

## Hierarchical Organization

Zarr supports hierarchical data organization similar to HDF5:

```python
# Save with hierarchical keys
stx.io.save({"temperature": temps}, "./data.zarr", key="sensors/environmental")
stx.io.save({"pressure": pressure}, "./data.zarr", key="sensors/environmental")
stx.io.save({"video": frames}, "./data.zarr", key="sensors/camera")

# Load specific groups
env_data = stx.io.load("./data.zarr", key="sensors/environmental")
```

## Compression Strategies

### Available Compressors

1. **zstd** (default): Best balance of speed and compression
2. **lz4**: Fastest compression/decompression
3. **gzip**: Maximum compatibility
4. **None**: No compression (fastest I/O)

### Compression Comparison

```python
# Test different compressors
compressors = ["zstd", "lz4", "gzip", None]
for comp in compressors:
    stx.io.save(large_array, f"./test_{comp}.zarr", compressor=comp)
```

## Chunking for Large Arrays

Chunking enables efficient partial loading of large arrays:

```python
# Large 3D array
shape = (1000, 2000, 3000)
large_data = np.random.randn(*shape)

# Save with chunks
stx.io.save(
    {"data": large_data},
    "./chunked.zarr",
    chunks=(100, 200, 300)  # Chunk shape
)

# Load only a slice (memory efficient)
import zarr
store = zarr.open("./chunked.zarr", mode='r')
slice_data = store['data'][0:10, 500:600, 1000:1100]
```

## Advanced Features

### Custom Compression Levels

```python
from numcodecs import Zstd, LZ4, GZip

# High compression
stx.io.save(data, "./high_comp.zarr", compressor=Zstd(level=9))

# Fast compression
stx.io.save(data, "./fast_comp.zarr", compressor=LZ4(acceleration=10))
```

### Concurrent Access

Zarr supports multiple readers without file locking:

```python
# Multiple processes can read simultaneously
# Process 1
data1 = stx.io.load("./shared.zarr", key="dataset1")

# Process 2 (different process)
data2 = stx.io.load("./shared.zarr", key="dataset2")
```

### Working with Attributes

```python
import zarr

# Add metadata to existing store
store = zarr.open("./data.zarr", mode='a')
store.attrs['created_date'] = '2025-07-12'
store.attrs['author'] = 'SciTeX User'
store['array'].attrs['units'] = 'meters'
```

## Best Practices

### 1. Choose Appropriate Chunk Sizes

```python
# For 2D arrays: chunks roughly 1-10 MB
# Example: float64 array (8 bytes per element)
# 1MB chunk ≈ sqrt(1024*1024/8) ≈ 360x360
chunks = (512, 512)  # Good for most 2D arrays

# For 3D arrays: consider access patterns
# Time series: (1, height, width) for time-slice access
# Spatial: (depth, 64, 64) for spatial region access
```

### 2. Compression Selection

- **Scientific data (floats)**: Use zstd or lz4
- **Integer data**: zstd provides good compression
- **Already compressed (images)**: Use None
- **Text/categorical**: gzip works well

### 3. Hierarchical Organization

```python
# Organize by experiment structure
data_structure = {
    "raw_data": {
        "subject_001": {"eeg": ..., "behavior": ...},
        "subject_002": {"eeg": ..., "behavior": ...}
    },
    "processed": {
        "features": ...,
        "statistics": ...
    },
    "metadata": {
        "parameters": ...,
        "timestamps": ...
    }
}
```

### 4. Memory Efficiency

```python
# Don't load entire large arrays
# Bad
all_data = stx.io.load("./huge.zarr")["massive_array"]

# Good - load only what you need
store = zarr.open("./huge.zarr", mode='r')
subset = store['massive_array'][1000:2000, :100]
```

## Performance Tips

### 1. Batch Operations

```python
# Save multiple arrays efficiently
with zarr.open("./output.zarr", mode='w') as store:
    for i, array in enumerate(arrays):
        store[f'array_{i}'] = array
```

### 2. Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor

def process_chunk(args):
    store_path, key, slice_idx = args
    store = zarr.open(store_path, mode='r')
    data = store[key][slice_idx]
    return data.mean()

# Process chunks in parallel
with ProcessPoolExecutor() as executor:
    slices = [(path, 'data', slice(i*100, (i+1)*100)) 
              for i in range(10)]
    results = executor.map(process_chunk, slices)
```

## Troubleshooting

### Common Issues

1. **Unicode Errors**: Zarr handles Unicode correctly by default
2. **Memory Issues**: Use chunking for large arrays
3. **Compression Errors**: Ensure compressor is installed (`pip install numcodecs`)
4. **Path Issues**: Use forward slashes even on Windows

### Debugging

```python
# Check store structure
with ZarrExplorer("./problem.zarr") as explorer:
    explorer.show()  # Visualize structure
    print(explorer.keys("/"))  # List all keys
```

## Migration from Other Formats

### From HDF5

```python
# Similar hierarchical structure
# HDF5
h5_data = stx.io.load("./data.h5")
stx.io.save(h5_data, "./data.zarr")

# Both support groups and datasets
# Both support compression and chunking
```

### From NumPy

```python
# Simple conversion
np_arrays = [np.load(f"array_{i}.npy") for i in range(10)]
zarr_data = {f"array_{i}": arr for i, arr in enumerate(np_arrays)}
stx.io.save(zarr_data, "./arrays.zarr")
```

## Example: Complete Scientific Workflow

```python
import scitex as stx
import numpy as np
from scitex.io._load_modules._ZarrExplorer import ZarrExplorer

# 1. Generate experimental data
experiment = {
    "config": {
        "name": "Neural Recording Analysis",
        "date": "2025-07-12",
        "sampling_rate": 30000,
        "channels": 64
    },
    "raw_signals": np.random.randn(64, 300000),  # 64 channels, 10 seconds
    "events": {
        "timestamps": np.sort(np.random.uniform(0, 10, 1000)),
        "labels": np.random.choice(["spike", "burst", "noise"], 1000)
    }
}

# 2. Save with appropriate chunking and compression
output_path = "./neural_experiment.zarr"
stx.io.save(
    experiment,
    output_path,
    chunks={"raw_signals": (64, 30000)},  # 1-second chunks
    compressor="zstd"
)

# 3. Process data efficiently
store = zarr.open(output_path, mode='r+')

# Process in chunks
for i in range(10):  # Process each second
    chunk = store['raw_signals'][:, i*30000:(i+1)*30000]
    filtered = np.abs(chunk)  # Simple processing
    store[f'processed/filtered_sec_{i}'] = filtered

# 4. Add analysis results
store['analysis/spike_rate'] = len(store['events/timestamps']) / 10
store.attrs['processed'] = True

# 5. Explore final structure
print("\nFinal data structure:")
explore_zarr(output_path)

# 6. Load specific results
with ZarrExplorer(output_path) as explorer:
    if explorer.has_key("analysis/spike_rate"):
        rate = explorer.load("analysis/spike_rate")
        print(f"\nSpike rate: {rate:.2f} Hz")
```

## Summary

The SciTeX Zarr module provides:
- **Efficient storage** for large scientific datasets
- **Flexible organization** with hierarchical groups
- **Memory-efficient access** through chunking
- **Space savings** through compression
- **Easy exploration** without loading data
- **Seamless integration** with SciTeX I/O

Use Zarr when you need:
- Large array storage
- Partial data access
- Concurrent reads
- Hierarchical organization
- Long-term data archival