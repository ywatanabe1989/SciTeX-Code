#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 12:00:00 (ywatanabe)"
# File: ./examples/scitex/db/database_operations.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/db/database_operations.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic SQLite database operations
  - Shows table creation and management
  - Performs CRUD operations (Create, Read, Update, Delete)
  - Handles batch operations for performance
  - Stores NumPy arrays as BLOBs
  - Manages transactions safely
  - Imports/exports data in various formats
  - Maintains database integrity

Dependencies:
  - scripts: None
  - packages: numpy, pandas, tempfile, datetime, scitex

IO:
  - input-files: None
  - output-files:
    - database_operations_out/example.db
    - database_operations_out/backup.db
    - database_operations_out/exported_*.csv
    - database_operations_out/arrays/*.npy
"""

"""Imports"""
import argparse
import numpy as np
import pandas as pd
import tempfile
from typing import Dict, List, Any


def example_basic_operations():
    """Demonstrates basic database connection and operations."""
    import scitex
    import tempfile

    print("\n=== Basic Database Operations ===")

    # Create a temporary database for examples
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "example.db")

        # Initialize SQLite database
        db = scitex.db.SQLite3(db_path)

        # Create a simple table
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "age": "INTEGER",
            "email": "TEXT UNIQUE",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }

        db.create_table("users", columns)
        print("Created 'users' table")

        # Insert single row
        db.execute(
            "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
            ("Alice Johnson", 30, "alice@example.com"),
        )
        print("Inserted single user")

        # Query data
        db.execute("SELECT * FROM users")
        result = db.cursor.fetchall()
        print(f"Query result: {result}")

        # Get table schema
        schema = db.get_table_schema("users")
        print(f"\nTable schema:\n{schema}")

        # Close connection
        db.close()


def example_batch_operations():
    """Demonstrates efficient batch operations."""
    import scitex
    import tempfile

    print("\n=== Batch Operations ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "batch_example.db")
        db = scitex.db.SQLite3(db_path)

        # Create products table
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "price": "REAL",
            "category": "TEXT",
            "stock": "INTEGER DEFAULT 0",
        }
        db.create_table("products", columns)

        # Prepare batch data
        products = [
            {"name": "Laptop", "price": 999.99, "category": "Electronics", "stock": 50},
            {"name": "Mouse", "price": 29.99, "category": "Electronics", "stock": 200},
            {
                "name": "Keyboard",
                "price": 79.99,
                "category": "Electronics",
                "stock": 150,
            },
            {
                "name": "Monitor",
                "price": 299.99,
                "category": "Electronics",
                "stock": 75,
            },
            {"name": "Desk", "price": 199.99, "category": "Furniture", "stock": 30},
            {"name": "Chair", "price": 149.99, "category": "Furniture", "stock": 40},
        ]

        # Batch insert
        db.insert_many("products", products, batch_size=3)
        print(f"Inserted {len(products)} products in batches")

        # Query with conditions
        electronics = db.get_rows(
            "products", where="category = 'Electronics'", order_by="price DESC"
        )
        print(f"\nElectronics products:\n{electronics}")

        # Batch update - apply 10% discount
        updates = [{"name": p["name"], "price": p["price"] * 0.9} for p in products]
        db.update_many("products", updates, where="name = ?")
        print("\nApplied 10% discount to all products")

        # Verify updates
        discounted = db.get_rows("products", columns=["name", "price"])
        print(f"\nDiscounted prices:\n{discounted}")

        db.close()


def example_numpy_array_storage():
    """Demonstrates storing and retrieving NumPy arrays as BLOBs."""
    import scitex
    import numpy as np
    import tempfile

    print("\n=== NumPy Array Storage ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "array_example.db")
        db = scitex.db.SQLite3(db_path)

        # Create table for time series data
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "sensor_id": "TEXT",
            "timestamp": "TIMESTAMP",
            "data": "BLOB",
            "sampling_rate": "REAL",
        }
        db.create_table("sensor_data", columns)

        # Generate sample sensor data
        n_samples = 1000
        n_channels = 8
        sensor_data = np.random.randn(n_samples, n_channels).astype(np.float32)

        # Save array with metadata
        db.save_array(
            "sensor_data",
            sensor_data,
            column="data",
            additional_columns={
                "sensor_id": "SENSOR_001",
                "timestamp": "2025-05-31 12:00:00",
                "sampling_rate": 250.0,
            },
        )
        print(f"Saved sensor data array with shape {sensor_data.shape}")

        # Load array back
        loaded_data = db.load_array("sensor_data", column="data", ids=1)  # First record
        print(f"Loaded array shape: {loaded_data.shape}")
        print(f"Data integrity check: {np.allclose(sensor_data, loaded_data[0])}")

        # Save multiple arrays
        print("\nSaving multiple sensor readings...")
        for i in range(5):
            data = np.random.randn(n_samples, n_channels).astype(np.float32)
            db.save_array(
                "sensor_data",
                data,
                column="data",
                additional_columns={
                    "sensor_id": f"SENSOR_{i+2:03d}",
                    "timestamp": f"2025-05-31 12:{i+1:02d}:00",
                    "sampling_rate": 250.0,
                },
            )

        # Load all arrays
        all_data = db.load_array("sensor_data", column="data", ids="all")
        print(f"Loaded all arrays, shape: {all_data.shape}")

        # Query with array data
        df = db.get_rows("sensor_data")
        array_dict = db.get_array_dict(df, columns=["data"])
        print(f"\nArray dictionary keys: {list(array_dict.keys())}")
        print(f"Combined data shape: {array_dict['data'].shape}")

        db.close()


def example_transaction_management():
    """Demonstrates transaction management for data integrity."""
    import scitex
    import tempfile

    print("\n=== Transaction Management ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "transaction_example.db")
        db = scitex.db.SQLite3(db_path)

        # Create accounts table for banking example
        columns = {
            "id": "INTEGER PRIMARY KEY",
            "account_number": "TEXT UNIQUE",
            "balance": "REAL DEFAULT 0",
            "status": "TEXT DEFAULT 'active'",
        }
        db.create_table("accounts", columns)

        # Create initial accounts
        accounts = [
            {"account_number": "ACC001", "balance": 1000.0},
            {"account_number": "ACC002", "balance": 500.0},
        ]
        db.insert_many("accounts", accounts)

        print("Initial balances:")
        print(db.get_rows("accounts", columns=["account_number", "balance"]))

        # Successful transaction - transfer money
        print("\nPerforming successful transfer...")
        try:
            with db.transaction():
                # Deduct from first account
                db.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                    (200.0, "ACC001"),
                )
                # Add to second account
                db.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                    (200.0, "ACC002"),
                )
                print("Transfer completed successfully")
        except Exception as e:
            print(f"Transfer failed: {e}")

        print("\nBalances after transfer:")
        print(db.get_rows("accounts", columns=["account_number", "balance"]))

        # Failed transaction - insufficient funds
        print("\nAttempting invalid transfer (will rollback)...")
        try:
            with db.transaction():
                # Try to deduct more than available
                db.execute(
                    "UPDATE accounts SET balance = balance - ? WHERE account_number = ?",
                    (2000.0, "ACC001"),
                )
                # Check balance
                db.execute(
                    "SELECT balance FROM accounts WHERE account_number = ?", ("ACC001",)
                )
                balance = db.cursor.fetchone()[0]
                if balance < 0:
                    raise ValueError("Insufficient funds!")
                # This won't execute due to exception
                db.execute(
                    "UPDATE accounts SET balance = balance + ? WHERE account_number = ?",
                    (2000.0, "ACC002"),
                )
        except ValueError as e:
            print(f"Transfer failed as expected: {e}")

        print("\nBalances after failed transfer (should be unchanged):")
        print(db.get_rows("accounts", columns=["account_number", "balance"]))

        db.close()


def example_import_export():
    """Demonstrates importing from and exporting to CSV files."""
    import scitex
    import tempfile
    import pandas as pd

    print("\n=== Import/Export Operations ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "import_export.db")
        csv_path = os.path.join(tmpdir, "employees.csv")
        export_path = os.path.join(tmpdir, "filtered_employees.csv")

        # Create sample CSV data
        employees_df = pd.DataFrame(
            {
                "name": [
                    "John Doe",
                    "Jane Smith",
                    "Bob Johnson",
                    "Alice Brown",
                    "Charlie Davis",
                ],
                "department": ["IT", "HR", "IT", "Finance", "IT"],
                "salary": [75000, 65000, 80000, 70000, 72000],
                "hire_date": [
                    "2020-01-15",
                    "2019-06-01",
                    "2021-03-20",
                    "2020-11-10",
                    "2022-02-01",
                ],
            }
        )
        employees_df.to_csv(csv_path, index=False)
        print(f"Created sample CSV with {len(employees_df)} employees")

        # Initialize database and import CSV
        db = scitex.db.SQLite3(db_path)
        db.load_from_csv("employees", csv_path, if_exists="replace")
        print(f"\nImported CSV into 'employees' table")

        # Verify import
        print("\nAll employees:")
        all_employees = db.get_rows("employees")
        print(all_employees)

        # Export filtered data
        db.save_to_csv(
            "employees",
            export_path,
            columns=["name", "department", "salary"],
            where="department = 'IT' AND salary > 70000",
        )
        print(f"\nExported IT employees with salary > 70000 to {export_path}")

        # Read exported file
        exported_df = pd.read_csv(export_path)
        print(f"\nExported data:\n{exported_df}")

        db.close()


def example_advanced_features():
    """Demonstrates advanced database features."""
    import scitex
    import tempfile

    print("\n=== Advanced Features ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "advanced.db")
        db = scitex.db.SQLite3(db_path)

        # Create related tables with foreign keys
        # Authors table
        db.create_table(
            "authors",
            {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT NOT NULL",
                "email": "TEXT UNIQUE",
            },
        )

        # Books table with foreign key
        db.create_table(
            "books",
            {
                "id": "INTEGER PRIMARY KEY",
                "title": "TEXT NOT NULL",
                "author_id": "INTEGER",
                "published_year": "INTEGER",
                "isbn": "TEXT UNIQUE",
            },
            foreign_keys=[
                {"tgt_column": "author_id", "src_table": "authors", "src_column": "id"}
            ],
        )

        # Enable foreign key constraints
        db.enable_foreign_keys()

        # Insert authors
        authors = [
            {"name": "George Orwell", "email": "gorwell@example.com"},
            {"name": "Jane Austen", "email": "jausten@example.com"},
            {"name": "Mark Twain", "email": "mtwain@example.com"},
        ]
        db.insert_many("authors", authors)

        # Get author IDs
        author_ids = {}
        for author in authors:
            db.execute("SELECT id FROM authors WHERE name = ?", (author["name"],))
            author_ids[author["name"]] = db.cursor.fetchone()[0]

        # Insert books with foreign key references
        books = [
            {
                "title": "1984",
                "author_id": author_ids["George Orwell"],
                "published_year": 1949,
                "isbn": "978-0451524935",
            },
            {
                "title": "Animal Farm",
                "author_id": author_ids["George Orwell"],
                "published_year": 1945,
                "isbn": "978-0451526342",
            },
            {
                "title": "Pride and Prejudice",
                "author_id": author_ids["Jane Austen"],
                "published_year": 1813,
                "isbn": "978-0141439518",
            },
        ]
        db.insert_many("books", books)

        # Create indexes for better query performance
        db.create_index("books", ["author_id"], unique=False)
        db.create_index("books", ["published_year"], unique=False)
        print("Created indexes on books table")

        # Complex query with JOIN
        query = """
        SELECT b.title, a.name as author, b.published_year
        FROM books b
        JOIN authors a ON b.author_id = a.id
        WHERE b.published_year < 1950
        ORDER BY b.published_year
        """
        db.execute(query)
        results = pd.DataFrame(
            db.cursor.fetchall(), columns=["title", "author", "published_year"]
        )
        print(f"\nBooks published before 1950:\n{results}")

        # Database statistics
        print("\nDatabase Statistics:")
        for table in ["authors", "books"]:
            stats = db.get_table_stats(table)
            print(f"{table}: {stats['row_count']} rows, {stats['total_size']} bytes")

        # Summary view
        print("\nDatabase Summary:")
        db()  # Calls the summary method

        db.close()


def example_database_maintenance():
    """Demonstrates database maintenance operations."""
    import scitex
    import tempfile

    print("\n=== Database Maintenance ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "maintenance.db")
        backup_path = os.path.join(tmpdir, "backup.db")

        db = scitex.db.SQLite3(db_path)

        # Create and populate a table
        db.create_table(
            "logs",
            {
                "id": "INTEGER PRIMARY KEY",
                "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "level": "TEXT",
                "message": "TEXT",
            },
        )

        # Insert many log entries
        logs = [{"level": "INFO", "message": f"Log entry {i}"} for i in range(1000)]
        db.insert_many("logs", logs)
        print(f"Created {len(logs)} log entries")

        # Delete old logs
        db.delete_where("logs", "id < 500")
        print("Deleted first 500 logs")

        # Check database size before optimization
        initial_stats = db.get_table_stats("logs")
        print(f"\nBefore optimization: {initial_stats}")

        # Optimize database (skip vacuum for example speed)
        print("\nOptimizing database...")
        # Note: db.optimize() includes VACUUM which can be slow
        # For demo purposes, we'll just run ANALYZE
        db.execute("ANALYZE")

        # Check size after optimization
        optimized_stats = db.get_table_stats("logs")
        print(f"After optimization: {optimized_stats}")

        # Create backup
        def backup_progress(progress, total):
            percent = (progress / total) * 100
            print(f"\rBackup progress: {percent:.1f}%", end="")

        print("\n\nCreating backup...")
        db.backup(backup_path, progress=backup_progress)
        print("\nBackup completed!")

        # Verify backup
        backup_db = scitex.db.SQLite3(backup_path)
        backup_count = backup_db.get_row_count("logs")
        print(f"\nBackup verified: {backup_count} logs")

        db.close()
        backup_db.close()


def main(args):
    """Run all database examples."""
    print("=" * 60)
    print("SciTeX Database Operations Examples")
    print("=" * 60)

    # Run examples
    example_basic_operations()
    example_batch_operations()
    example_numpy_array_storage()
    example_transaction_management()
    example_import_export()
    example_advanced_features()
    example_database_maintenance()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="Database operations examples")
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    # Start scitex framework
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    # Main
    exit_status = main(args)

    # Close the scitex framework
    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
