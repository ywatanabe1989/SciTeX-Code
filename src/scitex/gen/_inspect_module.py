#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-07 18:58:55 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_inspect_module.py

import inspect
import sys
import warnings
from typing import Any, List, Optional, Set, Union

import scitex
import pandas as pd


def inspect_module(
    module: Union[str, Any],
    columns: List[str] = ["Type", "Name", "Docstring", "Depth"],
    prefix: str = "",
    max_depth: int = 5,
    visited: Optional[Set[str]] = None,
    docstring: bool = False,
    tree: bool = True,
    current_depth: int = 0,
    print_output: bool = False,
    skip_depwarnings: bool = True,
    drop_duplicates: bool = True,
    root_only: bool = False,
) -> pd.DataFrame:
    return _inspect_module(
        module=module,
        prefix=prefix,
        max_depth=max_depth,
        visited=visited,
        docstring=docstring,
        tree=tree,
        current_depth=current_depth,
        print_output=print_output,
        skip_depwarnings=skip_depwarnings,
        drop_duplicates=drop_duplicates,
        root_only=root_only,
    )[columns]


def _inspect_module(
    module: Union[str, Any],
    columns: List[str] = ["Type", "Name", "Docstring", "Depth"],
    prefix: str = "",
    max_depth: int = 5,
    visited: Optional[Set[str]] = None,
    docstring: bool = False,
    tree: bool = True,
    current_depth: int = 0,
    print_output: bool = False,
    skip_depwarnings: bool = True,
    drop_duplicates: bool = True,
    root_only: bool = False,
) -> pd.DataFrame:
    """List the contents of a module recursively and return as a DataFrame.

    Example
    -------
    >>>
    >>> df = inspect_module(scitex)
    >>> print(df)
       Type           Name                    Docstring  Depth
    0    M            scitex  Module description              0
    1    F  scitex.some_function  Function description        1
    2    C  scitex.SomeClass  Class description               1
    ...

    Parameters
    ----------
    module : Union[str, Any]
        Module to inspect (string name or actual module)
    columns : List[str]
        Columns to include in output DataFrame
    prefix : str
        Prefix for nested modules
    max_depth : int
        Maximum recursion depth
    visited : Optional[Set[str]]
        Set of visited modules to prevent cycles
    docstring : bool
        Whether to include docstrings
    tree : bool
        Whether to display tree structure
    current_depth : int
        Current recursion depth
    print_output : bool
        Whether to print results
    skip_depwarnings : bool
        Whether to skip DeprecationWarnings
    drop_duplicates : bool
        Whether to remove duplicate module entries
    root_only : bool
        Whether to show only root-level modules

    Returns
    -------
    pd.DataFrame
        Module structure with specified columns
    """
    if skip_depwarnings:
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

    if isinstance(module, str):
        try:
            module = __import__(module)
        except ImportError as err:
            print(f"Error importing module {module}: {err}")
            return pd.DataFrame(columns=columns)

    if visited is None:
        visited = set()

    content_list = []

    try:
        module_name = getattr(module, "__name__", "")
        if max_depth < 0 or module_name in visited:
            return pd.DataFrame(content_list, columns=columns)

        visited.add(module_name)
        base_name = module_name.split(".")[-1]
        full_path = f"{prefix}.{base_name}" if prefix else base_name

        try:
            module_version = (
                f" (v{module.__version__})" if hasattr(module, "__version__") else ""
            )
            content_list.append(("M", full_path, module_version, current_depth))
        except Exception:
            pass

        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue

            obj_name = f"{full_path}.{name}"

            if inspect.ismodule(obj):
                if obj.__name__ not in visited:
                    content_list.append(
                        (
                            "M",
                            obj_name,
                            obj.__doc__ if docstring and obj.__doc__ else "",
                            current_depth,
                        )
                    )
                    try:
                        sub_df = _inspect_module(
                            obj,
                            columns=columns,
                            prefix=full_path,
                            max_depth=max_depth - 1,
                            visited=visited,
                            docstring=docstring,
                            tree=tree,
                            current_depth=current_depth + 1,
                            print_output=print_output,
                            skip_depwarnings=skip_depwarnings,
                            drop_duplicates=drop_duplicates,
                            root_only=root_only,
                        )
                        if sub_df is not None and not sub_df.empty:
                            content_list.extend(sub_df.values.tolist())
                    except Exception as err:
                        print(f"Error processing module {obj_name}: {err}")
            elif inspect.isfunction(obj):
                content_list.append(
                    (
                        "F",
                        obj_name,
                        obj.__doc__ if docstring and obj.__doc__ else "",
                        current_depth,
                    )
                )
            elif inspect.isclass(obj):
                content_list.append(
                    (
                        "C",
                        obj_name,
                        obj.__doc__ if docstring and obj.__doc__ else "",
                        current_depth,
                    )
                )

    except Exception as err:
        print(f"Error processing module structure: {err}")
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(content_list, columns=columns)

    if drop_duplicates:
        df = df.drop_duplicates(subset="Name", keep="first")

    if root_only:
        mask = df["Name"].str.count(r"\.") <= 1
        df = df[mask]

    if tree and current_depth == 0 and print_output:
        _print_module_contents(df)

    return df[columns]


def _print_module_contents(df: pd.DataFrame) -> None:
    """Prints module contents in tree structure.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing module structure
    """
    df_sorted = df.sort_values(["Depth", "Name"])
    depth_last = {}

    for index, row in df_sorted.iterrows():
        depth = row["Depth"]
        is_last = (
            index == len(df_sorted) - 1 or df_sorted.iloc[index + 1]["Depth"] <= depth
        )

        prefix = ""
        for d in range(depth):
            if d == depth - 1:
                prefix += "└── " if is_last else "├── "
            else:
                prefix += "    " if depth_last.get(d, False) else "│   "

        print(f"{prefix}({row['Type']}) {row['Name']}{row['Docstring']}")
        depth_last[depth] = is_last


if __name__ == "__main__":

    sys.setrecursionlimit(10_000)
    df = inspect_module(scitex, docstring=True, print_output=False, columns=["Name"])
    print(scitex.pd.round(df))
    #                                 Name
    # 0                               scitex
    # 1                            scitex.ai
    # 3     scitex.ai.ClassificationReporter
    # 4           scitex.ai.ClassifierServer
    # 5              scitex.ai.EarlyStopping
    # ...                              ...
    # 5373                     scitex.typing
    # 5375                 scitex.typing.Any
    # 5376            scitex.typing.Iterable
    # 5377                        scitex.web
    # 5379          scitex.web.summarize_url

    # [5361 rows x 1 columns]

# EOF
