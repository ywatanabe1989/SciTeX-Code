#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-10 08:05:21 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_check_health.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import sqlite3
from typing import Any, Dict, List

import pandas as pd


def check_health(
    db_path: str, verbose: bool = True, fix_issues: bool = False
) -> Dict[str, Any]:
    """Comprehensive health check for SQLite database

    Parameters
    ----------
    db_path : str
        Path to database file
    verbose : bool, default True
        Print detailed results
    fix_issues : bool, default False
        Attempt to fix detected issues

    Returns
    -------
    dict
        Health check results
    """
    results = {
        "database_path": db_path,
        "exists": False,
        "accessible": False,
        "integrity": "UNKNOWN",
        "tables": [],
        "issues": [],
        "stats": {},
        "recommendations": [],
        "loadability": {"rows": False, "arrays": False, "blobs": False},
    }

    # Check file existence
    if not os.path.exists(db_path):
        results["issues"].append(f"Database file does not exist: {db_path}")
        return results

    results["exists"] = True
    results["stats"]["file_size_mb"] = os.path.getsize(db_path) / (1024 * 1024)

    try:
        with sqlite3.connect(db_path, timeout=10.0) as conn:
            cursor = conn.cursor()
            results["accessible"] = True

            # Integrity check
            integrity_result = cursor.execute(
                "PRAGMA integrity_check"
            ).fetchall()
            results["integrity"] = (
                "OK" if integrity_result[0][0] == "ok" else "CORRUPTED"
            )

            if results["integrity"] == "CORRUPTED":
                results["issues"].append("Database integrity check failed")
                results["recommendations"].append(
                    "Run VACUUM or restore from backup"
                )

            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in cursor.fetchall()]
            results["stats"]["table_count"] = len(table_names)

            total_rows = 0
            for table_name in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                results["tables"].append(
                    {"name": table_name, "row_count": row_count}
                )

            results["stats"]["total_rows"] = total_rows

            # Check for empty tables
            empty_tables = [
                t for t in results["tables"] if t["row_count"] == 0
            ]
            if empty_tables:
                results["issues"].append(
                    f"{len(empty_tables)} empty tables found"
                )

            # Check database settings
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            results["stats"]["journal_mode"] = journal_mode

            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            results["stats"]["page_size"] = page_size

            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            results["stats"]["page_count"] = page_count

            # Check for foreign key violations
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            if fk_violations:
                results["issues"].append(
                    f"{len(fk_violations)} foreign key violations"
                )
                results["recommendations"].append(
                    "Fix foreign key constraints"
                )

            # Performance recommendations
            if results["stats"]["total_rows"] > 10000:
                cursor.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='index'"
                )
                index_count = cursor.fetchone()[0]
                if index_count < len(table_names):
                    results["recommendations"].append(
                        "Consider adding indexes for better performance"
                    )

            # Auto-vacuum check
            cursor.execute("PRAGMA auto_vacuum")
            auto_vacuum = cursor.fetchone()[0]
            if auto_vacuum == 0 and results["stats"]["file_size_mb"] > 100:
                results["recommendations"].append(
                    "Consider enabling auto_vacuum for large databases"
                )

            # Attempt fixes if requested
            if fix_issues and results["issues"]:
                if "CORRUPTED" in str(results["issues"]):
                    if verbose:
                        print("Attempting to fix corruption with VACUUM...")
                    try:
                        cursor.execute("VACUUM")
                        conn.commit()
                        results["recommendations"].append(
                            "Database vacuumed successfully"
                        )
                    except sqlite3.Error as ee:
                        results["issues"].append(f"VACUUM failed: {ee}")

    except sqlite3.Error as ee:
        results["issues"].append(f"Database connection failed: {ee}")
    except Exception as ee:
        results["issues"].append(f"Unexpected error: {ee}")

    # Test loadability
    results["loadability"]["rows"] = is_rows_loadable(db_path, verbose=verbose)
    results["loadability"]["arrays"] = is_arrays_loadable(
        db_path, verbose=verbose
    )
    results["loadability"]["blobs"] = is_blobs_loadable(
        db_path, verbose=verbose
    )

    # Add loadability issues
    if not results["loadability"]["rows"]:
        results["issues"].append("Rows are not loadable")
    if not results["loadability"]["arrays"]:
        results["issues"].append("Arrays are not loadable")
    if not results["loadability"]["blobs"]:
        results["issues"].append("Blobs are not loadable")

    # Generate summary
    health_score = 100
    health_score -= len(results["issues"]) * 20
    health_score = max(0, health_score)

    results["health_score"] = health_score
    results["status"] = (
        "HEALTHY"
        if health_score >= 80
        else "ISSUES_FOUND" if health_score >= 50 else "CRITICAL"
    )

    if verbose:
        print(f"\nDatabase Health Check: {db_path}")
        print(f"Status: {results['status']} (Score: {health_score}/100)")
        print(f"File size: {results['stats'].get('file_size_mb', 0):.2f} MB")
        print(f"Tables: {results['stats'].get('table_count', 0)}")
        print(f"Total rows: {results['stats'].get('total_rows', 0)}")

        # Loadability status
        loadability = results["loadability"]
        print(
            f"Loadability - Rows: {'✓' if loadability['rows'] else '✗'}, "
            f"Arrays: {'✓' if loadability['arrays'] else '✗'}, "
            f"Blobs: {'✓' if loadability['blobs'] else '✗'}"
        )

        if results["issues"]:
            print(f"\nIssues found ({len(results['issues'])}):")
            for issue in results["issues"]:
                print(f"  - {issue}")

        if results["recommendations"]:
            print(f"\nRecommendations ({len(results['recommendations'])}):")
            for rec in results["recommendations"]:
                print(f"  - {rec}")

    return results


def is_rows_loadable(
    db_path: str, table_name: str = None, verbose: bool = False
) -> bool:
    """Check if database/table is loadable without errors

    Parameters
    ----------
    db_path : str
        Path to database file
    table_name : str, optional
        Specific table to test. If None, tests all tables
    verbose : bool, default False
        Print detailed error information

    Returns
    -------
    bool
        True if loadable, False otherwise
    """
    import scitex as stx

    try:
        with stx.io.load(db_path) as db:
            if table_name:
                db.get_rows(table_name, limit=1)
                return True
            else:
                table_names = db.get_table_names()
                for tname in table_names:
                    db.get_rows(tname, limit=1)
                return True
    except Exception as ee:
        if verbose:
            print(f"Load failed for {db_path}/{table_name}: {ee}")
        return False


def is_arrays_loadable(
    db_path: str, table_name: str = None, verbose: bool = False
) -> bool:
    """Check if arrays in database/table are loadable

    Parameters
    ----------
    db_path : str
        Path to database file
    table_name : str, optional
        Specific table to test. If None, tests all tables
    verbose : bool, default False
        Print detailed error information

    Returns
    -------
    bool
        True if arrays loadable, False otherwise
    """
    import scitex as stx

    try:
        with stx.io.load(db_path) as db:
            if table_name:
                db.load_arrays(table_name)
                return True
            else:
                table_names = db.get_table_names()
                for tname in table_names:
                    try:
                        db.load_arrays(tname)
                    except:
                        continue
                return True
    except Exception as ee:
        if verbose:
            print(f"Array load failed for {db_path}/{table_name}: {ee}")
        return False


def is_blobs_loadable(
    db_path: str, table_name: str = None, verbose: bool = False
) -> bool:
    """Check if blobs in database/table are loadable

    Parameters
    ----------
    db_path : str
        Path to database file
    table_name : str, optional
        Specific table to test. If None, tests all tables
    verbose : bool, default False
        Print detailed error information

    Returns
    -------
    bool
        True if blobs loadable, False otherwise
    """
    import scitex as stx

    try:
        with stx.io.load(db_path) as db:
            if table_name:
                db.load_blob(table_name)
                return True
            else:
                table_names = db.get_table_names()
                for tname in table_names:
                    try:
                        db.load_blob(tname)
                    except:
                        continue
                return True
    except Exception as ee:
        if verbose:
            print(f"Blob load failed for {db_path}/{table_name}: {ee}")
        return False


def batch_health_check(
    db_paths: List[str], verbose: bool = False, fix_issues: bool = False
) -> Dict[str, Dict[str, Any]]:
    """
    Run health check on multiple databases

    Parameters
    ----------
    db_paths : list of str
        List of database paths
    verbose : bool, default False
        Print results for each database
    fix_issues : bool, default False
        Attempt to fix issues

    Returns
    -------
    dict
        Results for each database
    """
    results = {}

    print(f"Running health check on {len(db_paths)} databases...")

    for db_path in db_paths:
        if verbose:
            print(f"\nChecking: {db_path}")

        results[db_path] = check_health(
            db_path=db_path, verbose=verbose, fix_issues=fix_issues
        )

    # Summary
    healthy = sum(1 for r in results.values() if r["status"] == "HEALTHY")
    issues = sum(1 for r in results.values() if r["status"] == "ISSUES_FOUND")
    critical = sum(1 for r in results.values() if r["status"] == "CRITICAL")

    print(f"\nBatch Health Check Summary:")
    print(f"  Healthy: {healthy}")
    print(f"  Issues: {issues}")
    print(f"  Critical: {critical}")

    return results

# EOF
