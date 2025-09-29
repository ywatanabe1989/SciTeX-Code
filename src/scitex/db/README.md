<!-- ---
!-- Timestamp: 2025-09-10 07:43:20
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/README.md
!-- --- -->

<!-- ---
!-- title: ./scitex_repo/src/scitex/db/README.md
!-- author: ywatanabe
!-- date: 2024-11-24 23:08:15
!-- --- -->

# Database Module - SQLite3 Usage

## Cli
```bash
python -m scitex.db inspect database.db
python -m scitex.db health database1.db database2.db --fix
```

## Basic Usage

```python
from scitex.db import SQLite3

# Initialize database connection
db = SQLite3("my_database.db")

# Create a table
db.create_table(
    "users",
    {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT",
        "email": "TEXT",
        "data": "BLOB"  # Automatically gets metadata columns
    }
)

# Insert data
db.insert_many("users", [
    {"name": "John", "email": "john@example.com"},
    {"name": "Jane", "email": "jane@example.com"}
])

# Query data
results = db.get_rows("users", where="name LIKE 'J%'")
print(results)

# Update data
db.update_where("users", 
    {"email": "newemail@example.com"},
    "name = 'John'"
)

# Get database summary
db.summary  # or db()
```

## Array Storage

```python
import numpy as np

# Save numpy arrays
data = np.random.rand(100, 50)
db.save_array("experiments", data, column="features", 
              additional_columns={"experiment_id": 1})

# Load arrays
loaded_data = db.load_array("experiments", "features", ids=[1, 2, 3])

# Bulk save with compression
db = SQLite3("data.db", compress_by_default=True)
for ii in range(10):
    arr = np.random.rand(1000, 1000)
    db.save_array("large_data", arr, ids=[ii])
```

## Blob Storage for Any Objects

```python
# Save any Python object
my_dict = {"key": "value", "data": [1, 2, 3]}
db.save_blob("cache", my_dict, "my_key")

# Load objects
loaded_dict = db.load_blob("cache", "my_key")

# Load all objects
all_data = db.load_blob("cache")  # Returns dict of all key-value pairs
```

## Batch Operations

```python
# Batch insert with transaction safety
users = [
    {"name": f"User{ii}", "email": f"user{ii}@example.com"}
    for ii in range(1000)
]
db.insert_many("users", users, batch_size=100)

# Batch update
updates = [
    {"id": ii, "status": "active"} 
    for ii in range(1, 101)
]
db.update_many("users", updates, where="id = ?")
```

## Temporary Database

```python
# Use temporary copy for analysis without affecting original
db = SQLite3("production.db", use_temp=True)
# All operations work on temporary copy
# Original file remains unchanged
```

## Advanced Features

```python
# Transaction management
with db.transaction():
    db.insert_many("table1", data1)
    db.update_where("table2", updates, "condition")
    # Auto-commit or rollback on Exception

# Table management
db.add_column("users", "age", "INTEGER", default_value=0)
db.create_index("users", ["email"], unique=True)

# Maintenance
db.vacuum()  # Reclaim space
db.optimize()  # Full optimization

# Import/Export
db.load_from_csv("users", "data.csv")
db.save_to_csv("users", "backup.csv", where="active = 1")
```

## Key Features

1. **Automatic Metadata**: BLOB columns get dtype and shape columns automatically
2. **Compression**: Optional compression for large data
3. **Thread Safety**: Built-in locking for concurrent access
4. **Transaction Support**: Context managers for safe operations
5. **Batch Processing**: Efficient bulk operations
6. **Temporary Databases**: Safe analysis on copies
7. **Maintenance Tools**: Vacuum, optimize, backup/restore
8. **Type Safety**: Automatic parameter sanitization

## Performance Tips

- Use `batch_size` parameter for large datasets
- Enable compression for large arrays: `compress_by_default=True`
- Use temporary databases for analysis: `use_temp=True`
- Regular maintenance: `db.vacuum()` and `db.optimize()`


# PostgreSQL Database Interface

1. Install PostgreSQL:
```bash
sudo apt install postgresql postgresql-contrib
```

2. Start PostgreSQL service:
```bash
sudo service postgresql start
```

3. Create a database and user:
```bash
sudo -u postgres psql

postgres=# CREATE USER ywatanabe WITH PASSWORD 'your_password';
postgres=# CREATE DATABASE ywatanabe;
postgres=# GRANT ALL PRIVILEGES ON DATABASE ywatanabe TO ywatanabe;
postgres=# ALTER USER ywatanabe WITH SUPERUSER;
postgres=# \q
```

<!-- 4. Edit PostgreSQL configuration:
 !-- ```bash
 !-- sudo nano /etc/postgresql/[version]/main/postgresql.conf
 !-- # Set: listen_addresses = '*'
 !-- 
 !-- sudo nano /etc/postgresql/[version]/main/pg_hba.conf
 !-- # Add: host all all 0.0.0.0/0 md5
 !-- ``` -->

4. Restart PostgreSQL:
```bash
sudo service postgresql restart
```

## Basic Usage

```python
from scitex.db import PostgresDB

# Initialize connection
db = PostgresDB(
    dbname="your_database",
    user="your_username",
    password="your_password",
    host="localhost",
    port=5432
)

# Create a table
db.create_table(
    "users",
    {
        "id": "SERIAL PRIMARY KEY",
        "name": "VARCHAR(100)",
        "email": "VARCHAR(100)"
    }
)

# Insert data
db.insert("users", {"name": "John Doe", "email": "john@example.com"})

# Batch insert
users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
]
db.insert_many("users", users)

# Query data
results = db.select("users", where="name LIKE 'J%'")
print(results)

# Update data
db.update("users", 
    data={"email": "newemail@example.com"},
    where="name = 'John Doe'"
)

# Delete data
db.delete("users", where="name = 'Bob'")

# Get database summary
db.summary  # or db()

# Transaction handling
with db.transaction():
    db.insert("users", {"name": "Charlie", "email": "charlie@example.com"})
    db.update("users", {"email": "new@example.com"}, where="name = 'Alice'")

# Backup and restore
db.backup_database("backup.sql")
db.restore_database("backup.sql")

# Close connection
db.close()
```

## Features

- Full transaction support
- Batch operations
- Table management (create, drop, alter)
- Index management
- Import/Export functionality
- Database maintenance
- Backup and restore
- Query builder
- Connection management
- Schema inspection

## Requirements

- Python 3.6+
- psycopg2
- pandas (for DataFrame operations)

<!-- EOF -->