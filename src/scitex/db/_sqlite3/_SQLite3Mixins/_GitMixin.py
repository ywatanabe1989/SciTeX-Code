#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-08 06:55:13 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/db/_sqlite3/_SQLite3Mixins/_GitMixin.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/db/_sqlite3/_SQLite3Mixins/_GitMixin.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import hashlib
import json
import pickle
import time
import zlib
from typing import Any, Dict, List, Optional, Tuple


class _GitMixin:
    """Git-like version control for SQLite databases using diff-based tracking."""

    def git_init(self, force: bool = False) -> None:
        """Initialize version control tables.

        Parameters
        ----------
        force : bool
            If True, reinitialize even if tables exist
        """
        if force:
            self.execute("DROP TABLE IF EXISTS _git_commits")
            self.execute("DROP TABLE IF EXISTS _git_refs")
            self.execute("DROP TABLE IF EXISTS _git_changes")

        # Store commit metadata
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS _git_commits (
                hash TEXT PRIMARY KEY,
                parent_hash TEXT,
                message TEXT,
                author TEXT,
                timestamp REAL,
                tree_hash TEXT
            )
        """
        )

        # Store references (branches, HEAD)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS _git_refs (
                name TEXT PRIMARY KEY,
                commit_hash TEXT,
                type TEXT  -- 'branch', 'tag', 'HEAD'
            )
        """
        )

        # Store actual changes per commit
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS _git_changes (
                commit_hash TEXT,
                table_name TEXT,
                operation TEXT,  -- INSERT, UPDATE, DELETE
                row_id INTEGER,
                old_data BLOB,
                new_data BLOB,
                PRIMARY KEY (commit_hash, table_name, operation, row_id)
            )
        """
        )

        # Initialize HEAD if not exists
        if not self.execute(
            "SELECT 1 FROM _git_refs WHERE name='HEAD'"
        ).fetchone():
            self.execute("INSERT INTO _git_refs VALUES ('HEAD', NULL, 'HEAD')")
            self.execute(
                "INSERT INTO _git_refs VALUES ('main', NULL, 'branch')"
            )

    def git_commit(self, message: str = "", author: str = "unknown") -> str:
        """Create a new commit with current database state.

        Parameters
        ----------
        message : str
            Commit message
        author : str
            Author name

        Returns
        -------
        str
            Commit hash (first 8 characters)
        """
        # Get current HEAD
        parent_hash = self._git_get_head()

        # Calculate changes since parent
        changes = self._git_calculate_changes(parent_hash)

        if not changes and parent_hash:
            print("No changes to commit")
            return parent_hash

        # Generate commit hash
        tree_hash = self._git_calculate_tree_hash(changes)
        commit_data = (
            f"{parent_hash}:{message}:{author}:{time.time()}:{tree_hash}"
        )
        commit_hash = hashlib.sha256(commit_data.encode()).hexdigest()[:8]

        # Store commit
        self.execute(
            """
            INSERT INTO _git_commits VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                commit_hash,
                parent_hash,
                message,
                author,
                time.time(),
                tree_hash,
            ),
        )

        # Store changes
        for change in changes:
            self.execute(
                """
                INSERT INTO _git_changes VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    commit_hash,
                    change["table"],
                    change["operation"],
                    change["row_id"],
                    change["old_data"],
                    change["new_data"],
                ),
            )

        # Update HEAD and current branch
        current_branch = self._git_get_current_branch()
        self.execute(
            "UPDATE _git_refs SET commit_hash = ? WHERE name = 'HEAD'",
            (commit_hash,),
        )
        if current_branch:
            self.execute(
                "UPDATE _git_refs SET commit_hash = ? WHERE name = ?",
                (commit_hash, current_branch),
            )

        self.commit()  # SQL commit
        return commit_hash

    def git_checkout(self, ref: str) -> None:
        """Switch to a different commit or branch.

        Parameters
        ----------
        ref : str
            Commit hash or branch name
        """
        # Resolve ref to commit hash
        target_hash = self._git_resolve_ref(ref)
        if not target_hash:
            raise ValueError(f"Reference '{ref}' not found")

        current_hash = self._git_get_head()

        if target_hash == current_hash:
            return  # Already there

        # Find path between commits
        path = self._git_find_path(current_hash, target_hash)

        # Apply changes along path
        for i in range(len(path) - 1):
            from_commit = path[i]
            to_commit = path[i + 1]

            if self._git_is_ancestor(from_commit, to_commit):
                # Moving forward - apply changes
                self._git_apply_changes(to_commit, reverse=False)
            else:
                # Moving backward - reverse changes
                self._git_apply_changes(from_commit, reverse=True)

        # Update HEAD
        self.execute(
            "UPDATE _git_refs SET commit_hash = ? WHERE name = 'HEAD'",
            (target_hash,),
        )

        # If ref is a branch, update current branch tracking
        if self.execute(
            "SELECT 1 FROM _git_refs WHERE name = ? AND type = 'branch'",
            (ref,),
        ).fetchone():
            self.execute(
                "UPDATE _git_refs SET commit_hash = ? WHERE name = ?",
                (target_hash, ref),
            )

        self.commit()  # SQL commit

    def git_branch(
        self, name: Optional[str] = None, delete: bool = False
    ) -> List[Tuple[str, str]]:
        """Create, list, or delete branches.

        Parameters
        ----------
        name : str, optional
            Branch name to create
        delete : bool
            If True, delete the branch

        Returns
        -------
        list
            List of (branch_name, commit_hash) tuples if listing
        """
        if delete and name:
            self.execute(
                "DELETE FROM _git_refs WHERE name = ? AND type = 'branch'",
                (name,),
            )
            return []
        elif name:
            # Create new branch at current commit
            current_hash = self._git_get_head()
            self.execute(
                "INSERT OR REPLACE INTO _git_refs VALUES (?, ?, 'branch')",
                (name, current_hash),
            )
            return []
        else:
            # List branches
            return self.execute(
                """
                SELECT name, commit_hash
                FROM _git_refs
                WHERE type = 'branch'
                ORDER BY name
            """
            ).fetchall()

    def git_log(
        self, limit: int = 10, oneline: bool = False
    ) -> List[Dict[str, Any]]:
        """Show commit history.

        Parameters
        ----------
        limit : int
            Maximum number of commits to show
        oneline : bool
            If True, return condensed format

        Returns
        -------
        list
            List of commit information dictionaries
        """
        current = self._git_get_head()
        history = []
        visited = set()

        while current and len(history) < limit:
            if current in visited:
                break
            visited.add(current)

            commit_info = self.execute(
                """
                SELECT hash, parent_hash, message, author, timestamp
                FROM _git_commits
                WHERE hash = ?
            """,
                (current,),
            ).fetchone()

            if commit_info:
                if oneline:
                    history.append(
                        {
                            "hash": commit_info[0],
                            "message": commit_info[2][:50],
                        }
                    )
                else:
                    history.append(
                        {
                            "hash": commit_info[0],
                            "parent": commit_info[1],
                            "message": commit_info[2],
                            "author": commit_info[3],
                            "date": time.strftime(
                                "%Y-%m-%d %H:%M:%S",
                                time.localtime(commit_info[4]),
                            ),
                        }
                    )
                current = commit_info[1]  # Move to parent
            else:
                break

        return history

    def git_diff(
        self, from_ref: Optional[str] = None, to_ref: Optional[str] = None
    ) -> Dict[str, List]:
        """Show differences between commits.

        Parameters
        ----------
        from_ref : str, optional
            Starting commit (default: parent of HEAD)
        to_ref : str, optional
            Ending commit (default: HEAD)

        Returns
        -------
        dict
            Dictionary of changes by table
        """
        if not to_ref:
            to_ref = self._git_get_head()
        if not from_ref:
            # Get parent of to_ref
            parent = self.execute(
                "SELECT parent_hash FROM _git_commits WHERE hash = ?",
                (to_ref,),
            ).fetchone()
            from_ref = parent[0] if parent else None

        if not from_ref:
            # No parent, show all changes in to_ref
            changes = self.execute(
                """
                SELECT table_name, operation, row_id, old_data, new_data
                FROM _git_changes
                WHERE commit_hash = ?
            """,
                (to_ref,),
            ).fetchall()
        else:
            # This is simplified - real implementation would compute actual diff
            changes = self.execute(
                """
                SELECT table_name, operation, row_id, old_data, new_data
                FROM _git_changes
                WHERE commit_hash = ?
            """,
                (to_ref,),
            ).fetchall()

        # Group by table
        diff = {}
        for table, op, row_id, old_data, new_data in changes:
            if table not in diff:
                diff[table] = []
            diff[table].append(
                {
                    "operation": op,
                    "row_id": row_id,
                    "old": pickle.loads(old_data) if old_data else None,
                    "new": pickle.loads(new_data) if new_data else None,
                }
            )

        return diff

    def git_status(self) -> Dict[str, Any]:
        """Show working tree status.

        Returns
        -------
        dict
            Status information including current branch and uncommitted changes
        """
        current_branch = self._git_get_current_branch()
        current_commit = self._git_get_head()
        uncommitted = self._git_calculate_changes(current_commit)

        return {
            "branch": current_branch or "detached HEAD",
            "commit": current_commit,
            "uncommitted_changes": len(uncommitted),
            "changes_summary": self._summarize_changes(uncommitted),
        }

    def git_reset(self, ref: str, mode: str = "mixed") -> None:
        """Reset current HEAD to specified state.

        Parameters
        ----------
        ref : str
            Target commit
        mode : str
            'soft' (move HEAD only), 'mixed' (move HEAD + index),
            'hard' (move HEAD + working tree)
        """
        target_hash = self._git_resolve_ref(ref)

        if mode == "soft":
            # Just move HEAD
            self.execute(
                "UPDATE _git_refs SET commit_hash = ? WHERE name = 'HEAD'",
                (target_hash,),
            )
        elif mode == "hard":
            # Move HEAD and restore working tree
            self.git_checkout(ref)
        # 'mixed' would update index if we had one

    # Private helper methods

    def _git_get_head(self) -> Optional[str]:
        """Get current HEAD commit hash."""
        result = self.execute(
            "SELECT commit_hash FROM _git_refs WHERE name = 'HEAD'"
        ).fetchone()
        return result[0] if result else None

    def _git_get_current_branch(self) -> Optional[str]:
        """Get current branch name."""
        head = self._git_get_head()
        if not head:
            return None

        result = self.execute(
            """
            SELECT name FROM _git_refs
            WHERE commit_hash = ? AND type = 'branch'
            LIMIT 1
        """,
            (head,),
        ).fetchone()
        return result[0] if result else None

    def _git_resolve_ref(self, ref: str) -> Optional[str]:
        """Resolve a reference to a commit hash."""
        # Check if it's already a commit hash
        if self.execute(
            "SELECT 1 FROM _git_commits WHERE hash = ?", (ref,)
        ).fetchone():
            return ref

        # Check if it's a branch or tag
        result = self.execute(
            "SELECT commit_hash FROM _git_refs WHERE name = ?", (ref,)
        ).fetchone()
        return result[0] if result else None

    def _git_calculate_changes(
        self, since_commit: Optional[str]
    ) -> List[Dict]:
        """Calculate changes since a commit."""
        changes = []

        # Get all tracked tables (exclude git tables)
        tables = [
            t for t in self.get_table_names() if not t.startswith("_git_")
        ]

        for table in tables:
            # This is simplified - real implementation would track actual changes
            # For now, we'll snapshot current state
            current_data = self.execute(
                f"SELECT rowid, * FROM {table}"
            ).fetchall()

            for row in current_data[:10]:  # Limit for demo
                changes.append(
                    {
                        "table": table,
                        "operation": "UPDATE",  # Simplified
                        "row_id": row[0],
                        "old_data": None,  # Would need to track this
                        "new_data": pickle.dumps(row[1:]),
                    }
                )

        return changes

    def _git_calculate_tree_hash(self, changes: List[Dict]) -> str:
        """Calculate hash of current tree state."""
        tree_data = json.dumps(changes, sort_keys=True, default=str)
        return hashlib.sha256(tree_data.encode()).hexdigest()[:8]

    def _git_find_path(
        self, from_hash: Optional[str], to_hash: str
    ) -> List[str]:
        """Find path between two commits."""
        if not from_hash:
            return [to_hash]

        # Build commit graph
        commits = {}
        for hash, parent in self.execute(
            "SELECT hash, parent_hash FROM _git_commits"
        ):
            commits[hash] = parent

        # Find common ancestor and build path
        # Simplified - just return direct path
        return [from_hash, to_hash]

    def _git_is_ancestor(self, commit1: str, commit2: str) -> bool:
        """Check if commit1 is an ancestor of commit2."""
        current = commit2
        while current:
            if current == commit1:
                return True
            result = self.execute(
                "SELECT parent_hash FROM _git_commits WHERE hash = ?",
                (current,),
            ).fetchone()
            current = result[0] if result else None
        return False

    def _git_apply_changes(
        self, commit_hash: str, reverse: bool = False
    ) -> None:
        """Apply or reverse changes from a commit."""
        changes = self.execute(
            """
            SELECT table_name, operation, row_id, old_data, new_data
            FROM _git_changes
            WHERE commit_hash = ?
        """,
            (commit_hash,),
        ).fetchall()

        for table, op, row_id, old_data, new_data in changes:
            if reverse:
                # Reverse the operation
                if op == "INSERT":
                    self.execute(
                        f"DELETE FROM {table} WHERE rowid = ?", (row_id,)
                    )
                elif op == "DELETE" and old_data:
                    # Re-insert deleted data
                    data = pickle.loads(old_data)
                    placeholders = ",".join(["?" for _ in data])
                    self.execute(
                        f"INSERT INTO {table} VALUES ({placeholders})", data
                    )
                elif op == "UPDATE" and old_data:
                    # Restore old data
                    data = pickle.loads(old_data)
                    # Simplified - would need proper column mapping
            else:
                # Apply forward changes
                if op == "INSERT" and new_data:
                    data = pickle.loads(new_data)
                    placeholders = ",".join(["?" for _ in data])
                    self.execute(
                        f"INSERT INTO {table} VALUES ({placeholders})", data
                    )
                elif op == "DELETE":
                    self.execute(
                        f"DELETE FROM {table} WHERE rowid = ?", (row_id,)
                    )
                # UPDATE handling would go here

    def _summarize_changes(self, changes: List[Dict]) -> Dict[str, int]:
        """Summarize changes by operation type."""
        summary = {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
        for change in changes:
            summary[change["operation"]] += 1
        return summary

# EOF
