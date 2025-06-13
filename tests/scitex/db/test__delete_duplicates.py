#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 13:10:00 (Claude)"
# File: /tests/scitex/db/test__delete_duplicates.py

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

from scitex.db import (
    delete_duplicates,
    _sort_db,
    _determine_columns,
    _fetch_as_df,
    _find_duplicated,
    verify_duplicated_index,
    _delete_entry
)


class TestDeleteDuplicates:
    """Test cases for delete_duplicates functionality."""

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
    def db_with_duplicates(self, db_path):
        """Create a database with duplicate entries."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL,
                data BLOB
            )
        """)
        
        # Insert data with duplicates
        data = [
            (1, "Alice", 100.0, b"data1"),
            (2, "Bob", 200.0, b"data2"),
            (3, "Alice", 100.0, b"data1"),  # Duplicate of row 1
            (4, "Charlie", 300.0, b"data3"),
            (5, "Bob", 200.0, b"data2"),  # Duplicate of row 2
            (6, "Alice", 100.0, b"data1"),  # Another duplicate of row 1
        ]
        
        cursor.executemany(
            "INSERT INTO test_table VALUES (?, ?, ?, ?)",
            data
        )
        conn.commit()
        conn.close()
        
        return db_path

    def test_delete_duplicates_basic(self, db_with_duplicates):
        """Test basic duplicate deletion functionality."""
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_with_duplicates,
            "test_table",
            columns=["name", "value"],
            dry_run=False
        )
        
        # Assert
        assert total_processed is not None
        assert total_duplicates is not None
        assert total_duplicates == 3  # We have 3 duplicate rows
        
        # Verify database state
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3  # Should have only 3 unique entries

    def test_delete_duplicates_dry_run(self, db_with_duplicates):
        """Test dry run mode doesn't modify database."""
        # Get initial count
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        initial_count = cursor.fetchone()[0]
        conn.close()
        
        # Act
        delete_duplicates(
            db_with_duplicates,
            "test_table",
            columns=["name", "value"],
            dry_run=True
        )
        
        # Assert - count should remain the same
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        final_count = cursor.fetchone()[0]
        conn.close()
        
        assert final_count == initial_count

    def test_delete_duplicates_all_columns(self, db_with_duplicates):
        """Test deleting duplicates considering all columns."""
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_with_duplicates,
            "test_table",
            columns="all",
            include_blob=True,
            dry_run=False
        )
        
        # Assert
        assert total_duplicates == 3  # Same duplicates when considering all columns

    def test_delete_duplicates_exclude_blob(self, db_with_duplicates):
        """Test deleting duplicates excluding BLOB columns."""
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_with_duplicates,
            "test_table",
            columns="all",
            include_blob=False,  # Exclude BLOB columns
            dry_run=False
        )
        
        # Assert
        assert total_duplicates == 3  # Should still find duplicates in non-BLOB columns

    def test_sort_db(self, db_path):
        """Test database sorting functionality."""
        # Setup
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        """)
        
        # Insert unordered data
        data = [
            (1, "Charlie", 300.0),
            (2, "Alice", 100.0),
            (3, "Bob", 200.0),
        ]
        cursor.executemany("INSERT INTO test_table VALUES (?, ?, ?)", data)
        conn.commit()
        
        # Act
        _sort_db(cursor, "test_table", ["name"])
        conn.commit()
        
        # Assert - check order
        cursor.execute("SELECT name FROM test_table")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert names == ["Alice", "Bob", "Charlie"]

    def test_determine_columns(self, db_path):
        """Test column determination logic."""
        # Setup
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL,
                data BLOB
            )
        """)
        conn.commit()
        
        # Test "all" with include_blob=True
        columns = _determine_columns(cursor, "test_table", "all", include_blob=True)
        assert "id" in columns
        assert "name" in columns
        assert "value" in columns
        assert "data" in columns
        
        # Test "all" with include_blob=False
        columns = _determine_columns(cursor, "test_table", "all", include_blob=False)
        assert "data" not in columns  # BLOB column should be excluded
        
        # Test specific columns
        columns = _determine_columns(cursor, "test_table", ["name", "value"], include_blob=False)
        assert columns == ["name", "value"]
        
        # Test single column as string
        columns = _determine_columns(cursor, "test_table", "name", include_blob=False)
        assert columns == ["name"]
        
        conn.close()

    def test_fetch_as_df(self, db_with_duplicates):
        """Test fetching data as DataFrame."""
        # Setup
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        
        # Act
        df = _fetch_as_df(cursor, ["name", "value"], "test_table")
        
        # Assert
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6  # Total rows including duplicates
        assert list(df.columns) == ["name", "value"]
        
        conn.close()

    def test_find_duplicated(self):
        """Test finding duplicated entries in DataFrame."""
        # Setup
        data = {
            "name": ["Alice", "Bob", "Alice", "Charlie", "Bob"],
            "value": [100, 200, 100, 300, 200]
        }
        df = pd.DataFrame(data)
        
        # Act
        duplicates = _find_duplicated(df)
        
        # Assert
        assert len(duplicates) == 2  # Two duplicate rows
        assert duplicates.iloc[0]["name"] == "Alice"
        assert duplicates.iloc[1]["name"] == "Bob"

    def test_verify_duplicated_index(self, db_with_duplicates):
        """Test verification of duplicated entries."""
        # Setup
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        
        duplicated_row = pd.Series({"name": "Alice", "value": 100.0})
        
        # Act
        query, is_verified = verify_duplicated_index(
            cursor, duplicated_row, "test_table", dry_run=False
        )
        
        # Assert
        assert is_verified is True
        assert "SELECT" in query
        assert "WHERE" in query
        
        conn.close()

    def test_delete_entry(self, db_with_duplicates):
        """Test deleting a single entry."""
        # Setup
        conn = sqlite3.connect(db_with_duplicates)
        cursor = conn.cursor()
        
        duplicated_row = pd.Series({"name": "Alice", "value": 100.0})
        
        # Get initial count
        cursor.execute("SELECT COUNT(*) FROM test_table WHERE name='Alice' AND value=100.0")
        initial_count = cursor.fetchone()[0]
        
        # Act - delete one entry
        _delete_entry(cursor, duplicated_row, "test_table", dry_run=False)
        conn.commit()
        
        # Assert
        cursor.execute("SELECT COUNT(*) FROM test_table WHERE name='Alice' AND value=100.0")
        final_count = cursor.fetchone()[0]
        
        assert final_count == initial_count - 1
        
        conn.close()

    def test_delete_duplicates_with_chunks(self, db_path):
        """Test deleting duplicates with chunked processing."""
        # Create larger dataset
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        """)
        
        # Insert many rows with duplicates
        data = []
        for i in range(100):
            # Create pattern with duplicates
            name = f"Person_{i % 20}"  # Will create duplicates
            value = float(i % 10)  # Will create more duplicates
            data.append((i, name, value))
        
        cursor.executemany("INSERT INTO test_table VALUES (?, ?, ?)", data)
        conn.commit()
        conn.close()
        
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_path,
            "test_table",
            columns=["name", "value"],
            chunk_size=10,  # Small chunk size for testing
            dry_run=False
        )
        
        # Assert
        assert total_processed >= 100
        assert total_duplicates > 0
        
        # Verify unique entries
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT name || value) FROM test_table")
        unique_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM test_table")
        total_count = cursor.fetchone()[0]
        conn.close()
        
        assert total_count == unique_count  # All remaining should be unique

    def test_delete_duplicates_error_handling(self, temp_dir):
        """Test error handling in delete_duplicates."""
        # Test with non-existent database
        result = delete_duplicates(
            os.path.join(temp_dir, "non_existent.db"),
            "test_table",
            dry_run=False
        )
        
        assert result == (None, None)  # Should return None on error

    def test_delete_duplicates_empty_table(self, db_path):
        """Test deleting duplicates from empty table."""
        # Create empty table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_path,
            "test_table",
            dry_run=False
        )
        
        # Assert
        assert total_processed == 0
        assert total_duplicates == 0

    def test_delete_duplicates_no_duplicates(self, db_path):
        """Test deleting duplicates when there are none."""
        # Create table with unique entries
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        """)
        
        # Insert unique data
        data = [
            (1, "Alice", 100.0),
            (2, "Bob", 200.0),
            (3, "Charlie", 300.0),
        ]
        cursor.executemany("INSERT INTO test_table VALUES (?, ?, ?)", data)
        conn.commit()
        conn.close()
        
        # Act
        total_processed, total_duplicates = delete_duplicates(
            db_path,
            "test_table",
            columns=["name", "value"],
            dry_run=False
        )
        
        # Assert
        assert total_duplicates == 0
        
        # Verify no data was lost
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 3  # All original rows should remain


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
