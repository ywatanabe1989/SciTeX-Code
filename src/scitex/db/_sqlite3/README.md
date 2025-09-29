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

## Column Operations

Modern column management with automatic version detection:

### Drop Columns

```python
with SQLite3("data.db") as db:
    # Drop single column (uses native DROP COLUMN if SQLite >= 3.35.0)
    db.drop_column("table_name", "old_column")
    
    # Drop multiple columns efficiently
    db.drop_columns("table_name", ["col1", "col2", "col3"])
```

### Rename Columns

```python
# Rename column (uses native RENAME COLUMN if SQLite >= 3.25.0)
db.rename_column("table_name", "old_name", "new_name")
```

### Add Columns

```python
# Add new column with default value
db.add_column("table_name", "new_column", "TEXT", default="N/A")

# Add column with NOT NULL constraint
db.add_column("table_name", "required_field", "INTEGER NOT NULL", default=0)
```

### Reorder and Sort Columns

```python
# Explicit column ordering
db.reorder_columns("table_name", ["id", "name", "email", "created_at"])

# Sort alphabetically with key columns first
db.sort_columns("table_name", alphabetical=True, key_columns_first=["id", "created_at"])

# Custom sort with callable
db.sort_columns("table_name", key=lambda col: (col != "id", col.lower()))
```

### Column Information

```python
# Check if column exists
if db.column_exists("table_name", "column_name"):
    print("Column exists")

# Get column information
columns = db.get_column_info("table_name")
for col in columns:
    print(f"{col['name']}: {col['type']} {'PK' if col['pk'] else ''}")
```

### Version Detection

The module automatically detects SQLite version and uses native operations when available:
- DROP COLUMN: SQLite 3.35.0+ (native) or table recreation
- RENAME COLUMN: SQLite 3.25.0+ (native) or table recreation
- All operations preserve data, constraints, indexes, and triggers

<!-- EOF -->