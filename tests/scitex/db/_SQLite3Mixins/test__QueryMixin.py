#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 14:48:00 (ywatanabe)"
# File: ./tests/scitex/db/_SQLite3Mixins/test__QueryMixin.py

"""
Functionality:
    * Tests query operations for SQLite3
    * Validates SELECT, JOIN, and complex query handling
    * Tests query optimization and caching
Input:
    * Test database and query parameters
Output:
    * Test results
Prerequisites:
    * pytest
    * sqlite3
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch


class TestQueryMixin:
    """Test cases for _QueryMixin"""
    
    def test_select_basic(self):
        """Test basic SELECT query"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test"), (2, "test2")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table")
        assert len(results) == 2
        mixin.execute.assert_called_with("SELECT * FROM test_table", ())
        
    def test_select_with_columns(self):
        """Test SELECT with specific columns"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1,), (2,)]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", columns=["id"])
        assert len(results) == 2
        mixin.execute.assert_called_with("SELECT id FROM test_table", ())
        
    def test_select_with_where(self):
        """Test SELECT with WHERE clause"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", where="id = ?", params=(1,))
        assert len(results) == 1
        mixin.execute.assert_called_with("SELECT * FROM test_table WHERE id = ?", (1,))
        
    def test_select_with_order_by(self):
        """Test SELECT with ORDER BY"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(2, "b"), (1, "a")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", order_by="name DESC")
        mixin.execute.assert_called_with("SELECT * FROM test_table ORDER BY name DESC", ())
        
    def test_select_with_limit(self):
        """Test SELECT with LIMIT"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select("test_table", limit=1)
        mixin.execute.assert_called_with("SELECT * FROM test_table LIMIT 1", ())
        
    def test_join_query(self):
        """Test JOIN queries"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [(1, "test", "data")]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.join(
            "table1", 
            "table2", 
            "table1.id = table2.table1_id",
            join_type="INNER"
        )
        assert len(results) == 1
        assert "INNER JOIN" in mixin.execute.call_args[0][0]
        
    def test_count_rows(self):
        """Test row counting"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (42,)
        mixin.execute = Mock(return_value=mock_cursor)
        
        count = mixin.count("test_table")
        assert count == 42
        mixin.execute.assert_called_with("SELECT COUNT(*) FROM test_table", ())
        
    def test_exists_query(self):
        """Test existence check"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        
        # Record exists
        mock_cursor.fetchone.return_value = (1,)
        mixin.execute = Mock(return_value=mock_cursor)
        assert mixin.exists("test_table", "id = ?", (1,)) is True
        
        # Record doesn't exist
        mock_cursor.fetchone.return_value = None
        assert mixin.exists("test_table", "id = ?", (999,)) is False
        
    def test_aggregate_functions(self):
        """Test aggregate function queries"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        
        # Test SUM
        mock_cursor.fetchone.return_value = (1000,)
        mixin.execute = Mock(return_value=mock_cursor)
        result = mixin.aggregate("test_table", "SUM", "value")
        assert result == 1000
        
        # Test AVG
        mock_cursor.fetchone.return_value = (50.5,)
        result = mixin.aggregate("test_table", "AVG", "value")
        assert result == 50.5
        
    def test_group_by_query(self):
        """Test GROUP BY queries"""
from scitex.db._SQLite3Mixins import _QueryMixin
        
        mixin = _QueryMixin()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("category1", 10),
            ("category2", 20)
        ]
        mixin.execute = Mock(return_value=mock_cursor)
        
        results = mixin.select(
            "test_table",
            columns=["category", "COUNT(*)"],
            group_by="category"
        )
        assert len(results) == 2
        assert "GROUP BY category" in mixin.execute.call_args[0][0]


def main():
    """Run the tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    main()\n\n# --------------------------------------------------------------------------------\n# Start of Source Code from: /home/ywatanabe/proj/_scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-29 04:31:43 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py
#
# THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py"
#
# import sqlite3
# from typing import List, Tuple
#
# import pandas as pd
# from .._BaseMixins._BaseQueryMixin import _BaseQueryMixin
#
# class _QueryMixin:
#     """Query execution functionality"""
#
#     def _sanitize_parameters(self, parameters):
#         """Convert pandas Timestamp objects to strings"""
#         if isinstance(parameters, (list, tuple)):
#             return [str(p) if isinstance(p, pd.Timestamp) else p for p in parameters]
#         return parameters
#
#     def execute(self, query: str, parameters: Tuple = ()) -> None:
#         if not self.cursor:
#             raise ConnectionError("Database not connected")
#
#         if any(keyword in query.upper()
#                for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]):
#             self._check_writable()
#
#         try:
#             parameters = self._sanitize_parameters(parameters)
#             self.cursor.execute(query, parameters)
#             self.conn.commit()
#             return self.cursor
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Query execution failed: {err}")
#
#     def executemany(self, query: str, parameters: List[Tuple]) -> None:
#         if not self.cursor:
#             raise ConnectionError("Database not connected")
#
#         if any(keyword in query.upper()
#                for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"]):
#             self._check_writable()
#
#         try:
#             parameters = [self._sanitize_parameters(p) for p in parameters]
#             self.cursor.executemany(query, parameters)
#             self.conn.commit()
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Batch query execution failed: {err}")
#
#     def executescript(self, script: str) -> None:
#         if not self.cursor:
#             raise ConnectionError("Database not connected")
#
#         if any(
#             keyword in script.upper()
#             for keyword in [
#                 "INSERT",
#                 "UPDATE",
#                 "DELETE",
#                 "DROP",
#                 "CREATE",
#                 "ALTER",
#             ]
#         ):
#             self._check_writable()
#
#         try:
#             self.cursor.executescript(script)
#             self.conn.commit()
#         except sqlite3.Error as err:
#             raise sqlite3.Error(f"Script execution failed: {err}")
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/db/_SQLite3Mixins/_QueryMixin.py
# --------------------------------------------------------------------------------
