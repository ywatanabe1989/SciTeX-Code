<!-- ---
!-- Timestamp: 2025-07-15 09:07:01
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/README.md
!-- --- -->

# SQLite3 with NumPy and Compression

SQLite database manager with automatic metadata handling, numpy array storage, and compression support.

## Quick Start

```python
import numpy as np
from scitex.db._sqlite3 import SQLite3

# Initialize
with SQLite3("data.db", compress_by_default=True) as db:
    # Create table
    db.create_table("data", {"id": "INTEGER PRIMARY KEY", "array": "BLOB"})
    
    # Save array
    data = np.random.random((1000, 100))
    db.save_array("data", data, additional_columns={"id": 1})
    
    # Load array
    loaded = db.load_array("data", "array", where="id = 1")
```

## Features

- Automatic compression (70-90% reduction)
- Thread-safe operations
- Metadata handling for BLOB columns
- Batch processing support
- Auto-creation of metadata columns

## Table Creation

BLOB columns automatically get metadata columns:

```python
db.create_table(
    "measurements",
    {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "data": "BLOB",  # Auto-creates: data_dtype, data_shape, data_compressed
        "timestamp": "REAL"
    }
)
```

## Array Storage

Save numpy arrays with automatic compression:

```python
data_array = np.random.random((1000, 100)).astype(np.float32)
db.save_array(
    table_name="measurements",
    data=data_array,
    column="data",
    additional_columns={"name": "experiment_1", "timestamp": 1234567890},
    compress=True,
    compress_level=6
)
```

## Array Loading

Load arrays with automatic decompression:

```python
loaded_array = db.load_array(
    table_name="measurements",
    column="data",
    where="name = 'experiment_1'"
)

# Batch loading
arrays_dict = db.get_array_dict(df, columns=["data"])
```

## Generic Object Storage

Save any Python object as compressed blob:

```python
db.save_blob(
    table_name="objects",
    data={"model_weights": data_array, "params": {"lr": 0.001}},
    key="model_v1",
    compress=True,
    metadata={"version": "1.0", "author": "researcher"}
)

loaded_obj = db.load_blob("objects", key="model_v1")
```

## Metadata Columns

For each BLOB column, these are automatically created:
- `{column}_dtype`: Data type information
- `{column}_shape`: Array shape information  
- `{column}_compressed`: Compression flag (0/1)

## Compression

- Typically reduces storage by 70-90%
- Configurable compression levels (1-9)
- Automatic for arrays > 1KB
- Per-operation override available
- Compression status tracked in metadata

## Context Manager

Always use context manager for proper resource cleanup:

```python
with SQLite3("data.db", compress_by_default=True) as db:
    # Database operations
    pass
```

<!-- EOF -->