<!-- ---
!-- title: ./scitex_repo/src/scitex/db/README.md
!-- author: ywatanabe
!-- date: 2024-11-24 23:08:15
!-- --- -->


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
