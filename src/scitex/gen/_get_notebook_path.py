#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 12:00:00 (ywatanabe)"
# File: ./src/scitex/gen/_get_notebook_path.py

"""
Get the current Jupyter notebook path.

This module provides functions to detect and retrieve the path
of the currently running Jupyter notebook.
"""

import os
import json
from typing import Optional

__all__ = ['get_notebook_path', 'get_notebook_name']


def get_notebook_path() -> Optional[str]:
    """
    Get the full path of the current Jupyter notebook.
    
    Returns
    -------
    Optional[str]
        Full path to the notebook file, or None if not in a notebook
        
    Examples
    --------
    >>> path = get_notebook_path()
    >>> if path:
    ...     print(f"Running in notebook: {path}")
    """
    try:
        # Try to get from IPython
        from IPython import get_ipython
        ip = get_ipython()
        
        if not ip:
            return None
            
        # Check if we're in a notebook
        if type(ip).__name__ != 'ZMQInteractiveShell':
            return None
        
        # Try multiple methods to get the notebook path
        
        # Method 1: From IPython's config
        if hasattr(ip, 'config') and hasattr(ip.config, 'IPKernelApp'):
            connection_file = ip.config.IPKernelApp.connection_file
            if connection_file:
                # Extract kernel ID from connection file
                kernel_id = os.path.basename(connection_file).split('-', 1)[1].replace('.json', '')
                
                # Try to get notebook path from Jupyter server
                notebook_path = _get_notebook_from_server(kernel_id)
                if notebook_path:
                    return os.path.abspath(notebook_path)
        
        # Method 2: From environment variable (JupyterLab sets this)
        if 'JPY_SESSION_NAME' in os.environ:
            session_name = os.environ['JPY_SESSION_NAME']
            if session_name.endswith('.ipynb'):
                return os.path.abspath(session_name)
        
        # Method 3: From notebook's metadata
        try:
            # This works in some notebook environments
            import ipykernel
            import notebook
            from notebook.notebookapp import list_running_servers
            
            for server in list_running_servers():
                response = _get_notebook_list(server['url'], server.get('token', ''))
                if response:
                    for session in response:
                        if session['kernel']['id'] == kernel_id:
                            return os.path.join(server['notebook_dir'], session['notebook']['path'])
        except:
            pass
            
    except Exception:
        pass
    
    return None


def _get_notebook_from_server(kernel_id: str) -> Optional[str]:
    """Try to get notebook path from Jupyter server API."""
    try:
        import requests
        from notebook.notebookapp import list_running_servers
        
        for server in list_running_servers():
            url = f"{server['url']}api/sessions"
            token = server.get('token', '')
            
            if token:
                headers = {'Authorization': f'token {token}'}
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url)
                
            if response.status_code == 200:
                sessions = response.json()
                for session in sessions:
                    if session['kernel']['id'] == kernel_id:
                        return session['notebook']['path']
    except:
        pass
    
    return None


def _get_notebook_list(server_url: str, token: str) -> Optional[list]:
    """Get list of running notebooks from server."""
    try:
        import requests
        url = f"{server_url}api/sessions"
        
        if token:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
            
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None


def get_notebook_name() -> Optional[str]:
    """
    Get just the name of the current notebook (without path).
    
    Returns
    -------
    Optional[str]
        Notebook filename, or None if not in a notebook
        
    Examples
    --------
    >>> name = get_notebook_name()
    >>> if name:
    ...     print(f"Notebook: {name}")
    """
    notebook_path = get_notebook_path()
    if notebook_path:
        return os.path.basename(notebook_path)
    return None


def get_notebook_directory() -> Optional[str]:
    """
    Get the directory containing the current notebook.
    
    Returns
    -------
    Optional[str]
        Directory path, or None if not in a notebook
    """
    notebook_path = get_notebook_path()
    if notebook_path:
        return os.path.dirname(os.path.abspath(notebook_path))
    return None


# Simpler fallback method for when advanced detection fails
def get_notebook_info_simple() -> tuple[Optional[str], Optional[str]]:
    """
    Simple method to get notebook info using current working directory.
    
    Returns
    -------
    tuple[Optional[str], Optional[str]]
        (notebook_name, notebook_directory)
    """
    try:
        # In Jupyter, __file__ is not defined but we can use inspect
        import inspect
        import re
        
        # Get the call stack and look for notebook indicators
        for frame_info in inspect.stack():
            filename = frame_info.filename
            if filename:
                # Check for ipynb in the filename
                if filename.endswith('.ipynb'):
                    return os.path.basename(filename), os.path.dirname(os.path.abspath(filename))
                
                # Look for notebook execution patterns in the filename
                # Jupyter often uses patterns like <ipython-input-...> or kernel UUIDs
                if '<ipython-input' in filename or 'ipykernel_' in filename:
                    # We're definitely in a notebook, need to find which one
                    break
                    
        # If we can't find it in stack, check if we're in a notebook environment
        from IPython import get_ipython
        ip = get_ipython()
        
        if ip and type(ip).__name__ == 'ZMQInteractiveShell':
            # We're in a notebook but can't determine the name from stack
            # Try multiple strategies to find the notebook name
            
            # Strategy 1: Check IPython's config for hints
            if hasattr(ip, 'config') and hasattr(ip.config, 'IPKernelApp'):
                if hasattr(ip.config.IPKernelApp, 'connection_file'):
                    conn_file = ip.config.IPKernelApp.connection_file
                    # Sometimes the connection file path contains hints about the notebook
                    if conn_file and '.ipynb' in conn_file:
                        match = re.search(r'([^/]+)\.ipynb', conn_file)
                        if match:
                            return match.group(0), os.getcwd()
            
            # Strategy 2: Check environment variables
            for env_var in ['JUPYTER_NOTEBOOK_NAME', 'JPY_SESSION_NAME', 'NOTEBOOK_NAME']:
                if env_var in os.environ:
                    notebook_name = os.environ[env_var]
                    if notebook_name.endswith('.ipynb'):
                        return notebook_name, os.getcwd()
            
            # Strategy 3: Look for recently modified .ipynb files in current directory
            cwd = os.getcwd()
            try:
                # Get all .ipynb files with their modification times
                notebook_files = []
                for file in os.listdir(cwd):
                    if file.endswith('.ipynb') and not file.startswith('.') and not file.endswith('_test_output.ipynb'):
                        file_path = os.path.join(cwd, file)
                        mtime = os.path.getmtime(file_path)
                        notebook_files.append((file, mtime))
                
                # Sort by modification time (most recent first)
                notebook_files.sort(key=lambda x: x[1], reverse=True)
                
                if notebook_files:
                    # Return the most recently modified notebook
                    # This is a good heuristic as the currently running notebook
                    # is likely to have been saved recently
                    return notebook_files[0][0], cwd
            except:
                pass
                    
            # If no notebook found, return generic name
            return "untitled.ipynb", cwd
            
    except:
        pass
        
    return None, None


# EOF