#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:39:32 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_get_module_path.py


def get_data_path_from_a_package(package_str, resource):
    """
    Get the path to a data file within a package.

    This function finds the path to a data file within a package's data directory.

    Parameters:
    -----------
    package_str : str
        The name of the package as a string.
    resource : str
        The name of the resource file within the package's data directory.

    Returns:
    --------
    str
        The full path to the resource file.

    Raises:
    -------
    ImportError
        If the specified package cannot be found.
    FileNotFoundError
        If the resource file does not exist in the package's data directory.
    """
    import importlib
    import os
    import sys

    spec = importlib.util.find_spec(package_str)
    if spec is None:
        raise ImportError(f"Package '{package_str}' not found")

    data_dir = os.path.join(spec.origin.split("src")[0], "data")
    resource_path = os.path.join(data_dir, resource)

    if not os.path.exists(resource_path):
        raise FileNotFoundError(
            f"Resource '{resource}' not found in package '{package_str}'"
        )

    return resource_path


# EOF
