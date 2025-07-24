#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-01 10:55:00 (ywatanabe)"
# File: tests/scitex/db/_PostgreSQLMixins/test__ImportExportMixin.py

"""
Comprehensive tests for PostgreSQL ImportExportMixin.
Testing PostgreSQL-specific COPY operations for efficient data import/export.
"""

import pytest
import psycopg2
from unittest.mock import MagicMock, patch, mock_open, call
from scitex.db._PostgreSQLMixins import _ImportExportMixin


class TestPostgreSQLImportExportMixin:
    """Test suite for PostgreSQL ImportExportMixin."""

    @pytest.fixture
    def mixin(self):
        """Create ImportExportMixin instance with mocked methods."""
        mixin = _ImportExportMixin()
        mixin.execute = MagicMock()
        mixin.cursor = MagicMock()
        mixin.transaction = MagicMock()
        mixin.transaction().__enter__ = MagicMock()
        mixin.transaction().__exit__ = MagicMock()
        return mixin

    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content for testing."""
        return """id,name,age,email
1,John Doe,30,john@example.com
2,Jane Smith,25,jane@example.com
3,Bob Johnson,35,bob@example.com
"""

    def test_load_from_csv_append(self, mixin, sample_csv_content):
        """Test loading CSV with append mode."""
        csv_path = "/tmp/test_data.csv"
        
        with patch("builtins.open", mock_open(read_data=sample_csv_content)):
            mixin.load_from_csv("users", csv_path, if_exists="append")
        
        # Should not truncate table
        assert not any("TRUNCATE" in str(call) for call in mixin.execute.call_args_list)
        
        # Verify COPY command
        expected_sql = "COPY users FROM STDIN WITH CSV HEADER"
        mixin.cursor.copy_expert.assert_called_once()
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql

    def test_load_from_csv_replace(self, mixin, sample_csv_content):
        """Test loading CSV with replace mode."""
        csv_path = "/tmp/test_data.csv"
        
        with patch("builtins.open", mock_open(read_data=sample_csv_content)):
            mixin.load_from_csv("users", csv_path, if_exists="replace")
        
        # Should truncate table first
        mixin.execute.assert_called_once_with("TRUNCATE TABLE users")
        
        # Verify COPY command
        expected_sql = "COPY users FROM STDIN WITH CSV HEADER"
        mixin.cursor.copy_expert.assert_called_once()
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql

    def test_load_from_csv_file_handling(self, mixin, sample_csv_content):
        """Test proper file handling in load_from_csv."""
        csv_path = "/tmp/test_data.csv"
        mock_file = mock_open(read_data=sample_csv_content)
        
        with patch("builtins.open", mock_file):
            mixin.load_from_csv("users", csv_path)
        
        # Verify file was opened in read mode
        mock_file.assert_called_once_with(csv_path, "r")
        
        # Verify file handle was passed to copy_expert
        file_handle = mixin.cursor.copy_expert.call_args[1]['file']
        assert file_handle == mock_file.return_value

    def test_load_from_csv_error_handling(self, mixin):
        """Test error handling in load_from_csv."""
        csv_path = "/tmp/test_data.csv"
        
        # Simulate psycopg2 error
        mixin.cursor.copy_expert.side_effect = psycopg2.Error("Copy failed")
        
        with patch("builtins.open", mock_open()):
            with pytest.raises(ValueError, match="Failed to import from CSV"):
                mixin.load_from_csv("users", csv_path)

    def test_load_from_csv_transaction_context(self, mixin):
        """Test that load_from_csv uses transaction context."""
        csv_path = "/tmp/test_data.csv"
        
        with patch("builtins.open", mock_open()):
            mixin.load_from_csv("users", csv_path)
        
        # Verify transaction was used
        mixin.transaction.assert_called_once()
        mixin.transaction().__enter__.assert_called_once()
        mixin.transaction().__exit__.assert_called_once()

    def test_save_to_csv_all_columns(self, mixin):
        """Test saving all columns to CSV."""
        output_path = "/tmp/output.csv"
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            mixin.save_to_csv("users", output_path)
        
        # Verify COPY command with all columns
        expected_sql = "COPY (SELECT * FROM users) TO STDOUT WITH CSV HEADER"
        mixin.cursor.copy_expert.assert_called_once()
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql
        
        # Verify file was opened in write mode
        mock_file.assert_called_once_with(output_path, "w")

    def test_save_to_csv_specific_columns(self, mixin):
        """Test saving specific columns to CSV."""
        output_path = "/tmp/output.csv"
        columns = ["id", "name", "email"]
        
        with patch("builtins.open", mock_open()):
            mixin.save_to_csv("users", output_path, columns=columns)
        
        # Verify COPY command with specific columns
        expected_sql = "COPY (SELECT id, name, email FROM users) TO STDOUT WITH CSV HEADER"
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql

    def test_save_to_csv_with_where_clause(self, mixin):
        """Test saving to CSV with WHERE clause."""
        output_path = "/tmp/active_users.csv"
        
        with patch("builtins.open", mock_open()):
            mixin.save_to_csv("users", output_path, where="active = true")
        
        # Verify COPY command includes WHERE clause
        expected_sql = "COPY (SELECT * FROM users WHERE active = true) TO STDOUT WITH CSV HEADER"
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql

    def test_save_to_csv_with_columns_and_where(self, mixin):
        """Test saving specific columns with WHERE clause."""
        output_path = "/tmp/filtered.csv"
        columns = ["id", "name"]
        where = "age > 25"
        
        with patch("builtins.open", mock_open()):
            mixin.save_to_csv("users", output_path, columns=columns, where=where)
        
        # Verify combined query
        expected_sql = "COPY (SELECT id, name FROM users WHERE age > 25) TO STDOUT WITH CSV HEADER"
        actual_sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert actual_sql == expected_sql

    def test_save_to_csv_file_handling(self, mixin):
        """Test proper file handling in save_to_csv."""
        output_path = "/tmp/output.csv"
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            mixin.save_to_csv("users", output_path)
        
        # Verify file handle was passed to copy_expert
        file_handle = mixin.cursor.copy_expert.call_args[1]['file']
        assert file_handle == mock_file.return_value

    def test_save_to_csv_error_handling(self, mixin):
        """Test error handling in save_to_csv."""
        output_path = "/tmp/output.csv"
        
        # Simulate psycopg2 error
        mixin.cursor.copy_expert.side_effect = psycopg2.Error("Export failed")
        
        with patch("builtins.open", mock_open()):
            with pytest.raises(ValueError, match="Failed to export to CSV"):
                mixin.save_to_csv("users", output_path)

    def test_postgresql_copy_features(self, mixin):
        """Test PostgreSQL-specific COPY features."""
        # Test that COPY commands use PostgreSQL syntax
        csv_path = "/tmp/data.csv"
        
        with patch("builtins.open", mock_open()):
            mixin.load_from_csv("test_table", csv_path)
            
        # Check for PostgreSQL-specific keywords
        sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert "COPY" in sql
        assert "FROM STDIN" in sql
        assert "WITH CSV HEADER" in sql

    def test_batch_size_parameter(self, mixin):
        """Test batch_size parameter is accepted (though not used in COPY)."""
        csv_path = "/tmp/data.csv"
        
        with patch("builtins.open", mock_open()):
            # Should not raise error with batch_size
            mixin.load_from_csv("users", csv_path, batch_size=5000)
            mixin.save_to_csv("users", "/tmp/out.csv", batch_size=5000)
        
        # Verify methods were called successfully
        assert mixin.cursor.copy_expert.call_count == 2

    def test_chunk_size_parameter(self, mixin):
        """Test chunk_size parameter is accepted for load_from_csv."""
        csv_path = "/tmp/data.csv"
        
        with patch("builtins.open", mock_open()):
            # Should not raise error with chunk_size
            mixin.load_from_csv("users", csv_path, chunk_size=50000)
        
        # Verify method was called successfully
        assert mixin.cursor.copy_expert.called

    def test_multiple_operations(self, mixin):
        """Test multiple import/export operations."""
        with patch("builtins.open", mock_open()):
            # Load data
            mixin.load_from_csv("table1", "/tmp/data1.csv")
            mixin.load_from_csv("table2", "/tmp/data2.csv", if_exists="replace")
            
            # Save data
            mixin.save_to_csv("table1", "/tmp/out1.csv")
            mixin.save_to_csv("table2", "/tmp/out2.csv", columns=["id", "name"])
        
        # Verify all operations were performed
        assert mixin.cursor.copy_expert.call_count == 4
        assert mixin.execute.call_count == 1  # Only for TRUNCATE

    def test_special_characters_in_table_name(self, mixin):
        """Test handling of special characters in table names."""
        # Note: In real usage, table names should be properly escaped
        table_name = "user_data_2024"
        
        with patch("builtins.open", mock_open()):
            mixin.save_to_csv(table_name, "/tmp/out.csv")
        
        sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert table_name in sql

    def test_empty_columns_list(self, mixin):
        """Test behavior with empty columns list."""
        with patch("builtins.open", mock_open()):
            # Empty list should be treated differently than ["*"]
            mixin.save_to_csv("users", "/tmp/out.csv", columns=[])
        
        # Should still create valid SQL
        sql = mixin.cursor.copy_expert.call_args[1]['sql']
        assert "COPY (SELECT" in sql
        assert "FROM users)" in sql


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_ImportExportMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-02-27 22:14:59 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_ImportExportMixin.py
# 
# THIS_FILE = (
#     "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_ImportExportMixin.py"
# )
# 
# import pandas as pd
# from typing import List
# import psycopg2
# from io import StringIO
# 
# 
# class _ImportExportMixin:
#     def load_from_csv(
#         self,
#         table_name: str,
#         csv_path: str,
#         if_exists: str = "append",
#         batch_size: int = 10_000,
#         chunk_size: int = 100_000,
#     ) -> None:
#         with self.transaction():
#             try:
#                 if if_exists == "replace":
#                     self.execute(f"TRUNCATE TABLE {table_name}")
# 
#                 copy_sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
#                 with open(csv_path, "r") as f:
#                     self.cursor.copy_expert(sql=copy_sql, file=f)
# 
#             except (Exception, psycopg2.Error) as err:
#                 raise ValueError(f"Failed to import from CSV: {err}")
# 
#     def save_to_csv(
#         self,
#         table_name: str,
#         output_path: str,
#         columns: List[str] = ["*"],
#         where: str = None,
#         batch_size: int = 10_000,
#     ) -> None:
#         try:
#             columns_str = ", ".join(columns) if columns != ["*"] else "*"
#             query = f"COPY (SELECT {columns_str} FROM {table_name}"
#             if where:
#                 query += f" WHERE {where}"
#             query += ") TO STDOUT WITH CSV HEADER"
# 
#             with open(output_path, "w") as f:
#                 self.cursor.copy_expert(sql=query, file=f)
# 
#         except (Exception, psycopg2.Error) as err:
#             raise ValueError(f"Failed to export to CSV: {err}")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/db/_postgresql/_PostgreSQLMixins/_ImportExportMixin.py
# --------------------------------------------------------------------------------
