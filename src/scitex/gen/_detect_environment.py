#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:20:00 (ywatanabe)"
# File: ./src/scitex/gen/_detect_environment.py

"""
Enhanced environment detection for SciTeX.

Provides better discrimination between:
- Python scripts
- IPython console
- Jupyter notebooks
- Interactive Python
"""

import os
import sys
from typing import Literal, Tuple

__all__ = ['detect_environment', 'get_output_directory']

EnvironmentType = Literal['script', 'jupyter', 'ipython', 'interactive', 'unknown']


def detect_environment() -> EnvironmentType:
    """
    Detect the current execution environment.
    
    Returns
    -------
    EnvironmentType
        One of: 'script', 'jupyter', 'ipython', 'interactive', 'unknown'
        
    Examples
    --------
    >>> env = detect_environment()
    >>> print(f"Running in: {env}")
    Running in: script
    """
    # Check for Jupyter notebook
    if 'ipykernel' in sys.modules:
        try:
            ip = get_ipython()
            if ip and type(ip).__name__ == 'ZMQInteractiveShell':
                return 'jupyter'
        except NameError:
            pass
    
    # Check for IPython console
    try:
        ip = get_ipython()
        if ip and type(ip).__name__ == 'TerminalInteractiveShell':
            return 'ipython'
    except NameError:
        pass
    
    # Check for regular Python script
    if sys.argv and sys.argv[0] and sys.argv[0].endswith('.py'):
        return 'script'
    
    # Check for interactive Python
    if hasattr(sys, 'ps1'):
        return 'interactive'
    
    return 'unknown'


def get_output_directory(specified_path: str, env_type: EnvironmentType = None) -> Tuple[str, bool]:
    """
    Get the appropriate output directory based on environment.
    
    Parameters
    ----------
    specified_path : str
        The path specified by the user
    env_type : EnvironmentType, optional
        Override environment detection
        
    Returns
    -------
    tuple[str, bool]
        (output_directory, should_use_temp)
        
    Examples
    --------
    >>> output_dir, use_temp = get_output_directory("data.csv")
    >>> print(f"Save to: {output_dir}, Temp: {use_temp}")
    Save to: ./script_out/data.csv, Temp: False
    """
    import inspect
    
    if env_type is None:
        env_type = detect_environment()
    
    # For absolute paths, use as-is
    if specified_path.startswith('/'):
        return specified_path, False
    
    # Get base directory based on environment
    if env_type == 'script':
        # Use script location
        try:
            script_path = inspect.stack()[1].filename
            if script_path and not script_path.startswith('<'):
                script_dir = os.path.dirname(os.path.abspath(script_path))
                script_name = os.path.splitext(os.path.basename(script_path))[0]
                base_dir = os.path.join(script_dir, f"{script_name}_out")
                return os.path.join(base_dir, specified_path), False
        except:
            pass
    
    elif env_type == 'jupyter':
        # For Jupyter, use current working directory with subdirectory
        # This keeps outputs near the notebook
        base_dir = os.path.join(os.getcwd(), 'notebook_outputs')
        return os.path.join(base_dir, specified_path), False
    
    elif env_type in ['ipython', 'interactive']:
        # Use temp directory for console sessions
        user = os.getenv('USER', 'unknown')
        base_dir = f'/tmp/{user}/{env_type}'
        return os.path.join(base_dir, specified_path), True
    
    # Fallback: use current directory
    return os.path.join('./output', specified_path), False


def is_notebook() -> bool:
    """Check if running in Jupyter notebook."""
    return detect_environment() == 'jupyter'


def is_ipython() -> bool:
    """Check if running in IPython (console or notebook)."""
    return detect_environment() in ['jupyter', 'ipython']


def is_script() -> bool:
    """Check if running as a script."""
    return detect_environment() == 'script'


# Backward compatibility
def is_ipython_legacy() -> bool:
    """Legacy IPython detection for compatibility."""
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

# EOF