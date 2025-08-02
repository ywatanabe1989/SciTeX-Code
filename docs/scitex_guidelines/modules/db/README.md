# scitex.db Module Documentation

## Overview

The `scitex.db` module provides a unified interface for database operations with support for SQLite3 and PostgreSQL. It offers a high-level API with comprehensive functionality including transactions, batch operations, backups, and schema management. The module is designed for both simple data storage needs and complex database operations in scientific computing environments.

## Module Structure

```
scitex.db/
├── _SQLite3.py           # SQLite3 database implementation
├── _PostgreSQL.py        # PostgreSQL database implementation
├── _BaseMixins/          # Base mixin interfaces
├── _SQLite3Mixins/       # SQLite3-specific mixins
├── _PostgreSQLMixins/    # PostgreSQL-specific mixins
├── _delete_duplicates.py # Duplicate removal utilities
└── _inspect.py           # Database inspection tools
```

## Database Implementations

### 1. SQLite3 Database

Lightweight, file-based database perfect for local data storage and prototyping.

```python
import scitex.db

# Create/connect to SQLite database
db = scitex.db.SQLite3("my_data.db")

# Create a table
db.create_table(
    "experiments",
    {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "accuracy": "REAL",
        "parameters": "TEXT"
    }
)

# Insert data
db.insert("experiments", {
    "name": "exp_001",
    "accuracy": 0.95,
    "parameters": '{"lr": 0.001, "batch_size": 32}'
})

# Query data
results = db.select("experiments", where="accuracy > 0.9")
print(results)

# Close connection
db.close()
```

### 2. PostgreSQL Database

Full-featured database for production environments and multi-user access.

```python
import scitex.db

# Connect to PostgreSQL
db = scitex.db.PostgreSQL(
    dbname="research_db",
    user="researcher",
    password="secure_password",
    host="localhost",
    port=5432
)

# Create table with advanced features
db.create_table(
    "neural_recordings",
    {
        "id": "SERIAL PRIMARY KEY",
        "subject_id": "VARCHAR(50) NOT NULL",
        "session_date": "DATE",
        "recording_data": "BYTEA",
        "metadata": "JSONB",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
)

# Create index for performance
db.create_index("neural_recordings", ["subject_id", "session_date"])
```

## Core Features

### 1. Basic CRUD Operations

```python
# CREATE - Insert single record
db.insert("users", {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "score": 85.5
})

# READ - Select with conditions
users = db.select(
    "users",
    columns=["name", "email"],
    where="score > 80",
    order_by="score DESC",
    limit=10
)

# UPDATE - Modify records
db.update(
    "users",
    data={"score": 90.0},
    where="name = 'Alice Smith'"
)

# DELETE - Remove records
db.delete("users", where="score < 50")
```

### 2. Batch Operations

Efficient bulk data operations:

```python
# Batch insert
records = [
    {"name": "User1", "score": 75},
    {"name": "User2", "score": 82},
    {"name": "User3", "score": 91}
]
db.insert_many("users", records)

# Batch update
updates = [
    {"id": 1, "score": 80},
    {"id": 2, "score": 85},
    {"id": 3, "score": 90}
]
db.update_many("users", updates, key="id")
```

### 3. Transaction Management

Ensure data consistency with transactions:

```python
# Context manager for automatic commit/rollback
with db.transaction():
    db.insert("accounts", {"name": "Alice", "balance": 1000})
    db.insert("accounts", {"name": "Bob", "balance": 1000})
    
    # Transfer money
    db.update("accounts", {"balance": 900}, where="name = 'Alice'")
    db.update("accounts", {"balance": 1100}, where="name = 'Bob'")
    
    # If any operation fails, all changes are rolled back

# Manual transaction control
db.begin_transaction()
try:
    # Multiple operations
    db.insert(...)
    db.update(...)
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

### 4. Schema Management

```python
# Get table information
tables = db.list_tables()
print(f"Tables: {tables}")

# Get column information
columns = db.get_columns("experiments")
print(f"Columns: {columns}")

# Check if table exists
if db.table_exists("old_data"):
    db.drop_table("old_data")

# Alter table structure
db.add_column("experiments", "notes", "TEXT")
db.drop_column("experiments", "deprecated_field")

# Rename table
db.rename_table("old_name", "new_name")
```

### 5. Index Management

Optimize query performance:

```python
# Create single column index
db.create_index("users", ["email"])

# Create composite index
db.create_index("logs", ["user_id", "timestamp"])

# Create unique index
db.create_index("users", ["username"], unique=True)

# Drop index
db.drop_index("users", "idx_users_email")

# List all indexes
indexes = db.list_indexes("users")
```

### 6. Import/Export Operations

```python
# Export to CSV
db.export_to_csv("experiments", "experiments_backup.csv")

# Import from CSV
db.import_from_csv("experiments", "experiments_data.csv")

# Export to pandas DataFrame
df = db.to_dataframe("experiments")

# Import from pandas DataFrame
db.from_dataframe(df, "experiments", if_exists="append")

# Export query results
query = "SELECT * FROM experiments WHERE accuracy > 0.9"
db.export_query_to_csv(query, "high_accuracy_experiments.csv")
```

### 7. Backup and Restore

```python
# Full database backup
db.backup_database("backup_20250530.sql")

# Restore from backup
db.restore_database("backup_20250530.sql")

# Table-specific backup
db.backup_table("experiments", "experiments_backup.sql")

# Scheduled backups
import schedule

def daily_backup():
    timestamp = scitex.gen.gen_timestamp()
    db.backup_database(f"backup_{timestamp}.sql")

schedule.every().day.at("02:00").do(daily_backup)
```

### 8. Database Maintenance

```python
# Vacuum database (SQLite)
db.vacuum()

# Analyze tables for query optimization
db.analyze()

# Get database statistics
stats = db.get_stats()
print(f"Database size: {stats['size']}")
print(f"Number of tables: {stats['table_count']}")

# Database summary
print(db.summary)  # or simply db()
```

## Advanced Features

### 1. JSON/JSONB Support (PostgreSQL)

```python
# Store complex data as JSON
db.insert("experiments", {
    "name": "exp_001",
    "config": {
        "model": "resnet50",
        "optimizer": {
            "type": "adam",
            "lr": 0.001,
            "betas": [0.9, 0.999]
        }
    }
})

# Query JSON fields
results = db.select(
    "experiments",
    where="config->>'model' = 'resnet50'"
)

# Update JSON fields
db.execute("""
    UPDATE experiments 
    SET config = jsonb_set(config, '{optimizer,lr}', '0.0001')
    WHERE name = 'exp_001'
""")
```

### 2. BLOB Storage

Store binary data like images or numpy arrays:

```python
import numpy as np
import pickle

# Store numpy array
data = np.random.rand(100, 100)
blob_data = pickle.dumps(data)

db.store_blob("arrays", {
    "name": "random_matrix",
    "data": blob_data
})

# Retrieve numpy array
result = db.get_blob("arrays", "data", where="name = 'random_matrix'")
retrieved_data = pickle.loads(result)
```

### 3. Full-Text Search (PostgreSQL)

```python
# Create full-text search index
db.execute("""
    CREATE INDEX idx_fts ON articles 
    USING gin(to_tsvector('english', title || ' ' || content))
""")

# Search documents
results = db.execute("""
    SELECT * FROM articles 
    WHERE to_tsvector('english', title || ' ' || content) 
    @@ plainto_tsquery('english', 'machine learning')
""")
```

### 4. Database Inspection

```python
# Detailed inspection
inspector = scitex.db.inspect(db)

# Get all foreign keys
foreign_keys = inspector.get_foreign_keys("orders")

# Get primary keys
primary_keys = inspector.get_primary_keys("users")

# Get table creation SQL
create_sql = inspector.get_create_table_sql("experiments")

# Database schema diagram (if graphviz installed)
inspector.generate_schema_diagram("schema.png")
```

## Integration with Other SciTeX Modules

### With scitex.io

```python
# Save query results
results = db.select("experiments", where="accuracy > 0.9")
scitex.io.save(results, "high_accuracy_experiments.pkl")

# Load and insert data
data = scitex.io.load("new_experiments.json")
db.insert_many("experiments", data)
```

### With scitex.pd

```python
import scitex.pd

# Convert to pandas DataFrame
df = db.to_dataframe("experiments")

# Apply pandas operations
df = scitex.pd.force_df(df)
summary = df.describe()

# Save back to database
db.from_dataframe(summary, "experiment_summary")
```

### With scitex.plt

```python
# Visualize database metrics
data = db.select("experiments", columns=["timestamp", "accuracy"])
df = pd.DataFrame(data)

fig, ax = scitex.plt.subplots()
ax.plot(df['timestamp'], df['accuracy'])
ax.set_title("Model Accuracy Over Time")
scitex.io.save(fig, "accuracy_trend.png")
```

## Common Workflows

### 1. Experiment Tracking

```python
class ExperimentTracker:
    def __init__(self, db_path="experiments.db"):
        self.db = scitex.db.SQLite3(db_path)
        self._setup_tables()
    
    def _setup_tables(self):
        self.db.create_table("runs", {
            "run_id": "TEXT PRIMARY KEY",
            "experiment_name": "TEXT",
            "start_time": "DATETIME",
            "end_time": "DATETIME",
            "status": "TEXT",
            "config": "TEXT",
            "metrics": "TEXT"
        })
    
    def log_run(self, run_id, config, metrics):
        self.db.insert("runs", {
            "run_id": run_id,
            "experiment_name": config.get("name"),
            "start_time": config.get("start_time"),
            "end_time": scitex.gen.gen_timestamp(),
            "status": "completed",
            "config": json.dumps(config),
            "metrics": json.dumps(metrics)
        })
    
    def get_best_runs(self, metric="accuracy", n=5):
        # Query and parse JSON
        runs = self.db.select("runs")
        
        # Parse metrics and sort
        for run in runs:
            run['metrics'] = json.loads(run['metrics'])
        
        sorted_runs = sorted(
            runs, 
            key=lambda x: x['metrics'].get(metric, 0), 
            reverse=True
        )
        
        return sorted_runs[:n]
```

### 2. Time Series Data Storage

```python
class TimeSeriesDB:
    def __init__(self):
        self.db = scitex.db.PostgreSQL(...)
        self._setup_tables()
    
    def _setup_tables(self):
        self.db.create_table("timeseries", {
            "id": "SERIAL PRIMARY KEY",
            "sensor_id": "VARCHAR(50)",
            "timestamp": "TIMESTAMP",
            "value": "REAL",
            "metadata": "JSONB"
        })
        
        # Create time-based index
        self.db.create_index(
            "timeseries", 
            ["sensor_id", "timestamp"]
        )
    
    def insert_readings(self, sensor_id, readings):
        records = [
            {
                "sensor_id": sensor_id,
                "timestamp": r["timestamp"],
                "value": r["value"],
                "metadata": r.get("metadata", {})
            }
            for r in readings
        ]
        self.db.insert_many("timeseries", records)
    
    def get_time_range(self, sensor_id, start, end):
        return self.db.select(
            "timeseries",
            where=f"""
                sensor_id = '{sensor_id}' 
                AND timestamp BETWEEN '{start}' AND '{end}'
            """,
            order_by="timestamp"
        )
```

### 3. Multi-Database Synchronization

```python
class DatabaseSync:
    def __init__(self, local_db, remote_db):
        self.local = local_db
        self.remote = remote_db
    
    def sync_table(self, table_name, direction="both"):
        if direction in ["up", "both"]:
            # Local to remote
            local_data = self.local.select(table_name)
            self.remote.insert_many(
                table_name, 
                local_data,
                on_conflict="update"
            )
        
        if direction in ["down", "both"]:
            # Remote to local
            remote_data = self.remote.select(table_name)
            self.local.insert_many(
                table_name,
                remote_data,
                on_conflict="update"
            )
```

## Best Practices

### 1. Connection Management
Always close connections properly:
```python
# Using context manager (recommended)
with scitex.db.SQLite3("data.db") as db:
    db.insert(...)
    # Connection automatically closed

# Manual management
db = scitex.db.PostgreSQL(...)
try:
    db.insert(...)
finally:
    db.close()
```

### 2. SQL Injection Prevention
Use parameterized queries:
```python
# Good - parameterized
user_id = request.get("user_id")
results = db.select("users", where="id = ?", params=[user_id])

# Bad - string concatenation
results = db.select("users", where=f"id = {user_id}")  # DON'T DO THIS
```

### 3. Performance Optimization
```python
# Use indexes for frequently queried columns
db.create_index("logs", ["timestamp", "user_id"])

# Batch operations instead of loops
# Good
db.insert_many("records", large_list)

# Bad
for record in large_list:
    db.insert("records", record)
```

### 4. Regular Maintenance
```python
# Schedule regular maintenance
def maintenance():
    db.vacuum()
    db.analyze()
    db.backup_database(f"backup_{scitex.gen.gen_timestamp()}.sql")

# Remove old backups
import os
from datetime import datetime, timedelta

def cleanup_old_backups(directory, days=30):
    cutoff = datetime.now() - timedelta(days=days)
    for file in os.listdir(directory):
        if file.startswith("backup_") and file.endswith(".sql"):
            file_time = os.path.getmtime(os.path.join(directory, file))
            if datetime.fromtimestamp(file_time) < cutoff:
                os.remove(os.path.join(directory, file))
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```python
   # Check PostgreSQL service
   import subprocess
   subprocess.run(["sudo", "service", "postgresql", "status"])
   
   # Test connection
   try:
       db = scitex.db.PostgreSQL(...)
       print("Connection successful")
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

2. **Locked Database (SQLite)**
   ```python
   # Set timeout for busy database
   db = scitex.db.SQLite3("data.db", timeout=30)
   
   # Enable WAL mode for better concurrency
   db.execute("PRAGMA journal_mode=WAL")
   ```

3. **Performance Issues**
   ```python
   # Analyze query performance
   db.execute("EXPLAIN ANALYZE SELECT ...")
   
   # Check missing indexes
   tables = db.list_tables()
   for table in tables:
       indexes = db.list_indexes(table)
       print(f"{table}: {len(indexes)} indexes")
   ```

### Debug Mode
Enable logging:
```python
from scitex import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('scitex.db')
```

## References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python DB-API 2.0](https://www.python.org/dev/peps/pep-0249/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)