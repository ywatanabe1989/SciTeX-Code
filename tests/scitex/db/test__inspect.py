#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:15:00 (Claude)"
# File: /tests/scitex/db/test__inspect.py

import os
import sys
import tempfile
import shutil
import pytest
import sqlite3
import pandas as pd
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from scitex.db import inspect, Inspector


class TestInspect:
    """Test cases for database inspection functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test databases."""
        tmpdir = tempfile.mkdtemp()
        yield tmpdir
        # Cleanup
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    @pytest.fixture
    def db_path(self, temp_dir):
        """Get a temporary database path."""
        return os.path.join(temp_dir, "test.db")

    @pytest.fixture
    def sample_db(self, db_path):
        """Create a sample database with multiple tables."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER
            )
        """)
        
        # Insert sample data
        users_data = [
            (1, "Alice", "alice@example.com", 30),
            (2, "Bob", "bob@example.com", 25),
            (3, "Charlie", "charlie@example.com", 35),
            (4, "David", "david@example.com", 28),
            (5, "Eve", "eve@example.com", 32),
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users_data)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product TEXT,
                price REAL,
                data BLOB,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insert order data
        orders_data = [
            (1, 1, "Laptop", 999.99, b"binary_data_1"),
            (2, 1, "Mouse", 29.99, b"binary_data_2"),
            (3, 2, "Keyboard", 79.99, b"binary_data_3"),
            (4, 3, "Monitor", 299.99, b"binary_data_4"),
        ]
        cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders_data)
        
        conn.commit()
        conn.close()
        
        return db_path

    def test_inspector_init(self, sample_db):
        """Test Inspector initialization."""
        # Act
        inspector = Inspector(sample_db)
        
        # Assert
        assert inspector.db_path == sample_db

    def test_inspector_init_nonexistent(self, temp_dir):
        """Test Inspector initialization with non-existent database."""
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            Inspector(os.path.join(temp_dir, "nonexistent.db"))

    def test_get_table_names(self, sample_db):
        """Test retrieving table names."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        tables = inspector.get_table_names()
        
        # Assert
        assert "users" in tables
        assert "orders" in tables
        assert len(tables) >= 2  # At least our two tables

    def test_get_table_info(self, sample_db):
        """Test retrieving table structure information."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        info = inspector.get_table_info("users")
        
        # Assert
        assert len(info) == 4  # 4 columns in users table
        
        # Check column names
        column_names = [col[1] for col in info]
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names
        assert "age" in column_names
        
        # Check constraints
        for col in info:
            if col[1] == "id":
                assert "PRIMARY KEY" in col[-1]
            if col[1] == "name":
                assert "NOT NULL" in col[-1]

    def test_get_sample_data(self, sample_db):
        """Test retrieving sample data from table."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        columns, data, total_rows = inspector.get_sample_data("users", limit=3)
        
        # Assert
        assert columns == ["id", "name", "email", "age"]
        assert len(data) == 3  # Limited to 3 rows
        assert total_rows == 5  # Total 5 users in the table
        
        # Verify data content
        assert data[0][1] == "Alice"  # First user's name
        assert data[1][1] == "Bob"    # Second user's name

    def test_get_sample_data_with_blob(self, sample_db):
        """Test retrieving sample data with BLOB columns."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        columns, data, total_rows = inspector.get_sample_data("orders")
        
        # Assert
        assert "data" in columns
        assert len(data) > 0
        # BLOB data should be returned as bytes
        assert isinstance(data[0][4], bytes)

    def test_inspector_inspect_all_tables(self, sample_db):
        """Test inspecting all tables."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        results = inspector.inspect()
        
        # Assert
        assert len(results) >= 2  # At least users and orders tables
        
        # Check that each result is a DataFrame
        for result in results:
            assert isinstance(result, pd.DataFrame)
            assert "table_name" in result.index.names
            assert "n_total_rows" in result.index.names

    def test_inspector_inspect_specific_tables(self, sample_db):
        """Test inspecting specific tables."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        results = inspector.inspect(table_names=["users"])
        
        # Assert
        assert len(results) == 1
        
        # Check the result
        df = results[0]
        assert df.index.get_level_values("table_name")[0] == "users"
        assert df.index.get_level_values("n_total_rows")[0] == 5

    def test_inspector_inspect_blob_handling(self, sample_db):
        """Test that BLOB data is handled correctly in inspection."""
        # Arrange
        inspector = Inspector(sample_db)
        
        # Act
        results = inspector.inspect(table_names=["orders"])
        
        # Assert
        df = results[0]
        # BLOB columns should show "<BLOB>" in the DataFrame
        if len(df) > 0:
            assert "<BLOB>" in df["data"].values

    def test_inspect_function(self, sample_db, capsys):
        """Test the main inspect function."""
        # Act
        results = inspect(sample_db, verbose=True)
        
        # Assert
        assert len(results) >= 2
        
        # Check that output was printed (verbose=True)
        captured = capsys.readouterr()
        assert "users" in captured.out or "orders" in captured.out

    def test_inspect_function_quiet(self, sample_db, capsys):
        """Test inspect function with verbose=False."""
        # Act
        results = inspect(sample_db, verbose=False)
        
        # Assert
        assert len(results) >= 2
        
        # Check that no output was printed
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_inspect_specific_tables(self, sample_db):
        """Test inspecting specific tables only."""
        # Act
        results = inspect(sample_db, table_names=["users"], verbose=False)
        
        # Assert
        assert len(results) == 1
        assert results[0].index.get_level_values("table_name")[0] == "users"

    def test_empty_database(self, db_path):
        """Test inspecting an empty database."""
        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Act
        results = inspect(db_path, verbose=False)
        
        # Assert
        assert len(results) == 0

    def test_table_with_no_data(self, db_path):
        """Test inspecting a table with no data."""
        # Create database with empty table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE empty_table (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()
        
        # Act
        inspector = Inspector(db_path)
        columns, data, total_rows = inspector.get_sample_data("empty_table")
        
        # Assert
        assert columns == ["id", "name"]
        assert len(data) == 0
        assert total_rows == 0

    def test_inspector_with_complex_schema(self, db_path):
        """Test inspector with complex table schema."""
        # Create database with complex schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE complex_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                score REAL CHECK(score >= 0 AND score <= 100),
                category TEXT CHECK(category IN ('A', 'B', 'C'))
            )
        """)
        
        # Add some data
        cursor.execute(
            "INSERT INTO complex_table (name, score, category) VALUES (?, ?, ?)",
            ("Test", 85.5, "A")
        )
        
        conn.commit()
        conn.close()
        
        # Act
        inspector = Inspector(db_path)
        info = inspector.get_table_info("complex_table")
        
        # Assert
        assert len(info) == 6  # 6 columns
        
        # Check primary key constraint
        id_col = [col for col in info if col[1] == "id"][0]
        assert "PRIMARY KEY" in id_col[-1]

    def test_inspect_with_indexes(self, db_path):
        """Test that index information is properly captured."""
        # Create database with indexes
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE indexed_table (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                username TEXT
            )
        """)
        
        # Create additional index
        cursor.execute("CREATE INDEX idx_username ON indexed_table(username)")
        
        conn.commit()
        conn.close()
        
        # Act
        inspector = Inspector(db_path)
        info = inspector.get_table_info("indexed_table")
        
        # Assert
        # The primary key constraint should be detected
        id_info = [col for col in info if col[1] == "id"][0]
        assert "PRIMARY KEY" in id_info[-1]


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
