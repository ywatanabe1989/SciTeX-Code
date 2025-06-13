#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-02-27 22:15:38 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_dev/src/scitex/db/_PostgreSQLMixins/_TableMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_PostgreSQLMixins/_TableMixin.py"
)

from typing import Any, Dict, List, Union
import psycopg2


class _TableMixin:
    def create_table(
        self,
        table_name: str,
        columns: Dict[str, str],
        foreign_keys: List[Dict[str, str]] = None,
        if_not_exists: bool = True,
    ) -> None:
        try:
            exists_clause = "IF NOT EXISTS" if if_not_exists else ""
            columns_def = [
                f"{col_name} {col_type}" for col_name, col_type in columns.items()
            ]

            if foreign_keys:
                for fk in foreign_keys:
                    columns_def.append(
                        f"FOREIGN KEY ({fk['column']}) REFERENCES {fk['references']}({fk['referenced_column']})"
                    )

            columns_str = ", ".join(columns_def)
            query = f"CREATE TABLE {exists_clause} {table_name} ({columns_str})"
            self.execute(query)

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to create table: {err}")

    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        try:
            exists_clause = "IF EXISTS" if if_exists else ""
            self.execute(f"DROP TABLE {exists_clause} {table_name}")

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to drop table: {err}")

    def rename_table(self, old_name: str, new_name: str) -> None:
        try:
            self.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to rename table: {err}")

    def add_columns(
        self,
        table_name: str,
        columns: Dict[str, str],
        default_values: Dict[str, Any] = None,
    ) -> None:
        try:
            for col_name, col_type in columns.items():
                default_value = default_values.get(col_name) if default_values else None
                default_clause = (
                    f" DEFAULT {default_value}" if default_value is not None else ""
                )

                self.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{default_clause}"
                )

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to add columns: {err}")

    def add_column(
        self,
        table_name: str,
        column_name: str,
        column_type: str,
        default_value: Any = None,
    ) -> None:
        try:
            default_clause = (
                f" DEFAULT {default_value}" if default_value is not None else ""
            )
            self.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{default_clause}"
            )

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to add column: {err}")

    def drop_columns(
        self, table_name: str, columns: Union[str, List[str]], if_exists: bool = True
    ) -> None:
        try:
            if isinstance(columns, str):
                columns = [columns]

            exists_clause = "IF EXISTS" if if_exists else ""
            for column in columns:
                self.execute(
                    f"ALTER TABLE {table_name} DROP COLUMN {exists_clause} {column}"
                )

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to drop columns: {err}")

    def get_table_names(self) -> List[str]:
        try:
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
            self.cursor.execute(query)
            return [row[0] for row in self.cursor.fetchall()]

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to get table names: {err}")

    def get_table_schema(self, table_name: str):
        try:
            query = f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            """
            return self.execute(query).fetchall()

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to get table schema: {err}")

    def get_primary_key(self, table_name: str) -> str:
        try:
            query = f"""
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = '{table_name}'::regclass
            AND    i.indisprimary
            """
            result = self.execute(query).fetchone()
            return result[0] if result else None

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to get primary key: {err}")

    def get_table_stats(self, table_name: str) -> Dict[str, int]:
        try:
            stats = {}
            stats["row_count"] = self.get_row_count(table_name)

            size_query = f"""
            SELECT pg_total_relation_size('{table_name}') as total_size,
                   pg_table_size('{table_name}') as table_size,
                   pg_indexes_size('{table_name}') as index_size
            """
            size_result = self.execute(size_query).fetchone()

            stats.update(
                {
                    "total_size": size_result[0],
                    "table_size": size_result[1],
                    "index_size": size_result[2],
                }
            )
            return stats

        except (Exception, psycopg2.Error) as err:
            raise ValueError(f"Failed to get table stats: {err}")


# EOF
