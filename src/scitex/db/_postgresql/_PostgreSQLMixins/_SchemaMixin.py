#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:14:23 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_SchemaMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_SchemaMixin.py"
)

from typing import List, Dict, Any, Optional
from ..._BaseMixins._BaseSchemaMixin import _BaseSchemaMixin


class _SchemaMixin(_BaseSchemaMixin):
    def get_tables(self) -> List[str]:
        """Get all tables in the current database"""
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        self.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def get_columns(self, table: str) -> List[Dict[str, Any]]:
        """Get detailed information about columns in a table"""
        query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """
        self.execute(query, (table,))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_primary_keys(self, table: str) -> List[str]:
        """Get primary key columns for a table"""
        query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """
        self.execute(query, (table,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_foreign_keys(self, table: str) -> List[Dict[str, Any]]:
        """Get foreign key constraints for a table"""
        query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = %s
        """
        self.execute(query, (table,))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def get_indexes(self, table: str) -> List[Dict[str, Any]]:
        """Get all indexes for a table"""
        query = """
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s
        """
        self.execute(query, (table,))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def table_exists(self, table: str) -> bool:
        """Check if a table exists"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            )
        """
        self.execute(query, (table,))
        return self.cursor.fetchone()[0]

    def column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s
            )
        """
        self.execute(query, (table, column))
        return self.cursor.fetchone()[0]

    def create_index(
        self, table: str, columns: List[str], index_name: Optional[str] = None
    ) -> None:
        """Create an index on specified columns"""
        self._check_writable()
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        self.execute(f"CREATE INDEX {index_name} ON {table} ({columns_str})")

    def drop_index(self, index_name: str) -> None:
        """Drop an index"""
        self._check_writable()
        self.execute(f"DROP INDEX IF EXISTS {index_name}")


# EOF
